# 10.4 Fitness design

## Feasibility comes before fitness {#fitness data-seconds="75"}

::: {.question}
**Could a flawed scorer reward an invalid packing?**
:::

::: {.block}
**Flawed scorer:** sum radii without checking overlap. A valid pair scores **0.50**; an overlapping pair scores **0.60** and incorrectly wins.
:::

::: {.block}
**Corrected evaluator:** check every wall and pair, then score. Reject invalid or incomplete trials.

$$f(a\mid B_t)=-\operatorname{median}_{j=1,2,3}S(a;z_{t,j}).$$

Compare programs within one frozen packing bank $B_t$.
:::

::: {.answer}
**Close the scoring loophole; then test frozen programs on unseen starts.** Feasibility and transfer are separate checks.
:::

::: {.notes}
Chapter 10.4 treats the evaluator as the fitness function and warns that persistent optimization finds weaknesses in it. Here we explicitly compare a flawed scorer with the corrected evaluator, rather than merely presenting an invalid output. The flawed scorer returns the sum of radii and omits pair checks. It ranks two circles of radius 0.30 at centers (0.30, 0.50) and (0.70, 0.50) above two radius-0.25 circles at (0.25, 0.50) and (0.75, 0.50). The claimed gain is 0.10, but the first pair overlaps by 0.20. An optimizer rewarded by that flawed rule has an incentive to enlarge overlapping circles. The correct geometry checker rejects the apparent winner. These are instructor-made, numerically checked toy examples, not Luna outputs. The algorithm guide contains a revealable scorer illustration.

A production witness must contain exactly the required number of finite circle triples. Radii must be nonnegative, circles must fit inside the square, and every pair must avoid overlap. The server independently recomputes both geometry and summed radii; it ignores a program’s claimed score. Numerical tolerance is 1e-9 in unit-square units. A common radius-allocation construction margin of 1e-8 is applied before a final witness is returned and scored. No invalid output is silently repaired during evaluation.

Fitness is the negative median quality of three complete trials on the same bank. A failed trial is not quietly dropped from the average; it makes the program ineligible for selection. A valid intermediate packing is still a separate useful construction. This distinction is essential for anytime numerical search.

Feasibility checking does not establish algorithm transfer. Freeze program source before evaluating fresh numerical starts, exclude those validation results from mutation prompts and survivor decisions, and report them separately. The original runs used seeds 3, 4 and 5. A separate numerical-only check uses previously unused seeds 101, 102 and 103, common fixed starts, the same requested work and the same hard trial limit. The selection rule was fixed before seeing validation scores: compare the best initial program with the highest-ranked surviving new Luna program. The guide shows the actual results and source identities. This is a small post-search check, not a broad generalization study or a second live evolution.

Returning a fixed valid construction can be a legitimate solution to a fixed packing problem; a hard-coded layout alone is not proof of reward gaming. The loophole here is accepting infeasible geometry. Overfitting claims concern performance outside the observed starts or problem instances and require a separate evaluation contract. Multiobjective quality and cost are developed in the exploration frame and guide. The changing center positions define a nonconvex landscape; the fixed-center radius linear program does not solve that whole problem.
:::
