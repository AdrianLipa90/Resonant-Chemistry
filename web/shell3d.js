(function(global){
'use strict';
const TAU=Math.PI*2;
function assert36(v){if(!Array.isArray(v)||v.length!==36||v.some(x=>!Number.isFinite(x)))throw new Error('PhaseNav vector must contain exactly 36 finite lanes');return v;}
function rotX(p,a){const[x,y,z]=p,c=Math.cos(a),s=Math.sin(a);return[x,y*c-z*s,y*s+z*c];}
function rotY(p,a){const[x,y,z]=p,c=Math.cos(a),s=Math.sin(a);return[x*c+z*s,y,-x*s+z*c];}
function shellPointsFrom36(v36,opt={}){
 assert36(v36); const PN=global.ResChemPhaseNav36D;if(!PN)throw new Error('ResChemPhaseNav36D adapter required');
 const n=Number(opt.n??2),l=Number(opt.l??1),k=Number(opt.k??3),count=Number(opt.count??720);
 const R=PN.orderParameter(v36),phase=PN.meanPhase(v36),cap=2*(2*l+1),occ=Math.max(0,Math.min(1,k/Math.max(1,cap))),pts=[];
 for(let i=0;i<count;i++){const u=(i+.5)/count,z=1-2*u,b=Math.sqrt(Math.max(0,1-z*z)),a=(i*2.399963229728653+phase)%TAU,lane=v36[i%36],h=Math.cos((l+1)*a+lane)*Math.pow(Math.abs(z)+.15,Math.max(0,l-1)),r=(.65+.16*n)*(1+.12*h+.08*Math.sin(lane-phase));pts.push({x:r*b*Math.cos(a),y:r*b*Math.sin(a),z:r*z,lane:i%36,alpha:.18+.72*occ});}
 return{points:pts,R,phase,occupancy:occ};
}
function mountShell3D(canvas,v36,opt={}){
 assert36(v36);const ctx=canvas.getContext('2d');if(!ctx)throw new Error('canvas unavailable');let ax=-.35,ay=.45,drag=false,px=0,py=0,state={...opt};
 function draw(){const w=canvas.clientWidth,h=canvas.clientHeight;ctx.clearRect(0,0,w,h);const m=shellPointsFrom36(v36,state),q=m.points.map(p=>{let r=rotY([p.x,p.y,p.z],ay);r=rotX(r,ax);const d=3.7+r[2],s=Math.min(w,h)*.34/d;return{...p,sx:w/2+r[0]*s,sy:h/2-r[1]*s,depth:d};}).sort((a,b)=>b.depth-a.depth);ctx.fillStyle='rgba(255,255,255,.95)';ctx.beginPath();ctx.arc(w/2,h/2,8,0,TAU);ctx.fill();for(const pt of q){ctx.globalAlpha=pt.alpha;ctx.fillStyle=`hsl(${190+(pt.lane/36)*110} 75% 65%)`;ctx.beginPath();ctx.arc(pt.sx,pt.sy,1.4,0,TAU);ctx.fill();}ctx.globalAlpha=1;}
 function resize(){const dpr=Math.min(2,global.devicePixelRatio||1),r=canvas.getBoundingClientRect();canvas.width=Math.max(320,Math.floor(r.width*dpr));canvas.height=Math.max(260,Math.floor(r.height*dpr));ctx.setTransform(dpr,0,0,dpr,0,0);draw();}
 canvas.addEventListener('pointerdown',e=>{drag=true;px=e.clientX;py=e.clientY;canvas.setPointerCapture(e.pointerId);});canvas.addEventListener('pointermove',e=>{if(!drag)return;ay+=(e.clientX-px)*.009;ax+=(e.clientY-py)*.009;px=e.clientX;py=e.clientY;draw();});canvas.addEventListener('pointerup',()=>drag=false);global.addEventListener('resize',resize);resize();
 return{update(next){state={...state,...next};draw();},redraw:draw,destroy(){global.removeEventListener('resize',resize);}};
}
global.ResChemShell3D={assert36,shellPointsFrom36,mountShell3D};
})(window);
