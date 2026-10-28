# QuBowl availability investigation — blocked

## 1. Problem and supported input

The target is original signed weighted Max-Cut: $F(s)=\sum_E w_{ij}(1-s_i s_j)/2$. Each edge is counted once; positive weights favor opposite signs and negative weights favor equal signs. Original node order is preserved. See [shared contract](ARCHITECTURE.md) and [objective/transformation details](MATHEMATICS.md). This method's actual availability, topology/size restrictions, warm-start use and work unit are exposed by `uv run python run_solver.py --solver qubowl --features`.

## 2. Intuition

QuBowl is a distinct specialized exact implementation; another SCIP model cannot be renamed to satisfy its integration requirement.

## 3. Formulation and conventions

The research target remains original $F(s)$ with primal/dual bounds from its own exact algorithm. No local invocation or QuBowl bound is fabricated.

## 4. Algorithm steps

Review Rehfeldt–Koch–Shinano full paper; investigate official availability and author statements; retain the paper and precise source references. No obtainable official source was identified, so dispatch returns unavailable without assignment.

## 5. Fully worked small example

The +2 edge has optimum 2 by independent enumeration. That arithmetic does not demonstrate QuBowl ran. Its current adapter returns cut=null, assignment=null and execution_status=unavailable even on this trivial input.

[All required hand examples](MATHEMATICS.md#hand-worked-reference-instances) and [validation report](VERIFICATION.md) provide independent reference optima and original-format fixtures.

## 6. Illustration

![QuBowl availability investigation — blocked illustration](figures/branch_bound.svg)

Figures are labeled conceptual or measured. Numerical traces come from preserved tiny-run JSON/logs; arrows in conceptual diagrams are explanatory geometry, not measured backend events. [Regeneration and provenance](FIGURES.md).

## 7. Parameters and effects

No executable, runtime flags or warm-start API are invented. A future obtainable release would need its own pinned source, build, format conversion and witness/bound validation.

Copyable config: [`configs/portfolio/qubowl.json`](../../configs/portfolio/qubowl.json). Do not supply unsupported options; they are rejected rather than silently ignored.

## 8. Complexity and memory

The paper discusses sparse exact solving; no local performance or memory measurement is claimed because no executable was obtained.

## 9. Exactness and certification limits

No implemented solver and no local optimality claim. The structured unavailable result is an availability check, not a completed integration. Execution status, feasible assignment and optimality evidence remain separate. No serialized independently checked certificate is claimed by this portfolio.

## 10. Source-to-code mapping

solver_portfolio.solve qubowl branch; papers/qubowl.pdf; EXTERNAL_BUILDS.md. Author’s official SCIP mailing-list response dated March 6, 2024 states code was not public or part of SCIP; current search found no official release.

Primary source records: [`qubowl`](../../papers/README.md#qubowl). [External pins/builds](EXTERNAL_BUILDS.md) and [reading notes](SOURCE_REVIEW.md) distinguish obtained full text, unavailable PDFs, and inspected source code.

## 11. Run and interpret outputs

```bash
uv run python run_solver.py --solver qubowl \
  --instance evidence/portfolio/shared_validation_final/inputs/trap.txt \
  --config configs/portfolio/qubowl.json --seed 1 \
  --time-limit 10 --output runs/qubowl_example_01
```

Choose a new suffix if the output already exists. Optional methods require their extras/source builds from [setup](EXTERNAL_BUILDS.md). Read `result.json` and actual `worker.log`/native logs; `solutions/<input basename>` is written only for validated labels. The tiny example has no professor reference score: official cut verification still runs, while reference score is null. `upper_bound=null` means no bound was computed, not zero gap. QuBowl deliberately returns unavailable with no assignment.

## 12. Implementation deviations

Blocked with an explicit reason as permitted by the brief. The generic MILP and SMS integrations remain separately named and do not substitute for QuBowl.
