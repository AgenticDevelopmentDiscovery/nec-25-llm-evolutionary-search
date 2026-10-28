"""One bounded tool-free model request, using explicit provider-bound credentials.

The owned parent enforces the wall deadline. Only public answer text, completion
metadata, errors and actual usage enter evidence; hidden reasoning is excluded.
"""
import json
import os
from pathlib import Path
import sys
import urllib.request
import urllib.error

from settings import provider_settings, redact


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('provider redirected the API request; check the documented API endpoint/access')


class RequestsResponse:
    """Line-oriented adapter for TAMU's documented requests HTTP client."""
    def __init__(self, response):
        self.response = response
        self.headers = response.headers

    def __enter__(self): return self
    def __exit__(self, *_): self.response.close()
    def __iter__(self): return self.response.iter_lines()
    def close(self): self.response.close()
    def read(self, limit):
        data = bytearray()
        for chunk in self.response.iter_content(chunk_size=8192):
            data.extend(chunk)
            if len(data) > limit: raise ValueError('provider response exceeds byte limit')
        return bytes(data)


def open_api(request):
    # Do not forward bearer credentials through login or cross-host redirects.
    if provider_settings()['provider'] == 'tamu_chat_completions':
        import requests
        response = requests.request(request.get_method(), request.full_url, data=request.data,
            headers=dict(request.header_items()), stream=True, timeout=(10, 35), allow_redirects=False)
        wrapped = RequestsResponse(response)
        if 300 <= response.status_code < 400:
            wrapped.close()
            raise ValueError('provider redirected the API request; check the documented API endpoint/access')
        if response.status_code >= 400:
            raise urllib.error.HTTPError(request.full_url, response.status_code, 'TAMU API error', response.headers, wrapped)
        return wrapped
    return urllib.request.build_opener(NoRedirect).open(request, timeout=35)


def public_error(directory, diagnostic):
    safe = redact(json.dumps(diagnostic, allow_nan=False))
    (directory / 'provider-error.json').write_text(safe)
    raise ValueError('provider response did not complete: ' + safe[:400])


def payload_for(request, settings):
    if settings['protocol'] == 'responses':
        return {**request, 'stream': True, 'store': False, 'tools': []}
    # TAMU documents Chat Completions. Its provider-specific JSON-schema features
    # are not assumed: ask for JSON and independently validate the strict contract.
    schema = request['text']['format']['schema']
    payload = {'model': request['model'], 'stream': True,
            'tools': [], 'tool_ids': [],
            'messages': [{'role': 'system', 'content': request['instructions'] +
                          '\nReturn a JSON object only, without Markdown or explanation. It must match this JSON schema:\n' + json.dumps(schema)},
                         {'role': 'user', 'content': request['input']}]}
    if request['model'] in {'protected.gpt-5.6-sol', 'protected.gpt-5.6-luna'}:
        payload.update(max_completion_tokens=request['max_output_tokens'], reasoning_effort='low')
    else:
        payload['max_tokens'] = request['max_output_tokens']
    return payload


def chat_usage(usage):
    if not isinstance(usage, dict): return None
    checked = {name: usage[source] for name, source in [('input_tokens','prompt_tokens'), ('output_tokens','completion_tokens'), ('total_tokens','total_tokens')]
               if type(usage.get(source)) is int and usage[source] >= 0}
    return checked or None


def read_responses(response, directory, stream, provider, endpoint):
    public = []
    complete = None
    for line in response:
        if not line.startswith(b'data: '): continue
        raw = line[6:].strip()
        if raw == b'[DONE]': break
        event = json.loads(raw)
        kind = event.get('type', '')
        if kind in {'response.output_text.delta', 'response.output_text.done', 'response.refusal.delta', 'response.refusal.done'}:
            stream.write(redact(raw.decode()).encode() + b'\n'); stream.flush()
        if kind == 'response.output_text.delta': public.append(event['delta'])
        if kind == 'response.completed':
            final = event['response']
            complete = {'id': final.get('id'), 'model': final.get('model'), 'usage': final.get('usage'),
                        'status': final.get('status'), 'provider': provider, 'endpoint': endpoint}
        if kind in {'response.failed', 'error', 'response.incomplete'}:
            diagnostic = event.get('error') or event.get('response', {}).get('error') or event.get('response', {}).get('incomplete_details') or {k: event[k] for k in ('type','code','message','param') if k in event}
            public_error(directory, diagnostic)
    return ''.join(public), complete


