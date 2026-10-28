"""Isolated fixture tests exercise loop limits and replay mechanics; no live evidence is created."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import backend as b
from controller import Manager, Run, PROFILE


class LoopTests(unittest.TestCase):
    def test_three_rounds_even_after_target_duplicates_rejected_and_no_fixture_replay(self):
        with tempfile.TemporaryDirectory() as folder:
            m=Manager(folder);run=m.create({'mode':'live','seed':3})
            def fixture(self,round_id):
                self.calls+=1
                # Explicit fixture provenance; production never calls this test function.
                parent=self.population[0]['id']
                child={'stages':[{'backend':'tabu','config':{'tenure':10+round_id,'restart_after':200},'max_work':3000,'fresh':False}]}
                proposal={'round_id':round_id,'parent_ids':[parent],'hypothesis':'integration fixture','mutation_category':'parameters','children':[self.population[0]['strategy'],child],'plateau_reason':None}
                self.emit('proposal_received',provider='integration_fixture',proposal=proposal,round_id=round_id)
                return proposal
            with patch.object(Run,'propose',fixture), patch.dict(PROFILE,{'max_rounds':3,'max_model_calls':3}):
                m.start(run);run.thread.join(20)
            self.assertEqual(run.status,'finished');self.assertEqual(run.calls,3)
            self.assertEqual(len([e for e in run.events if e['type']=='round_closed']),3)
            self.assertTrue(any(e['type']=='candidate_rejected' and 'duplicate' in e['reason'] for e in run.events))
            self.assertEqual(len(run.population),3);self.assertEqual(run.best['cut'],68)
            self.assertEqual(m.recordings(),{})
            for event in (e for e in run.events if e['type']=='candidate_admitted'):
                parent_id=event['parent_ids'][0]
                self.assertTrue(any(e['type']=='candidate_ranked' and e['candidate']['id']==parent_id for e in run.events[:event['seq']]))
            m.close()

    def test_censored_fitness_and_deadline(self):
        with tempfile.TemporaryDirectory() as folder:
            m=Manager(folder);run=m.create({'mode':'numerical','seed':3});run.frozen=[tuple(b.seed_labels(s)) for s in run.seeds]
            # Valid witness from an incomplete strategy must never enter a comparable ranking.
            result={**b.run_strategy(b.PARENT,3),'complete':False}
            with patch.object(run,'trial',return_value=result):candidate=run.evaluate(b.PARENT,[],0)
            self.assertFalse(candidate['complete']);self.assertIsNone(candidate['median']);run.select([candidate]);self.assertEqual(run.population,[])
            with patch.dict(PROFILE,{'total_seconds':0.001}):
                new=m.reset({'mode':'numerical'});m.start(new);new.thread.join(9)
            self.assertEqual(new.status,'stopped');self.assertLess(new.elapsed(),9);m.close()

    def test_offline_playback_mechanics_fixture_with_original_clock_and_persistent_mode(self):
        with tempfile.TemporaryDirectory() as folder:
            m=Manager(folder);result=b.run_strategy(b.PARENT,3)
            events=[{'run_id':'test','seq':1,'mode':'live','type':'best_updated','elapsed':0.0,'best':result},
                    {'run_id':'test','seq':2,'mode':'live','type':'run_finished','elapsed':0.01,'status':'finished'}]
            fixture={'fixture':{'events':events,'sha256':'fixture-only','seconds':.01,'seed':3}}
            with patch.object(m,'recordings',return_value=fixture):
                r=m.create({'mode':'replay','replay':'fixture','speed':4});m.start(r);r.thread.join(3)
            self.assertEqual(r.status,'finished');self.assertEqual(r.calls,0)
            replay=[e for e in r.events if e['type']=='replay_event']
            self.assertEqual([e['original_elapsed'] for e in replay],[0,.01])
            self.assertTrue(all(e['mode']=='replay' for e in r.events));self.assertEqual(r.best['cut'],result['cut'])
            self.assertEqual(m.recordings(),{});m.close()


if __name__=='__main__':unittest.main()
