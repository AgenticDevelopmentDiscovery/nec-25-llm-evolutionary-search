# Class001 commands after suite-v3 integration

Current task: the two 100000-node IDs stopped as `no_eligible_candidate`.
Their recovered annealing witnesses cannot be promoted into selectable samples.
The cluster-local annealing/native-output revision is implemented in an isolated
source bundle; live root sources and existing campaign contracts are unchanged.
Use [CLASS001_SEARCH_V4.md](CLASS001_SEARCH_V4.md) for the next verification job,
then preparation of continuations carrying all existing time/call expenditure.
Do not blindly rerun the old closed screening. No laptop update is needed.
The following earlier milestones/commands predate this new source-version work.

`main` was fast-forwarded to `0ecbfc21` on October 21, 2026. Cluster adaptations
were restored and reconciled. No jobs, numerical tests, builds or model calls
were run during integration. The user submits all jobs from this repository.

## Next action: resume the six migrated IDs

Repair job **58571 passed** in 6m52s: 99 controller, 23 portfolio and 16
deployment tests OK, generated-fixture smoke passed, and all SIX migration
receipts verified. Protected-source and archive hashes match; saved state,
counters and spending are unchanged. No real model call or public optimization
occurred during maintenance. See `evidence/class001/setup-58571.B4rEsV/inspection.md`.

Using the same module/Python exports as that successful job, resume:

```bash
sbatch --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=10:30:00 \
  --array=0-5%6 scripts/class001_array.sbatch
```

This resumes all six existing public graph campaigns and may make real model
calls. Each keeps its remaining original ten-hour active/call budget. Stop flags
are cleared by explicit resume; interrupted comparisons replay with fresh IDs
and their existing admitted children/model plans. No automatic publication or
combination occurs. Large-graph v3 performance/target attainment is unverified.

## Historical repair procedure (completed by 58571; do not repeat without cause)

The user confirmed all six campaigns stopped. All six kernel locks were free
before editing the four pinned runtime files. Checkpoints, archive labels,
spent budgets, stop requests, old contracts and failure evidence are unchanged.
The static checks do not establish runtime verification. Do not resume the array
against its old source contracts.

Submit ONE maintenance job from the checkout root:

```bash
export CLASS001_PYTHON_MODULE=''
export CLASS001_EXTRA_MODULES=opensn/gcc/15.2.0-fortran
export CLASS001_PYTHON=/usr/bin/python3.11
export PATH="$HOME/.vscode-server/extensions/openai.chatgpt-26.1007.21434-linux-x64/bin/linux-x86_64:$PATH"
mkdir -p logs/slurm
sbatch --parsable --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=00:45:00 \
  --job-name=maxcut-runtime-repair \
  scripts/class001_setup.sbatch repair-runtime
```

This runs the affected controller, portfolio and deployment regressions plus a
generated-fixture smoke check, with zero real model calls and no public graph
optimization. Only if every check passes does it explicitly migrate the six
existing IDs using `scripts/migrate_class001_runtime.py`. Each source revision
archives its old/new contract and keeps all costs/reservations. Partial ordinary
comparisons are censored and replayed on resume, using their existing proposal
and admitted children. No budget is reset and no old trial is relabeled.

The 45-minute request bounds this maintenance job; the campaign window remains
36000 cumulative active seconds. Inspect the returned job ID and its evidence:

```bash
sacct -j YOUR_REPAIR_JOB_ID --format=JobID,State,ExitCode,Elapsed
cat logs/slurm/maxcut-runtime-repair-YOUR_REPAIR_JOB_ID.out
cat logs/slurm/maxcut-runtime-repair-YOUR_REPAIR_JOB_ID.err
```

The outer output names `evidence/class001/setup-JOBID.*/`. Require exit zero in
its `status.txt`, passing `controller/portfolio/deployment` logs, a passing
fixture `verification.json`, and SIX successful `migrate-runtime.stdout`
receipts. Interrupted migrations are journaled and restartable; preserve their
evidence. The `runtime-check` action runs checks only; `migrate-runtime` applies
the reviewed migration separately when verification is already established.

Only after the maintenance job passes and all six migration receipts exist,
resume the same IDs with the selected resources:

```bash
sbatch --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=10:30:00 \
  --array=0-5%6 scripts/class001_array.sbatch
```

This last command starts/resumes all six public graph campaigns and may make
real model calls. It is separate from maintenance and is for the user to submit.
The launcher clears earlier stop requests only on explicit resume, preserves
usage and resumes remaining work. Actual large-graph performance/target success
under v3 remains unverified. Failure history: `evidence/class001/array-58565-runtime-failures/`.

## Historical array failure: 58558

