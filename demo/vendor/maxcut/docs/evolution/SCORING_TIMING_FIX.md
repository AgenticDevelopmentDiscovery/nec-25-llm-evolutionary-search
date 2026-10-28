# Scoring timing policy and preserved timing-v2 history

## Current class001 runtime v3 (prepared October 21, 2026)

The user stopped all six campaigns after array 58565 and requested removal of
unnecessary limits. V3 removes the independent five-second scorer deadline and
the fixed 50% numerical ceiling. Every trial retains its aggregate deadline.
Before numerical execution it reserves min(30s, max(1s, half the trial)); numerical
execution can use the rest after setup. Scoring can use ALL remaining aggregate
time, including time returned by early worker completion. This gives screening
up to 90 numerical seconds within 120 aggregate seconds and ordinary class001
trials up to 30 within 60 seconds. Preparation, parsing and cleanup still count.
Saved-witness recovery reserves up to 60s from the remaining campaign budget,
charges actual time, uses zero new solver slots and earns no comparison credit.
Policy hashes distinguish measurements and cache entries across the boundary.

Owned cleanup now allows five seconds to confirm descendant exit after SIGKILL,
retaining all ancestry/start-tick checks. A real survivor remains a blocking
`cleanup_failed` state with raw receipt and active registration. Root reaping is
bounded; recovery refuses further work while recorded survivors remain live.

`scripts/migrate_class001_runtime.py` is the explicit four-source revision:
common/controller/evaluator/portfolio_external. Its shared migration engine
archives exact before/after source and checkpoint bytes, verifies all frozen
inputs/base/archive, preserves counters and held reservations, and journals each
publication. The revision directory is `source-revisions/class001-runtime-v3/`.
Existing partial ordinary comparisons are censored and replayed with fresh IDs,
retaining admitted children/model plans and all previous cost. Old screening
measurements retain their old identities; they are not relabeled as v3.

The user-submitted `class001_setup.sbatch repair-runtime` runs controller,
portfolio, deployment and generated-fixture smoke checks BEFORE migrating the
six stopped IDs. It launches no public optimization and makes no model calls.
User job 58571 passed runtime verification and migrated all six selected IDs:
99 controller, 23 portfolio and 16 deployment tests plus fixture smoke. Saved
state and usage are unchanged and all migration receipts were checked. See
[the current commands](CLASS001_COMMANDS.md). Existing failed receipts and old
manifests are retained; no budget, numerical base or public label is reset.

## Historical timing v2

The remainder records the earlier timing-v2 migration and its original contract.
Its 50%/five-second limits are superseded by v3 only across an explicit source
boundary. Do not use the old timing-only migration for the suite/runtime upgrade.

After the torus32 scoring failure, the user requested a permanent fix, then
stopped both other controllers and explicitly authorized changes to the unpinned
root controller. The fix is now integrated into `evolution_controller.py`,
`evolution_evaluation.py` and `evolution_common.py`. There is one execution engine;
ordinary root resume and the compatible create-or-resume launcher use it.

The old t0007 worker took 4.1168s of its 5s aggregate trial, leaving under 0.8832s
for scoring independently measured at 0.9257s. Its original scorer outcome was
not saved, so the precise historical timeout/exit classification remains unknown.
See [the diagnosis](../../evidence/solution_status_review/README.md).

## Timing and diagnostics

Trial seconds still mean aggregate end-to-end seconds, including setup, numerical
work and verification. Numerical execution receives at most 50% of that limit,
and less if setup has consumed the reserved verification window. Verification
reserves at least 1s when the aggregate limit permits, up to 5s. The numerical
allowance is bounded by both the half-budget ceiling and the remaining deadline.
The policy hash is in cache conditions. Immutable `timing-tNNNN.json` records
show the numerical allowance, reservation and aggregate limit. The remaining
trial time also covers independent exact metrics and source checks.

