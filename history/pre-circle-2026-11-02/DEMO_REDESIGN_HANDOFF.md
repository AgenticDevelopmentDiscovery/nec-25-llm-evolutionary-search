# Handoff: concept-focused evolutionary-search demonstrations

Prepared November 2, 2026. This document is intended to be sufficient for a new
model, account, or session working in this repository.

## 1. Active task and authority

The user created the local branch **`demo/concept-aligned-experiments`** to try a
different set of demonstrations, more closely tied to the tutorial's concepts.
It branches from **`Tamim-dev`**, initially at commit
`59dbd6bd9e5cad58f7c72922dc7a53a6a6d7dfb2`.

The current request is to document the redesign and explain a possible
circle-packing implementation. **Circle packing has not yet been selected as a
replacement, and no circle-packing demo has been implemented.** The proposed
experiments below are a concrete starting design, not measured results or an
already approved experimental protocol.

Preserve the existing Max-Cut implementation, prior critique rounds, recorded
evidence, private settings, and presenter edits. Do not commit, push, deploy,
invoke the reviewer panel, or modify `demo/vendor/maxcut/` without a new explicit
instruction. The old Max-Cut example is the baseline to preserve, not a constraint
that prevents choosing a new task on this branch.

**New model-call allowance: zero.** Earlier paid rehearsal allowances were used.
Configured credentials and previous user-run experiments do not authorize this
agent to make more calls. Complete planning, numerical prototypes, and offline
checks first; obtain a concrete call allowance before a new live rehearsal.

Another account/session must use its own private credentials. Never copy keys
into this handoff, prompts, source, output artifacts, or public run records.
See [STUDENT_SETUP.md](STUDENT_SETUP.md). A local branch and uncommitted files do
not appear in a fresh remote clone until the user separately publishes them.

## 2. Read these first

1. [AGENTS.md](AGENTS.md) and [CLAUDE.md](CLAUDE.md): workspace rules and paired
   `.prose.md` / `.concepts.md` method.
2. This handoff and [circle-packing design](demo/CIRCLE_PACKING_DESIGN.md).
3. [topic.md](topic.md), [metadata.yaml](metadata.yaml), and all current
   `sections/*.prose.md` / `sections/*.concepts.md`.
4. [demo/ARCHITECTURE.md](demo/ARCHITECTURE.md),
   [demo/README.md](demo/README.md), and [demo/READINESS.md](demo/READINESS.md).
5. Relevant implementation and tests, listed below, before editing them.

The course source is `notes/agentic-development-notes.pdf`, **Chapter 10**:
Definition 10.2 and Eq. 10.1; Sections 10.2.2–10.2.3 on LLM mutation and context;
10.3 on elitism, selection and population collapse; 10.4 on fitness design.
`notes/` is ignored and may be absent in another clone. If absent, request the
course notes or use their instructor-provided source; do not invent quotations.

The remainder of [CODEX_DEMO_HANDOFF.md](CODEX_DEMO_HANDOFF.md) preserves prior
Max-Cut tasks and evidence. Its old “implement next” instructions describe work
that already exists. Its old call allowances are not fresh authorization.

## 3. What currently exists

The runtime is a Linux/WSL Python loopback server with static HTML/CSS/JavaScript
and server-sent events. The usual address is `http://127.0.0.1:8766/`.
Use `python demo/server.py --port 8766 --rounds 3`; `--check` performs local
configuration/hash checks with no API request. No deployment is required.