All six elements passed preflight but failed before controller launch: exclusive
lock probing through a read-only descriptor raised error 9 on NFS4. The launcher
now opens the EXISTING lock with `r+b`, which does not create/truncate/write its
contents. Nonblocking ownership and symlink checks remain. An owned metadata
probe confirmed the cause and fix on the actual shared filesystem. No root
source/config, campaign checkpoint or pinned manifest was changed. All six
campaigns retain zero model/solver calls and their initialization time.

User job **58564 passed all 93 controller tests**, including both lock regressions
and actual shared-filesystem ownership checks. The previous pending verification
is resolved; no need to repeat the command below absent changes/new failures:

```bash
sbatch --parsable --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=00:15:00 \
  --job-name=maxcut-lock-regression \
  scripts/class001_setup.sbatch test --suite controller
```

At that milestone the next action was to resubmit. The launcher resumes the
SAME IDs, preserving starting labels and cumulative time/counters; do not delete
campaign folders, reset quotas or edit old manifests. Saved `initialized` state
alone does not mean that a controller is running. See
`evidence/class001/array-58558-launch-failure/`. No resubmission was made by the agent.

## Current profile and source boundary

`evolve/configs/class001_large.json` selects six independent fresh
`_class001_suite_v3_01` IDs and `evolve/configs/class001_campaign.json`.
All six IDs already exist from initialization in 58558; reuse them without resetting
usage. Keep the three laptop continuation IDs in
`parallel_sparse.json` separate; do not try to resume them on class001.

The class profile keeps the user's ten-hour cumulative active budget (36000s),
250 model-call cap, 300s call timeout and nullable round/solver-count caps.
Config schema version 2 enables these nullable caps; it is distinct from
scoring timing policy v3. All usage remains counted across resumes.

Incoming suite-v3 settings take precedence for **120 aggregate seconds per
screened configuration and 30 aggregate seconds per admission**. The local
60-second ordinary trial and 60-second finalization reserve remain. Timing policy
v3 reserves up to 30s for verification and lets numerical work use the remainder
after setup (up to 90s screening / 30s ordinary trial). Verification uses all
remaining aggregate time, without a separate five-second cap. Setup/copying/
parsing count. Recovery reserves up to 60s from the remaining campaign budget,
uses zero new solver slots, and remains excluded from fair timing credit.
This supersedes v2's fixed 50% numerical ceiling; the removed `scoring_seconds`
option remains rejected. Algorithm parameters, topology/size guards, finite
model spending and owned process deadlines remain enforced. Intrinsic finite
integration schedules are not rewritten into different numerical methods.

Suite-v3 toroidal windows, PT/cluster moves, Mixing and four guarded MQLib
configurations are preserved. Optional missing dependencies remain unavailable.
Strict target comparisons, native size/topology guards, source hashes, Bubblewrap
and honest failure stops remain enforced. No blind model retry or target
attainment guarantee is provided. Public labels and historical campaigns remain
unchanged; old pinned campaigns require their own matching source or a separately
reviewed migration, not manifest rewriting.

## Environment already verified in earlier Slurm jobs

```bash
export CLASS001_PYTHON_MODULE=''
export CLASS001_EXTRA_MODULES=opensn/gcc/15.2.0-fortran
export CLASS001_PYTHON=/usr/bin/python3.11
export PATH="$HOME/.vscode-server/extensions/openai.chatgpt-26.1007.21434-linux-x64/bin/linux-x86_64:$PATH"
mkdir -p logs/slurm
```

Module Python 3.12.3 lacks `_ctypes`; system Python 3.11 fixed the process
supervisor in jobs 58524/58525. Keep the existing `.venv`; the fetched commits
change neither `pyproject.toml` nor `uv.lock`, so integration does not require
recreating it. The CLI extension path can change after a VS Code update.
Credentials remain account-local and were not inspected or copied.

## Earlier verified regressions (before runtime v3)

Actual user jobs passed for the earlier source version:

- Deployment 58549: 15 tests OK.
- Pinned toroidal Python source setup 58553: exit 0, exact reviewed revision.
- Controller 58554: 91 tests OK, including the corrected timing integration test.
- Suite-v3 58555: 18 tests OK, including direct all-eight toroidal admission.
- Portfolio 58552: 23 tests OK with two skips.

Earlier failures 58550/58551 remain preserved. The toroidal source was obtained
inside the user's setup allocation; no native compilation/sudo was needed.
These receipts do not establish optional native MPI or large-graph performance.
Do not repeat the passing suites without changes or a new concern.

Earlier preflight 58556 and fixture smoke 58557 both passed with exit 0.
Preflight verified all 18 portable labels, CLI, Bubblewrap, raw capture, owned
cleanup and Git checks. Smoke used fixture-test, 15-second aggregate windows,
reached strict target cut 10 / score 1.0, preserved labels/Git and made zero real
model calls. The config still matches preflight, but all six selected IDs have
since run and stopped. These receipts predate runtime v3 and do not verify it.

