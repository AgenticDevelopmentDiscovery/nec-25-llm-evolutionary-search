# Topic

## In one sentence

LLM-driven evolutionary search uses language models as smart mutation operators inside a generate → evaluate → select loop to evolve programs under a carefully designed fitness function.

## What it is

LLM-driven evolutionary search keeps the evolutionary skeleton of a population or archive of candidate programs, but replaces the random mutation and crossover operator of classic genetic programming with a language model. The language model reads one or more high-scoring parent programs and proposes a revised program that is more likely to improve the score than a random subtree edit. In practice, the loop is generate → evaluate → select → mutate, and the mutation prompt carries parent code, scores, and constraints that guide the model toward a better candidate. A strong fitness function is the selective pressure; if it rewards the wrong things the search can optimize artifacts of the evaluator rather than the intended objective.

## Why it belongs in this course

This topic belongs in the course because it fuses the course’s central agentic development threads: generation, evaluation, orchestration, and sandboxed code execution. It is the clearest case in which an evaluation harness is not a side tool but the engine of selection. Students can see that the search loop depends on both the agentic model and the measurement design, and that a weak or gameable fitness function can produce plausible-looking but untrustworthy solutions.

## What the reader will be able to do

- Design a minimal generate → evaluate → select → mutate loop using an LLM as a mutation operator.
- Explain how fitness design, diversity maintenance, and held-out checks shape an evolutionary search.
- Distinguish LLM-guided search from random genetic programming and identify when evaluation hacking is likely.

## Scope

**In scope**

- LLM-as-mutation operator for evolving code or equations.
- Generate → evaluate → select → mutate as the shared loop.
- Fitness design, diversity maintenance, and eval hacking.
- A minimal symbolic-regression demo and held-out evaluation.

**Out of scope**

- Full production deployment of OpenEvolve or AlphaEvolve.
- Deep formal treatment of genetic programming theory.
- A complete implementation of every diversity scheme in the literature.

## Shape

- The tutorial keeps the default four-part arc: context, motivation, content, conclusion.
- The content section carries the longest explanation and frames the worked example as a symbolic-regression loop.
- The worked example in the content section is intentionally small: a five-generation loop that demonstrates the best-score curve, parent feedback, and one eval-hacking candidate.

## Open questions

- How should a student team balance the overhead of model calls against the number of useful evolutionary evaluations?
- What makes a fitness function robust enough to resist eval hacking in a classroom setting?
- Which diversity mechanism—archive, islands, MAP-Elites, or novelty search—is most natural for the shared task?

> What the team has not settled: an unresolved framing, an example you are not
> sure earns its place, a claim you cannot yet support.
>
> Naming these is cheap now and expensive in review. The panel reads them and
> will not report a known unknown as a discovery.

- (question)
