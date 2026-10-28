"""Serialize local prose rebuilds; an invalid draft keeps the last good deck."""
import json
from pathlib import Path
import shutil
import subprocess
import threading

from build_presentation import ROOT, build, source_hash
from settings import redact


class PresentationPreview:
    def __init__(self, root=ROOT, builder=build, pandoc_available=None):
        self.root = Path(root)
        self.bundle = self.root/'demo/static/presentation.json'
        self.builder = builder
        self.available = bool(shutil.which('pandoc')) if pandoc_available is None else pandoc_available
        self.lock = threading.Lock()
        self.failed_hash = None
        self.error = None

    def built_hash(self):
        try:
            return json.loads(self.bundle.read_text())['source_sha256']
        except (OSError, ValueError, KeyError, TypeError):
            return None

    def ensure(self):
        with self.lock:
            try:
                wanted = source_hash(self.root)
                if self.built_hash() == wanted:
                    self.error = None
                    self.failed_hash = None
                elif wanted != self.failed_hash:
                    try:
                        if not self.available:
                            raise ValueError('Pandoc is required to rebuild edited prose. The last built frames remain available.')
                        self.builder()
                        self.error = None
                        self.failed_hash = None
                    except Exception as error:
                        detail = error.stderr if isinstance(error, subprocess.CalledProcessError) and error.stderr else str(error)
                        self.error = redact(detail)[:1500]
                        self.failed_hash = wanted
            except OSError as error:
                self.error = redact(str(error))[:1500]
            return {'source_sha256':self.built_hash(), 'auto_rebuild':self.available, 'error':self.error}
