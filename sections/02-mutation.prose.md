# 10.2 Mutation operators

## Classical variation {#classical-mutation data-seconds="60"}

::: {.question}
**How can we vary a program without understanding why it works?**
:::

::: {.block}
**Point mutation:** change a move scale, for example $0.04\rightarrow0.02$. **Subtree replacement:** replace an acceptance expression. **Crossover:** inherit code from two parents.
:::

::: {.block}
These edits create hypotheses. The evaluator determines whether each resulting program still runs and improves its measured fitness.
:::

::: {.answer}
**Classical variation changes structure; selection supplies direction.** Small source edits can have large behavioral effects.
:::

::: {.notes}
Chapter 10.2.1 introduces point mutation, subtree mutation and crossover using expression trees. Translate that vocabulary to the code students will see. A literal change is a point edit. Replacing an acceptance rule changes a component of the computation. Combining one parent’s constructor with another parent’s search schedule is inheritance from multiple programs. These are conceptual examples, not claims that our controller implements a classical genetic-programming engine.

A move scale controls the distance of a proposed center displacement. Changing it does not by itself say whether a program is better. A smaller scale can help refine a packing but may impede escape from a basin. The complete program must be run and checked under the same trial conditions. This sets up the difference between blind variation and a mutator that reads numerical feedback.
:::

## A language model writes the mutation {#llm-mutation data-seconds="60"}

::: {.question}
**What can a mutator change when it reads the parent code and its results?**
:::

::: {.block}
1. Retain the parent’s center search and radius allocator.
2. Propose a different move scale, center subset, or acceptance schedule.
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