| Component | Current responsibility |
| --- | --- |
| `demo/backend.py` | Interpret bounded Max-Cut stage programs; generate numeric starts; independently rescore partitions |
| `demo/bm_refinement.py` | Retained downstream Burer–Monteiro refinement using unchanged numerical primitives |
| `demo/proposals.py` | JSON schema, context, normalization, genome identity, validation, readable diff |
| `demo/controller.py` | Population, trials, API round gates, execution, selection, cancellation, replay, evidence |
| `demo/model_worker.py`, `demo/settings.py` | Tool-free TAMU/OpenAI transport, private configuration and public response stream |
| `demo/server.py` | Loopback routes, tokens/origin checks, static teaching pages, preview rebuilds |
| `demo/experiments.py`, `demo/classroom_profile.json` | Current presets, progress metrics and resource limits |
| `demo/static/app.js`, `index.html`, `style.css` | Demo controls, trial table, numerical witness, lineage, source attribution |
| `demo/static/presentation.*`, `demo/build_presentation.py`, `demo/preview.py` | Browser frames and notes derived from shared prose, save-to-preview updates |
| `demo/static/algorithms.*`, `exchange.*` | Worked mechanisms and exact request/public-response inspection |
| `demo/ARCHITECTURE.md`, `demo/build_architecture.py` | Architecture document, HTML and PDF |

**Actual presentation snapshot at this handoff:** 18 main frames / 60 main
reveals, plus 3 appendix frames / 12 reveals. Main planned time is 1,250 seconds
(20:50), with 45 seconds reserve and 155 optional appendix seconds. The final-state
handout has 21 pages. Several older planning/status files still say 19 main frames
and 73 reveals; those counts became stale after the user shortened demo frames
and removed the comparison frame. Trust the saved sections and generated
`demo/static/presentation.json`; calculate counts rather than restoring old text.

Preserve recent functional corrections:

- Frames may have any number of reveal Divs; questions and answers are optional.
  Browser and PDF conversion handle their removal. Do not reintroduce a fixed
  four-reveal requirement. Preserve the tests in `demo/tests/test_presentation.py`.
- The displayed partition score identifies initial state, trial/seed/program,
  or best witness. Its source can be located in the scrollable solver table.
  Incomplete programs remain visible. Seed indexing handles uint32 wraparound.
- A retained downstream Burer–Monteiro stage now lifts the incoming partition to
  vectors, perturbs angles reproducibly, optimizes/rounds/polishes, and protects
  the incumbent. First-stage/fresh behavior is unchanged. New records identify
  execution version `retained-bm-refinement-v1`; older replay behavior is preserved.

Current Max-Cut runtime caps: population 3, stages 1–3, children at most 2 per
call, 3 model calls per run, 35 seconds per call, 240-second run deadline and
cleanup by 250 seconds. Current random/dense graph trials share 8 numerical
seconds across their stages; the historical torus uses 1.5 seconds. Numerical
trial seeds default to 3/4/5; they do not control Luna's randomness.

The selected provider is **chat.tamu.ai**, model **`protected.gpt-5.6-luna`**.
Keep private configuration in ignored `demo/.env`; use the committed example
and student setup guide rather than copying anyone's credentials. Preserve these
three distinct modes on every screen, export and run record:

- **LIVE LLM:** a real provider request produces the proposal; local numerical
  execution and independent evaluation follow. Show the actual sent context and
  received public response, including failures and partial streams.
- **NUMERICAL ONLY:** no model request occurs. Disclosed local programs or
  validation probes run through the evaluator; never label them Luna proposals.
- **RECORDED REPLAY:** play an identified earlier genuine run. It makes no new
  model request and does not establish a fresh result under a changed executor.

The current initial-suite comparison uses Tabu Search + Simulated Annealing versus
Tabu Search + Breakout Local Search + Burer–Monteiro. The latter was chosen from
a same-graph, three-seed pilot screen, not held-out evidence of general superiority.
The two suite sizes also require different initial evaluation effort.

Historical verification is recorded in `demo/evidence/`, including
`bm_handoff_verification.json` and `cut_display_verification.json`. The former
records 40 prior regression tests and 12 numerical worker trials. Later focused
preview/export checks covered 11 tests. These are historical records, not a claim
that the whole current suite was rerun for this handoff.

## 4. What the redesign should teach

The old presets mainly change starting algorithms or graph structure. The new
demonstrations should make these Chapter 10 mechanisms directly observable:

1. **Inherited variation:** a new artifact is derived from a survivor, with a
   visible parent-to-child change.