def read_chat(response, directory, stream, provider, endpoint):
    public = []
    complete = {'provider': provider, 'endpoint': endpoint, 'id': None, 'model': None,
                'usage': None, 'status': 'incomplete'}
    finish = None
    content_type = response.headers.get('Content-Type', '')
    if 'application/json' in content_type:
        # Some gateways return a completed nonstreaming JSON response to stream=True.
        events = [json.loads(response.read(2_000_000))]
    else:
        def events_from_sse():
            for line in response:
                if not line.startswith(b'data: '): continue
                raw = line[6:].strip()
                if raw == b'[DONE]': return
                yield json.loads(raw)
        events = events_from_sse()
    for event in events:
        if event.get('error'): public_error(directory, event['error'])
        if event.get('id'): complete['id'] = event['id']
        if event.get('model'): complete['model'] = event['model']
        if event.get('usage') is not None:
            complete['usage'] = chat_usage(event['usage'])
            complete['provider_usage'] = {k:v for k,v in event['usage'].items() if k in {'prompt_tokens','completion_tokens','total_tokens'} and type(v) is int}
        choices = event.get('choices', [])
        visible = []
        for choice in choices:
            if choice.get('index', 0) != 0: continue
            delta = choice.get('delta', choice.get('message', {}))
            if delta.get('tool_calls') or delta.get('function_call'):
                public_error(directory, {'message':'tool call refused; this proposer has no tools'})
            content = delta.get('content')
            if content is not None:
                if not isinstance(content, str): raise ValueError('unsupported public content format')
                public.append(content)
            if delta.get('refusal'): public_error(directory, {'message':'provider refused the proposal'})
            if choice.get('finish_reason') is not None: finish = choice['finish_reason']
            # Project only public content and finish metadata; reasoning_content,
            # reasoning and other gateway-private fields are never persisted.
            visible.append({'index': 0, 'delta': {'content': content}, 'finish_reason': choice.get('finish_reason')})
        record = {'id': complete['id'], 'model': complete['model'], 'choices': visible, 'usage': complete['usage']}
        stream.write(redact(json.dumps(record, allow_nan=False)).encode() + b'\n'); stream.flush()
    if finish != 'stop': public_error(directory, {'message':'incomplete chat completion', 'finish_reason': finish})
    complete['status'] = 'completed'
    return ''.join(public), complete


def main(directory):
    directory = Path(directory)
    request = json.loads((directory / 'request.json').read_text())
    settings = provider_settings()
    key = os.environ.get(settings['key_name'])
    if not key: raise ValueError(settings['key_name'] + ' is absent')
    # This override is only for isolated transport tests; the controller strips it.
    url = os.environ.get('DEMO_TEST_API_URL', settings['endpoint'])
    testing = url != settings['endpoint']
    if testing and not url.startswith('http://127.0.0.1:'): raise ValueError('unsupported provider URL')
    provider = 'test_transport' if testing else settings['provider']
    payload = payload_for(request, settings)
    (directory / 'payload.json').write_text(json.dumps(payload, indent=2, allow_nan=False))
    (directory / 'transport.json').write_text(json.dumps({'provider': provider, 'endpoint': url,
        'protocol': settings['protocol'], 'public_stream_projection': settings['protocol'] == 'chat_completions'}))
    req = urllib.request.Request(url, data=json.dumps(payload, allow_nan=False).encode(),
                                 headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    try:
        with open_api(req) as response, (directory / 'public-stream.jsonl').open('xb') as stream:
            reader = read_responses if settings['protocol'] == 'responses' else read_chat
            text, complete = reader(response, directory, stream, provider, url)
        # If a provider were to echo a credential, do not persist or admit that output.
        if redact(text) != text: raise ValueError('credential-like output refused; response not recorded')
        (directory / 'response.txt').write_text(text)
        if complete is None or complete['status'] != 'completed': raise ValueError('no complete provider response')
        proposal = json.loads(text)
        (directory / 'result.json').write_text(json.dumps({'proposal': proposal, **complete}, allow_nan=False))
    except urllib.error.HTTPError as error:
        try:
            body = json.loads(error.read(8192))
            detail = body.get('error', body.get('detail', {}))
            if isinstance(detail, dict): detail = {k:detail[k] for k in ('type','code','param','message') if k in detail}
            safe = redact(json.dumps(detail))
        except (ValueError, TypeError): safe = '{}'
        (directory / 'provider-error.json').write_text(safe)
        raise ValueError(f'provider HTTP {error.code}; no automatic retry: ' + safe[:400]) from None


if __name__ == '__main__':
    try:
        main(sys.argv[1])
    except Exception as error:
        print(redact(str(error))[:500], file=sys.stderr)
        sys.exit(1)
