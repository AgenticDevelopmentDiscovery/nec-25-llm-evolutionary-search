# Current handoff: 25-minute solver-evolution classroom

Current numerical fix: `demo/bm_refinement.py` makes retained Burer–Monteiro
stages after stage one lift/perturb/refine the incoming partition. First-stage
and fresh calls preserve the initial benchmark behavior; old replays are unchanged.
New records/context carry `retained-bm-refinement-v1`. This is an offline-tested
adapter change, not a new live Luna rehearsal. Do not spend additional model calls.

The current instructions supersede the historical initial handoff below. Read `demo/READINESS.md`, `demo/PRESENTATION_PLAN.md` and `demo/ARCHITECTURE.md` first. The server, checked initial populations, exact exchange and three genuine three-call recordings now exist. All nine original revision calls and six additional attempts are used; do not start more without a new allowance. The first two current cases use the 1000-vertex signed random graph and two real rounds each; one source terminated after invalid parent validation. See READINESS.md for exact outcomes. Checkboxes choose P0 only, while Luna may use all kernels. The current deck has 19 main frames / 73 reveals focused on content and three demos, followed by 3 optional architecture/API appendix frames / 12 reveals. Main content is 21:40 plus 45s reserve; the optional appendix adds 2:35. Use the Appendix button or frame-picker group; normal advancing ends at the main conclusion. Preserve earlier work, old rounds and the 133-file vendor snapshot. Do not commit, push, deploy or invoke the reviewer panel.

The current private script is complete at `/rehearsal` and `/rehearsal-script`. Voice and video generation are deferred at the user’s request; offline TTS is not the requested future voice. Presenter aloud timing remains distinct from synthetic narration. Helping materials stay under ignored `demo/rehearsal/`.

Current author preview: `just demo` reuses an identified server from this same
repository on the requested port. Saved prose automatically rebuilds browser
frames and HTML notes; open presentation tabs update without losing frame/reveal
or demo state. Invalid drafts keep the last successful deck and display an error.
PDF exports still require `just build`. No listener is killed automatically.

---

## Historical initial handoff (retained for provenance)

# Start here: the 15-minute LLM evolutionary-search tutorial

This is the tutorial project, separate from the submitted Max-Cut assignment.
The user selected a live Max-Cut demonstration to replace the old symbolic-regression
example. Preserve existing work and the source/concepts pairing described in
`CLAUDE.md`. Do not commit, push, deploy, run a reviewer panel or edit old critique
rounds unless asked. No new live model request was made during this handoff.

## Read in this order

1. `CLAUDE.md`, `demo/ASSESSMENT.md`, and the existing topic, sections and round-001 synthesis.
2. `demo/PRESENTATION_PLAN.md`: a complete 14-minute schedule plus one-minute reserve.
3. `demo/IMPLEMENTATION_BRIEF.md`: implement the local live server/controller/UI and tests.
4. `demo/README.md`, `demo/backend.py`, `demo/classroom_profile.json`.
5. `demo/vendor/SOURCE_MANIFEST.json`, then the vendored modules only as needed.

## What is already real

The algorithm suite/reference framework has been copied as unchanged source,
with original source commit and SHA-256 inventory. No credentials, environments,
assignment solutions, campaign histories or compiled native dependencies were
copied. The runnable classroom adapter supports bounded strategy programs,
original-graph rescoring, RNG seeds and validated starting labels. Four new
adapter checks and fourteen original BM test methods passed in the staged copy;
see the verification record for actual counts if a later rerun differs.

The selected public graph is `torus_pm_10_s11.txt`: 100 vertices, 200 signed edges.
Its reference cut is 68, not an independently established global optimum. With
seed 3 the weak parent gets 58; a measured tabu comparison gets 68. Across seeds
0–9 that tabu configuration reached 68 in ten numerical checks, about 0.05s per
call. These are numerical measurements, not LLM search results or a 180-second
latency guarantee. `demo/evidence/selection_benchmark.json` contains the actual
measurements without assignment vectors to avoid shipping the answer.

## What you must implement next

A loopback web demo with live model proposals, fair numerical evaluation,
selection, a visible strategy diff and a genuinely updated graph/fitness trace.
Allow RNG seeding, optional validated assignment seeding, Stop, Reset, New Run,
reconnect and clearly labeled replay. The server/controller/UI do not exist yet;
`demo/backend.py --smoke` is intentionally labeled numerical-only.

Use the bounded strategy-program representation in the brief. It evolves
compositions/configurations of real algorithms rather than pretending to invent
new kernels. Show this scope explicitly. Do not simply cycle the included smoke
fixtures and call that live LLM evolution. Keep a real model transcript and raw
measured events for every successful rehearsal. Replay must be derived from a
recorded real run and have a persistent REPLAY label.

The live budget is 165 seconds, hard closure by 175 seconds, at most three model
calls, two children per round, and serial bounded trials. Model latency is the
unverified part. Begin with no-cost/offline integration checks, then a single
bounded real-model rehearsal with the configured caps if existing local access
works. No automatic credential installation or recursive agent/controller calls.
If live access is blocked, report it and complete all independent UI/offline work.
Do not claim readiness until actual live/replay and interruption paths are tested.

Update `topic.md`, paired section sidecars and prose from symbolic regression to
this example. Retain Metropolis/16:9 and the shared build workflow. Replace the
placeholder bibliography and cite verified primary sources. Render and inspect
the actual deck: the existing PDF has 19 pages, including four section dividers,
which is too much for the intended demo-centered schedule.

Do not start with native solver builds, cluster support or the large graphs.
They add deployment risks without teaching the central idea in a short class.
The complete copied dispatcher remains useful as reference and for later expansion.
