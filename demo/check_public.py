"""Read-only check of prospective public files, Git's index, and optional history.

Reports filenames only, never matching secret contents. A clean heuristic scan is
not a guarantee; ignored files must never be force-added.
"""
import argparse
import os
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
KEY_PATTERN=r'sk-(proj-)?[A-Za-z0-9_-]{20,}|AIza[A-Za-z0-9_-]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY-----'
PATTERN=re.compile(KEY_PATTERN)


def git(*args):
    result=subprocess.run(['git',*args],cwd=ROOT,capture_output=True,check=True)
    return result.stdout


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--history',action='store_true');args=parser.parse_args()
    from settings import load_local_env, KEY_NAMES
    load_local_env()
    local_keys = [os.environ.get(name, '') for name in KEY_NAMES]
    files=set(git('ls-files','--cached','--others','--exclude-standard','-z').decode().split('\0'))-{''}
    failures=[]
    for name in sorted(files):
        path=ROOT/name
        if not path.is_file():continue
        if (path.name.startswith('.env') and path.name!='.env.example') or name.startswith(('demo/runs/','demo/.venv/','demo/replays/private/','demo/rehearsal/')) or path.name in ('auth.json','credentials.json'):
            failures.append((name,'private file would be published'));continue
        raw=path.read_bytes()
        if any(len(key) >= 12 and key.encode() in raw for key in local_keys):
            failures.append((name,'configured local key would be published; contents suppressed'))
        if b'\0' in raw:continue
        if PATTERN.search(raw.decode(errors='replace')):failures.append((name,'possible credential; contents suppressed'))
    # Verify ignored credentials/records and publishable blank template without creating secrets.
    for private in ('demo/.env','.env','demo/runs/test/events.jsonl','demo/rehearsal/presentation-rehearsal.mp4','demo/SPEAKER_NOTES.md'):
        result=subprocess.run(['git','check-ignore','-q',private],cwd=ROOT)
        if result.returncode!=0:failures.append((private,'ignore rule missing'))
    template=ROOT/'demo/.env.example'
    if template.is_file() and any(line.partition('=')[0] in KEY_NAMES and line.partition('=')[2].strip() for line in template.read_text().splitlines()):
        failures.append(('demo/.env.example','template key must be blank'))
    commits=[]
    if args.history:
        commits=git('rev-list','--all').decode().splitlines()
        for commit in commits:
            result=subprocess.run(['git','grep','-I','-l','-E','-e',KEY_PATTERN,commit,'--'],cwd=ROOT,capture_output=True)
            if result.returncode not in (0,1):raise RuntimeError('history scan failed; no clean result reported')
            for name in result.stdout.decode().splitlines():failures.append((name,'possible credential in history; contents suppressed'))
    for name,reason in failures:print(f'FAIL {name}: {reason}')
    print(f'Checked {len(files)} prospective files; {len(commits)} commits; {len(failures)} findings. No files changed.')
    if failures:raise SystemExit(1)


if __name__=='__main__':main()
