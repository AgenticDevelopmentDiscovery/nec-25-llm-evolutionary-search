# Preserved rank-two Burer–Monteiro solver

## 1. Problem and supported input

The target is original signed weighted Max-Cut: $F(s)=\sum_E w_{ij}(1-s_i s_j)/2$. Each edge is counted once; positive weights favor opposite signs and negative weights favor equal signs. Original node order is preserved. See [shared contract](ARCHITECTURE.md) and [objective/transformation details](MATHEMATICS.md). This method's actual availability, topology/size restrictions, warm-start use and work unit are exposed by `uv run python run_solver.py --solver bm --features`.

## 2. Intuition

Replace each binary sign by a unit vector on a circle, improve vectors sequentially, round them to signs, then improve the actual binary cut.

## 3. Formulation and conventions

$R(\theta)=\frac12\sum_Ew_{ij}[1-\cos(\theta_i-\theta_j)]$. Set $h_i=\sum_jw_{ij}v_j$ and $v_i=-h_i/\|h_i\|$ except near zero. Round by $s_i=\operatorname{sign}(v_i\cdot r)$.

## 4. Algorithm steps

Call the unchanged solver. Coordinate updates are immediate; sample rounding normals; use strictly improving one-flip polishing; select by direct original F. Existing restart/perturbation settings enter the old extended call, while the one-start no-incumbent path preserves its exact RNG behavior.

## 5. Fully worked small example

On +2 AB, fixing B vector at (1,0) makes A=(−1,0) maximize the edge relaxation at 2. A normal along the horizontal axis rounds the endpoints to opposite signs, cutting weight 2. Its separating line is vertical, perpendicular to that normal.

[All required hand examples](MATHEMATICS.md#hand-worked-reference-instances) and [validation report](VERIFICATION.md) provide independent reference optima and original-format fixtures.

## 6. Illustration

![Preserved rank-two Burer–Monteiro solver illustration](../figures/bm_coordinate.svg)

Figures are labeled conceptual or measured. Numerical traces come from preserved tiny-run JSON/logs; arrows in conceptual diagrams are explanatory geometry, not measured backend events. [Regeneration and provenance](FIGURES.md).

## 7. Parameters and effects

max_sweeps=200, rounding_count=32, restarts=1, perturb_rounds=0, perturb_scale=.35 radians; five original field/sweep/gain/projection tolerances are retained. max_work must cover restarts*(1+perturb_rounds) complete configured passes.

Copyable config: [`configs/portfolio/bm.json`](../../configs/portfolio/bm.json). Do not supply unsupported options; they are rejected rather than silently ignored.

## 8. Complexity and memory

Sparse $O(n+m)$ state; a coordinate sweep costs $O(n+m)$, with configured sweeps, rounds and binary flips adding work. The original implementation and histories remain authoritative.

## 9. Exactness and certification limits

A nonconvex rank-two local maximum and a reference score 1 do not certify the global cut. No upper bound is returned. Actual feasibility/cut are independently checked. Execution status, feasible assignment and optimality evidence remain separate. No serialized independently checked certificate is claimed by this portfolio.

## 10. Source-to-code mapping

solver_portfolio.solve_bm_adapter → unchanged bm_solver.solve_bm / solve_bm_extended. The original docs/BM_GUIDE.md and docs/BM_EXTENSION_GUIDE.md retain detailed derivations; the preservation regression compares actual labels to the old call.

Primary source records: [`bm`](../../papers/README.md#bm). [External pins/builds](EXTERNAL_BUILDS.md) and [reading notes](SOURCE_REVIEW.md) distinguish obtained full text, unavailable PDFs, and inspected source code.

## 11. Run and interpret outputs

```bash
uv run python run_solver.py --solver bm \
  --instance evidence/portfolio/shared_validation_final/inputs/trap.txt \
  --config configs/portfolio/bm.json --seed 1 \
  --time-limit 10 --output runs/bm_example_01
```

Choose a new suffix if the output already exists. Optional methods require their extras/source builds from [setup](EXTERNAL_BUILDS.md). Read `result.json` and actual `worker.log`/native logs; `solutions/<input basename>` is written only for validated labels. The tiny example has no professor reference score: official cut verification still runs, while reference score is null. `upper_bound=null` means no bound was computed, not zero gap. QuBowl deliberately returns unavailable with no assignment.

## 12. Implementation deviations

The original project uses educational sequential sweeps, sampled rounding and its documented extensions; it is not the complete original Burer–Monteiro–Zhang production heuristic. The adapter changes no core functions.
