"""Mathematical and failure-mode acceptance checks; run with unittest discovery."""

# product enumerates only tiny binary spaces, never the public instance ladder.
from itertools import product
# chdir temporarily changes the test working directory and restores it automatically.
from contextlib import chdir
# math supplies exact reference angles and scalar geometric expectations.
import math
# Path and TemporaryDirectory keep test files isolated from user solutions.
from pathlib import Path
# Temporary directories clean up their own test-only inputs and outputs automatically.
from tempfile import TemporaryDirectory
# unittest is the standard-library test runner required by the brief.
import unittest
# patch injects one deliberately stale gain cache to exercise termination refresh.
from unittest.mock import patch

# NumPy is already the sole required project dependency.
import numpy as np

# The solver's public routines and low-level kernels expose the equations under test.
import bm_solver as bm
# The unchanged official evaluator provides an external file/score check.
import evaluate as official
# The CLI is callable without executing it on import.
from run_bm import main as run_cli


# The enumeration helper is intentionally limited by callers to at most four nodes.
def assignments(node_count):
    """Steps 2/9 check: yield independent int8 sign arrays for tiny n (int, e.g. 3).

    Return a generator of shape-(n,) arrays; no mutation; O(2**n*n) total.
    assignments(2) includes [-1,-1],[-1,1],[1,-1],[1,1].
    """
    # repeat=n forms all length-n tuples from the two labels, without a matrix representation.
    for signs in product((-1, 1), repeat=node_count):
        # array copies the tuple into independently writable binary storage.
        yield np.array(signs, dtype=np.int8)


# A small shared collection holds the hand-specified mathematical examples.
def hand_cases():
    """Steps 1–9 checks: no arguments; return (name,Graph,exact optimum) triples.

    No external input is mutated. Each Graph owns its edges. At most four
    nodes per case, so exhaustive verification remains bounded. Example first
    record has a +4 edge and optimum 4.0.
    """
    # Every expected optimum is a hand value from the brief, independent of solve_bm.
    return [
        ("positive_edge", bm.Graph(2, [(0, 1, 4)]), 4.0),
        ("negative_edge", bm.Graph(2, [(0, 1, -4)]), 0.0),
        ("square", bm.Graph(4, [(0, 1, 1), (1, 2, 1), (2, 3, 1), (3, 0, 1)]), 4.0),
        ("triangle", bm.Graph(3, [(0, 1, 1), (1, 2, 1), (0, 2, 1)]), 2.0),
        ("weighted", bm.Graph(3, [(0, 1, 5), (1, 2, 3), (0, 2, 1)]), 8.0),
        ("compatible_signed", bm.Graph(3, [(0, 1, 4), (1, 2, 3), (0, 2, -2)]), 7.0),
        ("frustrated_signed", bm.Graph(3, [(0, 1, 4), (1, 2, -3), (0, 2, -2)]), 2.0),
        ("local_trap", bm.Graph(4, [(0, 1, 3), (2, 3, 3), (0, 2, 2),
                                  (0, 3, 2), (1, 2, 2), (1, 3, 2)]), 10.0),
    ]


