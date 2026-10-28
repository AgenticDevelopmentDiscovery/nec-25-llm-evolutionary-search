"""No paid calls: real kernels, boundary validation, serial selection and owned cancellation."""
import copy
import importlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import backend as b
from controller import Manager, Run, verify_result, rank_key, Cancelled, PROFILE
from proposals import genome, validate_proposal, context
from server import verify_snapshot
from evolution_common import owned_process
from portfolio_external import process_live


def wait_for(predicate, seconds=5):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        value = predicate()
        if value: return value
        time.sleep(.005)
    raise AssertionError('bounded wait expired')


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.manager = Manager(self.temp.name)
    def tearDown(self):
        self.manager.close(); self.temp.cleanup()

    def test_snapshot_and_semantic_boundaries(self):
        self.assertEqual(verify_snapshot(), 133)
        for labels in ([True]*100, [1.0]*100, [1]*99, [0]*100, [[1]*100]):
            with self.assertRaises(ValueError): self.manager.create({'initial':labels, 'graph_sha256':b.GRAPH_SHA256})
        for body in ({'weights':[1]}, {'seed':True}, {'seed':-1}, {'seed':2**32}, {'mode':'magic'}, {'mode':'replay','replay':'../../x'}, {'initial':[1]*100}):
            with self.assertRaises(ValueError): self.manager.create(body)
        r=self.manager.create({'seed':2**32-1,'initial':[1]*100,'graph_sha256':b.GRAPH_SHA256,'mode':'numerical'})
        self.assertEqual(r.seeds,[2**32-1,0,1])
        for method,key,value in [('tabu','tenure',True),('tabu','tenure',-1),('annealing','initial_temperature',float('nan')),('annealing','polish',1),('bls','q',2),('bm','max_sweeps',1.5)]:
            s={'stages':[{'backend':method,'config':{key:value},'max_work':1,'fresh':False}]}
            with self.assertRaises(ValueError): b.validate_strategy(s)
        with patch.object(b,'GRAPH_SHA256','altered'):
            with self.assertRaisesRegex(ValueError,'altered weights'): b.score_labels([1]*100)
        result=b.run_strategy(b.PARENT,3)
        for cut in (float('nan'),float('inf'),999):
            bad={**result,'cut':cut}
            with self.assertRaises(ValueError): verify_result(bad)

    def test_normalization_and_proposer_excludes_answers(self):
        s={'stages':[{'backend':'tabu','config':{},'max_work':100,'fresh':False}]}
        explicit=copy.deepcopy(s);explicit['stages'][0]['config']=b.DEFAULT_CONFIG['tabu'].copy()
        self.assertEqual(genome(s)[0],genome(explicit)[0])
        pid,strategy=genome(b.PARENT)
        ctx=context(1,[{'id':pid,'strategy':strategy,'median':60,'minimum':58}],[],[])
        text=json.dumps(ctx)
        for secret in ('assignment','NUMERICAL_CHILD','reference','benchmark','replay'):
            self.assertNotIn(secret,text)
        value={'round_id':1,'parent_ids':[pid],'hypothesis':'test bounded escape','mutation_category':'parameters','children':[s],'plateau_reason':None}
        validate_proposal(value,1,{pid})
        for bad in ({**value,'round_id':2},{**value,'score':999},{**value,'parent_ids':['unknown']},{**value,'children':[s,s,s]}):
            with self.assertRaises(ValueError): validate_proposal(bad,1,{pid})

    def test_frozen_fair_comparison_repeat_offline_no_network(self):
        results=[]
        with patch.object(socket,'socket',side_effect=AssertionError('network disabled')):
            for _ in range(2):
                r=self.manager.create({'seed':3,'mode':'numerical'})
                self.assertTrue(self.manager.start(r)); self.assertFalse(self.manager.start(r))
                r.thread.join(15); self.assertFalse(r.thread.is_alive()); self.assertEqual(r.status,'finished')
                self.assertEqual(r.calls,0); self.assertFalse(list(r.path.glob('model-*')))
                frozen=tuple(r.frozen)
                for path in r.path.glob('*-trial*/request.json'):
                    if path.parent.name.startswith('baseline'): continue
                    req=json.loads(path.read_text());i=r.seeds.index(req['seed'])
                    self.assertEqual(req['initial'],list(frozen[i]));self.assertEqual(req['seconds'],1.5)
                self.assertEqual(r.best['cut'],68)
                self.assertEqual(verify_result(r.best)['cut'],68)
                self.assertEqual(len(r.population),2)
                self.assertEqual(r.population,sorted(r.population,key=rank_key))
                self.assertEqual([e['seq'] for e in r.events],list(range(1,len(r.events)+1)))
                results.append([(c['id'],c['median'],c['minimum'],[t['cut'] for t in c['trials']]) for c in r.population])
        self.assertEqual(results[0],results[1]);self.assertEqual(self.manager.recordings(),{})

    def test_live_blocked_keeps_failure_and_reset_changes_identity(self):
        with patch.dict(os.environ,{},clear=True):
            r=self.manager.create({'seed':3,'mode':'live'});self.manager.start(r);r.thread.join(15)
        self.assertEqual(r.status,'failed');self.assertEqual(r.calls,0)
        self.assertIn('OPENAI_API_KEY',r.events[-1]['reason'])
        self.assertTrue(all(e['mode']=='live' for e in r.events))
        count=len(r.events);new=self.manager.reset({'seed':4,'mode':'numerical'})
        self.assertNotEqual(r.id,new.id);self.assertIsNone(new.best);self.assertEqual(len(r.events),count)
        self.assertTrue((r.path/'final.json').exists());self.assertEqual(self.manager.recordings(),{})

    def test_stop_real_numerical_worker_only_owned_processes(self):
        r=self.manager.create({'seed':3,'mode':'numerical'})
        # Isolate a long legal kernel trial so Stop can be tested during real numerical work.
        s={'stages':[{'backend':'annealing','config':{'polish':True},'max_work':30000,'fresh':False}]*3}
        r.started=time.monotonic();r.status='running';self.manager.active=r
        def trial():
            try:r.trial(s,3,b.seed_labels(3).tolist(),'interrupt-trial0');r.finish('finished','trial completed')
            except Cancelled:r.finish('stopped','test Stop')
            finally:self.manager.release(r)
        unrelated=subprocess.Popen([sys.executable,'-c','import time; time.sleep(10)'])
        try:
            r.thread=threading.Thread(target=trial);r.thread.start()
            marker=r.path/'interrupt-trial0/worker_started.json'
            wait_for(marker.exists)
            pid=json.loads(marker.read_text())['pid']
            from portfolio_external import process_tick
            tick=process_tick(pid);self.assertTrue(process_live(pid,tick))
            r.stop();self.assertEqual(r.status,'stopped');self.assertFalse(process_live(pid,tick))
            self.assertIsNone(unrelated.poll());self.assertFalse(list(r.path.glob('*/active_process.json')))
        finally:unrelated.terminate();unrelated.wait()


if __name__=='__main__':unittest.main()
