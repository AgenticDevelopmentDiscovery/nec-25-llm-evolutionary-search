# Durability and recovery in isolated campaigns

Current execution uses per-campaign locks and manual Git commits. See
[the concurrent workflow](CONCURRENT_CAMPAIGNS.md) for launch/publication commands.

The state file is atomic and preserves cumulative active time, solver/check
reservations, model calls, current parents, archive pointer and the pending round.
Each execution has a unique directory, frozen incumbent, work budget and effective
seed. An ambiguous interrupted reservation is charged its full allowance; it is
not rerun as a fresh unbilled sample. Recovery signals only registrations inside
that campaign, checking PID/start ticks and owned descendants.

Same-ID controllers cannot coexist. Status reads atomic checkpoints without
acquiring the mutation lock. Stop writes a durable campaign flag. User resume
revokes that flag under ownership, verifies frozen source/input hashes, records
explicit cumulative cap revisions, and continues the original pending execution
schedule. Batch startup preserves stop flags posted during process initialization.

Every round freezes its source references, schedule/outcomes and narrative under
an immutable hash manifest. `closure_receipt.json` identifies that manifest with
commit=null. Recovery after a receipt/checkpoint interruption revalidates the
manifest and advances once, without requiring Git or duplicating numerical work.
Corrupt closed evidence stops integrity checking. Archives are content-addressed;
the best pointer only moves on a verified strict exact improvement. Private
results are derived copies repairable from the archive.

Campaign execution never writes the shared round log, public solutions, index or
branch. User commits are independent of the state machine. Exact public
consolidation is a separate explicit maintenance operation with a fresh prepared
snapshot, source/hash records and backups of old labels and sidecars. Its complete
receipt is written only after official scoring confirms publication. Inspect the
prepared record/backups after interrupted consolidation; there is no hidden
rollback or claim of a transactional all-files replacement.

Historical version-1 branch/commit checkpoints, logs, receipts and raw transcripts
remain unchanged. Status can read them, but new run/resume refuses to mutate or
migrate them. New campaigns have storage version 2 / execution_mode=isolated and
start from the explicitly consolidated public solution set.
