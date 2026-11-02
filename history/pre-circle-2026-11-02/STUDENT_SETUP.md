# Student and agent setup guide

Use this guide to launch the presentation and signed Max-Cut solver demonstration
on your own computer. You can follow the commands yourself or give the agent
prompt near the end to a coding agent.

The supported environment is **Linux, including Windows through WSL**, with
**Python 3.11 or newer** and Git. Run the commands below in a Bash terminal.
The cancellation mechanism depends on Linux process information, so native
Windows and native macOS execution are not covered by these instructions.

You do not need an API key to view the presentation or run numerical-only mode.
Live Luna proposals require your own TAMU API key. The bundled presentation and
PDFs let you start without Pandoc, LaTeX, Node.js, or `just`.

## 1. Clone the course branch

Use the branch your instructor has published for class. The commands below use
`Tamim-dev`, the current tutorial branch. Substitute the instructor's branch if
it differs.

```bash
git clone --branch Tamim-dev https://github.com/AgenticDevelopmentDiscovery/nec-25-llm-evolutionary-search.git
cd nec-25-llm-evolutionary-search
python3 --version
```

Confirm that Python is at least 3.11. If you already have a checkout, enter that
directory and preserve any local changes rather than cloning over it or resetting it.

## 2. Create a local Python environment

From the repository root:

```bash
python3 -m venv demo/.venv
source demo/.venv/bin/activate
python -m pip install -r demo/requirements.txt
```

The requirements file installs NumPy and Requests. No native solver compilation
is required. If your system reports that `venv` or `ensurepip` is unavailable,
install the venv package matching your Python installation; on Ubuntu/Debian this
is commonly `python3-venv`. Then repeat this step.

## 3. Prepare private settings

```bash
cp -n demo/.env.example demo/.env
chmod 600 demo/.env
git check-ignore demo/.env demo/.venv/
```

The copy command preserves an existing `.env`. The final command should print
both paths, confirming that Git ignores them.

For **numerical-only mode**, leave the API key blank and continue to step 4.

For **live Luna proposals**, open `demo/.env` in your local editor and fill in
your own key. Keep these TAMU settings:

```dotenv
DEMO_LLM_PROVIDER=tamu
TAMUS_AI_CHAT_API_KEY=YOUR_OWN_KEY
TAMUS_AI_CHAT_MODEL=protected.gpt-5.6-luna
TAMUS_AI_CHAT_API_ENDPOINT=https://chat-api.tamu.ai
```