2. **Context-informed mutation:** measured successes, failures and history enter
   the next request and can influence the next proposal; model weights stay fixed.
3. **External evaluation and selection:** execution supplies evidence, invalid or
   incomplete results do not acquire invented fitness, and the survivor rule is
   visible, including its treatment of the incumbent.

Keep the evolving object a **solver program/heuristic**, unless the user explicitly
changes that choice. A returned partition or packing is its **solution witness**;
trial measurements determine program fitness. A more attractive visualization is
useful, but changing Max-Cut to circles alone does not change the evolutionary loop.

Define the implementation scope honestly. The current system evolves JSON
recipes over prewritten numerical kernels. It does not synthesize arbitrary
algorithm source. A source-code-evolution version is a separate representation
and execution project; do not describe a JSON recipe as newly invented Python.

## 5. Proposed three-demo design

These are teaching experiments. A few stochastic calls do not establish causal
or statistical superiority. Retain negative results and plateaus.

### Demo 1 — inherited mutation versus independent generation

Question: **What does using a survivor as a parent change?**

Prepare one evaluated initial population. Compare one parent-conditioned proposal
with one independently generated proposal. Both receive the same task, allowed
representation and resource limits; only the inheritance input differs. Evaluate
both from the same numerical starts under the same protocol. Show parent, diff,
child, trial results and actual survivor decision. Report whether structure was
actually inherited; do not guarantee the inherited child will win.

The existing response contract requires 1–3 parent IDs and assumes a parent when
building the diff. It cannot represent a genuinely independent child unchanged.
Add an explicit proposal origin and mode-specific ancestry validation; permit an
empty parent list for independent generation. Update lineage, diff and controller
paths accordingly. **Do not attach a fake parent ID to an independent proposal.**

### Demo 2 — structure-only versus evidence-rich context

Question: **What information makes a mutation informed?**

Use identical parent programs and a frozen, genuinely measured history snapshot.
One request receives program structure and required constraints. The other also
receives trial evidence, failed/duplicate attempts and a concise diversity or
mechanism summary. All numeric limits and evaluation starts remain fixed.

Make the payload difference visible. Canonically order parents in both arms so
ranked ordering does not leak withheld scores. Keep compulsory validity and
budget constraints in both. Define exactly what is withheld before testing.
Do not let one arm use children or evaluator outcomes generated by the other.

Compare the actual edits, invalid/duplicate rates, completed fitness changes and
cost. An explanation that sounds informed is not itself an improvement. Extra
context tokens are a real cost to report. No general advantage is guaranteed.

### Demo 3 — verified fitness, selection and elitism

Question: **Why does a plausible or high-scoring proposal sometimes not survive?**

Show at least two proposal/evaluation rounds with the next context incorporating
the previous results. Keep the actual acceptance/rejection and survivor decisions
visible. Preserve the best valid witness separately from eligible program fitness.

For a deterministic failure illustration, use an explicitly labeled
**NUMERICAL-ONLY VALIDATION PROBE**: invalid output, a verified but worse child,
or an incomplete trial. It is not a fabricated Luna response. With population
capacity three, a child worse than the champion may still occupy another slot;
to demonstrate nonselection of a worse child, start with a full population and
compare it with the actual cutoff. Elitism protects the incumbent under the
declared, comparable evaluation protocol; it does not require rejecting every
nonchampion child or guarantee diversity.

### Budget proposal to settle before rehearsal

The user's prior preference was at least two model calls in a live demonstration.
A small new plan could allocate two calls to Demo 1 (one per arm), two to Demo 2
(one per arm), and two sequential calls to Demo 3. **That is a proposal for six
calls, not permission to spend them.** If each comparison arm needs two generations,
the call requirement increases; state the full total before requesting allowance.

Keep the full presentation within 20–25 minutes. Replace the old demo slots;
do not simply add these experiments to the existing lecture. Target each guided
demo at 3–5 minutes, then measure latency and retime the whole deck. Use clearly
labeled genuine replay where necessary. Never add artificial waiting or claim
an untested runtime guarantee. Per-run caps and total rehearsal allowance are
separate quantities.

