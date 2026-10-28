"""Actual original-instance contract checks; no model or server required."""
import importlib.util
from pathlib import Path
import unittest
import json
import subprocess
import sys
import tempfile
import numpy as np

path = Path(__file__).resolve().parents[1] / 'backend.py'
spec = importlib.util.spec_from_file_location('classroom_backend', path)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


class ClassroomTests(unittest.TestCase):
    def test_seeded_parent_child_and_retention(self):
        labels = b.seed_labels(3); before = labels.copy()
        parent = b.run_strategy(b.PARENT, 3, labels)
        child = b.run_strategy(b.NUMERICAL_CHILD, 3, parent['assignment'])
        self.assertEqual(parent['cut'], 58)
        self.assertEqual(child['cut'], 68)
        self.assertEqual(child['score'], 1)
        self.assertEqual(child['proof_status'], 'unproven')
        np.testing.assert_array_equal(labels, before)
        np.testing.assert_array_equal(b.seed_labels(3), labels)
        self.assertEqual(b.score_labels(child['assignment'])['cut'], child['cut'])

    def test_reject_invalid_labels_and_unbounded_program(self):
        with self.assertRaises(ValueError): b.score_labels([0] * 100)
        with self.assertRaises(ValueError): b.run_strategy(b.PARENT, -1)
        with self.assertRaises(ValueError): b.validate_strategy({'stages': []})
        with self.assertRaises(ValueError): b.validate_strategy({'stages': [{'backend':'annealing','config':{},'max_work':5_000_000_000,'fresh':False}]})
        with self.assertRaises(ValueError): b.validate_strategy({'stages': [{'backend':'shell','config':{},'max_work':1,'fresh':False}]})
        with self.assertRaises(ValueError): b.validate_strategy({'stages': [{'backend':'bm','config':{'max_sweeps':20000},'max_work':1,'fresh':False}]})

    def test_actual_worker_cli_and_output_verification(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            initial = b.run_strategy(b.PARENT, 3)['assignment']
            request = folder / 'request.json'
            output = folder / 'result.json'
            request.write_text(json.dumps({'strategy': b.NUMERICAL_CHILD, 'seed': 3, 'initial': initial}))
            subprocess.run([sys.executable, str(path), '--request', str(request), '--output', str(output)], check=True, timeout=4)
            result = json.loads(output.read_text())
            self.assertEqual(result['cut'], 68)
            self.assertEqual(b.score_labels(result['assignment'])['cut'], result['cut'])

    def test_numeric_score_is_recomputed_not_supplied(self):
        state = b.score_labels(b.seed_labels(3))
        self.assertEqual(state['cut'], 0)
        self.assertNotEqual(state['score'], 1)
        self.assertEqual(len(state['assignment']),100)


if __name__ == '__main__': unittest.main()
