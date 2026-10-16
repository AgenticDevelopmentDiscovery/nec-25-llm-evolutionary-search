# Content — spine

## Purpose

Teach the HOW: the mental model, then worked use, then the failure modes — so the reader can use the tool on a case this tutorial never showed them.

## Claims

- The reader should be able to explain the LLM-guided program mutation loop as generate → evaluate → select → mutate.
- The reader should be able to identify a fitness function that rewards the intended objective and rejects exploitative shortcuts.
- The reader should be able to trace why diversity maintenance and held-out scoring matter in search.

## Decisions

- The worked example uses symbolic regression because it fits a small, explainable score and demonstrates both code generation and evaluation naturally.
- The tutorial chooses a five-generation demonstration rather than a larger benchmark because the lesson is the shape of the loop, not the final performance.
- The section frames eval hacking through a visible-data special case so the failure mode is concrete and memorable.

## Open questions

- How much of the evaluator should be made visible to the LLM and how much should stay implicit to reduce cheating?
- Which diversity mechanism is best for a small course deployment that must stay explainable?

## Not doing

- We are not introducing a production deployment of OpenEvolve or a full map-elites implementation.
- We are not proving that LLM mutation always outperforms random GP mutation in every setting.