## 6. Evaluation choices that must remain explicit

- **Fair solver comparison:** copy common starting states for every competing
  program and trial. All stages of one program share its trial allowance.
- **Within-program continuation:** a retained stage receives that trial's updated
  state. A replacement-only program does not silently inherit another competitor's
  previously evaluated output.
- **Across-generation warm starts:** possible, but a different protocol. Freeze
  the same incumbent bank for parents and children in each comparison and account
  for preparation/re-evaluation costs. Do not compare old fitness from one start
  distribution with new fitness from another as if conditions were unchanged.
- **Completion:** define normal bounded completion/convergence versus interruption,
  hard timeout or invalid output. This must be task-specific, especially for an
  anytime packing search; do not blindly copy a work-completion rule and call all
  intentional stopping censored.
- **Fitness convention:** the course minimizes `f`; a maximized verified quality
  can be mapped to `f = -median(quality across complete trials)`. State the primary
  metric and tie-breaks before running.
- **Seeds:** numerical repeatability, not algorithm selection or deterministic
  Luna responses. Three prescribed trials are classroom evidence, not a broad
  generalization study. Separate training and withheld checks if claiming transfer.
- **References:** an achieved construction supplies a feasible score, not a proof
  of global optimality. Record task, objective, constraints, tolerance and provenance.

## 7. Propagation map — the whole tutorial

An implementation is unfinished while different surfaces describe different
artifacts, objectives, protocols, modes or outcomes.

| Surface | Required propagation |
| --- | --- |
| `AGENTS.md`, `CODEX_DEMO_HANDOFF.md`, this handoff | Mark active task/domain and read order; preserve old instructions as history; update unresolved decisions and actual verification |
| `topic.md` | Rewrite the promise around the selected artifact and the three concepts; distinguish baseline, intended experiments and observed outcomes |
| `metadata.yaml` | Update subtitle, audience outcomes and domain-specific terminology |
| `sections/01-context.*` | Keep evolutionary optimization first; explain population, inheritance, fitness and seed terminology plainly |
| `sections/02-motivation.*` | Introduce the LLM operator and the selected problem; work one candidate through the objective/constraints; define who proposes, executes and scores |
| `sections/03-content.*` | Replace the old suite/stress-case demo narrative with the actual concept experiments, mechanisms, controls, failures, costs and evidence |
| `sections/04-conclusion.*` | Map the observed system to `(A,f,mu,sigma,P0)` after the demos; distinguish program quality from witness quality and reference attainment |
| `sections/05-appendix.*` | Keep architecture/API detail in the appendix; update schema, context, validation, state transfer and data-flow examples |
| Every `.concepts.md` pair | Update claims, decisions, unresolved questions and excluded claims; do not leave contradictory sidecars |
| `demo/PRESENTATION_PLAN.md` | Retitle/retime the full arc; per-frame questions, reveal transitions, demo navigation and planned audience pauses |
| `demo/IMPLEMENTATION_BRIEF.md` or a new active brief | Preserve the old brief as history; make the new executable contract and acceptance criteria unambiguous |
| Backend / task adapters | Witness format, starts, kernels, objective, validation, completion, reproducibility and work/time counters |
| `demo/proposals.py`, `controller.py` | Task-specific schema, independent versus inherited origin, context arms, duplicate identity, ancestry, fitness and selection |
| `demo/model_worker.py`, `settings.py` | Reuse fixed provider transport/key isolation; change transport only if genuinely required by the chosen representation |
| `demo/experiments.py`, `classroom_profile.json` | New named presets, controlled differences, active domain and measured caps; retain original scenarios as legacy where appropriate |
| `demo/server.py` | Task-aware instance/status/results and static routes; loopback-only service, token/origin checks and preserved old records |
| `demo/static/index.html`, `app.js`, `style.css`, `brand.css` | Show evolving artifact, actual diff, context, fitness/trials, witness and source; task-specific geometry; retain Aggie Maroon contrast and clear modes |
| Algorithms and exchange pages | Full algorithm names, mechanisms and worked examples; exact actual request/public response; no fabricated example presented as received output |
| `demo/ARCHITECTURE.md`, figures and architecture exports | Explain ownership, provider call, interpreter/executor, trusted evaluator and feedback; add task/representation/version boundaries |
| `references.bib`, figure captions | Verified primary sources; citations next to external facts; no unverified “best known” or copied solution claims |
| `demo/tests/` and new numerical tests | Ancestry/context controls, task validation, real numerical execution, budgets, cancellation, replay boundaries and old Max-Cut regressions |
| `demo/evidence/`, `READINESS.md` | New versioned evidence and actual outcomes; keep old reports unchanged and labeled with their original task/executor |
| `README.md`, `demo/README.md`, `STUDENT_SETUP.md`, requirements | Published branch, task selection, dependencies, keys, direct launch, zero-call setup and mode behavior |
| `justfile`, filters, CI | Fresh-clone builds, variable reveal counts and PDF validity; never invoke the deploy recipe as a validation step |
| Generated browser/HTML/PDF/site outputs | Rebuild from the common source; derive frame counts/timing; inspect changed frames and documents |
| Ignored `demo/rehearsal/` and speaker aids | Update scripts, pauses and transitions after the content settles; voice/video remain deferred unless requested; keep aids ignored |

