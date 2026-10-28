"""Editable SVG diagrams for the local architecture, never model-generated images."""
from pathlib import Path
from html import escape
import subprocess
import re
OUT=Path(__file__).resolve().parents[1]/'figures'
MAROON='#500000';INK='#30272a';LINE='#8b6e76'
def svg(w,h,body):return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="{MAROON}"/></marker></defs><rect width="100%" height="100%" fill="white"/>{body}</svg>'
def text(x,y,s,size=22,color=INK,anchor='start'):return f'<text x="{x}" y="{y}" font-family="DejaVu Sans,sans-serif" font-size="{size}" fill="{color}" text-anchor="{anchor}">{escape(s)}</text>'
def box(x,y,w,h,title,lines):
 s=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#f7eeee" stroke="{MAROON}" stroke-width="2"/>'+text(x+15,y+32,title,24,MAROON)
 for i,line in enumerate(lines):s+=text(x+15,y+66+i*26,line,19)
 return s
def arrow(d,label='',x=0,y=0):
 # Explicit arrowheads survive both browsers and ImageMagick's SVG rasterizer.
 points=[];px=py=0
 for command,numbers in re.findall(r'([MHV])([0-9 .-]+)',d):
  vals=[float(v) for v in numbers.split()]
  if command=='M':px,py=vals
  elif command=='H':px=vals[0]
  else:py=vals[0]
  points.append((px,py))
 ex,ey=points[-1];sx,sy=points[-2];dx=ex-sx;dy=ey-sy;length=(dx*dx+dy*dy)**.5;ux,uy=dx/length,dy/length
 triangle=f'{ex},{ey} {ex-11*ux+5*uy},{ey-11*uy-5*ux} {ex-11*ux-5*uy},{ey-11*uy+5*ux}'
 return f'<path d="{d}" fill="none" stroke="{MAROON}" stroke-width="3"/><polygon points="{triangle}" fill="{MAROON}"/>'+ (text(x,y,label,17) if label else '')

body=f'<rect x="300" y="12" width="1035" height="610" rx="14" fill="#f9f7f6" stroke="{LINE}" stroke-dasharray="8 6"/>'+text(330,45,'LOCAL PYTHON SERVER + OWNED WORKERS',20,MAROON)
for args in [(25,250,235,125,'Browser',['presentation + controls','read public events']), (330,250,250,125,'HTTP handler',['routes + write tokens','loopback :8766']), (655,250,270,125,'Run controller',['freeze starts; select','round gate + limits']), (1020,65,280,135,'Model worker',['API key in environment','one tool-free request']), (1410,65,285,135,'TAMU Luna API',['HTTPS request / stream','external computation']), (1020,250,280,125,'Numerical worker',['trusted solver programs','bounded subprocess']), (1020,470,280,120,'Original-edge checks',['witness + completeness','backend & controller']), (655,470,270,120,'Selection + history',['top ≤3 complete solvers','parents for next round']), (330,470,250,120,'Events + records',['append-only JSONL','SSE / reconnect / replay'])]:body+=box(*args)
body+=arrow('M260 310 H325','POST',272,290)+arrow('M580 310 H650','run',600,290)+arrow('M790 250 V130 H1015','context',810,115)+arrow('M1300 100 H1405','request',1310,82)+arrow('M1410 165 H1305','public text',1315,189)+arrow('M925 310 H1015','program',938,292)+arrow('M1160 375 V465','signs',1173,425)+arrow('M1020 528 H930','fitness',942,507)+arrow('M790 470 V380','survivors',800,425)+arrow('M655 528 H585','events',593,510)+arrow('M450 590 V640 H145 V380','SSE to browser',165,630)
body+=text(25,710,'Only the model worker sends an API request. The browser never receives the API key.',24,MAROON)
(OUT/'system-architecture.svg').write_text(svg(1740,740,body))
body=''
items=[('Seed population','researcher checks algorithms'),('Variation','derive children from parents'),('Evaluate','same harness and budget'),('Select','retain measured survivors')]
for i,(title,sub)in enumerate(items):
 x=15+350*i;body+=box(x,25,310,120,title,[sub]);
 if i<3:body+=arrow(f'M{x+310} 85 H{x+345}')
