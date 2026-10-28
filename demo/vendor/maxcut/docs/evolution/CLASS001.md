# Class001 deployment: six expensive graphs, resource choices left open

For the current `no_eligible_candidate` and annealing-budget task, use
[the cluster-local source-version guide](CLASS001_SEARCH_V4.md). Fixes and an
isolated experiment driver are prepared here without laptop updates or edits
to code pinned by live campaigns. Slurm verification is pending; continuation
preparation preserves old labels/history and cumulative spending.

This guide originated as a laptop handoff. A subsequent read-only cluster
inspection and deployment update is recorded in
[the current preparation evidence](../../evidence/class001/deployment-20261020/README.md).
Use [the current command guide](CLASS001_COMMANDS.md) for submission.
The user has since submitted setup/preflight/test jobs; current receipts and
remaining limitations are recorded in the project context. The user has no sudo
privileges, chooses all resources and submits all jobs.

The October 21 controller update uses config version 2 for fresh class001 IDs:
ten active hours, no round/solver-count ceiling, and a retained 250-model-call
budget. Read [the current commands and verification gate](CLASS001_COMMANDS.md)
before submitting. Earlier regressions/preflight/smoke passed, but public array
58565 exposed scoring and cleanup failures. The user has stopped all six IDs.
Runtime v3 removes the fixed scorer/50% limits within the aggregate trial window;
its regression checks, fixture smoke and all six explicit migrations PASSED in
user job 58571. Resume the six existing IDs using the current command guide;
their original remaining time/call budgets are retained.
Historical campaigns outside the six selected IDs are not migrated.

Start the next session with [the ready-to-paste prompt](CLASS001_START_PROMPT.md),
which explicitly loads [project instructions](../../instruction_Tamim/CLASS001_CODEX_INSTRUCTIONS.md)
and [project/cluster context](../../instruction_Tamim/CLASS001_CONTEXT.md).

## Pull and inspect before computation

The supplied access route is `ssh YOUR_NETID@orchard.engr.tamu.edu`, followed by
`ssh nuen-orch-class001`. The reported host had 64 CPUs and 124 GiB RAM; that is
historical host capacity, not an allocation. User-supplied class instructions use
partition/account `orchard-class`. Confirm current limits/site rules there.

Commit and push the reviewed files yourself, then pull in the cluster checkout
before initializing campaigns. Inspect `git status` before pulling; do not force
or reset over cluster results. Do not pull changed root code/native binaries or
edit manifests/configuration while affected jobs are queued/running. Existing
campaign source hashes must remain valid.

Transfer the new `cluster_inputs/class001_initial/` label snapshot with the code.
It has all 18 independently validated assignments/sidecars, graph/reference and
selection identities, provenance and full scores. It includes the retained
signed-random10000 cut **11388**. Its full snapshot score is
**0.9780330754570459**; the public `solutions/` folder was not changed. The
snapshot is a new portable input set, not remote resumption of a laptop campaign.
Use the fresh `_class001_suite_v3_01` IDs in `evolve/configs/class001_large.json`.
Absolute paths in old laptop state, runtime locks, `.venv` and compiled binaries
must not be treated as a cluster installation. Historical evidence stays intact.

The separate local manifest `parallel_sparse.json` contains torus100,
signed-random1000 and torus32. The cluster manifest contains only:

| Array index | Graph | Nodes | Edges |
| --- | --- | ---: | ---: |
| 0 | `rand_pm_100000_s43.txt` | 100000 | 501269 |
| 1 | `dense_gauss_1000_s24.txt` | 1000 | 499500 |
| 2 | `rand_pos_100000_s42.txt` | 100000 | 498683 |
| 3 | `torus_pm_316_s41.txt` | 99856 | 199712 |
| 4 | `rand_pm_10000_s33.txt` | 10000 | 50010 |
| 5 | `rand_pos_10000_s32.txt` | 10000 | 49825 |

## Choose resources explicitly

All four `.sbatch` files contain commented CPU/memory placeholders and **no
active fixed CPU/memory directives**. Pass explicit Slurm resource flags after
agreeing the values with the cluster session. The scripts require allocation
metadata, one node, task/CPU counts and a memory request; otherwise they fail
before solver execution. Full-portfolio public jobs need at least two task slots
for the existing two-rank native adapters, but start **one controller**, not one
per task. Extra cores do not parallelize serial candidate code automatically.
Native placement inside the sandbox still requires cluster verification.

The standard-library helper is usable before `.venv` exists. Module Python 3.12.3
was confirmed to lack `_ctypes`; existing system Python 3.11 subsequently passed
Slurm setup/preflight. See the current command guide for that interpreter/module
selection and the pending verification of this reconciled source:

```bash
/usr/bin/python3.11 -I scripts/class001_jobs.py request preflight \
  --ntasks CHOOSE_TASK_SLOTS \
  --cpus-per-task CHOOSE_CPUS_PER_TASK \
  --mem CHOOSE_MEMORY --time CHOOSE_WALL_TIME
```

