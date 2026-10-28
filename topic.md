# Topic

## In one sentence

An evolutionary algorithm improves solver programs; a language model supplies mutations and independent signed Max-Cut evaluation determines survival.

## Promise and course connection

Introduce ordinary evolutionary optimization, population, inheritance, fitness, exploration and selection before introducing the LLM as a mutation operator. Instantiate the loop with signed Max-Cut; explain the algorithms, bounded representation and fair starts; observe three experiments; then define Chapter 10's five components and recurrence rigorously.

Students should distinguish a program, its solution witness and measured fitness; explain each of the four numerical kernels; inspect the exact sent context and public response; and reason about initialization, completeness, cost, references and generalization.

## Current scope

- 19 main frames / 73 reveals; title then questions, two mechanism blocks and answers. Three optional architecture/API appendix frames add 12 reveals.
- 21:40 main content plus 0:45 reserve, including guided demos of 3, 3 and 4 minutes. Optional appendix: 2:35. Main content and demos precede the architecture explanation.
- Aggie Maroon base, high-contrast body text, white title/nav text and legible inactive controls.
- Default comparison: supplied 1000-vertex, 5043-edge signed random graph, reference 1098 unproven. Same raw starts and seeds 3/4/5 in both conditions.
- Limited suite: Tabu Search + Simulated Annealing. Informed suite: Tabu Search + Breakout Local Search + rank-two Burer–Monteiro. Checkboxes choose P0 only; all kernels remain available to Luna.
- Separate dense real-weight stress case: 100 vertices, 4950 edges, reference 402.5209 unproven. No universal difficulty ordering asserted.
- Three-call server cap; two real calls in each replacement recording, three in the preserved dense recording. 8s numerical trials, 35s model calls, 240s run deadline / 250s cleanup.
- One local server hosts every teaching view, exact exchange, architecture, notes and derived PDFs. Private script, voice, video and timings are ignored.
- No arbitrary code, new numerical kernels, solution publication, deployment, commit, push or reviewer panel.

## Evidence and limits

Normalized seed medians are 921, 975, 992, 1012. Burer–Monteiro is strongest here; the earlier BM-only torus seed was a pedagogical control, not a general initialization principle.

Limited replacement: median 975 → 1008, best witness 1031, two calls, 24.003s. Informed replacement: eligible median 1012 → 1012, best witness 1060 from incomplete children, two calls, 66.589s, stopped by invalid parent reference. Neither reached 1098. Stronger starting fitness did not establish a superior full search. Dense preserved source: reference matched at 16.091s after one call; three-call run 56.602s.

All nine initial revision calls and all six additional attempts are used. Two additional attempts were blocked by sandbox DNS before provider contact and are preserved. Valid failed sources may be replayed with explicit FAILED provenance; transport-only failures cannot masquerade as model evidence. Original-edge rescoring, complete-trial selection, real Stop evidence, immutable vendor hashes and old critique rounds remain intact.

## Open questions

- Actual presenter's aloud timing within 25 minutes.
- Equal-budget comparisons on unseen graphs, initial-suite sensitivity and diversity.
- Model-context changes that reduce invalid parent references without silently repairing output.
