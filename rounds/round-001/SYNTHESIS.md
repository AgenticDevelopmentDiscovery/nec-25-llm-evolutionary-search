# Round 1 — Synthesis

**Panel recommendation:** minor polish
**Seats:** clarity <minor polish> · pedagogy <minor polish> · visual <minor polish>

## Since last round
First round — no prior docket.

## Consensus
Two or more independent seats raised a common concern that the `03-content` section needs a more concrete and visible model of the generate → evaluate → select → mutate loop. The clarity and visual seats agree that the section should teach the control flow more explicitly, and the pedagogy and visual seats agree that the worked symbolic-regression example needs a smaller, more reproducible code trace.

## Conflicts
- none

## Docket
1. **Make the loop visible in the content section** — `sections/03-content.prose.md` § `How it works`
   *Raised by:* clarity · visual · pedagogy · Effort: medium
   Add a node-and-arrow representation or explicit step sequence showing how parent programs and scores enter the LLM mutation prompt and how the archive or survivor set carries the next generation.

2. **Give the basic case a concrete trace** — `sections/03-content.prose.md` § `Using it: the basic case`
   *Raised by:* clarity · pedagogy · visual · Effort: small
   Add a short code fence or command walk-through showing the symbolic-regression loop as propose → score → rank → mutate, with enough specificity for a reader to follow without guessing.

3. **Separate the fitness-design signal from the eval-hacking warning** — `sections/03-content.prose.md` § `Designing the fitness function`
   *Raised by:* clarity · pedagogy · Effort: small
   Rewrite the paragraph so the complexity penalty and the held-out check are clearly framed as different constraints on the same objective, and make the evaluation object more explicit.

4. **Split the slide shape of the scoring paragraph** — `sections/03-content.prose.md` § `Designing the fitness function`
   *Raised by:* visual · Effort: small
   Split the one dense paragraph into the two prose units required by the slide-level structure: one for fitness scoring and one for the held-out or penalty guard.

## Deferred
- `sections/03-content.prose.md` — The prose should eventually include a figure for the central abstraction in the context of the project’s visual register; this is a useful enhancement but it waits behind the loop-model and code-trace changes.

## Do next
1. Add the loop diagram or node-and-arrow explanation to the `How it works` section.
2. Add the concrete symbolic-regression trace in the basic example section.
3. Split or rewrite the dense fitness-function paragraph to reduce slide ideas and clarify the held-out-evaluation relationship.

## Panel health
- The panel produced three useful reports. The `visual` reviewer’s slide-overflow finding is a prose-level estimate, and its recommendation is to split the `Designing the fitness function` paragraph into one score-focused slide and one guard-focused slide. The report format is specific enough to read directly.
