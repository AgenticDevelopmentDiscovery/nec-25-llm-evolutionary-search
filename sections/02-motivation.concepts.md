# Claims
- The LLM supplies context-conditioned mutation; the external harness supplies fitness.
- Model weights remain fixed; population and history provide run-time memory.
- Signed Max-Cut penalizes negative crossings; both supplied references are unproven.
- Exact flip gain follows from incident edges; moving state, best witness and strategy fitness differ.
# Decisions
- Introduce the LLM only after the classical cycle, then instantiate the optimization problem.
- Use a four-vertex signed illustration; the default live graph is the 1000-vertex signed random instance. Preserve old torus records as history.
- Teach signs, objective and local moves before solver interpretation.
# Open questions
- Equal-budget comparison with independent or random mutation requires a separate experiment.
# Not doing
- Direct partition generation, model self-grading or a certified optimum.
