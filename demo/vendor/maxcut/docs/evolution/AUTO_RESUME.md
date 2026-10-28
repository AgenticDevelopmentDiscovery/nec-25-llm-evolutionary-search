# Start or resume automatically without disturbing active campaigns

The user requested that both single and manifest launches reuse an existing
campaign ID rather than fail, while explicitly keeping two campaigns running.
Use the compatible entry point `scripts/evolve_campaigns.py` for this behavior.

```bash
uv run python scripts/evolve_campaigns.py batch \
  --campaigns evolve/configs/parallel_sparse.json --jobs 2
```

The local manifest now selects fresh suite-v3 continuation IDs for three medium graphs: torus 100×100, signed
random 1,000 and torus 32×32. The user reserved the six largest unfinished graphs
for later cluster runs, using original edge count as the workload proxy. This
places dense Gaussian 1,000 (499,500 edges) on the cluster list. Two smaller
dense numerical-boundary cases are excluded from routine search. The
[complete size/score audit](../../evidence/local_cluster_split/README.md) explains
why there are fewer than six local graphs. `--jobs 2` queues three campaigns;
`--jobs 3` requests all three concurrently. Native subprocesses can use additional
cores. No controller was started by editing the manifest. Existing campaign IDs,
archives and checkpoints for the cluster-reserved graphs remain intact.

New IDs and the three explicitly migrated local IDs use the integrated
[permanent scoring timing fix](SCORING_TIMING_FIX.md). The default profile uses
15s screening. Old stopped IDs with a different source contract require the
explicit migration documented there; the launcher never silently changes hashes.

Or, from a separate terminal:

```bash
uv run python scripts/evolve_campaigns.py run \
  --instance instances/public/torus_pm_100_s31.txt \
  --campaign-id torus_pm_100_s31_parallel_01
```

The campaign ID is its directory name. Behavior is identical for both entry
paths:

| Selected ID | Action |
| --- | --- |
| Does not exist | Create it using the selected graph and configuration, then run. |
| Exists, belongs to the same graph, and is stopped | Resume its checkpoint and pending work. |
| Exists and its controller holds its kernel lock | Report `already_running`; launch nothing for that ID. |
| Belongs to a different graph | Reject before any batch launch. |
| Incomplete, changed protected inputs, or historical branch mode | Fail explicitly without overwriting evidence or migrating its contract. |

You can invoke the batch while your original two terminals are still running.
They continue in those terminals: the launcher does not transfer ownership,
change their thread settings, restart them or monitor them to completion. Its
summary lists `already_running_campaigns`; repeating the command is safe. After
they stop, repeating the same command resumes them automatically. New thread
limits apply only to controllers this launcher starts.

Saved assignments, archives, completed execution IDs, parents, pending rounds,
seeds, counters and cumulative active seconds are preserved. Omitted settings
use the saved configuration, not today's default JSON. No budget resets or
automatic budget extensions occur: exhausted runs stop again unless you
explicitly raise their cumulative caps. Runs already meeting the target return
without requesting another model proposal.

For example, to deliberately raise a stopped campaign's total limits:

```bash
uv run python scripts/evolve_campaigns.py run \
  --instance instances/public/torus_pm_100_s31.txt \
  --campaign-id torus_pm_100_s31_parallel_01 \
  --max-solver-trials 5000 --max-wall-seconds 72000 --max-rounds 400
```

For a batch, `config` and `overrides` in an entry are explicit requested updates
for existing IDs as well as initial settings for new IDs. Remove those fields
to preserve all saved settings. The prepared manifest explicitly contains
the user's saved 2500-slot/36000-second/250-call caps and 200/200/20 round caps.
Pinned input roots, provider and campaign seed cannot change
on resume; use a fresh ID for a different seed or graph. Settings for an
`already_running` ID are not applied: repeat after it stops if updates are wanted.

Every entry is prevalidated before any creation or process launch. A manifest
cannot contain the same ID twice. `--jobs` bounds controllers owned by this
invocation, not unrelated processes already running in other terminals. A batch
may mix new, stopped and externally running IDs. The low-level controller lock
remains authoritative if another CLI races a handoff; no duplicate controller
can own the checkpoint. Such a child rejection remains visible as a nonzero exit.

Each actual attempt has a unique directory:

```text
evolve/campaigns/<id>/logs/launches/<time-and-unique-suffix>/
  launcher.json          # action, argv, PID/start tick, thread caps, launcher hash
  overrides.json         # only for explicitly supplied resume updates
  controller.stdout
  controller.stderr
  result.json
```

Earlier log files remain untouched. Results continue to export under the same
campaign's `results/solutions/`; public solutions and Git remain unchanged.
The JSON summary separates target attainment, owned-process success and active
external IDs. Exit 0 for only `already_running` IDs means the request was safely
accepted, not that their targets were reached. An owned unsuccessful or
budget-limited controller produces exit 2. Ctrl-C sends SIGINT only to this
launcher's exact child processes, allows bounded graceful cleanup, and then
cleans verified owned descendants if necessary. It does not post stop flags to
externally owned campaigns. An explicit restart consumes an earlier stop flag
under the campaign lock; a new stop arriving during child startup is preserved.

Use the original read-only/status and explicit stop commands as before:

```bash
uv run python evolve_search.py status --campaign-id torus_pm_100_s31_parallel_01
uv run python evolve_search.py stop --campaign-id torus_pm_100_s31_parallel_01
```

## Entry points and source revisions

The compatible script supplies automatic same-ID reuse for `run` and `batch`.
The root CLI retains explicit `resume` and fresh-ID-only `run`/`batch` semantics.
Both execute the same fixed root controller. The launcher was originally added
outside root sources to preserve then-active contracts. After the user stopped
those runs, the timing fix was integrated through an explicit, tested source
revision, with old records and interrupted comparisons archived. Protected hashes
continue to apply; do not hot-edit controller sources during campaigns.

See [verification and preservation evidence](../../evidence/auto_resume_launcher/README.md)
and the [publication/concurrency guide](CONCURRENT_CAMPAIGNS.md). No live model
request or new public optimization was needed to implement this launcher.

The [suite-v3 guide](../portfolio/SUITE_V3.md) records source-version continuation,
120s fresh screening and inherited usage. Original `_parallel_01` checkpoints
remain immutable history under the earlier numerical base; do not resume them
against changed root sources. Use the updated manifest.
