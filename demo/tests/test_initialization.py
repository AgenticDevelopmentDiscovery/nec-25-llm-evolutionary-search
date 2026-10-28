"""Selection is confined to seeding, with explicit matched-design metadata."""
import sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from controller import Manager,Run,PROFILE
from experiments import progress_metrics
import backend as b

class InitializationTests(unittest.TestCase):
 def test_checkboxes_validate_and_presets_bind(self):
  with tempfile.TemporaryDirectory() as folder:
   m=Manager(folder)
   for ids in [[],['bm','bm'],['shell'],[True],'bm']:
    with self.assertRaises(ValueError):m.create({'initial_solvers':ids})
   with self.assertRaises(ValueError):m.create({'scenario':'contrast_limited','initial_solvers':['tabu']})
   a=m.create({'scenario':'contrast_limited','mode':'numerical'});z=m.create({'scenario':'contrast_informed','mode':'numerical'})
   self.assertEqual(a.instance,z.instance);self.assertEqual(a.seeds,z.seeds);self.assertEqual(a.initial_solvers,['tabu','annealing']);self.assertEqual(len(z.initial_solvers),3)
   self.assertTrue(a.population_protocol);m.close()
 def test_raw_small_graph_population_and_all_kernel_mutation(self):
  with tempfile.TemporaryDirectory() as folder:
   m=Manager(folder);r=m.create({'scenario':'contrast_limited','mode':'live'})
   def fixture(self,round_id):
    self.calls+=1;self.emit('model_started',round_id=round_id,call=self.calls,provider='integration_fixture')
    return {'parent_ids':[self.population[0]['id']],'children':[b.INITIAL_SOLVERS[3][1]],'hypothesis':'test only','mutation_category':'backend','plateau_reason':None}
   with patch.object(Run,'propose',fixture),patch.dict(PROFILE,{'max_rounds':1,'max_model_calls':1}):
    m.start(r);r.thread.join(10)
   self.assertEqual(r.status,'finished');self.assertEqual(r.best['cut'],1012)
   self.assertEqual(len([e for e in r.events if e['type']=='population_seeded'][0]['algorithms']),2)
   self.assertEqual(r.frozen,[tuple(b.seed_labels(seed,r.instance)) for seed in r.seeds])
   self.assertTrue(any(c['strategy']['stages'][0]['backend']=='bm' for c in r.population))
   metrics=progress_metrics(r.events,1012);self.assertEqual(metrics['initial_best_median'],975);self.assertEqual(metrics['median_reference']['calls'],1)
   m.close()
if __name__=='__main__':unittest.main()
