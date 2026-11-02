# 10.5 Diversity and exploration

## Preserve different search behaviors {#islands data-seconds="65"}

::: {.question}
**How can useful alternatives survive beside the current champion?**
:::

::: {.block}
**Islands:** evolve separate populations, with occasional migration. **MAP-Elites:** retain the best program in each behavior bin, such as one-center versus coordinated moves.
:::

::: {.block}
**Novelty search:** favor behaviors unlike those already seen. Different source text alone does not establish different search behavior.
:::

::: {.answer}
**Preserve several ways to search.** These are possible extensions; our top-three controller does not implement a diversity archive.
:::

::: {.notes}
Chapter 10.5.1 motivates preserving several search histories. An island owns a population and mutation history. Occasional migration shares programs; overly frequent migration can make the islands alike, while too little sharing can leave each stalled. Three evaluation seeds are not three islands, and the two circle counts are different problems rather than populations exchanging discoveries.

The Multi-dimensional Archive of Phenotypic Elites (MAP-Elites) organizes candidates by chosen behavior descriptors and keeps a high-quality representative in each bin [@mapelites2015]. For a packing-program archive, illustrative descriptors could measure the typical number of centers moved per proposal and the frequency of restarts. A one-center local search and a coordinated-move search could occupy different bins even if one currently has a lower verified sum. Their quality would still need comparable evaluation conditions. Those descriptors would require instrumentation; the present worker does not record them as a ready-made archive.

Novelty search instead scores behavioral difference from previously observed behaviors [@novelty2011]. A possible descriptor distance could use normalized numerical search statistics. It is not a measure of how unusual a program's variable names sound, and novelty alone does not certify packing quality. These are alternative selection designs whose performance depends on the task and descriptors.

Our controller retains the top three complete programs and rejects exact syntax duplicates. It has no islands, behavioral bins or novelty score. The guide works through the conceptual archive example so students can recognize both its purpose and its absence from the bounded demo.
:::

## Exploration, exploitation and cost {#exploration data-seconds="65"}

::: {.question}
**When should we refine, explore—or stop spending?**
:::

::: {.block}
**Exploit:** refine. **Explore:** change methods. **Stop:** respect the cap.
:::

::: {.block}
**Hypothetical policies**, same test conditions:

| Policy | Median sum | Numerical seconds |
|:--|--:|--:|
| A | 2.40 | 1 |
| B | 2.41 | 5 |
:::

::: {.answer}
**Illustrative utility $S-0.01t$ favors A: $2.39>2.36$.** Our demo reports costs separately.
:::

::: {.notes}
Chapter 10.5.2 frames the explore–exploit tension. Exploitation refines useful inherited structure; exploration tests a different search mechanism. Internal numerical exploration, such as accepting temporary losses, is different from an outer mutation changing the program. Neither a large source edit nor a fluent hypothesis guarantees an improvement.

The table is invented to explain a decision, not measured Luna performance. Both policies must first be valid and evaluated comparably. B offers 0.01 more quality but takes four more numerical seconds. Neither dominates: A is faster and B has higher quality. A quality–time Pareto view therefore keeps both as options. If we explicitly choose a value of 0.01 quality units per second, maximizing utility U=S−0.01t gives A=2.39 and B=2.36. The price is a teaching assumption, not a measured API tariff or universal preference. A smaller price could reverse the decision.

Chapter 10.8 expresses the corresponding minimization form as cost-adjusted fitness. Cost may mean marginal API dollars or a declared resource measure, with a coefficient that converts units. Generation cost belongs to the path that produced a program; it is not an intrinsic property of source code. Avoid double-counting shared preparation and distinguish per-program evaluation time from all model calls and numerical effort spent finding it. Source length is not automatically a good proxy for either runtime or algorithm quality.

The implemented demo keeps quality primary and reports numerical effort and model usage separately. It does not apply the illustrative price, a complexity penalty or a Pareto archive. Three model calls, 35 seconds per call, eight seconds per trial and a 240-second run deadline bound work. An optional predeclared plateau stopping rule could save further requests; it is not the current automatic policy. The current run can continue its planned rounds after a plateau so students can inspect the mechanism.

No number of calls is universally optimal. Three calls per demonstration are a teaching budget: the first child, a proposal informed by its evaluation, and another chance to inspect adaptation or plateau. This budget is far smaller than the research-scale searches in the AlphaEvolve report. A flat or failed run remains useful evidence. Do not add artificial motion or repeated requests to force a desired trajectory.
:::
