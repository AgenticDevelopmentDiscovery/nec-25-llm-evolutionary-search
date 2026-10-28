"""Public diagnostics retained without credentials or hidden reasoning; no network."""
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from model_worker import main


class ModelErrorTests(unittest.TestCase):
    def test_stream_error_recorded_and_key_redacted(self):
        secret='local-test-key-value'
        event={'type':'error','error':{'type':'insufficient_quota','code':'credit_balance_exhausted','message':'test '+secret}}
        public=b'data: '+json.dumps(event).encode()+b'\n\n'
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ,{'OPENAI_API_KEY':secret},clear=True):
            path=Path(folder);(path/'request.json').write_text(json.dumps({'model':'test','input':'test'}))
            with patch('model_worker.open_api',return_value=io.BytesIO(public)):
                with self.assertRaisesRegex(ValueError,'credit_balance_exhausted') as error:main(folder)
            self.assertNotIn(secret,str(error.exception))
            self.assertNotIn(secret,(path/'provider-error.json').read_text())
            self.assertFalse((path/'result.json').exists())


if __name__=='__main__':unittest.main()
