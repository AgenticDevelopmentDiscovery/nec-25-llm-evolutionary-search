# Independent campaigns and explicit consolidation

This guide describes the new isolated execution mode. It supersedes the initial
branch/automatic-commit/publication workflow. The user explicitly requested no
automatic commits, campaign-specific logs/artifacts, multiple concurrent campaigns
in one checkout, and consolidation only when requested.

The [automatic start/resume launcher](AUTO_RESUME.md) is now the recommended
entry point. It preserves existing running campaigns' pinned controller bytes.

## Histories and public results combined before implementation

Every existing campaign branch tip was an ancestor of `87ccccdb` (the user's
"before parallel campaign execution" commit). `main` was fast-forwarded from
`aff195df` to `87ccccdb`. No new commit was created, no branch was deleted, and
no remote push or tag was performed. Existing branch tips remain available.

The explicit consolidation independently validated retained experiment labels and
each campaign's content-addressed archive against the original graph. Exact
finite-decimal cut values selected the best assignment. Replaced public files
and sidecars were backed up before publication. The full 18-instance public set
now scores **0.9765192125551918**. Selection/source/hash records, snapshot labels,
old public bytes and official scores are in
[`evidence/concurrent_campaigns/consolidated/`](../../evidence/concurrent_campaigns/consolidated/).
This is assembly of existing validated results, not a new numerical campaign.
The small dense graph's **0.9999999999999997** remains its actual official score;
neither the scorer nor references were changed to round it into target success.

## Storage and ownership

Every new campaign owns:

```text
evolve/campaigns/<id>/
  campaign.lock
  campaign.json
  state.json
  config-revisions/
  base/                          # frozen implementation
  frozen/                        # immutable scoring baseline
  candidates/                    # immutable inherited variants
  archive/                       # verified assignment witnesses
  rounds/<round>/                # requests, numerical logs, scores, manifests
  logs/rounds.md                 # this campaign's narrative
  logs/codex/                    # raw/schema/JSONL/gzip model evidence
  logs/controller.stdout         # batch launches only
  logs/controller.stderr         # batch launches only
  logs/launcher*.json             # batch launches only
  logs/launches/<attempt>/        # automatic start/resume launcher attempts
  results/solutions/<graph>.txt
  results/solutions/<graph>.txt.metadata.json
  results/best.json
```

The kernel lock is per campaign. Different IDs may run concurrently, even on the
same graph, with independent budgets, RNG state, candidates, archives and logs. A
second controller using the same ID is rejected without changing its checkpoint.
ID creation is atomic. There is no branch switch, index mutation, automatic
commit or global round-log append. User commits can advance HEAD while a campaign
runs; the frozen source/input hashes remain the implementation contract. Stop
campaigns before editing those source/input files or changing native executables.

Best assignments are exported privately immediately after verified improvement,
and repaired from the immutable archive on recovery. The public `solutions/`
folder remains unchanged during campaigns. Partial generated label/sidecar copies
are recoverable; the archive and state pointer remain the source of truth. Full
assembled scoring receipts stay under each round's numerical execution directory.

Each assembled ladder score uses that campaign's frozen other-graph assignments.
It is not a continuously merged score across concurrent campaigns. Use explicit
consolidation and unchanged `evaluate.py` for the current combined public score.

## Multiple terminals on the laptop

Both commands below use the same checkout and the default 500 solver/check slots,
7200 active seconds, 20 ordinary rounds and 25 model-call cap per campaign.
These examples are prepared, not executed by the agent.

Terminal 1:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
uv run python scripts/evolve_campaigns.py run \
  --instance instances/public/torus_pm_100_s31.txt \
  --campaign-id torus_pm_100_s31_parallel_01
```

Terminal 2:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
uv run python scripts/evolve_campaigns.py run \
  --instance instances/public/rand_pm_1000_s23.txt \
  --campaign-id rand_pm_1000_s23_parallel_01
```

`run` also accepts `--max-solver-trials`, `--max-wall-seconds`, `--max-rounds` and
`--max-codex-calls`, or `--config` for a separate JSON file. Resolved settings are
stored in the initial config revision. Automatic commit/publication toggles must
be false; old custom configs with true are rejected with an actionable message.
Concurrency does not make candidates inside each campaign parallel.
If running the same graph twice, use different `campaign_seed` values in configs
or batch overrides for independent stochastic trajectories. Different names alone
do not change deterministic seed derivation.

