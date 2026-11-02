# Implement the local live demonstration

## Goal and boundary

Build a classroom demonstration in this tutorial checkout, separate from the
submitted assignment. Preserve the hashed vendored suite; adapt it through
`demo/backend.py`. Finish the server/controller/UI, documents, regression checks,
and a measured rehearsal. Do not commit, push or deploy. Keep the presentation
within 15 minutes and the interactive search segment within 2-3 minutes.

Default instance: `demo/data/torus_pm_10_s11.txt`, 100 vertices / 200 signed edges.
Default seed: 3; measured weak parent cut 58; instructor reference 68. A reference
match is not a proof of global optimality. Do not import the assignment's known
solutions or populate the UI with a prepared answer during a live run.

## Evolving object: a bounded strategy program

The genotype is a list of one to three search stages; `backend.py` is its fixed,
trusted interpreter. Each stage selects a trusted backend, validated parameters,
a bounded work count and whether to start fresh or from retained labels. Supported
classroom kernels are tabu, annealing, BM and BLS. The phenotype is the +/-1
assignment returned by running that strategy. Fitness is computed from the original
edges, never a score supplied by the model. Show all three objects in the UI.

An example of the representation, NOT a prepared live-model response:

```json
{"stages":[{"backend":"tabu","config":{"tenure":11,"restart_after":300},"max_work":3000,"fresh":false}]}
```

The LLM may compose stages and change their parameters; it may not supply weights,
fitness values, arbitrary commands, arbitrary filenames or final assignment vectors.
Render JSON as readable strategy code for the diff, labeled as an interpreted
strategy program. Do not claim arbitrary Python synthesis or novel kernel discovery.
The existing full framework's `evolution_codex.py`, `evolution_candidates.py`,
`evolution_worker.py` and owned-process handling are reference implementations;
do not require their entire legacy campaign state or branch/commit lifecycle.

The proposer receives only parent genomes, allowed-method metadata, scores and
constraints. Do not include the numerical benchmark fixture, known winning
configuration, cached answer vectors or replay records in its prompt/context.
Require JSON-only proposals; the model turn must not run its own numerical
search or recursively launch an agent.

Use a small strict model schema: round ID; parent IDs; a short testable hypothesis;
up to two child strategy objects; mutation category; and optional plateau reason.
Hash normalized genomes, reject duplicates/invalid configs, and record actual
proposal and rejection outcomes. Do not manufacture novelty quotas or silently
replace an invalid model response with an included smoke fixture.

## Fair comparison and population

1. At New Run, derive three trial seeds `[seed, seed+1, seed+2]` modulo 2**32.
2. Generate each trial's starting labels from its seed, and run the weak parent
   once to construct three frozen incumbents. Keep all original vectors private
   to the evaluator, fixed for the run and copied before use.
3. Evaluate parent and children from those SAME frozen starts, with the same
   aggregate strategy time allowance and backend-appropriate disclosed work caps.
   Each strategy receives at most 1.5 numerical seconds per trial.
4. Rank by median recomputed cut across complete trials, then minimum trial cut,
   fewer stages, and stable genome ID. Report incomplete/censored trials rather
   than pretending their fitness is comparable. Preserve the best valid solution
   separately, even if its strategy is not selected as a survivor.
5. Retain at most three strategy genomes; select parents using actual measured
   fitness. If preserving a diversity slot, declare its rule before scoring.
6. Every new model call receives selected parent genomes, scores, actual failures
   and previous admitted genome identities. A chain of fixed backend calls is not
   a live evolutionary experiment unless a real model supplied its mutations.

Default profile: `classroom_profile.json`. At most three model calls total,
including corrections, one active model call at a time, two children per round,
three rounds, 165 seconds total, and terminal cleanup/checkpoint by 175 seconds.
Do not stop solely at normalized score 1: the next bounded round can teach plateau
and selection. Respect earlier explicit user Stop. No model call is free; count
calls and expose recorded token usage if available. Do not invent dollar costs.

