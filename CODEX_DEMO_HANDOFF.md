# Active handoff — circle-packing tutorial, November 2, 2026

Continue on `demo/concept-aligned-experiments`. Read AGENTS.md, CLAUDE.md,
DEMO_REDESIGN_HANDOFF.md and demo/CIRCLE_PACKING_DESIGN.md.

The user confirmed circle packing and requested the exact two unit-square
problems from AlphaEvolve Appendix B.12, N=26 and N=32. The objective is the sum
of variable radii under wall and pairwise nonoverlap constraints. Our controller
and initial methods are classroom implementations; AlphaEvolve’s engine is not
released in its public results repository. Do not claim an exact engine or
record-result reproduction.

The main source follows Chapter 10.1–10.5 with 2/3/2/1/2 frames, plus a title
and six frames supporting two demos. There are three optional architecture/API
appendix frames. Every active surface should describe circle packing. Historical
sources, the previous server and all existing records are preserved separately.
No publication or reviewer panel is authorized.

All six approved rehearsal calls are spent: three genuine source-evolution
rounds per case, both runs complete. No model-call allowance remains. See
demo/READINESS.md and demo/evidence/circle_packing_rehearsal.json for outcomes.

The Python packing function receives a common incoming center bank per trial.
The default iterative-refinement protocol freezes previous best packings and
re-evaluates parents and children from the same bank each round. Fixed-start
comparison remains optional. Never rank different banks as one fitness protocol.
The cumulative verified construction curve is separate from program fitness.

Generated source runs in Bubblewrap, with no repository, private home, host
network or API credentials. Syntax checks alone are not isolation. Missing
isolation blocks execution. Original source, diff, geometry, exact public
exchange, failures and real timings must remain inspectable.

See demo/READINESS.md for actual checks and rehearsal outcomes. Historical
handoffs and earlier presentation sources live in history/pre-circle-2026-11-02/.
Voice/video remain deferred; private practice aids stay ignored.

## Scope clarification from the user — November 2, 2026

The user reports that the instructor suggested circle packing. The original
assigned demonstration is no longer a compliance target. Omit the lineage survey.
Treat the topic brief as guidance: add useful fitness, diversity and cost concepts
where they fit, while retaining the agreed frame counts, two packing demos,
three model rounds per demo and 20–25-minute presentation. Do not reintroduce a
different domain or require five generations merely to match the old brief.
All six model calls remain spent; the new frozen-program checks are numerical-only.
