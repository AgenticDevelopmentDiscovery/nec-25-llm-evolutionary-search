# Class001 cluster session: published results and engineering work

The class001 session deployed and ran the six expensive graph campaigns on the
Orchard class node without sudo. The user selected explicit resources and
submitted the search jobs; solver work, builds and numerical verification ran
inside Bash Slurm allocations. On the user's later explicit instruction, the
best verified retained assignments were consolidated into the real `solutions/`
directory. No GitHub repository visibility change is part of this publication.

## Result in the real solutions directory

After remote reconciliation, the unchanged official scorer reports
**0.9879417376062763**, up from **0.9765192125551918**. All 18 assignments are
valid. Seven cuts improved and no cut decreased. Rung scores are 1.0,
0.9999999999999999, 0.9951586502449752, 0.9821276971083209 and
0.9624223406780855. These are the scorer's actual floating
values; scores were not clipped or rounded into target attainment.

| Graph | Previous public cut | Published cut | Official graph score | Last saved search state |
| --- | ---: | ---: | ---: | --- |
| `rand_pm_100000_s43.txt` | 112269.0 | 114219.0 | 0.9650584130518854 | awaiting_codex |
| `dense_gauss_1000_s24.txt` | 12080.5474 | 12204.8867 | 0.9814802669418458 | awaiting_codex |
| `rand_pos_100000_s42.txt` | 360535.0 | 362136.0 | 0.9620205121644385 | evaluation_blocked |
| `torus_pm_316_s41.txt` | 63888.0 | 66408.0 | 0.9601880968179327 | wall_budget_exhausted |
| `rand_pm_10000_s33.txt` | 11121.0 | 11392.0 | 0.9755910869195441 | awaiting_codex |
| `rand_pos_10000_s32.txt` | 36395.0 | 36395.0 | 0.9771093051950814 | awaiting_codex |

Positive 10000 already had its retained best cut 36395 in the real public folder.
Its completed searches did not improve that cut. All six expensive graph scores
remain below 1. These are verified feasible assignments, not new proofs of
optimality or proof that a campaign reached its target.

The incoming laptop update supplied two additional public improvements, retained
alongside the five cluster improvements:

| Graph | Previous public cut | Final published cut | Official score |
| --- | ---: | ---: | ---: |
| `torus_pm_100_s31.txt` | 6392 | 6878 | 0.9936826992103374 |
| `torus_pm_32_s21.txt` | 728 | 732 | 1.0 |

The other eleven assignments did not lose cut value. The initial cluster-only
publication scored 0.9830097949799796; the final combined publication below
scores 0.9879417376062763.

Publication job **59864** passed four generated assignment-only tests, then
independently loaded and scored all candidates using the original graph bytes.
It considered 13 explicitly selected cluster campaign directories across the
original, search-v4, metadata-v1 and large-v1 runtimes, plus the portable starting
labels, retained experiments and previous public solutions. Exact finite-decimal
cut sums selected the winner for each graph. Zero candidate sources were rejected.
No solver or model ran during consolidation. Existing archive digests and
metadata were checked; campaign locks were held without changing their metadata.
Replaced labels and sidecars were backed up before publication.

- [Final official published scores](../../evidence/class001/publication-59865.qq796u/consolidated/public_scores.json)
- [Before-publication scores](../../evidence/class001/publication-59864.TFQvbW/consolidated/public_before_scores.json)
- [Final selected sources and snapshot hashes](../../evidence/class001/publication-59865.qq796u/consolidated/selection.json)
- [Final completed publication receipt](../../evidence/class001/publication-59865.qq796u/consolidated/publication_receipt.json)
- [Actual released solution hashes](../../evidence/class001/session-20261021/released_assignments.json)
- [Old public assignments and sidecars](../../evidence/class001/publication-59864.TFQvbW/consolidated/public_before/)
- [Saved six-campaign outcomes and cumulative counters](../../evidence/class001/session-20261021/campaign_outcomes.json)

The first publication attempt 59863 stopped at new fixture assertions comparing
`1` with canonical `+1` byte spelling, before touching real solutions. The checks
were corrected to compare assignment values. Its failed logs are retained;
59864 reran all checks successfully. This did not weaken an archive hash,
objective, sandbox or source-integrity check.

After fetching and merging the laptop commit, job **59865** passed ten distinct
relevant generated checks: four multi-runtime publication checks, five incoming
annealing experiment tests, and the existing consolidation regression. The
publisher reran its four checks before final publication. Both branch snapshots
and the incoming retained-label snapshot were available as candidates. Final
official scoring reproduced 0.9879417376062763 on all 18 real public files, with
no decrease from any cluster result and zero rejected sources. Existing valid
label bytes are preserved on ties by the verified writer; a canonical snapshot
can therefore spell `+1` where the real file retains `1`. The separate released
hash inventory records the actual public bytes without rewriting old receipts.
See [Git reconciliation](CLASS001_GIT_INTEGRATION.md) and its
[Slurm verification receipt](../../evidence/class001/integrated-publication-59865.LfQvrh/verification.json).

## Deployment and scheduling work

The checkout was reconciled with the incoming suite-v3 work while retaining its
cluster adaptations. The session established a usable Python 3.11 environment,
resolved module/compiler compatibility and added an explicit compiler wrapper
for the relevant native build. It preserved the existing portfolio, official
input graphs/references/scorer, portable starting labels and historical evidence.
No administrator privileges or system installation were used.

