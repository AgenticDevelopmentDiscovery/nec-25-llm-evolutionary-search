# MADAM semidefinite exact integration

## 1. Problem and supported input

The target is original signed weighted Max-Cut: $F(s)=\sum_E w_{ij}(1-s_i s_j)/2$. Each edge is counted once; positive weights favor opposite signs and negative weights favor equal signs. Original node order is preserved. See [shared contract](ARCHITECTURE.md) and [objective/transformation details](MATHEMATICS.md). This method's actual availability, topology/size restrictions, warm-start use and work unit are exposed by `uv run python run_solver.py --solver madam --features`.

## 2. Intuition

Runs the actual MPI parallel maximum-cut solver using its SDP bounding procedure, retaining its independent implementation and logs.

## 3. Formulation and conventions

Use exact integer scaling and one-based GSet edges. Parse the original Solution=(...) membership and Maximum/Best value; complement invariance permits either side orientation. Divide objective and bounds by scale and check direct F.

## 4. Algorithm steps

Validate supported input, seed, budgets and warm-start capability. Reserve a unique native artifact tree; write the inspected conversion and native parameters. Run the actual executable with owned-process timeout cleanup. Recover a real native witness; independently validate signs, direct original F and native primal agreement. Preserve raw logs, source pin, executable SHA, status and any computed bound.

## 5. Fully worked small example

For the trap, returned side {B,C} cuts AB=3, CD=3 and two cross edges of 2, totaling 10. Native bound/value is compared in original units rather than assumed from the side list.

[All required hand examples](MATHEMATICS.md#hand-worked-reference-instances) and [validation report](VERIFICATION.md) provide independent reference optima and original-format fixtures.

## 6. Illustration

![MADAM semidefinite exact integration illustration](figures/branch_bound.svg)

Figures are labeled conceptual or measured. Numerical traces come from preserved tiny-run JSON/logs; arrows in conceptual diagrams are explanatory geometry, not measured backend events. [Regeneration and provenance](FIGURES.md).

## 7. Parameters and effects

max_nodes=1024 dense-SDP guard; two MPI ranks; actual source seed is fixed at 2020. Runtime budget only, no supported warm-start flag in this adapter.

Copyable config: [`configs/portfolio/madam.json`](../../configs/portfolio/madam.json). Do not supply unsupported options; they are rejected rather than silently ignored.

## 8. Complexity and memory

Conversion is sparse O(n+m). Native SDP methods can use dense O(n²) matrices and expensive bound work; sparse exact/MQLib internal memory depends on its actual native algorithm. Conservative adapter guards do not predict practical runtime or avoid every native allocation.

## 9. Exactness and certification limits

Native Maximum output without a TIME LIMIT marker plus successful recovered completion supports solver_reported_optimal; time-limited best values remain feasible/unproven. Root bounds remain numerical native evidence. Execution status, feasible assignment and optimality evidence remain separate. No serialized independently checked certificate is claimed by this portfolio.

## 10. Source-to-code mapping

external/MADAM/admm; source params/text output and pinned revision.

Primary source records: [`madam`](../../papers/README.md#madam). [External pins/builds](EXTERNAL_BUILDS.md) and [reading notes](SOURCE_REVIEW.md) distinguish obtained full text, unavailable PDFs, and inspected source code.

## 11. Run and interpret outputs

```bash
uv run python run_solver.py --solver madam \
  --instance evidence/portfolio/shared_validation_final/inputs/trap.txt \
  --config configs/portfolio/madam.json --seed 2020 \
  --time-limit 10 --output runs/madam_example_01
```

Choose a new suffix if the output already exists. Optional methods require their extras/source builds from [setup](EXTERNAL_BUILDS.md). Read `result.json` and actual `worker.log`/native logs; `solutions/<input basename>` is written only for validated labels. The tiny example has no professor reference score: official cut verification still runs, while reference score is null. `upper_bound=null` means no bound was computed, not zero gap. QuBowl deliberately returns unavailable with no assignment.

## 12. Implementation deviations

SuiteSparse headers/libraries and OpenBLAS are isolated in external/native. Absolute rpath avoids make consuming $ORIGIN. A separately recorded failed link attempt is preserved; only the successful build is advertised.
