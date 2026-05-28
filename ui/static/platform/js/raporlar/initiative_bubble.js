(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const fmt = n => new Intl.NumberFormat('tr-TR').format(Math.round(n));
  const statCard = (l,v,c,sub) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;">
    <div style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div>
    <div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div>
    ${sub ? `<div style="font-size:11px;color:#94a3b8;margin-top:2px;">${esc(sub)}</div>`:''}</div>`;

  function drawBubble(bubbles){
    const svg = document.getElementById('bubble');
    svg.innerHTML='';
    const w = svg.clientWidth || 1100, h = 500;
    svg.setAttribute('viewBox', `0 0 ${w} ${h}`);
    const padL=50, padR=30, padT=20, padB=40;
    // axes
    svg.innerHTML = `
      <line x1="${padL}" y1="${h-padB}" x2="${w-padR}" y2="${h-padB}" stroke="#cbd5e1" stroke-width="1"/>
      <line x1="${padL}" y1="${padT}" x2="${padL}" y2="${h-padB}" stroke="#cbd5e1" stroke-width="1"/>
      <text x="${padL+8}" y="${padT+12}" font-size="11" fill="#64748b">↑ Bütçe Kullanımı %</text>
      <text x="${w-padR-100}" y="${h-padB+24}" font-size="11" fill="#64748b">İlerleme % →</text>
    `;
    // grid
    for (let p of [0,25,50,75,100]) {
      const y = padT + (h-padT-padB) * (1 - p/100);
      svg.innerHTML += `<line x1="${padL}" y1="${y}" x2="${w-padR}" y2="${y}" stroke="#f1f5f9" stroke-width="1"/>
        <text x="${padL-4}" y="${y+3}" font-size="9" fill="#94a3b8" text-anchor="end">${p}</text>`;
    }
    // bubbles
    const maxBudget = Math.max(...bubbles.map(b => b.budget_total), 1);
    bubbles.forEach(b => {
      const x = padL + (w-padL-padR) * (b.progress_pct/100);
      const y = padT + (h-padT-padB) * (1 - Math.min(b.budget_usage_pct,100)/100);
      const r = Math.max(8, Math.min(40, 8 + Math.sqrt(b.budget_total / maxBudget) * 32));
      svg.innerHTML += `
        <circle cx="${x}" cy="${y}" r="${r}" fill="${b.color}" opacity="${b.opacity}" stroke="#fff" stroke-width="1.5">
          <title>${esc(b.code)} · ${esc(b.name)} — bütçe ₺${fmt(b.budget_total)}, harcama %${b.budget_usage_pct}, ilerleme %${b.progress_pct}</title>
        </circle>
        <text x="${x}" y="${y+r+10}" font-size="9" fill="#475569" text-anchor="middle">${esc(b.code)}</text>`;
    });
  }

  async function load(){
    try {
      const j = await (await fetch('/raporlar/api/initiative-bubble',{credentials:'same-origin'})).json();
      if (!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const s = j.summary;
      document.getElementById('summary').innerHTML = [
        statCard('Toplam', s.total, '#0f172a'),
        statCard('Bütçe Toplam', '₺'+fmt(s.total_budget), '#0ea5e9'),
        statCard('Harcanan', '₺'+fmt(s.total_spent), '#f59e0b', 'kullanım %'+Math.round(s.total_spent/Math.max(s.total_budget,1)*100)),
        statCard('Ort. İlerleme', s.avg_progress+'%', '#10b981'),
      ].join('');
      drawBubble(j.bubbles);
      document.getElementById('tbl').innerHTML = j.bubbles.map(b => `
        <tr style="border-bottom:1px solid #f1f5f9;">
          <td style="padding:8px;color:#0f172a;font-weight:600;">${esc(b.code)}</td>
          <td style="padding:8px;color:#475569;">${esc(b.name)}</td>
          <td style="padding:8px;color:#475569;">${esc(b.status)}</td>
          <td style="padding:8px;"><span style="background:${b.color};color:#fff;padding:2px 8px;border-radius:6px;font-size:10.5px;font-weight:700;">${esc(b.priority)}</span></td>
          <td style="padding:8px;text-align:right;color:#475569;">₺${fmt(b.budget_total)}</td>
          <td style="padding:8px;text-align:right;color:#475569;">₺${fmt(b.budget_spent)}</td>
          <td style="padding:8px;text-align:right;color:#475569;">%${b.budget_usage_pct}</td>
          <td style="padding:8px;text-align:right;color:#10b981;font-weight:600;">%${b.progress_pct}</td>
          <td style="padding:8px;text-align:right;color:#64748b;">${b.start_year}-${b.end_year}</td>
        </tr>`).join('');
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err = document.getElementById('error'); err.style.display='block'; err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
