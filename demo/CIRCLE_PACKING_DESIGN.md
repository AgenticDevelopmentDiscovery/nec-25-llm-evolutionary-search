# Circle packing: implemented task and protocol

The active task uses AlphaEvolve Appendix B.12 exactly as a mathematical problem:
N=26 or N=32 disjoint variable-radius circles in a unit square, maximize Σr.
The source-generation controller is a classroom implementation, not the
unpublished AlphaEvolve engine. No reported answer coordinates are embedded.

## Mathematical contract

Each returned witness has exactly N finite [x,y,r] triples. Require r≥0,
r≤x≤1−r, r≤y≤1−r, and pairwise center distances ≥r_i+r_j. Tangency and
zero radii are allowed; zero-radius count is reported. Sum of radii differs
from covered area and from a common-radius objective. The independent server
checker recomputes all constraints and summed radii within tolerance 1e-9.
Floating checks are not exact-arithmetic certificates.

## Artifact and initial programs

The evolved artifact is actual Python source defining solve(initial,seed,steps).
It receives a copy of the common incoming center bank, a numerical seed and a
requested work count. The worker supplies np, math, radii(centers) and report.
Luna returns source and a hypothesis; Python executes the source, not the prose.

The disclosed initial programs are Perturbed Grid Constructor, Greedy Local
Center Search and Simulated Annealing of Centers. Their source is in
packing_programs/. All use the same radius allocator. Fixed-center radii solve
a linear program: maximize Σr subject to r_i+r_j≤d_ij and wall upper bounds.
SciPy HiGHS handles that subproblem with a common 1e-8 construction margin.
The centers remain a nonconvex search problem. These initial methods are our
classroom baselines, not methods claimed to have been discovered by AlphaEvolve.

## Iterative refinement and fairness

The default follows the paper’s described iterative construction refinement:
retain the best valid packing per numerical seed. Freeze those centers as the
incoming bank for the next round, re-evaluate the surviving programs on it,
and give the child copies of that same bank. A bank identity accompanies every
evaluation. Select only within that round’s bank. Old-bank fitness remains
history; cumulative best-construction progress is a different curve.

The fixed-start option keeps the original seeded perturbed grids throughout.
It is useful for stable program comparisons. Switching protocols creates a new
run. Seeds 3/4/5 are defaults, not special mathematical values or model seeds.
The per-trial hard allowance is 8 seconds, including isolated startup. Requested
steps are 80. Report actual radius calls and elapsed time; equal caps do not
imply equal effort.

## Proposal, execution and selection

A real response contains round_id, parent_ids, hypothesis and source. Mutation
requires actual survivor IDs; independent generation requires no claimed parent.
Validate syntax/signature and duplicate source identity before execution. Source
is mounted nowhere in the host server: it enters a separate Bubblewrap worker
on stdin. That worker has no host network, repository, .env, run logs or private
home, only read-only runtime libraries and its own temporary filesystem.
No unsandboxed fallback exists. API credentials are only available to the separate
provider worker. Geometry is checked again by the controller outside generated code.

All three trials must complete and validate for a program to have eligible fitness.
Rank by median, minimum and stable identity; retain up to three complete programs.
A worse-than-champion child can still fill another slot. No island or explicit
semantic diversity policy is implemented. Valid partial constructions may be
archived without granting their program complete fitness.

## Two demos and evidence

Demo 1 evolves programs for 26 circles. Demo 2 uses the 32-circle published case.
Each has three explicit model gates and a 240-second whole-run cap. Provider
requests time out at 35 seconds. Stop/Reset cancel owned work; reconnect cannot
start another request. The guide explains methods, API ownership and data flow.
The interface shows source, diffs, packing source/seed, trials, bank IDs, exact
public exchange, failures and cumulative construction progress.

LIVE LLM, NUMERICAL ONLY and RECORDED REPLAY stay labeled. Genuine replay uses
registered provider responses and verified geometry; no fabricated fallback is
allowed. Raw run files remain ignored. See READINESS.md for actual results.

Sources: [AlphaEvolve report](https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/AlphaEvolve.pdf),
[public results repository](https://github.com/google-deepmind/alphaevolve_results),
[SciPy radius LP interface](https://docs.scipy.org/doc/scipy/reference/optimize.linprog-highs.html).

## Instructor-aligned teaching refinements

The user reports that the instructor suggested circle packing; there is no
requirement to recreate the old assigned demonstration or give a lineage survey.
The current guide adds a numerically verified flawed-scorer toy and a separate
post-search check of frozen initial/evolved programs on new seeds 101–103.
Sources were chosen before those scores were inspected. See
evidence/packing_validation_sources.json and packing_heldout_validation.json.
These checks use common fixed starts, not the inherited construction bank.
No new model requests occur. The guide also explains MAP-Elites, novelty and
quality–time trade-offs as extensions; production ranking remains unchanged.
