# Context — spine

## Purpose

Say WHAT the topic is and where it came from, so the reader can hold it in mind before being told why it matters or how to use it.

## Claims

- LLM-driven evolutionary search replaces random GP mutation with a language model that reads parents and proposes improved code.
- The original idea is a search loop: generate candidates, evaluate them, select survivors, and feed them back as parents.
- The method grew from GP, FunSearch, AlphaEvolve, and OpenEvolve, but the tutorial treats the workflow rather than a full research history.

## Decisions

- The context section gives the definition first and then the historical lineage, rather than opening with a literature survey.
- The prose mentions FunSearch and AlphaEvolve only as anchor points and keeps the origin short to explain the design.

## Open questions

- How much parent context should an LLM mutation prompt include before the model becomes noisy rather than helpful?
- Should every student demo include a real evaluator, a symbolic-regression benchmark, and a deliberately gameable scoring example?

## Not doing

- We are not surveying all LLM-guided search systems or every evolutionary algorithm variant.
- We are not distinguishing GP formal syntax trees from the code-as-text setting in depth.
