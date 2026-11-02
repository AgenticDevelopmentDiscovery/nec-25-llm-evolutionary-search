# 10.2 Mutation operators

## Classical variation {#classical-mutation data-seconds="60"}

::: {.question}
**How can we change the packing program's code?**
:::

::: {.block}
**Point mutation:** edit one constant, such as $0.04\rightarrow0.02$ for smaller center moves. **Subtree replacement:** replace the condition that decides whether to keep a proposed center move.
:::

::: {.block}
**Crossover:** combine code from two parents, such as one program's starting construction with another's move acceptance rule.
:::

::: {.answer}
**These edits change the program, not just one packing.** Evaluate the resulting program with the same three-trial protocol before selecting it.
:::

::: {.notes}
Recall the earlier numerical-search frame before introducing these operators. It showed one unchanged program proposing center moves, allocating radii, and applying a move acceptance rule. We now edit the code defining those operations. Chapter 10.2.1 introduces point mutation, subtree mutation and crossover using expression trees. An expression tree represents an expression as nested operations and values. A subtree is one complete nested part, such as the condition in an if statement.

A point mutation can change the coefficient controlling random center movements from 0.04 to 0.02. The actual program also decreases its scale with the step index, so this is an edit to the schedule's coefficient, not a promise that every move has length 0.02. A subtree replacement can replace the strict-improvement condition with another compatible Boolean condition. A different acceptance rule might permit occasional score decreases while preserving valid geometry. Crossover can combine compatible source components from two parents. These examples translate the classical vocabulary to packing programs; the controller does not implement a hidden classical genetic-programming engine.

Such edits are hypotheses about a better method. Smaller moves may refine an arrangement but explore less widely. Accepting some temporary losses may help exploration but can also waste work. Run each changed program using the same three starting conditions and limits as its competitors, then compare complete valid trial scores. Inner move acceptance decides which center positions a program keeps; outer evolutionary selection decides which programs survive. The next frame introduces Luna as the source-code mutator used in the demonstration.
:::

## A language model writes the mutation {#llm-mutation data-seconds="60"}

::: {.question}
**What can a mutator change when it reads the parent code and its results?**
:::

::: {.block}
1. Retain the parent’s center search and radius allocator.
2. Change center-move size, which centers move, or the move acceptance rule.
:::

::: {.block}
3. Luna returns edited **Python source** and a hypothesis.
4. An isolated interpreter executes it; an independent checker evaluates the returned circles.
:::

::: {.answer}
**Luna implements the proposed code change; Python executes it.** A reasoned edit becomes evidence only after evaluation.
:::

::: {.notes}
Chapter 10.2.2 replaces blind variation with knowledge-guided variation. For example, a parent may perturb one center at a time and stop improving. The mutator can hypothesize that coordinated moves or a restart schedule will escape that basin. It writes the new function; the local Python interpreter does not translate the prose hypothesis into an algorithm.

Our response contains round_id, parent_ids, hypothesis and source. The source defines solve(initial, seed, steps). NumPy, math, a fixed-center radius allocator and a progress reporter are supplied. A source diff exposes what was retained and changed. The geometry checker and survivor rule are outside the editable source. Bubblewrap isolates generated code from credentials, private repository files and the host network. The model has no execution tools during its proposal call.

AlphaEvolve evolves code and evaluates it externally [@alphaevolve2025]. We use the published circle-packing tasks with our own small controller and TAMU Luna. The public results repository does not release the original discovery engine. Do not describe our initial numerical methods as the algorithms AlphaEvolve discovered.
:::

## Context joins the two course spines {#context data-seconds="60"}

::: {.question}
**Which evidence should the next mutation see?**
:::

::: {.block}
Parent source **and scores**; successful and failed attempts; task constraints and useful domain knowledge; population similarity and remaining budget.
:::

::: {.block}
**Evaluation becomes fitness. Context engineering drives mutation.** The next request carries the previous round’s actual results.
:::

::: {.answer}
**External memory makes the next proposal informed.** A plausible explanation does not replace a measured trial.
:::

::: {.notes}
These are the four context ingredients in Chapter 10.2.3 and the convergence of the two spines in Figure 10.2. Our domain knowledge includes the nonoverlap constraints and the fact that radius allocation is a linear program once centers are fixed. Source, scores, failures and tried IDs expose what the search already knows. The context labels the current packing bank, so scores from different starting conditions are not silently mixed.

The server’s request panel shows the actual provider payload; the response panel shows the public stream. Authorization is added separately inside the model worker. Hidden reasoning is neither requested as teaching evidence nor displayed. Numerical seeds control starting packings and numerical moves. They do not determine Luna’s wording. The optional structure-only control withholds scores and history, but a rigorous context comparison must additionally freeze identical parent programs and histories across the two conditions.
:::
