// See: docs/decisions/0001-escenas.md
import * as T from '../vendor/three/three.module.js';
import {OrbitControls} from '../vendor/three/addons/controls/OrbitControls.js';
import {EffectComposer} from '../vendor/three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from '../vendor/three/addons/postprocessing/RenderPass.js';
import {UnrealBloomPass} from '../vendor/three/addons/postprocessing/UnrealBloomPass.js';
import {OutputPass} from '../vendor/three/addons/postprocessing/OutputPass.js';
let renderer,scene,camera,controls,composer,tree,lights,star,snow,raf=0,active=false,paused=false,time=0,last=0,slow=0,spinning=!matchMedia('(prefers-reduced-motion: reduce)').matches;
const reduce=matchMedia('(prefers-reduced-motion: reduce)');
const host=document.querySelector('#tree-stage');
function mesh(geo,color,parent=scene){const m=new T.Mesh(geo,new T.MeshStandardMaterial({color,roughness:.45,metalness:.15}));parent.add(m);return m;}
export function init(){
 if(renderer)return;
 try{
 renderer=new T.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(Math.min(devicePixelRatio,innerWidth<650?1:1.5));host.append(renderer.domElement);
 scene=new T.Scene();scene.background=new T.Color('#d9effc');scene.fog=new T.Fog('#d9effc',16,38);
 camera=new T.PerspectiveCamera(42,1,.1,70);camera.position.set(9,7,13);
 controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,3,0);controls.enableDamping=true;controls.enablePan=false;controls.minDistance=9;controls.maxDistance=23;controls.maxPolarAngle=Math.PI*.48;
 scene.add(new T.HemisphereLight(0xffffff,0x779cb5,2));const sun=new T.DirectionalLight(0xfff6e2,2);sun.position.set(7,12,7);scene.add(sun);
 const island=mesh(new T.CylinderGeometry(4.8,4.5,.65,64),0xffffff);island.position.y=-.35;
 tree=new T.Group();scene.add(tree);const trunk=mesh(new T.CylinderGeometry(.25,.35,1.3,16),0x98795f,tree);trunk.position.y=.6;
 for(let tier=0;tier<7;tier++){
 const y=1+tier*.68,r=2.5-tier*.29;
 const branch=mesh(new T.ConeGeometry(r,1.8,32),tier%2?0x77b5c4:0x8fcbd3,tree);branch.position.y=y;
 const cap=mesh(new T.ConeGeometry(r*.92,1.2,32),0xf5fbff,tree);cap.position.y=y+.38;
 }
 lights=new T.Group();tree.add(lights);
 for(let i=0;i<160;i++){const y=.6+i/160*5.7,a=i*.36,r=2.65*(1-y/7);const bulb=mesh(new T.SphereGeometry(.055,8,6),i%3?0xc6edff:0xffde8a,lights);bulb.position.set(Math.cos(a)*r,y,Math.sin(a)*r);bulb.material.emissive.set(i%3?0x89d7ff:0xffd26c);bulb.material.emissiveIntensity=3;}
 for(let i=0;i<55;i++){const y=1+(i%11)*.42,a=i*2.4,r=2.6*(1-y/7);const ball=mesh(new T.SphereGeometry(.13,12,8),[0x7cbee8,0xffffff,0xc5d4e0][i%3],tree);ball.material.metalness=.7;ball.position.set(Math.cos(a)*r,y,Math.sin(a)*r);}
 const shape=new T.Shape();for(let i=0;i<10;i++){const a=i*Math.PI/5+Math.PI/2,r=i%2?.22:.5;const x=Math.cos(a)*r,y=Math.sin(a)*r;i?shape.lineTo(x,y):shape.moveTo(x,y);}shape.closePath();star=mesh(new T.ExtrudeGeometry(shape,{depth:.12,bevelEnabled:false}),0xffd978,tree);star.position.set(0,6.4,0);star.material.emissive.set(0xffce58);
 for(let i=0;i<7;i++){const gift=mesh(new T.BoxGeometry(.6,.5,.6),[0xa1d6f3,0xf2d4e1,0xffffff][i%3]);gift.position.set(Math.cos(i)*3,.25,Math.sin(i)*3);const ribbon=mesh(new T.BoxGeometry(.1,.52,.62),0xffffff,gift);}
 new T.TextureLoader().load('images/hachiware-navidad.jpeg',tex=>{tex.colorSpace=T.SRGBColorSpace;const pic=new T.Sprite(new T.SpriteMaterial({map:tex}));pic.position.set(-3.4,1,1);pic.scale.set(1.5,1.5,1);scene.add(pic);});
 const count=innerWidth<650?350:850;const pos=new Float32Array(count*3);for(let i=0;i<pos.length;i+=3){pos[i]=(Math.random()-.5)*24;pos[i+1]=Math.random()*15;pos[i+2]=(Math.random()-.5)*24;}
 const geo=new T.BufferGeometry();geo.setAttribute('position',new T.BufferAttribute(pos,3));snow=new T.Points(geo,new T.PointsMaterial({color:0xffffff,size:.075,transparent:true,opacity:.85}));scene.add(snow);
 composer=new EffectComposer(renderer);composer.addPass(new RenderPass(scene,camera));composer.addPass(new UnrealBloomPass(new T.Vector2(400,300),.22,.35,2));composer.addPass(new OutputPass());
 new ResizeObserver(resize).observe(host);resize();
 }catch(e){host.innerHTML='<img src="images/hachiware-navidad.jpeg" alt="Hachiware navideño"><p>No se pudo iniciar el árbol 3D en este dispositivo.</p>';console.warn(e);}
}
function resize(){if(!renderer||!host.clientWidth)return;const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h);composer?.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();}
function frame(now){raf=0;if(!active||document.hidden||!composer)return;const dt=Math.min((now-last)/1000,.05);last=now;if(!paused&&!reduce.matches)time+=dt;
 const t=reduce.matches?12:time;tree.scale.setScalar(Math.max(.001,Math.min(1,t/5)));lights.visible=t>5;star.visible=t>9;star.material.emissiveIntensity=t>9?2:0;
 controls.autoRotate=false;controls.update(dt);
 if(!paused&&spinning)tree.rotation.y+=dt*.32;
 if(!paused&&!reduce.matches){const a=snow.geometry.attributes.position;for(let i=1;i<a.array.length;i+=3){a.array[i]-=dt*.8;if(a.array[i]<0)a.array[i]=15;}a.needsUpdate=true;}
 if(dt>.04&&++slow>90){renderer.setPixelRatio(1);composer.passes[1].enabled=false;resize();slow=0;}
 composer.render();raf=requestAnimationFrame(frame);
}
export function show(value){active=value;if(value){init();last=performance.now();if(!raf)raf=requestAnimationFrame(frame);}else{cancelAnimationFrame(raf);raf=0;}}
export function pause(){paused=!paused;document.querySelector('#tree-play-btn').textContent=paused?'Reanudar':'Pausar';}
export function restart(){time=0;if(tree)tree.rotation.y=0;paused=false;document.querySelector('#tree-play-btn').textContent='Pausar';reset();}
export function reset(){camera?.position.set(9,7,13);controls?.target.set(0,3,0);controls?.update();}
export function capture(){if(renderer){const a=document.createElement('a');a.download='arbol-celeste.png';a.href=renderer.domElement.toDataURL();a.click();}}
document.addEventListener('visibilitychange',()=>{if(active)show(true);});

export function toggleRotation(){spinning=!spinning;const button=document.querySelector('#tree-spin-btn');button.textContent=spinning?'Detener giro':'Girar árbol';button.setAttribute('aria-pressed',String(spinning));}
const spinButton=document.querySelector('#tree-spin-btn');spinButton.textContent=spinning?'Detener giro':'Girar árbol';spinButton.setAttribute('aria-pressed',String(spinning));
