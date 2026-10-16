# Clarity & Exposition — Round 1

**Recommendation:** minor polish
The tutorial has a good topic line and a clear teaching arc, but the core search loop and the evaluation heuristic need sharper exposition in the content section.

## Strengths
- `topic.md` — The proposal is concrete and does not drift into vague course-general claims.
- `sections/01-context.prose.md` — The origin and scope are placed early in a way that helps the reader form a correct mental model before the motivation section.
- `sections/02-motivation.prose.md` — The role of evaluation and scoring pressure is framed directly in terms of agentic development rather than as a generic AI method.

## Weaknesses
- `sections/03-content.prose.md` — The `How it works` section names the generator, evaluator, selector, and LLM mutation operator, but it leaves the full loop relationship implicit instead of showing a reader how the pieces feed one another.
- `sections/03-content.prose.md` — The `Using it: the basic case` paragraph gestures toward a symbolic-regression demo, but does not yet give enough concrete code or commands for a reader to follow the loop without guessing.
- `sections/03-content.prose.md` — The section introduces fitness, complexity penalty, and held-out checks, but the prose does not explain which design choice is the primary input to the model prompt in the mutation step.

## Actionable
1. `sections/03-content.prose.md` § `How it works` — Turn the prose into a node-and-arrow explanation of the four-stage loop (`generate → evaluate → select → mutate`) and explicitly identify the parent score and archive object entering the mutation prompt. (*why:* This gives the reader a model they can carry into the example.)
2. `sections/03-content.prose.md` § `Using it: the basic case` — Add a short pseudocode block or actual one-paragraph command trace showing the scoring loop with one parent set, one evaluator call, and one mutation prompt. (*why:* It lowers the gap between the idea and a student’s ability to replicate it.)
3. `sections/03-content.prose.md` § `Designing the fitness function` — Clarify that the objective is a design decision for the evaluator, not a natural fact of the problem, and show why the complexity penalty and held-out error share equal status. (*why:* This is the most important distinction the reader needs to learn from the tutorial.)
