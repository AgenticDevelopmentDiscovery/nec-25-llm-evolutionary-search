"""Bounded conditional planar-window matching on an original periodic signed torus.

Inspired by Khoshbakht-Weigel, arXiv:1710.01670, section II.3. This readable
small-window variant does not reproduce their tuned large-window implementation
and never asserts a global optimum. Original seam edges become fixed-boundary
terms when crossing a window; no coupling is discarded from the original score.
"""
from time import perf_counter
from fractions import Fraction
import math
import numpy as np
from bm_solver import Graph, cut_value
from portfolio_common import deadline_from, result_record, settings, starting_signs
from portfolio_topology import solve_planar, torus_faces


def window_problem(graph, signs, side, row, column, width):
    """Build a planar conditional window plus one fixed boundary spin.

    For crossing edge w_ij, j outside, replace its variable contribution by
    a boundary edge of weight w_ij*s_j to ghost spin +1. The omitted constant
    is (sum crossing w - sum ghost weights)/2. Internal edges are unchanged.
    width<=side-2 prevents a noncontractible interior cycle. O(width²*degree).
    """
    if not 1 <= width <= side - 2:
        raise ValueError('window width must be in 1..side-2')
    nodes = [((row + r) % side) * side + (column + c) % side
             for r in range(width) for c in range(width)]
    local = {node: index for index, node in enumerate(nodes)}
    boundary = [Fraction(0) for node in nodes]
    edges = []
    crossing_sum = Fraction(0)
    for node in nodes:
        for neighbor, weight in graph.neighbors[node]:
            if neighbor in local:
                if node < neighbor:
                    edges.append((local[node], local[neighbor], weight))
            else:
                boundary[local[node]] += Fraction(str(weight)) * int(signs[neighbor])
                crossing_sum += Fraction(str(weight))
    ghost = len(nodes)
    edges.extend((index, ghost, float(weight)) for index, weight in enumerate(boundary) if weight != 0)
    problem = Graph(len(nodes) + 1, edges)
    warm = np.append(signs[nodes], 1).astype(np.int8)
    return problem, nodes, warm, float((crossing_sum - sum(boundary)) / 2)


def solve_window(graph, config, seed, budget, initial_assignment=None):
    """Max-work counts windows, with sparse O(n+m+window²) storage.

    Each completed window matching optimizes exactly that fixed boundary
    problem. A timeout/guard retains the previous feasible assignment. Only
    original full-graph rescoring accepts improvements; global upper_bound=None.
    """
    started = perf_counter()
    cfg = settings(config, {'window_side': 8, 'max_defects': 256})
    if any(type(value) is not int or value < 1 for value in cfg.values()) or cfg['window_side'] > 24:
        raise ValueError('window_side must be 1..24; max_defects must be positive')
    deadline = deadline_from(budget)
    side, faces = torus_faces(graph)
    del faces
    width = min(cfg['window_side'], side - 2)
    rng = np.random.default_rng(seed)
    best = starting_signs(graph, rng, initial_assignment)
    best_value = cut_value(graph, best)
    counts = {'windows': 0, 'conditional_optima': 0, 'limited_windows': 0, 'improvements': 0}
    history = []
    for iteration in range(budget.get('max_work', 10000)):
        remaining = deadline - perf_counter()
        if remaining <= .02:
            break
        row, col = int(rng.integers(side)), int(rng.integers(side))
        problem, nodes, warm, offset = window_problem(graph, best, side, row, col, width)
        remaining = deadline - perf_counter()
        if remaining <= 0:
            break
        solved = solve_planar(problem, {'max_nodes': 24 * 24 + 1, 'max_defects': cfg['max_defects']},
                              seed, {'seconds': remaining, 'max_work': problem.node_count}, warm)
        counts['windows'] += 1
        if solved['optimality_status'] != 'solver_reported_optimal':
            counts['limited_windows'] += 1
            if solved['execution_status'] == 'time_limit':
                break
            continue
        counts['conditional_optima'] += 1
        local = np.array(solved['assignment'], dtype=np.int8)
        # Complement the whole augmented solution to restore ghost=+1.
        local *= int(local[-1])
        candidate = best.copy()
        candidate[nodes] = local[:-1]
        value = cut_value(graph, candidate)
        if value > best_value:
            best, best_value = candidate, value
            counts['improvements'] += 1
        if len(history) < 100:
            history.append({'row': row, 'column': col, 'width': width,
                            'conditional_cut': solved['cut'], 'boundary_offset': offset,
                            'best_original_cut': best_value})
    return result_record('toroidal_window', graph, cfg, seed, budget, started, best,
        status='time_limit' if perf_counter() >= deadline else 'completed', reason='bounded_conditional_windows',
        counters=counts, history=history, implementation='project-conditional-planar-window-matching')
