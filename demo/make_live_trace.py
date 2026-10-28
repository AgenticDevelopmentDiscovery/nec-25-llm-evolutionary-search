"""Build the Luna teaching trace from a verified genuine run; no model requests."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from controller import HERE, Manager
from make_figures import document, text


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',required=True);args=parser.parse_args()
    source=Manager().recordings().get(args.run)
    if source is None or source['models'] != ['protected.gpt-5.6-luna']:
        raise ValueError('requires a completed, verified genuine Luna recording')
    events=source['events'];best=[(e['elapsed'],e['best']['cut']) for e in events if e['type']=='best_updated']
    xmax=source['seconds'];xx=lambda t:70+860*t/xmax;yy=lambda c:130-80*(c-56)/14
    body=text(72,24,'RECORDED LIVE LLM / GPT-5.6 Luna / seed 3',22)
    for cut in [58,62,68]:
        body+=f'<line x1="70" x2="935" y1="{yy(cut)}" y2="{yy(cut)}" stroke="#cbd7dc" stroke-dasharray="4 4"/>'+text(20,yy(cut)+6,cut,19)
    d=f'M {xx(best[0][0])} {yy(best[0][1])}'
    for t,c in best[1:]:d+=f' H {xx(t)} V {yy(c)}'
    body+=f'<path d="{d}" fill="none" stroke="#087f7c" stroke-width="4"/>'
    for t,c in best:body+=f'<circle cx="{xx(t)}" cy="{yy(c)}" r="4" fill="#087f7c"/>'
    body+=text(70,165,'0s',18)+text(815,165,f'{xmax:.2f}s total',18)+text(640,43,'68: reference matched',20)
    out=HERE.parent/'figures';svg=out/'luna-trace.svg';png=out/'luna-trace.png';svg.write_text(document(1000,175,body))
    subprocess.run(['convert','-background','white','-density','180','-font','DejaVu-Sans',str(svg),'-alpha','off','-depth','8',str(png)],check=True)
    provenance={'source_run':args.run,'mode':'live','model':source['models'][0],'source_events_sha256':source['sha256'],'best_events':best,'original_seconds':xmax,'figure':'figures/luna-trace.svg'}
    (HERE/'evidence/luna_trace_provenance.json').write_text(json.dumps(provenance,indent=2))
    print(json.dumps(provenance))


if __name__=='__main__':main()
