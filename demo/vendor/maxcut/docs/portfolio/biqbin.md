# BiqBin semidefinite branch-and-bound

## 1. Problem and supported input

The target is original signed weighted Max-Cut: $F(s)=\sum_E w_{ij}(1-s_i s_j)/2$. Each edge is counted once; positive weights favor opposite signs and negative weights favor equal signs. Original node order is preserved. See [shared contract](ARCHITECTURE.md) and [objective/transformation details](MATHEMATICS.md). This method's actual availability, topology/size restrictions, warm-start use and work unit are exposed by `uv run python run_solver.py --solver biqbin --features`.

## 2. Intuition

Runs the original parallel SDP-based binary quadratic branch-and-bound program, using a coordinator and worker MPI rank.

## 3. Formulation and conventions

Losslessly scale finite-decimal signed weights to integers; one-based original edge file. Parse actual ExecutionMD JSON OneSideOfTheCut and invert to complete original-order signs. Divide primal/root bounds by scale. No additional objective offset.

## 4. Algorithm steps

Validate supported input, seed, budgets and warm-start capability. Reserve a unique native artifact tree; write the inspected conversion and native parameters. Run the actual executable with owned-process timeout cleanup. Recover a real native witness; independently validate signs, direct original F and native primal agreement. Preserve raw logs, source pin, executable SHA, status and any computed bound.

## 5. Fully worked small example

Weights (.4,.3,−.2) scale by 10 to (4,3,−2); native optimum 7 and its partition give original cut .7. Scaling the objective back is essential; .7, not 7, is reported.

[All required hand examples](MATHEMATICS.md#hand-worked-reference-instances) and [validation report](VERIFICATION.md) provide independent reference optima and original-format fixtures.

## 6. Illustration

![BiqBin semidefinite branch-and-bound illustration](figures/branch_bound.svg)

Figures are labeled conceptual or measured. Numerical traces come from preserved tiny-run JSON/logs; arrows in conceptual diagrams are explanatory geometry, not measured backend events. [Regeneration and provenance](FIGURES.md).

## 7. Parameters and effects

max_nodes=1024 dense-SDP guard; two MPI ranks; requested seed must be 2020 because the pinned source hardcodes srand(2020). No work-counter budget or native warm start supported.

Copyable config: [`configs/portfolio/biqbin.json`](../../configs/portfolio/biqbin.json). Do not supply unsupported options; they are rejected rather than silently ignored.

## 8. Complexity and memory

Conversion is sparse O(n+m). Native SDP methods can use dense O(n²) matrices and expensive bound work; sparse exact/MQLib internal memory depends on its actual native algorithm. Conservative adapter guards do not predict practical runtime or avoid every native allocation.

## 9. Exactness and certification limits

Only an actual Optimal payload, successful completion and recovered assignment earn solver_reported_optimal. Printed root bounds are conservatively padded before integer-floor rescaling. Floating SDP/native tolerances are not an independently checked certificate. Execution status, feasible assignment and optimality evidence remain separate. No serialized independently checked certificate is claimed by this portfolio.

## 10. Source-to-code mapping

external/BiqBin/biqbin, main.c/bab_functions.c and native JSON writer, pinned Git revision.

Primary source records: [`biqbin`](../../papers/README.md#biqbin). [External pins/builds](EXTERNAL_BUILDS.md) and [reading notes](SOURCE_REVIEW.md) distinguish obtained full text, unavailable PDFs, and inspected source code.

## 11. Run and interpret outputs

```bash
uv run python run_solver.py --solver biqbin \
  --instance evidence/portfolio/shared_validation_final/inputs/trap.txt \
  --config configs/portfolio/biqbin.json --seed 2020 \
  --time-limit 10 --output runs/biqbin_example_01
```

Choose a new suffix if the output already exists. Optional methods require their extras/source builds from [setup](EXTERNAL_BUILDS.md). Read `result.json` and actual `worker.log`/native logs; `solutions/<input basename>` is written only for validated labels. The tiny example has no professor reference score: official cut verification still runs, while reference score is null. `upper_bound=null` means no bound was computed, not zero gap. QuBowl deliberately returns unavailable with no assignment.

## 12. Implementation deviations

The tested command has exactly five user arguments: graph.txt params run 1 2. The README describes an older extra-bound argument; adapter follows actual argc/source. Host versioned BLAS/LAPACK link override is explicit.
