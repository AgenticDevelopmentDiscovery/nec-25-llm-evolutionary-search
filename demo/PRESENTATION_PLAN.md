# Chapter 10 presentation plan

The title is followed by two circle-packing problem frames and two prerequisite
frames explaining numerical search and trials, then the requested Chapter 10
conceptual frames and five frames supporting two demonstrations.
The former pre-demo problem definition now belongs to the opening. A frame is a teaching unit. Each revealed
question, mechanism block or answer is another overlay slide of that frame.
Derive counts from sections/ and presentation.json; never enforce four reveals.

| Portion | Frames | Planned seconds |
| --- | ---: | ---: |
| Title | 1 | 20 |
| Circle-packing rules and objective | 2 | 90 |
| How a program searches; what a trial means | 2 | 120 |
| 10.1 The evolutionary loop | 2 | 120 |
| 10.2 Mutation operators | 3 | 180 |
| 10.3 Selection and population management | 2 | 110 |
| 10.4 Fitness design | 1 | 75 |
| 10.5 Diversity and exploration | 2 | 130 |
| Demo 1: 26 circles, execution and evidence | 2 | 255 |
| Demo 2: 32 circles, including setup and evidence | 3 | 300 |
| Reserve | — | 45 |
| Optional architecture/API appendix | 3 | 155 |

Main: 20 frames, 23:20 planned + 0:45 reserve = 24:05. Architecture/API appendix
is backup material beyond the timed main talk. Showing all of it adds 2:35,
making 26:40 with reserve. Aloud timing remains to be measured by the presenter.

Introduce center, radius, valid packing, summed-radii score, numerical search
step, move scale, move acceptance rule, trial, seed and packing bank before
using them in the framework. The first strategy frame defines population, parent,
child, mutation, selection and fitness in its notes. Keep the four-circle score
example distinct from the measured 26- and 32-circle demonstrations.

Every conceptual frame begins with a question, followed by mechanism and answer
reveals. Ask, pause roughly five seconds, then reveal. Notes explain each step
and distinguish course concepts from implemented features. Islands and tournament
selection are concepts, not hidden features of the live controller.

## Demo choreography

From demo-circle-a open the integrated demonstration and stage N=26. Choose
LIVE LLM, three calls, mutation, evidence context and inherited packings. Confirm
initial program checkboxes. Evaluate P0, inspect source and current bank, then
explicitly release each of three model calls. Follow the public source stream,
diff, geometry, three complete trial scores and selected survivors. Inspect how
the next context incorporates results. Return to the evidence frame.

From demo-circle-b stage N=32 and Stop/reset into a fresh run. Repeat the three
rounds. Do not compare raw sums across circle counts. Use the final evidence
frame to identify (A,f,mu,sigma,P0) in the actual run.

Allow 3:30 of each demo sequence for computation and inspection.
Faster computation leaves time to read code and question students. Never add
artificial delays. If using genuine replay, keep its label and source timing
visible. A failed source run remains failed evidence.

## Teaching and publication boundaries

These are exactly the paper’s two unit-square problem formulations. The local
controller, initial programs, model and compute budget differ from AlphaEvolve.
Do not imply record reproduction or optimality. The source evolution is real;
geometry supplies externally checked evidence. No voice/video generation now.

## Current scope and optional depth

The instructor suggested circle packing, as reported by the user; literal use
of the old assigned demo and a lineage survey are not targets. Preserve the
2/3/2/1/2 frame allocation and two three-round demos. The three added concepts
fit existing frames: flawed scoring/held-out checks, behavioral archives/novelty,
and a worked quality–time trade-off. The guide supplies more detail without
adding a third main demo. Its scorer reveal and fresh-start results are explicitly
numerical-only, with zero additional model calls. The runtime still uses top-three
quality ranking, not novelty, MAP-Elites, Pareto selection or a cost penalty.
