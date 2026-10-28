# Other graph recovery — verified wrappers; dense aggregate check pending

**Latest:** dense full-path verification PASSED for the NEW candidate3
completion repair (jobs59849/59850). Use
[the completion guide](CLASS001_LARGE_COMPLETION_REPAIR.md) for dense preparation
and its recovery_v2 continuation. The old other-v1 dense commands below remain
superseded; they lack the subsequently verified optional-polish budget fix.
Capacity/Torus commands here still apply with the restored Codex PATH and
original cutoff. The pending statements below are historical review context.

Reconnection review: job **59842 passed** all 11 prepared tests and its generated
dense worker probe. The matching sealed report is
`evidence/class001/other-v1-59842.hWI1WD/verification.json`. Restore the existing
cutoff **1792638620 (October 21, 22:10:20 CDT)**; never generate a new window.
Capacity/Torus commands below are available. **Defer dense preparation/resume**
until a generated test verifies the full campaign scheduling/official-scoring
path with its real aggregate allowances. The existing direct 30s worker probe
does not test that path. See [the review](CLASS001_SESSION_REVIEW.md).

October 21, 2026. User requests fixes for the four remaining graphs and at most
FIVE more hours because the assignment is due at 23:59 Chicago time. No jobs or
framework model calls have been initiated by the agent. Root pinned sources,
the metadata-v1 runtime, historical hashes and public solutions remain
unchanged. Read the original-root `instruction_Tamim/CLASS001_SESSION_HANDOFF.md`
for current ownership and historical evidence.

Latest incident at 17:08 CDT: both 59839 elements have stopped after all ordinary
trials timed out and their final models returned operational plateau decisions.
They are no longer running. This bundle's dense1000 completion probe does not
verify startup/completion for those 100000-node graphs. Their stopped histories
and cuts remain intact; see `evidence/class001/metadata-resume-59839-outcome/`.

## What is repaired

- Signed10000/positive10000: saved JSONL explicitly reports model capacity.
  The new wrapper prints that primary error before secondary stderr warnings.
  It resumes the SAME original IDs and retries only a newly observed genuine
  capacity failure, at most twice, after 30/60 seconds. Calls and active time
  remain charged by the original framework. Backoff is explicitly recorded
  paused time, bounded by the shared cutoff. There is no model/profile switch,
  syntax/auth/timeout retry or unbounded retry loop. External capacity itself
  cannot be guaranteed by a code change.
- Dense1000: 24 ordinary trials timed out before a nested runner serialized a
  result. A new isolated worker calls the same validated local tabu, BLS, LNS
  and annealing kernels directly inside the existing Bubblewrap sandbox. An
  absolute monotone deadline includes imports/graph loading, and stage budgets
  reserve graph checking/output time. Earlier search-v4 annealing/native fixes
  remain present. A generated 1000-node complete signed graph must produce valid
  eligible tabu AND annealing outputs within each 30-second outer limit before
  production preparation is permitted. This is not an official-graph quality
  claim. If that probe fails, do not prepare/resume; inspect its retained logs.
- Torus316: two saved launcher intervals total approximately 35858 seconds;
  checkpoint usage is 35897.824 seconds (9h 58m 18s), including initialization
  and accounting overhead. Its stop is an exhausted allowance, not OOM. The user
  conditionally authorized an extension and then capped it at five more hours.
  The wrapper adds only the remaining shared window to consumed time, through
  the framework's normal recorded config revision. Calls, trials, prior active
  seconds and best cut remain intact. The deadline is not renewed on retry.

## Bound the entire remaining window

Use one exported absolute deadline for verification, preparation and every new
resume. Generate it ONCE. It is the earlier of five hours from this command and
23:40 CDT on October 21 (19 minutes before the assignment deadline). Queue time
and maintenance consume this same window. Two minutes are reserved for orderly
cleanup. Expired jobs refuse to start; delayed jobs receive only remaining time.
Every optimization allocation also requests at most `05:00:00`. On starting,
its script reduces its own Slurm hard wall limit to the remaining cutoff
minutes (rounded down), then uses a graceful watchdog. If Slurm refuses that
reduction, the script fails before optimization rather than ignoring the bound.

The two 100000-node jobs originally had 10:30:00 limits and are now STOPPED.
Do not issue the earlier limit-reduction commands or relaunch them unchanged.
Check current scheduler state before any future resource/ownership decision:

```bash
squeue -u "$USER" -o '%.18i %.12T %.12M %.12l %.30j'
```

## 1. Restore the already verified session

From the ORIGINAL repository root, retain the known module/Python/Codex exports:

```bash
export CLASS001_PYTHON_MODULE=''
export CLASS001_EXTRA_MODULES=opensn/gcc/15.2.0-fortran
export CLASS001_PYTHON=/usr/bin/python3.11
export PATH="$HOME/.vscode-server/extensions/openai.chatgpt-26.1007.21434-linux-x64/bin/linux-x86_64:$PATH"
export CLASS001_STOP_EPOCH=1792638620
TZ=America/Chicago date -d "@$CLASS001_STOP_EPOCH"
mkdir -p logs/slurm
other_verify_job=59842
```

