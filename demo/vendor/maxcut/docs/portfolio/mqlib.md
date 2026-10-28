# MQLib independent heuristic portfolio

## 1. Problem and supported input

The target is original signed weighted Max-Cut: $F(s)=\sum_E w_{ij}(1-s_i s_j)/2$. Each edge is counted once; positive weights favor opposite signs and negative weights favor equal signs. Original node order is preserved. See [shared contract](ARCHITECTURE.md) and [objective/transformation details](MATHEMATICS.md). This method's actual availability, topology/size restrictions, warm-start use and work unit are exposed by `uv run python run_solver.py --solver mqlib --features`.

## 2. Intuition

Uses the build’s discovered heuristic identifier. BURER2002 is an upstream BM-family implementation independent of the project’s BM.

## 3. Formulation and conventions

Original one-based GSet edges are passed without integer scaling. The native +/-1 vector and its CSV objective are checked against original F.

## 4. Algorithm steps

Validate supported input, seed, budgets and warm-start capability. Reserve a unique native artifact tree; write the inspected conversion and native parameters. Run the actual executable with owned-process timeout cleanup. Recover a real native witness; independently validate signs, direct original F and native primal agreement. Preserve raw logs, source pin, executable SHA, status and any computed bound.

## 5. Fully worked small example

For +2 AB the native sign vector (+,−) has direct cut 2. For −2, equal signs give 0. Its all-eight/decimal/disconnected checks verify conversion, not a guarantee of global optimization.

[All required hand examples](MATHEMATICS.md#hand-worked-reference-instances) and [validation report](VERIFICATION.md) provide independent reference optima and original-format fixtures.

## 6. Illustration

![MQLib independent heuristic portfolio illustration](figures/branch_bound.svg)

Figures are labeled conceptual or measured. Numerical traces come from preserved tiny-run JSON/logs; arrows in conceptual diagrams are explanatory geometry, not measured backend events. [Regeneration and provenance](FIGURES.md).

## 7. Parameters and effects

heuristic=BURER2002; -l discovers actual supported identifiers, not a guessed BLS name. Seed 0–65535; runtime-only budget. Native runtime uses 80% of remaining API allowance to reserve final-output/parsing time.

Copyable config: [`configs/portfolio/mqlib.json`](../../configs/portfolio/mqlib.json). Do not supply unsupported options; they are rejected rather than silently ignored.

## 8. Complexity and memory

Conversion is sparse O(n+m). Native SDP methods can use dense O(n²) matrices and expensive bound work; sparse exact/MQLib internal memory depends on its actual native algorithm. Conservative adapter guards do not predict practical runtime or avoid every native allocation.

## 9. Exactness and certification limits

Heuristic only; no upper bound or optimal status is inferred from a high cut. Its natural runtime termination is recorded as time_limit even when the executable exits zero. Execution status, feasible assignment and optimality evidence remain separate. No serialized independently checked certificate is claimed by this portfolio.

## 10. Source-to-code mapping

external/MQLib/bin/MQLib; actual -l listing is retained per run. MQLib source/heuristics retain their independent pin.

Primary source records: [`portfolio`](../../papers/README.md#portfolio). [External pins/builds](EXTERNAL_BUILDS.md) and [reading notes](SOURCE_REVIEW.md) distinguish obtained full text, unavailable PDFs, and inspected source code.

## 11. Run and interpret outputs

```bash
uv run python run_solver.py --solver mqlib \
  --instance evidence/portfolio/shared_validation_final/inputs/trap.txt \
  --config configs/portfolio/mqlib.json --seed 1 \
  --time-limit 10 --output runs/mqlib_example_01
```

Choose a new suffix if the output already exists. Optional methods require their extras/source builds from [setup](EXTERNAL_BUILDS.md). Read `result.json` and actual `worker.log`/native logs; `solutions/<input basename>` is written only for validated labels. The tiny example has no professor reference score: official cut verification still runs, while reference score is null. `upper_bound=null` means no bound was computed, not zero gap. QuBowl deliberately returns unavailable with no assignment.

## 12. Implementation deviations

No warm start is exposed by this adapter; supplied labels are rejected. No local polishing is appended. Internal native model allocations are upstream-specific; max_nodes=100000 guard does not promise feasibility on every graph.
