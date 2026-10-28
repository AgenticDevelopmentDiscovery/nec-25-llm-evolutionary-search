# Review after session reconnection

**Subsequent repair verified:** the full-path gaps identified below are now
covered by candidate3 (jobs59849/59850,178 tests and12 complete comparisons).
Use [the completion guide](CLASS001_LARGE_COMPLETION_REPAIR.md) for the new
three-graph preparation/resume. The review below records the earlier evidence
and why the old dense/large continuation commands were deferred.

October 21, 2026, evening America/Chicago. The requested handoff is actually
`instruction_Tamim/CLASS001_SESSION_HANDOFF.md` (the name includes `001`).
This is a read-only implementation/evidence review followed by documentation
corrections. No scheduler request, numerical test, optimization, model call,
source migration, public solution update or Git action was executed.

## Confirmed work

- Metadata repair: job 59836 passed 16 tests; preparation 59837 completed. Its
  five overlay and four support files match their seal. The previous continuation
  `campaign_id` mismatch is repaired. The original four-file v4 writer produced
  metadata that failed on the real round-1 path; its earlier 172 tests missed
  that path. The later generated continuation regression addresses that gap.
- Other-run repair: job 59842 passed 11 tests and a generated dense worker probe.
  Its four overlay/five support files and full metadata baseline still match
  the passing report. This validates the tested retry/deadline/continuation
  behavior; it is not large-graph numerical completion evidence.
- All 31 original root Python files match the pre-v4 snapshot. Saved archive
  assignment hashes match for all six root campaigns and both metadata-runtime
  campaigns. This is a byte-identity check, not a new numerical rescore.
- Neither other-v1 nor large-v1 runtime exists at inspection. No automatic
  source change or fresh campaign has been silently applied for either version.

## Corrections and remaining gaps

1. **Dense test does not cover its production aggregate path.**
   `tests/test_class001_other_repair.py:259` calls `launch_trial` with a direct
   30s worker allowance. `Campaign.evaluate_schedule` first charges integrity/
   setup and reserves verification within the configured 60s ordinary aggregate.
   The saved old dense round-1 t0000 requested 19.645s of inner work and hit an
   outer timeout at 21.957s. The new direct worker probe took 24.611s (tabu) and
   23.232s (annealing). Its adaptive deadlines may behave differently under a
   shorter allowance, so these numbers do not prove that the repair fails.
   They do establish that the passing direct probe is insufficient evidence of
   production completion. Defer dense preparation/resume. Add a generated
   dense1000 test through actual open_round -> build_schedule ->
   evaluate_schedule for 60s ordinary and 120s screening; retain official scorer
   receipts, process logs, eligibility and total elapsed time. New tests/code
   need separate verification; keep the passed other-v1 seal and report intact.
2. **Large-worker diagnosis overstated missing artifacts.** Both signed and
   positive metadata-runtime campaigns' round-1/round-3 t0000 directories have
   `work/pre_assignment.txt`, each 300000 bytes. Worker stderr is empty, final
   result/stage directories are absent and exits are timed-out -15. This shows
   partial preparation, not termination before any preparation output. The
   incident JSON already lists the pre-assignment file. Correct the handoff;
   phase measurements inside a Slurm allocation are still required.
3. **Two 100000-node graphs are not ready to resume.** The 59839 array stopped
   after 26/26 and 20/20 ordinary trial timeouts. Its final models returned an
   operational plateau, not proof or search exhaustion. Best cuts 112766 and
   361017 remain saved. The large-v1 source/helper are unfinished and unsealed;
   manifest, Slurm scripts and tests are absent. Its proposed 120s ordinary
   aggregate is a profile change, not a measured fix. Complete generated signed
   AND positive100000/~500000-edge full-path probes, failure diagnostics and the
   pre-model `evaluation_blocked` guard tests before another public continuation.
   Preserve the immediate metadata parents, all histories and usage, and all
   ancestor kernel locks. Leftover `dense` wording in the unfinished helper
   should be corrected when completing it; it is not a usable dense repair.
4. **Old commands are historical.** Do not resubmit the old six-array, repeat
   metadata preparation, reduce limits of finished 59839 elements, or regenerate
   the five-hour cutoff. Keep the established cutoff below. No new claim about
   live scheduler ownership was made in this review; the dedicated launchers
   still enforce campaign/ancestor locks.

## What the user can submit now

From the original root, restore:

```bash
export CLASS001_PYTHON_MODULE=''
export CLASS001_EXTRA_MODULES=opensn/gcc/15.2.0-fortran
export CLASS001_PYTHON=/usr/bin/python3.11
export PATH="$HOME/.vscode-server/extensions/openai.chatgpt-26.1007.21434-linux-x64/bin/linux-x86_64:$PATH"
export CLASS001_STOP_EPOCH=1792638620
export CLASS001_OTHER_VERIFICATION="$PWD/evidence/class001/other-v1-59842.hWI1WD/verification.json"
mkdir -p logs/slurm
TZ=America/Chicago date -d "@$CLASS001_STOP_EPOCH"
```

The cutoff is October 21 at **22:10:20 CDT**. Two cleanup minutes are reserved;
queueing consumes the window. Expired launchers should refuse work. The original
five-hour maximum is not a new five hours from reconnection. These manual
submissions can make framework model calls:

```bash
sbatch --parsable --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=05:00:00 \
  --array=0-1%2 scripts/class001_other_resume.sbatch capacity \
  "$CLASS001_OTHER_VERIFICATION"

sbatch --parsable --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=05:00:00 \
  scripts/class001_other_resume.sbatch torus "$CLASS001_OTHER_VERIFICATION"
```

The capacity array resumes signed10000 and positive10000 using their original
IDs/model and at most two additional retries per new capacity failure. Torus316
gets the already-authorized extension only through the remaining shared window.
Each element requests 2 tasks x 5 CPUs and 15G; three elements request 30 CPUs
and 45G in total. Their scripts shorten the Slurm limits to the remaining
window, so the requested five-hour limit does not extend the cutoff.

Dense and both100000 remain deferred. No correct large-v1 verification command
exists yet, because its planned job script and test file are missing. Numerical
work, including completing the probes, must run through a user-submitted Bash
Slurm verification job; do not execute the partial helper as a finished repair.
