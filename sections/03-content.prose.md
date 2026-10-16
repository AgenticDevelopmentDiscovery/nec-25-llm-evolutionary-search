# Content

## How it works

The core idea is simple: treat the LLM as a learned mutation operator instead of a random one. A generation starts with a parent set, often the best-scoring candidates or examples from a diversity-preserving archive. The mutation prompt shows the parent program, the score, and a request to produce a candidate that improves the score. The evaluator then runs the new program and returns a numerical fitness value. Selection keeps the best candidates or preserves a diversity sketch in an archive, and the next generation begins again.

## Using it: the basic case

A good classroom walkthrough is a small symbolic-regression loop. The LLM proposes equations as code, the C2 harness scores them on held-out error plus a complexity penalty, and the search returns the best formula for several generations. A minimal script can run the loop in a few lines: generate candidates, evaluate them, sort by score, choose parents, prompt the LLM for a targeted improvement, and repeat. The live demo should show the best-fitness curve rising over roughly five generations and then finish by showing a gameable candidate that overfits a visible dataset.

## Using it: going further

Once the basic loop is stable, the search can be made more robust by preserving diversity instead of collapsing to a single high-scoring lineage. Islands, MAP-Elites, novelty archives, or a fixed-size elite pool all keep the population from becoming one narrow mutation chain. The key idea is that diversity in the parent set gives the LLM more ways to explore physically plausible or semantically distinct programs, improving the odds that the search crosses a region of the objective landscape that a single chain would miss.

## Designing the fitness function

The fitness function is the selective pressure. It should combine the actual objective with useful constraints, such as complexity, interpretability, or runtime. In the symbolic-regression example, fitness should reward held-out predictive accuracy and penalize complexity, because a pure training-error score encourages equations that memorize the visible data. The same discipline carries to other domains: a fitness function that measures exactly what you want the agent to optimize is a design decision, not an implementation detail.

## Pitfalls

The most important failure mode is eval hacking, where candidates improve their score by exploiting the scorer rather than solving the task. A model may special-case the visible data, inject a threshold that bypasses the real objective, or depend on a benchmark artifact. The symptom is a rising score curve with no corresponding improvement in held-out or out-of-domain checks. The remedy is to keep a separate validation or held-out evaluation, require transparent constraints, and inspect whether the scorer is rewarding the right behavior rather than a shortcut.
