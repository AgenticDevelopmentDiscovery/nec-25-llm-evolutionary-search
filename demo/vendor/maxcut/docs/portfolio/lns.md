# Large-neighborhood search with exact conditional repair

## 1. Problem and supported input

The target is original signed weighted Max-Cut: $F(s)=\sum_E w_{ij}(1-s_i s_j)/2$. Each edge is counted once; positive weights favor opposite signs and negative weights favor equal signs. Original node order is preserved. See [shared contract](ARCHITECTURE.md) and [objective/transformation details](MATHEMATICS.md). This method's actual availability, topology/size restrictions, warm-start use and work unit are exposed by `uv run python run_solver.py --solver lns --features`.

## 2. Intuition

Release a selected subset of signs, keep outside labels fixed, and solve that conditional problem. Larger neighborhoods can escape a one-flip trap.

## 3. Formulation and conventions

$F=C_{out}+\sum_{i,j\in B}w_{ij}(1-s_i s_j)/2+\sum_{i\in B,j\notin B}w_{ij}(1-s_i\bar s_j)/2$. Boundary terms are essential linear fields.

## 4. Algorithm steps

Choose uniform, connected, violated-weight or mixed subset. Enumerate at most 20 released spins or use full XOR MILP with outside variables fixed. Do not remove a released-spin complement symmetry. Keep a strict improved full assignment; record whether the conditional subproblem completed. Retain old best on ties or weaker partial returns.

## 5. Fully worked small example

Release A of +2 AB while B is fixed +. A+ contributes 0 and A− contributes 2. Add a fixed outside +3 cut and full conditional optimum becomes 5. Holding A arbitrarily positive or dropping the boundary would give the wrong answer.

[All required hand examples](MATHEMATICS.md#hand-worked-reference-instances) and [validation report](VERIFICATION.md) provide independent reference optima and original-format fixtures.

## 6. Illustration

![Large-neighborhood search with exact conditional repair illustration](figures/neighborhood.svg)

Figures are labeled conceptual or measured. Numerical traces come from preserved tiny-run JSON/logs; arrows in conceptual diagrams are explanatory geometry, not measured backend events. [Regeneration and provenance](FIGURES.md).

## 7. Parameters and effects

subset_size=12, selection=mixed, repair=auto, repair_work=1048576. auto enumerates <=20 released nodes and uses optional MILP above that. max_work counts neighborhoods; repair_work limits states/branch work inside each. Timeouts are separately recorded.

Copyable config: [`configs/portfolio/lns.json`](../../configs/portfolio/lns.json). Do not supply unsupported options; they are rejected rather than silently ignored.

## 8. Complexity and memory

Enumeration costs $O(2^{|B|}(m_{internal}+m_{boundary})+m)$ and sparse memory. MILP uses a full sparse model with fixed outside nodes. Selection and decomposition add graph-linear work.

## 9. Exactness and certification limits

A completed neighborhood is conditionally optimal only. It does not prove global optimality unless it releases every node and a separate global proof is established; the LNS result itself remains unproven with null global upper bound. Execution status, feasible assignment and optimality evidence remain separate. No serialized independently checked certificate is claimed by this portfolio.

## 10. Source-to-code mapping

portfolio_neighborhood.repair_exact / solve_lns; portfolio_milp.solve_milp(free_nodes=...); portfolio_perturbations.select_subset. See MATHEMATICS.md for boundary derivation.

Primary source records: [`bm`](../../papers/README.md#bm). [External pins/builds](EXTERNAL_BUILDS.md) and [reading notes](SOURCE_REVIEW.md) distinguish obtained full text, unavailable PDFs, and inspected source code.

## 11. Run and interpret outputs

```bash
uv run python run_solver.py --solver lns \
  --instance evidence/portfolio/shared_validation_final/inputs/trap.txt \
  --config configs/portfolio/lns.json --seed 1 \
  --time-limit 10 --output runs/lns_example_01
```

Choose a new suffix if the output already exists. Optional methods require their extras/source builds from [setup](EXTERNAL_BUILDS.md). Read `result.json` and actual `worker.log`/native logs; `solutions/<input basename>` is written only for validated labels. The tiny example has no professor reference score: official cut verification still runs, while reference score is null. `upper_bound=null` means no bound was computed, not zero gap. QuBowl deliberately returns unavailable with no assignment.

## 12. Implementation deviations

This is a project LNS controller, not a named published implementation. Conditional exhaustive/MILP search is exact when completed, but the subset-selection/controller is heuristic.
