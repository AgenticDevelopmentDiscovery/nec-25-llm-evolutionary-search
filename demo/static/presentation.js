'use strict';
const $=id=>document.getElementById(id);
let deck,frameIndex=0,step=0,view='present',timing=null,mainReturn=null;
const mainCount=()=>deck.main_frame_count;
const sectionStart=()=>deck.frames[frameIndex].appendix?mainCount():0;
const sectionEnd=()=>deck.frames[frameIndex].appendix?deck.frames.length-1:mainCount()-1;
const frameLabel=i=>deck.frames[i].appendix?`Appendix A${i-mainCount()+1}`:`frame ${i+1}`;
function fit(){const stage=$('stage');$('frame').style.setProperty('--scale',Math.min(stage.clientWidth/1600,stage.clientHeight/900));}
function locationState(){const match=location.hash.match(/^#([a-z-]+)(?:\/(\d+))?$/);if(!match)return;const n=deck.frames.findIndex(f=>f.id===match[1]);if(n>=0){frameIndex=n;step=Math.min(deck.frames[n].reveals-1,Number(match[2]||0));}}
function record(action){if(timing)timing.events.push({seconds:(performance.now()-timing.started)/1000,frame:deck.frames[frameIndex].id,reveal:step+1,view,appendix:deck.frames[frameIndex].appendix,action});}
function render(changeFrame=true){const f=deck.frames[frameIndex];if(changeFrame){$('frame').replaceChildren();const title=document.createElement('h1');title.textContent=f.appendix?`Appendix A${frameIndex-mainCount()+1}: ${f.title}`:f.title;const body=document.createElement('div');body.className='framebody';// Trusted, locally built Pandoc content, never model or API output.
body.innerHTML=f.html;$('frame').append(title,body);$('frame').dataset.frame=f.id;body.querySelectorAll('.question,.block,.answer').forEach(e=>e.classList.add('reveal'));}
$('frame').querySelectorAll('.reveal').forEach((el,i)=>{el.classList.toggle('shown',i<=step);el.setAttribute('aria-hidden',String(i>step));el.inert=i>step;});
const start=sectionStart(),end=sectionEnd(),before=deck.frames.slice(start,frameIndex).reduce((s,x)=>s+x.reveals,0),total=deck.frames.slice(start,end+1).reduce((s,x)=>s+x.reveals,0);
$('position').textContent=`${f.appendix?'Appendix A':'Main frame '}${frameIndex-start+1} / ${end-start+1} · slide ${before+step+1} / ${total} · block ${step+1} / ${f.reveals}`;
$('frames').value=String(frameIndex);$('previous').disabled=frameIndex===start&&step===0;$('next').disabled=frameIndex===end&&step===f.reveals-1;
$('appendixNav').textContent=f.appendix?'← Main presentation':'Appendix →';
const seconds=deck.frames.slice(start,frameIndex).reduce((s,x)=>s+x.seconds,0);const stamp=n=>`${Math.floor(n/60)}:${String(n%60).padStart(2,'0')}`;$('pace').textContent=`${f.appendix?'Optional':'Plan'} ${stamp(seconds)}–${stamp(seconds+f.seconds)}`;
$('progress').firstElementChild.style.width=`${100*(before+step+1)/total}%`;
history.replaceState(null,'',`${location.pathname}#${f.id}/${step}`);sessionStorage.setItem('maxcut-presentation',JSON.stringify({id:f.id,step}));$('openDemo').hidden=!f.id.startsWith('demo-');fit();}
function advance(delta){const old=frameIndex;if(delta>0){if(step<deck.frames[frameIndex].reveals-1)step++;else if(frameIndex<sectionEnd()){frameIndex++;step=0;}}else if(step>0)step--;else if(frameIndex>sectionStart()){frameIndex--;step=deck.frames[frameIndex].reveals-1;}render(old!==frameIndex);record('reveal');}
function jumpTo(index,reveal=0){if(!deck.frames[frameIndex].appendix&&deck.frames[index].appendix)mainReturn={index:frameIndex,reveal:step};frameIndex=index;step=reveal;render();record('jump');}
function showView(next){view=next;$('presentView').hidden=next!=='present';$('demoView').hidden=next!=='demo';$('presentTab').classList.toggle('selected',next==='present');$('demoTab').classList.toggle('selected',next==='demo');$('returnToFrame').textContent=`← Return to ${frameLabel(frameIndex)}: ${deck.frames[frameIndex].title}`;fit();record('view');}
$('next').addEventListener('click',()=>advance(1));$('previous').addEventListener('click',()=>advance(-1));$('frames').addEventListener('change',()=>jumpTo(Number($('frames').value)));
$('appendixNav').addEventListener('click',()=>{if(deck.frames[frameIndex].appendix){const back=mainReturn||{index:mainCount()-1,reveal:deck.frames[mainCount()-1].reveals-1};jumpTo(back.index,back.reveal);}else jumpTo(mainCount());});
$('demoTab').addEventListener('click',()=>showView('demo'));
$('openDemo').addEventListener('click',()=>{const scenario={'demo-limited':'contrast_limited','demo-informed':'contrast_informed','demo-harder':'harder'}[deck.frames[frameIndex].id];if(scenario)$('demoFrame').contentWindow.postMessage({type:'stage-demo-preset',scenario},location.origin);showView('demo');});
for(const id of ['presentTab','returnToFrame'])$(id).addEventListener('click',()=>showView('present'));
$('fullscreen').addEventListener('click',()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen());$('help').addEventListener('click',()=>$('helpDialog').showModal());$('closeHelp').addEventListener('click',()=>$('helpDialog').close());$('motion').addEventListener('change',()=>document.body.classList.toggle('motion-disabled',!$('motion').checked));
document.addEventListener('keydown',event=>{if(event.target.closest('input,select,textarea')||$('helpDialog').open||(event.target.closest('button')&&[' ','Enter'].includes(event.key)))return;if(event.key.toLowerCase()==='d'){event.preventDefault();showView(view==='present'?'demo':'present');return;}if(view!=='present')return;if(['ArrowRight',' ','PageDown'].includes(event.key)){event.preventDefault();advance(1);}if(['ArrowLeft','PageUp'].includes(event.key)){event.preventDefault();advance(-1);}if(event.key==='Home'||event.key==='End'){event.preventDefault();const target=event.key==='Home'?sectionStart():sectionEnd();jumpTo(target,event.key==='Home'?0:deck.frames[target].reveals-1);}if(event.key.toLowerCase()==='f')$('fullscreen').click();});
$('rehearsal').addEventListener('click',()=>{if(timing)return;timing={started:performance.now(),events:[],kind:'presenter-clock; speech not independently verified',target_seconds:1500};$('rehearsal').disabled=true;$('saveTiming').hidden=false;$('timingStatus').hidden=false;record('start');});
$('saveTiming').addEventListener('click',()=>{if(!timing)return;record('save');const elapsed=(performance.now()-timing.started)/1000;const result={kind:timing.kind,elapsed_seconds:elapsed,target_seconds:1500,within_budget:elapsed<=1500,main_planned_seconds:deck.prepared_seconds,appendix_optional_seconds:deck.appendix_seconds,events:timing.events};const url=URL.createObjectURL(new Blob([JSON.stringify(result,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='presenter-timing.json';a.click();URL.revokeObjectURL(url);$('timingStatus').textContent=`Saved ${elapsed.toFixed(1)}s timing. Save the file under ignored demo/rehearsal/.`;timing=null;$('rehearsal').disabled=false;$('saveTiming').hidden=true;});
setInterval(()=>{if(timing){const seconds=Math.floor((performance.now()-timing.started)/1000);$('timingStatus').textContent=`Aloud rehearsal ${Math.floor(seconds/60)}:${String(seconds%60).padStart(2,'0')} / 25:00 · timing only`; }},500);
window.addEventListener('message',event=>{if(event.origin===location.origin&&event.source===$('demoFrame').contentWindow&&event.data?.type==='return-to-presentation')showView('present');});
window.addEventListener('resize',fit);window.addEventListener('hashchange',()=>{if(deck){locationState();render();}});
function populateFrames(){
  $('frames').replaceChildren();
  const main=document.createElement('optgroup'),appendix=document.createElement('optgroup');
  main.label='Main presentation';appendix.label='Optional appendix';$('frames').append(main,appendix);
  for(const [i,f]of deck.frames.entries()){
    const option=document.createElement('option');option.value=i;
    option.textContent=`${f.appendix?'A'+(i-mainCount()+1):i+1}. ${f.title}`;
    (f.appendix?appendix:main).append(option);
  }
}
let sourceBusy=false,sourceError=null,sourceNoticeTimer=null;
function showSourceNotice(message,error=false){
  clearTimeout(sourceNoticeTimer);
  $('sourceNotice').textContent=message;$('sourceNotice').dataset.error=String(error);$('sourceNotice').hidden=false;
  if(!error)sourceNoticeTimer=setTimeout(()=>$('sourceNotice').hidden=true,3500);
}
async function readDeck(){
  const response=await fetch('/presentation.json',{cache:'no-store'});
  if(!response.ok)throw Error('Presentation could not be read.');
  return response.json();
}
function applyDeck(updated){
  const id=deck.frames[frameIndex].id,oldIndex=frameIndex,oldStep=step;
  const returnId=mainReturn?deck.frames[mainReturn.index]?.id:null;
  deck=updated;
  const found=deck.frames.findIndex(f=>f.id===id);
  frameIndex=found>=0?found:Math.min(oldIndex,deck.frames.length-1);
  step=Math.min(oldStep,deck.frames[frameIndex].reveals-1);
  if(mainReturn){const n=deck.frames.findIndex(f=>f.id===returnId&&!f.appendix);mainReturn=n>=0?{index:n,reveal:Math.min(mainReturn.reveal,deck.frames[n].reveals-1)}:null;}
  populateFrames();render();
  if(view==='demo')$('returnToFrame').textContent=`← Return to ${frameLabel(frameIndex)}: ${deck.frames[frameIndex].title}`;
  record('source-update');
}
async function checkSource(){
  if(!deck||sourceBusy||document.hidden)return;
  sourceBusy=true;
  try{
    const response=await fetch('/api/presentation',{cache:'no-store'});
    if(response.status===404)return; // Older servers still support manual rebuild/refresh.
    if(!response.ok)throw Error('Source preview is unavailable.');
    const status=await response.json();
    if(status.error){
      if(status.error!==sourceError)showSourceNotice(`Saved prose could not be built. Showing the last successful frames.\n${status.error}`,true);
      sourceError=status.error;return;
    }
    if(status.source_sha256&&status.source_sha256!==deck.source_sha256){
      applyDeck(await readDeck());showSourceNotice('Frames updated from saved prose.');
    }else if(sourceError)showSourceNotice('Saved prose is valid.');
    sourceError=null;
  }catch(error){
    const message='Preview disconnected. Existing frames remain available; updates resume when the server returns.';
    if(sourceError!==message)showSourceNotice(message,true);
    sourceError=message;
  }finally{sourceBusy=false;}
}
(async()=>{
  try{
    deck=await readDeck();populateFrames();
    if(!location.hash){try{const saved=JSON.parse(sessionStorage.getItem('maxcut-presentation'));if(saved){const n=deck.frames.findIndex(f=>f.id===saved.id);if(n>=0){frameIndex=n;step=Math.max(0,Math.min(saved.step,deck.frames[n].reveals-1));}}}catch{}}
    else locationState();
    render();checkSource();setInterval(checkSource,2000);
  }catch(error){showSourceNotice('Presentation unavailable. Check the server terminal and saved prose.',true);}
})();
