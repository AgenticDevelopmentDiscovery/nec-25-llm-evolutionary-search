# Visual & Multi-Register Exposition — Round 1

**Recommendation:** minor polish
The tutorial already has a usable multi-output shape, but it needs a figure and a clearer separation of the loop’s objects so the document, slides, and website can carry the same mental model.

## Slide overflow
- `sections/03-content.prose.md` § `Designing the fitness function` — Overflows because: too many ideas. It bundles model mutation, fitness pressure, complexity penalty, and held-out validation into one unit.

## Strengths
- `sections/03-content.prose.md` — The best material is a very teachable core: a loop around generation, evaluation, selection, and mutation.
- `sections/02-motivation.prose.md` — The motivation is concise and tied to the agentic system’s evaluation and selection pressure.

## Weaknesses
- `sections/03-content.prose.md` — There is no figure for the central abstraction, despite the content section being the longest and most compositional section.
- `sections/03-content.prose.md` — The prose uses the same compute and evaluation vocabulary across several paragraphs but does not yet give the reader the visual distinction between candidate generation, score return, survivor set, and mutation prompt.
- `sections/03-content.prose.md` — The paragraph on the symbolic-regression example remains too descriptive, and the slide projection will not teach the relationship well without an accompanying visual.

## Actionable
1. `sections/03-content.prose.md` § `How it works` — Add a one-figure abstraction showing `generate`, `evaluate`, `select`, and `mutate` as boxes with arrows flowing from parent programs and scores into the mutation prompt. (*why:* It repairs the document and slide register together.)
2. `sections/03-content.prose.md` § `Designing the fitness function` — Split the paragraph into two `##` units or sharply compress it into one slide: one unit for scoring and one unit for the held-out or complexity guard. (*why:* It repairs the slide register by ensuring one idea per heading.)
3. `sections/03-content.prose.md` § `Using it: the basic case` — Add an example code fence or command sequence that shows a small evaluation loop in the same order as the prose: propose equation → score → rank → return parents. (*why:* It makes the workflow visible across document and website registers.)
