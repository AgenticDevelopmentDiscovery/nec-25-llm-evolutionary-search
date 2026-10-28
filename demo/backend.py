"""Portable classroom adapter over unchanged, independently scored Max-Cut kernels.

Strategy programs are bounded stage lists, not arbitrary executable Python.
The server runs this interpreter in owned subprocesses for hard cancellation.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from time import perf_counter

import numpy as np

HERE = Path(__file__).resolve().parent
VENDOR = HERE / 'vendor/maxcut'
sys.path.insert(0, str(VENDOR))
from bm_solver import cut_value, load_graph, validate_signs
from solver_portfolio import solve
import evaluate

INSTANCE = HERE / 'data/torus_pm_10_s11.txt'
GRAPH_SHA256 = 'b57a871c1c196bd417b651ef3f9a9998d4a77076a93928deafee193e7e149704'
COMPARISON_INSTANCE = 'rand_pm_1000_s23.txt'
COMPARISON_GRAPH_SHA256 = 'ebb1ee5df894bb2159cd29b2a65d237fa72c9d1fdc2080b2cc7cdb16f25a0503'
NEW_INSTANCE = 'dense_gauss_100_s14.txt'
NEW_GRAPH_SHA256 = '3e43712162847581b5e10fb69feb7dc11845e6280b7fb8e5759d2abc56f75a34'

def instance_spec(instance=None):
    name = str(instance or INSTANCE.name)
    if name == INSTANCE.name:
        path, expected, side = INSTANCE, GRAPH_SHA256, 10
    elif name == NEW_INSTANCE:
        path, expected, side = HERE / 'data' / name, NEW_GRAPH_SHA256, 10
    elif name == COMPARISON_INSTANCE:
        path, expected, side = HERE / 'data' / name, COMPARISON_GRAPH_SHA256, 32
    else:
        raise ValueError('unknown classroom instance')
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError('original graph bytes changed; refusing altered weights')
    return {'name':name, 'path':path, 'sha256':expected, 'side':side, 'nodes':1000 if name==COMPARISON_INSTANCE else side**2, 'kind':'random' if name==COMPARISON_INSTANCE else 'dense' if name == NEW_INSTANCE else 'torus',
            'trial_seconds':8.0 if name in (NEW_INSTANCE,COMPARISON_INSTANCE) else 1.5,
            'reference':json.loads((HERE/'data/reference.json').read_text())[name]['ref']}


CAPS = {'tabu': 20000, 'annealing': 200000, 'bm': 1, 'bls': 12000}
CONFIG_KEYS = {
    'tabu': {'tenure', 'restart_after'},
    'annealing': {'initial_temperature', 'final_temperature', 'polish'},
    'bm': {'max_sweeps', 'rounding_count'},
    'bls': {'jump', 'stagnation', 'p_min', 'q', 'tenure_min', 'tenure_max'},
}
DEFAULT_CONFIG = {
    'tabu': {'tenure': 20, 'restart_after': 0},
    'annealing': {'initial_temperature': 2.0, 'final_temperature': 0.01, 'polish': True},
    'bm': {'max_sweeps': 60, 'rounding_count': 16},
    'bls': {'jump': 1, 'stagnation': 1000, 'p_min': 0.8, 'q': 0.5, 'tenure_min': 3, 'tenure_max': 10},
}
PARENT = {'stages': [{'backend': 'tabu', 'config': {'tenure': 0, 'restart_after': 0}, 'max_work': 100, 'fresh': False}]}
# A measured comparison fixture, explicitly not a recorded model proposal.
NUMERICAL_CHILD = {'stages': [{'backend': 'tabu', 'config': {'tenure': 11, 'restart_after': 300}, 'max_work': 3000, 'fresh': False}]}


INITIAL_SOLVERS = [
    ('Tabu Search', {'stages':[{'backend':'tabu','config':{'tenure':5,'restart_after':0},'max_work':800,'fresh':False}]}),
    ('Simulated Annealing', {'stages':[{'backend':'annealing','config':{'initial_temperature':2.0,'final_temperature':0.01,'polish':True},'max_work':6000,'fresh':False}]}),
    ('Breakout Local Search', {'stages':[{'backend':'bls','config':{},'max_work':700,'fresh':False}]}),
    ('rank-two Burer–Monteiro', {'stages':[{'backend':'bm','config':{'max_sweeps':20,'rounding_count':8},'max_work':1,'fresh':False}]}),
]

def seed_labels(seed, instance=None):
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError('seed must be an integer in [0, 2**32)')
    graph = load_graph(instance_spec(instance)['path'])
    return np.random.default_rng(seed).choice(np.array([-1, 1], dtype=np.int8), graph.node_count)


def score_labels(labels, instance=None):
    spec = instance_spec(instance)
    graph = load_graph(instance_spec(instance)['path'])
    labels = checked_labels(labels, instance)
    n, i, j, w = evaluate.load_instance(spec['path'])
    direct = evaluate.cut_value(i, j, w, labels)
    assert abs(direct - cut_value(graph, labels)) < 1e-9
    reference = spec['reference']
    half = float(w.sum() / 2)
    violated = int(np.count_nonzero(((w > 0) & (labels[i] == labels[j])) | ((w < 0) & (labels[i] != labels[j]))))
    return {'cut': direct, 'score': (direct - half) / (reference - half),
            'reference_cut': reference, 'reference_matched': direct >= reference-1e-9,
            'proof_status': 'unproven', 'frustrated_edges': violated,
            'assignment': labels.tolist(), 'graph_sha256': spec['sha256'], 'instance':spec['name']}


def checked_labels(labels, instance=None):
    values = np.asarray(labels)
    if values.shape != (instance_spec(instance)['nodes'],) or values.dtype.kind not in 'iu' or not np.isin(values, [-1, 1]).all():
        raise ValueError(f"initial labels require exactly {instance_spec(instance)['nodes']} integer +/-1 signs in original vertex order")
    return values.astype(np.int8, copy=True)


def validate_strategy(strategy):
    if not isinstance(strategy, dict) or set(strategy) != {'stages'}:
        raise ValueError('strategy requires only stages')
    stages = strategy['stages']
    if not isinstance(stages, list) or not 1 <= len(stages) <= 3:
        raise ValueError('strategy requires one to three stages')
    for stage in stages:
        if not isinstance(stage, dict) or set(stage) != {'backend', 'config', 'max_work', 'fresh'}:
            raise ValueError('stage fields must be backend, config, max_work, fresh')
        method = stage['backend']
        if not isinstance(method, str) or method not in CAPS or type(stage['fresh']) is not bool:
            raise ValueError('unsupported backend or fresh flag')
        work = stage['max_work']
        if type(work) is not int or not 1 <= work <= CAPS[method]:
            raise ValueError('work exceeds classroom cap')
        cfg = stage['config']
        if not isinstance(cfg, dict) or set(cfg) - CONFIG_KEYS[method]:
            raise ValueError('unsupported config keys')
        merged = {**DEFAULT_CONFIG[method], **cfg}
        for key, value in merged.items():
            if key == 'polish':
                if type(value) is not bool: raise ValueError('polish must be boolean')
            elif key in {'initial_temperature', 'final_temperature', 'p_min', 'q'}:
                if type(value) not in (int, float) or not math.isfinite(value):
                    raise ValueError('config requires finite numbers')
                lower, upper = (0, 1) if key in {'p_min', 'q'} else (1e-6, 1000)
                if not lower <= value <= upper: raise ValueError('parameter out of range')
            else:
                lower = 0 if key in {'tenure', 'restart_after'} else 1
                upper = {'max_sweeps': 60, 'rounding_count': 16}.get(key, 1000)
                if type(value) is not int or not lower <= value <= upper:
                    raise ValueError(f'{method}.{key} must be an integer in [{lower}, {upper}]')
        if method == 'bls' and merged['tenure_max'] < merged['tenure_min']:
            raise ValueError('tenure_max must be >= tenure_min')
    return strategy


def normalized_strategy(strategy):
    validate_strategy(strategy)
    stages = []
    for stage in strategy['stages']:
        defaults = DEFAULT_CONFIG[stage['backend']]
        config = {**defaults, **stage['config']}
        config = {key: float(value) if type(defaults[key]) is float else value for key,value in config.items()}
        stages.append({**stage, 'config': config})
    return {'stages': stages}


def run_strategy(strategy, seed, initial=None, seconds=1.5, instance=None):
    validate_strategy(strategy)
    seed_labels(seed, instance)  # Validate the seed even when the caller supplies labels.
    if not math.isfinite(seconds) or not 0 < seconds <= instance_spec(instance)['trial_seconds']:
        raise ValueError('candidate seconds exceed the instance-specific classroom cap')
    graph = load_graph(instance_spec(instance)['path'])
    best = seed_labels(seed, instance) if initial is None else checked_labels(initial, instance)
    best = best.copy()
    started = perf_counter()
    observations = []
    for index, stage in enumerate(strategy['stages']):
        remaining = seconds - (perf_counter() - started)
        if remaining <= 0:
            break
        config = stage['config'].copy()
        if stage['backend'] == 'bm':
            config = {'max_sweeps': 60, 'rounding_count': 16, **config}
        candidate = solve(graph, config, (seed + index) % 2**32,
            {'seconds': remaining / (len(strategy['stages']) - index), 'max_work': stage['max_work']},
            None if stage['fresh'] else best.copy(), solver=stage['backend'])
        checked = score_labels(candidate['assignment'], instance)
        if checked['cut'] > cut_value(graph, best):
            best = np.array(checked['assignment'], dtype=np.int8)
        observations.append({'stage': index, 'backend': stage['backend'], 'cut': checked['cut'],
                             'runtime_seconds': candidate['runtime_seconds'],
                             'work_counters': candidate['work_counters'],
                             'execution_status': candidate['execution_status']})
    complete = len(observations) == len(strategy['stages']) and all(o['execution_status'] == 'completed' for o in observations)
    return {**score_labels(best, instance), 'seed': seed, 'strategy': strategy, 'complete': complete,
            'elapsed_seconds': perf_counter() - started, 'stage_results': observations}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke', action='store_true')
    parser.add_argument('--seed', type=int, default=3)
    parser.add_argument('--request', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.smoke:
        initial = seed_labels(args.seed)
        parent = run_strategy(PARENT, args.seed, initial)
        child = run_strategy(NUMERICAL_CHILD, args.seed, parent['assignment'])
        print(json.dumps({'mode': 'numerical_smoke_not_llm', 'seed': args.seed,
            'initial_cut': score_labels(initial)['cut'], 'parent_cut': parent['cut'],
            'child_cut': child['cut'], 'child_score': child['score'],
            'reference_cut': child['reference_cut'], 'proof_status': 'unproven',
            'elapsed_solver_seconds': parent['elapsed_seconds'] + child['elapsed_seconds']}))
    elif args.request and args.output:
        request = json.loads(args.request.read_text())
        (args.output.parent / 'worker_started.json').write_text(json.dumps({'pid': __import__('os').getpid()}))
        result = run_strategy(request['strategy'], request['seed'], request.get('initial'), request.get('seconds', 1.5), request.get('instance'))
        with args.output.open('x') as stream:
            json.dump(result, stream, allow_nan=False)
    else:
        parser.error('choose --smoke or --request and --output')


if __name__ == '__main__':
    main()
