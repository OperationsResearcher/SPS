(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const colors = ['#4f46e5','#0ea5e9','#10b981','#f59e0b','#ef4444','#8b5cf6','#db2777','#0d9488'];

  function drawArc(svg, cx, cy, r0, r1, a0, a1, fill, label, info) {
    const ns = 'http://www.w3.org/2000/svg';
    const large = (a1 - a0) > Math.PI ? 1 : 0;
    const p = document.createElementNS(ns, 'path');
    const x0 = cx + r0 * Math.cos(a0), y0 = cy + r0 * Math.sin(a0);
    const x1 = cx + r1 * Math.cos(a0), y1 = cy + r1 * Math.sin(a0);
    const x2 = cx + r1 * Math.cos(a1), y2 = cy + r1 * Math.sin(a1);
    const x3 = cx + r0 * Math.cos(a1), y3 = cy + r0 * Math.sin(a1);
    p.setAttribute('d', `M${x0},${y0} L${x1},${y1} A${r1},${r1} 0 ${large} 1 ${x2},${y2} L${x3},${y3} A${r0},${r0} 0 ${large} 0 ${x0},${y0} Z`);
    p.setAttribute('fill', fill);
    p.setAttribute('stroke', '#fff');
    p.setAttribute('stroke-width', '2');
    p.style.cursor = 'pointer';
    p.addEventListener('mouseenter', () => { document.getElementById('info').textContent = info; p.setAttribute('opacity', '0.7'); });
    p.addEventListener('mouseleave', () => { document.getElementById('info').textContent = ''; p.setAttribute('opacity', '1'); });
    svg.appendChild(p);
  }

  function draw(tree){
    const svg = document.getElementById('sb');
    svg.innerHTML='';
    const cx=350, cy=350;
    const rings = [50, 130, 230, 330];  // vizyon merkez 50, strat 130, sub 230, surec 330

    // Merkez vizyon
    const ns = 'http://www.w3.org/2000/svg';
    const circ = document.createElementNS(ns, 'circle');
    circ.setAttribute('cx', cx); circ.setAttribute('cy', cy); circ.setAttribute('r', rings[0]);
    circ.setAttribute('fill', '#0f172a');
    svg.appendChild(circ);
    const t = document.createElementNS(ns, 'text');
    t.setAttribute('x', cx); t.setAttribute('y', cy+5); t.setAttribute('text-anchor', 'middle');
    t.setAttribute('fill', '#fff'); t.setAttribute('font-weight', '700'); t.setAttribute('font-size', '14');
    t.textContent = 'Vizyon';
    svg.appendChild(t);

    // Stratejiler — ağırlığa göre slice
    const strats = tree.children;
    const totalV = strats.reduce((s,c)=>s+c.value,0) || 1;
    let a = -Math.PI/2;
    strats.forEach((s, i) => {
      const slice = (s.value/totalV) * Math.PI * 2;
      const col = colors[i % colors.length];
      drawArc(svg, cx, cy, rings[0], rings[1], a, a+slice, col, s.name, `${s.name} — ağırlık %${s.value}`);
      // Alt stratejiler eşit pay
      const subs = s.children || [];
      const sliceSub = slice / Math.max(subs.length, 1);
      let sa = a;
      subs.forEach((ss, j) => {
        drawArc(svg, cx, cy, rings[1], rings[2], sa, sa+sliceSub, col, ss.name, `${ss.name} (alt strateji)`);
        // Süreçler
        const procs = ss.children || [];
        const sliceP = sliceSub / Math.max(procs.length, 1);
        let pa = sa;
        procs.forEach(p => {
          drawArc(svg, cx, cy, rings[2], rings[3], pa, pa+sliceP, col, p.name, `${p.name} (süreç)`);
          pa += sliceP;
        });
        sa += sliceSub;
      });
      a += slice;
    });
  }

  async function load(){
    try {
      const j = await (await fetch('/k-report/api/sunburst',{credentials:'same-origin'})).json();
      if (!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      draw(j.tree);
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error'); err.style.display='block'; err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
