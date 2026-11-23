// The local web copy starts at 17.8 s of the original FLAC, just before the first vocal.
const audio=document.querySelector('#tree-music-audio');
let visible=false;
export function showTreeMusic(active){
 if(!active){visible=false;audio.pause();if(audio.readyState)audio.currentTime=0;return;}
 if(visible)return;
 visible=true;
 if(audio.readyState)audio.currentTime=0;
 // Called from the navigation gesture. Native controls remain available if autoplay is blocked.
 audio.play().then(()=>{if(!visible||document.hidden)audio.pause();}).catch(()=>{});
}
document.addEventListener('visibilitychange',()=>{if(document.hidden)audio.pause();});