## Several campaigns from one terminal

Review/edit the explicit three-medium-graph/ID list for local execution in
[`evolve/configs/parallel_sparse.json`](../../evolve/configs/parallel_sparse.json),
then use this alternative to the two-terminal commands:

```bash
uv run python scripts/evolve_campaigns.py batch \
  --campaigns evolve/configs/parallel_sparse.json \
  --jobs 2
```

Both launch methods reuse the same IDs: stopped campaigns resume, and active
ones are reported without a second controller. The launcher validates all entries first,
then runs at most `--jobs` controllers simultaneously and queues remaining jobs.
Each entry may select `config` and `overrides`. No unlisted graph is searched.
`--jobs 2` queues the three selected local campaigns; `--jobs 3` requests all three
concurrently. The six largest unfinished graphs, ranked primarily by edge count,
are reserved for the cluster and excluded from this local manifest. See the
[audited split](../../evidence/local_cluster_split/README.md).
BLAS/OpenMP thread counts are set to one for each child, while a native method
can retain its real two MPI ranks. Two campaigns can issue two concurrent Codex
requests and consume both campaigns' usage. This is not recursive agent spawning.

The batch final JSON lists each status, cut and exit code. `batch_complete` means
all launched processes finished; `all_targets_met` separately reports success.
CLI exit is 2 if any target remains unmet or any controller exits unsuccessfully.
`all_processes_succeeded` is separate from whether the initial/best labels meet
the target, so an integrity failure cannot be hidden by an already-good incumbent. A numerical budget stop is an honest
outcome, not a failed launch. Increasing `--jobs` uses more CPU/RAM and may hit
account/service limits; the launcher does not invent an account-wide token budget.

Ctrl-C stops queuing new graphs and signals only its own active
children. The batch startup preserves a concurrently posted stop flag, including
the short interval before a child has acquired its campaign lock. Owned cleanup
never kills another terminal's unrelated campaign. Re-running the manifest
resumes stopped IDs without resetting their cumulative usage. IDs still running
in another terminal are not adopted. See the [automatic resume rules](AUTO_RESUME.md).

## Inspect, stop, resume and commit manually

```bash
uv run python evolve_search.py status --campaign-id torus_pm_100_s31_parallel_01
uv run python evolve_search.py stop --campaign-id torus_pm_100_s31_parallel_01
uv run python evolve_search.py resume --campaign-id torus_pm_100_s31_parallel_01
```

Resume consumes a deliberate old stop flag and preserves all cumulative usage.
Explicit cap overrides change total limits, not additional allowances. Before a
model request the controller requires enough numerical slots for one minimal
novel child and paired comparison. An honest zero-work plateau decision is
accepted without requiring positive evaluation time/repeats.

Round closure verifies an immutable manifest and records a closure receipt;
the next round does not wait for Git. When ready, review the completed campaign
directory and commit chosen files yourself. No commands in the new loop stage,
commit, switch branches, push or tag. Historical branch-based campaigns remain
readable; this controller refuses to resume them or rewrite their frozen version.
Start a new ID from the now-consolidated public assignments instead.

## Combine results only when requested

After the desired campaigns finish, explicitly publish the best verified labels:

```bash
uv run python scripts/consolidate_solutions.py \
  --output evidence/combined_after_parallel_01 \
  --publish
uv run python evaluate.py --json evidence/combined_after_parallel_01/check.json
```

Use a fresh output directory each time. Omitting `--publish` creates only a review
snapshot. The script does not solve graphs, call Codex, change Git or delete old
results. It retains backups and a prepared-publication record, and checks the
public score after writing. If an interruption occurs during publication, inspect
that record/backups before repeating the operation; no automatic rollback or
fabricated complete receipt is claimed. Root public labels can use a different
equivalent sign-text format from archive bytes; independent values and sidecars
are checked rather than treating text formatting as algorithmic novelty.

On class001, use the [Slurm instructions](CLASS001.md). Submit independent
campaign jobs through `sbatch`; do not launch the laptop batch directly on a
login node. Concurrent native MPI placement within one multi-campaign Slurm job
has not been cluster-verified.
