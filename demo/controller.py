"""Bounded run state, serial owned evaluation, selection and genuine-run replay."""
import copy
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import sys
import threading
import time
import uuid

import backend as b
from experiments import SCENARIOS, progress_metrics
from proposals import SCHEMA, INSTRUCTIONS, context, genome, code, difference, validate_proposal
from settings import KEY_NAMES, REAL_PROVIDERS, ENDPOINTS, provider_settings
# Reference implementation retains Linux subreaper and PID/start-tick ownership.
from evolution_common import owned_process

HERE = Path(__file__).resolve().parent
PROFILE = json.loads((HERE / 'classroom_profile.json').read_text())
TERMINAL = {'finished', 'failed', 'stopped'}


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False))


def live_access():
    try:
        settings = provider_settings()
    except ValueError as error:
        return {'available': False, 'reason': str(error), 'model': None, 'provider': None}
    missing = [settings['key_name']] if not os.environ.get(settings['key_name']) else []
    if not settings['model']: missing.append(settings['model_name'])
    return {'available': not missing, 'reason': ('Missing ' + ', '.join(missing)) if missing else 'Tool-free API configured; account availability is not checked',
            **{k:settings[k] for k in ('provider','protocol','model','endpoint')}}


def rank_key(candidate):
    return (-candidate['median'], -candidate['minimum'], len(candidate['strategy']['stages']), candidate['id'])


def verify_result(result):
    checked = b.score_labels(result.get('assignment'), result.get('instance'))
    if result.get('graph_sha256') != checked['graph_sha256']:
        raise ValueError('worker graph hash mismatch')
    for key in ('cut', 'score'):
        value = result.get(key)
        if type(value) not in (int, float) or not math.isfinite(value) or value != checked[key]:
            raise ValueError('worker supplied a nonfinite or invented score')
    return {**result, **checked}


class Cancelled(Exception): pass


