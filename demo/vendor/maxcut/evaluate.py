"""Official scorer: scores a folder of solution files against the references.

    python evaluate.py [--solutions solutions] [--instances instances/public]
                       [--refs references/public.json] [--rungs 0 1 2]
                       [--json out.json] [--fitness-only]

For each instance ``<name>.txt`` in ``--instances``, the solution is
``<solutions>/<name>.txt``: ``n`` lines, each ``-1`` or ``+1``. With ``W`` the
instance's total edge weight::

    score = (cut - W/2) / (ref - W/2)

``W/2`` is the expected cut of a coin-flip coloring, so 0 is random and 1
matches the reference. A missing or invalid solution scores 0. Scores are
averaged within each rung, and the overall score is the mean over rungs.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

# Rung r holds instances with RUNG_EDGES[r] <= n < RUNG_EDGES[r + 1].
RUNG_EDGES = [0, 50, 500, 5_000, 50_000]


def load_instance(path):
    """Read an instance file. Returns (n, i, j, w), node ids 0-indexed, each edge once."""
    with open(path) as f:
        n, m = (int(x) for x in f.readline().split())
        rows = np.loadtxt(f, ndmin=2).reshape(-1, 3)
    if len(rows) != m:
        raise ValueError(f"{path}: header says {m} edges, found {len(rows)}")
    return n, rows[:, 0].astype(np.int64) - 1, rows[:, 1].astype(np.int64) - 1, rows[:, 2]


def load_solution(path, n):
    """Read a solution file. Returns (s, message); ``s`` is None if missing or invalid."""
    if not os.path.exists(path):
        return None, "missing"
    try:
        s = np.loadtxt(path, ndmin=1)
    except ValueError as exc:
        return None, f"unreadable: {exc}"
    if s.shape != (n,):
        return None, f"expected {n} lines, found {s.size}"
    if not np.all((s == 1) | (s == -1)):
        return None, "entries must be -1 or +1"
    return s.astype(np.int8), "ok"


def cut_value(i, j, w, s):
    """Total weight of the edges whose endpoints get different colors."""
    return float(w[s[i] != s[j]].sum())


def rung_of(n):
    return int(np.searchsorted(RUNG_EDGES, n, side="right")) - 1


def score_folder(solutions_dir, instances_dir, refs_path, rungs=None):
    with open(refs_path) as f:
        refs = json.load(f)
    instances = {}
    for name in sorted(os.listdir(instances_dir)):
        if not name.endswith(".txt"):
            continue
        n, i, j, w = load_instance(os.path.join(instances_dir, name))
        rung = rung_of(n)
        if rungs is not None and rung not in rungs:
            continue
        if name not in refs:
            print(f"warning: no reference for {name}; skipped", file=sys.stderr)
            continue
        ref, half = refs[name]["ref"], w.sum() / 2
        s, message = load_solution(os.path.join(solutions_dir, name), n)
        cut = None if s is None else cut_value(i, j, w, s)
        score = 0.0 if cut is None else (cut - half) / (ref - half)
        instances[name] = {"rung": rung, "n": n, "cut": cut, "ref": ref,
                           "score": score, "status": message}
    by_rung = {}
    for r in instances.values():
        by_rung.setdefault(r["rung"], []).append(r["score"])
    rung_scores = {r: float(np.mean(v)) for r, v in sorted(by_rung.items())}
    overall = float(np.mean(list(rung_scores.values()))) if rung_scores else 0.0
    return {"overall": overall, "rungs": rung_scores, "instances": instances}


def format_table(result):
    lines = [f"{'instance':<28} {'rung':>4} {'cut':>12} {'ref':>12} {'score':>7}  status"]
    for name, r in result["instances"].items():
        cut = "—" if r["cut"] is None else f"{r['cut']:.6g}"
        lines.append(f"{name:<28} {r['rung']:>4} {cut:>12} {r['ref']:>12.6g} "
                     f"{r['score']:>7.4f}  {r['status']}")
    profile = ", ".join(f"{v:.4f}" for v in result["rungs"].values())
    lines.append(f"\nper rung: [{profile}]    overall: {result['overall']:.4f}")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--solutions", default="solutions")
    p.add_argument("--instances", default="instances/public")
    p.add_argument("--refs", default="references/public.json")
    p.add_argument("--rungs", type=int, nargs="+", help="score only these rungs")
    p.add_argument("--json", dest="json_out", help="also write the full result as JSON")
    p.add_argument("--fitness-only", action="store_true", help="print only the overall score")
    args = p.parse_args(argv)

    result = score_folder(args.solutions, args.instances, args.refs, args.rungs)
    if args.json_out:
        with open(args.json_out, "w") as f:
            json.dump(result, f, indent=2)
    print(f"{result['overall']:.6f}" if args.fitness_only else format_table(result))


if __name__ == "__main__":
    main()