body+=arrow('M1220 150 V205 H515 V150','survivors → next variation',560,193)
(OUT/'evolutionary-cycle.svg').write_text(svg(1425,230,body))
body=''
for i,(title,lines)in enumerate([('Browser intent',['POST /api/runs','POST .../start']),('Controller context',['programs + trial evidence','history + bounds + budget']),('API request',['system: instructions/schema','user: JSON context']),('Measured return',['public JSON → validation','execute → score → select'])]):
 x=15+i*350;body+=box(x,30,315,135,title,lines)
 if i<3:body+=arrow(f'M{x+315} 97 H{x+345}')
body+=text(25,218,'HTTPS Authorization is added by the worker; it is excluded from displayed request bodies.',21,MAROON)
(OUT/'request-data-flow.svg').write_text(svg(1425,245,body))
for name in ['system-architecture','evolutionary-cycle','request-data-flow']:
 subprocess.run(['convert','-background','white',str(OUT/(name+'.svg')),'-alpha','off','-depth','8',str(OUT/(name+'.png'))],check=True)
print('Rendered three SVG/PNG architecture figures.')
# A compact projection diagram and a portrait detailed diagram for the document.
body=''
for args in [(15,30,300,125,'Browser',['pages + controls','same-origin requests']), (375,30,365,125,'Local server / controller',['Manager + Run state','budgets, workers, records']), (800,30,300,125,'Model worker',['private API credential','HTTPS / public stream']), (1160,30,300,125,'TAMU Luna',['propose stage programs','no numerical execution'])]:body+=box(*args)
for d in ['M315 92 H370','M740 92 H795','M1100 92 H1155']:body+=arrow(d)
body+=arrow('M555 160 V230 H165 V160','measured events / SSE → browser',210,217)
body+=text(665,245,'Controller runs numerical kernels, checks witnesses and selects survivors.',20,MAROON)
(OUT/'architecture-overview.svg').write_text(svg(1500,285,body))
body='<path d="M385 10 H750 V360 H1145 V990 H10 V360 H385 Z" fill="#faf7f7" stroke="#ad8f96" stroke-dasharray="8 6"/>'+text(410,35,'LOCAL SERVER',20,MAROON)
for args in [(25,65,300,135,'Browser',['presentation + checkboxes','control / read events']), (420,65,300,135,'HTTP routes',['localhost:8766','write tokens + origin check']), (825,65,300,135,'TAMU Luna API',['external HTTPS service','public response stream']), (25,420,300,135,'Event feed',['sequence-numbered events','SSE + reconnect']), (420,420,300,135,'Run controller',['freeze starts + context','own one bounded run']), (825,420,300,135,'Model worker',['API key in environment','data-only model request']), (25,775,300,135,'Local records',['ignored request / response','trial files + verified logs']), (420,775,300,135,'Select + inherit',['top ≤3 complete solvers','next parents + feedback']), (825,775,300,135,'Numerical worker',['trusted algorithm stages','original-edge checking'])]:body+=box(*args)
body+=arrow('M325 130 H415','POST / GET',333,112)+arrow('M570 200 V415','create / start / continue',585,315)+arrow('M720 475 H820','context',735,458)+arrow('M825 515 H725','JSON',755,507)+arrow('M955 420 V205','HTTPS',835,300)+arrow('M1000 200 V415','public text',1015,350)+arrow('M720 525 H770 V815 H820','program',775,690)+arrow('M825 850 H725','verified trials',725,875)+arrow('M570 775 V560','survivors',583,680)+arrow('M420 485 H330','emit',350,466)+arrow('M175 420 V205','SSE updates',190,315)+arrow('M175 555 V770','append records',190,680)+arrow('M420 850 H330','evidence',333,830)
body+=text(25,1030,'Workers are owned child processes. Scoring is checked in both adapter and controller.',20,MAROON)
(OUT/'system-architecture.svg').write_text(svg(1160,1060,body))
for name in ['architecture-overview','system-architecture']:
 subprocess.run(['convert','-background','white',str(OUT/(name+'.svg')),'-alpha','off','-depth','8',str(OUT/(name+'.png'))],check=True)
