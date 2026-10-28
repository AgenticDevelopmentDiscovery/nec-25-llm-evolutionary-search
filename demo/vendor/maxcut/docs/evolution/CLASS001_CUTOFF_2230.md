# Explicit user extension to October21 22:30 CDT

User explicitly asked to increase the cutoff to22:30. New epoch1792639800
supersedes old1792638620 by1180 seconds (19m40s). This is a fixed requested
extension, not a renewed five-hour window. Assignment deadline remains23:59.

No running or verified source file, original verification report, transition
marker, source hash, checkpoint or historical campaign was edited. The separate
immutable authorization is
`evidence/class001/cutoff-2230-v1/authorization.json`. The new launcher verifies
both original passing source bundles, their exact report hashes and the new
policy's own code hashes before permitting the extension. It preserves the
existing ancestor locks and normal framework budget/config-revision handling.
The completion limit adds at most the authorized delta, retains the original
ten-hour ceiling, never resets consumed usage, and also clips to the remaining
absolute window. Original capacity/Torus behavior keeps its bounded retries and
previously authorized extension, under the new fixed cutoff.

**59855 PASSED:** six policy/limit/receipt/expiry tests in0.136s, Slurm exit0.
Evidence/proof: `evidence/class001/cutoff-2230-59855.5JqAg1/verification.json`.
No model call/public job was submitted. Existing three running jobs are array
59852 and still have the old in-memory watchdog. Merely exporting a new epoch
or changing only Slurm TimeLimit cannot change that running watchdog.

## Queue the running three's continuation

From the ORIGINAL root:

```bash
export CLASS001_PYTHON_MODULE=''
export CLASS001_EXTRA_MODULES=opensn/gcc/15.2.0-fortran
export CLASS001_PYTHON=/usr/bin/python3.11
export PATH="$HOME/.vscode-server/extensions/openai.chatgpt-26.1007.21434-linux-x64/bin/linux-x86_64:$PATH"
export CLASS001_STOP_EPOCH=1792639800
export CLASS001_CUTOFF_PROOF="$PWD/evidence/class001/cutoff-2230-59855.5JqAg1/verification.json"
mkdir -p logs/slurm
sbatch --parsable --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=01:45:00 \
  --dependency=afterany:59852 --array=0-2%3 \
  scripts/class001_cutoff_extension.sbatch completion "$CLASS001_CUTOFF_PROOF"
```

Dependency waits for the current array to finish; it does not reserve CPUs while
pending. Same three current campaign IDs, same histories/labels/source version,
all usage carried forward. They receive only the remaining time to22:30, with
two minutes reserved for cleanup; one hour45m remains an upper bound. Current
public jobs and their pinned launchers need no interruption or modification.
Already reached targets do not launch another continuation. Existing source,
cleanup and ownership errors still stop/refuse work rather than being ignored.
Do not duplicate an already queued extension array.

## Original two10000-node graphs and Torus316

Their earlier59843/59845 submissions failed before search because Codex PATH
was missing. If they have not since been submitted, the same environment above
allows the USER to start them directly under the new authorized cutoff:

```bash
sbatch --parsable --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 --mem=15G --time=01:45:00 \
  --array=0-2%3 scripts/class001_cutoff_extension.sbatch original \
  "$CLASS001_CUTOFF_PROOF"
```

Indices0/1 are signed/positive10000, index2 Torus316. This command can make model
calls and remains manual. Original failure/status guards still apply; already
active/advanced IDs are not silently copied or reset. New and old continuation
launchers cannot overlap the same protected ancestry. Every element requests
10CPUs/15G. All six combined request60CPUs/90G, subject to actual scheduling.

Monitor checkpoints in their respective original/new runtime roots as before.
Outer extension logs are in original-root `logs/slurm/maxcut-cutoff-2230-*`.
Do not change old verification/transition stop_epoch fields to force acceptance.
