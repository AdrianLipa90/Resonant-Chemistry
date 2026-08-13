(function(global){
'use strict';
const TAU=Math.PI*2;
function assert36(v){if(!Array.isArray(v)||v.length!==36||v.some(x=>!Number.isFinite(x)))throw new Error('PhaseNav vector must contain exactly 36 finite lanes');return v;}
function rotX(p,a){const[x,y,z]=p,c=Math.cos(a),s=Math.sin(a);return[x,y*c-z*s,y*s+z*c];}
function rotY(p,a){const[x,y,z]=p,c=Math.cos(a),s=Math.sin(a);return[x*c+z*s,y,-x*s+z*c];}
function shellPointsFrom36(v36,opt={}){
 assert36(v36);const PN=global.ResChemPhaseNav36D;if(!PN)throw new Error('ResChemPhaseNav36D adapter required');
 const n=Number(opt.n??2),l=Number(opt.l??1),k=Number(opt.k??3),count=Number(opt.count??720),role=String(opt.role??'particle');
 const R=PN.orderParameter(v36),phase=PN.meanPhase(v36),cap=2*(2*l+1),occ=Math.max(0,Math.min(1,k/Math.max(1,cap))),pts=[];
 for(let i=0;i<count;i++){
  const u=(i+.5)/count,z=1-2*u,b=Math.sqrt(Math.max(0,1-z*z)),a=(i*2.399963229728653+phase)%TAU,lane=v36[i%36];
  const angular=Math.cos((l+1)*a+lane)*Math.pow(Math.abs(z)+.15,Math.max(0,l-1));
  const polar=Math.acos(Math.max(-1,Math.min(1,z)));
  const nodal=l===0?1:Math.cos(l*a+phase)*Math.sin((l+1)*polar);
  const roleShift=role==='hole'?0.05*Math.sin(2*a+phase):0;
  const r=(.65+.16*n)*(1+.12*angular+.055*nodal+.08*Math.sin(lane-phase)+roleShift);
  pts.push({x:r*b*Math.cos(a),y:r*b*Math.sin(a),z:r*z,lane:i%36,alpha:(role==='hole'?.10:.18)+.62*occ,role});
 }
 return{points:pts,R,phase,occupancy:occ,capacity:cap};
}
function mountShell3D(canvas,v36,opt={}){
 assert36(v36);const ctx=canvas.getContext('2d');if(!ctx)throw new Error('canvas unavailable');
 let ax=-.35,ay=.45,drag=false,px=0,py=0,state={...opt},primary=assert36(v36).slice(),overlay=null;
 function project(points,w,h){return points.map(p=>{let r=rotY([p.x,p.y,p.z],ay);r=rotX(r,ax);const d=3.9+r[2],s=Math.min(w,h)*.36/d;return{...p,sx:w/2+r[0]*s,sy:h/2-r[1]*s,depth:d};}).sort((a,b)=>b.depth-a.depth);}
 function drawCloud(q,hole=false){for(const pt of q){ctx.globalAlpha=pt.alpha;ctx.fillStyle=hole?`hsla(${35+(pt.lane/36)*45} 85% 68% / 1)`:`hsla(${190+(pt.lane/36)*110} 75% 65% / 1)`;ctx.beginPath();ctx.arc(pt.sx,pt.sy,hole?1.15:1.45,0,TAU);ctx.fill();}}
 function draw(){const w=canvas.clientWidth,h=canvas.clientHeight;ctx.clearRect(0,0,w,h);const m=shellPointsFrom36(primary,state);drawCloud(project(m.points,w,h),false);if(overlay){const om=shellPointsFrom36(overlay.vector,{...state,...overlay.options,role:'hole'});drawCloud(project(om.points,w,h),true);}ctx.globalAlpha=1;ctx.strokeStyle='rgba(255,255,255,.42)';ctx.lineWidth=1;ctx.beginPath();ctx.arc(w/2,h/2,13,0,TAU);ctx.stroke();ctx.fillStyle='rgba(255,255,255,.96)';ctx.beginPath();ctx.arc(w/2,h/2,6.5,0,TAU);ctx.fill();}
 function resize(){const dpr=Math.min(2,global.devicePixelRatio||1),r=canvas.getBoundingClientRect();canvas.width=Math.max(320,Math.floor(r.width*dpr));canvas.height=Math.max(260,Math.floor(r.height*dpr));ctx.setTransform(dpr,0,0,dpr,0,0);draw();}
 canvas.addEventListener('pointerdown',e=>{drag=true;px=e.clientX;py=e.clientY;canvas.setPointerCapture(e.pointerId);});
 canvas.addEventListener('pointermove',e=>{if(!drag)return;ay+=(e.clientX-px)*.009;ax+=(e.clientY-py)*.009;px=e.clientX;py=e.clientY;draw();});
 canvas.addEventListener('pointerup',()=>drag=false);global.addEventListener('resize',resize);resize();
 return{update(next){state={...state,...next};draw();},setVector(next){primary=assert36(next).slice();draw();},setOverlay(next,options={}){overlay=next?{vector:assert36(next).slice(),options:{...options}}:null;draw();},redraw:draw,destroy(){global.removeEventListener('resize',resize);}};
}
global.ResChemShell3D={assert36,shellPointsFrom36,mountShell3D};
})(window);
