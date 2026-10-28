# Suite v3: domain-aware validation and broader sparse search

The user authorized stopping Torus100 gracefully before installing this source
version. Its retained cut at that boundary is 6838. Original public assignments,
BM kernels, official graphs/references and earlier immutable campaign bases stay
unchanged. New continuation IDs use the new code and fresh screening; old IDs
are history tied to their original source version.

## Correctness and integration fixes

- SMS partitions are validated and mapped in O(n) time/storage. Sets are built
  once, invalid/duplicate/missing IDs are rejected and original node order remains.
- MQLib's actual `-l` output accepts case-sensitive identifiers containing lower
  case letters, including `PALUBECKIS2004bMST1`. The previous uppercase-only
  expression silently excluded that documented native identifier.
- General methods retain all eight original signed fixtures and the local trap.
  Any toroidal stage instead receives eight supported signed/zero-edge 3×3 and
  4×4 periodic fixtures. False cuts, caller mutation, graph changes and invalid
  labels still fail. Unsupported topology is not mislabeled incorrect output.
  Tiny topology/dynamics admission work is capped at two units per fixture;
  comparative target trials retain their declared full work/time budget.
- Fresh production profiles use **120 aggregate seconds for every screened
  configuration**. Runtime v3 reserves up to 30s for verification, allowing up
  to 90s for numerical execution after setup. It removes timing v2's fixed 50%
  numerical ceiling and five-second scorer ceiling; scoring uses the remaining
  aggregate time. Existing campaigns require the explicit reviewed source migration.
  Admission has 30 aggregate seconds, shared across eight checks. Ordinary
  comparisons remain 30s by default. All screening candidates receive equal
  declared limits; exact algorithms are not ranked on longer hidden allowances.
  These are startup/search allowances, not claims of exact completion or tuning.
- The MQLib baseline and three explicit variants are separate content-addressed
  initial candidates: `BURER2002`, `PALUBECKIS2004bMST1`, `FESTA2002GVNSPR` and
  `MERZ2002KOPT`. Planning and initialization use the same deduplicated config
  enumeration. Variants count toward real solver slots and cumulative wall time.
  FESTA GVNSPR and MERZ KOPT have conservative 10000-node configuration guards:
  their repeated full-coordinate scans/path relinking are not assumed scalable
  to 100000 nodes. Such exclusions remain explicit in planning.

## New methods and their mathematical limits

### `toroidal_window`

