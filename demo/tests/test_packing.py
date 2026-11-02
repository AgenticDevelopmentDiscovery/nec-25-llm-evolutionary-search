"""Circle geometry, context controls and actual isolated execution; zero paid calls."""
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import packing as p
from packing_controller import PackingManager
from packing_sandbox import availability


class PackingContractTests(unittest.TestCase):
    def test_geometry_and_objective_are_independent_of_claims(self):
        result=p.verify([[.25,.5,.25],[.75,.5,.25]],n=2)
        self.assertEqual(result['score'],.5)
        self.assertEqual(result['min_gap'],0)
        for circles in ([[.3,.5,.3],[.7,.5,.3]], [[.1,.5,.2],[.75,.5,.1]],
                        [[.25,.5,-.1],[.75,.5,.1]], [[float('nan'),.5,.1],[.75,.5,.1]],
                        [[True,.5,.1],[.75,.5,.1]], [[.25,.5,.25]]):
            with self.subTest(circles=circles),self.assertRaises(ValueError):p.verify(circles,n=2)

    def test_starts_identity_and_controls(self):
        self.assertEqual(p.start_centers(3),p.start_centers(3))
        self.assertNotEqual(p.start_centers(3),p.start_centers(4))
        source=p.initial_programs()[0]['source']
        self.assertEqual(p.source_identity(source)[0],p.source_identity(source+'\n# comment\n')[0])
        with self.assertRaises(ValueError):p.source_identity('def solve(wrong): return []')
        with tempfile.TemporaryDirectory() as root:
            manager=PackingManager(root)
            for value in ({'n':27},{'seed':True},{'seed':-1},{'initial_solvers':[]},{'rounds':4},{'mode':'replay','replay':'fake'}):
                with self.subTest(value=value),self.assertRaises(ValueError):manager.create(value)
            run=manager.create({'context':'structure','seed':2**32-1})
            self.assertEqual(run.seeds,[2**32-1,0,1])
            run.population=[dict(id='b',source=source,median=2,minimum=1,trials=[]),
                            dict(id='a',source=source,median=3,minimum=1,trials=[])]
            run.failures=[{'reason':'example failure'}]
            ctx=run.context(1)
            self.assertEqual([v['id'] for v in ctx['parents']],['a','b'])
            self.assertNotIn('median',ctx['parents'][0]);self.assertEqual(ctx['history'],[])
            run.options['context']='evidence'
            self.assertEqual(run.context(1)['parents'][0]['median'],3)
            self.assertEqual(len(run.context(1)['history']),1)
            run.options['origin']='independent'
            self.assertEqual(run.context(1)['parents'],[])
            manager.close()


