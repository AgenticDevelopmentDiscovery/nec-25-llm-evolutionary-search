# Claims
- The LLM supplies context-conditioned mutation; the external harness supplies fitness.
- Example mutation retains vector optimization and rounding inside one Burer–Monteiro kernel, then appends local search initialized from its partition.
- The complete child shares the same per-trial time allowance across stages; adding a stage does not add evaluation time or guarantee improvement.
- Model weights remain fixed; population and history provide run-time memory.
- Signed Max-Cut penalizes negative crossings; both supplied references are unproven.
- Conflicting edge preferences require a global tradeoff: the illustrative triangle has weights +3, −2, −2 and partition scores 0, 1, −4 (symmetric remaining case: 1).
- Exact flip gain follows from incident edges; moving state, best witness and strategy fitness differ.
# Decisions
- Introduce the LLM only after the classical cycle, then instantiate the optimization problem.
- Explain the hypothetical mutation in four numbered steps across the existing two mechanism reveals; distinguish proposal from execution and measured benefit.
- Introduce Signed Max-Cut through a hypothetical triangle and a partition-score table; retain the old four-vertex artwork as prior work.
- Explain the crossing indicator and exact objective in detailed notes; introduce benchmark size and unproven reference values with experiment setup.
- Teach signs, objective and local moves before solver interpretation.
# Open questions
- Equal-budget comparison with independent or random mutation requires a separate experiment.
# Not doing
- Direct partition generation, model self-grading or a certified optimum.
