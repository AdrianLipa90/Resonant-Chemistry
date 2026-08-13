(function(global){
  'use strict';
  const TAU = Math.PI * 2;
  const PI = Math.PI;
  function assert36(vec){
    if(!Array.isArray(vec) || vec.length !== 36) throw new Error('PhaseNav vector must have exactly 36 lanes');
    for(const x of vec){ if(!Number.isFinite(x)) throw new Error('PhaseNav vector contains non-finite lane'); }
    return vec;
  }
  function gaugeLock36(vec){ return assert36(vec).map(v => ((v % TAU) + TAU) % TAU); }
  function meanPhase(vec){
    assert36(vec);
    let s=0,c=0;
    for(const v of vec){ s += Math.sin(v); c += Math.cos(v); }
    return Math.atan2(s/36,c/36);
  }
  function orderParameter(vec){
    assert36(vec);
    let s=0,c=0;
    for(const v of vec){ s += Math.sin(v); c += Math.cos(v); }
    return Math.sqrt(s*s+c*c)/36;
  }
  function distance(a,b){
    assert36(a); assert36(b);
    let sum=0;
    for(let i=0;i<36;i++){
      let d=((a[i]-b[i])%TAU+TAU)%TAU;
      if(d>PI) d=TAU-d;
      sum += d*d;
    }
    return Math.sqrt(sum);
  }
  function superposition(a,b,weight){
    assert36(a); assert36(b);
    const w2=Number(weight), w1=1-w2;
    if(!Number.isFinite(w2) || w2<0 || w2>1) throw new Error('weight must be within [0,1]');
    const out=[];
    for(let i=0;i<36;i++){
      const re=w1*Math.cos(a[i])+w2*Math.cos(b[i]);
      const im=w1*Math.sin(a[i])+w2*Math.sin(b[i]);
      out.push(((Math.atan2(im,re)%TAU)+TAU)%TAU);
    }
    return out;
  }
  function projectBloch(vec){
    const R=orderParameter(vec);
    const phi=meanPhase(vec);
    const theta=2*Math.atan2(Math.sqrt(Math.max(0,1-R*R)),Math.min(1,Math.max(0,R)));
    return [((theta%TAU)+TAU)%TAU,((phi%TAU)+TAU)%TAU];
  }
  function encodeShell(n,l,k){
    const cap=2*(2*l+1);
    if(!Number.isInteger(n)||n<1||!Number.isInteger(l)||l<0||l>3||!Number.isInteger(k)||k<0||k>cap) throw new Error('invalid shell state');
    const holes=cap-k;
    const base=[];
    for(let i=0;i<36;i++){
      const harmonic=(i+1)*(n+1)+(l+1)*7+(k+1)*11+(holes+1)*13;
      const phase=(harmonic*0.17320508075688773 + (i%6)*0.2617993877991494) % TAU;
      base.push(phase);
    }
    return gaugeLock36(base);
  }
  global.ResChemPhaseNav36D={TAU,assert36,gaugeLock36,meanPhase,orderParameter,distance,superposition,projectBloch,encodeShell};
})(window);