@unittest.skipUnless(availability()['available'],'real Bubblewrap/SciPy execution unavailable')
class IsolatedPackingTests(unittest.TestCase):
    def test_original_bank_validation_freezes_sources_and_excludes_failures(self):
        with tempfile.TemporaryDirectory() as root:
            manager=PackingManager(root)
            run=manager.create({'mode':'numerical','initial_solvers':['grid']})
            manager.start(run);run.thread.join(15)
            original_candidates=json.dumps(run.candidates,sort_keys=True)
            grid=run.population[0]
            local=p.initial_programs()[1]
            local_id,_=p.source_identity(local['source'])
            bad='def solve(initial, seed, steps):\n    raise ValueError("validation failure fixture")\n'
            bad_id,_=p.source_identity(bad)
            run.population=[grid,dict(id=local_id,source=local['source'],name=local['name']),
                            dict(id=bad_id,source=bad,name='Invalid final fixture')]
            run.frozen=[p.start_centers(seed+100) for seed in run.seeds]
            run.bank_id=run.bank_hash()
            validation=manager.validate_original(run)
            self.assertIs(manager.validate_original(run),validation)
            validation.thread.join(25)
            self.assertEqual(validation.status,'finished',validation.events[-1])
            self.assertEqual(validation.calls,0)
            self.assertEqual(validation.frozen,[p.start_centers(seed) for seed in run.seeds])
            self.assertNotEqual(validation.bank_id,run.bank_id)
            self.assertEqual(len(validation.candidates),3)  # Shared initial/final source once.
            self.assertEqual(validation.validation_roles[grid['id']],['initial','final'])
            failed=next(c for c in validation.candidates if c['id']==bad_id)
            self.assertFalse(failed['complete']);self.assertIsNone(failed['median'])
            self.assertTrue(all(c['bank_id']==validation.bank_id for c in validation.candidates))
            self.assertEqual(json.dumps(run.candidates,sort_keys=True),original_candidates)
            self.assertEqual(run.snapshot()['validation']['model_calls'],0)
            manager.close()
            restored=PackingManager(root)
            report=restored.get(run.id).snapshot()['validation']
            self.assertEqual(report['status'],'finished')
            self.assertEqual(len(report['candidates']),3)
            self.assertEqual(report['roles'][grid['id']],['initial','final'])
            restored.close()

    def test_stop_original_bank_validation_does_not_restart_it(self):
        with tempfile.TemporaryDirectory() as root:
            manager=PackingManager(root)
            run=manager.create({'mode':'numerical','initial_solvers':['grid']})
            manager.start(run);run.thread.join(15)
            hanging='def solve(initial, seed, steps):\n    while True: pass\n'
            identity,_=p.source_identity(hanging)
            run.population=[dict(id=identity,source=hanging,name='Stop fixture')]
            validation=manager.validate_original(run)
            deadline=time.monotonic()+12
            while not list(validation.path.glob(f'{identity}*/active_process.json')) and time.monotonic()<deadline:
                time.sleep(.03)
            records=list(validation.path.glob(f'{identity}*/active_process.json'))
            self.assertTrue(records)
            record=json.loads(records[0].read_text())
            validation.stop()
            self.assertEqual(validation.status,'stopped');self.assertIsNone(manager.active)
            from portfolio_external import process_live
            self.assertFalse(process_live(record['pid'],record['tick']))
            self.assertIs(manager.validate_original(run),validation)
            self.assertEqual(validation.calls,0);manager.close()

    def test_numerical_programs_complete_with_distinct_fitness(self):
        with tempfile.TemporaryDirectory() as root:
            manager=PackingManager(root)
            for n in (26,32):
                run=manager.create({'mode':'numerical','n':n});manager.start(run)
                run.thread.join(35)
                self.assertEqual(run.status,'finished',run.events[-1])
                self.assertEqual(run.calls,0)
                self.assertTrue(all(c['complete'] for c in run.candidates))
                self.assertGreater(len({round(c['median'],4) for c in run.candidates}),1)
                self.assertEqual(manager.recordings(),{})
                self.assertEqual(len([e for e in run.events if e['type']=='trial_scored']),9)
                self.assertGreater(len([e for e in run.events if e['type']=='witness_progress']),0)
                p.verify(run.best['circles'],n)
            manager.close()

    def test_private_host_files_and_environment_are_absent(self):
        with tempfile.TemporaryDirectory() as root:
            marker=Path(root)/'private-marker';marker.write_text('test-only-marker')
            manager=PackingManager(Path(root)/'runs');run=manager.create({})
            source='''def solve(initial, seed, steps):
    import os
    assert not os.path.exists(MARKER)
    assert not os.path.isfile(REPOSITORY+'/AGENTS.md')
    assert 'TAMUS_AI_CHAT_API_KEY' not in os.environ
    assert 'OPENAI_API_KEY' not in os.environ
    assert not os.path.exists('/proc/1/root'+MARKER)
    return np.column_stack((initial, radii(initial)))
'''.replace('MARKER',repr(str(marker))).replace('REPOSITORY',repr(str(Path(__file__).resolve().parents[2])))
            result=run.trial(source,3,p.start_centers(3),run.path/'isolation','test')
            self.assertTrue(result['complete']);manager.close()

    def test_stop_cleans_up_a_running_source_process_and_gate_never_calls(self):
        with tempfile.TemporaryDirectory() as root:
            manager=PackingManager(root)
            run=manager.create({'mode':'live','initial_solvers':['grid']});manager.start(run)
            deadline=time.monotonic()+12
            while run.waiting_round is None and time.monotonic()<deadline:time.sleep(.03)
            self.assertIsNotNone(run.waiting_round,run.events[-1]);self.assertEqual(run.calls,0)
            run.stop();self.assertEqual(run.status,'stopped');self.assertEqual(run.calls,0)
            fresh=manager.create({'mode':'numerical'})
            source='def solve(initial, seed, steps):\n    while True: pass\n'
            outcome=[]
            import threading
            def work():
                try:fresh.trial(source,3,p.start_centers(3),fresh.path/'loop','test')
                except Exception as error:outcome.append(error)
            thread=threading.Thread(target=work);thread.start()
            deadline=time.monotonic()+5
            while not (fresh.path/'loop'/'active_process.json').exists() and time.monotonic()<deadline:time.sleep(.03)
            record=json.loads((fresh.path/'loop'/'active_process.json').read_text())
            fresh.stop();thread.join(10)
            self.assertFalse(thread.is_alive());self.assertTrue(outcome)
            from portfolio_external import process_live
            self.assertFalse(process_live(record['pid'],record['tick']))
            manager.close()

    def test_inherited_bank_scores_are_comparable_at_the_gate(self):
        with tempfile.TemporaryDirectory() as root:
            manager=PackingManager(root)
            run=manager.create({'mode':'live','initial_solvers':['local'],'n':32})
            manager.start(run);deadline=time.monotonic()+15
            while run.waiting_round is None and run.status=='running' and time.monotonic()<deadline:time.sleep(.03)
            self.assertIsNotNone(run.waiting_round,run.events[-1])
            frozen=[e for e in run.events if e['type']=='start_bank_frozen'][-1]
            self.assertEqual(run.population[0]['bank_id'],frozen['bank_id'])
            self.assertNotEqual(run.candidates[0]['bank_id'],frozen['bank_id'])
            self.assertEqual(run.calls,0)
            run.stop();manager.close()


if __name__=='__main__':unittest.main()
