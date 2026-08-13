(() => {
  'use strict';
  const PN = window.ResChemPhaseNav36D;
  const $ = id => document.getElementById(id);
  const fmt = (x,n=6) => Number(x).toFixed(n);
  const card = (label,value,note='') => `<article class="result-card"><span>${label}</span><strong>${value}</strong>${note?`<small>${note}</small>`:''}</article>`;

  document.querySelectorAll('.tab').forEach(btn => btn.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(x => x.classList.remove('active'));
    btn.classList.add('active');
    $(btn.dataset.panel).classList.add('active');
  }));

  function updateShell(){
    const n=Number($('shell-n').value), l=Number($('shell-kind').value), k=Number($('shell-k').value);
    const cap=2*(2*l+1), holes=cap-k, selfDual=k===2*l+1;
    $('shell-k').max=String(cap); $('shell-k-output').value=String(k);
    const v=PN.encodeShell(n,l,k), R=PN.orderParameter(v), mean=PN.meanPhase(v), bloch=PN.projectBloch(v);
    $('shell-result').innerHTML=[
      card('capacity C_l',cap), card('holes',holes), card('particle-hole partner',`${['s','p','d','f'][l]}^${holes}`),
      card('self-dual',selfDual?'YES':'NO'), card('PhaseNav R',fmt(R)), card('mean phase',fmt(mean)),
      card('Bloch θ',fmt(bloch[0])), card('Bloch φ',fmt(bloch[1]))
    ].join('');
    renderLanes(v);
  }

  function renderLanes(v){
    const host=$('phase-lanes'); if(!host) return;
    host.innerHTML=v.map((x,i)=>`<div class="lane"><span>${String(i+1).padStart(2,'0')}</span><i style="--p:${(x/PN.TAU)*100}%"></i><b>${fmt(x,3)}</b></div>`).join('');
  }

  function updateConformal(){
    const re=Number($('phi-re').value), im=Number($('phi-im').value), a=Number($('anchor').value);
    const zr=re-a, zi=im, den=zr*zr+zi*zi;
    const singular=den===0;
    const er=singular?Infinity:zr/den, ei=singular?Infinity:-zi/den;
    $('conformal-result').innerHTML=[card('ζ',`${fmt(zr,4)} ${zi<0?'-':'+'} ${fmt(Math.abs(zi),4)}i`),card('η = 1/ζ',singular?'SINGULAR':`${fmt(er,4)} ${ei<0?'-':'+'} ${fmt(Math.abs(ei),4)}i`),card('|ζ|',fmt(Math.sqrt(den),6)),card('status',singular?'ANCHOR HIT':'FINITE')].join('');
  }

  async function loadData(){
    try{
      const carbon=await fetch('../benchmarks/CARBON_STATE_AVERAGED_P_RELAXATION_V0_1.json').then(r=>{if(!r.ok)throw new Error('carbon benchmark');return r.json();});
      $('overview-carbon').textContent=carbon.status;
      $('carbon-summary').innerHTML=[
        card('baseline Ē',fmt(carbon.baseline.state_average_hartree,9),'Ha'),
        card('best sampled θ',fmt(carbon.best_sampled.theta_rad,3),'rad'),
        card('best Ē',fmt(carbon.best_sampled.state_average_hartree,9),'Ha'),
        card('variational gain',fmt(carbon.improvement_hartree,9),'Ha')
      ].join('');
      const pts=carbon.local_refined_bracket;
      function interp(theta){
        if(theta<=pts[1].theta_rad){const a=pts[0],b=pts[1],t=(theta-a.theta_rad)/(b.theta_rad-a.theta_rad);return a.state_average_hartree+t*(b.state_average_hartree-a.state_average_hartree);}
        const a=pts[1],b=pts[2],t=(theta-a.theta_rad)/(b.theta_rad-a.theta_rad);return a.state_average_hartree+t*(b.state_average_hartree-a.state_average_hartree);
      }
      const draw=()=>{const th=Number($('theta').value);$('theta-output').value=fmt(th,3);$('theta-result').textContent=`Recorded-bracket interpolation: Ē ≈ ${fmt(interp(th),9)} Ha. This is visualization only, not a CI solve.`;};
      $('theta').addEventListener('input',draw); draw();
      $('control-cards').innerHTML=[
        card('Carbon p relaxation',carbon.status,'production numerical candidate'),
        card('Experimental energies in objective',carbon.acceptance.experimental_term_energies_used_in_objective?'YES':'NO'),
        card('TIR used',carbon.acceptance.tir_used?'YES':'NO'),
        card('Full MCSCF', 'NO','next gate')
      ].join('');
      $('data-status').textContent='Benchmark data: loaded';
    }catch(err){
      $('overview-carbon').textContent='Unavailable';
      $('data-status').textContent='Benchmark data: unavailable — run via HTTP server';
    }
  }

  ['shell-n','shell-kind','shell-k'].forEach(id=>$(id).addEventListener('input',updateShell));
  ['phi-re','phi-im','anchor'].forEach(id=>$(id).addEventListener('input',updateConformal));
  updateShell(); updateConformal(); loadData();
})();
