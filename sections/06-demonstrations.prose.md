# Two published circle-packing problems

## Demo 1: the 26-circle problem {#packing-26 data-seconds="45"}

::: {.question}
**What exactly makes a packing valid, and what does “better” mean?**
:::

::: {.block}
Place $N=26$ variable-radius circles in the unit square and maximize $\sum_i r_i$.

$$r_i\ge0,\quad r_i\le x_i,y_i\le1-r_i,\quad \|c_i-c_j\|_2\ge r_i+r_j.$$
:::

::: {.answer}
**These are AlphaEvolve’s published constraints and objective.** We search live with Luna; the paper’s reported construction is a separate research result.
:::

::: {.notes}
Appendix B.12 of the AlphaEvolve report gives this unit-square, sum-of-radii problem for 26 and 32 circles [@alphaevolve2025]. This is variable-radius packing; it is not equal-radius packing and not maximization of covered area. Tangency and zero radii are allowed under our stated contract; zero-radius count remains visible. The paper reports historical construction scores, not certificates of optimality, and they are not hidden inputs to our search.

Start the first demo with 26 selected in the instance control. Show the three initial Python programs in the guide: perturbed grid construction, greedy local center search, and simulated annealing of centers. The fixed-center radius allocator is common. The constructor intentionally spends less effort; compare actual numerical costs as well as quality. All programs in a round receive copies of the same packing bank for seeds 3, 4 and 5.
:::

## Demo 1: follow three mutations {#demo-circle-a data-seconds="210"}

::: {.question}
**Which part of the parent survives, and does the changed program earn its place?**
:::

::: {.block}
Evaluate the initial population → inspect parent source and context → send Luna round 1 → read the actual code diff and verified packing.
:::

::: {.block}
Repeat for rounds 2 and 3. Inspect inherited packing-bank IDs, complete trial scores, failures and survivor decisions.
:::

::: {.answer}
**Follow the real chain: source → execution → checked geometry → fitness → selection → next context.**
:::

::: {.notes}
Open the integrated demo from this frame. Select LIVE LLM, 26 circles, three calls, mutation, evidence-rich context and inherited packings. Check the selected initial programs and evaluate them. This starts numerical work only; every model call waits at an explicit gate.

At the first gate, point to the incoming packing bank: it contains the best valid construction found for each seed. Parents are re-evaluated from that bank before their scores enter the context. When sending a round, identify the actual provider request, public response and source string. Show who implemented the proposal: Luna wrote the Python; the isolated interpreter executes that exact admitted source. A live intermediate packing is independently verified, but it is not yet complete program fitness.

After evaluation, compare all three trials and the actual top-three decision. Before sending the next call, show that the latest results have entered the context and the packing bank has been updated. Keep failures or plateaus visible. Use the remaining teaching time for questions and inspection if computation finishes early; no artificial delay is inserted. A genuine recording may be used when needed, with a persistent RECORDED REPLAY label.
:::

## Read the first run’s evidence {#packing-evidence-a data-seconds="45"}

::: {.question}
**What improved: one packing, the program’s measured fitness, or both?**
:::

::: {.block}
A witness proves one feasible construction. Three complete trials rank a program on one declared bank. A source diff explains what changed; it does not prove an improvement.
:::

::: {.answer}
**Keep construction progress and program comparison separate.** Report the actual outcome, calls and numerical effort.
:::

::: {.notes}
Ask students to point to the record supporting each claim. The circle view includes program identity, seed, validity and summed radii. The table includes complete or failed trials, medians and current-bank selection. The cumulative construction curve retains valid witnesses; it must not be mislabeled as a fixed-protocol program-fitness curve when banks change.

Do not substitute expected improvements for measured outcomes. If an eligible child is worse than the champion, it can still enter another slot. If a trial fails, the program has no eligible median. Matching a historical literature score would still not prove optimality. A three-call classroom run cannot establish broad model or algorithm superiority. The guide’s separate numerical validation illustrates how to test frozen programs beyond the evolution starts, rather than treating geometric feasibility as proof of transfer.
:::

