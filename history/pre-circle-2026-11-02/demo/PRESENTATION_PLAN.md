# Browser-first teaching plan: main presentation and optional appendix

Teach evolutionary optimization and the LLM mutation operator, instantiate signed
Max-Cut and solver mechanisms, observe three demos, then formalize the framework.
The main conclusion ends with research transfer. Architecture and API internals
are optional appendix material for questions or follow-up.

There are **19 main frames / 73 overlay slides**, followed by **3 appendix frames /
12 overlay slides**. The title is one state; other frames reveal a question, two
blocks and an answer. Aggie Maroon and the existing high-contrast design remain.

The main plan is **21:40 plus 0:45 reserve (22:25)**. The optional appendix adds
**2:35**; presenting it as well uses the full 25-minute allowance including reserve.

| Main clock | Frame |
| --- | --- |
| 0:00–0:20 | 1. Evolutionary search with a language-model mutator |
| 0:20–1:00 | 2. Optimization as search |
| 1:00–1:40 | 3. Population and fitness |
| 1:40–2:25 | 4. Variation, evaluation and selection |
| 2:25–3:05 | 5. Exploration and exploitation |
| 3:05–3:50 | 6. The language-model mutator |
| 3:50–4:35 | 7. Signed Max-Cut |
| 4:35–5:15 | 8. Local moves and feasible witnesses |
| 5:15–6:00 | 9. Solver programs |
| 6:00–7:10 | 10. Four numerical algorithms |
| 7:10–7:50 | 11. Initial population and fair starts |
| 7:50–8:25 | 12. Designing the three experiments |
| 8:25–11:25 | 13. Demo 1: a limited initialization |
| 11:25–14:25 | 14. Demo 2: a researcher-selected suite |
| 14:25–15:15 | 15. Comparing the evidence |
| 15:15–19:15 | 16. Demo 3: a dense real-weight stress case |
| 19:15–20:00 | 17. Reading solver evidence |
| 20:00–21:00 | 18. The agentic evolutionary framework |
| 21:00–21:40 | 19. Applying the framework to research |
| 21:40–22:25 | Reserve |

| Optional appendix clock | Frame |
| --- | --- |
| 0:00–0:45 | A1. Server architecture |
| 0:45–1:45 | A2. The API request and context |
| 1:45–2:35 | A3. Response and loop closure |

## Server choreography

Run `python demo/server.py --port 8766 --rounds 3` and keep the terminal running.
Open http://127.0.0.1:8766/ on that computer. Right/Space reveals; Left reverses;
D switches between the presentation and mounted demo; F requests full screen.
Returning preserves the exact frame/reveal and existing run. Normal advancing stops
at the main conclusion. Use **Appendix →** or the Optional appendix group in the
frame picker for A1–A3; **Main presentation** restores your prior main frame.

For each demo, stage its preset, confirm checkboxes and mode, use New Run, then
Evaluate initial solvers. Checkboxes choose P0 only: unchecked kernels remain
available to Luna. The first two presets keep graph, seeds and numerical allowance
fixed; only their seed suite differs. The dense third case is a separate task.

Inspect survivors at every gate, press Send N parents to Luna, inspect actual
request context and public response, then observe validation, trials and selection.
There are three rounds/calls per case; no automatic retry or early stop at target
in this teaching profile. Stay within the controller's 240-second deadline and
250-second cleanup limit. Model timeout is 35 seconds per call. Use time left in
each guided segment for explanation after the run closes; do not idle at a gate.

## Evidence to teach

The easy torus has been replaced by the 1,000-vertex signed random graph, because
its normalized seed-program medians separate: Simulated Annealing 921, Tabu
Search 975, Breakout Local Search 992, rank-two Burer–Monteiro 1012. The supplied
reference is 1098, unproven. Both comparisons use identical raw starts and seeds
3/4/5. Both current graphs allow 8s numerical trials.

Limited preset: Tabu Search + Simulated Annealing; informed preset: Tabu Search +
Breakout Local Search + Burer–Monteiro. The old BM-only torus control is preserved
but is not the current demonstration. Checkboxes choose P0 only.

The limited two-call run improved eligible median 975 → 1008, best witness 1031,
and finished at 24.003s. The informed two-call run retained eligible median 1012;
its incomplete children produced best witness 1060. An invalid parent reference
stopped it at 66.589s. Neither reached 1098. Show the failed source as FAILED and
explain why the higher witness did not supply eligible program fitness. Stronger
initial fitness did not guarantee the intended efficient-win narrative.

The dense real-weight case is separate: reference matched in all trials after
one call at 16.091s; the genuine three-call run ended at 56.602s. Graph density
alone does not establish a universal hardness ordering. Teach structure, evidence
and limits rather than equating vertex or edge count with difficulty.

All nine original revision calls and six additional attempts are used. Two of the
six were sandbox DNS failures before provider contact; four were actual Luna
requests. Use genuine recorded replay for further zero-cost practice. Verified
failed sources retain their source failure status; transport-only failures cannot
be presented as model results. Numerical-only mode is separately labeled.

`/algorithms` provides the initial screen, full names and worked mechanisms.
`/exchange` shows the actual request and public return. `/architecture` and its PDF
map server ownership, modules, routes, messages and boundaries. Read-only views
cannot start paid work. Current recordings use two real rounds for each replacement
comparison; the server still permits up to three calls per classroom case.

## Private practice and timing

The current private script is complete at `/rehearsal`, with 85 reveal segments,
question pauses, live alternatives and recorded outcomes. Voice and video are
deferred at the user’s request. Earlier private videos remain historical aids. The Rehearse aloud control downloads actual navigation
timings; save them in that ignored directory. Only the presenter can complete the
human aloud check. A synthetic video cannot certify delivery pace or room response.
The separate real-provider Stop test is already complete and need not be repeated.
