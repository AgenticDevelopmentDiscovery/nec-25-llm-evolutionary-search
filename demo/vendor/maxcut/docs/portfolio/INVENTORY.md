# Portfolio implementation inventory — October 20, 2026

Starting revision: `483252d` (`before, big change`), clean worktree before
this request. The new brief is preserved verbatim at
`instruction_Tamim/CODEX_PORTFOLIO_BRIEF.md`.

## Reuse and preservation

The repository has a validated sparse `bm_solver.Graph`, direct cut and gain
evaluation, sequential rank-two sweeps, sampled rounding, binary polishing,
stable-seeded perturbations/restarts, atomic assignment retention and the
official scorer. `run_bm.py`, `compare_bm.py`, `run_bm_experiment.py`, guides,
figures, raw histories and prior solutions are reusable. The latest completed
18-file set is `experiments/bm_real_pilot_s1_s2/solutions`, official fitness
0.9713800081806563. The all-unmatched comparison is prepared but has no
completed run directory. No existing solution is used as a test output.

All **38 pre-existing tests pass** (actual output:
`evidence/portfolio/tests_before.txt`). Existing BM defaults are seed 42,
max_sweeps 200, rounding_count 32, one start, zero perturbation rounds;
sigma defaults to 0.35 radians when enabled. Existing tolerances, coupled
legacy initialization/order stream, immediate coordinate updates, near-zero
field handling, rounding boundary rule and local-gain updates must remain
unchanged. The new portfolio adapts BM instead of replacing it. Its observed
relaxation value is not an upper bound.

`evidence/portfolio/baseline.json` inventories SHA-256 hashes of all 573
starting tracked files. Official instances, references, README, problem,
evaluator, visualizer, existing kernels and all old solutions/history evidence
are protected. Changes to optional dependency declarations, process notes and
documentation will be recorded explicitly.

## Missing components

There is no shared multi-solver result interface or one-shot portfolio runner,
exhaustive oracle, tabu/BLS/SA implementation, exact MILP/neighborhood repair,
bifurcation family, installed external backend, or local paper collection.
None of those is credited as implemented merely because a repository can be
downloaded. Every external solver needs its real conversion, output parsing,
limits, source identity and independent assignment checks.

## Environment and initial availability

The isolated `.venv` is Python 3.14.7 with `include-system-site-packages=false`;
its base interpreter is the user's conda installation. Declared dependencies
are NumPy plus the optional matplotlib `viz` extra. NumPy and matplotlib are
available. SciPy, PySCIPOpt, torch, and simulated-bifurcation are absent.
GCC/G++, gfortran, CMake, make, MPI compiler wrappers, git and Poppler tools
(`pdfinfo`, `pdftotext`, `pdftoppm`) are available. Detailed executable paths
are in the baseline inventory. Builds must use project-local directories;
no system package installation or change to the base conda environment.
Optional backends must remain optional for basic solvers.

Public repository access failed DNS inside the sandbox and succeeded after
the required network escalation. Actual download/build logs and pinned
revisions will identify obtained sources. Availability is determined from
bounded build/run attempts, not the compiler list alone.

## Implementation sequence

1. Obtain and verify primary papers; pin upstream sources and licenses.
2. Add the shared result/validation contract without changing the BM API.
3. Implement a guarded exhaustive oracle and adapt/regression-check BM.
4. Implement documented tabu, source-grounded BLS and baseline annealing.
5. Add optional SCIP MILP and exact neighborhood repair with boundary terms.
6. Build/validate MQLib and attempt ScientificMaxcutSolver.
7. Build/validate or precisely diagnose BiqBin, MADAM and BiqCrunch.
8. Check planar/toroidal assumptions, conversion and bounds on tiny lattices.
9. Read and implement/adapt each distinct bifurcation formulation.
10. Validate through the common runner, illustrate every method, preserve raw
    evidence and report each component's actual status and limitations.

Only bounded exact checks and smoke runs belong to this phase. No evolutionary
controller, automatic model calls or large portfolio campaign is included.
