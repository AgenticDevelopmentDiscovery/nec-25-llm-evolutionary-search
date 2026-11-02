# Local circle-packing classroom

The active tutorial follows Chapter 10 and uses the 26- and 32-circle unit-square
problems from AlphaEvolve Appendix B.12. We evolve actual Python packing programs
using TAMU Luna and independently evaluate their geometry. This is our bounded
classroom loop, not the unpublished AlphaEvolve engine or its reported result.

## Launch

Use Python 3.11+ on Linux or WSL. In a virtual environment:

```bash
python -m pip install -r demo/requirements.txt
# Ubuntu/WSL, if missing:
sudo apt-get install bubblewrap
python demo/server.py --port 8766
```

`just demo` automatically uses demo/.venv when that environment exists.
The current limits are in packing_profile.json.

Open http://127.0.0.1:8766/ for the presentation, /packing for the demo,
/algorithms for worked methods, /architecture for data flow, /notes for notes,
and /handout.pdf for final-state frames. The hub switches to the same running
demo and returns to your frame. `just demo 8767` uses another port if needed.
Never kill an unidentified listener. Python backend changes require restarting
your server; saved prose updates automatically when Pandoc is available.

If an older open tab reports **write token required**, hard-refresh it once
(Ctrl+Shift+R) to load the current client. This is the local server's control
token, separate from your Luna API key. Reconnecting tabs now share a stable
run token. The client refreshes expired credentials after a server restart and
retries only a write explicitly rejected before execution. Completed runs and
their comparisons remain available; reconnect never starts a model request.

## Your own private key

Copy `.env.example` to ignored `.env` inside demo/, then edit locally. Select
TAMU and enter your own key in TAMUS_AI_CHAT_API_KEY. Use model
protected.gpt-5.6-luna. Do not paste keys into chat, commit them, put them into
source or share raw provider records. See ../STUDENT_SETUP.md for the steps.
Only the blank template belongs in the repository.

## Modes and controls

A **trial** is one execution of one unchanged packing program, from one starting
packing with a numerical random seed and limits. It can contain many **search
steps**, each proposing a center change and deciding whether to keep it. Three
trials use default seeds 3, 4 and 5. Every competing program receives the same
three starts, seeds and limits. All three trials must complete and validate;
their median score is the primary program fitness, with higher values preferred.
A **model round** instead asks Luna for a new program and evaluates it. See
/algorithms for the worked explanation of movement size, move acceptance and
the distinction between a step, trial, round and full run.

NUMERICAL ONLY is the default and evaluates disclosed source programs with zero
API calls. LIVE LLM evaluates parents, then waits for an explicit button for
each real Luna request. RECORDED REPLAY plays a verified genuine source run;
it makes no new requests. Failed proposals do not trigger free retries.

Choose 26 or 32 circles, initial programs, seeds, a one-to-three call cap,
parent-conditioned or independent proposals, evidence-rich or structure-only
context, and inherited or fixed numerical starts. These controls allow exploratory
experiments; a controlled ablation must also freeze identical parents/history.

Default inherited starts retain the previous best packing for each trial seed.
Parents and child are re-evaluated from the same frozen bank each round. Only
bank-comparable complete scores enter selection. The separate curve tracks the
best verified construction. Checkboxes select P0, not the full source search space.

## Offline checks and editing

```bash
python demo/server.py --check
python -m unittest discover -s demo/tests -v
python demo/check_public.py --history
just build
just overlays
```

No check above sends a model request. Isolated numerical execution needs both
SciPy and working Bubblewrap namespaces; it fails closed when unavailable.
Edit sections/*.prose.md and matching concepts sidecars. Each ## heading is a
frame; question/block/answer Divs create sequential reveal slides. Notes Divs
supply detailed explanations. Keep Chapter 10 frame counts and two demo slots.

Read ARCHITECTURE.md, PRESENTATION_PLAN.md, CIRCLE_PACKING_DESIGN.md and
READINESS.md for the executable contract, timing and actual verification.
Historical teaching sources and all previous evidence remain preserved separately.
Do not commit, push, deploy or run the reviewer panel without explicit instructions.

## Additional numerical teaching checks

The algorithm guide includes an instructor-made flawed-scorer example and
separate fixed-start evaluation of frozen programs on seeds 101–103. Run
`python demo/validate_frozen_programs.py` to reproduce that numerical check
without an API key. The original live rounds used seeds 3–5. New validation
scores never enter those recorded mutation requests or their survivor ranking.
Behavioral archives, novelty and cost scalarization are teaching options, not
implemented policies. The source selection, trial results and limitations are
in evidence/packing_heldout_validation.json.