class Run:
    def __init__(self, manager, seed, mode, initial=None, replay=None, speed=1, instance=None, stepwise=False, initial_solvers=None, scenario=None):
        self.manager = manager
        self.instance = instance or b.INSTANCE.name
        self.spec = b.instance_spec(self.instance)
        self.initial_solvers = initial_solvers
        self.scenario = scenario
        self.population_protocol = initial_solvers is not None or self.instance in (b.NEW_INSTANCE,b.COMPARISON_INSTANCE)
        self.stepwise = stepwise
        self.round_gate = threading.Event()
        self.waiting_round = None
        self.id = uuid.uuid4().hex
        self.seed, self.mode, self.replay, self.speed = seed, mode, replay, speed
        self.path = manager.root / self.id
        self.path.mkdir(parents=True)
        self.lock = threading.RLock()
        self.changed = threading.Condition(self.lock)
        self.events = []
        self.stop_flag = threading.Event()
        self.thread = None
        self.started = None
        self.ended = None
        self.created = time.monotonic()
        self.status = 'created'
        self.calls = 0
        self.population = []
        self.seen = set()
        self.failures = []
        self.best = None
        self.frozen = []
        self.initial = b.checked_labels(initial, self.instance).tolist() if initial is not None else None
        self.seeds = [(seed + i) % 2**32 for i in range(3)]
        self.phase = 'ready'
        self.current = b.score_labels(self.initial if self.initial is not None else b.seed_labels(seed, self.instance), self.instance)
        save(self.path / 'request.json', {'seed': seed, 'mode': mode, 'initial': self.initial,
                                         'graph_sha256': self.spec['sha256'], 'instance':self.instance, 'replay': replay, 'speed': speed, 'initial_solvers':initial_solvers, 'scenario':scenario})
        save(self.path / 'config.json', {**PROFILE, 'trial_seeds': self.seeds, 'initial_solvers':initial_solvers, 'scenario':scenario, 'population_protocol':'shared_raw' if self.population_protocol else 'legacy_frozen_parent', 'live_access': live_access()})
        self.emit('run_created', initial_solvers=initial_solvers, scenario=scenario, population_protocol='shared_raw' if self.population_protocol else 'legacy_frozen_parent', seed=seed, trial_seeds=self.seeds, initial=self.current,
                  graph_sha256=self.spec['sha256'], instance=self.instance, total_seconds=PROFILE['total_seconds'], strategy_scope='interpreted trusted-kernel stages',
                  selection='top 3, median then minimum then fewer stages then stable ID; no diversity slot')

    def elapsed(self):
        return (self.ended or time.monotonic()) - self.started if self.started else 0.0

    def emit(self, kind, **data):
        with self.changed:
            event = {'run_id': self.id, 'seq': len(self.events) + 1, 'elapsed': self.elapsed(),
                     'mode': self.mode, 'type': kind, **data}
            # Serialization rejects NaN before anything reaches disk or graph.
            line = json.dumps(event, allow_nan=False)
            with (self.path / 'events.jsonl').open('a') as stream:
                stream.write(line + '\n'); stream.flush()
            self.events.append(event)
            self.changed.notify_all()
            return event

    def snapshot(self):
        with self.lock:
            return copy.deepcopy({'id': self.id, 'status': self.status, 'seed': self.seed, 'mode': self.mode,
                'elapsed': self.elapsed(), 'remaining': max(0, PROFILE['total_seconds'] - self.elapsed()),
                'model_calls': self.calls, 'phase': self.phase, 'current': self.current, 'best': self.best,
                'population': self.population, 'instance': self.instance, 'total_seconds': PROFILE['total_seconds'],
                'initial_solvers':self.initial_solvers, 'scenario':self.scenario, 'population_protocol':'shared_raw' if self.population_protocol else 'legacy_frozen_parent', 'stepwise':self.stepwise, 'waiting_round':self.waiting_round, 'events': self.events, 'replay': self.replay, 'speed': self.speed})

    def check(self):
        if self.stop_flag.is_set(): raise Cancelled('explicit Stop/Reset')
        if self.elapsed() >= PROFILE['total_seconds']: raise Cancelled(str(PROFILE['total_seconds'])+'-second run deadline')

    def owned(self, argv, directory, seconds, model=False):
        self.check()
        env = os.environ.copy()
        env.pop('DEMO_TEST_API_URL', None)
        if not model:
            for key in KEY_NAMES: env.pop(key, None)
        env.update({'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1'})
        receipt = owned_process(argv, directory, min(seconds, PROFILE['total_seconds'] - self.elapsed()),
                                directory / 'stdout.raw', directory / 'stderr.raw', environment=env,
                                registration=directory / 'active_process.json', stop_path=self.path / 'STOP')
        save(directory / 'process.json', receipt)
        self.check()
        if receipt['timed_out']: raise TimeoutError('owned process deadline exceeded')
        if receipt['exit_code'] != 0:
            diagnostic = (directory / 'stderr.raw').read_text(errors='replace')[-500:]
            raise ValueError('owned process failed: ' + diagnostic)
        return receipt

    def trial(self, strategy, seed, initial, name):
        directory = self.path / name
        directory.mkdir()
        trial_seconds = self.spec['trial_seconds']
        save(directory / 'request.json', {'strategy': strategy, 'seed': seed, 'initial': initial, 'seconds': trial_seconds, 'instance':self.instance})
        self.emit('trial_started', candidate_id=name.split('-trial')[0], trial_seed=seed, trial=name)
        # Startup allowance is separate from the shared 1.5-second strategy allowance.
        self.owned([sys.executable, str(HERE / 'backend.py'), '--request', str(directory / 'request.json'),
                    '--output', str(directory / 'result.json')], directory, trial_seconds+1.0)
        result = verify_result(json.loads((directory / 'result.json').read_text()))
        save(directory / 'verified.json', result)
        self.emit('trial_scored', trial=name, trial_seed=seed, candidate_id=name.split('-trial')[0], **result)
        with self.lock: self.current = result
        if self.best is None or result['cut'] > self.best['cut']:
            with self.lock: self.best = {**result, 'candidate_id': name.split('-trial')[0]}
            save(self.path / 'best.json', self.best)
            self.emit('best_updated', best=self.best)
        return result

    def evaluate(self, strategy, parents, round_id, hypothesis='', category='baseline'):
        identity, strategy = genome(strategy)
        self.seen.add(identity)
        candidate = {'id': identity, 'strategy': strategy, 'code': code(strategy), 'parent_ids': parents,
                     'round_id': round_id, 'hypothesis': hypothesis, 'mutation_category': category,
                     'diff': difference(next(p['strategy'] for p in self.population if p['id'] == parents[0]), strategy) if parents else '', 'trials': []}
        for i, seed in enumerate(self.seeds):
            self.check()
            try:
                result = self.trial(strategy, seed, list(self.frozen[i]), f'{identity}-trial{i}')
                candidate['trials'].append({'seed': seed, 'cut': result['cut'], 'complete': result['complete'],
                                             'stage_results': result['stage_results'], 'seconds': result['elapsed_seconds']})
                if not result['complete']:
                    self.failures.append({'id':identity,'seed':seed,'reason':'incomplete numerical trial; excluded from ranking','strategy':strategy,'stage_results':result['stage_results']})
            except Cancelled: raise
            except (ValueError, TimeoutError) as error:
                candidate['trials'].append({'seed': seed, 'complete': False, 'error': str(error)})
                self.failures.append({'id': identity, 'trial': i, 'reason': str(error)})
        candidate['complete'] = len(candidate['trials']) == 3 and all(t['complete'] for t in candidate['trials'])
        if candidate['complete']:
            cuts = [t['cut'] for t in candidate['trials']]
            candidate.update(median=statistics.median(cuts), minimum=min(cuts))
        else:
            candidate.update(median=None, minimum=None)
        save(self.path / f'candidate-{identity}.json', candidate)
        self.emit('candidate_ranked', candidate=candidate, comparable=candidate['complete'])
        return candidate

    def propose(self, round_id):
        access = live_access()
        if not access['available']:
            raise ValueError('Live preflight blocked: ' + access['reason'] + '; no model request sent')
        if self.calls >= PROFILE['max_model_calls']: raise ValueError('model-call cap reached')
        parents = [{key: p[key] for key in ('id', 'strategy', 'median', 'minimum', 'trials')} for p in self.population]
        # Trial records contain scores/counters only, never assignments or fixtures.
        ctx = context(round_id, parents, sorted(self.seen), self.failures)
        ctx.update(trial_seconds=self.spec['trial_seconds'], initialization='shared raw seeded starts' if self.population_protocol else 'shared frozen parent starts',
                   initial_solver_selection=self.initial_solvers, mutation_scope='all four trusted kernels remain available; checkboxes choose seed population only',
                   graph_summary={'nodes':self.spec['nodes'],'edges':len(b.load_graph(self.spec['path']).edges),'signed':True},
                   remaining_seconds=max(0, PROFILE['total_seconds']-self.elapsed()))
        self.emit('context_sent', round_id=round_id, parents=parents, context=ctx)
        directory = self.path / f'model-{round_id}'
        directory.mkdir()
        save(directory / 'context.json', ctx)
        request = {'model': access['model'], 'instructions': INSTRUCTIONS,
            'input': json.dumps(ctx, allow_nan=False), 'max_output_tokens': 2400,
            'text': {'format': {'type': 'json_schema', 'name': 'maxcut_mutation', 'strict': True, 'schema': SCHEMA}}}
        if access['model'] == 'gpt-5-mini': request['reasoning'] = {'effort': 'low'}
        save(directory / 'request.json', request)
        self.calls += 1
        self.emit('model_started', round_id=round_id, call=self.calls, model=access['model'],
                  provider=access['provider'], endpoint=access['endpoint'], timeout_seconds=35)
        halt = threading.Event()
        def public_stream():
            position=0; pending=''
            while True:
                path=directory/'public-stream.jsonl'
                if path.exists():
                    with path.open() as stream:
                        stream.seek(position); pending+=stream.read(); position=stream.tell()
                    lines=pending.split('\n'); pending=lines.pop()
                    for line in lines:
                        try:
                            event=json.loads(line)
                            delta=event.get('delta') if event.get('type')=='response.output_text.delta' else ''.join(c.get('delta',{}).get('content') or '' for c in event.get('choices',[]))
                            if delta:self.emit('model_public_delta',round_id=round_id,text=delta)
                        except (ValueError,TypeError): pass
                if halt.wait(.025): break
        watcher=threading.Thread(target=public_stream,daemon=True);watcher.start()
        try:
            self.owned([sys.executable, str(HERE / 'model_worker.py'), str(directory)], directory, 35, model=True)
        finally:
            halt.set();watcher.join(1)

        result = json.loads((directory / 'result.json').read_text())
        if result['provider'] != access['provider'] or result.get('endpoint') != access['endpoint']:
            raise ValueError('test/foreign transport is not the configured live model')
        proposal = result['proposal']
        self.emit('proposal_received', round_id=round_id, proposal=proposal, usage=result.get('usage'),
                  provider=result['provider'], endpoint=result['endpoint'], response_id=result.get('id'))
        return validate_proposal(proposal, round_id, {p['id'] for p in self.population})

    def select(self, candidates):
        eligible = [c for c in candidates if c['complete']]
        with self.lock: self.population = sorted(eligible, key=rank_key)[:3]
        self.emit('survivors_selected', ids=[c['id'] for c in self.population],
                  reason='complete 3 trials; median descending, minimum descending, fewer stages, stable ID; top 3; no diversity slot',
                  summaries=[{k: c[k] for k in ('id', 'median', 'minimum')} for c in self.population])

    def execute(self):
        try:
            if self.mode == 'replay':
                self.playback()
            else:
                self.phase = 'evaluate'
                if self.population_protocol:
                    initial_algorithms = [(name,strategy) for name,strategy in b.INITIAL_SOLVERS if self.initial_solvers is None or strategy['stages'][0]['backend'] in self.initial_solvers]
                    self.frozen = [tuple(self.initial if self.initial is not None else b.seed_labels(seed, self.instance).tolist()) for seed in self.seeds]
                    self.emit('population_seeded', algorithms=[{'name':name,'id':genome(strategy)[0],'strategy':genome(strategy)[1],'code':code(genome(strategy)[1])} for name,strategy in initial_algorithms], initialization='same raw seeded partitions for every solver')
                    save(self.path / 'frozen-private.json', {'seeds':self.seeds,'labels':self.frozen})
                    initial_candidates=[]
                    for name,strategy in initial_algorithms:
                        self.emit('algorithm_started', name=name, candidate_id=genome(strategy)[0], round_id=0)
                        candidate=self.evaluate(strategy, [], 0, hypothesis='Initial '+name+' solver', category='seed')
                        initial_candidates.append(candidate)
                    self.select(initial_candidates)
                    if not self.population: raise ValueError('no complete initial solver')
                    parent=self.population[0]
                else:
                    # Freeze each weak-parent incumbent once, then copy for EVERY strategy trial.
                    for i, seed in enumerate(self.seeds):
                        initial = self.initial if self.initial is not None else b.seed_labels(seed).tolist()
                        result = self.trial(b.PARENT, seed, initial, f'baseline-trial{i}')
                        if not result['complete']: raise ValueError('incomplete weak-parent construction')
                        self.frozen.append(tuple(result['assignment']))
                        self.emit('baseline_scored', trial_seed=seed, **result)
                    save(self.path / 'frozen-private.json', {'seeds': self.seeds, 'labels': self.frozen})
                    parent = self.evaluate(b.PARENT, [], 0)
                    if not parent['complete']: raise ValueError('parent comparison incomplete')
                    self.select([parent])
                for round_id in range(1, PROFILE['max_rounds'] + 1):
                    self.check()
                    if self.stepwise and self.mode == 'live':
                        self.round_gate.clear()
                        self.waiting_round = round_id
                        self.phase = 'awaiting model'
                        self.emit('round_ready', round_id=round_id, parents=self.population,
                                  reason='Inspect top solvers, then explicitly send this context to Luna')
                        while not self.round_gate.wait(.1): self.check()
                        self.waiting_round = None
                        self.check()
                    self.phase = 'propose'
                    if self.mode == 'live':
                        try:
                            proposal = self.propose(round_id)
                        except Cancelled: raise
                        except Exception as error:
                            self.failures.append({'round_id': round_id, 'reason': str(error)})
                            self.emit('candidate_rejected', round_id=round_id, reason=str(error))
                            # Malformed responses do not silently become fixtures or another free call.
                            raise
                    else:
                        if round_id > 1: break
                        proposal = {'round_id': round_id, 'parent_ids': [parent['id']],
                            'hypothesis': 'Preset numerical comparison; no LLM supplied this strategy',
                            'mutation_category': 'parameters', 'children': [b.NUMERICAL_CHILD], 'plateau_reason': None}
                        self.emit('proposal_received', round_id=round_id, proposal=proposal, provider='numerical_preset', usage=None)
                    candidates = list(self.population)
                    self.phase = 'evaluate'
                    for strategy in proposal['children']:
                        self.check()
                        try:
                            identity, normalized = genome(strategy)
                            if identity in self.seen: raise ValueError('duplicate normalized genome')
                        except (ValueError, TypeError) as error:
                            self.failures.append({'round_id': round_id, 'reason': str(error), 'strategy':strategy})
                            self.emit('candidate_rejected', round_id=round_id, reason=str(error), strategy=strategy)
                            continue
                        self.emit('candidate_admitted', candidate_id=identity, strategy=normalized, code=code(normalized),
                                  diff=difference(next(p['strategy'] for p in self.population if p['id'] == proposal['parent_ids'][0]), normalized), parent_ids=proposal['parent_ids'],
                                  hypothesis=proposal['hypothesis'], mutation_category=proposal['mutation_category'])
                        candidates.append(self.evaluate(normalized, proposal['parent_ids'], round_id, proposal['hypothesis'], proposal['mutation_category']))
                    self.phase = 'select'
                    self.select(candidates)
                    self.emit('round_closed', round_id=round_id, plateau_reason=proposal['plateau_reason'])
            self.finish('finished', 'bounded experiment completed')
        except Cancelled as error:
            self.finish('stopped', str(error))
        except Exception as error:
            self.finish('failed', str(error))
        finally:
            self.manager.release(self)

    def finish(self, status, reason):
        with self.lock:
            self.ended = time.monotonic()
            self.status, self.phase = status, status
        self.emit('run_failed' if status == 'failed' else 'run_finished', status=status, reason=reason, model_calls=self.calls)
        save(self.path / 'final.json', {k: v for k, v in self.snapshot().items() if k != 'events'})

    def stop(self):
        with self.lock:
            if self.status not in TERMINAL:
                if not self.stop_flag.is_set():
                    self.emit('run_stopping', reason='explicit Stop/Reset')
                self.stop_flag.set()
                (self.path / 'STOP').touch()
                if self.thread is None:
                    self.finish('stopped', 'stopped before Start')
        if self.thread is not None:
            self.thread.join(timeout=9)
            if self.thread.is_alive(): raise RuntimeError('owned cleanup is still pending; reset refused')

    def continue_round(self):
        with self.lock:
            if self.status != 'running' or self.waiting_round is None or self.round_gate.is_set():
                return False
            self.round_gate.set()
            return True

    def playback(self):
        source = self.manager.recordings()[self.replay]
        self.emit('replay_provenance', source_run_id=self.replay, source_sha256=source['sha256'],
                  original_seconds=source['seconds'], playback_speed=self.speed, source_status=source.get('status','finished'), source_reason=source.get('reason',''))
        started = time.monotonic()
        for original in source['events']:
            self.check()
            delay = original['elapsed'] / self.speed - (time.monotonic() - started)
            if delay > 0 and self.stop_flag.wait(delay): raise Cancelled('replay stopped')
            event = {k: v for k, v in original.items() if k not in {'run_id', 'seq', 'elapsed', 'mode', 'type'}}
            # Original timestamps are distinct from this playback's wall time.
            self.emit('replay_event', original_type=original['type'], original_elapsed=original['elapsed'], data=event)
            if original['type'] == 'best_updated':
                self.best = verify_result(event['best']); self.current = self.best
            if original['type'] == 'survivors_selected': self.phase = 'replay selection'


