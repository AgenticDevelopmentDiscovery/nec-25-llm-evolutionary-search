# 10.1 The evolutionary loop

## An external evolutionary loop {#evolution data-seconds="60"}

::: {.question}
**What must survive between calls for the next attempt to build on the previous one?**
:::

::: {.block}
Keep executable candidates, their measured results, and the changes already tried. Select survivors before proposing their descendants.
:::

::: {.block .visual}
![Initialize once; evaluate, select and mutate repeatedly.](figures/evolutionary-cycle.svg){width=100%}
:::

::: {.answer}
**Evolution gives the next proposal ancestry and external memory.** Repeated independent generation does not inherit the survivors.
:::

::: {.notes}
Chapter 10.1 distinguishes an evolutionary loop from the generate–evaluate–select loop of Chapter 9: mutation consumes the survivors. Initialization happens once. Later rounds preserve an artifact and vary its structure instead of asking for an unrelated answer every time. The outside controller stores programs and measurements; this memory persists even though the language model’s weights stay fixed. An external evaluator supplies evidence beyond a model’s verbal self-assessment.

A survivor is a program. Executing it produces a circle arrangement. Keeping a successful arrangement can also provide a numerical starting point for later programs, but that is separate from inheriting program source. Our default demonstration exposes both: program ancestry and a frozen bank of the previous best packings.
:::

## Five choices define the search {#framework data-seconds="60"}

::: {.question}
**Which choices turn “try to improve this” into a reproducible procedure?**
:::

::: {.block}
$(\mathcal A,f,\mu,\sigma,P_0)$: program space, fitness, mutation, selection, and initial population.
:::

::: {.block}
$$P_{t+1}=\sigma\!\left(P_t\cup\{\mu(a):a\in\sigma(P_t)\}\right).$$

Choose parents → mutate → pool parents and children → select survivors.
:::

::: {.answer}
**The inner selection chooses parents; the outer selection forms the next generation.** Every component is a design choice.
:::

::: {.notes}
This is Chapter 10, Definition 10.2 and Equation 10.1. The course minimizes fitness f. For our maximization problem, use negative median verified sum of radii. The artifact space consists of Python packing programs with a fixed function interface and bounded execution. Mutation is a Luna request containing actual selected parent source. Selection retains at most three complete programs. Checkboxes choose the initial population; they do not restrict the source changes Luna may propose.

The displayed recurrence is the chapter’s conceptual definition. Our controller sends up to three selected parents in one request and asks for one child, rather than making one request for every parent. It then evaluates that child and selects from parents plus child. This is a declared classroom choice, not a hidden implementation of every feature of AlphaEvolve. The chapter’s fixed fitness f corresponds directly to our fixed-start control. Default iterative refinement uses conditional fitness f(a | B_t), where the incoming packing bank is explicit evaluation state. Re-evaluating parents makes each round comparable; it does not make medians from different banks stationary program quality.
:::
