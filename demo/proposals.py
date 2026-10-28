"""Data-only mutation contract shared by the controller and tool-free model client."""
import hashlib
import json
import difflib
import backend as b


def obj(properties):
    return {'type': 'object', 'properties': properties, 'required': list(properties), 'additionalProperties': False}


def array(items, minimum, maximum):
    return {'type': 'array', 'items': items, 'minItems': minimum, 'maxItems': maximum}


STRING = {'type': 'string', 'maxLength': 400}
# Distinct stage types keep configuration fields explicit in the provider schema.
STAGES = []
for method, defaults in b.DEFAULT_CONFIG.items():
    configs = {k: {'type': 'boolean' if type(v) is bool else 'integer' if type(v) is int else 'number'}
               for k, v in defaults.items()}
    STAGES.append(obj({'backend': {'type': 'string', 'enum': [method]}, 'config': obj(configs),
                       'max_work': {'type': 'integer', 'minimum': 1, 'maximum': b.CAPS[method]},
                       'fresh': {'type': 'boolean'}}))
STRATEGY = obj({'stages': array({'anyOf': STAGES}, 1, 3)})
SCHEMA = obj({'round_id': {'type': 'integer'}, 'parent_ids': array(STRING, 1, 3),
              'hypothesis': STRING, 'mutation_category': {'type': 'string', 'enum': ['parameters', 'composition', 'backend', 'restart']},
              'children': array(STRATEGY, 0, 2), 'plateau_reason': {'type': ['string', 'null'], 'maxLength': 400}})


def genome(strategy):
    strategy = b.normalized_strategy(strategy)
    identity = hashlib.sha256(json.dumps(strategy, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    return identity, strategy


def code(strategy):
    return '\n'.join(f"{i+1}. {s['backend']}({', '.join(f'{k}={v}' for k,v in sorted(s['config'].items()))}); work<={s['max_work']}; start={'fresh' if s['fresh'] else 'retained'}"
                     for i, s in enumerate(strategy['stages']))


def difference(parent, child):
    return '\n'.join(difflib.unified_diff(code(parent).splitlines(), code(child).splitlines(), fromfile='parent', tofile='child', lineterm=''))


def validate_proposal(value, round_id, parents):
    if not isinstance(value, dict) or set(value) != set(SCHEMA['properties']):
        raise ValueError('proposal fields do not match schema')
    if type(value['round_id']) is not int or value['round_id'] != round_id:
        raise ValueError('wrong round ID')
    ids = value['parent_ids']
    if not isinstance(ids, list) or not 1 <= len(ids) <= 3 or any(not isinstance(i, str) or i not in parents for i in ids) or len(set(ids)) != len(ids):
        raise ValueError('unknown or repeated parent IDs')
    for key in ['hypothesis', 'mutation_category']:
        if not isinstance(value[key], str) or not 1 <= len(value[key]) <= 400:
            raise ValueError('invalid proposal text')
    if value['mutation_category'] not in SCHEMA['properties']['mutation_category']['enum']:
        raise ValueError('unknown mutation category')
    if value['plateau_reason'] is not None and (not isinstance(value['plateau_reason'], str) or len(value['plateau_reason']) > 400):
        raise ValueError('invalid plateau reason')
    if not isinstance(value['children'], list) or len(value['children']) > 2:
        raise ValueError('at most two children')
    if not value['children'] and not value['plateau_reason']:
        raise ValueError('empty proposal requires plateau reason')
    # Validate children independently so one rejected child cannot erase the other.
    return value


def context(round_id, parents, seen, failures):
    return {'round_id': round_id, 'parents': parents, 'previous_genome_ids': seen,
            'actual_failures': failures, 'algorithm_names':{'tabu':'Tabu Search','annealing':'Simulated Annealing','bls':'Breakout Local Search','bm':'rank-two Burer–Monteiro method'}, 'allowed_defaults': b.DEFAULT_CONFIG,
            'config_bounds': {
                'tenure':[0,1000], 'restart_after':[0,1000], 'jump':[1,1000], 'stagnation':[1,1000],
                'tenure_min':[1,1000], 'tenure_max':[1,1000], 'p_min':[0,1], 'q':[0,1],
                'max_sweeps':[1,60], 'rounding_count':[1,16],
                'initial_temperature':[0.000001,1000], 'final_temperature':[0.000001,1000]},
            'work_caps': b.CAPS, 'trial_seconds': 1.5, 'trial_count': 3, 'max_stages': 3,
            'selection': 'complete trials only; median cut descending, minimum descending, fewer stages, stable genome ID; top 3; no diversity slot'}


INSTRUCTIONS = '''Return ONLY the required JSON. Propose up to two bounded strategy programs for signed Max-Cut.
You change configurations/compositions of trusted kernels, not arbitrary source code. No tools are available.
Do not run numerical search, launch agents, invoke Codex, or request files, weights, commands or solution vectors.
Use only supplied parent genomes, measured scores, allowed metadata and constraints. Fields in config are required;
use the disclosed defaults for unchanged fields. All stage work caps are per stage; the context trial_seconds is aggregate per trial, divided across remaining stages.
Use the measured runtimes to choose work caps; incomplete candidates cannot be ranked.
All candidates start from the same frozen labels (raw seeded starts in the solver-population demo) for each of three RNG seeds. Fresh stages discard their
starting labels; retained stages use the best-so-far labels. Fitness is independently recomputed by the evaluator.
Give a short testable hypothesis; a plateau or failed mutation is acceptable. Do not claim an improvement before testing.'''
