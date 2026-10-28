"""Real warm-state handoff, retention, deadlines and unchanged initial/fresh paths."""
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import backend as b
import bm_refinement as warm
from bm_solver import angles_from_signs


BM = b.INITIAL_SOLVERS[3][1]['stages'][0]
TABU = b.INITIAL_SOLVERS[0][1]['stages'][0]


class RefinementTests(unittest.TestCase):
    def test_real_tabu_to_bm_uses_perturbed_incoming_partition_reproducibly(self):
        initial = b.seed_labels(3); before = initial.copy()
        strategy = {'stages': [TABU, BM]}
        with patch.object(b, 'refine_partition', wraps=b.refine_partition) as dispatch, \
             patch.object(warm, 'solve_from_angles', wraps=warm.solve_from_angles) as core:
            result = b.run_strategy(strategy, 3, initial)
        self.assertTrue(result['complete'])
        self.assertEqual(dispatch.call_count, 1)
        incoming = dispatch.call_args.args[4]
        self.assertEqual(b.score_labels(incoming)['cut'], result['stage_results'][0]['retained_cut'])
        angles = core.call_args.args[1]
        offsets = (angles - angles_from_signs(incoming) + np.pi) % (2*np.pi) - np.pi
        self.assertGreater(np.max(np.abs(offsets)), 0)
        self.assertLessEqual(np.max(np.abs(offsets)), warm.PERTURB_SCALE + 1e-12)
        self.assertEqual(core.call_args.args[0].node_count, len(incoming))
        self.assertEqual(result['stage_results'][1]['initialization'], 'retained_partition_lift_perturb_refine')
        self.assertGreaterEqual(result['cut'], b.score_labels(incoming)['cut'])
        self.assertLessEqual(result['stage_results'][0]['allocated_seconds'], .75)
        self.assertLessEqual(result['stage_results'][1]['allocated_seconds'], 1.5)
        replay = b.run_strategy(strategy, 3, initial)
        self.assertEqual(result['assignment'], replay['assignment'])
        self.assertEqual(result['cut'], b.score_labels(result['assignment'])['cut'])
        np.testing.assert_array_equal(initial, before)

    def test_bm_to_tabu_starts_tabu_from_retained_bm_partition(self):
        with patch.object(b, 'solve', wraps=b.solve) as solve, \
             patch.object(b, 'refine_partition', wraps=b.refine_partition) as refinement:
            result = b.run_strategy({'stages': [BM, TABU]}, 3)
        self.assertTrue(result['complete'])
        refinement.assert_not_called()
        self.assertEqual(solve.call_args_list[1].kwargs['solver'], 'tabu')
        incoming = solve.call_args_list[1].args[4]
        self.assertEqual(b.score_labels(incoming)['cut'], result['stage_results'][0]['retained_cut'])
        self.assertGreaterEqual(result['cut'], b.score_labels(incoming)['cut'])

    def test_initial_and_fresh_bm_keep_original_dispatch(self):
        for stages in [[BM], [TABU, {**BM, 'fresh': True}]]:
            with self.subTest(stages=stages), patch.object(b, 'refine_partition') as refinement, \
                 patch.object(b, 'solve', wraps=b.solve) as solve:
                result = b.run_strategy({'stages': stages}, 3)
                self.assertTrue(result['complete'])
                refinement.assert_not_called()
                self.assertEqual(solve.call_args_list[-1].kwargs['solver'], 'bm')
                if len(stages) == 2: self.assertIsNone(solve.call_args_list[-1].args[4])

    def test_worse_refinement_cannot_erase_incoming_solution(self):
        initial = b.run_strategy(b.NUMERICAL_CHILD, 3)['assignment']
        graph = b.load_graph(b.INSTANCE)
        with patch.object(warm, 'solve_from_angles', return_value=(np.ones(100, dtype=np.int8), 0, {})):
            result = warm.refine_partition(graph, BM['config'], 3, {'seconds': 1, 'max_work': 1}, initial)
        self.assertEqual(result['assignment'], initial)
        self.assertEqual(result['cut'], 68)
        self.assertEqual(result['proposed_cut'], 0)

    def test_deadline_censors_a_valid_retained_result(self):
        initial = b.seed_labels(3); graph = b.load_graph(b.INSTANCE)
        def slow_core(*args, **kwargs):
            time.sleep(.02)
            return initial.copy(), 0, {}
        with patch.object(warm, 'solve_from_angles', side_effect=slow_core):
            result = warm.refine_partition(graph, BM['config'], 3, {'seconds': .005, 'max_work': 1}, initial)
        self.assertEqual(result['execution_status'], 'time_limit')
        self.assertEqual(result['cut'], b.score_labels(result['assignment'])['cut'])
        with patch.object(warm, 'deadline_from', return_value=-1), patch.object(warm, 'solve_from_angles') as core:
            result = warm.refine_partition(graph, BM['config'], 3, {'seconds': 1, 'max_work': 1}, initial)
        core.assert_not_called()
        self.assertEqual(result['work_counters']['passes'], 0)


if __name__ == '__main__': unittest.main()
