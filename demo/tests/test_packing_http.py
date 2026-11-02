"""Current teaching routes, tokens and reconnect; never releases a model gate."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.request
import urllib.error

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import DemoServer
from packing_controller import PackingManager


class PackingClientAuthTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Node required for client recovery checks')
    def test_rejected_writes_recover_once_without_retrying_ambiguous_failures(self):
        result=subprocess.run(['node',str(Path(__file__).with_name('test_packing_auth.js'))],
                              capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)


class PackingHTTPTests(unittest.TestCase):
    def test_routes_write_tokens_modes_and_reconnect(self):
        with tempfile.TemporaryDirectory() as root:
            manager=PackingManager(root);server=DemoServer(('127.0.0.1',0),manager)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            base=f'http://127.0.0.1:{server.server_address[1]}'
            def request(path,body=None,token=None,origin=None):
                headers={}
                if token:headers['X-Demo-Token']=token
                if origin:headers['Origin']=origin
                if body is not None:headers['Content-Type']='application/json'
                req=urllib.request.Request(base+path,data=None if body is None else json.dumps(body).encode(),headers=headers)
                try:
                    with urllib.request.urlopen(req,timeout=10) as response:return response.status,response.read()
                except urllib.error.HTTPError as response:return response.code,response.read()
            try:
                for path in ('/','/packing','/demo','/algorithms','/architecture','/notes','/packing.js','/packing.css'):
                    status,raw=request(path);self.assertEqual(status,200,path)
                    self.assertNotIn(b'Max-Cut',raw,path)
                access=json.loads(request('/api/status')[1]);self.assertEqual(access['cases'],[26,32])
                self.assertEqual(request('/api/packing/runs',{})[0],403)
                self.assertEqual(request('/api/packing/runs',{},access['write_token'],'https://other.example')[0],403)
                _,raw=request('/api/packing/runs',{'mode':'numerical','n':32},access['write_token'])
                created=json.loads(raw);rid=created['run_id'];token=created['write_token']
                self.assertEqual(created['snapshot']['model_calls'],0)
                _,raw=request(f'/api/packing/runs/{rid}/claim',{},access['write_token'])
                self.assertEqual(json.loads(raw)['write_token'],token)
                self.assertEqual(manager.get(rid).status,'created')
                self.assertEqual(request(f'/api/packing/runs/{rid}/start',{})[0],403)
                self.assertEqual(request(f'/api/packing/runs/{rid}/validate',{})[0],403)
                self.assertEqual(request(f'/api/packing/runs/{rid}/validate',{},token)[0],400)
                self.assertEqual(request(f'/api/packing/runs/{rid}/validation-stop',{},token)[0],400)
                _,raw=request(f'/api/packing/runs/{rid}/stop',{},token)
                self.assertEqual(json.loads(raw)['status'],'stopped')
                _,raw=request(f'/api/packing/runs/{rid}/events?after=0')
                self.assertIn(b'run_created',raw);self.assertEqual(manager.get(rid).calls,0)
                self.assertEqual(request('/.env')[0],404)
                self.assertEqual(request('/runs/private')[0],404)
                self.assertEqual(request('/api/packing/runs/nope')[0],404)
                if not access['sandbox']['available']: return
                _,raw=request('/api/packing/runs',{'mode':'numerical','initial_solvers':['grid']},access['write_token'])
                fresh=json.loads(raw);rid=fresh['run_id'];token=fresh['write_token']
                self.assertEqual(request(f'/api/packing/runs/{rid}/start',{},token)[0],200)
                manager.get(rid).thread.join(15)
                status,raw=request(f'/api/packing/runs/{rid}/validate',{},token)
                self.assertEqual(status,200);validation=json.loads(raw)
                self.assertEqual(request(f'/api/packing/runs/{rid}/validate',{},token)[0],200)
                manager.get(validation['id']).thread.join(15)
                state=json.loads(request(f'/api/packing/runs/{rid}')[1])['validation']
                self.assertEqual(state['status'],'finished');self.assertEqual(state['model_calls'],0)
                self.assertEqual(state['roles'][state['candidates'][0]['id']],['initial','final'])
                self.assertEqual(request(f'/api/packing/runs/{rid}/claim',{})[0],403)
                _,raw=request(f'/api/packing/runs/{rid}/claim',{},access['write_token'])
                claimed=json.loads(raw)
                self.assertEqual(claimed['write_token'],token)
                self.assertEqual(request(f'/api/packing/runs/{rid}/validate',{},claimed['write_token'])[0],200)
                self.assertEqual(request(f'/api/packing/runs/{rid}/validate',{},token)[0],200)
            finally:manager.close();server.shutdown();server.server_close();thread.join()


if __name__=='__main__':unittest.main()