Replace every `CHOOSE_...` value. These are placeholders, not suggested
allocations. Missing/non-numeric CPU choices or the memory placeholder are
rejected. The helper **prints a reviewable request by default**, without writing
logs or submitting. Add `--submit` only when ready to submit that stage; it
creates `logs/slurm` first and retains the scheduler stdout/stderr/job-ID response
in `logs/slurm/submissions/`. Resources apply separately to each array element.
Array concurrency is chosen independently of CPUs per element and model-call
budgets; six concurrent elements can issue six concurrent model requests.

For direct submission, create `logs/slurm` first and pass the same resource
flags to `sbatch` before the `.sbatch` filename. Do not put shell variable
substitutions into `#SBATCH` headers: Slurm reads those literally. See the
[official sbatch documentation](https://slurm.schedmd.com/sbatch.html).

## Environment, builds and tests through Slurm

The observed module is `python3/3.12.3`. Scripts retain that historical default and add
`$HOME/.local/bin` to PATH. An alternate approved Python module can be selected
with `CLASS001_PYTHON_MODULE`. An explicitly empty value skips module Python;
`CLASS001_PYTHON` selects an absolute existing interpreter. Jobs clear the
module's `PYTHONHOME`/`PYTHONPATH` before `.venv` use. Compiler/MPI modules can be passed
as space-separated `CLASS001_EXTRA_MODULES`; no compiler or MPI module is assumed.
The scripts cap numerical-library threads to one per process. Account-local
uv and Codex must already be installed by an approved method; no root command
or automatic installation is attempted by campaign/preflight jobs. Whether
interactive agent use/networking is permitted on login nodes is a site question.

Prepare the cluster `.venv` inside a setup allocation:

```bash
/usr/bin/python3.11 -I scripts/class001_jobs.py request setup \
  --setup-action sync --extra matching --extra milp --extra tesb \
  --ntasks CHOOSE_TASK_SLOTS --cpus-per-task CHOOSE_CPUS_PER_TASK \
  --mem CHOOSE_MEMORY --time CHOOSE_WALL_TIME
```

Review, then append `--submit`. This runs `uv sync --locked` with the module
interpreter. Optional extras are explicit; unavailable wheels/libraries are
recorded failures, not permission to install system packages. Follow site rules
for permitted package/source network access. OpenSn and Boost are not requirements
of this Max-Cut project; the screenshot's OpenSn instructions were for a different
application.

Pinned optional builds and regression tests have separate setup actions:

```bash
/usr/bin/python3.11 -I scripts/class001_jobs.py request setup \
  --setup-action build --backend mqlib --fetch \
  --ntasks CHOOSE_TASK_SLOTS --cpus-per-task CHOOSE_CPUS_PER_TASK \
  --mem CHOOSE_MEMORY --time CHOOSE_WALL_TIME

/usr/bin/python3.11 -I scripts/class001_jobs.py request setup --setup-action test \
  --ntasks CHOOSE_TASK_SLOTS --cpus-per-task CHOOSE_CPUS_PER_TASK \
  --mem CHOOSE_MEMORY --time CHOOSE_WALL_TIME
```

Builds use `external/sources.json` and `scripts/build_portfolio_backends.py`.
`--fetch` explicitly permits fetching pinned sources; no moving default branch
or substituted algorithm is accepted. The build script currently uses `-j2`;
request at least two CPU slots for builds/tests. MPI-capable tests need task slots
suitable for two ranks. Rebuild with the cluster's actual toolchain before
freezing campaigns. The historical Scientific wrapper names missing
`/usr/bin/g++-12`. Cluster builds can explicitly select
`--cxx-wrapper scripts/class001_gxx_compat` and an absolute `CLASS001_CXX`;
the historical wrapper stays unchanged. Source pins
and node/topology guards remain enforced. See [build records](../portfolio/EXTERNAL_BUILDS.md).

## Preflight and optional bounded live integration

After setup, request `preflight` as above, review, then add `--submit`.
`class001_preflight.sbatch` checks the portable snapshot and runs `doctor` using
`class001_campaign.json`. It captures unique reports under
`evidence/class001/preflight-JOBID.*`. Default preflight makes **no model call**
and performs no public optimization. Missing optional backends are reported;
Codex CLI compatibility, Bubblewrap, raw capture, owned cleanup and Git checkout
must pass before a public campaign can start. Git author identity does not gate
campaigns, which do not make commits.

Infrastructure success does not establish authentication/compute-node egress or
native sandboxed MPI functionality. When the user explicitly requests a real
bounded integration check, use stage `live-check` with the same resource choices.
It adds `--live-check` to preflight and runs only the framework's generated tiny
scratch trap (220 active seconds, one model-call slot, 90-second call timeout,
30 numerical slots). Preserve raw failures and inspect `verification.json`.
Fixture output is not a substitute for a real successful call.

If Bubblewrap/user namespaces are disallowed, ask the administrator for a
supported configuration. Account-local installation cannot grant missing kernel
permissions; do not disable the sandbox. Model credentials remain account-local
and must never be logged, committed or copied from the laptop as repository data.

## Later: submit one graph or the six-element array

A single graph, with automatic creation or same-checkout checkpoint resume:

```bash
/usr/bin/python3.11 -I scripts/class001_jobs.py request campaign \
  --instance instances/public/rand_pm_100000_s43.txt \
  --campaign-id rand_pm_100000_s43_class001_suite_v3_01 \
  --ntasks CHOOSE_TASK_SLOTS --cpus-per-task CHOOSE_CPUS_PER_TASK \
  --mem CHOOSE_MEMORY --time CHOOSE_WALL_TIME
```

All six cluster graphs, one independent allocation per array element:

```bash
/usr/bin/python3.11 -I scripts/class001_jobs.py request array \
  --manifest evolve/configs/class001_large.json \
  --max-concurrent CHOOSE_SIMULTANEOUS_CAMPAIGNS \
  --ntasks CHOOSE_TASK_SLOTS --cpus-per-task CHOOSE_CPUS_PER_TASK \
  --mem CHOOSE_MEMORY --time CHOOSE_WALL_TIME
```

Again, replace placeholders, review, then add `--submit`. A limit of one queues
the six array elements; larger limits allow that many independent campaign jobs.
CPU/memory requests are **per element**, not shared totals for all six. This
avoids several native MPI controllers sharing one allocation without verified
placement. Do not use laptop `batch --jobs 6` on a cluster login node or launch
`srun -n N` copies of the controller.

The class001 profile combines [suite-v3 methods](../portfolio/SUITE_V3.md) and
current timing policy v3 with the user's 36000-second active budget and 250
model calls. Config schema version 2 accepts `null` for `max_rounds` and
`max_solver_trials`; all work is still counted. The general version-1 defaults
remain 500 slots / 7200 seconds / 20 rounds / 25 calls.

Class001 screening is **120 aggregate seconds per configuration**, admission is
30 aggregate seconds, ordinary comparison trials are up to 60 aggregate seconds,
and finalization reserves 60 seconds. Numerical work uses the remaining trial
time after setup and a verification reserve of up to 30s. Scoring receives ALL
remaining trial time without a separate five-second ceiling. Recovery reserves
up to 60s from remaining campaign time. The fixed 50% worker ceiling is removed;
the old `scoring_seconds` option remains rejected.
Copying/parsing count; failures retain score request/process receipts. Recovered
verification is charged without new solver slots and cannot earn fair comparison
timing credit. Cache conditions include the timing-policy hash.

The explicit BM eight-pass override remains removed; original algorithm defaults
and the worker's default 10000 work-unit ceiling are unchanged. Per-trial bounds
permit fair comparisons, checkpointing and subsequent proposals. Strict target,
manual stop, model-call quota, invalid/duplicate proposal review, service errors,
proof/numerical diagnostics and integrity checks can still stop a launch early.
Three stagnant rounds require diversification, not automatic success or blind
retry. No target attainment is guaranteed. Config version cannot change on resume;
reuse the six `_class001_suite_v3_01` IDs only after the reviewed source migration,
leaving old contracts/evidence archived intact.

Use Slurm wall `10:30:00` for the ten-hour active budget and preflight/cleanup
margin. No active CPU/memory/wall directives override the explicit request. An early
`B:INT@120` signal is directed to the `exec`-replaced batch process for bounded
owned-child cleanup. This signal's scheduler delivery and native/MPI integration
remain remotely unverified. Hard kills can still leave ambiguous reservations,
which recovery conservatively charges. Longer campaign caps need reviewed Slurm
wall limits (`request --time ...`) and config changes; neither changes the other
automatically. Budget stops commonly exit 2 and can show as Slurm FAILED even
though they retain valid progress; inspect the campaign reason before diagnosing
an infrastructure failure. Repeated submissions preserve cumulative usage.

Outer logs: `logs/slurm/%x-%j.out/.err`, or `%x-%A_%a.out/.err` for the array.
Each campaign keeps separate raw Codex/numerical logs, checkpoints, private labels
and attempt receipts. `already_running` means an external controller keeps
ownership; the new job does not adopt or duplicate it. Use status and durable stop
commands on the cluster's own IDs. Read `squeue -u "$USER"` and job accounting for
State/ExitCode/Elapsed/AllocCPUS/ReqMem/MaxRSS after completion; site accounting
availability may vary. Do not automatically resubmit failed jobs indefinitely.

The user will decide when to consolidate/publish selected improvements and commit
results. No script pushes, tags, commits or changes the public solution folder.
The current local verification is indexed in
[the handoff evidence](../../evidence/class001_handoff/README.md); earlier simulated
preparation receipts remain historical evidence, not remote acceptance.

## Suite v3 source update

Read `docs/portfolio/SUITE_V3.md` before starting new cluster campaigns. The class
profile now screens each configuration for 120 aggregate seconds and gives
admission 30 seconds. It includes four MQLib configurations, sparse torus-window
matching, PT/cluster moves and higher-rank Mixing. Large global matching and
native SDP size guards remain enforced. The six cluster IDs are fresh v3 IDs.
Keep CPU/task and RAM choices explicit in the Slurm request; use no sudo. Do not
pull this source update into a checkout with active pinned jobs. Rebuild optional
native prerequisites and run submitted preflight/tests on class001; local checks
do not establish remote readiness. Public assignments remain unchanged.