The runtime-v3 source changes require the maintenance gate at the top of this
guide before resumption. Public campaigns can make paid model calls (up to 250
per graph). The agent has submitted nothing. Failed evidence remains unchanged.

## Optional dependency/build verification

No dependency sync or native build ran during integration. Earlier absence of
MQLib, Scientific, BiqBin/MADAM/BiqCrunch and TESB remains unresolved until an
actual allocation verifies them. The toroidal Python source/admission path is
verified by jobs 58553/58555; it does not require a native build. Pure Python v3 methods add
no new mandatory dependency. The new preflight supplies current availability.

The Scientific builder retains explicit `--cxx-wrapper scripts/class001_gxx_compat`.
Select an absolute approved compiler through `CLASS001_CXX`; the wrapper adds
`-include cstdint` and preserves arguments. Its deployment tests use a generated
fake compiler. The historical wrapper, upstream pins and source trees stay intact.
An actual Scientific build additionally needs an account-local SCIP prefix and
other libraries described in `docs/portfolio/EXTERNAL_BUILDS.md`; the module alone
does not supply those dependencies. No sudo or substitute backend is appropriate.

When a desired native backend's prerequisites are ready, its prepared build request
can be previewed without execution (example MQLib; `--fetch` permits pinned fetch):

```bash
/usr/bin/python3.11 -I scripts/class001_jobs.py request setup \
  --setup-action build --backend mqlib --fetch \
  --ntasks 2 --cpus-per-task 5 --mem 15G --time 00:45:00
```

Add `--submit` yourself only when requesting that build. Slurm's 45-minute wall
bounds the build; `-j2` remains. Real two-rank verification, after installing the
actual backend, is separately bounded to 180 seconds plus cleanup:

```bash
sbatch --parsable --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=00:05:00 \
  scripts/class001_setup.sbatch native-check --backend biqbin
```

This command intentionally fails if BiqBin is absent; generic MPI launch success
is not proof that its confined adapter works. Do not run it merely to repeat a
known missing dependency.

## Later: six-graph submission after reviewing verification

```bash
sbatch --parsable --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=10:30:00 \
  --array=0-5%6 scripts/class001_array.sbatch \
  evolve/configs/class001_large.json
```

One controller runs per element, with ten logical CPUs and 15 GiB requested per
graph: up to 60 logical CPUs and 90 GiB overall. This reservation does not make
serial numerical algorithms use ten threads. Native MPI adapters retain exactly
two task slots. Scheduler acceptance and large-graph peak memory are unmeasured;
15G is the user's selected request, not a measured requirement. No allocation
is inferred from `nproc` or `free`. The Slurm wall includes margin beyond the
ten-hour cumulative active quota and the early cleanup signal remains enabled.

For a single graph, use the v3 ID from the manifest, for example
`rand_pm_100000_s43_class001_suite_v3_01`. The compatible launcher resumes only
same-checkout IDs without resetting expenditure, and leaves active owners alone.

## Preservation and recovery

For saved solution progress while campaigns run, use this standard-library-only
reader from the repository root (no numerical imports, job launch or state writes):

```bash
/usr/bin/python3.11 -I scripts/class001_status.py
watch -n 30 '/usr/bin/python3.11 -I scripts/class001_status.py'
```

Use `--details` for stop reasons, reserved operation, saved active time, solver
slots and private label paths. SCORE/BEST CUT come from the verified archive;
MODEL counts real model-call attempts and TARGET uses the stored strict flag.
Round 0 is screening. Output is the latest checkpoint, not a scheduler/lock
ownership assertion. `squeue -u "$USER"` shows actual queued/running jobs.
Public `solutions/` does not receive private improvements automatically.

The stash `ab1cfd5dbfdd644c448131ef4e02c3fbb9411158` remains retained after apply.
A verified archive at `/tmp/class001-before-origin-20261021-3g8myq6f/checkout-before.tar`
also includes nested scratch Git repositories omitted by `stash --include-untracked`.
It excludes root ignored environments/native builds/credentials. Those were left
in place. Do not blindly reapply the stash over this reconciled checkout.

See `evidence/class001/integration-origin-20261021/` for reconciliation and static
verification. Earlier raw evidence, failed jobs, public labels and historical
campaigns were not rewritten. No commit, push, publication or result aggregation
was performed. Collect available job accounting after submission:

```bash
sacct -j YOUR_JOB_ID --format=JobID,State,ExitCode,Elapsed,AllocCPUS,ReqMem,MaxRSS
```