Slurm scripts now require explicit task, CPU, memory and time choices. The user's
campaign allocation was one node, two task slots times five CPUs, and 15 GiB per
array element. Six simultaneous elements request 60 logical CPUs and 90 GiB in
total; extra allocated CPUs do not make serial candidate kernels parallel.
Host `nproc`/`free` output was not treated as an allocation. The controller starts
once per array element, not once per Slurm task. Shell/Python/module/preflight
commands, array manifests and a unified six-root checkpoint monitor were prepared.

Dependencies, process ownership, Bubblewrap sandboxing, native MPI and source
identity were checked through bounded Slurm jobs. Failed checks were retained,
then repaired and rerun rather than being hidden by changing old manifests.
Remote/main integration and deployment notes remain in the class001 command,
blocker and handoff documents.

## Numerical/controller repairs and their verification

The session found and addressed several distinct limits and failure modes:

- Controller active-window handling now preserves cumulative time/call spending,
  supports intentionally unset round/solver-count ceilings, and reserves time for
  verification and finalization. Timing-v3 removes the old fixed five-second
  scorer ceiling and 50-percent worker ceiling inside the same aggregate trial
  allowance. Owned process cleanup records unreaped survivors as a failure.
- The old annealing path injected a 10000-proposal fallback. A separate source
  revision supports time-based cooling when no work cap is requested, explicit
  fixed-work cooling telemetry and honest censoring of incomplete schedules.
  A reproducible calibration/comparison driver was prepared; no unrequested
  public comparison experiment or paid model call was substituted for validation.
- Cluster workers now use direct sandboxed local kernels with absolute deadlines
  and durable phase events. Trusted controller graph caching is deeply immutable
  and rehashes original bytes; numerical workers retain graph-mutation checks.
  Controller return/setup overhead is reserved separately from the unchanged
  verification-reserve receipt. Optional annealing polish respects measured
  initialization/return cost and cannot turn an incomplete schedule into a pass.
- Continuation metadata uses a canonical campaign identity. Source versions,
  full histories, verified starting labels, all usage counters and ancestor
  locks are preserved across reviewed continuations. Source/fitness failures
  remain distinct from operational model capacity errors and wall exhaustion.
- Exact-solver shutdown/output handling was investigated with generated fixtures.
  A recovered native assignment, an incumbent fallback and an optimality proof
  remain separate. SMS source/binary were absent here, so real SMS-native recovery
  is not claimed verified.

The final large-worker candidate passed **59849**: six repair test methods and
**twelve complete generated full-path comparisons**, covering signed and positive
graphs with 100000 nodes and 500000 edges, plus dense graphs with 1000 nodes. All comparisons returned valid,
selectable labels and official scoring within their aggregate allowance. Job
**59850** passed 172 existing controller/search/portfolio/suite/deployment tests.
Total: 178 test methods, with the 12 comparisons inside one of those methods.
Previous failed candidates 59846/59847/59848 and their source snapshots remain
preserved locally; their failure summaries are retained with the handoff.

- [Combined exact-bundle verification](../../evidence/class001/large-v1-59849.K4PG4x/release_verification.json)
- [Full campaign repair and failure chronology](CLASS001_LARGE_COMPLETION_REPAIR.md)
- [Annealing/native-recovery revision](CLASS001_SEARCH_V4.md)
- [Cluster command and dependency record](CLASS001_COMMANDS.md)

## Stops, remaining limits and unverified work

All six search jobs were stopped before this publication. Four campaigns stopped
on model plateau or failure to admit a novel child; Torus exhausted its active
allowance. Positive 100000 reached `evaluation_blocked`: its round 2 had successful
120-second comparisons, but a later model plan selected 35 aggregate seconds, leaving
only 7.710s for worker preparation after verification/setup/return reserves. All
executed comparisons timed out. The guard correctly prevented another paid
proposal before useful numerical evidence existed.

The positive minimum-budget repair is **prepared, not Slurm-verified**. It uses a
new isolated controller source version, advertises and enforces 120-second aggregate trials
for the measured large profiles and prepares an explicit recovery screen of the
previous four admitted candidates. It retains the old failures, full history,
verified best labels and all spending. It has not been run on public graphs and
must not be described as a successful recovery. See
[the positive recovery guide](CLASS001_POSITIVE_RECOVERY.md).

The user's final public cutoff was October 21 at 22:30 CDT, with 120s reserved for
cleanup. Its extension was separately authorized/tested in 59855; old receipts
were not rewritten. That window expired and publication did not restart search
or renew budgets. Positive 100000 had only 979.3 active seconds left before
further preparation, rather than a newly replenished 105-minute allowance.

## What is retained in Git and locally

The handoff commits the published assignments, source changes and isolated
source overlays, Slurm/experiment/monitoring scripts, tests, this report, and
selected validation/publication receipts. Bulky runtime copies, raw campaign/model
transcripts, generated test repositories, environments and native builds remain
local. They are not erased or silently replaced. A verified private backup of
87034 pre-publication local-work files and the tracked patch was made outside the
checkout before Git integration. The official graphs, references and evaluator
were not changed to improve reported scores.

The user explicitly authorized this publication and Git handoff. Earlier
instructions forbidding automatic publication/commit/push applied to search
execution; they do not negate this later explicit request.
