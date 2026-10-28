# Evolutionary optimization

## Evolutionary search with a language-model mutator {#title .title-frame data-seconds="20"}

::: {.question .title-only}
**Evolving solver programs through measured feedback**

ENGR 689 · Texas A&M University · Fall 2026

:::

## Optimization as search {#optimization data-seconds="40"}

::: {.question}
**When the best candidate is unknown, what can we do?**
:::

::: {.block}
Define a candidate space $\mathcal A$ and a measurable objective $F$. Seek

$$a^*\in\arg\max_{a\in\mathcal A}F(a).$$
:::

::: {.block}
Generate candidates → measure them → spend the next trial where the evidence suggests it may help.
:::

::: {.answer}
**Optimization is an evidence-guided search.** An evolutionary algorithm adds a population, inherited variation and selection.
:::

::: {.notes}
The candidate may be a parameter vector, a program or a design. An optimizer does not need to enumerate the whole space, but it needs an operational definition of quality. A candidate that sounds plausible is not a measured result. Our objective can be computed automatically, which lets repeated search use the same external check.

Begin with evolutionary computation itself. Language models are introduced later as one possible variation mechanism. This ordering separates the optimization framework from the technology used to propose a change. It also makes a numerical-only baseline meaningful: the framework does not require a language model to define or evaluate a candidate.
:::

## Population and fitness {#population data-seconds="40"}

::: {.question}
**Why keep several candidates instead of only the current champion?**
:::

::: {.block}
Fitness measures how well a candidate performs now. A different candidate may offer changes that the champion's structure does not readily suggest.
:::

::: {.block}
Hypothetical example, equal mutation budgets:

A: current fitness **7** → best tested child **8**.\
B: current fitness **6** → best tested child **9**.
:::

::: {.answer}
**Keep promising alternatives because a lower-scoring parent can lead to a better descendant.** Multiple parents preserve several paths for future search.
:::

::: {.notes}
Pause after the question and let students argue for keeping only the champion: it has the highest measured fitness, so why spend effort elsewhere? The missing information is how good the candidates' descendants could be. Current fitness evaluates a candidate under a declared protocol; it does not evaluate every possible mutation of that candidate or of its competitors.

The numbers are a hypothetical maximization example, not Max-Cut measurements or predictions. Suppose A and B have different structures, and we give each the same mutation and evaluation budget. A currently scores 7 and its best tested child scores 8; B currently scores 6 and its best tested child scores 9. Keeping only A would discard B as a direct starting point before discovering that child. B's lower current score therefore does not make it useless for future search. The mechanism is that inherited structure affects which changes are available or likely under the variation operator. A search from A might eventually rediscover B's structure; retaining B keeps that route directly available.

A population reduces dependence on descendants of a single parent, but it costs evaluations and does not guarantee improvement. Several nearly identical programs may offer little useful variety. The benefit depends on their behavioral differences, the variation operator, selection and the available budget. This example motivates retaining promising alternatives; it does not justify retaining every weak candidate.

In the classroom controller the population contains solver programs, with a cap of three complete evaluated survivors and deterministic fitness ranking. Up to three survivors enter Luna's context as potential parents; a later execution of a solver produces a separate solution witness. There is no reserved diversity slot, island migration or tournament sampling. The controller preserves highly ranked alternatives when available, but it does not explicitly enforce structural or behavioral diversity, and a potentially useful lower-ranked program can still be discarded.
:::

## Variation, evaluation and selection {#evolution data-seconds="45"}

::: {.question}
**What turns repeated candidate generation into an evolutionary algorithm?**
:::

::: {.block .visual}
![Seed once; derive children from survivors; evaluate and select again.](figures/evolutionary-cycle.svg){width=100%}
:::

::: {.block}
Mutation can perturb a parameter, replace a component or compose stages. Selection compares parents and children using the same fitness protocol.
:::

::: {.answer}
**Useful structure is inherited, varied and tested.** Elitism retains measured parents when a mutation is worse.
:::

::: {.notes}
A classical variation operator can make random parameter edits, replace a subtree in a program or combine material from parents. Variation does not have to improve fitness. The evaluator supplies evidence and selection decides which structures remain. Carrying parents into the enlarged pool prevents an unsuccessful child from automatically erasing the incumbent.

Chapter 10 distinguishes initial generation from survivor-conditioned mutation. Its recurrence selects parents, generates variants, pools parents and children, then selects again. Here the controller retains prior measured scores, so elitism protects the observed leaderboard under the fixed protocol. That is not a theorem about expected quality on new trials or eventual global convergence.
:::

## Exploration and exploitation {#exploration data-seconds="40"}

::: {.question}
**Should the next mutation refine a strong candidate or try a different mechanism?**
:::

::: {.block}
**Exploit:** adjust a promising parameter or refine an existing composition. **Explore:** replace a stage or try another algorithm family.
:::

::: {.block}
Too little variation can collapse the population. Too much unconstrained variation can waste evaluations on poor candidates.
:::

::: {.answer}
**Variation and selection must balance inheritance with discovery.** Better starting material may help; a weak start does not imply permanent failure.
:::

::: {.notes}
The search neighborhood is defined by the representation and mutation rules. An operator limited to small parameter changes explores a different neighborhood from one allowed to replace a kernel. Strong selection can remove useful alternatives; weak selection can spend resources on low-quality programs. The controller exposes complete-trial ranking and exact-duplicate rejection but does not implement a general diversity guarantee.

The distinction matters for the initialization experiment. Checkboxes choose the initial population only. They do not remove unchecked kernels from the artifact space. A language-model mutator may therefore recover a useful algorithm absent from the initial suite. Claiming that a poor suite can never reach the reference would contradict that permitted search space.
:::
