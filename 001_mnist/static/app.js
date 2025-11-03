
// Canvas setup
const c = document.getElementById('canvas');
const ctx = c.getContext('2d');
const brush = document.getElementById('brush');
const eraseBtn = document.getElementById('erase');
let drawing = false, last = null, erasing = false;

function resetCanvas(){
  ctx.fillStyle = '#FFFFFF';
  ctx.fillRect(0,0,c.width,c.height);
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.lineWidth = parseInt(brush.value,10);
  ctx.strokeStyle = '#000000';
}
resetCanvas();

function pos(e){
  const r = c.getBoundingClientRect();
  const clientX = (e.touches ? e.touches[0].clientX : e.clientX);
  const clientY = (e.touches ? e.touches[0].clientY : e.clientY);
  return { x: clientX - r.left, y: clientY - r.top };
}
function draw(p){
  if(!last){ last = p; return; }
  ctx.beginPath();
  ctx.moveTo(last.x, last.y);
  ctx.lineTo(p.x, p.y);
  ctx.strokeStyle = erasing ? '#FFFFFF' : '#000000';
  ctx.stroke();
  last = p;
}
c.addEventListener('mousedown', e=>{ drawing=true; last=null; draw(pos(e)); });
c.addEventListener('mousemove', e=>{ if(drawing) draw(pos(e)); });
window.addEventListener('mouseup', ()=> drawing=false);
c.addEventListener('touchstart', e=>{ e.preventDefault(); drawing=true; last=null; draw(pos(e)); }, {passive:false});
c.addEventListener('touchmove',  e=>{ e.preventDefault(); if(drawing) draw(pos(e)); }, {passive:false});
c.addEventListener('touchend',   e=>{ e.preventDefault(); drawing=false; }, {passive:false});
brush.addEventListener('input', ()=> ctx.lineWidth = parseInt(brush.value,10));

document.getElementById('clear').onclick = ()=>{ resetCanvas(); setPrediction(null); };
eraseBtn.onclick = ()=>{ erasing = !erasing; eraseBtn.textContent = 'Eraser: ' + (erasing ? 'On' : 'Off'); };

// Prediction UI
const predDigit = document.getElementById('predDigit');
const predConf  = document.getElementById('predConf');
const probsPre  = document.getElementById('probs');
const barsRoot  = document.getElementById('bars');

function setPrediction(out){
  if(!out){
    predDigit.textContent = '–';
    predConf.textContent = '–';
    probsPre.textContent = '';
    barsRoot.innerHTML = '';
    for(let i=0;i<10;i++) addBar(i, 0);
    return;
  }
  predDigit.textContent = out.prediction;
  predConf.textContent  = out.confidence.toFixed(3);
  probsPre.textContent  = JSON.stringify(out.probabilities.map(p=>+p.toFixed(6)), null, 2);
  barsRoot.innerHTML = '';
  out.probabilities.forEach((p,i)=> addBar(i, p));
}
function addBar(i, p){
  const pct = Math.round(p * 100);

  const row = document.createElement('div');
  row.className = 'flex items-center gap-3';

  const label = document.createElement('div');
  label.className = 'w-6 text-sm tabular-nums';
  label.textContent = String(i);

  const bg = document.createElement('div');
  bg.className = 'flex-1 h-2 rounded-full bg-zinc-200 dark:bg-zinc-800 overflow-hidden';

  const fill = document.createElement('div');
  fill.className = 'h-2 bg-zinc-900 dark:bg-zinc-100';
  fill.style.width = pct + '%';   // <-- this draws the progress

  const pctText = document.createElement('div');
  pctText.className = 'w-12 text-right text-xs tabular-nums';
  pctText.textContent = pct + '%';

  bg.appendChild(fill);
  row.appendChild(label);
  row.appendChild(bg);
  row.appendChild(pctText);
  barsRoot.appendChild(row);
}
setPrediction(null);

document.getElementById('predict').onclick = async ()=>{
  const dataURL = c.toDataURL('image/png');
  const res = await fetch('/predict', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({image:dataURL}) });
  const out = await res.json();
  setPrediction(out);
};