At the timing-only release, default/class001 screening changed from 5s to 15s.
Current suite-v3 production profiles use 120s screening and 30s admission;
ordinary trials default to 30s (the class001 cluster override is 60s).
This provides conservative startup room, not a measured optimum.
Existing checkpoint configurations and scheduled total seconds remain unchanged.
No finite allowance guarantees completion under arbitrary machine contention.
Actual overruns remain visible and cannot earn fair comparison credit.

The unchanged official evaluator receives only its remaining verification
allowance (at most 5s). Preparation/copying and output parsing count. Each
attempt retains `score_request.json`, `score_process.json`, raw streams and its
fresh `score-N` directory, including failure details:

- `verification_timeout`: allowance exhausted during preparation, execution or parsing.
- `verification_failed`: scorer launch, nonzero exit or malformed output.
- `integrity_error`: changed protected data or an actual target/score disagreement.
- `interrupted`: user stop or interrupted execution.

Saved worker output can be verified again without repeating search or asking
Codex. Recovery first reconciles old reservations conservatively, then reserves
and charges a separate verification operation of at most 5s, with zero new solver
slots. Such an observation is `verification_recovery`, excluded from selection
timing credit, but its independently verified feasible witness may improve the
monotone archive. Target thresholds, proof status and official scoring are unchanged.

## Explicit migration of stopped checkpoints

`migrate_evolution_timing.py` acquires the campaign kernel lock and refuses
active owners or changes outside the three reviewed source files. It checks
frozen inputs, numerical base and exact archive before publishing a new contract.
It archives the old campaign record, checkpoint, open round and exact old/new
source bytes under:

```text
evolve/campaigns/<id>/source-revisions/verification-timing-v2/
  before/                 # original campaign/checkpoint/open round; old sidecar if present
  after/                  # prepared new contract and checkpoint
  source_before/
  source_after/
  journal.json            # recoverable, explicitly authorized publication plan
  receipt.json
```

The old numerical base, immutable candidates, completed trial directories and
closed rounds stay intact. The record increments `source_revision` and links
its history. The script is restartable and idempotent; any unrelated checkpoint
or source edit during interrupted migration is refused. Historical branch-based
campaigns are not migrated. Other old isolated IDs require this explicit step
before root resume, or a fresh ID; source guards are not disabled.

For an ordinary open comparison, all old schedule/observations are retained in
the revision evidence and censored from the new selection table. Its existing
proposal, admitted children, completed admission checks, frozen incumbent and
repeat seeds are reused. Phase returns to `admitting`, then the entire same
parent/child comparison is scheduled with fresh IDs under the new policy. No
new model proposal is requested for this replay. Prior spending is retained and
new measurements consume remaining quotas. The initial screening round may
retain old completed observations across the explicit boundary; their original
conditions are not relabeled as v2 evidence.

The three local manifest campaigns are migrated by this maintenance task:

- torus100: pending round 23, planning; no comparison to replay.
- signed random1000: pending round 24, evaluation; replay its whole comparison
  with fresh IDs after retaining the old seven observations and prepared slot.
- torus32: pending initial screening; retain the separately repaired t0007
  verification, old failed scorer attempt and nonselectable recovery status.

The earlier additive runtime and its torus32 marker are retired and archived
as development history. They are not a second supported execution path.
Campaign counters, active seconds, best assignments and the user's saved
2500-slot/36000-second/250-call caps remain intact. The local round caps remain
200/200/20. No public label, project commit or remote job is produced here.

To migrate another compatible stopped isolated ID explicitly:

```bash
uv run python scripts/migrate_evolution_timing.py --campaign-id NAME
```

To resume the three prepared local campaigns concurrently:

```bash
uv run python scripts/evolve_campaigns.py batch \
  --campaigns evolve/configs/parallel_sparse.json --jobs 3
```

Each campaign continues to use its own results, checkpoint and logs. A second
owner is refused. See [verification evidence](../../evidence/scoring_timing_fix/README.md).
