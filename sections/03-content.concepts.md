# Claims
- Retained downstream Burer–Monteiro stages lift/perturb/refine the incoming partition; initial/fresh Burer–Monteiro calls remain unchanged. Older replays preserve original behavior.
- Replacing a solver starts a new program from common raw labels; composing retained stages passes partitions within that program's trial.
- Programs comprise one to three trusted stages with configuration, work and start rules.
- Tabu Search, Simulated Annealing, Breakout Local Search and rank-two Burer–Monteiro use distinct mechanisms and work units.
- Checkboxes choose only the initial population; all four kernels remain available to Luna.
- The initialization comparison fixes the 1000-vertex signed graph, seeds 3/4/5, raw starts, trial allowance and mutation space; seed-suite size changes initial evaluation cost.
- Validation precedes numerical execution; complete-trial ranking differs from best-witness retention.
- Current normalized seed medians are 921, 975, 992 and 1012; reference 1098 is unproven.
- Limited suite is Tabu Search + Simulated Annealing; informed suite adds the stronger relaxation/escape programs, using Tabu Search + Breakout Local Search + Burer–Monteiro.
- Six additional authorized attempts are exhausted: two DNS failures and four real calls.
- Limited run improved eligible median 975 to 1008; best witness 1031; 24.003s and two calls.
- Informed run retained eligible median 1012; censored children left best witness 1060; invalid parent ID stopped it at 66.589s after two calls.
- Neither comparison reached 1098; stronger initial fitness did not establish superior full-run efficiency.
- Dense case remains separate: reference matched after one call at 16.091s, three-call run 56.602s.
# Decisions
- Keep benchmark sizes and unproven reference targets in experiment/demo setup; the Signed Max-Cut frame first explains conflicting preferences and score calculation.
- Keep the main sequence on solver programs, numerical algorithms, initialization, three demos and their evidence; architecture/API details move to the appendix.
- Reserve 3min + 3min + 4min for the three demos, within 21:40 main content + 0:45 reserve; optional appendix adds 2:35.
- Report primary median, stronger all-trial criterion, numerical effort and continued three-call cost separately.
- Preserve all earlier recordings, failed calls and immutable vendor hashes; current scenarios use explicit raw-start protocol.
- A separate architecture document maps ownership, routes, context and data flow.
# Open questions
- Human aloud timing remains a presenter action; a prerecorded voice cannot certify it.
- No unseen-graph generalization or causal model-versus-numerical advantage established.
# Not doing
- New paid calls beyond the exhausted approved call allowances, silent fallback, fabricated trajectories, arbitrary generated code or answer-vector publication.