## Demo 2: the 32-circle problem {#packing-32 data-seconds="45"}

::: {.question}
**Does the same program-evolution mechanism still work when the number of circles changes?**
:::

::: {.block}
Use $N=32$, the second unit-square case in AlphaEvolve Appendix B.12. Keep the objective, checker, trial seeds, source interface and numerical limits declared.
:::

::: {.answer}
**Change the problem instance, then inspect adaptation.** A higher raw sum for 32 circles is not evidence of a better algorithm than the 26-circle run.
:::

::: {.notes}
Reset and select 32 circles. The problem fingerprint changes, as do the number of wall and pair constraints. The method signatures accept n=len(initial), so a program must not assume 26 rows. This is a second published mathematical problem, not an arbitrary graph substitution. Its score scale is different; do not compare raw sums between the two circle counts as though they measured the same instance.

Use the same three disclosed initial methods and seeds so students can recognize the mechanism, but do not call this a controlled test of generalization. The programs are evolved with access to each task. The point is to observe the same Chapter 10 components operating on a changed instance. A separate withheld-size evaluation would be required for a transfer claim. A separate fixed-start check of already-frozen programs is now available in the algorithm guide. It used new seeds 101–103, zero additional model calls and no feedback into evolution. The initial baseline and a surviving new program were selected before inspecting those results. This small check concerns fresh starts at the same N; it is not an unseen-size transfer study.
:::

## Demo 2: inspect adaptation and limits {#demo-circle-b data-seconds="210"}

::: {.question}
**Does Luna change its search after seeing the 32-circle trial evidence?**
:::

::: {.block}
Evaluate 32-circle parents → send three gated requests → inspect actual source edits, verified packings and the feedback entering each next request.
:::

::: {.block}
Keep invalid proposals, incomplete executions and repeated ideas visible. Stop cancels owned work; replay remains explicitly recorded.
:::

::: {.answer}
**The mechanism is testable even when improvement is absent.** Evidence decides which proposed programs survive.
:::

::: {.notes}
Follow the same procedure as demo one. Make the changed n visible in the request context and in the circle count of returned witnesses. A response that hard-codes the wrong number is invalid; the interpreter does not silently fix it. A source syntax error, duplicate, invalid packing or hard timeout remains part of the outcome and does not trigger an unannounced free retry.

The class should see the proposal arrive, the function execute and the resulting geometry checked. Compare the child with parents evaluated from the same incoming packing bank. Inspect the actual next request rather than asserting that the model learned. Its weights remain unchanged; its context contains the search memory. If a recorded run is used, show its source identity and recorded timing, while making clear that no new request is being made.
:::

## Name the framework we observed {#packing-evidence-b data-seconds="45"}

::: {.question}
**Can you identify every Chapter 10 component in the live record?**
:::

::: {.block}
$\mathcal A$: Python packing programs. $f$: verified current-bank trial fitness. $\mu$: Luna’s code mutation. $\sigma$: complete-program selection. $P_0$: checked initial programs.
:::

::: {.answer}
**Context proposes; external evaluation measures; selection preserves.** For your research problem, define these five choices before spending search budget.
:::

::: {.notes}
Return to the tuple after both demos so its components are now concrete. Students should distinguish the evolving program, the numerical packing returned by execution, and fitness used to select programs. They should also be able to explain ancestry, inherited numerical starts, context feedback and evaluator independence.

Chapter 10 supplies the conceptual structure. AlphaEvolve supplies the two published problem formulations and a real precedent for evolving search programs. Our bounded implementation supplies inspectable classroom evidence. The mathematical task matches the paper; the original engine, model ensemble, compute scale and reported optimized constructions are not reproduced. Those limits matter when explaining what the demonstration establishes.
:::
