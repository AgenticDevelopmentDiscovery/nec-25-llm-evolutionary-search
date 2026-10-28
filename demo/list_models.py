"""List TAMU-accessible model IDs. Metadata GET only; no generation or agent call."""
import json
import os
import re
import urllib.request
import urllib.error
from settings import load_local_env, provider_settings, redact
from model_worker import open_api


def main():
    load_local_env()
    settings = provider_settings()
    if settings['provider'] != 'tamu_chat_completions': raise ValueError('select DEMO_LLM_PROVIDER=tamu first')
    key = os.environ.get(settings['key_name'])
    if not key: raise ValueError(settings['key_name'] + ' is absent')
    request = urllib.request.Request('https://chat-api.tamu.ai/api/models', headers={'Authorization':'Bearer '+key,'Accept':'application/json'})
    try:
        with open_api(request) as response: body = json.loads(response.read(2_000_000))
    except urllib.error.HTTPError as error:
        raw = error.read(8192).decode(errors='replace')
        try:
            body = json.loads(raw)
            detail = body.get('error', body.get('detail', 'no public diagnostic'))
            diagnostic = json.dumps(detail)[:600]
        except (ValueError, TypeError):
            title = re.search(r'<title[^>]*>(.*?)</title>', raw, re.S | re.I)
            diagnostic = 'HTML response: ' + (title.group(1).strip()[:200] if title else 'no title')
        raise ValueError(redact(f'TAMU model list HTTP {error.code}; ' + diagnostic)) from None
    models = body.get('data', [])
    ids = sorted({m['id'] for m in models if isinstance(m,dict) and isinstance(m.get('id'),str)})
    if not ids: raise ValueError('TAMU returned no accessible model IDs')
    print(redact(json.dumps({'provider':settings['provider'],'model_ids':ids,'generation_calls':0},indent=2)))


if __name__=='__main__':
    try: main()
    except Exception as error:
        print(redact(str(error))[:500]); raise SystemExit(1)
