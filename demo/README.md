# Local solver-evolution classroom

Use Linux (or WSL) with Python 3.11 or newer. Owned-process cancellation uses
Linux process start ticks; no native solver build is needed. Start from the repository root:

```bash
python3 -m venv demo/.venv
demo/.venv/bin/python -m pip install -r demo/requirements.txt
cp -n demo/.env.example demo/.env
chmod 600 demo/.env
# Edit demo/.env locally and insert your OWN TAMU key.
demo/.venv/bin/python demo/server.py --port 8766 --rounds 3
```

Leave that terminal running. On the same computer open **http://127.0.0.1:8766/**.
This is a local loopback server; no account login on the server page is required.
The previous port 8765 belongs to a separate application and is left alone.
The public presentation bundle, teaching notes and PDF handout are included, so
students do not need Pandoc or LaTeX to run the server. Authors use `just build` to rebuild PDFs and the browser bundle.

## Daily launch and prose editing

From the repository root, run `just demo`, then open http://127.0.0.1:8766/.
If this repository's server is already running, the command prints its URL and
reuses it. It does not launch a duplicate or stop another process. Changing Conda
environments does not stop an existing server; its interpreter and settings remain
in use until that process is stopped.

Edit and save `sections/*.prose.md`. The running server rebuilds the browser
frames and HTML teaching notes when the source changes. Open presentation tabs
check every two seconds and update the current frame without resetting its reveal
or the mounted demo. No browser refresh or restart is required for prose edits.
Refresh an already-open Notes tab to read its newly built HTML.

If a draft fails validation, the last successful frames remain visible and a
notice explains the error. Correct and save the source to recover. Pandoc is
needed for authoring; unchanged bundled frames still work on student machines
without it. `just presentation` remains available for a manual rebuild.

PDFs are separate exports: run `just build`, then reopen or refresh the PDF.
Python server/configuration changes require restarting the existing process first.
If another repository or an unrecognized service occupies the port, use
`just demo 8767` and open the printed URL. No listener is automatically killed.

## Pages and presenter navigation

- `/` or `/present`: 19 main frames (73 reveals), then 3 optional appendix frames (12 reveals). Right/Space reveals
  one block; Left reverses; D switches demo/presentation; F requests full screen.
- `/demo`: solver population, measured trials, top-three context, public proposal
  stream, mutation diff, admission/rejection and selection. The hub keeps this
  page mounted while you present, preserving the run and exact return frame.
- `/algorithms`: full algorithm names, mechanisms, pseudocode, configurations and
  worked examples. A four-vertex flip example and annealing acceptance slider run
  locally without an API call.
- `/exchange`: exact API request body, controller context, incoming public response
  and parsed result/usage. It follows the existing run and never starts a request.
  Authorization is excluded. Replay reveals responses only at their recorded time.
- `/architecture`, `/architecture.pdf`: responsibility diagram, exact API/data flow, routes, limits and experiment interpretation.
- `/notes`: detailed explanations from the same prose as the presentation.
- `/handout.pdf`, `/document.pdf`: derived frame handout and detailed PDF notes.
- `/rehearsal`: instructor-only local wording/video aids when generated. These
  materials live under ignored `demo/rehearsal/` and are absent from public clones.

A frame contains one idea. Four overlay slides reveal its question, two mechanism
blocks and answer; the title uses one state. Main content is 21:40 plus 0:45 reserve,
including guided demos of 3, 3 and 4 minutes. The optional architecture/API appendix
adds 2:35. Main advancing stops at the conclusion. Use the Appendix button or
frame-picker group to open it, then Main presentation to restore the prior frame.
Use Rehearse aloud and save actual timing JSON under ignored `demo/rehearsal/`.
A navigation clock or synthetic narration cannot certify human aloud delivery.

## Student keys and public-repository structure

