# Cluster-local annealing budgets and native output recovery

Everything here is derived from this checkout. No laptop update, fetch, build,
model call, public experiment, job submission, commit or publication was made.
The current root sources remain unchanged because three campaigns hold their
locks. Implemented changes are isolated in `staging/class001_search_v4/source/`.
They are prepared code, not yet numerically verified on Slurm.

## Findings

Both 100000-node campaigns closed screening as `no_eligible_candidate`.
Each has ten timed-out candidates and one valid annealing observation recovered
after the earlier scorer failure. Recovery is deliberately nonselectable, so
there is no eligible parent population. An unchanged resubmission cannot repair
that screening result. Do not promote recovered observations or reset usage.

`evolution_worker.py` currently injects `max_work=10000` when a work-cap map is
empty. `portfolio_search.solve_annealing` also defaults to 10000 proposals.
Cooling is geometric in the proposal index, not in elapsed time. Therefore
giving the enclosing process more seconds does not lengthen a completed cooling
schedule. One sweep is **n independently sampled vertex proposals**, not accepted
flips. The class001 configuration has empty ordinary/screen work-cap maps, 120s
aggregate screening, 60s ordinary trials, and 30s admission. Timing policy v3
reserves up to 30s for verification; the numerical worker has a further 90%
inner allowance. None of those time limits removes the injected proposal cap.

The local saved stage records differ from the laptop's reported counts: signed
1000 has 3, 49 and 207 annealing records in its three historical campaigns;
Torus100 has 211. Every inspected record reports 10000 proposals: ten and one
sweep-equivalents respectively. These are saved stage records, not a new claim
of independent 30-second runs. See `historical_annealing_audit.json` in the bundle.
Both current 100000-node screening annealing records also report 10000 proposals.

The SMS adapter currently supplies nearly all remaining time to native SCIP,
then must still let SMS serialize `solution.json`, parse it, validate labels,
and let enclosing Python workers save their results. The runner can kill its
worker before that final Python record exists, returning only its known
incumbent. The actual ScientificMaxcutSolver source and binary are absent here;
upstream shutdown behavior and a real native recovery remain unverified.
The retained historical `evidence/portfolio/smoke_scientific/native/solution.json`
does use the expected `partition_0`/`partition_1` schema. Its old successful
receipt is historical evidence, not a present cluster-native verification or a
reproduction of the laptop's 1800-second failure.

## Implemented changes in the isolated source bundle

- Annealing with an explicit `max_work` retains fixed proposal-based geometric
  cooling. Without a proposal cap it cools over 80% of its remaining time,
  leaving time for optional polish and result return. Acceptance, random-node
  selection, original objective, and monotone incumbent retention use the
  existing kernel. Telemetry includes requested/actual proposals, sweep-
  equivalents, temperatures actually used, cooling completion, acceptance,
  worsening moves, raw labels/cut, polished cut and core/runtime measurements.
  Incomplete schedules are censored.
- The evolutionary worker stops injecting 10000 for annealing and calls that
  same kernel directly inside its existing Bubblewrap boundary. This avoids the
  nested runner's duplicate graph loading and serialization for this backend.
  Correctness admission gets a small explicit 2n-proposal limit; target trials
  use time unless an actual annealing cap is configured. Censored cooling does
  not earn selection credit, but independently checked improvements survive.
  Other backends keep their own work units and existing caps; no blanket cap
  increase, guard lift, larger aggregate allowance or budget reset is introduced.
- The runner charges parent/worker loading against one deadline and reserves
  up to 15s (20% for short runs) for parent return/independent save. Native
  execution reserves up to 30s (20% for short runs), with separate cooperative
  native and hard process deadlines, leaving parse time. Reaping is bounded,
  cleanup failures retain their ownership records, and discovery is bounded.
- SMS recovery validates a complete native partition and its native primal
  against the **native** labels before retaining a stronger supplied incumbent.
  A hard-stopped runner can recover an actual `native/solution.json` even when
  `worker_result.json` was not written. Missing/malformed native data stays
  distinct from fallback. A hard-stop recovery remains unproven even if raw text
  says optimal. Exit success or reference equality never establishes proof.

No old candidate base, manifest, observation, public label, native source or
binary is rewritten. Existing live campaigns keep the old kernel; this release
does not hot-upgrade them. It preserves the cluster's modules, compiler wrapper,
Slurm scripts, source/sandbox checks, size guards and timing-v3 controller window.

## Verify first: generated data only

Use the environment already validated on class001:

```bash
export CLASS001_PYTHON_MODULE=''
export CLASS001_EXTRA_MODULES=opensn/gcc/15.2.0-fortran
export CLASS001_PYTHON=/usr/bin/python3.11
export PATH="$HOME/.vscode-server/extensions/openai.chatgpt-26.1007.21434-linux-x64/bin/linux-x86_64:$PATH"
mkdir -p logs/slurm
verify_job=$(sbatch --parsable --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=00:45:00 \
  --job-name=maxcut-search-v4-check scripts/class001_search_v4.sbatch verify)
printf '%s\n' "$verify_job"
```

This builds a fresh private test checkout from current cluster files plus the
sealed four-file overlay. It runs generated signed-graph checks for fixed/time
cooling, assignment correctness, incumbent retention, censoring, actual bounded
process cleanup, locking, completed-attempt resume, reviewed partial retries,
SMS output fixtures and inherited campaign spending. It also runs portfolio,
controller, suite-v3 and deployment regressions. It launches no public search,
native build or model. All outputs live under the reported
`evidence/class001/search-v4-JOBID.*/` directory. A passing `verification.json`
is written only after every suite succeeds; status.txt and individual logs remain.

