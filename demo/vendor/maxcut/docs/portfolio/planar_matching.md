# Exact signed planar matching reduction

## 1. Problem and supported input

The target is original signed weighted Max-Cut: $F(s)=\sum_E w_{ij}(1-s_i s_j)/2$. Each edge is counted once; positive weights favor opposite signs and negative weights favor equal signs. Original node order is preserved. See [shared contract](ARCHITECTURE.md) and [objective/transformation details](MATHEMATICS.md). This method's actual availability, topology/size restrictions, warm-start use and work unit are exposed by `uv run python run_solver.py --solver planar_matching --features`.

## 2. Intuition

Choose the preferred relation on each edge, then pay the smallest total absolute weight needed to repair frustrated face parity. On a plane, face consistency reconstructs vertex signs.

## 3. Formulation and conventions

Let $t_e=1$ for $w_e>0$. Face defects have odd sum of preferred cut indicators. A minimum-cost dual T-join with cost $D$ gives $F^*=\sum_E\max(w_e,0)-D$.

## 4. Algorithm steps

Check planarity and obtain a combinatorial embedding for each connected component. Walk oriented faces, treating bridge incidences correctly. Build the weighted dual, shortest-path defect metric and minimum perfect matching. XOR matched paths into violated-edge indicators; reconstruct signs and check every primal edge. Assert exact scaled objective equals the matching expression.

## 5. Fully worked small example

An all-positive unit triangle prefers cutting all three edges, impossible around either face. The two face defects pair across a cheapest edge of cost 1. Positive sum=3, repair cost=1, exact optimum=2. Signs (+,−,+) provide the feasible witness.

[All required hand examples](MATHEMATICS.md#hand-worked-reference-instances) and [validation report](VERIFICATION.md) provide independent reference optima and original-format fixtures.

## 6. Illustration

![Exact signed planar matching reduction illustration](figures/torus.svg)

Figures are labeled conceptual or measured. Numerical traces come from preserved tiny-run JSON/logs; arrows in conceptual diagrams are explanatory geometry, not measured backend events. [Regeneration and provenance](FIGURES.md).

## 7. Parameters and effects

max_defects=256 and max_nodes=100000 are explicit resource guards. max_work counts connected components, seconds checked between expensive operations; use CLI hard cap around matching. Nonplanar inputs are unavailable for this method, not silently approximated.

Copyable config: [`configs/portfolio/planar_matching.json`](../../configs/portfolio/planar_matching.json). Do not supply unsupported options; they are rejected rather than silently ignored.

## 8. Complexity and memory

Sparse primal/dual storage plus a potentially dense defect metric $O(|T|^2)$. Blossom matching is polynomial but expensive; Dijkstra distances are computed per defect and only matched paths reconstructed to avoid all-path storage.

## 9. Exactness and certification limits

Complete verified reduction reports solver-reported optimal under exact scaled-integer matching/embedding assumptions. Independent reconstruction and oracle comparisons validate the reduction; no separately checked serialized certificate is emitted. Execution status, feasible assignment and optimality evidence remain separate. No serialized independently checked certificate is claimed by this portfolio.

## 10. Source-to-code mapping

portfolio_topology.solve_planar; NetworkX planarity/Dijkstra/perfect matching. Primary references Pardella–Liers and periodic-boundary literature explain frustration/matching; the local signed T-join code is independent of upstream toroidal HAPI.

Primary source records: [`planar`](../../papers/README.md#planar), [`domain_walls`](../../papers/README.md#domain-walls). [External pins/builds](EXTERNAL_BUILDS.md) and [reading notes](SOURCE_REVIEW.md) distinguish obtained full text, unavailable PDFs, and inspected source code.

## 11. Run and interpret outputs

```bash
uv run python run_solver.py --solver planar_matching \
  --instance evidence/portfolio/shared_validation_final/inputs/trap.txt \
  --config configs/portfolio/planar_matching.json --seed 1 \
  --time-limit 10 --output runs/planar_matching_example_01
```

Choose a new suffix if the output already exists. Optional methods require their extras/source builds from [setup](EXTERNAL_BUILDS.md). Read `result.json` and actual `worker.log`/native logs; `solutions/<input basename>` is written only for validated labels. The tiny example has no professor reference score: official cut verification still runs, while reference score is null. `upper_bound=null` means no bound was computed, not zero gap. QuBowl deliberately returns unavailable with no assignment.

## 12. Implementation deviations

Project implementation uses generic face-dual T-join matching rather than claiming the precise specialized expanded-lattice performance algorithm of Pardella–Liers. No magnetic fields and no nonplanar fallback.
