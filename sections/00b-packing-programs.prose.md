# How we run and compare packing programs

## How a packing program searches {#packing-search data-seconds="65"}

::: {.question}
**What does a program do to improve one packing?**
:::

::: {.block}
Example: **Greedy Local Center Search**. Start with circle centers. **Radius allocation** chooses radii for those fixed centers to maximize their sum while satisfying the packing rules.
:::

::: {.block}
Propose a random change to one center. The **move scale** controls the typical size of that change.
:::

::: {.block}
Recalculate radii and score. The **move acceptance rule** keeps the proposed change only if the score increases. This cycle is one **search step**.
:::

::: {.answer}
**Repeat the steps, then return the best packing found.** This loop changes a packing. Later, we will change the program itself.
:::

::: {.notes}
Explain the numerical method before discussing edits to its code. This frame describes the disclosed Greedy Local Center Search program. It starts with the supplied centers. The helper radii(centers) solves a linear program for the radii: the centers and their pairwise distances are fixed, the radii are the unknowns, and every wall and pair imposes a linear bound. The helper maximizes the sum of radii under those bounds with the common numerical safety margin. Choosing good center positions remains the search problem.

One search step copies the centers, randomly chooses one circle and proposes random changes to its x and y coordinates. The move scale is the standard deviation of each coordinate change before clipping centers to their allowed coordinate range. It controls typical displacement, not a fixed step length or a maximum distance. The implemented scale decreases during a run: scale = 0.04 × (1 − k/steps) + 0.002. Here k is the step index. The coefficient 0.04 controls the larger early movements and the added 0.002 keeps a small positive scale. Changing that coefficient to 0.02 reduces typical movement at the same step; it does not make every displacement exactly 0.02.

The program reallocates radii after the proposed center move and computes the new sum. Its move acceptance rule is a condition in an if statement. If the current sum is 2.00 and the proposed sum is 2.03, the greedy program keeps the proposed centers. If the proposed sum is 1.98, it keeps the previous centers. These numbers are teaching examples. The separate Simulated Annealing of Centers program can accept a temporary score decrease with a controlled probability and retains its best packing separately. That is a different move acceptance rule, not permission to accept overlapping geometry.

The program repeats numerical steps until it returns or its execution is stopped by a limit. We call one execution of the whole program a trial in the next frame. Keep the levels distinct: a center move changes an arrangement inside a program; a later mutation changes the program's source; evolutionary selection compares whole programs after evaluation.
:::

## What is a trial? {#packing-trials data-seconds="55"}

::: {.question}
**What do Trial 1, Trial 2 and Trial 3 mean?**
:::

::: {.block}
A **trial** is one execution of an unchanged program from given centers. It may contain many search steps. Limits: **80 requested steps**, **8 seconds maximum**.
:::

::: {.block}
A **random seed** is a number that initializes the program's random choices. Our defaults are:

| Trial | 1 | 2 | 3 |
|:--|--:|--:|--:|
| Random seed | 3 | 4 | 5 |
:::

::: {.answer}
**Use the same three starting packings and seeds for every program.** This shared set of starting packings is the **packing bank**.
:::

::: {.notes}
A trial is one call to solve(initial, seed, steps), executed in an isolated Python worker. The source stays unchanged during that execution. It receives a copy of one specified set of starting centers, one numerical random seed, and the requested step count. The program can make many proposed center moves before returning one final arrangement. A checked intermediate arrangement is progress within the trial, not another completed trial.

The controller evaluates a program three times. With the default first seed of 3, Trial 1 uses seed 3, Trial 2 uses seed 4, and Trial 3 uses seed 5. These numbers are ordinary defaults, not special mathematical conditions. A random seed initializes a pseudo-random number generator, making its generated sequence repeatable for the same program and inputs. A changed program may consume random numbers differently, so equal seeds do not force two programs to make identical moves. Hard time limits and numerical execution conditions can also affect reproducibility. Numerical seeds do not control Luna's wording.

The three trials use three specified starting packings. Every competing program receives copies of the same bank, with the corresponding seed and limits. Eight seconds is a hard wall-time cap including worker startup; 80 is a requested number of search steps. A constructor may finish with fewer steps, and generated source may use the work request differently. Equal limits do not imply equal numerical effort. A timeout is an incomplete trial, not a successfully completed eight-second score.

In the default refinement protocol, the bank for the next round comes from the best previous packing for each seed. Freeze those centers, re-evaluate parents and the new program from copies of that bank, and compare only their current-bank scores. The fixed-start option instead keeps the original bank. The next frame explains fitness: all three trials must complete and be valid, then their middle score ranks the program. One trial is a numerical execution, a model call proposes source code, and an evolutionary round coordinates proposal, evaluation and selection. They are different units of work.
:::
