# Building and observing the system

## Solver programs {#program data-seconds="45"}

::: {.question}
**What can Luna edit if the assignment itself is not the evolving artifact?**
:::

::: {.block}
A program has one to three stages: algorithm, configuration, work cap and start rule.

```text
bm(max_sweeps=20, rounding_count=8); retained
→ bls(max_work=9000); retained
```
:::

::: {.block}
Execute a program → obtain signs → recompute the original cut → summarize three trials → rank the program.

Retained **Tabu Search → Burer–Monteiro** lifts and perturbs the incoming partition before vector refinement.
:::

::: {.answer}
**Evolve the solver; evaluate its witness.** Trusted kernels execute the stages. Unchecked algorithms remain available to the mutator.
:::

::: {.notes}
The identifiers bm and bls denote the rank-two Burer–Monteiro method and Breakout Local Search. The displayed composition was proposed in the earlier genuine dense-graph rehearsal. Each schema stage contains backend, config, max_work and fresh. Missing defaults are normalized before hashing so equivalent encodings cannot receive separate evaluations merely by omitting a default.

A retained stage receives a copy of the best witness from preceding work in the same trial. A fresh stage uses a seeded random exploratory start; the interpreter retains an older better witness if the new stage is worse. Remaining numerical time is allocated among remaining stages, with unused time carried forward. The model supplies data describing this bounded interpreter, not shell commands or arbitrary source code.

Distinguish replacement from composition. A child containing only Tabu Search replaces a Burer–Monteiro parent as a program and starts from the same raw trial labels as its competitors. It does not consume that previously evaluated parent's final partition. A child containing Burer–Monteiro followed by retained Tabu Search passes the best partition between its own stages. In the reverse retained order, the classroom adapter embeds the incoming Tabu partition as vector angles 0 or pi, adds seeded uniform offsets in [-0.35, 0.35] radians, optimizes those vectors, then rounds and polishes. It keeps the incoming partition if the new result is worse. This changes the complete solver recipe; it does not rewrite Tabu Search's internal algorithm. First-stage and fresh Burer–Monteiro stages keep their original independent vector search. Older recorded replays preserve their original execution behavior and do not demonstrate this new downstream refinement.
:::

## Four numerical algorithms {#kernels data-seconds="70"}

::: {.question}
**Which mechanism changes when we choose a different solver stage?**
:::

::: {.block}
**Tabu Search:** best admissible flips, temporary reversal bans and aspiration. **Simulated Annealing:** temperature-dependent acceptance of random flips.
:::

::: {.block}
**Breakout Local Search:** improving descent followed by adaptive perturbations. **Rank-two Burer–Monteiro:** unit-vector refinement, projection to signs and polish.
:::

::: {.answer}
**Acceptance, memory, escape and representation are different design levers.** Full examples and parameter meanings are available in the algorithm guide.
:::

::: {.notes}
Tabu Search maintains current signs, one-flip gains, tabu expiry and a separate best witness. It flips the highest-gain admissible vertex even when the gain is nonpositive. Seeded ties are reproducible. A flip at iteration t sets expiry to t+tenure+1; aspiration admits an otherwise prohibited flip if it would beat the global incumbent. restart_after=0 disables a stagnation restart. The work cap is 20000 iterations.

Simulated Annealing proposes a uniformly selected vertex and accepts a gain Δ with probability min(1,exp(Δ/T)). Temperature falls geometrically over the proposal budget. A logarithmic comparison avoids unstable exponentiation; optional bounded improving-flip polish shares the trial clock. The cap is 200000 proposals.

Breakout Local Search alternates steepest improving descent and perturbation. Repeating the same local optimum can increase jump magnitude. Its adaptive mechanism chooses directed tabu single/pair moves or random perturbation. The controls jump, stagnation, p_min, q and tenure_min/max govern that choice; the cap is 12000 individual flips. These work units are not interchangeable with tabu iterations or annealing proposals.

