# Generic exact XOR MILP using SCIP

## 1. Problem and supported input

The target is original signed weighted Max-Cut: $F(s)=\sum_E w_{ij}(1-s_i s_j)/2$. Each edge is counted once; positive weights favor opposite signs and negative weights favor equal signs. Original node order is preserved. See [shared contract](ARCHITECTURE.md) and [objective/transformation details](MATHEMATICS.md). This method's actual availability, topology/size restrictions, warm-start use and work unit are exposed by `uv run python run_solver.py --solver milp --features`.

## 2. Intuition

Represent a cut edge by the XOR of its two binary endpoint decisions, then let SCIP branch and bound the resulting sparse integer program.

## 3. Formulation and conventions

$x_i=(1-s_i)/2\in\{0,1\}$ and $0\le y_{ij}\le1$. Enforce both lower bounds $y\ge x_i-x_j,x_j-x_i$ and both upper bounds $y\le x_i+x_j,2-x_i-x_j$. Maximize $\sum_Ew_{ij}y_{ij}$; fix global $x_0=0$.

## 4. Algorithm steps

Create original-order binary nodes and continuous edge indicators; add all four XOR inequalities. Inject a complete native incumbent with its exact XOR values. Set time, node, gap and feasibility controls. Extract native signs, direct F, primal, dual, gap, status, tolerances and node count.

## 5. Fully worked small example

For a −2 edge, equal binary endpoints force y=0 and value 0. Unequal endpoints force y=1 and value −2. Omitting a lower or upper inequality can allow an indicator inconsistent with the cut, particularly for signed weights. All four inequalities remove that ambiguity.

[All required hand examples](MATHEMATICS.md#hand-worked-reference-instances) and [validation report](VERIFICATION.md) provide independent reference optima and original-format fixtures.

## 6. Illustration

![Generic exact XOR MILP using SCIP illustration](figures/branch_bound.svg)

Figures are labeled conceptual or measured. Numerical traces come from preserved tiny-run JSON/logs; arrows in conceptual diagrams are explanatory geometry, not measured backend events. [Regeneration and provenance](FIGURES.md).

## 7. Parameters and effects

Optional milp extra; max_nodes=5000 model guard, feasibility_tolerance=1e-9, relative_gap=0. max_work counts branch nodes; seconds includes setup via remaining native solve allowance. Seed shift is requested seed modulo 2^31−1.

Copyable config: [`configs/portfolio/milp.json`](../../configs/portfolio/milp.json). Do not supply unsupported options; they are rejected rather than silently ignored.

## 8. Complexity and memory

$O(n+m)$ variables/constraints and sparse model data; exponential worst-case search and potentially large native branch/cut storage. Model construction is also timed by the outer runner.

## 9. Exactness and certification limits

Native optimal status means solver-reported optimum within SCIP floating tolerances. Nonzero requested gap can stop without exact completion; status remains distinct. No standalone rational certificate is checked. Execution status, feasible assignment and optimality evidence remain separate. No serialized independently checked certificate is claimed by this portfolio.

## 10. Source-to-code mapping

portfolio_milp.solve_milp; derivation and all four truth-table cases are in MATHEMATICS.md. This project formulation is independent of SMS.

Primary source records: [`scientific`](../../papers/README.md#scientific). [External pins/builds](EXTERNAL_BUILDS.md) and [reading notes](SOURCE_REVIEW.md) distinguish obtained full text, unavailable PDFs, and inspected source code.

## 11. Run and interpret outputs

```bash
uv run python run_solver.py --solver milp \
  --instance evidence/portfolio/shared_validation_final/inputs/trap.txt \
  --config configs/portfolio/milp.json --seed 1 \
  --time-limit 10 --output runs/milp_example_01
```

Choose a new suffix if the output already exists. Optional methods require their extras/source builds from [setup](EXTERNAL_BUILDS.md). Read `result.json` and actual `worker.log`/native logs; `solutions/<input basename>` is written only for validated labels. The tiny example has no professor reference score: official cut verification still runs, while reference score is null. `upper_bound=null` means no bound was computed, not zero gap. QuBowl deliberately returns unavailable with no assignment.

## 12. Implementation deviations

Generic edge-XOR formulation rather than SMS’s refined model/separators. PySCIPOpt uses its own installed SCIP; SMS was separately built against the native prefix.
