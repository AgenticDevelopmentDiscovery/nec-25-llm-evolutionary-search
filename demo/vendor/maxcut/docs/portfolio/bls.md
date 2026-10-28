# Breakout Local Search

## 1. Problem and supported input

The target is original signed weighted Max-Cut: $F(s)=\sum_E w_{ij}(1-s_i s_j)/2$. Each edge is counted once; positive weights favor opposite signs and negative weights favor equal signs. Original node order is preserved. See [shared contract](ARCHITECTURE.md) and [objective/transformation details](MATHEMATICS.md). This method's actual availability, topology/size restrictions, warm-start use and work unit are exposed by `uv run python run_solver.py --solver bls --features`.

## 2. Intuition

Alternate ascent to a local optimum with history-guided or random perturbation of that current optimum. Adapt jump magnitude when the same attractor recurs.

## 3. Formulation and conventions

$P=\max(\exp(-\omega/T),P_0)$ selects directed versus random perturbation. Directed single/pair gains use $g_i$ and $g_i+g_j-2w_{ij}s_i s_j$. Tabu aspiration requires beating the retained global best.

## 4. Algorithm steps

Run steepest one-flip ascent ignoring tabu, as in the paper. Compare actual attractor labels to the previous attractor: increment jump on repetition, reset otherwise. Select one mode for the phase: M1 single, M2 opposite-side pair, or M3 uniform random. Update random tabu tenures after every flip; force random mode after too many unimproved attractors. Continue from the resulting current state, not the saved best.

## 5. Fully worked small example

AB|CD on the trap has all gains −1. A directed single can move to 7, allowing subsequent ascent to 10. Exchanging A+ with C− directly changes the cut by −1−1−2*2*(−1)=2, reaching 10. Individual gains alone would incorrectly predict −2. Best labels are stored separately before another perturbation.

[All required hand examples](MATHEMATICS.md#hand-worked-reference-instances) and [validation report](VERIFICATION.md) provide independent reference optima and original-format fixtures.

## 6. Illustration

![Breakout Local Search illustration](figures/escape.svg)

Figures are labeled conceptual or measured. Numerical traces come from preserved tiny-run JSON/logs; arrows in conceptual diagrams are explanatory geometry, not measured backend events. [Regeneration and provenance](FIGURES.md).

## 7. Parameters and effects

jump=max(1,ceil(.01*n)), stagnation=1000 attractors, p_min=.8, q=.5, tenure_min=3, tenure_max=max(3,n//10). max_work counts individual flips: M2 consumes two. Jump increments on repeated labels, not merely an equal objective.

Copyable config: [`configs/portfolio/bls.json`](../../configs/portfolio/bls.json). Do not supply unsupported options; they are rejected rather than silently ignored.

## 8. Complexity and memory

Readable gain scans cost $O(n)$ per choice, update $O(deg(i))$, state $O(n+m)$. No integer bucket sorting is implemented; this favors clarity over the paper’s high-throughput implementation.

## 9. Exactness and certification limits

Heuristic, no upper bound. A worsening trajectory is intentional and global best never aliases current. Direct rescoring protects incumbent quality. Execution status, feasible assignment and optimality evidence remain separate. No serialized independently checked certificate is claimed by this portfolio.

## 10. Source-to-code mapping

portfolio_search.solve_bls implements Benlic–Hao Algorithms 1–3 and Sections 2.1–2.4; pair internal-edge correction and joint aspiration are explicit. Stagnation tracks retained progress across perturbation intermediates.

Primary source records: [`bls`](../../papers/README.md#bls). [External pins/builds](EXTERNAL_BUILDS.md) and [reading notes](SOURCE_REVIEW.md) distinguish obtained full text, unavailable PDFs, and inspected source code.

## 11. Run and interpret outputs

```bash
uv run python run_solver.py --solver bls \
  --instance evidence/portfolio/shared_validation_final/inputs/trap.txt \
  --config configs/portfolio/bls.json --seed 1 \
  --time-limit 10 --output runs/bls_example_01
```

Choose a new suffix if the output already exists. Optional methods require their extras/source builds from [setup](EXTERNAL_BUILDS.md). Read `result.json` and actual `worker.log`/native logs; `solutions/<input basename>` is written only for validated labels. The tiny example has no professor reference score: official cut verification still runs, while reference score is null. `upper_bound=null` means no bound was computed, not zero gap. QuBowl deliberately returns unavailable with no assignment.

## 12. Implementation deviations

Finite-decimal scans replace integer buckets; tiny-graph jump/tenure floors, random fallback when directed moves are impossible, a final one-flip remainder, and retention of transient improvements are explicit project extensions. M2 first selects highest individually eligible vertices on each side; if joint aspiration fails it retries with non-tabu vertices. This is not an all-pairs neighborhood maximizer.
