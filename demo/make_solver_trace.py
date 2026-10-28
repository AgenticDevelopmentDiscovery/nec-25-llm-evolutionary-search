"""Render measured best-witness evidence from the verified two-call solver run."""
import argparse,json,subprocess
from controller import Manager,HERE
from make_figures import document,text

def main():
 p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args()
 source=Manager().recordings()[a.run];events=source['events'];best=[(e['elapsed'],e['best']['cut']) for e in events if e['type']=='best_updated']
 lo=min(c for t,c in best)-.3;hi=max(c for t,c in best)+.3;xmax=source['seconds'];x=lambda t:100+810*t/xmax;y=lambda c:145-90*(c-lo)/(hi-lo)
 body=text(100,25,'RECORDED LIVE / Luna / 2 model calls / guided pauses included',20)
 for cut in [396,400,402.5209]:
  body+=f'<line x1="100" x2="920" y1="{y(cut)}" y2="{y(cut)}" stroke="#bdcbd0" stroke-dasharray="4 3"/>'+text(4,y(cut)+5,f'{cut:g}',16)
 d=f'M {x(best[0][0])} {y(best[0][1])}'
 for t,c in best[1:]:d+=f' H {x(t)} V {y(c)}'
 d+=f' H {x(xmax)}';body+=f'<path d="{d}" fill="none" stroke="#087f7c" stroke-width="3"/>'
 for e in events:
  if e['type']=='model_started':body+=f'<line x1="{x(e["elapsed"])}" x2="{x(e["elapsed"])}" y1="45" y2="150" stroke="#b66132" stroke-dasharray="3 3"/>'+text(x(e['elapsed'])+4,47,f'call {e["call"]}',15)
 body+=text(100,180,'0s',16)+text(790,180,f'{xmax:.2f}s',16)
 target=HERE.parent/'figures/solver-trace.svg';target.write_text(document(1000,195,body))
 subprocess.run(['convert','-background','white',str(target),'-alpha','off','-depth','8',str(target.with_suffix('.png'))],check=True)
 (HERE/'evidence/solver_trace_provenance.json').write_text(json.dumps({'source_run':a.run,'events_sha256':source['sha256'],'best_events':best,'models':source['models'],'seconds':xmax},indent=2)+'\n')
if __name__=='__main__':main()