Create an individual key at [chat.tamu.ai](https://chat.tamu.ai/), following the
[TAMU key guide](https://docs.tamus.ai/docs/prod/api-tool/create-and-test-api-key).
Use it only in the ignored local `demo/.env`:

```dotenv
DEMO_LLM_PROVIDER=tamu
TAMUS_AI_CHAT_API_KEY=
TAMUS_AI_CHAT_MODEL=protected.gpt-5.6-luna
TAMUS_AI_CHAT_API_ENDPOINT=https://chat-api.tamu.ai
```

The blank `.env.example` is public; a filled `.env` is private. Each student adds
their own key after cloning. Restart the server after changing settings. The key
stays in the Python API client, never in browser JavaScript, request bodies,
exchanges or run records. No shared instructor key is shipped. TAMU and optional
direct OpenAI credentials remain bound to separate fixed HTTPS destinations;
redirects and silent provider fallback are refused. The client has no model tools.

Metadata check, zero generations: `python demo/list_models.py`. The configured
Luna ID was confirmed through TAMU's authenticated metadata. Account availability
and service limits still apply; see [TAMU API documentation](https://docs.tamus.ai/docs/prod/api-tool/api-docs).

Before making the repository public, run `python demo/check_public.py --history`.
Do not force-add `.env`, `runs/`, presenter aids or private replays. Ignore rules do
not remove a previously tracked secret from history; rotate any exposed key.

## Three experiments and solver checkboxes

Choose a preset, inspect the checkboxes and mode, then use **New Run** and
**Evaluate initial solvers**. Editing settings only stages them. Check at least
one algorithm. Checkboxes choose P0 only; Luna may use every trusted kernel.

| Preset | Graph / seeds | Initial suite |
| --- | --- | --- |
| Limited suite | 1000-vertex signed random graph / 3, 4, 5 | Tabu Search + Simulated Annealing |
| Informed suite | SAME graph / SAME seeds | Tabu Search + Breakout Local Search + rank-two Burer–Monteiro |
| Dense stress case | 100-vertex dense signed graph / 3, 4, 5 | All four |

The default graph is `rand_pm_1000_s23.txt`, 5043 signed edges, supplied unproven
reference 1098. It replaces the ceiling-prone easy torus. With normalized classroom
seed configurations, algorithm medians are 921 (Simulated Annealing), 975 (Tabu
Search), 992 (Breakout Local Search), and 1012 (Burer–Monteiro). Burer–Monteiro was
not chosen as a universally weak or required parent: it is strongest in this screen.
The current limited preset uses two local-search algorithms, not BM alone.

The dense case has 100 vertices, 4950 signed real-valued edges and unproven
reference 402.5209. Similar edge counts do not make these graphs equally difficult;
density, degree and weight distribution differ. It is a separate structural stress
test, not a justified universal hardness ranking. Public provenance and selection
justification are in ARCHITECTURE.md. The original torus and its records remain
available as historical evidence.

All current programs and children receive copies of identical raw starts for
seeds 3/4/5. A partition is a **feasible witness**. The population consists of solver
programs; the harness independently rescores original edges and supplies fitness.

1. Evaluate the checked algorithms and inspect up to three complete survivors.
2. Press **Send N parents to Luna**; watch actual context and public chunks.
3. Observe validation, numerical trials, mutation diff and survivor selection.
4. Inspect the next population before explicitly sending the next round.
5. Return to the exact presentation frame and interpret fitness and cost.

The server permits three calls per case; each is bounded by 35s, at most two
children and no automatic retry. Current replacement recordings contain two real
calls each. Run deadline: 240s; cleanup: 250s. Guided pauses consume that deadline.
Each current trial shares 8 numerical seconds across one to three stages; the
historical torus retains 1.5s. Startup is separately bounded. Work caps: 20000 Tabu
Search iterations, 200000 Simulated Annealing proposals, 12000 Breakout Local Search
flips; Burer–Monteiro one solve, 60 sweeps and 16 directions.

Only complete three-trial programs rank: higher median, higher minimum, fewer
stages, stable normalized genome ID. Keep top three; no diversity slot. A censored
trial can leave a valid witness while its program remains ineligible.

**LIVE LLM** makes new paid proposals. **NUMERICAL ONLY** runs a disclosed fixed
program, zero calls. **RECORDED LLM REPLAY** plays a verified genuine source, zero
new calls, persistent source identity/status and separate recorded/playback clocks.
A failed source remains FAILED when playback ends. No mode silently becomes another.
Navigation, comparison reads and reconnecting cannot start a model request.

## Measured replacement evidence

| Case | Initial / final eligible median | Best witness | Calls | Seconds | Outcome |
| --- | --- | ---: | ---: | ---: | --- |
| Limited | 975 / 1008 | 1031 | 2 | 24.003 | Finished, reference not reached |
| Informed | 1012 / 1012 | 1060 | 2 | 66.589 | Incomplete children; invalid parent stopped run |
| Dense | 402.3824 / 402.5209 | 402.5209 | 3 | 56.602 | Reference matched after one call |

The stronger suite improved initial fitness; it did not establish a more efficient
full search here. Incomplete high-scoring witnesses cannot replace eligible fitness.
Neither replacement run reached 1098. These are inspectable bounded observations,
not a scripted guarantee or unseen-instance validation. The 3/3/4-minute demo windows
include questioning and interpretation, not fabricated computation or forced delays.

The six additional authorized attempts are used: two sandbox DNS failures before
provider contact plus four real calls. The earlier nine authorized calls are also
complete. Raw transcripts stay ignored; public evidence omits assignment vectors.

## Verification and rebuilding

```bash
python demo/server.py --check
python -m unittest discover -s demo/tests -v
PYTHONPATH=demo/vendor/maxcut python -m unittest discover -s demo/vendor/maxcut/tests -p 'test_bm_solver.py' -v
python demo/rehearse.py --mode numerical --instance dense_gauss_100_s14.txt
python demo/rehearse.py --mode replay --replay 051251dcd77c4bd4942055114dd45a00 --speed 4
just build
just overlays  # optional 85-page PDF of all reveal states
```

A live rehearsal is a paid request. No unused allowance remains. The current
sources are 674ece0b370441dd9e68c7b53b35eb2d (limited, finished),
529482638cac4e17bca87f8587bc4cf7 (informed, FAILED), and
166aa16ae7c84e309fbed5af73b03b25 (dense, finished). All earlier recordings remain
intact. The separately approved real-provider Stop check passed; closing a client
does not establish immediate remote billing cancellation. Teaching-page visits
and replay spend zero new model calls.

Private narration, script, video and timings belong under ignored `demo/rehearsal/`.
The current 85-segment private script is available at `/rehearsal` and
`/rehearsal-script`. Voice and video generation are deferred at the user’s request.
The script includes live alternatives and exact recorded outcomes. Neither a
script nor future synthetic narration certifies the presenter’s aloud timing.

All 133 hashed vendor files stay unchanged. No commit, push, deployment, assignment
solution import or reviewer panel is part of this workflow.
