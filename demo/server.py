"""Loopback-only classroom server. Run: python demo/server.py"""
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import signal
import threading
from urllib.parse import urlsplit, parse_qs

import backend as b
from controller import Manager, HERE, PROFILE, live_access, TERMINAL
from experiments import SCENARIOS


def verify_snapshot():
    root = HERE.parent
    manifest = json.loads((HERE / 'vendor/SOURCE_MANIFEST.json').read_text())
    for item in manifest['files']:
        path = root / item['destination']
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('vendored snapshot changed: ' + item['destination'])
    b.score_labels(b.seed_labels(3))
    return len(manifest['files'])


def instance(name=None):
    spec = b.instance_spec(name)
    graph = b.load_graph(spec['path'])
    return {'name':spec['name'], 'nodes':spec['nodes'], 'side':spec['side'], 'kind':spec['kind'],
            'edges':graph.edges.tolist() if hasattr(graph.edges, 'tolist') else graph.edges,
            'graph_sha256':spec['sha256'], 'reference':spec['reference'], 'proof_status':'unproven',
            'layout':f"{spec['side']}x{spec['side']} indexing; "+('strongest 80 edges displayed; all edges scored' if spec['kind']!='torus' else 'torus wrap edges split at borders')}


class DemoServer(ThreadingHTTPServer):
    daemon_threads = True
    def __init__(self, address=('127.0.0.1', 8766), manager=None):
        if address[0] != '127.0.0.1': raise ValueError('only 127.0.0.1 is supported')
        self.manager = manager or Manager(instance=PROFILE['instance'])
        self.bootstrap = secrets.token_urlsafe(32)
        self.tokens = {}
        self.route_lock = threading.RLock()
        super().__init__(address, Handler)

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
            if path == '/api/instance': return self.reply(instance(parse_qs(url.query).get('instance', [self.server.manager.instance])[0]))
            if path == '/api/comparisons': return self.reply(self.server.manager.comparisons())
            if path == '/api/activity': return self.reply(self.server.manager.activity())
            if path == '/api/status':
                recordings = self.server.manager.recordings()
                return self.reply({'write_token': self.server.bootstrap, 'live': live_access(), 'profile': PROFILE,
                    'default_instance':self.server.manager.instance, 'scenarios':SCENARIOS,
                    'initial_solver_catalog':[{'id':s['stages'][0]['backend'],'name':n,'strategy':b.normalized_strategy(s)} for n,s in b.INITIAL_SOLVERS],
                    'recordings': [{'id': identity, **{k:v for k,v in r.items() if k != 'events'}} for identity,r in recordings.items()]})
            parts = path.strip('/').split('/')
            if len(parts)==5 and parts[:2]==['api','runs'] and parts[3]=='exchange':
                return self.reply(self.server.manager.exchange(parts[2], int(parts[4])))
            if len(parts) in (3, 4) and parts[:2] == ['api', 'runs']:
                run = self.server.manager.get(parts[2])
                if len(parts) == 3: return self.reply(run.snapshot())
                if parts[3] == 'events':
                    after = self.headers.get('Last-Event-ID') or parse_qs(url.query).get('after', ['0'])[0]
                    after = int(after)
                    if not 0 <= after <= len(run.events): raise ValueError('invalid event cursor')
                    return self.events(run, after)
            # Explicit teaching routes only; never expose .env, runs or repository files.
            static = {
                '/': ('presentation.html', 'text/html'), '/present': ('presentation.html', 'text/html'),
                '/demo': ('index.html', 'text/html'), '/app.js': ('app.js', 'text/javascript'), '/style.css': ('style.css', 'text/css'),
                '/presentation.js': ('presentation.js', 'text/javascript'), '/presentation.css': ('presentation.css', 'text/css'),
                '/presentation.json': ('presentation.json', 'application/json'), '/notes': ('teaching-notes.html', 'text/html'),
                '/notes.css': ('notes.css', 'text/css'), '/brand.css':('brand.css','text/css'), '/architecture':('architecture.html','text/html'), '/architecture.pdf':('architecture.pdf','application/pdf'),
                '/algorithms': ('algorithms.html','text/html'), '/algorithms.js':('algorithms.js','text/javascript'),
                '/exchange':('exchange.html','text/html'), '/exchange.js':('exchange.js','text/javascript'),
                '/exchange.css':('exchange.css','text/css'),
                '/handout.pdf': ('handout.pdf', 'application/pdf'),
                '/document.pdf': ('document.pdf', 'application/pdf'),
                '/rehearsal': ('../rehearsal/index.html', 'text/html'),
                '/rehearsal.mp4': ('../rehearsal/presentation-rehearsal.mp4', 'video/mp4'),
                '/rehearsal.vtt': ('../rehearsal/captions.vtt', 'text/vtt'),
                '/rehearsal-script': ('../rehearsal/script.md','text/plain'),
            }
            for figure in ('weak-parent.svg', 'signed-four-vertex.svg', 'classroom-partition.svg', 'luna-trace.svg', 'solver-trace.svg','evolutionary-cycle.svg','architecture-overview.svg','system-architecture.svg','request-data-flow.svg'):
                static['/figures/' + figure] = ('../../figures/' + figure, 'image/svg+xml')
            if path not in static: return self.reply({'error': 'not found'}, 404)
            filename, mime = static[path]
            asset = HERE / 'static' / filename
            if not asset.is_file(): return self.reply({'error': 'asset not built; run just build'}, 404)
            size = asset.stat().st_size
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
            with asset.open('rb') as stream:
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
                if parts in (['api', 'runs'], ['api', 'reset']):
                    if not secrets.compare_digest(token, self.server.bootstrap): raise PermissionError('write token required')
                    run = self.server.manager.reset(body) if parts[-1] == 'reset' else self.server.manager.create(body)
                    if parts[-1] == 'reset': self.server.tokens.clear()
                    return self.reply(self.server.register(run), 201)
                if len(parts) == 4 and parts[:2] == ['api', 'runs'] and parts[-1] in ('start', 'stop', 'continue'):
                    run = self.server.manager.get(parts[2])
                    if not secrets.compare_digest(token, self.server.tokens.get(run.id, 'invalid')): raise PermissionError('run write token required')
                    if body != {}: raise ValueError('start/stop require an empty object')
                    if parts[-1] == 'continue':
                        return self.reply({'continued':run.continue_round(), 'run_id':run.id})
                    if parts[-1] == 'start':
                        started = self.server.manager.start(run)
                        return self.reply({'started': started, 'run_id': run.id})
                    run.stop()
                    return self.reply(run.snapshot())
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
        print(json.dumps({'vendored_files_verified': verified, 'live': live_access(), 'recursive_agent_calls': False})); return
    import shutil
    if shutil.which("pandoc"):
        from build_presentation import build
        build()
    elif not (HERE/"static/presentation.json").is_file():
        parser.error("presentation bundle missing: generate with python demo/build_presentation.py on the author machine")
    server = DemoServer(('127.0.0.1', args.port))
    def shutdown(*_):
        threading.Thread(target=server.shutdown, daemon=True).start()
    signal.signal(signal.SIGINT, shutdown); signal.signal(signal.SIGTERM, shutdown)
    print(f'Max-Cut demo: http://127.0.0.1:{server.server_address[1]} (local only)', flush=True)
    try: server.serve_forever(poll_interval=0.1)
    finally:
        server.manager.close(); server.server_close()


if __name__ == '__main__': main()
