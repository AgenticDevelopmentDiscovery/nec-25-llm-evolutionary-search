"""Loopback-only classroom server. Run: python demo/server.py"""
import argparse
import errno
import hashlib
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import signal
import os
import sys
import threading
from urllib.parse import urlsplit, parse_qs

from controller import HERE, live_access, TERMINAL
from preview import PresentationPreview
from packing_controller import PackingManager, PROFILE
import packing
from packing_sandbox import availability as packing_availability

SERVICE = 'engr689-circle-demo'
WORKSPACE = hashlib.sha256(str(HERE.parent.resolve()).encode()).hexdigest()
BACKEND_SHA256 = hashlib.sha256(b''.join((HERE/name).read_bytes() for name in (
    'server.py','packing.py','packing_controller.py','packing_sandbox.py',
    'packing_worker.py','packing_profile.json','model_worker.py','settings.py'))).hexdigest()


def existing_server(port):
    """Identify only this repository's service; never stop or replace a listener."""
    connection = http.client.HTTPConnection('127.0.0.1', port, timeout=1)
    try:
        connection.request('GET', '/api/server-info')
        response = connection.getresponse()
        if response.status != 200: return None
        info = json.loads(response.read(8192))
        if not isinstance(info,dict) or type(info.get('pid')) is not int: return None
        return info if info.get('service')==SERVICE and info.get('workspace')==WORKSPACE else None
    except (OSError, ValueError, http.client.HTTPException):
        return None
    finally:
        connection.close()


def verify_snapshot():
    root = HERE.parent
    manifest = json.loads((HERE / 'vendor/SOURCE_MANIFEST.json').read_text())
    for item in manifest['files']:
        path = root / item['destination']
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('vendored snapshot changed: ' + item['destination'])
    return len(manifest['files'])



