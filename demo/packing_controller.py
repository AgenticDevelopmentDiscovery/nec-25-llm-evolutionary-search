"""Source-program evolution for the AlphaEvolve circle-packing classroom example."""
import copy
import difflib
import hashlib
import json
import os
from pathlib import Path
import statistics
import sys
import threading
import time
import uuid

import packing as task
from packing_sandbox import availability, command
from controller import (Run as BaseRun, Manager as BaseManager, Cancelled, HERE,
                        TERMINAL, live_access, save, owned_process)
from settings import KEY_NAMES, REAL_PROVIDERS, ENDPOINTS

PROFILE = task.PROFILE


class PackingRun(BaseRun):
    def __init__(self, manager, options):
        self.manager, self.options = manager, options
        self.id = uuid.uuid4().hex
        self.path = manager.root/self.id
        self.path.mkdir(parents=True)
        self.mode, self.seed = options['mode'], options['seed']
        self.n = options['n']
        self.seeds = [(self.seed+i) % 2**32 for i in range(3)]
        self.replay = options.get('replay')
        self.lock = threading.RLock()
        self.changed = threading.Condition(self.lock)
        self.events, self.population, self.candidates, self.failures = [], [], [], []
        self.stop_flag, self.round_gate = threading.Event(), threading.Event()
        self.waiting_round = self.thread = self.started = self.ended = None
        self.status, self.phase, self.calls = 'created', 'ready', 0
        self.current = self.best = None
        self.seen = set()
        self.frozen = [task.start_centers(s,self.n) for s in self.seeds]
        self.trial_best = [None]*3
        self.bank_id = self.bank_hash()
        save(self.path/'config.json', dict(options=options, task=task.specification(self.n), seeds=self.seeds))
        self.emit('run_created', options=options, task=task.specification(self.n), seeds=self.seeds)

    def snapshot(self):
        with self.lock:
            return copy.deepcopy(dict(id=self.id, mode=self.mode, status=self.status,
                phase=self.phase, elapsed=self.elapsed(), model_calls=self.calls,
                waiting_round=self.waiting_round, population=self.population,
                candidates=self.candidates, current=self.current, best=self.best,
                options=self.options, seeds=self.seeds, events=self.events))

    def bank_hash(self):
        return hashlib.sha256(json.dumps(self.frozen,sort_keys=True).encode()).hexdigest()[:12]

    def check(self):
        if self.stop_flag.is_set():raise Cancelled('explicit Stop/Reset')
        if self.elapsed()>=PROFILE['total_seconds']:raise Cancelled('240-second run deadline')

    def owned(self, argv, directory, seconds, model=False):
        self.check()
        env=os.environ.copy();env.pop('DEMO_TEST_API_URL',None)
        if not model:
            for key in KEY_NAMES:env.pop(key,None)
        env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
        receipt=owned_process(argv,directory,min(seconds,PROFILE['total_seconds']-self.elapsed()),
            directory/'stdout.raw',directory/'stderr.raw',environment=env,
            registration=directory/'active_process.json',stop_path=self.path/'STOP')
        save(directory/'process.json',receipt);self.check()
        if receipt['timed_out']:raise TimeoutError('owned process deadline exceeded')
        if receipt['exit_code']!=0:raise ValueError('owned process failed: '+(directory/'stderr.raw').read_text(errors='replace')[-500:])
        return receipt

    def retain_witness(self, checked, seed):
        index=self.seeds.index(seed)
        if self.trial_best[index] is None or checked['score']>self.trial_best[index]['score']:
            self.trial_best[index]=checked

    def trial(self, source, seed, initial, folder, candidate_id):
        self.check()
        folder.mkdir()
        request = dict(source=source, seed=seed, initial=initial, steps=task.STEPS,n=self.n)
        save(folder/'request.json', request)
        self.emit('trial_started', candidate_id=candidate_id, seed=seed)
        halt = threading.Event()
        overflow = threading.Event()
        def progress():
            position = 0
            while not halt.wait(.04):
                if self.stop_flag.is_set(): (folder/'STOP').touch()
                if any(p.exists() and p.stat().st_size > 2_000_000 for p in (folder/'stdout.raw',folder/'stderr.raw')):
                    overflow.set(); (folder/'STOP').touch(); return
                path = folder/'stdout.raw'
                if not path.exists(): continue
                with path.open() as stream:
                    stream.seek(position)
                    while True:
                        before = stream.tell(); line = stream.readline()
                        if not line.endswith('\n'):
                            position = before; break
                        position = stream.tell()
                        try:
                            item = json.loads(line)
                            if item.get('type') != 'progress': continue
                            checked = task.verify(item['circles'],self.n)
                            self.current = {**checked, 'candidate_id': candidate_id, 'seed': seed, 'complete': False,'bank_id':self.bank_id}
                            self.retain_witness(self.current,seed)
                            self.emit('witness_progress', **self.current)
                            if self.best is None or checked['score'] > self.best['score']:
                                self.best = self.current
                                self.emit('best_updated', best=self.best)
                        except (ValueError, TypeError, KeyError): pass
        watcher = threading.Thread(target=progress, daemon=True); watcher.start()
        started = time.monotonic()
        try:
            receipt = owned_process(command(), folder, min(task.TRIAL_SECONDS, PROFILE['total_seconds']-self.elapsed()),
                folder/'stdout.raw', folder/'stderr.raw', stdin=json.dumps(request).encode(),
                environment={'PATH': os.environ.get('PATH', '/usr/bin:/bin')},
                registration=folder/'active_process.json', stop_path=folder/'STOP')
        finally:
            halt.set(); watcher.join(1)
        self.check()
        save(folder/'process.json', receipt)
        if overflow.is_set(): raise ValueError('program output exceeded the 2 MB capture limit')
        items = []
        for line in (folder/'stdout.raw').read_text().splitlines():
            try: items.append(json.loads(line))
            except ValueError: pass
        valid_results = [v for v in items if v.get('type') == 'result']
        if receipt['timed_out']: raise TimeoutError('8-second numerical trial deadline exceeded')
        if receipt['exit_code'] or len(valid_results) != 1:
            errors = [v.get('error') for v in items if v.get('type') == 'error']
            raise ValueError('isolated program failed: '+str(errors[-1] if errors else 'no single completed result'))
        result = task.verify(valid_results[0].get('circles'),self.n)
        result.update(candidate_id=candidate_id, seed=seed, complete=True,
                      bank_id=self.bank_id,
                      elapsed_seconds=time.monotonic()-started,
                      radius_calls=valid_results[0].get('radius_calls'))
        save(folder/'verified.json', result)
        self.current = result
        self.retain_witness(result,seed)
        self.emit('trial_scored', **result)
        if self.best is None or result['score'] > self.best['score']:
            self.best = result
            self.emit('best_updated', best=result)
        return result

    def evaluate(self, source, parents, round_id, name, hypothesis=''):
        identity, source = task.source_identity(source)
        self.seen.add(identity)
        parent = next((p for p in self.population if p['id'] in parents), None)
        difference = ''.join(difflib.unified_diff(parent['source'].splitlines(True), source.splitlines(True),
                                               fromfile='parent.py', tofile='child.py')) if parent else ''
        candidate = dict(id=identity, name=name, source=source, parent_ids=parents,
                         round_id=round_id, hypothesis=hypothesis, diff=difference, trials=[],
                         bank_id=self.bank_id,evaluation_id=f'{identity}-{self.bank_id}')
        self.candidates.append(candidate)
        self.emit('candidate_admitted', candidate=copy.deepcopy(candidate))
        for i, seed in enumerate(self.seeds):
            try:
                result = self.trial(source, seed, copy.deepcopy(self.frozen[i]),
                                    self.path/f'{identity}-{self.bank_id}-r{round_id}-trial{i}', identity)
                candidate['trials'].append({k: result[k] for k in
                    ('seed', 'score', 'min_gap', 'complete', 'elapsed_seconds', 'radius_calls')})
            except Cancelled: raise
            except (ValueError, TimeoutError) as error:
                candidate['trials'].append(dict(seed=seed, complete=False, error=str(error)))
                self.failures.append(dict(candidate_id=identity, seed=seed, reason=str(error)))
                self.emit('trial_rejected', candidate_id=identity, seed=seed, reason=str(error))
        candidate['complete'] = len(candidate['trials']) == 3 and all(t['complete'] for t in candidate['trials'])
        scores = [v['score'] for v in candidate['trials']] if candidate['complete'] else []
        candidate.update(median=statistics.median(scores) if scores else None,
                         minimum=min(scores) if scores else None)
        save(self.path/f'candidate-{identity}-{self.bank_id}-r{round_id}.json', candidate)
        self.emit('candidate_ranked', candidate=copy.deepcopy(candidate))
        return candidate

    def select(self, candidates):
        self.population = sorted([c for c in candidates if c['complete']],
                                 key=lambda c: (-c['median'], -c['minimum'], c['id']))[:3]
        self.emit('survivors_selected', ids=[c['id'] for c in self.population],bank_id=self.bank_id,
                  rule='complete three trials; median descending; minimum descending; stable program ID; top three')

    def context(self, round_id):
        evidence = self.options['context'] == 'evidence'
        independent = self.options['origin'] == 'independent'
        parents = [] if independent else [dict(id=p['id'], source=p['source'], **(
            {k:p[k] for k in ('median', 'minimum', 'trials')} if evidence else {}))
            for p in sorted(self.population, key=lambda c: c['id'])]
        return dict(round_id=round_id, origin=self.options['origin'], context_condition=self.options['context'],
            task=task.specification(self.n), parents=parents, trial_seeds=self.seeds,
            history=[{'id':c['id'],'round':c['round_id'],'bank_id':c['bank_id'],
                      'median':c.get('median'),'minimum':c.get('minimum'),'complete':c.get('complete',False)}
                     for c in self.candidates] + self.failures if evidence else [], tried_ids=sorted(self.seen),
            diversity={'distinct_source_programs':len(parents),
                       'note':'syntax identity is not a guarantee of behavioral diversity'} if evidence else None,
            execution='solve(initial, seed, steps); NumPy/math/radii/report supplied; isolated Python source',
            numerical_protocol=f"{self.options['starts']} starts; bank {self.bank_id}; common three-seed bank, 80 steps, 8-second hard cap per trial",
            remaining_seconds=max(0, PROFILE['total_seconds']-self.elapsed()))

    def propose(self, round_id):
        access = live_access()
        if not access['available']: raise ValueError(access['reason']+'; no API request sent')
        if self.calls >= self.options['rounds']: raise ValueError('model-call cap reached')
        ctx = self.context(round_id)
        folder = self.path/f'model-{round_id}'; folder.mkdir()
        request = dict(model=access['model'], instructions=task.INSTRUCTIONS,
            input=json.dumps(ctx, allow_nan=False), max_output_tokens=3500,
            text={'format': {'type': 'json_schema', 'name': 'packing_program', 'strict': True, 'schema': task.SCHEMA}})
        save(folder/'context.json', ctx); save(folder/'request.json', request)
        self.emit('context_sent', round_id=round_id, context=ctx)
        self.calls += 1
        self.emit('model_started', round_id=round_id, call=self.calls, model=access['model'],
                  provider=access['provider'], endpoint=access['endpoint'])
        halt = threading.Event()
        def stream():
            position = 0
            while not halt.wait(.04):
                path = folder/'public-stream.jsonl'
                if not path.exists(): continue
                with path.open() as handle:
                    handle.seek(position)
                    while True:
                        before = handle.tell(); line = handle.readline()
                        if not line.endswith('\n'):
                            position = before; break
                        position = handle.tell()
                        try:
                            item = json.loads(line)
                            delta = item.get('delta', '') if item.get('type') == 'response.output_text.delta' else ''.join(
                                c.get('delta', {}).get('content') or '' for c in item.get('choices', []))
                            if delta: self.emit('model_public_delta', round_id=round_id, text=delta)
                        except (ValueError, TypeError): pass
        watcher = threading.Thread(target=stream, daemon=True); watcher.start()
        try: self.owned([sys.executable, str(HERE/'model_worker.py'), str(folder)], folder, 35, model=True)
        finally: halt.set(); watcher.join(1)
        result = json.loads((folder/'result.json').read_text())
        if result['provider'] != access['provider'] or result['endpoint'] != access['endpoint'] or result['status'] != 'completed':
            raise ValueError('foreign/incomplete provider response')
        proposal = result['proposal']
        self.emit('proposal_received', round_id=round_id, proposal=proposal,
                  provider=result['provider'], model=result.get('model'), usage=result.get('usage'))
        if not isinstance(proposal, dict) or set(proposal) != set(task.SCHEMA['required']):
            raise ValueError('response fields do not match the packing schema')
        if type(proposal['round_id']) is not int or proposal['round_id'] != round_id:
            raise ValueError('wrong round ID')
        ids = proposal['parent_ids']
        known = {p['id'] for p in self.population}
        if not isinstance(ids, list) or any(type(v) is not str for v in ids) or len(ids) != len(set(ids)):
            raise ValueError('parent IDs must be distinct strings')
        if self.options['origin'] == 'independent':
            if ids: raise ValueError('independent generation must not claim a parent')
        elif not 1 <= len(ids) <= 3 or not set(ids) <= known:
            raise ValueError('mutation must name one to three actual survivor IDs')
        if not isinstance(proposal['hypothesis'], str) or len(proposal['hypothesis']) > 4000:
            raise ValueError('hypothesis must be a string of at most 4000 characters')
        identity, _ = task.source_identity(proposal['source'])
        if identity in self.seen: raise ValueError('duplicate program syntax')
        return proposal

    def execute(self):
        try:
            if self.mode == 'replay':
                source = self.manager.recordings()[self.replay]
                self.emit('replay_provenance', source_run_id=self.replay, source_sha256=source['sha256'])
                started = time.monotonic()
                for event in source['events']:
                    self.check()
                    delay = event['elapsed']-(time.monotonic()-started)
                    if delay > 0 and self.stop_flag.wait(delay): raise Cancelled('replay stopped')
                    data = {k:v for k,v in event.items() if k not in ('run_id','mode','seq','elapsed','type')}
                    self.emit('replay_event', original_type=event['type'], original_elapsed=event['elapsed'], data=data)
                    if event['type'] in ('trial_scored','witness_progress'):self.current={**data,**task.verify(data['circles'],self.n)}
                    if event['type'] == 'best_updated': self.best = {**data['best'], **task.verify(data['best']['circles'],self.n)}
                    if event['type'] == 'survivors_selected': self.population = [c for c in self.candidates if c['id'] in data['ids']]
                    if event['type'] == 'candidate_ranked': self.candidates.append(data['candidate'])
            else:
                if not availability()['available']: raise ValueError(availability()['reason'])
                self.phase = 'initial evaluation'
                for program in task.initial_programs():
                    if program['key'] in self.options['initial_solvers']:
                        self.evaluate(program['source'], [], 0, program['name'])
                self.select(self.candidates)
                if not self.population: raise ValueError('no complete initial program')
                if self.mode == 'live':
                    for round_id in range(1, self.options['rounds']+1):
                        if self.options['starts']=='inherited':
                            self.frozen=[[[x,y] for x,y,r in w['circles']] for w in self.trial_best]
                            self.bank_id=self.bank_hash()
                            self.emit('start_bank_frozen',bank_id=self.bank_id,round_id=round_id,
                                incoming_scores=[w['score'] for w in self.trial_best],
                                reason='previous best packing per seed; re-evaluate parents and child from this same bank')
                            parents=list(self.population)
                            self.phase='re-evaluate parents on inherited packings'
                            measured=[self.evaluate(p['source'],[],round_id,f"{p['name']} (bank {round_id})") for p in parents]
                            self.select(measured)
                            if not self.population:raise ValueError('no complete parent on the inherited bank')
                        self.check(); self.round_gate.clear()
                        self.waiting_round, self.phase = round_id, 'awaiting explicit model call'
                        self.emit('round_ready', round_id=round_id, preview=self.context(round_id))
                        while not self.round_gate.wait(.1): self.check()
                        self.waiting_round = None
                        self.phase = 'Luna proposal'
                        try:
                            proposal = self.propose(round_id)
                        except Cancelled: raise
                        except Exception as error:
                            self.failures.append({'round_id':round_id,'reason':str(error)})
                            self.emit('candidate_rejected',round_id=round_id,reason=str(error))
                            self.emit('round_closed',round_id=round_id,outcome='rejected; no numerical substitute or free retry')
                            continue
                        self.phase = 'child evaluation'
                        child = self.evaluate(proposal['source'], proposal['parent_ids'], round_id,
                                              f'Luna child {round_id}', proposal['hypothesis'])
                        self.select(self.population+[child])
                        self.emit('round_closed', round_id=round_id)
            self.finish('finished', 'bounded circle-packing run completed')
        except Cancelled as error: self.finish('stopped', str(error))
        except Exception as error:
            self.failures.append({'reason': str(error)})
            self.emit('candidate_rejected', reason=str(error))
            self.finish('failed', str(error))
        finally: self.manager.release(self)


