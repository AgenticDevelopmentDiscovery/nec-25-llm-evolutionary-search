# Student and agent setup

This repository serves a Chapter 10 tutorial and two circle-packing demos.
The problems are N=26 and N=32 variable-radius circles in a unit square,
maximizing summed radii. The implementation evolves Python search programs.

## 1. Clone the instructor-published branch

```bash
git clone https://github.com/AgenticDevelopmentDiscovery/nec-25-llm-evolutionary-search.git
cd nec-25-llm-evolutionary-search
# Only after the instructor publishes this branch:
git switch demo/concept-aligned-experiments
```

A local, uncommitted branch is not available to students until the instructor
publishes it. Do not silently substitute an older branch and expect the new demos.

## 2. Create an environment

Use Python 3.11+ on Linux or WSL. Ubuntu/WSL also needs Bubblewrap:

```bash
sudo apt-get install python3-venv bubblewrap
python3 -m venv demo/.venv
source demo/.venv/bin/activate
python -m pip install -r demo/requirements.txt
```

The numerical requirements are NumPy and SciPy; requests supports the TAMU API.
Generated source runs only in Bubblewrap. If namespace support is blocked by your
system, execution stops with an explanation; do not bypass isolation to run LLM code.
Pandoc/TeX are optional for viewing bundled materials and required for rebuilding
PDF exports. The authoring toolchain is Pandoc, XeLaTeX, librsvg/ImageMagick and just.

## 3. Verify without a key or paid request

```bash
python demo/server.py --check
python -m unittest discover -s demo/tests -p test_packing.py -v
python demo/server.py --port 8766
```

Open http://127.0.0.1:8766/ for the presentation, /packing for the demo,
/algorithms for methods, /architecture for the architecture, and /notes for notes.
Select NUMERICAL ONLY and evaluate the initial programs. All three seeds must
return feasible packings before their program gets eligible fitness.

Keep the terminal running. Use Ctrl+C there to stop your server. If the port is
occupied, open your identified existing server or use `--port 8767`. Never kill
an unidentified listener. Saved prose updates automatically; Python changes need
a server restart. A stale backend cannot acquire new routes by refreshing a tab.

## 4. Add your own TAMU key locally

```bash
cp demo/.env.example demo/.env
chmod 600 demo/.env
```

Edit demo/.env in your editor. Select DEMO_LLM_PROVIDER=tamu and place your own
key in TAMUS_AI_CHAT_API_KEY. Keep TAMUS_AI_CHAT_MODEL=protected.gpt-5.6-luna.
Do not paste your key into chat or source. The file is ignored; the committed
example has no key. Do not remove the ignore rule or share private run folders.
Restart your server to load the saved settings. The browser never receives the key.

## 5. Run the live experiment

Select LIVE LLM, a published circle count and initial programs. Default trials
use seeds 3/4/5; the seed determines numerical randomness, not model output.
The default three-call cap is per run, not permission for an agent to spend money.
Agree an API budget with your instructor before letting an agent run requests.

Start evaluates initial programs. Each model request then waits for Send context
to Luna. Inspect the sent body, public response, actual source and parent diff.
The worker executes the code; the server checks every wall and circle pair and
recomputes summed radii. Three complete trial scores determine eligible fitness.

Inherited-start mode freezes the previous best packing for each seed and tests
parents and child from that same bank. Fixed-start mode keeps original starts.
Do not mix fitness from different banks. Stop cancels owned work; reset creates
a new run; refresh reconnects without another paid call. Replay needs an existing
genuine source recording and stays labeled RECORDED REPLAY.

## 6. Editing and an agent instruction

Edit the saved sections/*.prose.md and corresponding *.concepts.md. Each ## is
a frame; question/block/answer Divs reveal one after another. Notes Divs hold
detailed explanations. With Pandoc available the browser refreshes saved content.
Use `just build` and `just overlays` for updated exports.

```text
Read AGENTS.md, CLAUDE.md, CODEX_DEMO_HANDOFF.md and DEMO_REDESIGN_HANDOFF.md.
Inspect git status and preserve existing work. Set up a local environment from
demo/requirements.txt and verify the circle-packing demo numerically first.
Never print keys, expose private logs, bypass Bubblewrap, fabricate live output,
or spend model calls without a stated allowance. Keep Chapter 10 sources, notes,
server pages and PDF exports consistent. Do not commit, push or deploy.
```

## Extra numerical illustration

After setup, `python demo/validate_frozen_programs.py` evaluates the included
frozen source programs on fresh starts, with zero API calls. Read /algorithms
for the flawed-scorer reveal, actual validation table and the distinction between
implemented top-three ranking and optional diversity/cost policies.
