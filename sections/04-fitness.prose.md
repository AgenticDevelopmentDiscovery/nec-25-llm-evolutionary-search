# 10.4 Fitness design

## Packing score and program fitness {#fitness data-seconds="75"}

::: {.question}
**How do we turn packing scores into a program's fitness?**
:::

::: {.block}
**Packing score:** $S=\sum_i r_i$, after checking the geometry. A scorer that ignores overlap can reward invalid packings.
:::

::: {.block}
**Program fitness:** run three complete, valid trials with the same starting packings and numerical limits for every program.

$$F=\operatorname{median}(S_1,S_2,S_3).$$

Example scores $1.90,\ 2.10,\ 2.00$ give **$F=2.00$**.
:::

::: {.answer}
**The demo maximizes $F$.** Chapter 10 minimizes $f=-F$. Any invalid or incomplete trial makes the program ineligible.
:::

::: {.notes}
Chapter 10.4 treats the evaluator as the fitness function and warns that persistent optimization finds weaknesses in it. Here we explicitly compare a flawed scorer with the corrected evaluator, rather than merely presenting an invalid output. The flawed scorer returns the sum of radii and omits pair checks. It ranks two circles of radius 0.30 at centers (0.30, 0.50) and (0.70, 0.50) above two radius-0.25 circles at (0.25, 0.50) and (0.75, 0.50). The claimed gain is 0.10, but the first pair overlaps by 0.20. An optimizer rewarded by that flawed rule has an incentive to enlarge overlapping circles. The correct geometry checker rejects the apparent winner. These are instructor-made, numerically checked toy examples, not Luna outputs. The algorithm guide contains a revealable scorer illustration.

A production witness must contain exactly the required number of finite circle triples. Radii must be nonnegative, circles must fit inside the square, and every pair must avoid overlap. The server independently recomputes both geometry and summed radii; it ignores a program’s claimed score. Numerical tolerance is 1e-9 in unit-square units. A common radius-allocation construction margin of 1e-8 is applied before a final witness is returned and scored. No invalid output is silently repaired during evaluation.

Separate the two levels explicitly. One execution returns a packing. After independently checking its geometry, add its radii to obtain that trial's score $S_j$. A program receives three trials, using the same starting packings, trial seeds and numerical limits as its competitors. Its primary ranking value is $F=\operatorname{median}(S_1,S_2,S_3)$, which the demonstration maximizes and displays as a positive median. Sort the illustrative scores 1.90, 2.10 and 2.00 into 1.90, 2.00 and 2.10. The middle score is 2.00, so $F=2.00$. These numbers illustrate the calculation and are not measured demo results.

Chapter 10 uses a minimization convention. Its equivalent fitness is $f(a\mid B_t)=-F(a\mid B_t)=-\operatorname{median}_{j=1,2,3}S(a;z_{t,j})$, where $a$ is a program and $B_t$ contains the three starting packings $z_{t,j}$ frozen for this round. Thus the example has $f=-2.00$. A larger $F$ corresponds exactly to a smaller $f$. The server ranks by the positive median, then by the minimum trial score, then by stable program identity. It does not need to store the negative value to implement this ordering.

A failed trial is not quietly dropped when calculating fitness. Any invalid or incomplete trial makes the whole program ineligible for selection. A valid intermediate packing remains a separate useful construction. Comparisons use one frozen bank; medians from different banks do not measure program quality under the same conditions. This distinction is essential for anytime numerical search.

Feasibility checking does not establish algorithm transfer. Freeze program source before evaluating fresh numerical starts, exclude those validation results from mutation prompts and survivor decisions, and report them separately. The original runs used seeds 3, 4 and 5. A separate numerical-only check uses previously unused seeds 101, 102 and 103, common fixed starts, the same requested work and the same hard trial limit. The selection rule was fixed before seeing validation scores: compare the best initial program with the highest-ranked surviving new Luna program. The guide shows the actual results and source identities. This is a small post-search check, not a broad generalization study or a second live evolution.

Returning a fixed valid construction can be a legitimate solution to a fixed packing problem; a hard-coded layout alone is not proof of reward gaming. The loophole here is accepting infeasible geometry. Overfitting claims concern performance outside the observed starts or problem instances and require a separate evaluation contract. Multiobjective quality and cost are developed in the exploration frame and guide. The changing center positions define a nonconvex landscape; the fixed-center radius linear program does not solve that whole problem.
:::
