"""Derive the separate architecture page and PDF from its Markdown source."""
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def build():
 static=ROOT/'demo/static';out=ROOT/'output';out.mkdir(exist_ok=True)
 args=['pandoc','demo/ARCHITECTURE.md','--standalone','--toc','--toc-depth=2']
 page=subprocess.check_output(args+['--mathml','--css=/notes.css','--css=/brand.css','-t','html5'],cwd=ROOT,text=True)
 page=page.replace('src="../figures/','src="/figures/').replace('<body>', '<body><nav><a href="/">Presentation</a> · <a href="/demo">Solver demo</a> · <a href="/exchange">Luna exchange</a> · <a href="/architecture.pdf">Download architecture PDF</a></nav><main>').replace('</body>','</main></body>')
 (static/'architecture.html').write_text(page)
 subprocess.run(args+['--pdf-engine=xelatex','--resource-path=.:demo:figures','--lua-filter=filters/pdf-images.lua','--include-in-header=site/document-header.tex','-V','documentclass=article','-V','fontsize=11pt','-V','geometry:margin=0.8in','-V','colorlinks=true','-V','urlcolor=Maroon','-o','output/architecture.pdf'],cwd=ROOT,check=True)
 (static/'architecture.pdf').write_bytes((out/'architecture.pdf').read_bytes())
 print('Built architecture HTML and PDF.')
if __name__=='__main__':build()