The job runs 11 new regressions (including the generated dense completion gate)
with no paid calls, Git commits or official graph optimization. Each test uses
fresh generated inputs. It stages a separate checkout and records the exact
source/support identity. The step limit is 900s plus cleanup. Status/logs:

```bash
sacct -j "${other_verify_job%%;*}" --format=JobID,State,ExitCode,Elapsed
cat "logs/slurm/maxcut-other-check-${other_verify_job%%;*}.out"
cat "logs/slurm/maxcut-other-check-${other_verify_job%%;*}.err"
```

Require exit zero, all 11 tests OK, `generated_dense_probe.json` passed and a
matching `verification.json` under `evidence/class001/other-v1-JOBID.*/`.
The report and `stop_epoch.txt` retain the cutoff. After an SSH disconnect,
restore that exact value; do not generate a later deadline. Preparation and
resumes reject a deadline that differs from the verified window.
These 11 tests PASSED in job 59842. Existing 172/16 suites are separate older
verification. No repeat of the unchanged passed tests is needed. Preserve the
source seals; additional full-path dense tests require a separately recorded
verification rather than relabeling the direct worker probe.

## 2. Only after verification passes

Resolve the report belonging to THIS job, preserving the same cutoff export:

```bash
reports=(evidence/class001/other-v1-"${other_verify_job%%;*}".*/verification.json)
if (( ${#reports[@]} == 1 )) && [[ -f "${reports[0]}" ]]; then
  export CLASS001_OTHER_VERIFICATION="$PWD/${reports[0]}"
  printf '%s\n' "$CLASS001_OTHER_VERIFICATION"
else
  printf '%s\n' 'No unique passing verification report; inspect the job.' >&2
fi
```

Capacity and Torus can then resume with unchanged numerical bases in the
ORIGINAL root. These commands can make model calls; the user submits them:

```bash
sbatch --parsable --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=05:00:00 \
  --array=0-1%2 scripts/class001_other_resume.sbatch capacity \
  "$CLASS001_OTHER_VERIFICATION"
sbatch --parsable --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=05:00:00 \
  scripts/class001_other_resume.sbatch torus "$CLASS001_OTHER_VERIFICATION"
```

These are three elements, each 10 allocated CPUs and 15G. With the dense
element below that is up to 40 CPUs/60G; any later large-graph jobs add their own
explicit resources. Site/account availability controls actual
concurrency; queued jobs still obey the original cutoff. Do not claim exclusive
access to host capacity or renew the cutoff to compensate for queuing.

### Dense commands deferred pending full-path verification

The following preparation/resume commands are retained for reference. The
reconnection review identified the missing aggregate completion check above;
do not use them as evidence that dense recovery is fully verified.

Prepare dense separately, with NO optimization/model call:

```bash
other_prepare_job=$(sbatch --parsable --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=00:30:00 \
  --job-name=maxcut-other-prepare \
  scripts/class001_other_repair.sbatch prepare "$CLASS001_OTHER_VERIFICATION")
printf '%s\n' "$other_prepare_job"
```

Preparation holds the old dense kernel lock and verifies all closed evidence.
It preserves the original campaign and copies its complete history into the
new continuation's `continuation/parent_history/`. The new numerical base and
candidate identities are explicit; no old source/base hashes are rewritten.
The new ID is `dense_gauss_1000_s24_class001_recovery_v1_01`, with inherited
best assignment, all counters and active seconds plus actual preparation time.
Fresh screening is necessary for its changed numerical execution contract;
historical failed controls remain history, never comparable new samples.
All original portfolio entries/configuration/guards remain available.

Require preparation exit zero and the completed
`staging/class001_other_v1/runtime/other_transition.json`. Existing/partial
destinations are refused and retained for review; preparation is not a reset.
Only THEN, keeping the SAME cutoff environment, enter the new dense runtime:

```bash
cd staging/class001_other_v1/runtime
sbatch --parsable --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=05:00:00 \
  scripts/class001_other_resume.sbatch dense
```

The dedicated guard holds the original dense campaign's real kernel lock in
both launcher and controller; direct/unguarded resume is rejected. Do not resume
the old dense campaign simultaneously or resubmit a partial/advanced copy.

## Monitor and submission

Keep each monitor's working directory explicit. New dense runtime:

```bash
watch -n 30 '/usr/bin/python3.11 -I -B scripts/class001_status.py --manifest evolve/configs/class001_dense_recovery_v1.json --details'
```

Original-root `class001_large.json` shows the original six checkpoints, including
old 100000-node parents and the old dense parent; it is NOT the current six-graph
combined monitor. The current 100000-node retry monitor remains in the metadata
runtime. Check their respective private result folders when preparing the
assignment; publication/aggregation remains a separate manual user action.
Preserve feasible witnesses and distinguish target matches, reported bounds and
proofs. No quality improvement is guaranteed by this operational repair.
