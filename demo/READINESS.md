# Verified local teaching status — October 28, 2026

Open **http://127.0.0.1:8766/** on the computer running the server. Start it from
the repository root with `python demo/server.py --port 8766 --rounds 3` and keep
that terminal running. This is loopback access, not a publicly deployed server.
Port 8765 belongs to another application and has been left alone.

## Current teaching materials

- 19 main frames / 73 reveals: title, evolutionary algorithms, LLM mutation,
  solver mechanisms, three demos and the formal tuple. Three architecture/API
  frames / 12 reveals follow in an optional appendix.
- 21:40 main content plus 0:45 reserve; optional appendix adds 2:35. Demo windows are 3, 3 and 4 minutes, including
  discussion and inspection. No artificial computation fills those windows.
- Aggie Maroon, dark body/code text on white, white navigation/title text and
  legible disabled controls. All 85 rendered states passed fit, image and answer
  overlap checks. The measured minimum text contrast was 7.68:1.
- One server hosts presentation, mounted demo, algorithm examples, exact exchange,
  architecture, notes, a 22-page handout and 85-page optional reveal PDF.
- The separate architecture PDF explains module ownership, routes, request
  construction, actual context, validation, scoring, selection and cancellation.

## Replacement comparison and actual evidence

The default is `rand_pm_1000_s23.txt`: 1000 vertices, 5043 signed edges, reference
1098 (unproven). It replaces the easy torus's ceiling effect. Explicitly normalized
classroom seed programs, common raw starts and seeds 3/4/5 give medians:

| Solver | Median |
| --- | ---: |
| Simulated Annealing | 921 |
| Tabu Search | 975 |
| Breakout Local Search | 992 |
| Rank-two Burer–Monteiro | 1012 |

Burer–Monteiro is strongest here. The earlier BM-only torus control was not a
universal initialization recommendation. The limited preset now checks Tabu
Search and Simulated Annealing. The informed preset checks Tabu Search, Breakout
Local Search and Burer–Monteiro. All four kernels remain available to Luna.

| Genuine source | Initial / final eligible median | Best witness | Calls | Time | Outcome |
| --- | --- | ---: | ---: | ---: | --- |
| Limited: `674ece0b…` | 975 / 1008 | 1031 | 2 | 24.003s | Finished, reference not reached |
| Informed: `52948263…` | 1012 / 1012 | 1060 | 2 | 66.589s | Failed after ineligible parent reference |
| Dense: `166aa16a…` | 402.3824 / 402.5209 | 402.5209 | 3 | 56.602s | Reference matched after one call |

The informed run's high-scoring children were incomplete and could not rank. Its
second public response named an ineligible parent; validation stopped the run.
The stronger start did not establish a faster or more effective full search.
Neither replacement run reached 1098. Do not present an inevitable efficient-win
narrative. Failed replay sources remain visibly FAILED; transport-only failures
cannot qualify as genuine recordings.

The dense real-weight case has 100 vertices and 4950 edges, reference 402.5209
(unproven). It matched all three trials at 16.091s after one call. Similar edge
counts with different density, degree and weights make this a separate transfer
test; no universal difficulty ordering is asserted.

## Budgets, provenance and verification

All nine original revision calls and six additional attempts are used. Two of the
six failed at sandbox DNS before provider contact and are preserved. Four real
replacement calls then completed. No unused allowance remains; there are no
silent retries, numerical fallbacks or altered recorded responses.

The server permits up to three calls, 35s each, two children and three stages;
8s per current numerical trial, 240s run deadline and cleanup by 250s. Guided gates
consume that deadline. The older torus keeps its own 1.5s protocol and records.

The earlier approved real-provider Stop test remains valid: source `7d038c3c…`,
real public stream opened, owned client stopped with exit -15 at 9.952s, no
completed result and no remaining owned-process marker. This does not prove
immediate remote billing cancellation.

Prior core offline suite: 29 tests passed. All 14 preserved Burer–Monteiro tests and
all 133 source hashes passed. Prospective public files and existing history were
scanned without credential findings. Updated PDFs were rendered and visually
reviewed; architecture and notes passed text-margin checks. Browser checks cover
preset counts 2/3/4, shared initial results, genuine failed replay, exact return
frame, read-only exchange and contrast. The prior core checks are in `evidence/replacement25-verification.json`; current appendix/navigation checks are in `evidence/appendix_revision_verification.json`.

Raw witnesses, transcripts and practice aids stay ignored. No commit, push,
deployment, assignment-solution import or reviewer panel was performed. Old
critique rounds and original vendor files remain unchanged.

## Remaining presenter and voice actions

The **human aloud rehearsal** is still a presenter action. Use Rehearse aloud,
teach the whole sequence and save its timing JSON under ignored demo/rehearsal/.
A clock or generated voice cannot certify the presenter's delivery.

The private script is complete at `/rehearsal`, with a Markdown download at
`/rehearsal-script`. It includes 85 reveal segments, question pauses, exact view
transitions, actual replay outcomes and adaptable live wording. Voice and video
generation are **deferred at the user's request**; no OpenAI speech request was
made. Earlier 15-minute private aids remain historical and unchanged.