The Burer–Monteiro-style implementation uses two-dimensional unit vectors, coordinate refinement, projection directions and discrete polish. It allows one solve with at most 60 sweeps and 16 directions. An encountered nonconvex relaxed value is not a certified Max-Cut upper bound. Warm signs participate in the preserved extended path and remain eligible for retention. All 133 hashed reference files stay unchanged; classroom adaptations live outside the vendor snapshot.
:::

## Initial population and fair starts {#initialization data-seconds="40"}

::: {.question}
**Do the solver checkboxes change the initial population or the whole search space?**
:::

::: {.block}
Checkboxes choose $P_0$. Every selected program and proposed child receives copies of the same raw starts for seeds 3, 4 and 5.
:::

::: {.block}
All four trusted kernels remain available to Luna. Both current graphs allow 8 numerical seconds per trial. The selected seed programs produce distinct initial fitness on the 1,000-vertex graph.
:::

::: {.answer}
**Change initialization deliberately and hold the comparison protocol fixed.** A missing seed algorithm can still appear in a later mutation.
:::

::: {.notes}
The first two scenarios hold the 1,000-vertex signed graph, raw starts, seeds, per-trial allowance, kernel catalog, selection and model-call cap constant. Only the seed suite differs. A numerical screen with the same initial programs measured medians 921 for Simulated Annealing, 975 for Tabu Search, 992 for Breakout Local Search and 1012 for Burer–Monteiro. The reference is 1098. These are program-and-budget measurements, not universal rankings of algorithm families. The limited suite contains Tabu Search and Simulated Annealing. The informed suite contains Tabu Search, Breakout Local Search and rank-two Burer–Monteiro. Initial configurations for a given kernel are identical across scenarios; no hidden weak variant is substituted.

The initial configurations are disclosed: tabu tenure 5 with 800 iterations; annealing temperature 2 to 0.01, 6000 proposals and polish; Breakout Local Search 700 flips; Burer–Monteiro 20 sweeps and 8 directions. More seed programs mean more initial evaluations, so numerical effort must be reported alongside calls and wall time. Researcher design effort before the run is not measured by the run clock.
:::

## Designing the three experiments {#experiment-design data-seconds="35"}

::: {.question}
**Which differences can our initialization comparison actually explain?**
:::

::: {.block}
Demos 1 and 2: same signed graph, seeds, trial allowance, mutation catalog and call cap. Change only the initial solver suite.
:::

::: {.block}
Report initial median, calls and time to the median target, all-trial robustness, numerical effort and total teaching-run time.
:::

::: {.answer}
**Declare the success criterion before comparing runs.** The third graph is a separate dense real-weight stress case.
:::

::: {.notes}
The first two experiments use the same 1,000-vertex signed graph with 5,043 edges and supplied reference 1098. The third uses a separate 100-vertex dense graph with 4,950 real-valued signed edges and supplied reference 402.5209. Neither reference is a certified optimum. Earlier torus records remain historical evidence rather than substitutes for these cases.

Primary fitness is median cut across three complete trials. Matching the reference median is weaker than matching it in every trial; the latter additionally requires the minimum to meet the reference. The comparison page exposes both milestones. It reports calls and time to target separately from all calls spent in a fixed three-round teaching run.

These are bounded classroom observations with a stochastic model, not repeated research estimates. Larger seed suites consume more initial numerical effort. Human prior knowledge and its development cost are not captured by the run clock. Changing graph structure and weight distribution in demo three prevents a causal speed comparison with the first two; it tests whether the same architecture still operates on a denser signed problem. Three calls are permitted by the server; the replacement rehearsal has two successful-call slots per case after two network-restricted attempts, all counted within the authorized allowance.
:::

## Demo 1: a limited initialization {#demo-limited data-seconds="180"}


::: {.block}
Use the **1,000-vertex signed graph (5,043 edges)**, seed 3, **Tabu Search and Simulated Annealing**. The initial best median is 975; reference 1098 is unproven.
:::


