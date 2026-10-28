"""Students supply their own ignored local credentials; values never enter evidence."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from settings import load_local_env


class SettingsTests(unittest.TestCase):
    def test_local_only_environment_precedence_and_no_shell_expansion(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ,{},clear=True):
            path=Path(folder)/'.env'
            path.write_text('# private local test\nOPENAI_API_KEY="local-test-value"\nOPENAI_MODEL=test-model\n')
            load_local_env(path)
            self.assertEqual(os.environ['OPENAI_API_KEY'],'local-test-value')
            self.assertEqual(os.environ['OPENAI_MODEL'],'test-model')
            os.environ['OPENAI_API_KEY']='environment-test-value';load_local_env(path)
            self.assertEqual(os.environ['OPENAI_API_KEY'],'environment-test-value')
            path.write_text('OPENAI_API_KEY=$(touch /tmp/should-never-run)\n')
            os.environ.pop('OPENAI_API_KEY');load_local_env(path)
            self.assertEqual(os.environ['OPENAI_API_KEY'],'$(touch /tmp/should-never-run)')
            path.write_text('UNSUPPORTED=private-value\n')
            with self.assertRaises(ValueError) as error:load_local_env(path)
            self.assertNotIn('private-value',str(error.exception))


if __name__=='__main__':unittest.main()