## 8. Implementation sequence and completion criteria

1. Inspect branch/status and preserve current work. Resolve only material choices:
   task, evolved representation, experimental controls and later API allowance.
2. Freeze the new task/evaluator contract and draft the three experiments. See
   the circle-packing document if that option is chosen.
3. Implement and numerically test the task adapter and verifier first. Screen
   feasible baselines and timing; do not tune on the displayed seeds and claim
   that as held-out success. Keep the old Max-Cut path and tests functional.
4. Add origin/context conditions, versioned lineage and task-aware records. Carry
   those distinctions through replay and comparison pages.
5. Complete the observable UI and teaching propagation above. Keep each frame
   focused: question, concrete mechanism/example, then answer. Optional blocks
   and sequential reveals are supported; do not refill deleted presenter content.
6. Run offline tests and real numerical worker checks; inspect browser rendering
   and all changed PDF pages. `python demo/check_public.py --history` must pass.
7. Only with a new call allowance, run bounded live rehearsals and real-provider
   interruption checks as needed. Preserve outcomes, including failures. No silent
   retries, fallback proposals, altered responses or fabricated success curves.
8. Rehearse the whole presentation aloud and record actual timings. Generated
   narration cannot certify human delivery. Update readiness with what was
   actually verified and what remains a presenter action.

Done means: three concept questions have visible experimental evidence, every
surface uses the same artifact/objective/protocol, mode provenance is accurate,
fresh student setup works, required checks pass, the timing fits, and the user can
follow a real proposal from context through execution, measurement and selection.
No claim requires beating a published record or guaranteeing that Luna improves.

## 9. Paste into a fresh session

```text
Continue the tutorial redesign on branch demo/concept-aligned-experiments.
Read AGENTS.md, CLAUDE.md, DEMO_REDESIGN_HANDOFF.md, and
demo/CIRCLE_PACKING_DESIGN.md first, then inspect git status and the current code.
The previous Max-Cut demo must be preserved. The intended new demos explain
inherited variation, context-informed mutation, and verified selection.
Circle packing is an option described in the handoff, not an implemented feature
or a confirmed replacement. Resolve the task and representation choice before
changing the runtime; continue independent offline preparation where possible.
Keep prose/concepts, slides, notes, server/UI, architecture, student guide and
evidence consistent. Do not restore removed presenter text or fixed reveal counts.
No new model calls are authorized. Do not commit, push, deploy, run the reviewer
panel, modify the hashed Max-Cut snapshot, or expose private keys/run records.
Report actual verification, unresolved decisions, and the next concrete step.
```