::: {.notes}
Use the first named preset and confirm two checked algorithms. The server verifies graph, seed and selection metadata. Start evaluates only those programs. At each gate inspect the selected parents and explicitly send their context. A two-parent population supplies two actual parents; no manufactured copies are added to make three.

The earlier BM-only torus demonstration was an algorithm-recovery control, not a recommendation to initialize every task with Burer–Monteiro. That easy graph saturated near its reference and obscured differences. The replacement screen uses unchanged seed configurations and identical raw seeds. Burer–Monteiro is actually the strongest initial program here, so excluding it from this limited suite tests whether mutation can introduce a useful absent mechanism. Recovery and reference matching are hypotheses, never scripted outcomes. The genuine replacement run completed two Luna rounds in 24.003 seconds. Its eligible median improved from 975 to 1008; its best witness was 1031. No reference match occurred. Luna refined the two existing mechanisms rather than introducing Burer–Monteiro, even though all kernels remained available.
:::

## Demo 2: a researcher-selected suite {#demo-informed data-seconds="180"}



::: {.block}
Keep graph, seeds and caps fixed. Select **Tabu Search, Breakout Local Search and rank-two Burer–Monteiro**.
:::



::: {.notes}
The initial medians come from complete numerical trials on common raw starts. The four full seed-program medians are 921, 975, 992 and 1012 for Simulated Annealing, Tabu Search, Breakout Local Search and Burer–Monteiro respectively. Including the stronger relaxation and escape mechanism improves this initial population. No kernel definition or hidden work cap changes between the two scenarios.

More initial programs cost more numerical evaluations and alter the context supplied to Luna. Prior researcher design effort is also a real cost even though it is absent from the run clock. Compare complete-program fitness, best-witness quality, model calls and numerical time. A fluent proposal, an incomplete high-scoring trial or a favorable single run does not establish a general advantage. The genuine replacement run made two model calls in 66.589 seconds. Burer–Monteiro followed by longer Breakout Local Search produced witnesses up to 1060, but its trials were incomplete, so the best eligible median stayed 1012. The second response referred to an ineligible parent and validation stopped the run. Replay labels this source FAILED. This is evidence of the validation and completeness rules, not a successful reference-matching run.
:::


## Demo 3: a dense real-weight stress case {#demo-harder data-seconds="240"}


::: {.block}
Use **100 vertices, 4950 real-valued signed edges**, all four initial solvers and supplied reference **402.5209**, unproven.
:::

::: {.block}
Eight numerical seconds per trial; three Luna calls maximum. Inspect composition, rejection, completeness and the actual surviving programs.
:::


## Reading solver evidence {#harder-evidence data-seconds="45"}

::: {.question}
**Which record proves that a solver improved: the graph, the hypothesis or the completed trials?**
:::

::: {.block}
Require original-order integer signs and a matching graph hash. Recompute the objective from the original signed edges with two scoring paths.
:::

::: {.block}
Rank complete programs by median, minimum, fewer stages and stable genome ID. Retain a valid best witness separately, including one from a censored trial.
:::

::: {.answer}
**Selection follows complete measured evidence.** Preserve failures, timeouts and plateaus so students can inspect the full mechanism.
:::

::: {.notes}
A valid witness answers a feasibility-and-quality question for one execution. A complete candidate ranking answers how its program performed across the declared trials. Neither the model's hypothesis nor an attractive partition drawing supplies fitness. Incomplete programs receive no eligible median/minimum ranking entry, even if all returned witnesses happen to match the reference.

Changing work limits can trade quality against completion risk. The exact-exchange and comparison pages expose requested programs, measured execution time, actual token usage where supplied, invalid proposals and survivor decisions. Calls after a target has already been achieved are visible as teaching continuation. No extra activity or artificial solver motion is fabricated to fill the allotted demonstration window.
:::
