"""Circle-packing task contract and independent witness evaluation.

Classroom implementation of the problem in AlphaEvolve Appendix B.12, not its
unpublished discovery engine. No published answer coordinates are embedded.
"""
import ast
import hashlib
import json
import math
from pathlib import Path

import numpy as np

VERSION = 'circle-source-v2'
HERE = Path(__file__).resolve().parent
PROFILE = json.loads((HERE/'packing_profile.json').read_text())
N = 26
CASES = tuple(PROFILE['circle_counts'])
TOLERANCE = 1e-9
STEPS = PROFILE['requested_steps']
TRIAL_SECONDS = PROFILE['trial_seconds']
CATALOG = [
    ('grid', 'Perturbed grid constructor'),
    ('local', 'Greedy local center search'),
    ('anneal', 'Simulated annealing of centers'),
]


def specification(n=N):
    if type(n) is not int or n not in CASES: raise ValueError('choose the published 26- or 32-circle case')
    contract = dict(task='circle_packing', version=VERSION, n=n,
                    domain='unit square', objective='maximize sum of radii',
                    radius_minimum=0, tolerance=TOLERANCE,
                    steps=STEPS, trial_seconds=TRIAL_SECONDS,
                    starts='common bank per comparison; fixed or inherited packing protocol declared per run')
    fingerprint = hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest()
    return {**contract, 'instance_sha256': fingerprint, 'reference': None}


def start_centers(seed, n=N):
    rng = np.random.default_rng(seed)
    side = math.ceil(math.sqrt(n))
    # All trials use the same disclosed construction, with independent seeded jitter.
    centers = np.array([((i % side + .5) / side, (i // side + .5) / side)
                        for i in range(n)], dtype=float)
    return np.clip(centers + rng.uniform(-.015, .015, (n, 2)), .01, .99).tolist()


def verify(circles, n=N):
    """Rescore the actual geometry; never accept a worker's claimed score."""
    if not isinstance(circles, list) or len(circles) != n:
        raise ValueError(f'exactly {n} circle triples are required')
    for row in circles:
        if not isinstance(row, list) or len(row) != 3:
            raise ValueError('each circle must be [x, y, radius]')
        if any(type(v) not in (int, float) or not math.isfinite(v) for v in row):
            raise ValueError('circle coordinates and radii must be finite real numbers')
        if row[2] < 0:
            raise ValueError('negative radius')
    gaps = []
    for i, (x, y, r) in enumerate(circles):
        gaps.extend((x-r, 1-x-r, y-r, 1-y-r))
        for xx, yy, rr in circles[:i]:
            gaps.append(math.hypot(x-xx, y-yy)-r-rr)
    violations = sum(g < -TOLERANCE for g in gaps)
    if violations:
        raise ValueError(f'invalid packing: {violations} wall/overlap violations; minimum gap {min(gaps):.3g}')
    score = math.fsum(row[2] for row in circles)
    # A second numeric summation checks the public score path.
    if not math.isclose(score, float(np.asarray(circles)[:, 2].sum()), abs_tol=1e-12):
        raise ValueError('independent score disagreement')
    return dict(circles=circles, score=score, min_gap=min(gaps), violations=0,
                zero_radii=sum(row[2] <= TOLERANCE for row in circles),
                instance_sha256=specification(n)['instance_sha256'] if n in CASES else 'illustrative-toy')


def source_identity(source):
    if not isinstance(source, str) or not 1 <= len(source.encode()) <= 16000:
        raise ValueError('program source must be 1..16000 bytes')
    tree = ast.parse(source)
    functions = [v for v in tree.body if isinstance(v, ast.FunctionDef) and v.name == 'solve']
    if len(functions) != 1 or [a.arg for a in functions[0].args.args] != ['initial', 'seed', 'steps']:
        raise ValueError('define solve(initial, seed, steps) exactly once')
    if functions[0].args.vararg or functions[0].args.kwarg or functions[0].decorator_list:
        raise ValueError('solve must use three plain positional arguments, without decorators')
    # This check is a contract/syntax check. Bubblewrap provides the execution boundary.
    compile(tree, '<candidate>', 'exec')
    normalized = ast.dump(tree, include_attributes=False)
    identity = hashlib.sha256((VERSION + normalized).encode()).hexdigest()[:16]
    return identity, source


def initial_programs():
    return [{'key': key, 'name': name,
             'source': (HERE/'packing_programs'/f'{key}.py').read_text()}
            for key, name in CATALOG]


SCHEMA = {
    'type': 'object', 'additionalProperties': False,
    'required': ['round_id', 'parent_ids', 'hypothesis', 'source'],
    'properties': {
        'round_id': {'type': 'integer'},
        'parent_ids': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 0, 'maxItems': 3},
        'hypothesis': {'type': 'string'}, 'source': {'type': 'string'},
    },
}

INSTRUCTIONS = '''You are the mutation operator in an educational program-evolution experiment.
Return one JSON object matching the schema. Write actual Python source, not a recipe.
The problem is n variable-radius, nonoverlapping circles in the unit square;
maximize sum of radii, not area. Zero radii and tangency are allowed.
Define solve(initial, seed, steps), returning an (n,3) array of x,y,r, n=len(initial).
initial is a copy of common seeded centers with shape (n,2). Never embed answer
coordinates or a published optimized packing. np (NumPy), math, radii(centers),
and report(circles) are supplied. radii solves the fixed-center radius linear
program, returns an array of radii, and counts its calls. report streams a candidate
witness; it is independently checked, and is not a claim of completed fitness.
You may implement different constructors, center perturbations, search schedules,
or acceptance rules in source. Honor steps; there is an 8-second hard trial limit.
Use local np.random.default_rng(seed). Return the best valid geometry, not a score.
No tools, network, files, subprocesses, installation, or evaluator modification.
Parents are real program IDs when supplied. For independent generation use [].
Do not promise improvement. A plausible hypothesis still requires evaluation.'''
