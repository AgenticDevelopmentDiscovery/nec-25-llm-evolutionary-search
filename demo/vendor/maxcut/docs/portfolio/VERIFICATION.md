# Bounded verification and actual outcomes

Current extension: [suite v3](SUITE_V3.md) and its
[verification record](../../evidence/suite_v3/README.md). The 61-test count and
retained score below are historical phase results, not the current totals.

The final regression suite passes **61 tests** in the isolated environment (original 38 plus 23 portfolio tests). Actual output: [`tests_release.txt`](../../evidence/portfolio/tests_release.txt). These are small correctness/integration tests, not a public performance campaign. Earlier failing checks remain preserved alongside their corrections.

## What was checked

- All eight required signed examples, including the cut-eight local trap with optimum ten; exact enumeration agrees with an independent full all-tuples oracle.
- Direct versus incremental gains, complement invariance, negative/zero/decimal edges, isolated/disconnected nodes and caller-array ownership.
- All nine local search/dynamics identities return valid original-order witnesses on every required example; heuristic optimality is not required or inferred.
- Existing BM adapter matches the unchanged core's actual labels/cut with the same seed. Warm extended behavior retains the incumbent. The original 38 tests continue passing.
- Tabu actually accepts a worsening escape; seeded local methods reproduce labels with equal work; selected perturbations leave all unselected angles unchanged.
- Exact release of a singleton includes its fixed boundary and outside constant; partial conditional enumeration is not reported as complete.
- Generic SCIP MILP and signed planar matching agree with all required optima. Twenty-five additional signed/zero random four-node planar graphs agree with independent enumeration.
- Verified odd 3×3 and even 4×4 torus embeddings retain wraps, with computed U at least the independent exhaustive optimum. Missing wrap edges are rejected. A nonzero 1e−9-scale bound gap remains unproven through exact scaled-integer attainment comparison.
- One-step bSB/dSB/GSB equations are hand-checked. SBQA checks the correct replica axis, both 1/R factors and finite final regularization. A 100000-node/one-edge field uses linear state storage. An overflowing integration step must fail before wall clipping can hide infinity.
- One-shot original-format save/reload and unchanged official cut corroboration; existing output directories rejected; a zero-second hard timeout produces a valid explicitly unproven fallback.
- Missing optional PySCIPOpt gives unavailable rather than an import crash. Native timeout reaping, stale PID no-op and a separate-session SIGTERM-ignoring descendant are tested.

## Actual shared-runner evidence

[`shared_validation_final/summary.json`](../../evidence/portfolio/shared_validation_final/summary.json) contains **93 bounded observations**, including the expected QuBowl-unavailable result. Native MQLib, SMS, BiqBin, MADAM and BiqCrunch each ran ten tiny fixtures: the seven basic signed examples, trap, decimal triangle and disconnected/zero-edge graph. Each now recovers an actual native assignment; the validation rejects a mere timeout fallback as insufficient native conversion evidence. All reported exact optima match known values and all reported bounds dominate the known optima.

That matrix preserves one BM adapter failure (incorrectly unpacking the unchanged core's three-part result). It is superseded by [`bm_adapter_verified/result.json`](../../evidence/portfolio/bm_adapter_verified/result.json), the exact label-regression test, and the final config smoke below. The failed raw result is intentionally not overwritten. The initial matrix also preserved an SMS zero-edge parser failure and MQLib final-output timing fallbacks. These are diagnostic history, not successful backend-witness validation.

[`config_validation/summary.json`](../../evidence/portfolio/config_validation/summary.json) then verified **all 21 explicit method configs** through the actual runner: 20 available entries produced valid assignments and QuBowl returned the expected unavailable outcome. All five native programs recovered native witnesses. Each command is in its `request.json`/native command record; worker/native logs and original-format labels are retained. SMS additionally received and used an actual native partition warm start in [`scientific_warm_verified`](../../evidence/portfolio/scientific_warm_verified/result.json).

MPI cleanup had a real first failure: ranks created separate process groups and survived group-only launcher termination. [`mpi_timeout/verification.json`](../../evidence/portfolio/mpi_timeout/verification.json) records that failed observation. The repaired helper records verified ancestry/start ticks, terminates descendants individually, gives a bounded reaping interval and waits for asynchronous kill delivery. [`mpi_timeout_fixed/verification.json`](../../evidence/portfolio/mpi_timeout_fixed/verification.json) shows both actual MPI ranks gone; the stronger independent-session/ignored-TERM regression passes too. No broad name-based process killing is used.

## Artifact and math review

[`artifact_verification.json`](../../evidence/portfolio/artifact_verification.json) checks every starting tracked file against the pre-edit baseline, actual source revisions and absence of upstream tracked modifications, all 17 PDF hashes/structures, every new method/config link, SVG XML, all saved runner witnesses, and adjacent code comments/docstring presence. It also records actual Python/dependency versions and source hashes. Comment accuracy and method deviations remain reviewable in the guides; a syntactic comment audit does not establish paper fidelity.

All extracted inline/display formulas from the new Markdown guides are compiled with LaTeX/amsmath to DVI, with actual compiler output in [`math_compile.log`](../../evidence/portfolio/math_compile.log) and extracted source in [`math_equations.tex`](../../evidence/portfolio/math_equations.tex). No legacy backslash math delimiters are used. The 10 new SVGs were rendered and visually inspected; [`figures_review.png`](../../evidence/portfolio/figures_review.png) is a contact sheet, with full-size diagrams linked in [FIGURES.md](FIGURES.md). Primary GSB/SBQA equation pages were visually reviewed as well.

## Preservation and score

The baseline hashes **573 existing tracked files**. The only intentionally updated preexisting files are dependency declarations/lock, `process.md`, and the raw-log index. Official README, problem statement, instances, references, evaluator, visualizer, BM kernels/CLIs, prior figures and all existing assignments remain unchanged.

The unchanged official evaluator was rerun on the full latest retained 18-instance set: **overall 0.9713800081806563**, rungs approximately [1.0000, 0.9999, 0.9745, 0.9422, 0.9402]. Raw full-precision result: [`retained_scores.json`](../../evidence/portfolio/retained_scores.json); terminal table: [`retained_scores.txt`](../../evidence/portfolio/retained_scores.txt). This includes that set's latest improvements across all graphs. New tiny portfolio fixtures do not alter this public score or prove all public instances optimal.

## Reproduce the checks

```bash
uv sync --extra viz --extra milp --extra matching --extra tesb
uv run python -m unittest discover -s tests
uv run python scripts/verify_portfolio_artifacts.py
uv run python scripts/validate_portfolio.py \
  --output evidence/portfolio/check_again_01 --native
```

Rebuild ignored native checkouts first on another machine using [EXTERNAL_BUILDS.md](EXTERNAL_BUILDS.md). Native MPI needs permitted local sockets. The last command runs only tiny bounded fixtures, with five seconds per solver invocation; choose a fresh path. It will not run the public-instance campaign. Repeated work/time limits should be distinguished from optimization quality. No new global performance comparison, GPU benchmark, automatic orchestration or separately checked SDP certificate is claimed.