# Related acceptance checks are grouped without introducing a solver framework.
class SolverTests(unittest.TestCase):
    """Standard-library runner for Steps 1–9; methods mutate only temporary test objects."""

    # Parsing checks concern input semantics rather than implementation formatting.
    def test_parse_fractional_signed_and_disconnected(self):
        """Step 1: self is TestCase; return None; check owned O(n+m) representation."""
        # The context owns a disposable directory, leaving official inputs untouched.
        with TemporaryDirectory() as directory:
            # Path(directory)/'graph.txt' constructs the disposable input filename.
            path = Path(directory) / "graph.txt"
            # write_text supplies UTF-8 input with isolated node 4 and a zero-weight edge.
            path.write_text("4 2\n1 2 -0.25\n2 3 0\n", encoding="utf-8")
            # Loading must preserve real weights and subtract one from node IDs exactly once.
            graph = bm.load_graph(path)
            # Expected neighbors explicitly require both directions and the isolated node.
            self.assertEqual(graph.neighbors, [[(1, -0.25)], [(0, -0.25), (2, 0.)], [(1, 0.)], []])
            # The objective counts the negative edge once, not once per adjacency entry.
            self.assertEqual(bm.cut_value(graph, [1, -1, 1, 1]), -0.25)
            # Empty edge sets remain valid for positive node counts.
            path.write_text("3 0\n\n", encoding="utf-8")
            # All nodes remain present even though there are no edge records.
            empty = bm.load_graph(path)
            # Assert the representation and both objectives on an edgeless graph.
            self.assertEqual(empty.neighbors, [[], [], []])
            # A cut through no edges has value zero for every assignment.
            self.assertEqual(bm.cut_value(empty, [-1, 1, -1]), 0.)
            # General angles also contribute no terms when m=0.
            self.assertEqual(bm.relaxed_value(empty, [0., 1., 2.]), 0.)

    # Malformed input should fail with actionable messages instead of silently changing the problem.
    def test_malformed_graphs(self):
        """Step 1: self is TestCase; return None; reject bounded malformed examples."""
        # Each pair supplies an input string and the expected informative error fragment.
        cases = [("", "expected n m"), ("0 0\n", "n > 0"), ("2 -1\n", "m >= 0"),
                 ("2.5 0\n", "integers"), ("2 1\n", "expected i j w"),
                 ("2 0\n1 2 1\n", "extra data"), ("2 1\n1 1 2\n", "self-loop"),
                 ("2 1\n0 2 1\n", "endpoints"), ("2 1\n1 3 1\n", "endpoints"),
                 ("2 1\n1.5 2 1\n", "invalid endpoint"), ("2 1\n1 2 nan\n", "finite"),
                 ("2 1\n1 2 inf\n", "finite"), ("2 2\n1 2 1\n2 1 -2\n", "duplicate")]
        # All malformed test files stay inside a disposable directory.
        with TemporaryDirectory() as directory:
            # This path is explicitly selected by the test, never a user solution path.
            path = Path(directory) / "invalid.txt"
            # Iterate named counterexamples so failures identify their exact input.
            for text, message in cases:
                # subTest adds input context while allowing subsequent cases to run.
                with self.subTest(text=text):
                    # Replace this disposable file with the next malformed input.
                    path.write_text(text, encoding="utf-8")
                    # assertRaisesRegex checks the exception type and a meaningful part of its message.
                    with self.assertRaisesRegex(ValueError, message):
                        # Parsing must fail rather than invent missing data.
                        bm.load_graph(path)

    # Validation must happen before any lossy cast to small integers.
    def test_invalid_vectors_and_settings(self):
        """Steps 2–9: self is TestCase; return None; invalid arrays/settings must fail."""
        # A one-edge graph makes validation tests independent of optimization complexity.
        graph = bm.Graph(2, [(0, 1, 4)])
        # The cases include incorrect lengths/shapes, zeros, fractions, and NaNs.
        for signs in ([1], [[1], [-1]], [1, 0], [1, .9], [1, math.nan]):
            # The direct public evaluator must reject each invalid assignment.
            with self.assertRaises(ValueError):
                # No implicit rounding or flattening is allowed.
                bm.cut_value(graph, signs)
        # Invalid relaxed vectors likewise fail shape/finiteness checks.
        with self.assertRaises(ValueError):
            # Infinity cannot represent a direction.
            bm.relaxed_value(graph, [0, math.inf])
        # Invalid tolerances and budgets must not result in silent default behavior.
        for setting in ({"rounding_count": 0}, {"seed": -1}, {"max_sweeps": -1},
                        {"field_rtol": -1}, {"gain_tolerance": math.nan}, {"projection_tolerance": 1}):
            # subTest includes the invalid setting name and value.
            with self.subTest(setting=setting):
                # kwargs expansion is confined to enumerating test cases, not the solver API.
                with self.assertRaises(ValueError):
                    # Every production solver argument still has an explicit named signature.
                    bm.solve_bm(graph, **setting)

    # Exhaustive tiny checks establish hand optima independently of the heuristic.
    def test_hand_objectives_and_binary_embedding(self):
        """Steps 2–3: self is TestCase; return None; enumerate n<=4, checking F and R."""
        # The expected hand values do not come from the heuristic under test.
        for name, graph, expected in hand_cases():
            # Group assertions by the named graph example.
            with self.subTest(name=name):
                # Collect actual objective values for exhaustive comparison.
                cuts = []
                # Each generated vector is independent and covers one tiny assignment.
                for signs in assignments(graph.node_count):
                    # The direct evaluator supplies the binary objective.
                    value = bm.cut_value(graph, signs)
                    # Reversing every label leaves every crossing decision unchanged.
                    self.assertEqual(value, bm.cut_value(graph, -signs))
                    # zeros creates one angle slot per node for the binary embedding.
                    angles = np.zeros(graph.node_count)
                    # Explicitly map +1 to 0 and -1 to pi radians.
                    for node, sign in enumerate(signs):
                        # Only the -1 group points left in the binary angular representation.
                        if sign == -1:
                            # This angle has cosine -1 and sine approximately zero.
                            angles[node] = math.pi
                    # delta is an absolute tolerance suitable for these integer-weight toy objectives.
                    self.assertAlmostEqual(value, bm.relaxed_value(graph, angles), delta=1e-12)
                    # Store this real cut for the tiny global maximum calculation.
                    cuts.append(value)
                # max over ALL assignments proves the expected tiny optimum.
                self.assertEqual(max(cuts), expected)

    # The 120-degree case distinguishes a relaxed objective from any valid discrete cut.
    def test_rounding_geometry_and_ties(self):
        """Steps 3/7: self is TestCase; return None; check exact projections and ties."""
        # This graph has three unit positive edges.
        graph = bm.Graph(3, [(0, 1, 1), (1, 2, 1), (0, 2, 1)])
        # All three arrows originate at the same origin, 120 degrees apart.
        angles = np.array([0., 2 * math.pi / 3, 4 * math.pi / 3])
        # The local continuous representation can score 2.25 although the best binary cut is 2.
        self.assertAlmostEqual(bm.relaxed_value(graph, angles), 2.25)
        # alpha=0 is a horizontal NORMAL and therefore a vertical dividing line.
        np.testing.assert_array_equal(bm.round_angles(angles, 0.), [1, -1, -1])
        # Rotating the normal to 60 degrees changes which two nodes share a group.
        np.testing.assert_array_equal(bm.round_angles(angles, math.pi / 3), [1, 1, -1])
        # Both actual assignments cut exactly two unit edges.
        self.assertEqual(bm.cut_value(graph, bm.round_angles(angles, 0.)), 2.)
        # The second required normal also yields a valid cut of two, not the relaxed value 2.25.
        self.assertEqual(bm.cut_value(graph, bm.round_angles(angles, math.pi / 3)), 2.)
        # Boundary arrows receive +1 even at slightly negative floating projections.
        np.testing.assert_array_equal(bm.round_angles([math.pi / 2, math.pi / 2 + 1e-13], 0.), [1, 1])
        # Outside the documented 1e-12 neighborhood, a negative projection receives -1.
        np.testing.assert_array_equal(bm.round_angles([math.pi / 2 + 1e-8], 0.), [-1])
        # Away from the boundary, normals separated by pi reverse all labels.
        np.testing.assert_array_equal(bm.round_angles(angles, math.pi), -bm.round_angles(angles, 0.))
        # Exact boundary ties demonstrate why the reversal identity needs its qualification.
        self.assertEqual(bm.round_angles([math.pi / 2], math.pi)[0], bm.round_angles([math.pi / 2], 0.)[0])

    # The nonzero field example catches a swapped atan2 argument order or sign error.
    def test_coordinate_update_and_zero_fields(self):
        """Step 5: self is TestCase; return None; verify opposite-field unit geometry."""
        # Only AB and AC are present; there must be no accidental BC edge.
        graph = bm.Graph(3, [(0, 1, 2), (0, 2, 1)])
        # A starts at 45 degrees, B points right, and C points upward.
        angles = np.array([math.pi / 4, 0., math.pi / 2])
        # Elementwise cos/sin create synchronized caches from the initial radian vector.
        cosines = np.cos(angles)
        # Sines are separate owned storage for immediate sequential updates.
        sines = np.sin(angles)
        # Record the whole R, equal to the incident contribution because only two edges exist.
        before = bm.relaxed_value(graph, angles)
        # Perform the exact update on node A=0, mutating only its cache entries.
        bm.update_coordinate(graph, 0, angles, cosines, sines)
        # The expected arrow is exactly opposite the (2,1) field, with unit length.
        np.testing.assert_allclose([cosines[0], sines[0]], [-2 / math.sqrt(5), -1 / math.sqrt(5)], atol=1e-15)
        # The norm check distinguishes a unit arrow from the longer field vector.
        self.assertAlmostEqual(math.hypot(cosines[0], sines[0]), 1.)
        # The given initial relaxed contribution is approximately 0.439340.
        self.assertAlmostEqual(before, 1.5 - 3 / (2 * math.sqrt(2)))
        # The optimized contribution is approximately 2.618034.
        self.assertAlmostEqual(bm.relaxed_value(graph, angles), 1.5 + math.sqrt(5) / 2)
        # Zero, all-zero-weight, isolated, and near-cancelling fields must keep A unchanged.
        for zero_graph, initial in [(bm.Graph(1, []), [1.]),
                                    (bm.Graph(2, [(0, 1, 0)]), [1., 0.]),
                                    (bm.Graph(3, [(0, 1, 1), (0, 2, 1)]), [1., 0., math.pi])]:
            # array owns these small diagnostic angles.
            state = np.array(initial)
            # Keep a copy to prove that a negligible field causes no rotation.
            saved = state.copy()
            # The caller supplies synchronized cosine/sine arrays and the default scale tolerance.
            changed = bm.update_coordinate(zero_graph, 0, state, np.cos(state), np.sin(state))
            # Exact cancellation and floating pi cancellation both qualify as negligible here.
            self.assertFalse(changed)
            # Keeping the angle unchanged must not create a NaN.
            np.testing.assert_array_equal(state, saved)

    # A manual sequential sweep and a full history check test the update schedule and stopping rule.
    def test_sequential_sweeps_monotonicity_and_stopping(self):
        """Steps 5–6: self is TestCase; return None; check seeded order and scaled R changes."""
        # Signed fractional weights also exercise cancellation and noninteger objectives.
        graph = bm.Graph(4, [(0, 1, .75), (1, 2, -1.25), (2, 3, 2.5), (0, 3, .125)])
        # This fixed angular vector is owned by the test and must remain unchanged.
        initial = np.array([.2, 1.1, 2., 4.])
        # Copy the expected working angles for an independently scheduled manual sweep.
        expected = initial.copy()
        # Build caches from that manual state.
        cosines = np.cos(expected)
        # Each manual coordinate update will synchronize both caches.
        sines = np.sin(expected)
        # A fresh local seed fixes the permutation used by both independent executions.
        order = np.random.default_rng(19).permutation(4)
        # Visit each node sequentially, measuring R before each individual update.
        for node in order:
            # A decrease at the coordinate level should be limited to floating roundoff.
            before = bm.relaxed_value(graph, expected)
            # Apply exactly this coordinate to the immediately updated state.
            bm.update_coordinate(graph, int(node), expected, cosines, sines)
            # These tiny graphs have weight scale below 5, making 1e-12 conservative.
            self.assertGreaterEqual(bm.relaxed_value(graph, expected), before - 1e-12)
        # One sweep with an independently reset identical RNG must match that schedule exactly.
        actual, history = bm.coordinate_ascent(graph, initial, np.random.default_rng(19), max_sweeps=1)
        # Exact array equality catches stale simultaneous updates and ordering changes.
        np.testing.assert_array_equal(actual, expected)
        # This nonstationary first sweep exhausts its one-sweep budget before tolerance convergence.
        self.assertEqual(history["stop_reason"], "max_sweeps")
        # The caller's initialization is not reused as mutable workspace.
        np.testing.assert_array_equal(initial, [.2, 1.1, 2., 4.])
        # Returned storage must not alias initial input memory.
        self.assertFalse(np.shares_memory(actual, initial))
        # A zero budget is explicitly iteration-limited, with no fabricated sweep records.
        unused, empty_history = bm.coordinate_ascent(graph, initial, np.random.default_rng(19), max_sweeps=0)
        # No sweep means the copy remains exactly the initial vector.
        np.testing.assert_array_equal(unused, initial)
        # The stop reason documents the budget limit.
        self.assertEqual(empty_history["stop_reason"], "max_sweeps")
        # An edgeless graph reaches the configured full-sweep tolerance after its first sweep.
        unused, empty_history = bm.coordinate_ascent(bm.Graph(2, []), [0., 1.], np.random.default_rng(19))
        # The label describes a numerical stopping rule rather than a proof of optimality.
        self.assertEqual(empty_history["stop_reason"], "sweep_tolerance")
        # Check several graph scales, including very small and very large weight units.
        for scale in (1e-8, 1., 1e8):
            # Explicitly construct scaled fixed edges without changing the original graph.
            edges = []
            # Weight scaling should preserve the mathematical coordinate direction.
            for i, j, weight in graph.edges:
                # append creates a new edge tuple in the requested weight units.
                edges.append((i, j, scale * weight))
            # The same seeded sweep schedule is used at every scale.
            unused, scaled_history = bm.coordinate_ascent(bm.Graph(4, edges), initial, np.random.default_rng(4))
            # Every recorded decrease must fall inside the documented weight-scaled allowance.
            for sweep in scaled_history["sweeps"]:
                # The measurements are real before/after values, not a cumulative maximum.
                self.assertGreaterEqual(sweep["improvement"], -sweep["roundoff_allowance"])

    # Independent direct differences test gains and every intermediate incremental update.
    def test_gains_direct_differences_and_incremental_updates(self):
        """Step 8: self is TestCase; return None; signed fractional tiny exhaustive check."""
        # Mix edge signs, zeros, fractions, and an isolated node.
        graphs = [bm.Graph(4, [(0, 1, .25), (1, 2, -.75), (0, 2, 1.125)]),
                  bm.Graph(3, [(0, 1, -2.5), (1, 2, 0.)])]
        # Both graphs are tiny enough to check every assignment.
        for graph in graphs:
            # Each original vector remains unchanged during the direct-difference comparison.
            for signs in assignments(graph.node_count):
                # Compute the gain vector once before independent single-flip evaluations.
                gains = bm.compute_flip_gains(graph, signs)
                # The original direct cut is the common subtraction baseline.
                before = bm.cut_value(graph, signs)
                # Every possible single node must obey the gain identity.
                for node in range(graph.node_count):
                    # Copying avoids accumulating unrelated moves in the direct comparison.
                    flipped = signs.copy()
                    # Negating one sign constructs the neighboring assignment independently.
                    flipped[node] *= -1
                    # Direct F difference is independent of the adjacency gain cache.
                    self.assertAlmostEqual(gains[node], bm.cut_value(graph, flipped) - before)
                # Exercise several consecutive kernel flips, including repeated nodes.
                for node in (0, 1, 2, 0):
                    # This kernel mutates both working signs and cached gains.
                    bm.flip_node(graph, signs, gains, node)
                    # Fresh recomputation after EACH flip catches old/new-sign mistakes immediately.
                    np.testing.assert_allclose(gains, bm.compute_flip_gains(graph, signs), atol=1e-14)
        # The required weighted-triangle gain values are independently specified hand values.
        graph = bm.Graph(3, [(0, 1, 5), (1, 2, 3), (0, 2, 1)])
        # The prescribed initial assignment has cut 6.
        signs = np.array([-1, 1, 1], dtype=np.int8)
        # Its three gains are (-6,-2,+2), so C is the improving node.
        gains = bm.compute_flip_gains(graph, signs)
        # Confirm the exact old gains before mutation.
        np.testing.assert_array_equal(gains, [-6., -2., 2.])
        # Flip C=2 using its OLD sign +1 in every neighbor correction.
        bm.flip_node(graph, signs, gains, 2)
        # These updated gains detect the sign error called out in the brief.
        np.testing.assert_array_equal(gains, [-4., -8., -2.])

    # Best-improvement must remain greedy even when a worsening move could escape a trap.
    def test_local_search_and_trap(self):
        """Step 8: self is TestCase; return None; audit improving moves and the 8/10 trap."""
        # Enumerate small graph examples and all of their possible initial signs.
        for name, graph, optimum in hand_cases():
            # Exhaustive testing here is bounded by n<=4, not applied to public inputs.
            for initial in assignments(graph.node_count):
                # verify_moves=True records actual per-move F values for these tiny examples only.
                signs, cut, history = bm.local_search(graph, initial, verify_moves=True)
                # Greedy polishing cannot lower the starting cut on these exact hand examples.
                self.assertGreaterEqual(cut, bm.cut_value(graph, initial))
                # Fresh final gains are the real termination condition.
                self.assertLessEqual(float(np.max(bm.compute_flip_gains(graph, signs))), 1e-10)
                # The returned vector must own its storage independently of the supplied initial signs.
                self.assertFalse(np.shares_memory(signs, initial))
                # Recorded actual direct cut changes must agree with the predicted gains.
                for move in history["moves"]:
                    # Strict positivity enforces that this is not annealing or perturbation search.
                    self.assertGreater(move["after"], move["before"])
                    # The expected actual change comes from independent objective evaluations.
                    self.assertAlmostEqual(move["after"] - move["before"], move["gain"])
        # Select the last named hand case, whose exact optimum was independently enumerated as 10.
        name, trap, optimum = hand_cases()[-1]
        # This particular initial assignment is a true single-flip local optimum at cut 8.
        initial = np.array([1, 1, -1, -1], dtype=np.int8)
        # Every initial gain is -1, so a greedy solver must stop immediately.
        np.testing.assert_array_equal(bm.compute_flip_gains(trap, initial), [-1., -1., -1., -1.])
        # Polishing cannot secretly add an out-of-scope escape stage.
        signs, cut, history = bm.local_search(trap, initial)
        # The exact returned value distinguishes a local optimum from global optimum 10.
        self.assertEqual(cut, 8.)
        # No negative-gain move may be accepted.
        self.assertEqual(history["accepted_flips"], 0)
        # Flip B manually only to demonstrate the forbidden worsening escape path.
        initial[1] *= -1
        # The first escape move loses one point, so greedy search correctly rejected it.
        self.assertEqual(bm.cut_value(trap, initial), 7.)
        # The second manual move flips C and attains the actual optimum.
        initial[2] *= -1
        # This is an explanatory counterexample, not a change to the local-search policy.
        self.assertEqual(bm.cut_value(trap, initial), 10.)

    # A synthetic stale cache exercises the mandatory fresh-gain termination check.
    def test_local_search_refreshes_apparent_termination(self):
        """Step 8: self is TestCase; return None; repair an intentionally stale initial cache."""
        # A positive edge with equal labels has a known improving move of gain 4.
        graph = bm.Graph(2, [(0, 1, 4)])
        # Save the true function so only its first result is deliberately corrupted.
        original = bm.compute_flip_gains
        # This list counts calls without changing the graph or the solver's function signature.
        calls = []
        # The nested diagnostic function supplies the same arguments as the real gain evaluator.
        def stale_first(current_graph, signs):
            """Step 8 test injection: Graph and sign vector in; gains out; mutate call counter only."""
            # append records that a full recomputation was requested.
            calls.append(1)
            # Only the initial cache pretends that all gains are non-improving.
            if len(calls) == 1:
                # zeros returns the intentionally stale two-entry gain vector.
                return np.zeros(2)
            # Subsequent calls use the genuine current-sign calculation.
            return original(current_graph, signs)
        # patch is scoped to this test block and restores the original function afterward.
        with patch("bm_solver.compute_flip_gains", side_effect=stale_first):
            # Apparent zero-gain termination must be refreshed and discover the +4 move.
            signs, cut, history = bm.local_search(graph, [1, 1])
        # A solver that skipped the termination refresh would incorrectly return zero.
        self.assertEqual(cut, 4.)
        # Best-improvement breaks the equal initial gains in favor of node 0.
        np.testing.assert_array_equal(signs, [-1, 1])

    # Degenerate graphs must also work through the entire pipeline, not just their evaluators.
    def test_empty_zero_weight_and_gain_threshold(self):
        """Steps 4–9: self is TestCase; return None; degenerate whole solves stay finite."""
        # Empty and zero-weight edge sets must never require dividing by a field norm.
        for graph in (bm.Graph(3, []), bm.Graph(3, [(0, 1, 0.)])):
            # Two rounding directions are sufficient to exercise every stage on this diagnostic case.
            signs, cut, history = bm.solve_bm(graph, rounding_count=2)
            # The zero baseline remains a valid incumbent throughout.
            self.assertEqual(cut, 0.)
            # No node has a nonzero field, so exactly one no-change sweep meets tolerance.
            self.assertEqual(len(history["continuous"]["sweeps"]), 1)
            # The all-plus baseline wins every equal-cut comparison.
            np.testing.assert_array_equal(signs, [1, 1, 1])
        # The absolute threshold intentionally ignores sufficiently small weight-unit improvements.
        tiny = bm.Graph(2, [(0, 1, 1e-12)])
        # The default 1e-10 threshold refuses this +1e-12 move, as documented.
        signs, cut, history = bm.local_search(tiny, [1, 1])
        # This tolerance-based stop is not a claim of exact stationarity.
        self.assertEqual(cut, 0.)
        # An explicitly zero threshold permits the same real positive improvement.
        signs, cut, history = bm.local_search(tiny, [1, 1], gain_tolerance=0.)
        # The direct objective confirms the accepted tiny move.
        self.assertEqual(cut, 1e-12)

    # Retention and reproducibility concern every generated candidate, not just the final score.
    def test_retention_reproducibility_and_tiny_gaps(self):
        """Steps 4–9: self is TestCase; return None; repeat seeded runs and bound tiny gaps."""
        # These are correctness checks rather than a demand that the heuristic always be exact.
        for name, graph, optimum in hand_cases():
            # Fixed iteration/count settings keep this test deterministic in one environment.
            signs, cut, history = bm.solve_bm(graph, seed=42, max_sweeps=40, rounding_count=8)
            # Repeating with the identical settings must reproduce the entire mathematical trace.
            again, again_cut, again_history = bm.solve_bm(graph, seed=42, max_sweeps=40, rounding_count=8)
            # Array equality covers assignment reproducibility, not merely objective equality.
            np.testing.assert_array_equal(signs, again)
            # Timing is deliberately absent from solve_bm's reproducible history.
            self.assertEqual(history, again_history)
            # The direct cut is computed from the actual returned assignment.
            self.assertEqual(cut, bm.cut_value(graph, signs))
            # The polished all-+1 baseline is one required retention competitor.
            self.assertGreaterEqual(cut, history["baseline"]["polished_cut"])
            # A valid retained assignment is also no worse than the raw zero baseline.
            self.assertGreaterEqual(cut, 0.)
            # Every rounded candidate was polished and evaluated, including exact ties.
            for direction in history["roundings"]:
                # No generated polished candidate may be better than the saved incumbent.
                self.assertGreaterEqual(cut, direction["polished_cut"])
                # Tiny-case exhaustive optimum bounds the heuristic from above.
                self.assertLessEqual(direction["polished_cut"], optimum)
            # A heuristic gap is permitted; a value above the true optimum is a correctness error.
            self.assertGreaterEqual(optimum - cut, 0.)
            # Returned arrays from independent solves must not alias each other.
            self.assertFalse(np.shares_memory(signs, again))
            # Mutating one returned array must leave the other solve's incumbent unchanged.
            signs[0] *= -1
            # The independently retained copy still has its originally reported direct score.
            self.assertEqual(bm.cut_value(graph, again), again_cut)
        # The signed graph with no positive edges must retain its zero-cut polished baseline on ties.
        signs, cut, history = bm.solve_bm(bm.Graph(2, [(0, 1, -4)]), rounding_count=2)
        # Exact ties preserve the earlier incumbent rather than replacing it by the last direction.
        self.assertEqual(history["retained"], "baseline")

    # File-format and CLI checks use the official loader without modifying official code.
    def test_assignment_official_round_trip_and_cli(self):
        """Steps 1/9: self is TestCase; return None; use disposable files and external evaluator."""
        # Temporary outputs never overwrite a student solution or public graph.
        with TemporaryDirectory() as directory:
            # Path joins define separate input, assignment, and optional history files.
            source = Path(directory) / "example.txt"
            # This graph includes a fractional negative weight in official file format.
            source.write_text("3 3\n1 2 4\n2 3 3\n1 3 -2.5\n", encoding="utf-8")
            # Explicit output selection authorizes writing only this disposable file.
            output = Path(directory) / "out.txt"
            # History is a separate JSON file, never included as assignment entries.
            history_path = Path(directory) / "history.json"
            # main accepts an explicit argv list; small fixed budgets keep this smoke check bounded.
            run_cli(["--instance", str(source), "--output", str(output), "--history", str(history_path),
                     "--seed", "42", "--max-sweeps", "20", "--roundings", "4"])
            # The official graph loader independently converts the file's 1-based indices.
            n, i, j, w = official.load_instance(source)
            # The official assignment loader independently checks length and ±1 membership.
            signs, status = official.load_solution(output, n)
            # A successful official validation is necessary for a project solution file.
            self.assertEqual(status, "ok")
            # Both independent evaluators must give exactly the hand cut 7.
            self.assertEqual(official.cut_value(i, j, w, signs), 7.)
            # Build the independently expected integer records in original node order.
            expected_lines = []
            # Every official-loaded sign must correspond to exactly one signed integer record.
            for sign in signs:
                # +d emits '+1' or '-1', never a float such as '1.0'.
                expected_lines.append(f"{int(sign):+d}")
            # The output contains only these integer records, with no header.
            self.assertEqual(output.read_text(encoding="utf-8").splitlines(), expected_lines)
            # Invalid assignments must fail before any output file is created.
            invalid_path = Path(directory) / "must_not_exist.txt"
            # This failure must happen before write_assignment opens its destination.
            with self.assertRaises(ValueError):
                # A zero label violates the exact binary output contract.
                bm.write_assignment(invalid_path, [1, 0, 1], bm.load_graph(source))
            # No invalid partial solution should appear on disk.
            self.assertFalse(invalid_path.exists())

    # Default smoke output must not silently replace an existing solution without explicit selection.
    def test_default_output_requires_explicit_overwrite(self):
        """Step 9 plumbing: self is TestCase; return None; default files survive repeat runs."""
        # Both the current directory and all files are scoped to a disposable test directory.
        with TemporaryDirectory() as directory, chdir(directory):
            # A relative source path exercises the real default smoke destination logic.
            source = Path("example.txt")
            # A two-node graph keeps the initial demonstration bounded to one sweep/direction.
            source.write_text("2 1\n1 2 4\n", encoding="utf-8")
            # Omitting --output selects the separate smoke directory on this first run.
            run_cli(["--instance", str(source), "--max-sweeps", "1", "--roundings", "1"])
            # The default basename is derived from the source's original filename.
            output = Path("solutions_bm_smoke/example.txt")
            # Save exact bytes so any unauthorized overwrite would be visible.
            before = output.read_bytes()
            # A second omitted-output run must ask for explicit path selection via a usage error.
            with self.assertRaises(SystemExit) as failure:
                # No solver runs or output writes should occur after this early guard fails.
                run_cli(["--instance", str(source)])
            # argparse's status 2 identifies a user-input error rather than a successful solve.
            self.assertEqual(failure.exception.code, 2)
            # The previously created assignment remains byte-for-byte intact.
            self.assertEqual(output.read_bytes(), before)


# Direct test execution is also supported, although discovery from the root is the documented command.
if __name__ == "__main__":
    # unittest.main discovers the TestCase methods in this module and reports failures.
    unittest.main()
