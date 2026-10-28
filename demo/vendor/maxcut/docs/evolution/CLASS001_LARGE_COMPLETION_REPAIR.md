# Full campaign completion repair and verification

**VERIFIED candidate3:** job59849 passed all12 complete comparisons and six new
repair test methods; job59850 passed all172 existing regressions. Finished
October21 at21:03 CDT. Passing combined test receipt:
`evidence/class001/large-v1-59849.K4PG4x/release_verification.json`.
All original reports/source snapshots and failed attempts remain preserved.
The following older candidate descriptions are chronological history.

October 21, 2026. User explicitly requested finishing the repair and verifying
complete generated trials through Slurm. This authorizes the bounded verification
submission; public preparation/resume and paid models remain separate actions.
No root or previously verified source bundle is changed. All new sources live
under `staging/class001_large_v1/source/`, with their own manifest and receipts.

Actual verification: first candidate job59846 failed a full dense screening
comparison: valid tabu output exceeded 120s at 122.537s and was correctly
nonselectable. Failed snapshot and source manifest remain in its evidence.
Candidate revision2 is being checked in 59847; existing regression suites for
its exact source snapshot run in 59848. Neither is a passing claim yet.

Superseding result: revision2 failed honestly. Dense screening now passed
(100.556s tabu, 90.315s annealing) and ordinary tabu passed at 39.303s/60s.
Ordinary annealing finished cooling, but its optional polish setup exceeded
the 4.588s stage allowance (actual 5.424s); it was correctly censored. Job59848
passed 98/99 controller regressions; the failed assertion required the original
verification reserve to remain a separate receipt field from added controller
overhead. No old test was relaxed. Revision3 keeps the reserve fields separate
and bounds optional polish using measured initialization cost and an explicit
return reserve. Raw SA labels/cuts and skipped-polish telemetry remain visible;
incomplete/overrun schedules remain censored. It runs in job59849, with a fresh
regression job against that exact snapshot. Reports are pending.

Revision2 reuses deeply immutable original-loader graph snapshots only inside
trusted controller verification, with raw-byte hashing on every lookup and
before/after load hashes. At most two graphs are cached. Numerical workers keep
their independent original Graph and all mutation checks. Objectives, exact
rechecks and official scorer are unchanged. A generated test checks deep
immutability and detects changed bytes even if size and mtime are preserved.
Controller setup/check time is measured and added to the retained verification
reserve; no end-to-end allowance or global ledger is enlarged by this repair.

The original three latest reruns (59843/59845) failed infrastructure preflight:
Codex was missing from their inherited PATH. Their displayed capacity/exhausted
states are old checkpoints; no recovery wrapper launched. Restore the known
extension executable directory before resubmission; do not change source guards
or infer that the retry/extension ran. The executable still exists.

## Repair and test scope

- Preserve tested direct sandboxed local kernels and absolute worker deadlines.
  Add flushed JSONL phase events covering imports, graph load, ownership hashes,
  preparation, search stages and result serialization. Timed-out observations
  carry structured failure and last-phase information into controller evidence.
- Before another mutation request, stop with `evaluation_blocked` when the last
  ordinary schedule has no valid selectable comparison. Valid operational
  fallback/censored witnesses do not justify another paid mutation request.
- Proposed large-graph profile: 120s aggregate ordinary and screening trials;
  dense remains 60s ordinary/120s screening. Original verification reserves,
  source/sandbox guards, backend-specific work caps, size guards, global time
  and model-call ledgers remain enforced. A larger trial is not itself proof
  that the performance issue is fixed.
- Twelve real generated comparisons: dense1000 complete signed graph (499500
  edges), signed100000 and positive100000 (500000 edges each); unchanged
  annealing parent and tabu control; screening and ordinary rounds. All use
  actual `Campaign.open_round -> build_schedule -> evaluate_schedule`, including
  source checks, setup, Bubblewrap, independent official scoring and archive
  handling. Require exit 0, valid and selectable returned labels, official score
  receipts and aggregate elapsed <= the requested allowance. Retain input files,
  requests, raw logs, phases and failures. No public graph optimization/model.
