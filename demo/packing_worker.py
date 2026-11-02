"""Mounted alone inside Bubblewrap; JSON request on stdin, public JSONL on stdout."""
import contextlib
import io
import json
import math
import resource
import sys
import time

import numpy as np
from scipy.optimize import linprog


def main():
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    resource.setrlimit(resource.RLIMIT_AS, (2_000_000_000, 2_000_000_000))
    resource.setrlimit(resource.RLIMIT_FSIZE, (2_000_000, 2_000_000))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    # Candidates are single-process programs. Existing threads count against
    # this limit too, so numerical libraries are configured single-threaded.
    resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))
    request = json.loads(sys.stdin.read(100_000))
    n = request['n']
    if type(n) is not int or n not in (26,32): raise ValueError('unsupported circle count')
    ii, jj = np.triu_indices(n, 1)
    matrix = np.zeros((len(ii), n))
    matrix[np.arange(len(ii)), ii] = 1
    matrix[np.arange(len(ii)), jj] = 1
    calls, reports = 0, 0
    output = sys.stdout
    def emit(value):
        output.write(json.dumps(value, allow_nan=False)+'\n'); output.flush()
    def radii(centers):
        nonlocal calls
        calls += 1
        c = np.asarray(centers, dtype=float)
        if c.shape != (n, 2) or not np.isfinite(c).all() or (c < 0).any() or (c > 1).any():
            raise ValueError(f'centers must be finite ({n},2) points in the unit square')
        walls = np.minimum(c, 1-c).min(axis=1)
        distances = np.linalg.norm(c[ii]-c[jj], axis=1)
        # A common construction margin makes final returned geometry conservative.
        upper = np.maximum(0, walls-1e-8)
        result = linprog(-np.ones(n), A_ub=matrix, b_ub=np.maximum(0, distances-1e-8),
                         bounds=list(zip(np.zeros(n), upper)), method='highs',
                         options={'primal_feasibility_tolerance': 1e-9, 'time_limit': 1.0})
        if not result.success:
            raise ValueError('radius allocation did not complete: '+result.message)
        return result.x
    def report(circles):
        nonlocal reports
        if reports >= 32: return
        reports += 1
        emit({'type': 'progress', 'circles': np.asarray(circles).tolist()})
    scope = {'np': np, 'math': math, 'radii': radii, 'report': report}
    start = time.monotonic()
    # OS isolation is mandatory outside this wrapper. Redirect accidental prints
    # so they cannot be confused with the wrapper's public result protocol.
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(request['source'], '<evolved-packing-program>', 'exec'), scope)
        circles = scope['solve'](np.array(request['initial'], dtype=float), request['seed'], request['steps'])
    emit({'type': 'result', 'circles': np.asarray(circles).tolist(),
          'radius_calls': calls, 'seconds': time.monotonic()-start})


if __name__ == '__main__':
    try: main()
    except Exception as error:
        print(json.dumps({'type': 'error', 'error': str(error)[:300]}), flush=True)
        sys.exit(1)
