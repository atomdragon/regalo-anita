// See: docs/decisions/0001-escenas.md
const audio=document.querySelector('#hachiware-audio'),canvas=document.querySelector('#hachi-canvas'),ctx=canvas.getContext('2d'),status=document.querySelector('#hachi-status');
let active=false,loading,raf=0,cues=[],currentCue=null,currentMode=null;
// See: docs/decisions/0002-ascii-source.md
// Source already contains ASCII art. Decode it once rather than converting its glyphs again.
const clip=document.createElement('video');
clip.src='video/hachiware.mp4';clip.muted=true;clip.loop=true;clip.playsInline=true;clip.preload='auto';
canvas.width=720;canvas.height=800;
async function load(){
 if(clip.readyState>=2)return;
 if(!loading)loading=new Promise((resolve,reject)=>{
  const ready=()=>{cleanup();if(audio.paused)clip.pause();resolve();};const failed=()=>{cleanup();loading=null;reject(new Error('No se pudo cargar la animación.'));};
  const cleanup=()=>{clip.removeEventListener('loadeddata',ready);clip.removeEventListener('error',failed);};
  clip.addEventListener('loadeddata',ready,{once:true});clip.addEventListener('error',failed,{once:true});clip.load();clip.play().catch(()=>{});
 });await loading;
}
function draw(){
 if(clip.readyState<2)return;
 const duration=Number.isFinite(clip.duration)?Math.min(25,clip.duration):25;
 const target=audio.currentTime%duration;
 if(!clip.seeking&&Math.abs(clip.currentTime-target)>.12)clip.currentTime=target;
 // The top 800 pixels hold the ASCII performance; the lower part is a code editor.
 ctx.drawImage(clip,0,24,720,800,0,0,720,800);
}
clip.addEventListener('seeked',()=>{if(active)draw();});
clip.addEventListener('loadeddata',()=>{if(active)draw();});
function glyphs(container,cue,language="jp"){
 container.replaceChildren();
 for(const token of (language==="es"?cue.esTokens:cue.tokens)){const span=document.createElement('span');span.className='karaoke-char';span.textContent=token.text;span.dataset.start=token.start;span.dataset.end=token.end;container.append(span);}
}
function captions(){
 const time=audio.currentTime, cue=cues.find(c=>time>=c.start&&time<c.end);
 const mode=document.querySelector('#caption-mode').value;
 const box=document.querySelector('#lyrics-box');box.dataset.mode=mode;
 if(cue!==currentCue||mode!==currentMode){
  const jp=document.querySelector('#caption-jp'),es=document.querySelector('#caption-es');jp.replaceChildren();es.textContent='';
  if(cue){if(['both','jp'].includes(mode))glyphs(jp,cue);if(['both','es'].includes(mode))glyphs(es,cue,'es');}
  box.querySelectorAll('.lyric-item').forEach(b=>{const selected=Number(b.dataset.start)===cue?.start;b.classList.toggle('active',selected);if(selected)b.setAttribute('aria-current','true');else b.removeAttribute('aria-current');});
  if(cue!==currentCue&&cue&&active){const row=box.querySelector('.active');if(row){const r=row.getBoundingClientRect(),v=box.getBoundingClientRect();box.scrollTo({top:box.scrollTop+r.top-v.top-box.clientHeight/2+r.height/2,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});}}
  currentCue=cue;currentMode=mode;
 }
 document.querySelectorAll('.karaoke-char').forEach(span=>{const a=Number(span.dataset.start),b=Number(span.dataset.end);const percent=b>a?Math.max(0,Math.min(100,(time-a)/(b-a)*100)):(time>=b?100:0);span.style.setProperty('--sung',percent+'%');});
}

function update(){draw();captions();const format=t=>`${Math.floor(t/60).toString().padStart(2,'0')}:${Math.floor(t%60).toString().padStart(2,'0')}`;document.querySelector('#hachi-current-time').textContent=format(audio.currentTime);document.querySelector('#hachi-duration').textContent=format(Number.isFinite(audio.duration)?audio.duration:0);const seekbar=document.querySelector('#hachi-seek');seekbar.max=Number.isFinite(audio.duration)?audio.duration:87.4;seekbar.value=audio.currentTime;}
function loop(){raf=0;if(!active||document.hidden||audio.paused)return;update();raf=requestAnimationFrame(loop);}
function buttons(){for(const id of ['hachi-play-btn','hachi-canvas-play-btn'])document.getElementById(id).textContent=audio.ended?'Volver a escuchar':audio.paused?'Reproducir':'Pausar';}
export async function show(value){active=value;if(!value){clip.pause();audio.pause();cancelAnimationFrame(raf);raf=0;}else{try{await load();await document.fonts.ready;update();}catch(e){status.textContent=e.message;}}}
export async function play(){if(!audio.paused){audio.pause();return;}try{await load();if(!active||document.hidden)return;await audio.play();if(!active||document.hidden){audio.pause();return;}status.textContent='';}catch(e){status.textContent='No se pudo iniciar. Pulsa Reproducir para intentarlo otra vez.';}}
export function restart(){audio.pause();seek(0);play();}
export function seek(t){audio.currentTime=Math.max(0,Math.min(Number(t)||0,Number.isFinite(audio.duration)?audio.duration:87.4));if(clip.readyState>=2)clip.currentTime=audio.currentTime%25;update();}
export function mute(){audio.muted=!audio.muted;document.querySelector('#hachi-mute-btn').textContent=audio.muted?'Activar sonido':'Silenciar';}
export function capture(){if(clip.readyState<2)return;draw();const a=document.createElement('a');a.download='hachiware-ascii.png';a.href=canvas.toDataURL();a.click();}
audio.addEventListener('play',()=>{if(active){clip.currentTime=audio.currentTime%25;clip.play().catch(()=>{});}buttons();if(!raf)loop();});audio.addEventListener('pause',()=>{clip.pause();const box=document.querySelector('#lyrics-box');box.scrollTo({top:box.scrollTop,behavior:'instant'});buttons();cancelAnimationFrame(raf);raf=0;update();});audio.addEventListener('ended',()=>{buttons();status.textContent='Fin de la canción. Puedes volver a escucharla.';});audio.addEventListener('loadedmetadata',update);audio.addEventListener('seeked',update);document.addEventListener('visibilitychange',()=>{if(document.hidden)audio.pause();});
document.querySelector('#caption-mode').addEventListener('change',captions);
// System volume remains in the phone's media output path; do not attenuate with a second slider.
async function loadLyrics(){
 try{
  const response=await fetch('subtitles/hitorigotsu-karaoke.json');if(!response.ok)throw Error('Letra no disponible');cues=await response.json();
  const box=document.querySelector('#lyrics-box');box.replaceChildren();
  for(const cue of cues){const b=document.createElement('button');b.type='button';b.className='lyric-item';b.dataset.start=cue.start;b.setAttribute('aria-label',cue.jp+' — '+cue.es);
   const jp=document.createElement('span');jp.className='karaoke-jp';jp.lang='ja';glyphs(jp,cue);
   const es=document.createElement('span');es.className='karaoke-es';glyphs(es,cue,'es');b.append(jp,es);b.onclick=()=>seek(cue.start);box.append(b);
  }captions();
 }catch(e){const box=document.querySelector('#lyrics-box');const retry=document.createElement('button');retry.type='button';retry.className='action-btn';retry.textContent='Volver a cargar la letra';retry.onclick=loadLyrics;box.replaceChildren(retry);}
}
loadLyrics();
