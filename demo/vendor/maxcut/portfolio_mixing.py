"""Sparse higher-rank Mixing coordinate descent with independent cut rounding.

Wang, Chang and Kolter, arXiv:1706.00476, Algorithm 1. This is a bounded
heuristic implementation, not a certified SDP optimizer or an exact Max-Cut solver.
"""
from time import perf_counter
import numpy as np
from bm_solver import cut_value, compute_flip_gains, flip_node
from portfolio_common import deadline_from, result_record, settings, starting_signs


def mixing_coordinate(graph, vectors, node):
    """Minimize sum w_ij <v_i,v_j> over one unit vector; leave zero fields alone."""
    field = np.zeros(vectors.shape[1])
    for neighbor, weight in graph.neighbors[node]:
        field += weight * vectors[neighbor]
    norm = np.linalg.norm(field)
    if not np.isfinite(norm):
        raise FloatingPointError('nonfinite Mixing field')
    if norm > 1e-14:
        vectors[node] = -field / norm


def solve_mixing(graph, config, seed, budget, initial_assignment=None):
    """Optimize n*rank vectors, round and polish within one deadline; no input writes.

    max_work counts full coordinate sweeps. Storage O(n*rank+m); arithmetic
    O(m*rank) per sweep. Warm signs seed a noisy rank-one embedding and are
    independently retained. No encountered relaxed value is called an upper bound.
    """
    started = perf_counter()
    cfg = settings(config, {'rank': 8, 'rounding_count': 32, 'warm_noise': .1, 'polish_flips': 10000})
    if type(cfg['rank']) is not int or not 2 <= cfg['rank'] <= 64:
        raise ValueError('Mixing rank must be an integer in 2..64')
    if any(type(cfg[k]) is not int or cfg[k] < 0 for k in ('rounding_count', 'polish_flips')) or cfg['rounding_count'] < 1:
        raise ValueError('invalid Mixing work counts')
    if not isinstance(cfg['warm_noise'], (int, float)) or isinstance(cfg['warm_noise'], bool) or not np.isfinite(cfg['warm_noise']) or cfg['warm_noise'] <= 0:
        raise ValueError('warm_noise must be finite and positive')
    deadline = deadline_from(budget)
    rng = np.random.default_rng(seed)
    best = starting_signs(graph, rng, initial_assignment)
    best_value = cut_value(graph, best)
    sweeps = rounds = flips = 0
    history = []
    if perf_counter() < deadline and budget.get('max_work', 10000) > 0:
        vectors = rng.normal(size=(graph.node_count, cfg['rank']))
        if initial_assignment is not None:
            vectors *= cfg['warm_noise']
            vectors[:, 0] += best
        vectors /= np.linalg.norm(vectors, axis=1)[:, None]
        for sweep in range(budget.get('max_work', 10000)):
            complete = True
            for node in rng.permutation(graph.node_count):
                if perf_counter() >= deadline:
                    complete = False
                    break
                mixing_coordinate(graph, vectors, int(node))
            sweeps += int(complete)
            # Round partial iterates too, when time remains; no work is hidden after a deadline.
            for repeat in range(cfg['rounding_count']):
                if perf_counter() >= deadline:
                    break
                direction = rng.normal(size=cfg['rank'])
                signs = np.where(vectors @ direction >= 0, 1, -1).astype(np.int8)
                rounds += 1
                value = cut_value(graph, signs)
                if value > best_value:
                    best, best_value = signs.copy(), value
            if len(history) < 100:
                history.append({'sweeps': sweeps, 'roundings': rounds, 'best_cut': best_value})
            if not complete or perf_counter() >= deadline:
                break
        gains = compute_flip_gains(graph, best)
        while flips < cfg['polish_flips'] and perf_counter() < deadline and gains.max() > 1e-10:
            flip_node(graph, best, gains, int(np.argmax(gains)))
            flips += 1
    return result_record('mixing', graph, cfg, seed, budget, started, best,
        status='time_limit' if perf_counter() >= deadline else 'completed', reason='bounded_coordinate_sweeps',
        counters={'sweeps': sweeps, 'roundings': rounds, 'polish_flips': flips}, history=history,
        implementation='project-sparse-higher-rank-Mixing')
