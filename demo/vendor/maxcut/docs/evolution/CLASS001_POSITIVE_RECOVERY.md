# Positive100000 evaluation recovery

Prepared October 21, 2026 after the user reported all six graphs stopped.
**Not Slurm-verified yet. No new job, public run or model call was submitted.**
The October 21 22:30 CDT public cutoff has expired. These changes do not extend
it, change old receipts, reset expenditure, or resume any graph automatically.

The latest positive100000 campaign is
`staging/class001_large_v1/runtime/evolve/campaigns/rand_pos_100000_s42_class001_search_v5_01`.
Its verified checkpoint has cut362136, score0.9620205121644385, eight model
calls, and6487.4 active seconds consumed. Round2 had valid120s comparisons.
Round3's model plan requested35 aggregate seconds. Verification/setup/return
reserves left7.710s for the worker, and all executed candidates timed out in
preparation. The existing guard correctly blocked more paid proposals.

## Implementation and version boundary

The separate controller under `staging/class001_positive_floor_v1/source/`
rejects proposals below120 aggregate seconds for the two measured class001
100000-node profiles. It exposes `minimum_trial_seconds` in model context,
rejects short plans before writing artifacts, and checks direct schedule
creation too. The existing bounded single correction can explain the rejection.
Zero-work plateau responses, novelty checks, upper trial limits, aggregate
verification reserves, solver caps and cumulative spending remain enforced.
Other graph profiles retain their own budgets. This is a minimum aggregate
allowance, not a new proposal-count cap or a promise of target attainment.

Original root sources and every earlier runtime/source seal remain unchanged.
Stopping jobs does not permit changing their pinned bytes and old hashes.

The preparation job is gated by a passing report for the exact sealed new
source/support bundle. It builds a separate runtime, verifies the original
parent and every closed-round file, and requires the pending round to be an
untouched planning checkpoint. It preserves complete parent history, the best
independently verified labels, all model/solver counters, stagnation and consumed
active time, including preparation costs. It keeps the existing active-time
ceiling: a new wall window does not replenish that allowance.

New ID: `rand_pos_100000_s42_class001_search_v6_01`.
New runtime: `staging/class001_positive_floor_v1/runtime`.
Manifest: `evolve/configs/class001_positive_recovery_v1.json` inside that runtime.

Its explicit round-zero recovery measures the previous admitted candidates,
rebased onto the new source identity, at120s each, with a common frozen starting
assignment. Previously unlaunched schedule entries are included. The full
default portfolio catalogue and BM restart remain available. Prior admissions
and raw source bytes are retained in the copied history; inherited candidates
receive no novelty credit. All new fitness is from new measured trials. If no
candidate is selectable, it stops before new model calls. Old failed trials
remain failures. It then uses the ordinary controller with the enforced floor.
All four ancestor locks, their identity/history checks, and the new campaign's
own lock prevent competing continuations. A changed ancestor or partial existing
destination blocks preparation rather than being overwritten.

## Next action: generated verification only

Run from the ORIGINAL repository root, not a nested runtime:

```bash
cd /home/grads/m/mahmudulhasantamim/engr-689/projects_github/bipartite/bipartite-mahmudulh-tamim
export CLASS001_PYTHON_MODULE=''
export CLASS001_EXTRA_MODULES=opensn/gcc/15.2.0-fortran
export CLASS001_PYTHON=/usr/bin/python3.11
mkdir -p logs/slurm
sbatch --parsable --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=00:25:00 \
  scripts/class001_positive_repair.sbatch verify
```

This runs policy/migration fixtures, two actual full-path comparisons on a
generated positive100000 graph with500000 edges at120s, and existing controller
regressions. No public graph optimization or real model call occurs. Small
fixture failures are explicitly synthetic migration inputs, not claimed public
timing evidence. Full-size probes retain generated inputs, worker logs, phases
and independent official scorer receipts. Admission-floor, zero-work plateau,
upper budget, novelty, incumbent/history/counter retention, expired cutoffs and
ancestor descriptor tests must pass. Old numerical kernels are inherited from
the previously verified candidate3; they are not modified here.

Evidence is printed at job start under
`evidence/class001/positive-floor-JOBID.SUFFIX/`. Check:

```bash
sacct -j "$job_id" --format=JobID,State,ExitCode,Elapsed
cat logs/slurm/maxcut-positive-repair-"$job_id".out
cat logs/slurm/maxcut-positive-repair-"$job_id".err
```

Set `job_id` to the number sbatch returned. A passing job writes
`verification.json` next to its generated-probe report and logs. Retain failed
reports. Do not use a receipt from a different source/support revision.

## After verification passes: prepare, without running the graph

Set `positive_proof` to that exact passing verification.json pathname, then:

```bash
sbatch --parsable --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=00:10:00 \
  scripts/class001_positive_repair.sbatch prepare "$positive_proof"
```

Preparation verifies the old incumbent using the unchanged scorer inside Slurm.
It does not run search or call a model. Existing/partial runtime directories
must be reviewed explicitly; neither preparation nor verification cleans them.

## Public continuation needs a new user-selected window

After successful preparation, the `run` action accepts an explicit future stop
epoch. No default public cutoff is supplied. Choosing/submitting a new window
is the user's action; the expired22:30 command must not be reused.

```bash
export PATH="$HOME/.vscode-server/extensions/openai.chatgpt-26.1007.21434-linux-x64/bin/linux-x86_64:$PATH"
read -r -p 'New stop time (YYYY-MM-DD HH:MM:SS, America/Chicago): ' positive_stop_time
positive_stop_epoch=$(TZ=America/Chicago date -d "$positive_stop_time" +%s)
sbatch --parsable --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=01:45:00 \
  scripts/class001_positive_repair.sbatch run "$positive_stop_epoch"
```

The deadline reserves120s for orderly cleanup; Slurm's wall limit also applies.
The saved active allowance may end the campaign earlier. Before preparation it
has only about979s remaining; preparation and re-evaluation consume that same
allowance. This does not authorize another105 active minutes or extend Torus.
All other five campaigns remain stopped. Public source/admission/fitness errors
can still block a later round; they are not automatically bypassed.

The unified read-only monitor automatically selects the new positive ID only
after its complete transition marker exists:

```bash
/usr/bin/python3.11 -I -B scripts/class001_all_status.py --details
```
