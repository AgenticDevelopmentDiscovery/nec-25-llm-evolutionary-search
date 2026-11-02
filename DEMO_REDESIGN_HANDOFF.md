# Handoff: Chapter 10 and the two circle-packing demonstrations

Updated November 2, 2026. Branch: `demo/concept-aligned-experiments`.
This is the active cross-account/session entry point. Earlier teaching sources
are preserved in `history/pre-circle-2026-11-02/`; do not restore them into the
active presentation or expose private credentials/run logs.

## User’s current requirements

- Replace the prior task throughout active slides, notes, server teaching pages,
  setup, architecture and documentation with circle packing.
- Follow the supplied notes’ Chapter 10.1–10.5: 2/3/2/1/2 conceptual frames.
  A separate title and the remaining main frames support two demonstrations.
- Use both unit-square cases from AlphaEvolve Appendix B.12: N=26 and N=32,
  variable radii, maximize summed radii; tangency allowed. Do not substitute area
  or equal-radius packing.
- Keep questions first, sequential mechanism blocks, then answers; full presenter
  explanations in notes; Aggie Maroon with strong contrast; 20–25 minutes total.
- Introduce packing rules and the summed-radii objective in two frames after the
  title, before the framework. Define basic terms for students with mixed backgrounds.
- Keep architecture/API detail in the appendix and a separate document.
- Evolve actual program source; show what Luna receives, returns and changes.
- Preserve historical work, all critique rounds and the unchanged vendor snapshot.
  Do not commit, push, deploy or run the reviewer panel.
- All six approved Luna calls are spent: three completed rounds per case, timeout
  35s. See `demo/READINESS.md`; a new session has zero remaining allowance.
- Voice/video are deferred; scripts and private recordings remain ignored.

## What “the AlphaEvolve example” means

The mathematical tasks match the paper’s Appendix B.12. Its public repository
contains discoveries and verification, not the original engine. This repository
implements the source → execution → independent evaluation → selection loop
using TAMU `protected.gpt-5.6-luna`, bounded local work and our own initial solvers.
Never present its short-run results as the paper’s reported construction or as
proof of a global optimum. Do not put a published answer into a hidden start.

## Read order and implementation map

1. AGENTS.md and CLAUDE.md: preservation and paired-source method.
2. This handoff, demo/CIRCLE_PACKING_DESIGN.md, demo/READINESS.md.
3. Current topic.md, metadata.yaml and all source/concepts pairs in sections/.
4. demo/ARCHITECTURE.md and demo/PRESENTATION_PLAN.md.
5. packing.py (contract/validator), packing_programs/ (initial source),
   packing_worker.py (radius LP + execution), packing_sandbox.py (isolation),
   packing_controller.py (population/rounds/history/replay), model_worker.py
   and settings.py (provider), server.py and static/packing.* (HTTP/UI).

The local course PDF may be missing from a fresh clone because notes/ is ignored.
Obtain the instructor’s Chapter 10 when absent rather than inventing quotations.
The current shared Pandoc source produces browser frames, notes, PDF handout,
overlays, long-form document and static site. The server rebuilds saved prose;
PDF exports require `just build` and `just overlays`.

## Evaluation semantics

- A program is source implementing solve(initial, seed, steps). A witness is the
  returned circle triples. Fitness aggregates three complete, valid trials.
- Default starts are inherited packings: freeze the previous best construction
  per seed, re-evaluate all parents on that bank, then compare the child on copies
  of it. Store bank IDs. Old-bank medians are history, not current selection.
- An optional fixed-start protocol keeps the original common starts throughout.
- Current limits: N=26/32; seeds 3/4/5 by default; 80 requested steps; 8 seconds
  hard wall per trial; at most three calls/run; 35 seconds/call; 240 seconds/run.
  Actual work/time can differ. Source can fail to honor a requested step count;
  the hard deadline still bounds it and incomplete execution is ineligible.
- Radius allocation is a linear program only for fixed centers. SciPy HiGHS solves
  it with a common 1e-8 construction margin. Independent checks use tolerance 1e-9.
- Top-three selection ranks complete medians, then minimum, then stable source ID.
  It does not implement tournament sampling, islands or guaranteed diversity.
- Keep best valid construction progress separately, including a verified partial
  witness. Do not call that curve fixed-protocol program fitness.
- LIVE LLM means a real provider proposal. NUMERICAL ONLY makes no API request.
  RECORDED REPLAY needs genuine provider/transcript/geometry provenance and never
  establishes fresh performance after an executor change.

## Propagation checklist

| Surface | Required consistency |
| --- | --- |
| topic / metadata | Chapter 10 outcomes, Python artifacts, two published packing cases |
| sections + concepts | Requested frame counts; claims, examples, notes and exclusions agree |
| presentation plan | Derived frame/reveal counts, 20–25-minute schedule, two demo transitions |
| browser deck / PDFs / site | Rebuild from saved prose; no stale task text or clipped content |
| demo controls | Both N cases, solver checkboxes, origins/context, inherited/fixed starts, explicit gates |
| source and diff | Actual admitted Python, real parent IDs, syntax-normalized duplicate identity |
| evaluation | Geometry, scores, completion, bank identities, seeds, work/time and separate best witness |
| guide and exchange | Full method names, actual mechanisms, exact request/public return; no authorization |
| architecture and figures | Source execution boundary, independent verifier, state ownership and feedback |
| setup and READMEs | SciPy + Bubblewrap, own ignored key, launch/reconnect, no-call preflight |
| tests / readiness | Actual checks and outcomes; no paid call hidden in a test or retry |
| private practice | Script matches final frames; no voice/video generation unless requested |

## Continuation and completion

Inspect git status before changes; preserve the uncommitted work. Complete real
numerical tests, HTTP/Stop/reconnect checks, source isolation tests and required
regressions. Inspect browser rendering and changed PDF pages. Run the public-file
scanner. Rehearse only within the remaining six-call allowance and retain failures.
Update readiness with actual call use and outcomes. Presenter aloud timing remains
a human action; synthetic speech does not verify it.

A fresh agent should first read readiness and inspect existing processes rather
than launching duplicate servers or replaying paid calls. Use an unoccupied port
if an old server is still running; never kill an unidentified listener.

## Scope clarification from the user — November 2, 2026

The user reports that the instructor suggested circle packing. The original
assigned demonstration is no longer a compliance target. Omit the lineage survey.
Treat the topic brief as guidance: add useful fitness, diversity and cost concepts
where they fit, while retaining the agreed frame counts, two packing demos,
three model rounds per demo and 20–25-minute presentation. Do not reintroduce a
different domain or require five generations merely to match the old brief.
All six model calls remain spent; the new frozen-program checks are numerical-only.
