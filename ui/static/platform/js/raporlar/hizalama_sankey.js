(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

  function statCard(label, value, color) {
    return `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;">
      <div style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(label)}</div>
      <div style="font-size:22px;font-weight:700;color:${color};">${esc(value)}</div></div>`;
  }

  function drawSankey(nodes, links) {
    // basit kolon-bazlı sankey (D3 yok, native SVG)
    const svg = document.getElementById('sankey');
    svg.innerHTML = '';
    const width = svg.clientWidth || 1100;
    const height = 700;
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);

    // her seviyenin x koordinatı
    const levels = [0, 1, 2, 3];
    const xPos = { 0: 50, 1: width * 0.30, 2: width * 0.58, 3: width - 220 };
    const colW = 130;

    // her seviyedeki node'ları y'ye yerleştir
    const byLevel = {};
    levels.forEach(l => byLevel[l] = nodes.filter(n => n.level === l));
    const yMap = {};
    levels.forEach(l => {
      const arr = byLevel[l];
      const slotH = (height - 40) / Math.max(arr.length, 1);
      arr.forEach((n, i) => {
        yMap[n.id] = {
          x: xPos[l],
          y: 20 + i * slotH + slotH / 2,
          w: colW,
          h: Math.max(slotH - 6, 18),
        };
      });
    });

    // linkler (curved path)
    links.forEach(lk => {
      const s = nodes[lk.source];
      const t = nodes[lk.target];
      const sp = yMap[s.id], tp = yMap[t.id];
      if (!sp || !tp) return;
      const sx = sp.x + sp.w, sy = sp.y;
      const tx = tp.x, ty = tp.y;
      const mx = (sx + tx) / 2;
      const strokeW = Math.max(1, Math.min(lk.value / 4, 18));
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', `M${sx},${sy} C${mx},${sy} ${mx},${ty} ${tx},${ty}`);
      path.setAttribute('stroke', s.color);
      path.setAttribute('stroke-width', strokeW);
      path.setAttribute('fill', 'none');
      path.setAttribute('opacity', '0.35');
      svg.appendChild(path);
    });

    // node'lar (kutu + label)
    nodes.forEach(n => {
      const p = yMap[n.id]; if (!p) return;
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.innerHTML = `
        <rect x="${p.x}" y="${p.y - p.h/2}" width="${p.w}" height="${p.h}" rx="4" fill="${n.color}" opacity="0.92"/>
        <text x="${p.x + p.w/2}" y="${p.y + 4}" font-size="10.5" font-weight="600" fill="#fff" text-anchor="middle">${esc(n.label.substring(0,28))}</text>`;
      svg.appendChild(g);
    });
  }

  async function load() {
    try {
      const j = await (await fetch('/raporlar/api/hizalama-sankey', {credentials:'same-origin'})).json();
      if (!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display = 'none';
      document.getElementById('content').style.display = 'block';
      const s = j.summary;
      document.getElementById('summary').innerHTML = [
        statCard('Strateji', s.strategy_nodes, '#4f46e5'),
        statCard('Alt Strateji', s.sub_strategy_nodes, '#8b5cf6'),
        statCard('Süreç', s.process_nodes, '#10b981'),
        statCard('Bağlantı', s.total_links, '#0ea5e9'),
        statCard('Plan Yılı', s.plan_year || '—', '#64748b'),
      ].join('');
      drawSankey(j.nodes, j.links);
    } catch(e) {
      document.getElementById('loading').style.display='none';
      const err = document.getElementById('error'); err.style.display='block'; err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
