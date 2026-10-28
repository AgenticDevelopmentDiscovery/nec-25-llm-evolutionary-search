"""Private local settings; explicit provider credentials never cross destinations."""
import os
from pathlib import Path

KEY_NAMES = ('OPENAI_API_KEY', 'TAMUS_AI_CHAT_API_KEY')
ALLOWED = {*KEY_NAMES, 'OPENAI_MODEL', 'DEMO_LLM_PROVIDER',
           'TAMUS_AI_CHAT_MODEL', 'TAMUS_AI_CHAT_API_ENDPOINT'}
REAL_PROVIDERS = frozenset({'openai_responses', 'tamu_chat_completions'})
ENDPOINTS = {'openai_responses': 'https://api.openai.com/v1/responses',
             'tamu_chat_completions': 'https://chat-api.tamu.ai/api/chat/completions'}


def load_local_env(path=None):
    path = Path(path or Path(__file__).resolve().with_name('.env'))
    if not path.exists(): return
    if path.stat().st_size > 16384: raise ValueError('local .env is too large')
    for number, line in enumerate(path.read_text().splitlines(), 1):
        line = line.strip()
        if not line or line.startswith('#'): continue
        key, separator, value = line.partition('=')
        key, value = key.strip(), value.strip()
        if not separator or key not in ALLOWED:
            raise ValueError(f'unsupported setting on .env line {number}; see .env.example for allowed names')
        if value.startswith(('"', "'")):
            if len(value) < 2 or value[-1] != value[0]: raise ValueError(f'unclosed quote on .env line {number}')
            value = value[1:-1]
        if value:
            # A supplied environment variable takes precedence. No value is printed.
            os.environ.setdefault(key, value)


def provider_settings():
    provider = os.environ.get('DEMO_LLM_PROVIDER', 'openai')
    if provider == 'openai':
        return {'provider': 'openai_responses', 'protocol': 'responses', 'key_name': 'OPENAI_API_KEY',
                'model_name': 'OPENAI_MODEL', 'model': os.environ.get('OPENAI_MODEL'),
                'endpoint': ENDPOINTS['openai_responses']}
    if provider == 'tamu':
        base = os.environ.get('TAMUS_AI_CHAT_API_ENDPOINT', 'https://chat-api.tamu.ai').rstrip('/')
        if base != 'https://chat-api.tamu.ai':
            raise ValueError('TAMU endpoint must be https://chat-api.tamu.ai; credentials are not sent to other hosts')
        return {'provider': 'tamu_chat_completions', 'protocol': 'chat_completions',
                'key_name': 'TAMUS_AI_CHAT_API_KEY', 'model_name': 'TAMUS_AI_CHAT_MODEL',
                'model': os.environ.get('TAMUS_AI_CHAT_MODEL', 'protected.gpt-5.6-luna'),
                'endpoint': ENDPOINTS['tamu_chat_completions']}
    raise ValueError('DEMO_LLM_PROVIDER must be tamu or openai')


def redact(message):
    for name in KEY_NAMES:
        key = os.environ.get(name)
        if key: message = message.replace(key, '[redacted]')
    return message