Replace `YOUR_OWN_KEY` locally. Create a key through your
[TAMU Chat account](https://chat.tamu.ai/); the
[TAMU API-key guide](https://docs.tamus.ai/docs/prod/api-tool/create-and-test-api-key)
provides additional instructions. Your account must have access to the selected model.

The filled `.env` belongs only on your machine. Do not paste a key into an agent
conversation, source file, screenshot, issue, or commit. The public
`.env.example` must remain a blank template. Restart the server after changing
settings. Existing shell environment variables take precedence over `.env`.

## 4. Check the setup without contacting a model

```bash
python demo/server.py --check
```

This verifies the reference solver snapshot and reports local model configuration.
It makes **zero API requests**. With a blank key, live access being unavailable is
expected. A report that API access is configured does not test account quota or
make a successful live request.

If a reference snapshot hash fails, stop and report it. Do not edit
`demo/vendor/maxcut/` or bypass verification.

## 5. Start the server

```bash
python demo/server.py --port 8766 --rounds 3
```

Keep this terminal running. On the same computer, open:

**http://127.0.0.1:8766/**

For WSL, run the server inside WSL and open the address in your Windows browser
using the usual WSL localhost forwarding. The service listens only on your own
computer; it is not a public website or a classroom-wide server.

If this repository's server is already running on that port, the command prints
its URL and reuses it. The existing process keeps its Python environment and
settings. To change those settings, stop that process in its original terminal
with **Ctrl+C**, then launch it again.

If another service occupies the port, leave it alone and use:

```bash
python demo/server.py --port 8767 --rounds 3
```

Then open **http://127.0.0.1:8767/**. Do not kill unrelated processes to free a port.

## 6. Complete a numerical-only check first

1. Open **Demonstration** in the presentation's navigation bar.
2. Select a demonstration preset or check the initial solvers you want.
3. Select **Numerical only** as the mode.
4. Click **New Run** to apply the staged settings.
5. Click **Evaluate numerical preset**.

Confirm that the page says **NUMERICAL ONLY**, trial values populate, and model
calls remain **0**. This mode evaluates the selected initial programs and a
disclosed fixed numerical comparison program. Luna does not generate its proposal.

Each solver is tested three times. With base seed 3, the trial seeds are 3, 4,
and 5. Checkboxes select the initial population; all four supported algorithms
remain available for a later live Luna proposal.

## 7. Run a live experiment when requested

After configuring your own key and restarting the server:

1. Choose the graph/preset and initial solver checkboxes.
2. Set **Live LLM**, then click **New Run**.
3. Click **Evaluate initial solvers**. This step performs numerical evaluations.
4. Inspect the surviving programs and trial results.
5. Click **Send selected parents to Luna** to initiate a real API request.
6. Inspect the streamed proposal, validation, child trials, and selection.
7. Continue only for the number of calls you intended to use, or press **Stop**.

The standard server allows up to **three model calls per run**, with a
35-second timeout per request and no automatic retry. Guided pauses count toward
the run deadline. Model requests use your account's access and usage allowance.

For the exact outgoing request and public response, open **Luna exchange**.
Authorization headers and API keys are excluded from that view.

Keep the three modes distinct:

| Mode | What happens | New model calls |
| --- | --- | --- |
| Live LLM | Luna generates new solver-program proposals | Up to the configured run cap |
| Numerical only | Existing numerical algorithms and a fixed comparison program execute | 0 |
| Recorded LLM replay | An available, verified genuine recording is played back | 0 |

Private instructor recordings are not included in a public clone. Replay being
disabled on a fresh clone is expected. Earlier recordings keep their original
execution behavior; they are not new measurements of a changed solver.

## 8. Return later or stop

To stop the server, press **Ctrl+C** in the terminal that owns it. The demo's
**Stop** button stops the current experiment while leaving the server running.

On a later visit, from the repository root:

```bash
source demo/.venv/bin/activate
python demo/server.py --port 8766 --rounds 3
```

If `just` is installed, `just demo` is an optional equivalent after activating
the environment. It is not required for the setup above.

## Editing frames, if assigned

Edit `sections/*.prose.md`; `.concepts.md` files are supporting notes and do not
render into the presentation. Keep the paired concepts consistent when changing
the teaching content.

Install Pandoc before editing rendered content. With Pandoc available, saving
prose rebuilds the browser presentation and HTML notes; the open presentation
checks for updates every two seconds. Questions and answers are optional, and
each question/block/answer Div present becomes a reveal. Keep frame IDs and
`data-seconds` attributes on the `##` headings. Refresh an open Notes page to read
its updated HTML.

If rebuilding fails, the previous slides remain visible with an error notice.
Fix the reported source problem and save again. A manual browser rebuild is:

```bash
python demo/build_presentation.py
```

PDF regeneration additionally needs the authoring toolchain described in
[README.md](README.md), including LaTeX and `just`. Use `just build`, then reopen
the PDF. Python code or `.env` changes require a server restart.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| `ModuleNotFoundError: numpy` or `requests` | Activate `demo/.venv` and install `demo/requirements.txt` with that environment's Python. |
| `venv` / `ensurepip` unavailable | Install the venv support package for your Python version, then recreate the environment. |
| `just: command not found` | Use the direct Python launch command; `just` is optional for running the demo. |
| Port already in use | Reuse the identified tutorial server or choose port 8767. Changing Conda environments does not stop an existing server. |
| Browser cannot connect | Keep the server terminal running and use its printed port on the same computer. |
| Live access unavailable with a blank key | Select Numerical only, or configure your own TAMU key locally and restart. |
| Wrong provider/model reported | Check for shell environment overrides and confirm the server was restarted after changing `.env`; do not print key values. |
| Provider rejects a live request | Read the displayed error, check account/model access, and preserve the failed result. Do not silently substitute replay or automatically repeat requests. |
| Saved prose does not appear | Save a `.prose.md` file, check the presentation's error notice, and ensure Pandoc is installed. |
| Replay unavailable | A fresh public clone does not contain the instructor's private run recordings. |
| `unknown run ID` after restarting | The old server session ended. Saved records remain local; use New Run, or an available verified replay. |

## Copy this prompt to your coding agent

```text
Set up and launch this repository's local classroom presentation and solver demo.

Read AGENTS.md and STUDENT_SETUP.md first. Read CODEX_DEMO_HANDOFF.md for current
implementation context. Preserve local edits and all existing private settings.
Do not commit, push, deploy, run a reviewer panel, or change demo/vendor/maxcut/.

Use the instructor's published course branch. If already inside a checkout,
inspect its state and do not switch branches or reset changes without direction.
Confirm Linux/WSL and Python >=3.11. Create demo/.venv if needed and install
demo/requirements.txt there. Copy demo/.env.example only if demo/.env is absent,
set its permissions to 600, and verify Git ignores the private file and venv.
Never read out, print, paste, or log API-key values. Leave the public template blank.

Default budget: ZERO model calls. Complete setup and numerical checks without
waiting for an API key. If I later request live execution, use only the explicit
call allowance I provide; do not retry failed requests automatically. If a key
is missing, tell me how to enter it locally rather than asking me to paste it.

Run python demo/server.py --check using the venv. Start the local server on 8766
in a persistent terminal/session. Reuse a recognized instance; do not interrupt
active work. If another service owns the port, choose an available port instead.

Verify the presentation, Demonstration, Algorithms, and Luna exchange pages load.
If browser tools are available, complete a Numerical only run and confirm its
mode label, populated trials, and zero model calls. Otherwise report exactly
which startup/page checks you could verify and which browser check remains.

Report the Python version, check result, URL/port, running status, mode tested,
actual model-call count, and how I can stop/restart the server. Do not claim live
Luna access or a successful model run from a configuration check alone. If your
environment cannot keep the process alive, say so and give me the exact command.
```

Example follow-up after you have entered a key privately:

> Run one Live LLM experiment with at most three Luna calls. Keep the graph,
> base seed and solver suite I select. Preserve unsuccessful proposals and report
> actual calls, complete-program fitness and best-witness score separately.

## Note for the instructor before distributing the repository

Students receive only files in the published branch. Include the current demo
code, graph data, reference snapshot, blank environment template, and generated
files under `demo/static/` in that branch before sharing it. Local uncommitted
fixes are not delivered by a clone. Keep `.env`, virtual environments, run logs,
private replays, and presenter practice materials ignored.

Publishing remains a separate instructor action; these setup instructions do
not ask a student or agent to commit, push, or deploy this tutorial.
