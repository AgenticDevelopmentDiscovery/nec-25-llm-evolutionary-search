# Fix the current environment blockers

October 21 runtime update: the user has gracefully stopped all six campaigns.
Array 58565's blockers were the five-second scorer ceiling and too-short owned
cleanup confirmation, rather than missing modules. Runtime v3 and a preserved
source-contract migration are prepared. Use the `repair-runtime` job in
[the current command guide](CLASS001_COMMANDS.md); no dependency reinstall or
module search is needed for these failures. This repair is not runtime verified
until the user submits that job. All older failure receipts remain intact.

Current status after suite-v3 integration: user jobs 58524/58525 already resolved
the interpreter/venv blocker, and job 58527 established actual CLI access before
its separate scoring failure. Keep the existing environment. The fetched commits
did not change the lockfile or Python dependency specification. These commands
are recovery procedures, not instructions to repeat successful setup. Use
[the current verification commands](CLASS001_COMMANDS.md) for this source version.

Run from the project root. These commands are prepared for the user to submit;
the agent has not submitted them. They make no model calls or public graph runs.

Job 58521 installed packages successfully, but preflight 58522 and retained
diagnostic 58523 established that the module Python lacks `_ctypes`. The same
Slurm diagnostic imported ctypes successfully with existing `/usr/bin/python3.11`.
Use that interpreter to recreate the environment. The lockfile already contains
its Python 3.11 dependency branches; do not edit or regenerate the lockfile.

## Select the working modules and existing Codex executable

```bash
export CLASS001_PYTHON_MODULE=''
export CLASS001_EXTRA_MODULES=opensn/gcc/15.2.0-fortran
export CLASS001_PYTHON=/usr/bin/python3.11
export PATH="$HOME/.vscode-server/extensions/openai.chatgpt-26.1007.21434-linux-x64/bin/linux-x86_64:$PATH"
mkdir -p logs/slurm
```

System Python 3.11 passed the ctypes import in Slurm job 58523, locked sync in
58524 and infrastructure preflight in 58525. Recheck the new code in submitted
verification jobs; do not recreate the environment solely because Git advanced.
Codex version/help compatibility passed in job 58522. Exporting its PATH makes
it discoverable to subsequent jobs submitted with `--export=ALL`. It does not
copy credentials, change global shell initialization or invoke a model.

The versioned extension path can change after a VS Code update. Recheck the
executable path then, or use an approved persistent standalone account-local
installation. [Official CLI documentation](https://learn.chatgpt.com/docs/codex/cli)
describes standalone installation and sign-in. No new installation is needed
just to test the existing binary, and authentication remains a separate condition.

## Create the cluster virtual environment

```bash
sbatch --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 \
  --mem=15G --time=00:20:00 \
  --job-name=maxcut-sync311 \
  scripts/class001_setup.sbatch sync \
  --extra matching --extra milp --extra tesb
```

This uses the user's ten-CPU allocation preference for one setup job, not an
array. uv runs `sync --locked` with the selected cluster interpreter inside the
allocation, recreates `.venv` for the selected interpreter as needed and installs
the requested Python dependencies. The sync action now checks ctypes before
asking uv to change the environment. Previous failure evidence is retained.
It may need compute-node package network access. The step is bounded at 900
seconds plus cleanup. Failed downloads/builds are retained, not retried silently.
These Python extras do not compile the separate optional native solver trees.

Review `logs/slurm/maxcut-sync311-JOBID.out` and `.err`. The outer output identifies
`evidence/class001/setup-JOBID.*/`, which contains `sync.stdout`, `sync.stderr`
and `status.txt`. Slurm COMPLETED/0:0 and step exit_code=0 establish sync success.
If interpreter validation fails, `interpreter.stderr` retains its traceback.

uv supports selecting an existing interpreter by executable path; see
[its Python-version documentation](https://docs.astral.sh/uv/concepts/python-versions/#requesting-a-version).

## Only after sync succeeds, check readiness

Keep the exports above in the submitting shell, then run:

```bash
sbatch --export=ALL --nodes=1 \
  --ntasks=2 --cpus-per-task=5 \
  --mem=15G --time=00:10:00 \
  scripts/class001_preflight.sbatch
```

This verifies portable input bytes, checks actual backend availability and Codex
version/help compatibility, and tests Bubblewrap/owned cleanup. It makes no
model call and runs no public optimization campaign. A passed preflight still
does not verify authentication/egress or sandboxed native MPI. Keep missing native
methods explicitly unavailable until their separate pinned builds/checks pass.

Do not launch the six-graph array until the remaining readiness conditions are
reviewed. No old manifests, source checks, protected inputs or solutions were
changed for these commands.
