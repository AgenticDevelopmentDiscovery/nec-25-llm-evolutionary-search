# Current architecture: private concurrent campaigns

The current controller supports multiple independent campaigns in one checkout.
Read [the complete concurrent workflow](CONCURRENT_CAMPAIGNS.md) for storage,
commands, numerical budgets, manual commits and explicit consolidation.

Each campaign owns one kernel lock, frozen source/input/scoring snapshots,
immutable candidate population, monotone verified archive, round evidence and
private best-assignment exports. The checked-out branch and Git index are not
modified by execution. Different IDs can run concurrently. The compatible launcher
automatically resumes stopped IDs and reports active owners; the low-level lock
still rejects duplicate controllers. There is no shared mutable round log or public publication
in the campaign loop.

`evolve_search.py` exposes run/status/stop/resume/batch and diagnostics.
`scripts/evolve_campaigns.py` adds automatic ID reuse for single and batch launches
while preserving the pinned root CLI/controller bytes of existing campaigns.
`evolution_batch.py` launches only manifest-selected graphs with bounded
concurrency. `evolution_controller.py` owns each state machine and cumulative
caps. `evolution_candidates.py` validates source, identity and inheritance.
`evolution_worker.py` runs serial numerical candidates using pinned portfolio
modules. `evolution_evaluation.py` independently scores labels and stores
immutable witnesses. `evolution_common.py` supplies exact diagnostics, campaign
locks and owned-process primitives; `evolution_reaper.py` handles orphan cleanup.
The explicit `scripts/consolidate_solutions.py` is the separate publication path.

All candidate comparisons in a round share a frozen incumbent. The archive can
improve after every validated trial, independent of which candidate survives.
Generated results update privately immediately; immutable closure manifests and
receipts permit recovery without requiring a Git commit. Raw transcripts are
stored unedited and gzip-checked inside this campaign's logs/codex directory.

Research code can use narrow numerical hooks inside a read-only filesystem
sandbox with one writable trial directory. Objective, official files, source
manifests, bounds/proof classification and independent scoring are protected.
Every new child passes the signed/ownership/scope examples. Exact/native methods
retain their true adapters; no unsupported warm start or guard increase is
invented. Target matching and mathematical optimality remain distinct.

Other graphs are frozen scoring inputs within a campaign. Another campaign may
improve its own graph independently, but no combined global score is claimed
until explicit consolidation. Existing branch/commit campaign evidence remains
unchanged historical data and is not silently migrated to this storage version.
