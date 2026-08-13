(function(global){
'use strict';
const TAU=Math.PI*2,PI=Math.PI;
const MOD=(1n<<61n)-1n;
const SCALE=10n**35n;
const LN2_OVER_12=5776226504666210911810267678818141n;
const TAU_FIXED=628318530717958647692528676655900570n;
function assert36(v){if(!Array.isArray(v)||v.length!==36||v.some(x=>!Number.isFinite(x)))throw new Error('PhaseNav vector must contain exactly 36 finite lanes');return v;}
function textHash(text){const bytes=new TextEncoder().encode(String(text));let h=0n;for(const b of bytes)h=(h*256n+BigInt(b))%MOD;for(let i=0;i<13;i++)h=(h%2n===0n?h/2n:3n*h+1n)%MOD;return h;}
function phasePrecise(h,i){const num=(h*BigInt(i+1)*LN2_OVER_12)%TAU_FIXED;return Number(num)/1e35;}
function stateVector36D(eid){const h=textHash(String(eid).toLowerCase());return Array.from({length:36},(_,i)=>Number(phasePrecise(h,i).toFixed(10)));}
function shellId(n,l,k){const letters='spdf';const cap=2*(2*l+1);if(!Number.isInteger(n)||n<1||!Number.isInteger(l)||l<0||l>3||!Number.isInteger(k)||k<0||k>cap)throw new Error('invalid shell state');return `reschem:shell:${n}${letters[l]}${k}`;}
function encodeShell(n,l,k){return stateVector36D(shellId(n,l,k));}
function meanPhase(v){assert36(v);let s=0,c=0;for(const x of v){s+=Math.sin(x);c+=Math.cos(x);}return Math.atan2(s/36,c/36);}
function orderParameter(v){assert36(v);let s=0,c=0;for(const x of v){s+=Math.sin(x);c+=Math.cos(x);}return Math.sqrt(s*s+c*c)/36;}
function distance(a,b){assert36(a);assert36(b);let sum=0;for(let i=0;i<36;i++){let d=((a[i]-b[i])%TAU+TAU)%TAU;if(d>PI)d=TAU-d;sum+=d*d;}return Math.sqrt(sum);}
function superposition(a,b,w=.5){assert36(a);assert36(b);w=Number(w);if(!Number.isFinite(w)||w<0||w>1)throw new Error('weight must be within [0,1]');return a.map((x,i)=>{const re=(1-w)*Math.cos(x)+w*Math.cos(b[i]),im=(1-w)*Math.sin(x)+w*Math.sin(b[i]);return((Math.atan2(im,re)%TAU)+TAU)%TAU;});}
function projectBloch(v){const R=orderParameter(v),phi=meanPhase(v),theta=2*Math.atan2(Math.sqrt(Math.max(0,1-R*R)),Math.min(1,Math.max(0,R)));return[theta,((phi%TAU)+TAU)%TAU];}
global.ResChemPhaseNav36D={TAU,assert36,textHash,stateVector36D,shellId,encodeShell,meanPhase,orderParameter,distance,superposition,projectBloch};
})(window);