This bounded small-window method is inspired by
[Khoshbakht and Weigel, section II.3](https://arxiv.org/html/1710.01670v3).
It validates the original row-major periodic grid, selects wrapping windows of
width at most L−2 and holds all outside spins fixed. A boundary edge contributes
$w_{ij}(1-s_i s_j)/2$. Its variable term is represented by a ghost spin fixed to
+1 with weight $w_{ij}s_j$. Aggregated boundary weights and the constant offset
preserve the conditional objective. The augmented planar graph is solved by the
existing signed matching algorithm. Complementing the augmented answer restores
ghost=+1. Only rescoring on the entire original graph accepts an improvement.
Both original periodic seams remain present.

Storage is O(n+m+window²), with a default window side of 8, configurable up to
24 and a separate parity-defect guard of 256. The global expanded-dual limit of
4096 is unchanged. Large tori can use bounded windows without allocating a
399424-vertex NetworkX matching problem. Exact conditional windows do not prove
a global optimum: `upper_bound` is null and status is `unproven`. This is a
readable small-window variant, not a reproduction of the paper's tuned large
window protocol or its reported success probabilities.

### `pt_icm`

This implements paired replicas at each temperature, Metropolis sweeps, adjacent
temperature swaps and low-temperature disagreement-cluster moves following the
[Houdayer/isoenergetic-cluster formulation](https://arxiv.org/html/1501.05630v2).
For $H=W-2F$, a move with cut gain g has Metropolis ratio exp(2βg). A temperature
swap has log ratio $2(\beta_a-\beta_b)(F_b-F_a)$.

A connected disagreement component is flipped in both same-temperature replicas;
the sum of their energies is conserved. Global complement symmetry reduces
trivial system-spanning disagreement sets. The default has eight temperatures,
two replicas each, and storage O(nT+m). Work counts full tempering cycles;
partial cycles and actual proposals are recorded. This uses the supplied weights,
not regenerated random couplings. It is a heuristic search implementation with
null global bound, not an equilibrium or exactness certificate. The independent
Python implementation adds no Rust/PeaPods dependency and makes no PeaPods speed claim.

### `mixing`

[Wang, Chang and Kolter's Mixing method](https://arxiv.org/abs/1706.00476)
optimizes unit vectors by normalized coordinate updates. For field
$h_i=\sum_j w_{ij}v_j$, the update is $v_i=-h_i/\|h_i\|$; a zero field leaves
that vector unchanged. This minimizes that coordinate's contribution to the
vector objective. Warm signs initialize a noisy rank-one embedding and remain
separately retained. Hyperplane rounding and bounded one-flip polishing produce
feasible original-order cuts.

The default rank is 8, configurable from 2 to 64. Storage is O(nr+m), and work
counts full sweeps. This bounded implementation does not establish the paper's
SDP convergence assumptions. Neither a rounded solution nor an encountered
relaxed value supplies a certified global Max-Cut upper bound. The original
rank-two BM implementation and its random stream are unchanged.

## Continuation and preservation

`scripts/prepare_suite_v3.py --prepare-local` explicitly creates:

- `torus_pm_100_s31_suite_v3_01`
- `rand_pm_1000_s23_suite_v3_01`
- `torus_pm_32_s21_suite_v3_01`

Preparation starts no search or Codex call. It snapshots the strongest validated
known labels for all public graphs into `cluster_inputs/suite_v3_initial/solutions`
without publishing them. Each new ID inherits its parent's consumed solver/model
counters and active time. An ambiguous stopped reservation is charged in full,
as in ordinary recovery. Global solver/time/model caps stay the same; the new
ordinary-round cap is the parent's unused round count. Initialization overhead
is added, not discarded. Historical summary metadata remains in the new model
context, labeled as a different source/timing version.

The parent record/checkpoint and original base identity are saved in each child's
`continuation/` tree. Old closed rounds, source, candidates, results and labels
are never rewritten. New numerical source means new candidate identities and
fresh fair screening; old failed admission is not retrospectively relabeled
passed. The updated local manifest selects these new IDs. Repeating preparation
is idempotent after completion; incomplete inheritance is refused explicitly.

```bash
uv run python scripts/evolve_campaigns.py batch \
  --campaigns evolve/configs/parallel_sparse.json --jobs 3
```

This launches numerical work and potentially paid model calls. Maintenance leaves
all campaigns stopped until the user invokes it. Public results still require
explicit consolidation; no automatic Git commit or push occurs.

## Bounded comparisons and exact backends

A planning-only command creates no run folder:

```bash
uv run python scripts/benchmark_suite_v3.py \
  --instance instances/public/torus_pm_32_s21.txt \
  --initial-assignment cluster_inputs/suite_v3_initial/solutions/torus_pm_32_s21.txt \
  --seconds 120 --output experiments/torus32_suite_v3_comparison_01
```

Add `--execute` to run it. The runner compares the four MQLib variants, applicable
SMS/BiqBin/matching methods and new backends. Native seed/warm restrictions are
honored; unsupported methods are recorded as excluded. Each method gets the
same stated seconds, logs/results stay separate, and the script makes no Codex
request or public publication. A fresh output path is required.

For near-target medium graphs, use the existing SMS or BiqBin one-shot runner
with an explicitly longer limit, for example 900s. SMS accepts a real incumbent;
BiqBin does not accept a warm vector and requires seed 2020. More time may improve
a witness or bound; it does not guarantee exact completion. Keep numerical native
optimality, a separately checked certificate and score-target attainment distinct.

## Cluster operation

The six `class001_large.json` entries have fresh `_class001_suite_v3_01` IDs.
After cluster reconciliation, the class001 config keeps the user's ten-hour
active budget, 250 model calls, nullable round/solver-count caps, 60s ordinary
trials and 60s finalization reserve. Screening/admission remain 120s/30s and
incoming timing policy v2 is unchanged. Config schema version 2 for nullable
caps is distinct from that timing-policy version. See the concrete
[class001 verification commands](../evolution/CLASS001_COMMANDS.md).
The class profile uses the new screening/admission settings, all eligible methods
and all four MQLib configurations where their guards permit. Its validated portable seed snapshot
remains `cluster_inputs/class001_initial`; local v3 continuations separately use
the newer private snapshot. The node/expanded-size guards are unchanged.

Submit through the existing Slurm Bash scripts. CPU/task and RAM placeholders
remain user decisions; no sudo or remote submission is needed for this update.
More allocated cores do not automatically parallelize each numerical algorithm.
Use a checkout dedicated to this source version: never pull changed controller
or solver files into a checkout with active pinned jobs. Run setup/preflight and
bounded smoke checks in submitted allocations before a public campaign. Native
builds, sockets, optional dependencies and Slurm delivery remain host-specific;
local tests do not establish that cluster integration has passed.

[Actual tests and native smoke evidence](../../evidence/suite_v3/README.md).