- Generated regression checks cover canonical continuation context, complete
  copied history, cumulative spending/counters and best labels, refusal of an
  existing child, actual timeout diagnostics, and all ancestor locks remaining
  held across a launcher-to-controller style process handoff. Original campaigns
  and previously sealed metadata/other-run sources remain untouched.

## Bounded verification

From the original root, with the established module/Python/PATH exports:

```bash
export CLASS001_PYTHON_MODULE=''
export CLASS001_EXTRA_MODULES=opensn/gcc/15.2.0-fortran
export CLASS001_PYTHON=/usr/bin/python3.11
export PATH="$HOME/.vscode-server/extensions/openai.chatgpt-26.1007.21434-linux-x64/bin/linux-x86_64:$PATH"
export CLASS001_STOP_EPOCH=1792638620
mkdir -p logs/slurm
sbatch --parsable --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=00:35:00 \
  scripts/class001_large_repair.sbatch verify \
  "$PWD/evidence/class001/other-v1-59842.hWI1WD/verification.json"
```

The agent may submit this verification under the user's explicit latest request.
Do not duplicate a running verification. The shared cutoff remains October 21
22:10:20 CDT, with two cleanup minutes. A stage has at most 300s, tests 1700s,
bounded interrupt/kill cleanup 30s. A verification.json is written only when
all twelve complete comparisons and the regressions pass for the sealed bytes.
Failures preserve their source snapshot; any fixes get a newly sealed candidate
and a fresh verification job, never a rewritten historical report.

## Later preparation and public run

Passing verification is now available. The helper can prepare three explicit
new numerical bases in `staging/class001_large_v1/runtime/`: two search-v5 large
continuations and `dense_gauss_1000_s24_class001_recovery_v2_01`. It validates
closed parent evidence, retains complete histories, inherits all counters/time
and best labels, charges preparation, and keeps all ancestor locks. Partial
destinations are preserved and refused. No old hashes or budgets are reset.

The dedicated resume script requires a completed `large_transition.json` and
array indices 0/1/2. It retains original campaign ledgers and the original shared
cutoff, with a maximum requested 2h30m allocation. Public preparation, rerun and
model calls are not part of the generated verification request. Give exact
next commands only after reviewing the actual verification outcome.

## Exact next user commands after passing verification

From the ORIGINAL root, restore the full environment. This PATH fixes the
preflight failure in the earlier capacity/Torus submissions too.

```bash
export CLASS001_PYTHON_MODULE=''
export CLASS001_EXTRA_MODULES=opensn/gcc/15.2.0-fortran
export CLASS001_PYTHON=/usr/bin/python3.11
export PATH="$HOME/.vscode-server/extensions/openai.chatgpt-26.1007.21434-linux-x64/bin/linux-x86_64:$PATH"
export CLASS001_STOP_EPOCH=1792638620
command -v codex
mkdir -p logs/slurm
sbatch --parsable --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=00:30:00 \
  --job-name=maxcut-completion-prepare \
  scripts/class001_large_repair.sbatch prepare \
  "$PWD/evidence/class001/large-v1-59849.K4PG4x/release_verification.json"
```

This performs no search/model calls. Require COMPLETED/exit0 and
`staging/class001_large_v1/runtime/large_transition.json` with all three completed
campaign receipts. Partial/existing destinations remain review errors. Only
after preparation actually succeeds, user may start public search:

```bash
cd staging/class001_large_v1/runtime
sbatch --parsable --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=02:30:00 \
  --array=0-2%3 scripts/class001_large_resume.sbatch
```

Indices0/1 are signed/positive100000, index2 dense1000. Each element requests
10 CPUs and15G; they retain spent counters/time. The shared original cutoff
22:10:20 CDT may stop them sooner than2h30m. No target attainment is guaranteed.
The other three original campaigns use their original recovery wrappers and
remain separate; no original ancestor should run concurrently with its new copy.

Monitor the new three from the new runtime:

```bash
watch -n 30 '/usr/bin/python3.11 -I -B scripts/class001_status.py --manifest evolve/configs/class001_large_completion_v1.json --details'
```
