# A language model as the mutation operator

## The language-model mutator {#llm-mutation data-seconds="45"}

::: {.question}
**What changes if the variation operator can read programs and measured feedback?**
:::

::: {.block}
1. **Retain vector optimization:** adjust one vector per vertex to improve a continuous cut objective.
2. **Round:** convert the optimized vectors into a two-group partition.
:::

::: {.block}
3. **Luna proposes an extension:** append local search, starting from that partition.
4. **Evaluate the child:** compare it with the parent using identical trials and the same total time limit per trial.
:::

::: {.answer}
**The child inherits vector optimization and adds local search.** Whether the extension helps is a hypothesis tested by numerical evaluation.
:::

::: {.notes}
Present the numbered example as a hypothetical mutation, not a claim about a particular recorded Luna response. The candidate being changed is a solver program. Its execution produces a partition, which the evaluator uses to measure the program's quality.

Step 1 retains the parent's vector method. Instead of immediately choosing one of two groups for each vertex, the Burer–Monteiro method optimizes continuously adjustable vectors using an objective related to the cut value. Our implementation uses two-dimensional unit vectors. This is a numerical search over a continuous surrogate; it does not certify the global Max-Cut optimum.

Step 2 rounds the vectors into a feasible partition. A direction through the vector space determines which side each vector falls on, assigning each graph vertex to one of two groups. Vector optimization and rounding are internal operations of the existing Burer–Monteiro kernel, not two independently editable strategy stages.

Step 3 is the proposed program mutation. Luna reads selected parent programs, measured trial results and the allowed edits, then may propose appending a trusted local-search kernel. That kernel receives the partition produced by the first stage and explores changes such as moving vertices between groups. The parent recipe is vector optimization followed by rounding. The child recipe retains both operations and adds local search. The numerical kernels execute these operations after the proposal has passed validation.

Step 4 tests the complete child program against the parent under the declared evaluation protocol: the same graph, seeds, raw starting partitions and numerical limits. Each program has the same total time allowance per trial; the child shares its allowance across its stages. Appending local search does not grant extra evaluation time. The evaluator independently rescores the original graph and aggregates complete trials into fitness. The added stage might help, offer no improvement, or reduce performance within the fixed allowance. The proposal is a hypothesis because those outcomes must be measured rather than inferred from a plausible explanation.

The model replaces one part of the evolutionary algorithm: the variation operator. It does not replace the artifact representation, objective, evaluator, selection rule or external population memory. Between calls, the controller changes the context; it does not update model weights. The same selected structure and failure record can make the next proposal more informed than an independent guess.

Chapter 10 connects context engineering to mutation and evaluation to fitness. FunSearch is a primary program-search example [@funsearch2024]. The classroom system uses a narrower interpreter over existing numerical kernels. Its proposals can change configurations and compositions but cannot invent arbitrary executable Python or modify the objective. Better proposals are possible, never guaranteed.
:::

## Signed Max-Cut {#problem data-seconds="45"}

::: {.question}
**Can every edge preference be satisfied at once?**
:::

::: {.block}
Illustrative triangle: **A–B = +3; A–C = −2; B–C = −2.**

Positive weights reward separation. Negative weights penalize separation.
:::

::: {.block}
| Partition | Crossing contributions | Cut value |
|:--|:--|--:|
| A, B, C together | None | 0 |
| A alone; B with C | $+3-2$ | **1** |
| C alone; A with B | $-2-2$ | −4 |
:::

::: {.answer}
**Edge preferences can conflict. Maximize their total crossing weight.** Separating A and B forces at least one negative edge to cross.
:::

::: {.notes}
The purpose of this frame is to establish a conflict that requires a global tradeoff before introducing the objective's notation. This three-vertex triangle is a hypothetical teaching example, not an instance measurement from the live demonstration. There is an edge between every pair: A–B has weight +3, and A–C and B–C each have weight −2. A partition assigns every vertex to one of two groups; a group may be empty.

Show the question, pause, and invite students to try satisfying all three preferences. The positive edge asks for A and B to be separated. Both negative edges ask for C to remain with their respective endpoints. C cannot be in the same group as both A and B while those two vertices are separated. Individual edge preferences therefore cannot all be satisfied at once.

Reveal the table and compute each row aloud. Keeping all three vertices together cuts no edges, giving 0. Separating A while keeping B and C together cuts A–B and A–C: +3 minus 2 equals 1. Separating C while keeping A and B together cuts both negative edges: −2 minus 2 equals −4. Separating B gives the symmetric score 1. Together with exchanging the two group names, these exhaust the possible partitions, so 1 is the optimum for this small illustrative triangle. That direct enumeration does not certify either live benchmark's reference value.

Conclude: a solver must account for the whole graph because a single vertex's placement affects several edges. A crossing contributes its signed weight; an uncut edge contributes zero. Keeping a negative edge uncut avoids a penalty rather than earning an extra positive reward. Maximizing the total crossing weight balances the incompatible preferences.

For the formal definition, encode the two group memberships by $s_i\in\{-1,+1\}$. Equal labels have product $s_i s_j=1$, so the crossing indicator $(1-s_i s_j)/2$ is 0. Opposite labels have product −1, so the indicator is 1. Thus

$$C_G(s)=\sum_{(i,j)\in E}w_{ij}\frac{1-s_i s_j}{2},\qquad \max_{s\in\{-1,+1\}^{|V|}}C_G(s).$$

Complementing every sign exchanges the group names without changing the cut value. The demonstration evaluates each solver's returned partition by independently summing the original graph's edge contributions. This gives external numerical feedback for evolving solver programs. Graph size, trial conditions and unproven reference values are introduced with the experiment setup, after students understand what a score means.
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
