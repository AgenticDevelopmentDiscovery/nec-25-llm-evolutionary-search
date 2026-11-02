"""Use the checkout's ignored environment when present; never install or call a model."""
import os
from pathlib import Path
import sys

here=Path(__file__).resolve().parent
local=here/'.venv/bin/python'
python=str(local) if local.is_file() else sys.executable
os.execv(python,[python,str(here/'server.py'),*sys.argv[1:]])
