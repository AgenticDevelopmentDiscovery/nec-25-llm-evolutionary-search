"""Current teaching routes, tokens and reconnect; never releases a model gate."""
from pathlib import Path
import json
import sys
import tempfile
import threading
import unittest
import urllib.request
import urllib.error

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import DemoServer
from packing_controller import PackingManager


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
                self.assertEqual(request(f'/api/packing/runs/{rid}/start',{})[0],403)
                _,raw=request(f'/api/packing/runs/{rid}/stop',{},token)
                self.assertEqual(json.loads(raw)['status'],'stopped')
                _,raw=request(f'/api/packing/runs/{rid}/events?after=0')
                self.assertIn(b'run_created',raw);self.assertEqual(manager.get(rid).calls,0)
                self.assertEqual(request('/.env')[0],404)
                self.assertEqual(request('/runs/private')[0],404)
                self.assertEqual(request('/api/packing/runs/nope')[0],404)
            finally:manager.close();server.shutdown();server.server_close();thread.join()


if __name__=='__main__':unittest.main()
