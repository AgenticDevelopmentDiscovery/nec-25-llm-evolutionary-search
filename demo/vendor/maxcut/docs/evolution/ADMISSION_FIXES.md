# Admission fixes after the first public campaign

Historical maintenance report: the later [concurrent campaign mode](CONCURRENT_CAMPAIGNS.md)
keeps these admission rules and replaces automatic branches/commits/publication
with private results and manual commits. Existing source-pinned campaign evidence
remains unchanged.

The user requested fixes for rigid comment validation and repeated duplicate
proposals. This is maintenance of the trusted framework, not an evolved solver
variant or evidence of a new public cut. The earlier raw model responses,
rejections, rounds and public assignments remain preserved.

## Observed failures and changes

In `rand_pm_1000_s23_campaign_01`, round 7's correction supplied explanations at
the ends of its Python statements. The old validator recognized only comments
on preceding lines. The source was rejected for formatting before any numerical
comparison, not because the proposed search had been demonstrated incorrect.
The validator now accepts either a preceding standalone comment or a real inline
comment on the statement. For a multiline statement/header, a comment on its
closing line also qualifies. Python tokenization distinguishes a real `#` comment
from a hash character inside a string. A nested body's comments cannot substitute
for its containing function/branch/loop header explanation. Missing explanations
identify the line and bounded statement text in the correction request. Teaching
docstrings, numerical import/I/O restrictions and independent correctness checks
remain required. Comments/docstrings still do not create candidate novelty.

Repeated proposals also occurred because the model saw the current parents and
only the last three round summaries. It did not receive a complete catalogue of
the immutable candidates already present. Every new planning context now includes
all known candidates, with IDs, resolved backend configurations, policies, stages,
source identities, creation rounds and categories. This includes non-survivors
and baseline candidates. The prompt explicitly defines `parameter`, `state_policy`
and `algorithm_policy`, explains inheritance, and asks for fewer useful children
rather than filling slots with repeats.

The controller still independently computes semantic identity. If a valid batch
mixes novel and duplicate children, it records the duplicate handles and matching
artifact IDs, admits only novel children, and removes the duplicate handles from
the effective comparison order. It does not overwrite the existing artifact,
bill numerical checks/trials for the duplicate or claim another evolved variant.
Duplicates between siblings receive the same treatment. The original structured
plan is saved unchanged alongside the reduced effective schedule. Skipped handles
appear in round state, selection JSON and the human summary.

An entirely duplicate continuation is still rejected with the matching IDs and
gets at most the existing single correction attempt. A second all-duplicate plan
stops honestly. No random replacement or unchecked source is substituted. These
changes reduce avoidable rejection; they cannot guarantee that a model proposes
novel, correct or effective strategies.

## Saved campaign compatibility

The user's first campaign was resumed again before maintenance began. A graceful
stop was requested and the repository lock was verified free before source edits.
The checkpoint is interrupted with its pending round/reservation retained. Its
archive remains cut **1097**, target **1098**, graph score **0.999154334038055**,
and recorded assembled ladder score **0.9723102407387957**. These are preserved
campaign results, not new results from this maintenance task.

The original campaign pins its controller/validator code and numerical base.
Changing those manifests or its saved base in place would conceal the version
under which earlier evidence was produced. This maintenance therefore **does not
migrate or resume it**. The CLI now detects changed protected files before applying
resume config/checkpoint changes and explains the version mismatch. To use the
fixes for another public search, the user
must explicitly initiate a fresh campaign ID after reviewing the changes:

```bash
uv run python evolve_search.py run \
  --instance instances/public/rand_pm_1000_s23.txt \
  --config evolve/configs/default.json \
  --campaign-id rand_pm_1000_s23_campaign_02
```

This command has not been executed. It snapshots the updated code and selects
the best valid starting assignment from the configured retained/public folders,
including the preserved cut-1097 public assignment. It creates a separate budget
and candidate population; it is not continuation of the old population or a
reset of the original campaign's recorded expenditure. Keep both campaign
histories when reporting total work. Resuming the original requires its original
recorded source checkout, where its old admission behavior still applies.

## Verification and preservation

The new regressions cover inline/preceding identity equivalence, multiline
comments, hashes inside strings, missing compound-header comments, forbidden
imports/I/O, precise mutation categories, complete known-candidate context,
existing and sibling duplicates, raw plan preservation, malformed schedules,
bounded all-duplicate correction and a real sandboxed numerical fixture.
The fixture uses inline-commented source, skips a duplicate sibling, validates
only one child and reaches trap cut 10 through the unchanged scorer. It uses the
explicit fixture provider, not a real model call or a public optimization run.

The [evidence directory](../../evidence/evolution/admission_fixes/) contains
regression stdout/stderr, machine-readable outcomes, a read-only replay of the
actual rejected source, and before/after preservation receipts. No real Codex
call, public solver run, remote job, push or milestone tag is part of this fix.

The final full suite passed **103 tests in 44.807 seconds**, including 12 new
admission/version-boundary regressions. The prior 102-test run before the final
resume guard also passed and is retained separately. See
[final raw output](../../evidence/evolution/admission_fixes/regression_final.stderr)
and the [run receipt](../../evidence/evolution/admission_fixes/regression_final.json).
The [actual rejected-source replay](../../evidence/evolution/admission_fixes/rejected_source_replay.json)
confirms static acceptance without executing it on the public graph. All **3749**
hashed saved campaign, solution and official files are unchanged since the
post-stop snapshot, with no added files in the original campaign namespace
([preservation receipt](../../evidence/evolution/admission_fixes/preservation_after.json)).

An additional read-only score check of `solutions/` alone returned
**0.961172030194863**. This folder is not the campaign's assembled set, which
selects/fixes other graphs from both configured retained/public directories and
records **0.9723102407387957**. Both measurements are labeled separately in the
preservation receipt. No labels were changed to reconcile those distinct sets.
