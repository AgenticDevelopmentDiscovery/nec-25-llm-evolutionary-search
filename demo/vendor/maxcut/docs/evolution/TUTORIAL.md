# Run, monitor and resume campaigns

Use the [current concurrent campaign guide](CONCURRENT_CAMPAIGNS.md) for complete
commands, manual commits and explicit publication. New campaigns make no Git
mutations and write only inside their own directory.

```bash
uv run python evolve_search.py doctor
uv run python evolve_search.py plan --config evolve/configs/default.json --instance instances/public/torus_pm_100_s31.txt
uv run python scripts/evolve_campaigns.py run \
  --instance instances/public/torus_pm_100_s31.txt \
  --campaign-id torus_pm_100_s31_suite_v3_01
```

New IDs use [timing runtime v2](SCORING_TIMING_FIX.md), with the [suite-v3 profiles](../portfolio/SUITE_V3.md): 120s screening and 30s admission.
For new IDs, defaults are 20 rounds, 500 solver/check slots, 7200 active seconds, 25 Codex
calls and serial candidate trials. Independent IDs may run concurrently in
separate terminals. Alternatively, queue the three local medium graphs with two workers:

```bash
uv run python scripts/evolve_campaigns.py batch \
  --campaigns evolve/configs/parallel_sparse.json --jobs 2
```

Both methods create new IDs or automatically resume existing stopped IDs. Active
IDs are reported without another controller. The [compatible launcher](AUTO_RESUME.md)
uses the integrated controller and its verified source contract. Inspect/stop/resume one exact ID:

```bash
uv run python evolve_search.py status --campaign-id torus_pm_100_s31_suite_v3_01
uv run python evolve_search.py stop --campaign-id torus_pm_100_s31_suite_v3_01
uv run python scripts/evolve_campaigns.py resume --campaign-id torus_pm_100_s31_suite_v3_01 \
  --max-solver-trials 5000 --max-wall-seconds 72000
```

Overrides are cumulative caps. An explicit resume revokes the old stop flag;
other campaign state remains untouched. Logs, round manifests, private best
labels and scoring receipts are under `evolve/campaigns/<id>/`. The public
`solutions/` folder changes only through explicitly requested consolidation.

Historical branch-based campaigns remain inspectable. Their code/source/path
identity is pinned, so this controller refuses to resume them or alter their
manifests. Create a new ID using the consolidated public incumbents. Keep the
working source and native executable bytes unchanged while campaigns are active.

For development-only generated tiny graphs:

```bash
uv run python evolve_search.py test --provider fixture-test --output /tmp/evolution-fixture-new
# Only when explicitly requesting a real bounded model integration check:
uv run python evolve_search.py test --provider codex --output /tmp/evolution-live-new
uv run python -m unittest discover -s tests
```

Fixture checks are labeled fixture-test and do not demonstrate live model
reasoning. The historical real integration passed with Codex CLI 0.163.0; this
concurrency maintenance did not request another real model call. Use the synced
`.venv/bin/python` if the host Snap uv cannot start inside an outer tool sandbox.
On class001, numerical work must use Slurm rather than these laptop commands on
a login node; see [the cluster guide](CLASS001.md).