class Manager:
    def __init__(self, root=None, instance=None):
        self.instance = instance or b.INSTANCE.name
        b.instance_spec(self.instance)
        self.root = Path(root or HERE / 'runs')
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.runs = {}
        self.active = None

    def create(self, body):
        if not isinstance(body, dict) or set(body) - {'seed', 'mode', 'initial', 'graph_sha256', 'replay', 'speed', 'instance', 'stepwise', 'initial_solvers', 'scenario'}:
            raise ValueError('unknown run fields')
        preset=SCENARIOS.get(body.get('scenario'))
        seed, mode = body.get('seed', preset['seed'] if preset else 3), body.get('mode', 'live')
        instance = body.get('instance', preset['instance'] if preset else self.instance)
        spec = b.instance_spec(instance)
        b.seed_labels(seed, instance)
        if mode not in ('live', 'numerical', 'replay'): raise ValueError('unsupported mode')
        initial = body.get('initial')
        if initial is not None:
            b.checked_labels(initial, instance)
            if body.get('graph_sha256') != spec['sha256']: raise ValueError('labels must bind to the displayed graph hash')
        speed = body.get('speed', 1)
        if type(speed) not in (int, float) or speed not in (1, 2, 4): raise ValueError('replay speed must be 1, 2, or 4')
        replay = body.get('replay')
        if mode == 'replay':
            if not isinstance(replay, str) or replay not in self.recordings(): raise ValueError('no verified genuine LLM recording selected')
            seed = self.recordings()[replay]['seed']
            instance = self.recordings()[replay].get('instance', b.INSTANCE.name)
        initial_solvers=body.get('initial_solvers',preset['initial_solvers'] if preset else None)
        if initial_solvers is not None:
            if not isinstance(initial_solvers,list) or not 1<=len(initial_solvers)<=4 or any(type(v) is not str or v not in b.DEFAULT_CONFIG for v in initial_solvers) or len(set(initial_solvers))!=len(initial_solvers):
                raise ValueError('select one to four distinct initial solver identifiers')
            initial_solvers=[strategy['stages'][0]['backend'] for _,strategy in b.INITIAL_SOLVERS if strategy['stages'][0]['backend'] in initial_solvers]
        scenario=body.get('scenario')
        if scenario is not None and scenario not in {*SCENARIOS,'custom'}:raise ValueError('unknown experiment scenario')
        if preset and mode!='replay' and (instance!=preset['instance'] or seed!=preset['seed'] or set(initial_solvers or [])!=set(preset['initial_solvers'])):
            raise ValueError('preset metadata must match graph, seed and solver checkboxes; choose custom after editing')
        if mode=='replay':
            original=self.recordings()[replay]
            initial_solvers=original.get('initial_solvers');scenario=original.get('scenario')
        stepwise = body.get('stepwise', False)
        if type(stepwise) is not bool: raise ValueError('stepwise must be boolean')
        with self.lock:
            if self.active is not None: raise ValueError('Stop/Reset the active run before New Run')
            run = Run(self, seed, mode, initial, replay, speed, instance, stepwise, initial_solvers, scenario)
            self.runs[run.id] = run
            return run

    def get(self, identity):
        if identity not in self.runs: raise KeyError('unknown run ID')
        return self.runs[identity]

    def start(self, run):
        with self.lock, run.lock:
            if run.thread is not None or run.status != 'created':
                return False  # Duplicate Start is idempotent and never launches work.
            if self.active is not None: raise ValueError('another run owns the controller')
            self.active = run
            run.status, run.started = 'running', time.monotonic()
            run.thread = threading.Thread(target=run.execute, name='run-' + run.id, daemon=True)
            run.thread.start()
            return True

    def release(self, run):
        with self.lock:
            if self.active is run: self.active = None

    def reset(self, body):
        with self.lock: old = list(self.runs.values())
        for run in old: run.stop()
        return self.create(body)

    def close(self):
        for run in list(self.runs.values()): run.stop()

    def activity(self):
        with self.lock:
            runs=[]
            for r in self.runs.values():
                matches=[e for e in r.events if e['type']=='candidate_ranked' and e['candidate']['complete'] and e['candidate']['minimum']>=r.spec['reference']-1e-9]
                first=matches[0] if matches else None
                calls_at_match=sum(e['type']=='model_started' and e['seq']<first['seq'] for e in r.events) if first else None
                complete=[e['candidate'] for e in r.events if e['type']=='candidate_ranked' and e['candidate']['complete']]
                runs.append({'id':r.id,'mode':r.mode,'status':r.status,'instance':r.instance,'replay':r.replay,
                    'initial_solvers':r.initial_solvers,'scenario':r.scenario,'elapsed':r.elapsed(),
                    'complete_reference_seconds':first['elapsed'] if first else None,'calls_to_complete_reference':calls_at_match,
                    'best_cut':r.best['cut'] if r.best else None,'best_median':max((c['median'] for c in complete),default=None),
                    'numerical_seconds':sum(e.get('elapsed_seconds',0) for e in r.events if e['type']=='trial_scored'),
                    'model_calls':max([e['data'].get('call',0) for e in r.events if e['type']=='replay_event' and e['original_type']=='model_started'],default=0) if r.mode=='replay' else r.calls})
            return {'active_run_id':self.active.id if self.active else None,'runs':runs}

    def comparisons(self):
        rows=[]
        for r in self.runs.values():
            if r.mode=='replay' or not r.scenario: continue
            rows.append({'id':r.id,'scenario':r.scenario,'mode':r.mode,'status':r.status,'instance':r.instance,'seed':r.seed,'initial_solvers':r.initial_solvers,'elapsed':r.elapsed(),'evidence':'current server run',**progress_metrics(r.events,r.spec['reference'])})
        ids={r['id'] for r in rows}
        for identity,record in self.recordings().items():
            if identity in ids or not record.get('scenario'):continue
            rows.append({'id':identity,'scenario':record['scenario'],'mode':'live','status':record.get('status','finished'),'instance':record['instance'],'seed':record['seed'],'initial_solvers':record['initial_solvers'],'elapsed':record['seconds'],'evidence':'stored genuine live run',**progress_metrics(record['events'],b.instance_spec(record['instance'])['reference'])})
        order={name:i for i,name in enumerate(SCENARIOS)}
        rows.sort(key=lambda row:(order.get(row['scenario'],99),row['evidence']!='current server run',row['id']))
        return {'runs':rows}

    def exchange(self, identity, round_id):
        if type(round_id) is not int or not 1 <= round_id <= 3: raise ValueError('round must be 1..3')
        run=self.runs.get(identity)
        replay=run is not None and run.mode=='replay'
        if run:
            source_id=run.replay if replay else run.id
            mode=run.mode
        else:
            if identity not in self.recordings(): raise KeyError('no registered or verified source run')
            source_id=identity;mode='recorded source'
        folder=self.root/source_id/f'model-{round_id}'
        def read(name, json_value=True):
            path=folder/name
            if not path.is_file(): return None
            if path.stat().st_size>2_000_000: raise ValueError('public exchange exceeds size limit')
            from settings import redact
            raw=redact(path.read_text())
            return json.loads(raw) if json_value else raw
        started=not replay or any(e['type']=='replay_event' and e['original_type']=='model_started' and e['data']['round_id']==round_id for e in run.events)
        completed=not replay or any(e['type']=='replay_event' and e['original_type']=='proposal_received' and e['data']['round_id']==round_id for e in run.events)
        if replay:
            partial=''.join(e['data']['text'] for e in run.events if e['type']=='replay_event' and e['original_type']=='model_public_delta' and e['data']['round_id']==round_id)
        else:
            partial=''
            raw=read('public-stream.jsonl',False) or ''
            for line in raw.splitlines():
                try:
                    event=json.loads(line)
                    partial+=event.get('delta','') if event.get('type')=='response.output_text.delta' else ''.join(c.get('delta',{}).get('content') or '' for c in event.get('choices',[]))
                except (ValueError,TypeError): pass
        return {'run_id':identity,'source_run_id':source_id,'mode':mode,'round_id':round_id,
                'request_body':read('payload.json') if started else None,
                'controller_context':read('context.json') if started else None,
                'public_text':(read('response.txt',False) if completed else None) or partial,
                'validated_response':read('result.json') if completed else None,
                'provider_error':read('provider-error.json') if completed else None,
                'authorization_included':False}

    def recordings(self):
        recordings = {}
        for folder in self.root.iterdir():
            if not folder.is_dir() or len(folder.name) != 32 or any(c not in '0123456789abcdef' for c in folder.name): continue
            try:
                final = json.loads((folder / 'final.json').read_text())
                if final['status'] not in ('finished','failed') or final['mode'] != 'live': continue
                raw = (folder / 'events.jsonl').read_bytes()
                events = [json.loads(line) for line in raw.splitlines()]
                if any(e['mode'] != 'live' or e['run_id'] != folder.name or e['seq'] != i+1 for i,e in enumerate(events)):
                    raise ValueError('invalid event identities')
                proposals = [e for e in events if e['type'] == 'proposal_received' and e.get('provider') in REAL_PROVIDERS]
                if not proposals or not any(e['type'] == 'candidate_admitted' for e in events): continue
                models = set()
                for p in proposals:
                    result = json.loads((folder / f"model-{p['round_id']}" / 'result.json').read_text())
                    if result['provider'] != p['provider'] or result['status'] != 'completed' or result['proposal'] != p['proposal']:
                        raise ValueError('invalid recording provenance')
                    endpoint = result.get('endpoint', ENDPOINTS['openai_responses'] if p['provider'] == 'openai_responses' else None)
                    if endpoint != ENDPOINTS[p['provider']]: raise ValueError('recording endpoint mismatch')
                    model = result.get('model') or json.loads((folder / f"model-{p['round_id']}" / 'request.json').read_text())['model']
                    if not isinstance(model, str): raise ValueError('invalid recorded model identity')
                    models.add(model)
                    if not (folder / f"model-{p['round_id']}" / 'public-stream.jsonl').is_file(): raise ValueError('missing transcript')
                for e in events:
                    if e['type'] == 'best_updated': verify_result(e['best'])
                    if e['type'] in {'trial_scored', 'baseline_scored'}: verify_result(e)
                    if e['type'] == 'run_created': verify_result(e['initial'])
                    if e['type'] == 'candidate_ranked':
                        candidate = e['candidate']
                        if genome(candidate['strategy'])[0] != candidate['id']: raise ValueError('candidate hash mismatch')
                if not any(e['type'] == 'candidate_ranked' and e['candidate']['round_id'] > 0 and (e['candidate']['complete'] or final['status']=='failed') for e in events): continue
                config = json.loads((folder / 'config.json').read_text())
                recordings[folder.name] = {'events': events, 'seed': final['seed'], 'seconds': events[-1]['elapsed'],
                    'initial_solvers':config.get('initial_solvers'), 'scenario':config.get('scenario'),
                    'instance':events[0].get('instance', b.INSTANCE.name), 'total_seconds':config['total_seconds'],
                    'status':final['status'], 'reason':events[-1].get('reason',final.get('reason','')), 'models': sorted(models), 'model_call_limit': config['max_model_calls'],
                    'sha256': hashlib.sha256(raw).hexdigest()}
            except (ValueError, KeyError, TypeError, OSError): continue
        return recordings
