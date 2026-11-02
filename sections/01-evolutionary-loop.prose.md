# 10.1 The evolutionary loop

## Our strategy: evolve packing programs {#evolution data-seconds="60"}

::: {.question}
**How can we improve the method that finds the packings?**
:::

::: {.block}
Run several Python programs to produce packings. Check their circles and record their scores. Keep useful programs as **parents**.
:::

::: {.block .visual}
![Initialize once; evaluate, select and mutate repeatedly.](figures/evolutionary-cycle.svg){width=100%}
:::

::: {.answer}
**Luna writes changes to the parent programs.** We test each new program before deciding whether to keep it.
:::

::: {.notes}
We now have a problem and a score. Our proposed strategy improves the programs used to search for packings. Start with a few Python programs. Run them, check that their returned circles obey the rules, and record the sums of radii. The group of programs is the population. Programs chosen for further changes are parents. Luna writes a modified program, called a child. That change is mutation. Running and checking the child tells us whether to keep it, which is selection. Fitness means the measured performance used in that decision; later we define how our three test runs produce it.

Point through the diagram in order. Initialization happens once. Later rounds use selected programs and their results to propose changes. This is the Chapter 10.1 evolutionary loop: the next attempt builds on survivors rather than starting as an unrelated guess. The outside controller stores programs and measurements. Luna's model weights stay fixed, while the information sent in its next request changes. The checker supplies evidence beyond the model's explanation of its proposal.

A survivor is a program. Executing it produces a circle arrangement. Keeping a successful arrangement can also provide a numerical starting point for later programs, but that is separate from inheriting program source. Our default demonstration exposes both: program ancestry and a frozen bank of the previous best packings.
:::

## Five choices define the search {#framework data-seconds="60"}

::: {.question}
**What must we define before running this search?**
:::

::: {.block}
$(\mathcal A,f,\mu,\sigma,P_0)$: allowed programs, measured performance (**fitness**), how programs change (**mutation**), which programs we keep (**selection**), and the starting group (**initial population**).
:::

::: {.block}
$$P_{t+1}=\sigma\!\left(P_t\cup\{\mu(a):a\in\sigma(P_t)\}\right).$$

Choose parents → mutate → pool parents and children → select survivors.
:::

::: {.answer}
**New programs compete with the parents.** A worse new program does not have to replace a useful parent.
:::

::: {.notes}
This is Chapter 10, Definition 10.2 and Equation 10.1. The course minimizes fitness f. For our maximization problem, use negative median verified sum of radii. The artifact space consists of Python packing programs with a fixed function interface and bounded execution. Mutation is a Luna request containing actual selected parent source. Selection retains at most three complete programs. Checkboxes choose the initial population; they do not restrict the source changes Luna may propose.

The displayed recurrence is the chapter’s conceptual definition. Our controller sends up to three selected parents in one request and asks for one child, rather than making one request for every parent. It then evaluates that child and selects from parents plus child. This is a declared classroom choice, not a hidden implementation of every feature of AlphaEvolve. The chapter’s fixed fitness f corresponds directly to our fixed-start control. Default iterative refinement uses conditional fitness f(a | B_t), where the incoming packing bank is explicit evaluation state. Re-evaluating parents makes each round comparable; it does not make medians from different banks stationary program quality.
:::
