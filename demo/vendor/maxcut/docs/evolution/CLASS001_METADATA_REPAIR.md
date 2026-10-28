# Continuation identity repair: prepared, not Slurm verified

**Historical guide:** metadata verification59836 and preparation59837 passed.
Later59839 runs exposed numerical timeouts, now addressed and fully generated-
verified by completion candidate3 in59849/59850. Use
[the completion guide](CLASS001_LARGE_COMPLETION_REPAIR.md) for the next two
large-graph continuations. Do not repeat the old metadata preparation or resume
its old numerical runtime unchanged. Old receipts/sources remain preserved.

This repair is isolated in `staging/class001_metadata_v1/source/`. Neither root
pinned sources nor the old `staging/class001_search_v4/runtime/` was edited.
The new runtime and campaign copies have NOT been created. The agent submitted
no jobs, ran no numerical tests, and made no framework model calls.

## Schema and compatibility

New continuation metadata uses this parent identity inside `continuation_of`
and its creation receipt:

```json
{"identity_version": 1, "campaign_id": "PARENT_CAMPAIGN_ID"}
```

Other provenance fields are retained. The reader normalizes unversioned
`parent_id` and `campaign_id` legacy records without rewriting their bytes.
Matching dual aliases are accepted; missing, malformed, conflicting, unknown
version, or parent-snapshot-mismatched identities are rejected. Canonical
version 1 requires `campaign_id`. The normalized record and receipt must agree,
and the saved parent campaign/state snapshot hashes must match their receipts.

Both continuation writers are corrected in the overlay. The controller uses
the validated normalized identity when constructing round-1 proposal context.
This changes metadata handling, not the numerical kernels, scoring policy,
solver guards, configuration caps, or previously fixed annealing/native code.
SMS is unavailable and is not required by this repair or its verification.

## Version transition

The prepared helper builds a separate checkout at
`staging/class001_metadata_v1/runtime/` only after a passing verification report
matches the sealed source/support bundle. It copies the SAME two campaign IDs,
their immutable numerical bases, raw logs, artifacts, closed screening round 0,
pending round-1 planning state, verified archive and complete cumulative usage.
It never creates fresh screening or resets a budget.

The old runtime remains intact. Both old campaign kernel locks must be free and
held throughout preparation; outstanding reservations or process registrations
require review. Only the reviewed metadata-error checkpoint shape is accepted.

The new source contract is explicit: previous records, live context/state,
source bytes and hashes are archived under each copied campaign's
`source-revisions/class001-continuation-metadata-v1/`. Only the NEW copy gets
the new protected-source manifest and source-history entry. Its canonical
`continuation_of` is compatible with the unchanged historical creation receipt.
Live path pointers are rebased into the new checkout; historical closed-round,
trial and candidate files remain byte-identical. Counters and cap configuration
are identical; active seconds carry forward plus preparation/validation time.
Current best assignment hashes and completed round manifests stay unchanged.

Preparation performs actual integrity validation and constructs proposal context
read-only, but does not request a proposal, run a solver or start a controller.
A complete global `metadata_transition.json` is written only after BOTH copies
are ready. A complete unchanged preparation can be inspected/repeated without
adding spending. Partial destinations are preserved and refused for explicit
review rather than overwritten or silently resumed.

The dedicated resume launcher holds the OLD campaign's unchanged kernel lock
across exec, then passes the descriptor to the new controller too. Thus a lost
launcher cannot release the old lock while its controller is still running.
It rejects an old runtime that advanced or changed since preparation. The new
controller also requires this inherited descriptor, so direct unguarded resume
and the old array script are not supported entry points for the repaired copies.
Use the dedicated `class001_metadata_array.sbatch` command below.

## Verification status and coverage

Prepared: **16 generated-data tests**, including real continuation preparation,
real bounded round-0 numerical screening and closure, then round-1 context
construction and a real `fixture-test` bridge response. The response deliberately
stops after planning; no paid provider is inspected or invoked. A legacy
`parent_id` case exercises the same path without rewriting the old receipt.

Other regressions cover canonical/legacy aliases and invalid identities,
snapshot/provenance corruption, transition preservation, pending-round reuse,
idempotence, partial-copy refusal, advanced/active old runtime refusal, inherited
lock lifetime, and guarded resume without repeating screening. Fixtures contain
only a generated four-node graph and labels; no Git initialization/commits or
native SMS runs occur. Temporary fixture locks live on the job evidence
filesystem, so their NFS behavior is exercised inside the allocation.

Executed by the agent: Python AST parsing, Bash syntax and source/file-identity
inspection only. **The 16 tests have not been executed.** Earlier 172 passing
tests remain historical evidence for the old version and are not a passing
receipt for this repair. The sealed manifest pins the baseline runtime,
five overlay files, and four support/test files. A subsequent code change
requires a newly sealed bundle and a new verification report.

