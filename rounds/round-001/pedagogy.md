# Pedagogical Readiness — Round 1

**Recommendation:** minor polish
The tutorial is concrete and focused enough for a student audience, but the method still needs a stronger worked trace and one more explicit bridge between the proposed loop and the audience’s next action.

**Audience read against:** Students and researchers who already understand Python, simple code-generation workflows, and evaluation harnesses; they should be able to explain the loop and identify why the fitness design matters after reading.

## Strengths
- `topic.md` — The proposal is clear about the tutorial’s subject and its promised capabilities.
- `metadata.yaml` — The audience is specified precisely enough for pedagogy review.
- `sections/03-content.prose.md` — The worked example is appropriate for a small classroom setting: a symbolic-regression loop with held-out scoring and an eval-hacking example.

## Weaknesses
- `sections/03-content.prose.md` — The tutorial speaks of a symbolic-regression example, but the prose does not yet show the reader the actual objects that move between generation, evaluation, selection, and mutation in a way they can reproduce.
- `sections/03-content.prose.md` — The current prose includes the fitness-function and eval-hacking themes, but does not yet make the pedagogical contrast between training error and held-out error fully operational.
- `sections/04-conclusion.prose.md` — The conclusion is readable, but it promises capability without naming the smallest reproducible exercise the reader can perform next.

## Actionable
1. `sections/03-content.prose.md` § `Using it: the basic case` — Add one miniature command or script trace for the symbolic-regression task that shows how an equation is generated, evaluated, ranked, and fed back as a parent. (*why:* This moves the reader from abstract understanding to a follow-along workflow.)
2. `sections/03-content.prose.md` § `Designing the fitness function` — Surface the distinction between visible score and held-out score in the same paragraph that introduces the complexity penalty. (*why:* It directly clarifies what readiness tier the tutorial is asking the reader to reach.)
3. `sections/04-conclusion.prose.md` § `What you can do now` — Rewrite the concluding capability as an implementable action: “You can sketch a minimal generate → evaluate → select → mutate runner and identify a grader that can be hacked.” (*why:* This gives the conclusion a verified promise rather than a topic summary.)
