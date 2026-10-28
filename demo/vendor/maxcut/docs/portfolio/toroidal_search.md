# Toroidal cycle-repair search

## 1. Problem and supported input

The target is original signed weighted Max-Cut: $F(s)=\sum_E w_{ij}(1-s_i s_j)/2$. Each edge is counted once; positive weights favor opposite signs and negative weights favor equal signs. Original node order is preserved. See [shared contract](ARCHITECTURE.md) and [objective/transformation details](MATHEMATICS.md). This method's actual availability, topology/size restrictions, warm-start use and work unit are exposed by `uv run python run_solver.py --solver toroidal_search --features`.

## 2. Intuition

Start with the same face-parity matching bound, then repair global-cycle inconsistencies to improve an actual feasible assignment. Keep that feasible trajectory separate from its upper bound.

## 3. Formulation and conventions

Local faces plus two fundamental global cycles are required for globally integrable edge signs. Candidate quality is original $F(s)$; $U-F(s)$ is the remaining bound gap.

## 4. Algorithm steps

Verify the complete periodic embedding and compute initial local matching bound. Recover a feasible current state. Use upstream generator cycles and matching-based cycle-repair proposals, accepting nondecreasing feasible quality. Stop at equality, stall, repair count or time. Retain best original-order labels and never call an inconsistent edge set a cut.

## 5. Fully worked small example

On the preserved 3×3 signed fixture, the initial feasible cut is 8 and U=9. Bounded repairs retain cut 8 and report the remaining unit gap; absence of further improvement does not promote 8 to a proven optimum. Independent exhaustive enumeration supplies the separate tiny optimum check.

[All required hand examples](MATHEMATICS.md#hand-worked-reference-instances) and [validation report](VERIFICATION.md) provide independent reference optima and original-format fixtures.

## 6. Illustration

![Toroidal cycle-repair search illustration](figures/torus.svg)

Figures are labeled conceptual or measured. Numerical traces come from preserved tiny-run JSON/logs; arrows in conceptual diagrams are explanatory geometry, not measured backend events. [Regeneration and provenance](FIGURES.md).

## 7. Parameters and effects

max_expanded_nodes=4096, max_stall=10 consecutive non-improving repairs, max_work counts additional cycle-repair iterations. Seed controls starting/cycle choices; a supplied warm assignment initializes the actual repair state.

Copyable config: [`configs/portfolio/toroidal_search.json`](../../configs/portfolio/toroidal_search.json). Do not supply unsupported options; they are rejected rather than silently ignored.

## 8. Complexity and memory

Each repair can require an expanded-dual blossom computation; sparse primal state but expensive matching workspace. Hard CLI time caps protect calls whose internals have no cooperative interruption.

## 9. Exactness and certification limits

Search is heuristic; only a feasible cut attaining computed U supports the bound-attainment conclusion. The initial U remains an upper bound even when search stalls. Execution status, feasible assignment and optimality evidence remain separate. No serialized independently checked certificate is claimed by this portfolio.

## 10. Source-to-code mapping

portfolio_topology.solve_toroidal(search=True), upstream find_generator_cycles/matching/painting primitives. Local wrappers preserve original indices and sparse inputs.

Primary source records: [`toroidal`](../../papers/README.md#toroidal), [`domain_walls`](../../papers/README.md#domain-walls). [External pins/builds](EXTERNAL_BUILDS.md) and [reading notes](SOURCE_REVIEW.md) distinguish obtained full text, unavailable PDFs, and inspected source code.

## 11. Run and interpret outputs

```bash
uv run python run_solver.py --solver toroidal_search \
  --instance evidence/portfolio/shared_validation_final/inputs/torus.txt \
  --config configs/portfolio/toroidal_search.json --seed 1 \
  --time-limit 10 --output runs/toroidal_search_example_01
```

Choose a new suffix if the output already exists. Optional methods require their extras/source builds from [setup](EXTERNAL_BUILDS.md). Read `result.json` and actual `worker.log`/native logs; `solutions/<input basename>` is written only for validated labels. The tiny example has no professor reference score: official cut verification still runs, while reference score is null. `upper_bound=null` means no bound was computed, not zero gap. QuBowl deliberately returns unavailable with no assignment.

## 12. Implementation deviations

Uses the reviewed LP-bound/cycle primitives in a bounded educational controller, not a claim to reproduce every upstream HAPI mode. No full toroidal exact optimizer is advertised when the bound is not attained.