## Server and interface

Prefer Python standard-library ThreadingHTTPServer plus static HTML/CSS/JS and
Server-Sent Events, avoiding a frontend build step. Flask/FastAPI is acceptable
only if it materially simplifies implementation and dependencies are explicit.
Bind to `127.0.0.1:8765` by default; no public deployment or credentials in browser
code. Serve the demo UI and API from the same origin. Keep the existing static
Pandoc site usable; add a clearly named demo launch recipe without changing
`just serve` into an unrelated application.

Suggested endpoints:

- `GET /` static demo UI; `GET /api/instance` immutable edges and reference metadata.
- `POST /api/runs` creates a fresh run with mode, seed and optional checked initial
  labels; returns run ID and a per-server write token. Validate size/types.
- `POST /api/runs/{id}/start` starts exactly one owned controller for that ID.
- `POST /api/runs/{id}/stop` cancels its own controller/model/worker processes.
- `POST /api/reset` waits for old owned work to stop, then creates a new run ID;
  it preserves old records. Never delete source/input files or prior run folders.
- `GET /api/runs/{id}` snapshot; `GET /api/runs/{id}/events` SSE with monotone IDs
  and Last-Event-ID/reconnect support. Read/reconnect must never start paid work.

Protect state-changing routes from cross-origin requests; do not provide generic
shell, file-read or file-write endpoints. Treat model JSON as data and UI strings
as text, not HTML. Validate request path/run IDs against the app's run registry.

Use a single controller per run and serial numerical trials. Run kernels in owned
worker subprocesses so Stop/Reset can actually terminate them; a Python thread
with a flag is insufficient for hard cancellation. Reuse start-tick/ownership
checks for model and worker process trees; do not broad-kill other Python/Codex
processes. Avoid nested Codex invocation from a model turn. Reset must await
termination, rotate its run token/ID and ignore late events from the old run.

## State, evidence and real-time events

Use append-only `demo/runs/<run-id>/events.jsonl`, request/config snapshots, graph
and candidate hashes, raw model streams, candidate observations, selected parent
IDs and final assignment. Auto-generated run data should not be picked up by
Pandoc or silently committed; document its retention/export location. A run's
own events retain its mode; switching to replay must never rewrite a failed live
run's evidence. Do not expose tokens, authentication files or hidden reasoning.

Event types: `run_created`, `baseline_scored`, `model_started`, `proposal_received`,
`candidate_rejected`, `trial_started`, `trial_scored`, `candidate_ranked`,
`survivors_selected`, `best_updated`, `round_closed`, `run_stopping`, `run_finished`,
`run_failed`. Include run ID, sequence, elapsed time and actual finite data.
Only send trusted validated assignment labels to the graph renderer. No fabricated
inner-solver trajectory: the adapter currently provides stage/trial outcomes, not
vertex-by-vertex state snapshots. Animate only genuine events, and distinguish
exploratory/current state from the retained best. Do not stretch runtime with
fake sleeps or a synthetic rising curve.

Modes must remain visible:

- **LIVE LLM:** real bounded proposals and real numerical evaluations.
- **RECORDED LLM REPLAY:** previously captured real-model run with provenance;
  original timestamps and any replay speed factor shown separately.
- **NUMERICAL ONLY:** measured preset comparison for offline debugging; never
  called live LLM evolution or used as a hidden fallback.

Show a fixed 10x10 layout with wrap conventions, sign/dash edge legend and hot
frustrated edges. Cut, reference, elapsed/remaining time, seed, call count, current
phase, actual strategy diff, lineage, survivor reason and best-cut history should
fit one projector view. Highlight the active loop diagram stage during model wait.
Require only Start, Stop, Reset/New Run, Seed, Mode and Replay controls; advanced
method settings may be behind an optional details panel.

