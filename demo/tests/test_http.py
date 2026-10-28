"""Loopback transport checks. These tests make no external requests and spend no model calls."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import urllib.request
import urllib.error

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import DemoServer
from controller import Manager
from evolution_common import owned_process
from portfolio_external import process_tick, process_live
from test_controller import wait_for


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.manager=Manager(self.temp.name)
        self.server=DemoServer(('127.0.0.1',0),self.manager)
        self.base='http://127.0.0.1:'+str(self.server.server_address[1])
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
    def tearDown(self):
        self.manager.close();self.server.shutdown();self.server.server_close();self.thread.join();self.temp.cleanup()
    def request(self,path,body=None,token=None,origin=None):
        headers={}
        if token:headers['X-Demo-Token']=token
        if origin:headers['Origin']=origin
        data=None if body is None else json.dumps(body).encode()
        if data:headers['Content-Type']='application/json'
        req=urllib.request.Request(self.base+path,data=data,headers=headers)
        try:
            with urllib.request.urlopen(req,timeout=12) as res:return res.status,json.load(res)
        except urllib.error.HTTPError as res:return res.code,json.load(res)

    def test_http_start_reconnect_reset_and_write_protection(self):
        status,access=self.request('/api/status');self.assertEqual(status,200)
        self.assertEqual(self.request('/api/runs',{'mode':'numerical'})[0],403)
        self.assertEqual(self.request('/api/runs',{'mode':'numerical'},access['write_token'],'https://evil.example')[0],403)
        _,created=self.request('/api/runs',{'mode':'numerical','seed':3},access['write_token'])
        rid=created['run_id'];token=created['write_token'];base='/api/runs/'+rid
        self.assertEqual(self.request(base+'/start',{},token)[1]['started'],True)
        self.assertEqual(self.request(base+'/start',{},token)[1]['started'],False)
        run=self.manager.get(rid);run.thread.join(15);self.assertEqual(run.status,'finished')
        with urllib.request.urlopen(urllib.request.Request(self.base+base+'/events',headers={'Last-Event-ID':'10'}),timeout=5) as res:
            lines=res.read().decode().splitlines()
        ids=[int(line[4:]) for line in lines if line.startswith('id: ')]
        self.assertEqual(ids,list(range(11,len(run.events)+1)))
        _,snap=self.request(base);self.assertEqual(snap['best']['cut'],68);self.assertEqual(snap['model_calls'],0)
        _,fresh=self.request('/api/reset',{'mode':'numerical','seed':4},access['write_token'])
        self.assertNotEqual(rid,fresh['run_id']);self.assertNotEqual(token,fresh['write_token'])
        self.assertIsNone(fresh['snapshot']['best']);self.assertEqual(fresh['snapshot']['status'],'created')
        self.assertEqual(self.request(base+'/start',{},token)[0],403)
        self.assertEqual(self.request('/api/runs/nope')[0],404)
        self.assertEqual(self.request('/../../etc/passwd')[0],404)
        self.assertEqual(self.request('/api/runs',{'mode':'replay','replay':rid},access['write_token'])[0],400)
        self.assertEqual(self.request('/api/status')[1]['recordings'],[])
        self.assertEqual(run.calls,0)

    def test_actual_model_http_transport_and_stop_are_test_only(self):
        # A deliberately stalled loopback provider tests cancellation, NOT real model integration.
        requested=threading.Event();release=threading.Event()
        class Fake(BaseHTTPRequestHandler):
            def log_message(self,*_):pass
            def do_POST(self):
                body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                self.server.body=body;requested.set();release.wait(6)
                try:
                    self.send_response(200);self.send_header('Content-Type','text/event-stream');self.end_headers()
                    self.wfile.write(b'data: {"type":"response.output_text.delta","delta":"{}"}\n\n')
                    self.wfile.write(b'data: {"type":"response.completed","response":{"id":"test","model":"test","status":"completed","usage":{"input_tokens":1,"output_tokens":1}}}\n\n')
                except (BrokenPipeError,ConnectionResetError):pass
        fake=ThreadingHTTPServer(('127.0.0.1',0),Fake)
        ft=threading.Thread(target=fake.serve_forever,daemon=True);ft.start()
        try:
            env={**os.environ,'DEMO_LLM_PROVIDER':'openai','OPENAI_API_KEY':'test-only-not-a-credential','DEMO_TEST_API_URL':f'http://127.0.0.1:{fake.server_address[1]}/v1/responses'}
            directory=Path(self.temp.name)/'model-transport';directory.mkdir()
            (directory/'request.json').write_text(json.dumps({'model':'test','input':'test'}))
            stop=directory/'STOP';outcome=[]
            def work():outcome.append(owned_process([sys.executable,str(Path(__file__).resolve().parents[1]/'model_worker.py'),str(directory)],directory,3,directory/'stdout.raw',directory/'stderr.raw',environment=env,registration=directory/'active.json',stop_path=stop))
            thread=threading.Thread(target=work);thread.start()
            self.assertTrue(requested.wait(3));record=json.loads((directory/'active.json').read_text())
            self.assertTrue(process_live(record['pid'],record['tick']))
            stop.touch();thread.join(8);self.assertFalse(thread.is_alive());self.assertTrue(outcome[0]['stopped'])
            self.assertFalse(process_live(record['pid'],record['tick']));self.assertFalse((directory/'result.json').exists())
            self.assertEqual(fake.body['tools'],[]);self.assertFalse(fake.body['store']);self.assertTrue(fake.body['stream'])
            release.set()
            # Successful test transport is explicitly tagged and cannot become a genuine replay.
            complete=Path(self.temp.name)/'completed-transport';complete.mkdir()
            (complete/'request.json').write_text(json.dumps({'model':'test','input':'test'}))
            receipt=owned_process([sys.executable,str(Path(__file__).resolve().parents[1]/'model_worker.py'),str(complete)],complete,3,complete/'stdout.raw',complete/'stderr.raw',environment=env)
            self.assertEqual(receipt['exit_code'],0)
            self.assertEqual(json.loads((complete/'result.json').read_text())['provider'],'test_transport')
            self.assertEqual(self.manager.recordings(),{})
        finally:release.set();fake.shutdown();fake.server_close();ft.join()


if __name__=='__main__':unittest.main()

class TeachingRouteTests(HTTPTests):
    # Inherit setup/teardown only; avoid rerunning the parent test methods.
    test_http_start_reconnect_reset_and_write_protection = None
    test_actual_model_http_transport_and_stop_are_test_only = None

    def test_teaching_routes_are_read_only_and_allowlisted(self):
        for path,marker in [('/',b'Presentation'),('/demo',b'Solver population'),('/algorithms',b'Tabu Search'),('/exchange',b'Sent to Luna'),('/architecture',b'Architecture'),('/architecture.pdf',b'%PDF'),('/brand.css',b'#500000'),('/handout.pdf',b'%PDF'),('/document.pdf',b'%PDF')]:
            with urllib.request.urlopen(self.base+path,timeout=5) as response:
                self.assertIn(marker,response.read());self.assertIn("frame-ancestors 'self'",response.headers['Content-Security-Policy'])
        self.assertEqual(self.manager.runs,{})
        self.assertEqual(self.request('/api/activity')[1]['runs'],[])
        self.assertEqual(self.request('/api/comparisons')[1]['runs'],[])
        self.assertEqual(len(self.request('/api/status')[1]['initial_solver_catalog']),4)
        self.assertEqual(len(self.request('/api/status')[1]['scenarios']),3)
        self.assertEqual(self.request('/.env')[0],404)
        self.assertEqual(self.request('/api/runs/nope/exchange/1')[0],404)
        self.assertEqual(self.request('/api/instance?instance=../../secret')[0],400)

    def test_duplicate_launch_reuses_same_repository_without_traceback(self):
        result=subprocess.run([sys.executable,str(Path(__file__).resolve().parents[1]/'server.py'),
                               '--port',str(self.server.server_address[1])],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('Already running:',result.stdout)
        self.assertNotIn('Traceback',result.stderr)
        self.assertEqual(self.request('/api/server-info')[0],200)
        self.assertEqual(self.manager.runs,{})

    def test_other_workspace_is_not_reused_or_stopped(self):
        with patch('server.WORKSPACE','different-repository'):
            result=subprocess.run([sys.executable,str(Path(__file__).resolve().parents[1]/'server.py'),
                                   '--port',str(self.server.server_address[1])],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,2)
        self.assertIn('No process was stopped',result.stderr)
        self.assertNotIn('Traceback',result.stderr)
        self.assertEqual(self.request('/api/server-info')[0],200)