class DemoServer(ThreadingHTTPServer):
    daemon_threads = True
    def __init__(self, address=('127.0.0.1', 8766), manager=None, preview=None):
        if address[0] != '127.0.0.1': raise ValueError('only 127.0.0.1 is supported')
        super().__init__(address, Handler)
        self.packing = manager or PackingManager()
        self.manager = self.packing
        self.preview = preview or PresentationPreview()
        self.bootstrap = secrets.token_urlsafe(32)
        self.tokens = {}
        self.route_lock = threading.RLock()

    def register(self, run):
        token = secrets.token_urlsafe(32)
        self.tokens[run.id] = token
        return {'run_id': run.id, 'write_token': token, 'snapshot': run.snapshot()}


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    def log_message(self, *_): pass

    def headers_ok(self, write=False):
        port = self.server.server_address[1]
        hosts = {f'127.0.0.1:{port}', f'localhost:{port}'}
        if self.headers.get('Host') not in hosts: raise PermissionError('invalid Host')
        origin = self.headers.get('Origin')
        if origin is not None and origin not in {'http://' + h for h in hosts}:
            raise PermissionError('cross-origin request rejected')
        if write and self.headers.get('Sec-Fetch-Site') == 'cross-site': raise PermissionError('cross-site request rejected')

    def reply(self, value, status=200):
        raw = json.dumps(value, allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers(); self.wfile.write(raw)

    def do_GET(self):
        try:
            self.headers_ok()
            url = urlsplit(self.path)
            path = url.path
            if path == '/api/server-info':
                return self.reply({'service':SERVICE,'workspace':WORKSPACE,'pid':os.getpid(),'rounds':PROFILE['max_rounds'],'auto_rebuild':self.server.preview.available,'execution_version':packing.VERSION,'circle_packing':packing.VERSION,'backend_sha256':BACKEND_SHA256,'active_run_id':self.server.packing.active.id if self.server.packing.active else None})
            if path == '/api/presentation': return self.reply(self.server.preview.ensure())
            if path in ('/api/packing/status','/api/status'):
                return self.reply({'write_token': self.server.bootstrap, 'task': packing.specification(), 'cases': list(packing.CASES),
                    'sandbox': packing_availability(), 'live': live_access(),
                    'programs': packing.initial_programs(),
                    'recordings': [{'id':identity, **{k:v for k,v in r.items() if k!='events'}}
                                   for identity,r in self.server.packing.recordings().items()]})
            if path in ('/presentation.json','/notes'): self.server.preview.ensure()
            parts = path.strip('/').split('/')
            if len(parts) in (4,5,6) and parts[:3] == ['api','packing','runs']:
                run = self.server.packing.get(parts[3])
                if len(parts)==4: return self.reply(run.snapshot())
                if len(parts)==5 and parts[4]=='events':
                    after = int(self.headers.get('Last-Event-ID') or parse_qs(url.query).get('after',['0'])[0])
                    if not 0 <= after <= len(run.events): raise ValueError('invalid event cursor')
                    return self.events(run, after)
                if len(parts)==6 and parts[4]=='exchange':
                    return self.reply(self.server.packing.exchange(parts[3],int(parts[5])))
            # Explicit teaching routes only; never expose .env, runs or repository files.
            static = {
                '/': ('presentation.html', 'text/html'), '/present': ('presentation.html', 'text/html'),
                '/packing': ('packing.html','text/html'), '/packing.js':('packing.js','text/javascript'),
                '/packing.css':('packing.css','text/css'), '/packing-guide':('packing-guide.html','text/html'),
                '/demo': ('packing.html', 'text/html'),
                '/presentation.js': ('presentation.js', 'text/javascript'), '/presentation.css': ('presentation.css', 'text/css'),
                '/presentation.json': ('presentation.json', 'application/json'), '/notes': ('teaching-notes.html', 'text/html'),
                '/notes.css': ('notes.css', 'text/css'), '/brand.css':('brand.css','text/css'), '/architecture':('architecture.html','text/html'), '/architecture.pdf':('architecture.pdf','application/pdf'),
                '/algorithms': ('packing-guide.html','text/html'),
                '/exchange':('packing.html','text/html'),
                '/exchange.css':('exchange.css','text/css'),
                '/handout.pdf': ('handout.pdf', 'application/pdf'),
                '/document.pdf': ('document.pdf', 'application/pdf'),
                '/rehearsal': ('../rehearsal/index.html', 'text/html'),
                '/rehearsal-script': ('../rehearsal/script.md','text/plain'),
            }
            for figure in ('evolutionary-cycle.svg','architecture-overview.svg','system-architecture.svg','request-data-flow.svg'):
                static['/figures/' + figure] = ('../../figures/' + figure, 'image/svg+xml')
            if path not in static: return self.reply({'error': 'not found'}, 404)
            filename, mime = static[path]
            asset = HERE / 'static' / filename
            if not asset.is_file(): return self.reply({'error': 'asset not built; run just build'}, 404)
            with asset.open('rb') as stream:
                size = os.fstat(stream.fileno()).st_size
                start, end = 0, size - 1
                partial = False
                if mime == 'video/mp4' and self.headers.get('Range'):
                    import re
                    match = re.fullmatch(r'bytes=(\d+)-(\d*)', self.headers['Range'])
                    if not match: return self.reply({'error': 'unsupported byte range'}, 416)
                    start, end = int(match[1]), min(int(match[2]) if match[2] else end, end)
                    if start > end: return self.reply({'error': 'range outside video'}, 416)
                    partial = True
                self.send_response(206 if partial else 200)
                self.send_header('Content-Type', mime + ('; charset=utf-8' if mime.startswith('text/') else ''))
                self.send_header('Content-Length', str(end - start + 1))
                if mime == 'video/mp4': self.send_header('Accept-Ranges', 'bytes')
                if partial: self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
                self.send_header('Cache-Control', 'no-store')
                self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-src 'self'; media-src 'self'; object-src 'none'; frame-ancestors 'self'")
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.end_headers()
                stream.seek(start)
                remaining = end - start + 1
                while remaining:
                    chunk = stream.read(min(remaining, 65536))
                    if not chunk: break
                    self.wfile.write(chunk); remaining -= len(chunk)
        except (BrokenPipeError, ConnectionResetError): pass
        except PermissionError as error: self.reply({'error': str(error)}, 403)
        except KeyError: self.reply({'error': 'unknown run ID'}, 404)
        except (ValueError, TypeError) as error: self.reply({'error': str(error)}, 400)

    def events(self, run, after):
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Connection', 'close')
        self.end_headers()
        while True:
            with run.changed:
                if len(run.events) <= after and run.status not in TERMINAL:
                    run.changed.wait(timeout=0.5)
                batch = run.events[after:]
                terminal = run.status in TERMINAL
            for event in batch:
                raw = f"id: {event['seq']}\ndata: {json.dumps(event, allow_nan=False)}\n\n".encode()
                self.wfile.write(raw); after = event['seq']
            if not batch: self.wfile.write(b': heartbeat\n\n')
            self.wfile.flush()
            if terminal and after >= len(run.events): break
        self.close_connection = True

    def do_POST(self):
        try:
            self.headers_ok(write=True)
            if self.headers.get('Content-Type') != 'application/json': raise ValueError('application/json required')
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 8192: raise ValueError('request body must be 1..8192 bytes')
            # Reject nonfinite JSON constants at the boundary.
            body = json.loads(self.rfile.read(length), parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite JSON')))
            parts = urlsplit(self.path).path.strip('/').split('/')
            token = self.headers.get('X-Demo-Token', '')
            with self.server.route_lock:
                if parts in (['api','packing','runs'], ['api','packing','reset']):
                    if not secrets.compare_digest(token,self.server.bootstrap): raise PermissionError('write token required')
                    run = self.server.packing.reset(body) if parts[-1]=='reset' else self.server.packing.create(body)
                    return self.reply(self.server.register(run),201)
                if len(parts)==5 and parts[:3]==['api','packing','runs'] and parts[-1] in ('start','stop','continue'):
                    run = self.server.packing.get(parts[3])
                    if not secrets.compare_digest(token,self.server.tokens.get(run.id,'invalid')): raise PermissionError('run write token required')
                    if body != {}: raise ValueError('run actions require an empty object')
                    if parts[-1]=='continue': return self.reply({'continued':run.continue_round()})
                    if parts[-1]=='start':
                        return self.reply({'started':self.server.packing.start(run)})
                    run.stop(); return self.reply(run.snapshot())
            self.reply({'error': 'not found'}, 404)
        except (BrokenPipeError, ConnectionResetError): pass
        except PermissionError as error: self.reply({'error': str(error)}, 403)
        except KeyError: self.reply({'error': 'unknown run ID'}, 404)
        except (ValueError, TypeError, json.JSONDecodeError) as error: self.reply({'error': str(error)}, 400)
        except RuntimeError as error: self.reply({'error': str(error)}, 409)


def main():
    from settings import load_local_env
    load_local_env()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8766)
    parser.add_argument('--rounds', type=int, choices=[1,2,3], default=3, help='default three mutation rounds; one is a diagnostic only')
    parser.add_argument('--check', action='store_true', help='offline hashes + direct model-access preflight; no requests')
    args = parser.parse_args()
    PROFILE['max_rounds'] = args.rounds
    PROFILE['max_model_calls'] = args.rounds
    verified = verify_snapshot()
    if args.check:
        print(json.dumps({'vendored_files_verified': verified, 'live': live_access(),
            'packing':packing.specification(),'execution':packing_availability(),'recursive_agent_calls': False})); return
    url = f'http://127.0.0.1:{args.port}/'
    try:
        server = DemoServer(('127.0.0.1', args.port))
    except OSError as error:
        if error.errno != errno.EADDRINUSE: raise
        info = existing_server(args.port)
        if info:
            print(f'Already running: {url} (PID {info["pid"]}). Open or refresh that page; no second server started.')
            print('The existing Python environment and server settings remain in use.')
            if info.get('auto_rebuild'): print('Save prose to update open presentation tabs automatically.')
            if info.get('backend_sha256') != BACKEND_SHA256:
                print('Backend files changed since that server started. Stop it in its terminal and relaunch, or use another port. Refreshing alone reloads static content, not Python.')
            if info.get('circle_packing') != packing.VERSION:
                print('That older server does not include the circle-packing backend. Stop its terminal and relaunch, or use: just demo 8767')
            if info.get('rounds') != args.rounds:
                print(f'Existing server uses {info["rounds"]} rounds. Stop it first to change that setting.')
            return 0
        print(f'Port {args.port} is already in use by another or older service. No process was stopped.\n'
              f'Open {url} if it is your tutorial server, or use: just demo 8767', file=sys.stderr)
        return 2
    preview = server.preview.ensure()
    if not (HERE/'static/presentation.json').is_file():
        server.manager.close();server.server_close()
        print('Presentation unavailable: '+str(preview['error']),file=sys.stderr)
        return 1
    if preview['error']: print('Showing the last built frames. Prose error: '+preview['error'],file=sys.stderr)
    def shutdown(*_):
        threading.Thread(target=server.shutdown, daemon=True).start()
    signal.signal(signal.SIGINT, shutdown); signal.signal(signal.SIGTERM, shutdown)
    print(f'Tutorial: http://127.0.0.1:{server.server_address[1]} · Circle packing: /packing (local only)', flush=True)
    print('Save sections/*.prose.md to update browser frames automatically. PDFs: just build.' if preview['auto_rebuild'] else 'Serving bundled frames. Install Pandoc to rebuild edited prose.',flush=True)
    try: server.serve_forever(poll_interval=0.1)
    finally:
        server.packing.close(); server.server_close()


if __name__ == '__main__': raise SystemExit(main())
