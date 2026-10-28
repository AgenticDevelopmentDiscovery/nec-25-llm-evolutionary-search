"""Render vector teaching figures from an actual NUMERICAL ONLY event record."""
import argparse
import json
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape
from controller import HERE, verify_result


def document(width,height,body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="#ffffff"/>{body}</svg>'


def text(x,y,value,size=24,color='#203842'):
    return f'<text x="{x}" y="{y}" font-family="DejaVu Sans,sans-serif" font-size="{size}" fill="{color}">{escape(str(value))}</text>'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True);args=p.parse_args()
    if len(args.run)!=32 or any(c not in '0123456789abcdef' for c in args.run):raise ValueError('expected local run ID')
    events=[json.loads(line) for line in (HERE/'runs'/args.run/'events.jsonl').read_text().splitlines()]
    if events[-1]['mode']!='numerical' or events[-1]['status']!='finished':raise ValueError('requires completed numerical recording')
    baseline=next(e for e in events if e['type']=='baseline_scored');verify_result(baseline)
    edges=__import__('backend').load_graph(__import__('backend').INSTANCE).edges
    body=''
    xy=lambda i:(25+(i%10)*29,25+(i//10)*29)
    for u,v,w in edges:
        x,y=xy(u);xx,yy=xy(v)
        hot=(baseline['assignment'][u]==baseline['assignment'][v]) if w>0 else (baseline['assignment'][u]!=baseline['assignment'][v])
        style=f'stroke="{"#d66836" if hot else "#a7b8c0"}" stroke-width="{1.8 if hot else 1}"'+(' stroke-dasharray="3 3"' if w<0 else '')
        lines=[(x,y,xx,yy)]
        if abs(x-xx)>100:lines=[(x,y,5 if x<xx else 306,y),(xx,yy,5 if xx<x else 306,yy)]
        elif abs(y-yy)>100:lines=[(x,y,x,5 if y<yy else 306),(xx,yy,xx,5 if yy<y else 306)]
        for a,c,d,e in lines:body+=f'<line x1="{a}" y1="{c}" x2="{d}" y2="{e}" {style}/>'
    for i,s in enumerate(baseline['assignment']):
        x,y=xy(i);body+=f'<circle cx="{x}" cy="{y}" r="4.3" fill="{"#087f7c" if s==1 else "#ffffff"}" stroke="#203842" stroke-width="1.3"/>'
    body+=text(360,65,'100 vertices / 200 signed edges',26)+text(360,128,'Weak parent: cut 58',36)+text(360,182,'Instructor reference: 68',30)+text(360,230,'Reference optimality is unproven.',22)+text(360,278,'Solid + / dashed - / hot = frustrated',20)
    out=HERE.parent/'figures';(out/'weak-parent.svg').write_text(document(1000,320,body))
    boxes=[('Parents','genomes + measured scores'),('LLM','bounded proposals'),('Evaluator','original-edge cuts'),('Elite pool','rank / keep at most 3')]
    body=''
    for i,(title,subtitle) in enumerate(boxes):
        x=10+i*300
        body+=f'<rect x="{x}" y="25" width="265" height="105" rx="8" fill="{"#d8efeb" if i==1 else "#eef2f4"}" stroke="#2e616d" stroke-width="2"/>'
        body+=text(x+15,65,title,28)+text(x+15,103,subtitle,17)
        if i<3:body+=f'<path d="M {x+268} 77 h 26 m -8 -6 l 8 6 -8 6" stroke="#267d7d" fill="none" stroke-width="3"/>'
    body+='<path d="M 1050 135 v 34 H 145 v -31 m -6 8 l 6 -8 6 8" stroke="#267d7d" stroke-width="3" fill="none"/>'
    body+=text(385,207,'selected parents + failures feed the next proposal',23)
    (out/'search-loop.svg').write_text(document(1200,225,body))
    best=[(e['elapsed'],e['best']['cut']) for e in events if e['type']=='best_updated']
    xmax=events[-1]['elapsed'];xx=lambda t:70+860*t/xmax;yy=lambda c:130-80*(c-56)/14
    body=text(72,24,'NUMERICAL ONLY / seed 3 / measured best-cut events',22)
    for cut in [58,62,68]:
        body+=f'<line x1="70" x2="935" y1="{yy(cut)}" y2="{yy(cut)}" stroke="#cbd7dc" stroke-dasharray="4 4"/>'+text(20,yy(cut)+6,cut,19)
    d=f'M {xx(best[0][0])} {yy(best[0][1])}'
    for t,c in best[1:]:d+=f' H {xx(t)} V {yy(c)}'
    body+=f'<path d="{d}" fill="none" stroke="#087f7c" stroke-width="4"/>'
    for t,c in best:body+=f'<circle cx="{xx(t)}" cy="{yy(c)}" r="4" fill="#087f7c"/>'
    body+=text(70,165,'0s',18)+text(815,165,f'{xmax:.2f}s total',18)+text(640,43,'68: reference matched',20)
    (out/'measured-trace.svg').write_text(document(1000,175,body))
    for name in ('weak-parent', 'search-loop', 'measured-trace'):
        subprocess.run(['convert', '-background', 'white', '-density', '180', '-font', 'DejaVu-Sans', str(out/f'{name}.svg'), '-alpha', 'off', '-depth', '8', str(out/f'{name}.png')], check=True)
    print(json.dumps({'source_run':args.run,'mode':'numerical','verified_best_events':best,'figures':3}))


if __name__=='__main__':main()
