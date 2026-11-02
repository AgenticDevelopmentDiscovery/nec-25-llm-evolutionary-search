"""Fail-closed Bubblewrap boundary for generated packing Python programs."""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def command():
    executable = shutil.which('bwrap')
    if not executable: raise ValueError('Bubblewrap is required: install bubblewrap; no unsandboxed fallback')
    argv = [executable, '--unshare-all', '--die-with-parent', '--new-session',
            '--cap-drop', 'ALL', '--clearenv', '--tmpfs', '/tmp', '--proc', '/proc',
            '--dev', '/dev']
    # Mount runtime code only. No repository, home directory, .env, run logs,
    # credentials, host /tmp, or host network is made available to candidate code.
    roots = [Path('/usr'), Path('/lib'), Path('/lib64'), Path(sys.base_prefix), Path(sys.prefix)]
    mounted = []
    for root in roots:
        if not root.exists() or any(root == x or x in root.parents for x in mounted): continue
        if root in (Path('/'), Path.home(), HERE, HERE.parent):
            raise ValueError('unsafe Python runtime mount; use a dedicated virtual environment')
        argv += ['--ro-bind', str(root), str(root)]; mounted.append(root)
    argv += ['--ro-bind', str(HERE/'packing_worker.py'), '/worker.py',
             '--setenv', 'OPENBLAS_NUM_THREADS', '1', '--setenv', 'OMP_NUM_THREADS', '1',
             '--setenv', 'PATH', '/usr/bin:/bin', '--chdir', '/tmp',
             sys.executable, '-I', '-B', '/worker.py']
    return argv


def availability():
    if importlib.util.find_spec('scipy') is None:
        return {'available': False, 'reason': 'SciPy missing; install demo/requirements.txt'}
    try:
        argv = command()
        # Test actual namespace support without running a candidate or model.
        result = subprocess.run(argv[:-4]+['/usr/bin/true'], capture_output=True, timeout=4,
                                env={'PATH': os.environ.get('PATH', '/usr/bin:/bin')})
        if result.returncode:
            return {'available': False, 'reason': 'Bubblewrap unavailable: '+result.stderr.decode(errors='replace')[:250]}
        return {'available': True, 'reason': 'Bubblewrap: isolated network/PID/mount namespaces; read-only runtime; no credentials'}
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        return {'available': False, 'reason': str(error)[:250]}
