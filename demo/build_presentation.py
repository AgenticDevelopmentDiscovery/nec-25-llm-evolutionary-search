"""Derive server presentation and notes from the shared Pandoc prose; no model calls."""
import json
import hashlib
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / 'demo/static'

def source_hash(root=ROOT):
    files = sorted((root/'sections').glob('*.prose.md'))
    return hashlib.sha256(b''.join(p.read_bytes() for p in [*files,root/'references.bib'])).hexdigest()

def atomic_write(path, content):
    """Readers see a complete artifact even while a preview is rebuilding."""
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                     prefix='.'+path.name, suffix='.tmp', delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(content)
            stream.close()
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)

def pandoc(args, source=None):
    return subprocess.run(['pandoc', *args], input=source, text=True, capture_output=True, check=True, cwd=ROOT).stdout

def reveal_count(blocks):
    """Match the browser's reveal Divs; questions and answers are optional."""
    def count(node):
        if isinstance(node, list):
            return sum(count(item) for item in node)
        if not isinstance(node, dict):
            return 0
        reveal = node.get('t') == 'Div' and any(
            name in node['c'][0][1] for name in ('question', 'block', 'answer'))
        return int(reveal) + sum(count(value) for value in node.values())
    # Plain Markdown or a heading-only frame has one presentation state.
    return max(1, count(blocks))

def build():
    initial_hash = source_hash()
    files = sorted((ROOT/'sections').glob('*.prose.md'))
    doc = json.loads(pandoc([str(p.relative_to(ROOT)) for p in files] + ['-t','json','--citeproc','--bibliography=references.bib']))
    groups=[]
    for block in doc['blocks']:
        if block['t']=='Header' and block['c'][0]==2:
            attr=block['c'][1]
            title=pandoc(['-f','json','-t','plain'],json.dumps({**doc,'meta':{},'blocks':[{'t':'Plain','c':block['c'][2]}]})).strip()
            groups.append({'id':attr[0],'title':title,'seconds':int(dict(attr[2])['data-seconds']),
                           'appendix':'appendix' in attr[1],'blocks':[]})
        elif groups and block['t']!='Header' and not (block['t']=='Div' and block['c'][0][0]=='refs'):
            groups[-1]['blocks'].append(block)
    if not groups: raise ValueError('No frames found; each frame needs a ## heading.')
    notes=[]; frames=[]; appendix_count=0
    for group in groups:
        visible=[]; explanation=[]
        for block in group.pop('blocks'):
            if block['t']=='Div' and 'notes' in block['c'][0][1]: explanation.extend(block['c'][1])
            else: visible.append(block)
        render=lambda blocks:pandoc(['-f','json','-t','html5','--mathml','--wrap=none'],json.dumps({**doc,'meta':{},'blocks':blocks}))
        html=render(visible).replace('src="figures/','src="/figures/')
        count=reveal_count(visible)
        if group['appendix']:
            appendix_count+=1
            if appendix_count==1: notes.append('<h1 id="appendix">Appendix: architecture and API</h1><p>Optional implementation detail, outside the main presentation schedule.</p>')
            label=f'Appendix A{appendix_count}'
        else:
            if appendix_count: raise ValueError('main frames must precede the appendix')
            label=str(len(frames)+1)
        frames.append({**group,'html':html,'reveals':count})
        notes.append(f'<section id="{group["id"]}"><h2>{label}. {group["title"]}</h2>'+render(visible+explanation).replace('src="figures/','src="/figures/')+'</section>')
    if len(frames)==appendix_count: raise ValueError('The presentation needs at least one main frame.')
    result={'source_sha256':initial_hash,'title':'LLM-driven evolutionary search','chapter':'Chapter 10: Agentic Evolutionary Frameworks','frames':frames,
            'main_frame_count':len(frames)-appendix_count,'main_reveals':sum(f['reveals'] for f in frames if not f['appendix']),
            'prepared_seconds':sum(f['seconds'] for f in frames if not f['appendix']),
            'appendix_seconds':sum(f['seconds'] for f in frames if f['appendix']),'reserve_seconds':45}
    if source_hash()!=initial_hash:
        raise ValueError('Prose changed during the build; the next preview check will rebuild the saved version.')
    STATIC.mkdir(exist_ok=True)
    atomic_write(STATIC/'presentation.json',json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    atomic_write(STATIC/'teaching-notes.html','<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Teaching notes · evolutionary search</title><link rel="stylesheet" href="/notes.css"><link rel="stylesheet" href="/brand.css"></head><body><nav><a href="/">Presentation hub</a> · <a href="/document.pdf">PDF notes</a> · <a href="/handout.pdf">Frame handout</a></nav><main><h1>LLM-driven evolutionary search</h1><p>The questions, mechanisms and detailed explanations share the presentation source. Course connection: Chapter 10, Definition 10.2 and Figures 10.1–10.2.</p>'+''.join(notes)+'</main></body></html>')
    print(f'{result["main_frame_count"]} main frames + {appendix_count} appendix frames; {sum(f["reveals"] for f in frames)} overlay slides; {result["prepared_seconds"]} main seconds + 45 reserve; {result["appendix_seconds"]} optional appendix seconds')
    return result

if __name__=='__main__': build()
