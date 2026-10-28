"""Classroom warm refinement using the unchanged rank-two numerical primitives."""
from time import perf_counter

import numpy as np

from bm_solver import angles_from_signs, cut_value, perturb_angles, solve_from_angles, validate_signs
from portfolio_common import deadline_from, result_record


PERTURB_SCALE = 0.35  # Fixed angular half-width in radians, disclosed to Luna.


def refine_partition(graph, config, seed, budget, initial_assignment):
    """One lift/perturb/optimize/round pass, retaining a better input partition."""
    started = perf_counter()
    deadline = deadline_from(budget)
    initial = validate_signs(initial_assignment, graph.node_count)
    initial_cut = cut_value(graph, initial)
    if budget.get('max_work', 1) != 1:
        raise ValueError('classroom Burer–Monteiro refinement requires one pass')
    if perf_counter() >= deadline:
        result = result_record('bm', graph, config, seed, budget, started, initial,
                               status='time_limit', reason='before_retained_refinement', counters={'passes': 0})
    else:
        # Separate local streams make both the perturbation and sweep order reproducible.
        noise_seed, sweep_seed = np.random.SeedSequence([seed, 0x424D]).spawn(2)
        angles = perturb_angles(angles_from_signs(initial), np.random.default_rng(noise_seed), PERTURB_SCALE)
        signs, _, history = solve_from_angles(graph, angles, np.random.default_rng(sweep_seed),
                                              seed=seed, **config)
        candidate_cut = cut_value(graph, signs)
        retained = signs if candidate_cut > initial_cut else initial
        result = result_record('bm', graph, config, seed, budget, started, retained,
                               status='time_limit' if perf_counter() >= deadline else 'completed',
                               reason='retained_partition_refinement', counters={'passes': 1}, history=history,
                               implementation='classroom-retained-bm-refinement-v1')
        result['proposed_cut'] = candidate_cut
    result.update(initialization='retained_partition_lift_perturb_refine', incoming_cut=initial_cut,
                  perturb_scale_radians=PERTURB_SCALE)
    return result
