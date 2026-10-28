# A language model as the mutation operator

## The language-model mutator {#llm-mutation data-seconds="45"}

::: {.question}
**What changes if the variation operator can read programs and measured feedback?**
:::

::: {.block}
A large language model reads selected programs, trial outcomes and allowed edits, then proposes a motivated mutation.
:::

::: {.block}
For example: retain a vector-relaxation stage, then append local search to improve the rounded assignment. The proposal is a hypothesis.
:::

::: {.answer}
**The LLM supplies context-conditioned variation. The harness still supplies fitness.** Its weights are not trained during this run.
:::

::: {.notes}
The model replaces one part of the evolutionary algorithm: the variation operator. It does not replace the artifact representation, objective, evaluator, selection rule or external population memory. Between calls, the controller changes the context; it does not update model weights. The same selected structure and failure record can make the next proposal more informed than an independent guess.

Chapter 10 connects context engineering to mutation and evaluation to fitness. FunSearch is a primary program-search example [@funsearch2024]. The classroom system uses a narrower interpreter over existing numerical kernels. Its proposals can change configurations and compositions but cannot invent arbitrary executable Python or modify the objective. Better proposals are possible, never guaranteed.
:::

## Signed Max-Cut {#problem data-seconds="45"}

::: {.question}
**How should vertices be partitioned when some edges prefer separation and others prefer agreement?**
:::

::: {.block .visual}
![Four-vertex illustration of signed edge preferences.](figures/signed-four-vertex.svg){width=65%}
:::

::: {.block}
Positive edge: prefer different sides. Negative edge: prefer the same side.

$$C_G(s)=\sum_{(i,j)\in E}w_{ij}\frac{1-s_i s_j}{2},\quad s_i\in\{-1,+1\}.$$
:::

::: {.answer}
**Maximize the original signed cut.** The comparison uses 1,000 vertices, 5,043 signed edges and reference 1098.
:::

::: {.notes}
A solution witness is one integer sign per vertex in original order. A crossing contributes its signed weight; an uncut edge contributes zero. Thus leaving a negative edge uncut avoids a penalty rather than earning an extra positive reward. Complementing every sign gives the same objective. The four-vertex picture is an illustration; the live comparison uses the supplied sparse random signed graph.

Both initialization experiments use the same 1,000-vertex graph, 5,043 edges and raw random assignments for seeds 3, 4 and 5. Its supplied reference is 1098. The separate dense stress case has 100 vertices, 4950 real-valued signed edges and reference 402.5209. It tests another numerical structure; fewer vertices and greater density do not imply a universal hardness ordering. Neither reference is a certified optimum. The earlier 100-vertex torus recordings are historical and remain preserved.
:::

## Local moves and feasible witnesses {#move data-seconds="40"}

::: {.question}
**Can the search move to a worse state while keeping a better result?**
:::

::: {.block}
Flip one sign, $s_i\leftarrow-s_i$, with exact gain

$$\Delta_i=s_i\sum_{j:(i,j)\in E}w_{ij}s_j.$$
:::

::: {.block}
The exploratory assignment may worsen. A separate best-so-far copy preserves the strongest valid witness seen during that execution.
:::

::: {.answer}
**Separate the moving state, best witness and strategy fitness.** Only a complete evaluation makes a strategy eligible for ranking.
:::

::: {.notes}
Only terms incident to the flipped vertex change; their differences sum to the stated gain. Cached gains make local moves inexpensive. Numerical methods can accept neutral or worsening moves to escape a basin while retaining the best feasible assignment separately.

This distinguishes three levels. The strategy is a program. Executing it produces a sign vector. The evaluator recomputes that vector's objective and summarizes three trials into strategy fitness. A witness from a censored trial may be valid even though the program is ineligible for complete-trial selection. A zero-cut partition is legal; a vector of zero-valued signs is not.
:::
