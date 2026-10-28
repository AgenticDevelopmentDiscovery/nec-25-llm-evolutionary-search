"""TAMU transport and credential separation, with zero external requests."""
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import urllib.request
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from settings import load_local_env, provider_settings
from controller import live_access
from model_worker import main, payload_for, NoRedirect, open_api
from proposals import SCHEMA, INSTRUCTIONS


def canonical():
    return {'model':'protected.gemini-2.5-flash-lite','instructions':INSTRUCTIONS,'input':'parent context',
            'max_output_tokens':2400,'text':{'format':{'schema':SCHEMA}}}


class Response(io.BytesIO):
    def __init__(self, raw, mime='text/event-stream'):
        super().__init__(raw);self.headers={'Content-Type':mime}


class TamuTests(unittest.TestCase):
    def test_sol_budget_and_documented_requests_client(self):
        request=canonical();request['model']='protected.gpt-5.6-sol'
        with patch.dict(os.environ,{'DEMO_LLM_PROVIDER':'tamu'},clear=True):
            for model in ('protected.gpt-5.6-sol','protected.gpt-5.6-luna'):
                request['model']=model
                payload=payload_for(request,provider_settings())
                self.assertEqual(payload['model'],model)
                self.assertEqual(payload['max_completion_tokens'],2400)
                self.assertEqual(payload['reasoning_effort'],'low');self.assertNotIn('max_tokens',payload)
            from unittest.mock import Mock
            response=Mock(status_code=200,headers={'Content-Type':'text/event-stream'})
            response.iter_lines.return_value=iter([b'data: test'])
            with patch('requests.request',return_value=response) as network:
                with open_api(urllib.request.Request('https://chat-api.tamu.ai/api/models')) as wrapped:
                    self.assertEqual(list(wrapped),[b'data: test'])
                self.assertFalse(network.call_args.kwargs['allow_redirects'])
                self.assertTrue(network.call_args.kwargs['stream']);response.close.assert_called_once()
            response=Mock(status_code=302,headers={'Location':'https://evil.example'})
            with patch('requests.request',return_value=response) as network:
                with self.assertRaisesRegex(ValueError,'redirected'):open_api(urllib.request.Request('https://chat-api.tamu.ai/api/models'))
                self.assertEqual(network.call_count,1);response.close.assert_called_once()

    def test_explicit_provider_binding_and_fixed_destination(self):
        with patch.dict(os.environ,{'DEMO_LLM_PROVIDER':'tamu','OPENAI_API_KEY':'wrong-provider-key','OPENAI_MODEL':'wrong-provider-model'},clear=True):
            access=live_access()
            self.assertFalse(access['available']);self.assertIn('TAMUS_AI_CHAT_API_KEY',access['reason'])
            self.assertEqual(access['model'],'protected.gpt-5.6-luna')
            self.assertEqual(access['endpoint'],'https://chat-api.tamu.ai/api/chat/completions')
            with tempfile.TemporaryDirectory() as folder:
                path=Path(folder);(path/'request.json').write_text(json.dumps(canonical()))
                with patch('model_worker.open_api') as network:
                    with self.assertRaisesRegex(ValueError,'TAMUS_AI_CHAT_API_KEY'):main(path)
                    network.assert_not_called()
            for invalid in ('https://evil.example','http://chat-api.tamu.ai','https://chat-api.tamu.ai.evil.example','https://chat-api.tamu.ai@evil.example'):
                os.environ['TAMUS_AI_CHAT_API_ENDPOINT']=invalid
                with self.assertRaises(ValueError):provider_settings()
        with self.assertRaisesRegex(ValueError,'redirected'):NoRedirect().redirect_request(None,None,302,'',{},'https://evil.example')

    def test_local_tamu_settings_and_payload(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ,{},clear=True):
            path=Path(folder)/'.env';path.write_text('DEMO_LLM_PROVIDER=tamu\nTAMUS_AI_CHAT_API_KEY=test-local-key\nTAMUS_AI_CHAT_MODEL=protected.test-model\nTAMUS_AI_CHAT_API_ENDPOINT=https://chat-api.tamu.ai\n')
            load_local_env(path);settings=provider_settings()
            self.assertEqual(settings['model'],'protected.test-model')
            payload=payload_for(canonical(),settings)
            self.assertEqual(payload['messages'][1]['content'],'parent context')
            self.assertIn('JSON schema',payload['messages'][0]['content'])
            self.assertEqual(payload['tools'],[]);self.assertEqual(payload['tool_ids'],[])
            self.assertNotIn('response_format',payload);self.assertNotIn('instructions',payload)

    def run_response(self, raw, mime='text/event-stream'):
        folder=tempfile.TemporaryDirectory();self.addCleanup(folder.cleanup)
        path=Path(folder.name);(path/'request.json').write_text(json.dumps(canonical()))
        env={'DEMO_LLM_PROVIDER':'tamu','TAMUS_AI_CHAT_API_KEY':'tamu-local-test-secret','OPENAI_API_KEY':'openai-local-test-secret'}
        with patch.dict(os.environ,env,clear=True), patch('model_worker.open_api',return_value=Response(raw,mime)) as network:
            main(path)
            req=network.call_args.args[0]
            self.assertEqual(req.full_url,'https://chat-api.tamu.ai/api/chat/completions')
            self.assertEqual(req.headers['Authorization'],'Bearer tamu-local-test-secret')
        for file in path.iterdir():
            self.assertNotIn('tamu-local-test-secret',file.read_text())
            self.assertNotIn('openai-local-test-secret',file.read_text())
        return path

    def test_stream_public_text_usage_and_completion_receipt(self):
        chunks=[{'id':'test-response','model':'protected.test','choices':[{'index':0,'delta':{'reasoning_content':'PRIVATE_REASONING','content':'{"round_id":'},'finish_reason':None}]},
                {'choices':[{'index':0,'delta':{'content':'1}'},'finish_reason':'stop'}]},
                {'choices':[],'usage':{'prompt_tokens':11,'completion_tokens':7,'total_tokens':18}}]
        raw=b''.join(b'data: '+json.dumps(c).encode()+b'\n\n' for c in chunks)+b'data: [DONE]\n\n'
        path=self.run_response(raw);result=json.loads((path/'result.json').read_text())
        self.assertEqual(result['provider'],'tamu_chat_completions')
        self.assertEqual(result['proposal'],{'round_id':1});self.assertEqual(result['status'],'completed')
        self.assertEqual(result['usage'],{'input_tokens':11,'output_tokens':7,'total_tokens':18})
        self.assertFalse(any('PRIVATE_REASONING' in p.read_text() for p in path.iterdir()))

    def test_nonstream_response_and_absent_usage_remains_unknown(self):
        body={'id':'test','model':'protected.test','choices':[{'message':{'role':'assistant','content':'{"round_id":1}'},'finish_reason':'stop'}]}
        path=self.run_response(json.dumps(body).encode(),'application/json')
        self.assertIsNone(json.loads((path/'result.json').read_text())['usage'])

    def test_incomplete_and_tool_calls_are_refused_without_retry(self):
        for choice in ({'delta':{'content':'{}'},'finish_reason':'length'},
                       {'delta':{'tool_calls':[{'function':{'name':'execute'}}]},'finish_reason':'tool_calls'}):
            with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ,{'DEMO_LLM_PROVIDER':'tamu','TAMUS_AI_CHAT_API_KEY':'test-key'},clear=True):
                path=Path(folder);(path/'request.json').write_text(json.dumps(canonical()))
                raw=b'data: '+json.dumps({'choices':[choice]}).encode()+b'\n\n'
                with patch('model_worker.open_api',return_value=Response(raw)) as network:
                    with self.assertRaises(ValueError):main(path)
                    self.assertEqual(network.call_count,1)
                self.assertFalse((path/'result.json').exists())


if __name__=='__main__':unittest.main()