Allow both an RNG seed and optional original-order +/-1 starting labels. Validate
exactly 100 signs and bind them to this graph. Never accept arbitrary file paths
from the browser. Explain that numerical seeds do not fix stochastic LLM outputs.

## Presentation edits

Follow `PRESENTATION_PLAN.md` and `ASSESSMENT.md`; keep paired concept sidecars.
Update the old symbolic-regression claims in topic/context/content/conclusion.
Replace the placeholder bibliography with primary sources. Keep one loop diagram,
one honest strategy diff and one measured trace. The Max-Cut score does not need
a regression complexity penalty; stage complexity is a disclosed tie-breaker.
Testing more seeds on this graph is not held-out graph generalization.

## Acceptance before claiming classroom readiness

- Vendored file hashes still match SOURCE_MANIFEST; original BM tests and demo
  adapter checks pass in the tutorial environment, not only in the source repo.
- Same-seed numerical runs repeat; invalid labels, altered weights, NaN scores,
  unsupported genomes and oversized work are rejected; parent state is not mutated.
- Real server/browser Start updates actual graph labels and cut; an event-only
  mock is insufficient. Refresh/reconnect does not launch another controller.
- Stop during a real worker and during a bounded model call cleans up only owned
  work. Reset produces a new ID, clears displayed fitness and cannot receive old
  events. Two starts cannot duplicate paid requests.
- No-cost numerical integration works with networking disabled. A stopped/failed
  live call remains visibly failed, not converted into a numerical success.
- Run one bounded real-model rehearsal under the profile caps using existing
  local authentication. Save raw responses, actual candidate strategy diffs and
  independently scored labels. If unavailable, state the precise blocker; do not
  claim a fixture established live integration. Spend no more than the declared
  three calls; no indefinite retries or model-agent self-recursion.
- Then rehearse at least three live seeds/sessions if explicitly authorized by
  the presenter and budget permits. Record time-to-first-proposal, target match,
  total wall time, failures and model calls. Numerical speed measurements alone
  do not guarantee a 2-3-minute network/model outcome.
- Capture a successful genuine run for REPLAY and test its offline playback.
  Do not advertise a replay button as ready until such a recording exists.
- Rebuild/inspect the actual slides and time the full presentation aloud. The
  total including switchovers/recovery must be <=15 minutes. Keep a PDF fallback.

Deliver a brief verified readiness report, real launch/test commands, actual
measured results and remaining limits. Do not commit, push or deploy automatically.

## October 26 presenter revision: current default profile

The user's later instructions supersede the original single-parent, 100-node
and 165-second demo profile above. The current default is a population of four
solver algorithms on the supplied public dense signed graph (100 vertices,
4950 edges). Evaluate every solver and child from identical raw starts, select
the top three, expose exact sent/public-received model context, stream public
proposal text, and demonstrate two model calls even after matching the reference.
The previous torus and its genuine recordings remain a distinct legacy mode.

For the 3–5 minute guided window: default two rounds/calls, 240-second run deadline,
cleanup by 250, 35 seconds per model call, at most two children and serial three-seed
trials. Dense trials allow eight numerical seconds shared across at most three
stages, with work caps 20000 tabu iterations / 200000 annealing proposals / 12000
BLS flips; BM remains 60 sweeps and 16 directions. Bounds are disclosed to the model.
Presenter-controlled round gates permit inspection; waiting consumes the deadline.
Never force delays, fabricate progress, silently fix recorded output, or guarantee
a reference match. Preserve original-edge rescoring, cancellation and eligibility.
The supplied public reference is 402.5209, unproven. No solution vectors are imported.

The user authorized the two-call rehearsal and one additional real-call Stop check.
Those requests are complete; see READINESS.md. Further generation needs a new
allowance. Presenter narration, video, captures and timing logs must be gitignored.


## Later user revision: authoritative 20–25-minute, three-demo profile