class PackingManager(BaseManager):
    def __init__(self, root=None):
        self.root=Path(root or HERE/'runs'/'packing')
        self.root.mkdir(parents=True,exist_ok=True)
        self.lock=threading.RLock();self.runs={};self.active=None

    def create(self, body):
        if not isinstance(body, dict) or set(body)-{'mode','seed','rounds','origin','context','initial_solvers','replay','n','starts'}:
            raise ValueError('unknown packing run fields')
        options = dict(mode='numerical', seed=3, rounds=3, origin='mutation', starts='inherited',
                       context='evidence', n=26, initial_solvers=[p[0] for p in task.CATALOG])
        options.update(body)
        task.specification(options['n'])
        if options['starts'] not in ('fixed','inherited'):raise ValueError('starts must be fixed or inherited')
        if options['mode'] not in ('live','numerical','replay'): raise ValueError('unknown mode')
        if type(options['seed']) is not int or not 0 <= options['seed'] < 2**32: raise ValueError('seed must be uint32')
        if type(options['rounds']) is not int or not 1 <= options['rounds'] <= min(3,PROFILE['max_model_calls']): raise ValueError('rounds must respect the one-to-three call cap')
        if options['origin'] not in ('mutation','independent') or options['context'] not in ('structure','evidence'):
            raise ValueError('invalid origin or context condition')
        selected = options['initial_solvers']
        if not isinstance(selected,list) or not 1 <= len(selected) <= 3 or any(type(v) is not str for v in selected) or len(set(selected)) != len(selected) or not set(selected) <= {p[0] for p in task.CATALOG}:
            raise ValueError('choose one to three distinct initial programs')
        if options['mode'] == 'replay':
            source = self.recordings().get(options.get('replay'))
            if not source: raise ValueError('select a verified genuine circle-packing recording')
            options = {**source['options'], 'mode':'replay', 'replay':options['replay']}
        if self.active is not None: raise ValueError('Stop/Reset the active circle-packing run first')
        run = PackingRun(self, options); self.runs[run.id] = run
        return run

    def recordings(self):
        records = {}
        for folder in self.root.iterdir():
            if len(folder.name) != 32 or any(c not in '0123456789abcdef' for c in folder.name): continue
            try:
                final = json.loads((folder/'final.json').read_text())
                config = json.loads((folder/'config.json').read_text())
                if final['mode'] != 'live' or final['status'] not in ('finished','failed'): continue
                if config['task'] != task.specification(config['options']['n']): continue
                raw = (folder/'events.jsonl').read_bytes()
                events = [json.loads(line) for line in raw.splitlines()]
                proposals = [e for e in events if e['type'] == 'proposal_received']
                if not proposals: continue
                measured=[]
                for i, e in enumerate(events):
                    if e['run_id'] != folder.name or e['mode'] != 'live' or e['seq'] != i+1: raise ValueError('invalid identity')
                    if e['type'] in ('trial_scored','witness_progress'):
                        checked=task.verify(e['circles'],config['options']['n'])
                        if checked['score'] != e['score']: raise ValueError('replay score mismatch')
                    if e['type']=='best_updated':
                        if task.verify(e['best']['circles'],config['options']['n'])['score'] != e['best']['score']:
                            raise ValueError('invalid archived best score')
                    if e['type']=='candidate_admitted': measured=[]
                    if e['type']=='trial_scored':measured.append(e)
                    if e['type'] == 'candidate_ranked':
                        c=e['candidate']
                        if task.source_identity(c['source'])[0] != c['id']: raise ValueError('invalid source hash')
                        if c['complete']:
                            if len(c['trials'])!=3 or len(measured)!=3 or any(not t['complete'] for t in c['trials']):
                                raise ValueError('invalid complete program evidence')
                            if [(t['seed'],t['score']) for t in c['trials']] != [(t['seed'],t['score']) for t in measured]:
                                raise ValueError('trial summary does not match geometry evidence')
                            scores=[t['score'] for t in measured]
                            if c['median']!=statistics.median(scores) or c['minimum']!=min(scores):
                                raise ValueError('invalid fitness aggregation')
                        elif c['median'] is not None or c['minimum'] is not None:
                            raise ValueError('incomplete program has invented fitness')
                for p in proposals:
                    r=json.loads((folder/f"model-{p['round_id']}"/'result.json').read_text())
                    if r['provider'] not in REAL_PROVIDERS or r['provider'] != p['provider'] or r['endpoint'] != ENDPOINTS[r['provider']] or r['status'] != 'completed' or r['proposal'] != p['proposal']:
                        raise ValueError('invalid model provenance')
                    if not (folder/f"model-{p['round_id']}"/'public-stream.jsonl').is_file(): raise ValueError('missing stream')
                if not any(e['type']=='candidate_ranked' and e['candidate']['round_id']>0 for e in events): continue
                records[folder.name] = dict(events=events, options=config['options'], status=final['status'],
                    seconds=events[-1]['elapsed'], sha256=hashlib.sha256(raw).hexdigest())
            except (OSError, ValueError, KeyError, TypeError): continue
        return records

    def exchange(self, identity, round_id):
        if type(round_id) is not int or not 1 <= round_id <= 3: raise ValueError('round must be 1..3')
        run = self.get(identity)
        source = run.replay if run.mode == 'replay' else identity
        folder = self.root/source/f'model-{round_id}'
        visible = run.mode != 'replay' or any(e['type']=='replay_event' and e['original_type']=='model_started' and e['data']['round_id']==round_id for e in run.events)
        def read(name, parsed=True):
            path = folder/name
            if not visible or not path.is_file(): return None
            if path.stat().st_size > 2_000_000: raise ValueError('exchange too large')
            from settings import redact
            text = redact(path.read_text())
            return json.loads(text) if parsed else text
        # Replay response text is reconstructed from elapsed replay events only.
        completed=run.mode!='replay' or any(e['type']=='replay_event' and e['original_type']=='proposal_received' and e['data']['round_id']==round_id for e in run.events)
        public = read('response.txt',False) if completed else ''.join(e['data']['text'] for e in run.events if e['type']=='replay_event' and e['original_type']=='model_public_delta' and e['data']['round_id']==round_id)
        error_visible=run.mode!='replay' or any(e['type']=='replay_event' and e['original_type']=='candidate_rejected' and e['data'].get('round_id')==round_id for e in run.events)
        return dict(request_body=read('payload.json'), context=read('context.json'),
                    public_text=public, provider_error=read('provider-error.json') if error_visible else None, authorization_included=False)
