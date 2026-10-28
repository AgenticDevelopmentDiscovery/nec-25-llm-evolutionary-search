"""Sparse parallel tempering plus paired Houdayer/isoenergetic cluster moves.

Zhu, Ochoa and Katzgraber, arXiv:1501.05630. Search uses the supplied original
couplings; it never generates substitute disorder. Returned cuts are heuristic.
"""
from time import perf_counter
import math
import numpy as np
from bm_solver import cut_value, compute_flip_gains, flip_node
from portfolio_common import deadline_from, result_record, settings, starting_signs


def cluster_pair(graph, first, second, rng):
    """Flip a connected disagreement component in both owned replicas.

    The pair's total H (equivalently total F) is invariant. This function copies
    caller arrays. A global flip of the first replica suppresses trivial large
    disagreement components using zero-field complement symmetry.
    """
    a, b = first.copy(), second.copy()
    disagree = a != b
    if np.count_nonzero(disagree) > graph.node_count // 2:
        a *= -1
        disagree = a != b
    choices = np.flatnonzero(disagree)
    if not len(choices):
        return a, b, 0
    root = int(rng.choice(choices))
    seen = {root}
    queue = [root]
    for node in queue:
        for neighbor, weight in graph.neighbors[node]:
            if weight != 0 and disagree[neighbor] and neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    a[queue] *= -1
    b[queue] *= -1
    return a, b, len(queue)


def swap_log_probability(beta_a, beta_b, cut_a, cut_b):
    """Log PT ratio in maximized-cut units: H=W-2F, no sign/factor ambiguity."""
    return 2 * (beta_a - beta_b) * (cut_b - cut_a)


def solve_pt_icm(graph, config, seed, budget, initial_assignment=None):
    """Two replicas per temperature; max_work counts full PT/ICM sweep cycles.

    Storage O(n*T+m), not n*n. Metropolis ΔH=-2*gain, adjacent-temperature
    swaps and low-temperature paired clusters retain an independently scored
    global incumbent. Cooperative checks complement the runner's hard timeout.
    """
    started = perf_counter()
    cfg = settings(config, {'temperatures': 8, 'temperature_min': .1, 'temperature_max': 5., 'cluster_temperature_max': 1.})
    if type(cfg['temperatures']) is not int or not 2 <= cfg['temperatures'] <= 32:
        raise ValueError('temperatures must be an integer in 2..32')
    for key in ('temperature_min', 'temperature_max', 'cluster_temperature_max'):
        if isinstance(cfg[key], bool) or not isinstance(cfg[key], (int, float)) or not math.isfinite(cfg[key]) or cfg[key] <= 0:
            raise ValueError('temperatures must be finite and positive')
    if cfg['temperature_min'] >= cfg['temperature_max']:
        raise ValueError('temperature_min must be less than temperature_max')
    deadline = deadline_from(budget)
    rng = np.random.default_rng(seed)
    best = starting_signs(graph, rng, initial_assignment)
    best_value = cut_value(graph, best)
    counts = {'sweeps': 0, 'proposals': 0, 'accepted': 0, 'swaps': 0, 'cluster_moves': 0, 'cluster_nodes': 0}
    if perf_counter() >= deadline or budget.get('max_work', 10000) == 0:
        return result_record('pt_icm', graph, cfg, seed, budget, started, best,
            status='time_limit' if perf_counter() >= deadline else 'completed', counters=counts)
    temps = np.geomspace(cfg['temperature_min'], cfg['temperature_max'], cfg['temperatures'])
    beta = 1 / temps
    states = rng.choice(np.array([-1, 1], dtype=np.int8), size=(len(temps), 2, graph.node_count))
    states[0, 0] = best.copy()
    gains = np.array([[compute_flip_gains(graph, state) for state in pair] for pair in states])
    values = np.array([[cut_value(graph, state) for state in pair] for pair in states])
    history = []

    def retain(t, r):
        nonlocal best, best_value
        # Floating trajectory totals only trigger a check; original F chooses the witness.
        if values[t, r] > best_value + 1e-10:
            actual = cut_value(graph, states[t, r])
            values[t, r] = actual
            if actual > best_value:
                best, best_value = states[t, r].copy(), actual

    for t in range(len(temps)):
        for r in range(2):
            retain(t, r)
    for sweep in range(budget.get('max_work', 10000)):
        complete = True
        for t in range(len(temps)):
            for r in range(2):
                for step, node in enumerate(rng.permutation(graph.node_count)):
                    if step % 64 == 0 and perf_counter() >= deadline:
                        complete = False
                        break
                    gain = float(gains[t, r, node])
                    counts['proposals'] += 1
                    if gain >= 0 or rng.random() < math.exp(2 * beta[t] * gain):
                        flip_node(graph, states[t, r], gains[t, r], int(node))
                        values[t, r] += gain
                        counts['accepted'] += 1
                    if step % 64 == 63:
                        retain(t, r)
                retain(t, r)
                if not complete:
                    break
            if not complete:
                break
            if temps[t] <= cfg['cluster_temperature_max'] and perf_counter() < deadline:
                a, b, size = cluster_pair(graph, states[t, 0], states[t, 1], rng)
                states[t, 0], states[t, 1] = a, b
                gains[t] = [compute_flip_gains(graph, a), compute_flip_gains(graph, b)]
                values[t] = [cut_value(graph, a), cut_value(graph, b)]
                counts['cluster_moves'] += int(size > 0)
                counts['cluster_nodes'] += size
                retain(t, 0)
                retain(t, 1)
        if not complete:
            break
        for t in range(sweep % 2, len(temps) - 1, 2):
            if perf_counter() >= deadline:
                complete = False
                break
            for r in range(2):
                log_p = swap_log_probability(beta[t], beta[t + 1], values[t, r], values[t + 1, r])
                if log_p >= 0 or rng.random() < math.exp(log_p):
                    states[[t, t + 1], r] = states[[t + 1, t], r].copy()
                    gains[[t, t + 1], r] = gains[[t + 1, t], r].copy()
                    values[[t, t + 1], r] = values[[t + 1, t], r].copy()
                    counts['swaps'] += 1
        counts['sweeps'] += int(complete)
        if len(history) < 100:
            history.append({'sweep': sweep, 'best_cut': best_value})
        if not complete:
            break
    return result_record('pt_icm', graph, cfg, seed, budget, started, best,
        status='time_limit' if perf_counter() >= deadline else 'completed', reason='bounded_tempering_cycles',
        counters=counts, history=history, implementation='project-PT-paired-isoenergetic-clusters')
