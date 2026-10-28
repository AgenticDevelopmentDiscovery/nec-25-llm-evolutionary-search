# Exhaustive search

## 1. Problem and supported input

The target is original signed weighted Max-Cut: $F(s)=\sum_E w_{ij}(1-s_i s_j)/2$. Each edge is counted once; positive weights favor opposite signs and negative weights favor equal signs. Original node order is preserved. See [shared contract](ARCHITECTURE.md) and [objective/transformation details](MATHEMATICS.md). This method's actual availability, topology/size restrictions, warm-start use and work unit are exposed by `uv run python run_solver.py --solver exhaustive --features`.

## 2. Intuition

Examine every complementary equivalence class. Unlike a heuristic, a completed enumeration leaves no unexamined class.

## 3. Formulation and conventions

Fix $s_0=+1$; enumerate $2^{n-1}$ assignments and maximize the exact scaled integer sum of cut-edge weights.

## 4. Algorithm steps

Validate size/scaling; retain the initial candidate; enumerate masks for nodes 1 through n−1; directly sum each original edge; replace best only on a strict improvement. Mark completeness only after every required assignment.

## 5. Fully worked small example

For a +2 edge, canonical labels (+,+) give 0 and (+,−) give 2. Both classes are examined, so the result is feasible 2 with upper bound 2. With max_work=1, an equally good random initial cut would still leave enumeration incomplete.

[All required hand examples](MATHEMATICS.md#hand-worked-reference-instances) and [validation report](VERIFICATION.md) provide independent reference optima and original-format fixtures.

## 6. Illustration

![Exhaustive search illustration](figures/branch_bound.svg)

Figures are labeled conceptual or measured. Numerical traces come from preserved tiny-run JSON/logs; arrows in conceptual diagrams are explanatory geometry, not measured backend events. [Regeneration and provenance](FIGURES.md).

## 7. Parameters and effects

max_nodes=24 is an exponential-work safety guard, independently capped at 26. max_work counts completed assignments, not nodes; seconds also limits enumeration.

Copyable config: [`configs/portfolio/exhaustive.json`](../../configs/portfolio/exhaustive.json). Do not supply unsupported options; they are rejected rather than silently ignored.

## 8. Complexity and memory

$O(2^{n-1}m)$ time and $O(n+m)$ memory. This readable implementation uses direct sums, not Gray-code incremental enumeration.

## 9. Exactness and certification limits

Exact comparison uses finite-decimal integer scaling. Complete enumeration reports its completeness evidence. An interrupted run gives a computed sum-of-positive-weights bound and unproven status; no standalone certificate checker is claimed. Execution status, feasible assignment and optimality evidence remain separate. No serialized independently checked certificate is claimed by this portfolio.

## 10. Source-to-code mapping

portfolio_search.solve_exhaustive; portfolio_common.integer_weights. Complement invariance and independent all-tuples tests are in tests/test_portfolio.py.

Primary source records: [`bm`](../../papers/README.md#bm). [External pins/builds](EXTERNAL_BUILDS.md) and [reading notes](SOURCE_REVIEW.md) distinguish obtained full text, unavailable PDFs, and inspected source code.

## 11. Run and interpret outputs

```bash
uv run python run_solver.py --solver exhaustive \
  --instance evidence/portfolio/shared_validation_final/inputs/trap.txt \
  --config configs/portfolio/exhaustive.json --seed 1 \
  --time-limit 10 --output runs/exhaustive_example_01
```

Choose a new suffix if the output already exists. Optional methods require their extras/source builds from [setup](EXTERNAL_BUILDS.md). Read `result.json` and actual `worker.log`/native logs; `solutions/<input basename>` is written only for validated labels. The tiny example has no professor reference score: official cut verification still runs, while reference score is null. `upper_bound=null` means no bound was computed, not zero gap. QuBowl deliberately returns unavailable with no assignment.

## 12. Implementation deviations

Gray-code acceleration is intentionally absent. Default n/work guards are project safety controls. Deterministic enumeration records the seed but needs no random search trajectory.