This addendum supersedes the older duration, fixed-population and two-call defaults
above. Use a title, ordinary evolutionary algorithms before the LLM mutation
operator, and three architecture/API frames. There are 22 frames / 85 reveals,
24:15 prepared plus 0:45 reserve. Keep Aggie Maroon as the base and generate a
separate architecture/data-flow document and diagram.

Checkboxes choose initial solver programs only; all four trusted kernels remain
available to mutation. Presets: Burer–Monteiro only on the easy signed torus;
Tabu Search, Simulated Annealing and Breakout Local Search on the SAME torus and
seeds; all four on the dense signed graph. All programs and children receive
copies of common raw starts with seeds 3/4/5. The old frozen-parent recordings
retain their original protocol. Small trials allow 1.5s, dense trials 8s; other
stage/work/cancellation contracts remain. Default three rounds/calls per case,
35s per call, 240s total and cleanup by 250s. At most two children and three stages.

The user authorized up to nine new Luna calls, three per case; all nine are now
used. No retries or further paid chat generation without new authorization.
Report median-target and all-trial outcomes separately: the limited suite recovered;
the informed suite reached the primary median target during initialization but
was not universally faster. Calls after target are visible teaching continuation.
Never script the narrative as an inevitable failure of a weak suite.

Final voice must be generated through ChatGPT/OpenAI speech from a proper private
script after all other work. Do not substitute offline TTS as the requested final
voice. Practice aids are gitignored. Presenter aloud timing is a separate human
check and must not be claimed from synthetic narration.


## Latest presenter correction: stronger separation and contrast

Replace the first two torus conditions with `rand_pm_1000_s23.txt`: 1000 vertices,
5043 signed edges, supplied unproven reference 1098. Initial programs and raw seeds
3/4/5 stay fixed. Limited preset checks Tabu Search + Simulated Annealing; informed
preset checks Tabu Search + Breakout Local Search + rank-two Burer–Monteiro. All
kernels remain available to mutation. Both current graphs allow 8s numerical trials.
The dense graph remains a separate real-weight stress case; do not assert a
universal difficulty ordering from density alone. Preserve the old torus evidence.

Normalized initial medians are 921, 975, 992 and 1012 respectively. A preliminary
BLS direct-dispatch screen did not expand classroom defaults; only the normalized
screen is authoritative. Burer–Monteiro is strongest here, not inherently weak.
The public algorithm guide explains why initial suites differ.

The user authorized six additional attempts. Two sandbox DNS failures were counted,
then four real requests completed across two replacement runs. The limited suite
improved median 975 → 1008; the informed suite retained eligible median 1012 while
incomplete children produced witness 1060; an invalid parent stopped that run.
Neither reached 1098. The current recordings have two real calls each; the server
still permits three per case. No unused call allowance remains. Verified failed
model sources may replay with explicit FAILED provenance; transport-only failures
cannot qualify. Never repair or conceal the recorded parent-ID failure.

Use dark body/code text on white, white text on maroon, visible disabled controls,
and high-contrast graph markers. Check actual rendered text/background pairs;
keep helper captures and the final OpenAI narration private and gitignored.


## Latest user instruction: script only for now

The presenter deferred voice and video generation to a later task. Complete the
private script, pauses and choreography now; do not generate speech or a new video.
The current script is served at `/rehearsal` with a Markdown download at
`/rehearsal-script`; all helping materials remain gitignored. Preserve prior aids.


## October 28 revision: optional architecture appendix

Move Server architecture, The API request and context, and Response and loop closure
out of the main sequence. Preserve these three frames as optional appendix A1–A3
after the research-transfer conclusion. Main: 19 frames / 73 reveals, 21:40 plus
45s reserve. Appendix: 3 frames / 12 reveals, optional 2:35. Keep the concepts,
algorithms, three demos and framework definition central. Browser advancing stops
at the main conclusion; explicit controls open the appendix and return to the prior
main frame. Update the shared-source PDFs, notes and private script in the same order.
No model calls, audio/video generation, commit, push or deployment are needed.