```bash
sacct -j "${verify_job%%;*}" --format=JobID,State,ExitCode,Elapsed
```

## Prepare two continuations after verification passes

The following preparation command is ready for the user; it has not been run.
Keep the original `verify_job` value in the shell, or use the actual report path
printed by that completed job. No public graph is optimized by preparation.

```bash
report_files=(evidence/class001/search-v4-"${verify_job%%;*}".*/verification.json)
[[ ${#report_files[@]} -eq 1 && -f "${report_files[0]}" ]] && \
sbatch --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=00:30:00 \
  --job-name=maxcut-search-v4-prepare \
  scripts/class001_search_v4.sbatch prepare "${report_files[0]}"
```

The preparation requires a matching passing verification identity. It creates
`staging/class001_search_v4/runtime/`, a separate source-version checkout with
copied original inputs/scorer/labels and shared existing `.venv`/native prefix.
It acquires each stopped parent's lock, validates its original source/base and
archive, and creates new `_class001_search_v4_01` IDs for the two blocked graphs.
Their new numerical bases get fresh fair screening. All parent counters,
cumulative active time and any held reservation are carried forward. Initialization
and preparation cost are counted too. The original ten-hour and model-call caps
stay unchanged. Old records/failed screening evidence are archived by reference
and copied into continuation receipts; the old campaigns remain unchanged.

Preparation never starts a controller. It refuses active parents and partial
unreviewed continuations. A previous partial version checkout is preserved for
inspection rather than overwritten. Do not resume the old parent in parallel
with its continuation. The other live campaigns need no source change or stop
for this isolated preparation, but they retain their original annealing behavior.

After passing preparation, this is the **later public-run command**, only when
the user requests resumption:

```bash
cd staging/class001_search_v4/runtime
sbatch --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=10:30:00 \
  --array=0-1%2 scripts/class001_array.sbatch \
  evolve/configs/class001_search_v4_retry.json
```

This new manifest has two entries: index0 signed100000, index1 positive100000.
It is separate from the old six-entry manifest. Use the explicit new manifest.
It retains remaining budgets; it cannot guarantee target attainment or completion
of every backend within a screening slot.

Monitor these two continuations from the **new runtime checkout** with:

```bash
/usr/bin/python3.11 -I scripts/class001_status.py \
  --manifest evolve/configs/class001_search_v4_retry.json --details
```

The original checkout's monitor will continue to show the preserved parent
statuses. It also remains the place to monitor the other original campaigns.

## Prepared experiment protocol (do not run until requested)

`scripts/annealing_experiment.py` uses the existing, extended kernel. The supplied
manifest selects signed1000 and Torus100 because those are the graphs in the
request; this is separate from the six class001 campaigns. The driver freezes
the strongest independently reverified local incumbent and original graph/ref
hashes before any calibration. Absolute laptop paths are not resumed; local
archive bytes and assignment files are independently checked instead.

For each graph, calibration is exactly 100000 proposals, T=6 throughout, seed0,
no polish. It must finish. Throughput uses actual proposal-loop runtime;
setup, full kernel and outer worker runtime are recorded separately. Sizing is:

```text
sweeps = floor(proposals_per_second * 30 * 0.8 / n)
proposals = sweeps * n
```

Fewer than 100 sweeps stops for budget review. No automatic larger budget or
lower minimum is substituted. Actual throughput and feasibility are unmeasured.

For seeds101,102,103,104, interleave fresh/T2->.01, frozen-incumbent/T2->.01,
frozen-incumbent/T6->.01 within each seed, with the same graph-specific proposal
count. Frozen labels never follow another condition's improvement. Comparison
polish is enabled equally in all three conditions, matching the existing kernel
default; calibration polish is disabled. Raw and polished cuts/labels and work
are reported separately, so polish is not credited as intrinsic annealing gain.

Every calibration/comparison gets a 60s worker ceiling, with the existing
bounded owned cleanup outside it. The 30s sizing target is not a runtime promise.
Incomplete schedules/failures remain censored and excluded from completed means
and medians. All independently verified improvements (including censored ones)
are retained privately with provenance; the frozen incumbent never degrades.

Each experiment ID has a kernel lock, immutable protocol/source identities,
frozen inputs, numbered attempt directories, raw streams, process receipts,
result hashes, work/temperature telemetry and private summaries. Completed
attempts resume without duplicate optimization. Partial, failed or censored
attempts require explicit review and a new numbered attempt; old evidence stays.
Historical censoring stays outside completed-schedule statistics after a retry.

From the verified private runtime checkout, this is the **later experiment
command**, only when requested:

```bash
sbatch --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=00:45:00 \
  scripts/class001_annealing.sbatch --experiment-id sa_fixed_work_01
```

Reusing that ID resumes completed work. An explicitly reviewed retry additionally
uses `--review-retry graph_stem/s101-incumbent-T6 --review-reason 'actual reviewed reason'`.
Use the exact step printed in the failure; do not blindly repeat failures.
The source, protocol and calibrated work plan cannot change under an existing ID.

## Remaining verification

Only syntax, metadata and file-identity checks have been performed in this
editing session. Generated numerical tests, calibration, public experiments,
large-graph fresh screening and real native SMS recovery are not yet verified.
SMS source/binary and its SCIP/toolchain prerequisites remain unavailable here;
no build, fetch, sudo operation or guessed alternative solver is attempted.
All resource values above are explicit user submissions, not inferred host
capacity. Public solutions are not combined or published automatically.
