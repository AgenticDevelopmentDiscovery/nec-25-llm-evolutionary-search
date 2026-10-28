# Authors’ Tabu-Enhanced Simulated Bifurcation

## 1. Problem and supported input

The target is original signed weighted Max-Cut: $F(s)=\sum_E w_{ij}(1-s_i s_j)/2$. Each edge is counted once; positive weights favor opposite signs and negative weights favor equal signs. Original node order is preserved. See [shared contract](ARCHITECTURE.md) and [objective/transformation details](MATHEMATICS.md). This method's actual availability, topology/size restrictions, warm-start use and work unit are exposed by `uv run python run_solver.py --solver tesb --features`.

## 2. Intuition

Run the pinned authors’ CPU implementation in a warm phase, then use its continuous checking dynamics with sampled history-dependent repulsion.

## 3. Formulation and conventions

The reviewed CPU code uses a momentum force $-(\delta-p)x+\xi(Ax-\widehat S)$ with $A=-W$, where $\widehat S$ is the sampled tabu-sign sum divided by the configured sampled-history count. Its update is momentum first, then position, followed by walls.

## 4. Algorithm steps

Load the original tSB.py class from its separate pinned checkout. Temporarily save legacy RNG/environment, reseed after import, build sparse CSR J, run warm SB.update_b, record all warm replica signs into tabu history, then run checking SB.update_b with sampled tabu entries. Evaluate both phases on original F and retain best/incumbent. Restore caller RNG/environment.

## 5. Fully worked small example

A +2 AB graph maps to CSR off-diagonals −2. In the warm phase, xB<0 pushes A’s momentum positively through A*x. During checking, the same physical force has an added sampled-history repulsion. Its actual cut still comes only from original final signs, not the internal continuous energy.

[All required hand examples](MATHEMATICS.md#hand-worked-reference-instances) and [validation report](VERIFICATION.md) provide independent reference optima and original-format fixtures.

## 6. Illustration

![Authors’ Tabu-Enhanced Simulated Bifurcation illustration](figures/replicas.svg)

Figures are labeled conceptual or measured. Numerical traces come from preserved tiny-run JSON/logs; arrows in conceptual diagrams are explanatory geometry, not measured backend events. [Regeneration and provenance](FIGURES.md).

## 7. Parameters and effects

warm_fraction=.2 of total max_work steps, warm_samples=16, check_samples=8, tabu_sample=2, dt=1. warm_xi=None invokes authors’ max-absolute-signed-row-sum reciprocal, with 0 for zero denominator; check_xi=.05. seed is reduced modulo 2^32 and caller state restored.

Copyable config: [`configs/portfolio/tesb.json`](../../configs/portfolio/tesb.json). Do not supply unsupported options; they are rejected rather than silently ignored.

## 8. Complexity and memory

Authors’ sparse CSR CPU path uses $O(nR+m+nH)$ history/state memory (H warm_samples); time is sparse matrix multiplication plus sampled-history work per step. The default stored history is bounded; no dense graph adjacency.

## 9. Exactness and certification limits

Heuristic, no upper bound. No binary polishing. Warm/checking raw phase cuts and the final retained answer are distinct. The upstream global-RNG adapter is serial and not thread-safe. Execution status, feasible assignment and optimality evidence remain separate. No serialized independently checked certificate is claimed by this portfolio.

## 10. Source-to-code mapping

portfolio_tesb.solve_tesb → external/TESB/tSB.py SB.update_b at the recorded source pin and SHA. Paper DOI 10.1038/s42005-026-02538-2 plus actual CPU source were reviewed.

Primary source records: [`tesb`](../../papers/README.md#tesb). [External pins/builds](EXTERNAL_BUILDS.md) and [reading notes](SOURCE_REVIEW.md) distinguish obtained full text, unavailable PDFs, and inspected source code.

## 11. Run and interpret outputs

```bash
uv run python run_solver.py --solver tesb \
  --instance evidence/portfolio/shared_validation_final/inputs/trap.txt \
  --config configs/portfolio/tesb.json --seed 1 \
  --time-limit 10 --output runs/tesb_example_01
```

Choose a new suffix if the output already exists. Optional methods require their extras/source builds from [setup](EXTERNAL_BUILDS.md). Read `result.json` and actual `worker.log`/native logs; `solutions/<input basename>` is written only for validated labels. The tiny example has no professor reference score: official cut verification still runs, while reference score is null. `upper_bound=null` means no bound was computed, not zero gap. QuBowl deliberately returns unavailable with no assignment.

## 12. Implementation deviations

This integrates the authors’ CPU code, not a new discrete tabu algorithm. The code’s sampled repulsion differs from a full gradient of the paper’s stated Hamiltonian penalty (which includes additional x-dependent terms); those are not asserted equivalent. Zero-row normalization guard and explicit step allocation are adapter policies.
