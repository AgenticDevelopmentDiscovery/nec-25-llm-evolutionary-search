'use strict';
const edges=[[0,1,2],[1,2,-1],[2,3,2],[3,0,1]],names=['A','B','C','D'];let signs=[1,1,1,1];
const cut=s=>edges.reduce((sum,[i,j,w])=>sum+w*(1-s[i]*s[j])/2,0);
function render(){document.getElementById('toyState').textContent=`Signs: ${signs.map((s,i)=>`${names[i]}=${s>0?'+1':'−1'}`).join(' · ')}. Recomputed cut: ${cut(signs)}.`;}
for(let i=0;i<4;i++)document.getElementById('flip'+names[i]).addEventListener('click',()=>{const before=cut(signs),gain=edges.reduce((a,[u,v,w])=>a+(u===i?w*signs[i]*signs[v]:v===i?w*signs[i]*signs[u]:0),0);signs[i]*=-1;render();document.getElementById('toyResult').textContent=`Flip ${names[i]}: predicted gain ${gain}; complete rescoring ${before} → ${cut(signs)}; change ${cut(signs)-before}.`;});
document.getElementById('resetToy').addEventListener('click',()=>{signs=[1,1,1,1];document.getElementById('toyResult').textContent='';render();});
function acceptance(){const t=Number(document.getElementById('temperature').value);document.getElementById('acceptance').textContent=`T = ${t.toFixed(1)}: P(accept loss of 2) = exp(−2/${t.toFixed(1)}) = ${(100*Math.exp(-2/t)).toFixed(2)}%.`;}
document.getElementById('temperature').addEventListener('input',acceptance);render();acceptance();
