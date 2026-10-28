"""New solver population, shared raw starts and explicit round gates; no API calls."""
import json
from pathlib import Path
import sys,tempfile,time,unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import backend as b
from controller import Manager,Run,PROFILE,verify_result
from test_controller import wait_for

class PopulationTests(unittest.TestCase):
    def test_two_inherited_rounds_shared_raw_starts_and_manual_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            m=Manager(directory,instance=b.NEW_INSTANCE)
            run=m.create({'mode':'live','seed':3,'stepwise':True})
            contexts=[]
            def fixture(self,round_id):
                self.calls+=1;contexts.append([p['id'] for p in self.population])
                child={'stages':[{'backend':'tabu','config':{'tenure':17+round_id},'max_work':3000,'fresh':False}]}
                self.emit('proposal_received',round_id=round_id,provider='integration_fixture',proposal={'hypothesis':'test only'})
                return {'parent_ids':[self.population[0]['id']],'children':[child],'hypothesis':'test only','mutation_category':'parameters','plateau_reason':None}
            try:
                with patch.object(Run,'propose',fixture),patch.dict(PROFILE,{'max_rounds':2,'max_model_calls':2}):
                    m.start(run)
                    wait_for(lambda:run.waiting_round==1,20)
                    self.assertEqual(run.calls,0);self.assertEqual(len(run.population),3)
                    self.assertTrue(run.continue_round());self.assertFalse(run.continue_round())
                    wait_for(lambda:run.waiting_round==2,20)
                    self.assertEqual(run.calls,1);self.assertTrue(run.continue_round())
                    run.thread.join(20)
                self.assertEqual(run.status,'finished');self.assertEqual(run.calls,2)
                self.assertEqual(len(contexts[0]),3);self.assertEqual(len(contexts[1]),3)
                self.assertTrue(any(i not in contexts[0] for i in contexts[1]))
                for request in run.path.glob('*-trial*/request.json'):
                    d=json.loads(request.read_text());self.assertEqual(d['initial'],b.seed_labels(d['seed'],b.NEW_INSTANCE).tolist());self.assertEqual(d['seconds'],8.0)
                self.assertEqual(len(run.best['assignment']),100);verify_result(run.best)
                self.assertFalse(m.recordings())
            finally:m.close()

    def test_cross_instance_witness_and_gated_stop(self):
        result=b.score_labels(b.seed_labels(3,b.NEW_INSTANCE),b.NEW_INSTANCE)
        self.assertEqual(len(result['assignment']),100)
        self.assertNotEqual(b.score_labels(result['assignment'])['graph_sha256'],result['graph_sha256'])
        with self.assertRaises(ValueError):verify_result({**result,'instance':b.INSTANCE.name})
        with tempfile.TemporaryDirectory() as directory:
            m=Manager(directory,instance=b.NEW_INSTANCE);r=m.create({'mode':'live','stepwise':True})
            try:
                m.start(r);wait_for(lambda:r.waiting_round==1,20);r.stop()
                self.assertEqual(r.status,'stopped');self.assertEqual(r.calls,0);self.assertFalse(r.continue_round())
            finally:m.close()
if __name__=='__main__':unittest.main()