## 1. Submit verification only

Run from the original repository root, not the old `runtime` directory:

```bash
cd /home/grads/m/mahmudulhasantamim/engr-689/projects_github/bipartite/bipartite-mahmudulh-tamim
export CLASS001_PYTHON_MODULE=''
export CLASS001_EXTRA_MODULES=opensn/gcc/15.2.0-fortran
export CLASS001_PYTHON=/usr/bin/python3.11
export PATH="$HOME/.vscode-server/extensions/openai.chatgpt-26.1007.21434-linux-x64/bin/linux-x86_64:$PATH"
mkdir -p logs/slurm
metadata_verify_job=$(sbatch --parsable --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=00:45:00 \
  scripts/class001_metadata_repair.sbatch verify)
printf '%s\n' "$metadata_verify_job"
```

The script stages a fresh test checkout under the job's evidence directory.
Staging is bounded at 300s; generated tests at 900s, with bounded timeout cleanup.
The 45-minute Slurm wall is explicit headroom, not a campaign allowance.

```bash
sacct -j "${metadata_verify_job%%;*}" --format=JobID,State,ExitCode,Elapsed,MaxRSS
cat "logs/slurm/maxcut-metadata-check-${metadata_verify_job%%;*}.out"
cat "logs/slurm/maxcut-metadata-check-${metadata_verify_job%%;*}.err"
```

Require COMPLETED/0:0, `status.txt` exit 0, the `metadata.stderr` unittest
summary OK, and `verification.json` with `passed: true` under
`evidence/class001/metadata-v1-JOBID.*/`. Failed/interrupted receipts remain
evidence; do not prepare or resume on a failed verification. If reconnecting,
set `metadata_verify_job` to the actual completed verification job ID.

## 2. Only after verification passes: prepare copies

Still from the ORIGINAL repository root with the same exports:

```bash
metadata_reports=(evidence/class001/metadata-v1-"${metadata_verify_job%%;*}".*/verification.json)
if [[ ${#metadata_reports[@]} -eq 1 && -f "${metadata_reports[0]}" ]]; then
  metadata_prepare_job=$(sbatch --parsable --export=ALL --nodes=1 \
    --ntasks=2 --cpus-per-task=5 --mem=15G --time=00:30:00 \
    --job-name=maxcut-metadata-prepare \
    scripts/class001_metadata_repair.sbatch prepare "${metadata_reports[0]}")
  printf '%s\n' "$metadata_prepare_job"
else
  printf '%s\n' 'No unique metadata verification report found; inspect the completed job.' >&2
fi
```

Preparation independently checks `passed` and the exact sealed identity. It is
bounded at 1500s plus cleanup and starts no numerical/model search.

```bash
sacct -j "${metadata_prepare_job%%;*}" --format=JobID,State,ExitCode,Elapsed,MaxRSS
cat "logs/slurm/maxcut-metadata-prepare-${metadata_prepare_job%%;*}.out"
cat "logs/slurm/maxcut-metadata-prepare-${metadata_prepare_job%%;*}.err"
```

Require successful accounting/status, the new runtime's
`metadata_transition.json`, and TWO completed per-campaign transition receipts.
The copied checkpoint may still display the historical `integrity_error` stop
reason before explicit resume; preparation does not pretend a controller ran.
No old job, old parent, old runtime or public solution should be restarted.

## 3. Only after preparation passes: explicit guarded resume

From the original repository root, enter the NEW runtime:

```bash
cd staging/class001_metadata_v1/runtime
sbatch --parsable --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=10:30:00 \
  --array=0-1%2 scripts/class001_metadata_array.sbatch \
  evolve/configs/class001_search_v4_retry.json
```

Index 0 is signed100000, index 1 positive100000. IDs remain
`rand_pm_100000_s43_class001_search_v4_01` and
`rand_pos_100000_s42_class001_search_v4_01`, now in the reviewed new runtime.
They keep only their original remaining cumulative ten-hour/250-call budgets.
This last command can make paid model calls and is for the user to initiate
separately. Do not use a generic `resume_command` printed by the older status
implementation; it lacks the required cross-runtime ownership guard.

Monitor from that new runtime:

```bash
watch -n 30 '/usr/bin/python3.11 -I -B scripts/class001_status.py --manifest evolve/configs/class001_search_v4_retry.json --details'
```

These are saved checkpoints; `squeue` shows live scheduler state. Keep old
runtime results as evidence and do not publish/aggregate automatically.

## Subsequent tasks

Keep the two 10000-node model-capacity cases, dense1000 trial-completion/timing
review, and Torus316 cumulative-budget review separate from this repair.
Calibrated comparisons and actual SMS/native prerequisites remain separate
scientific/dependency work. None is a prerequisite for validating the metadata
schema or resuming these two campaigns after the explicit verification gates.
