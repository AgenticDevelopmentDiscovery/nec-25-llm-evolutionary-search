# Conclusion — spine

## Purpose

Say what the reader can now do, point at what comes next, and name what is still open.

## Claims

- The reader can describe an LLM-guided mutation loop and the role of the fitness function in selecting candidate programs.
- The reader can distinguish exploration pressure from eval hacking and demand held-out validation.
- The reader can see that the next learnings are fitness design, diversity management, and search-budget discipline.

## Decisions

- The conclusion keeps the capabilities in the same language as the topic proposal rather than offering a broad topic summary.
- The recommended next readings are ordered from the seminal paper to the open implementation and then to evaluator-design practice.

## Open questions

- Which of the diversity strategies is most useful for short, classroom-style evidence loops?
- What makes a reward function robust enough to use as a teaching example without inviting a gameable benchmark?

## Not doing

- We are not recommending a specific production evaluator architecture.
- We are not pretending that LLM mutation has a settled general method across all code-generation domains.
