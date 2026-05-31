(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const fmt = n => new Intl.NumberFormat('tr-TR').format(Math.round(n));
  const tooltip = document.getElementById('ib-tooltip');

  const STATUS_TR = {
    planned:'Planlandı', in_progress:'Devam Ediyor', on_hold:'Beklemede',
    completed:'Tamamlandı', cancelled:'İptal', delayed:'Gecikmiş', active:'Aktif'
  };
  const PRIORITY_TR = {
    critical:'Kritik', high:'Yüksek', medium:'Orta', low:'Düşük',
    Critical:'Kritik', High:'Yüksek', Medium:'Orta', Low:'Düşük'
  };
  const trStatus = s => STATUS_TR[s] || s || '—';
  const trPriority = p => PRIORITY_TR[p] || p || '—';

  const statCard = (l,v,c,sub) => `<div class="mc-card" style="padding:12px 14px;">
    <div style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;">${esc(l)}</div>
    <div style="font-size:22px;font-weight:800;color:${c};margin-top:3px;">${esc(v)}</div>
    ${sub ? `<div style="font-size:11px;color:#94a3b8;margin-top:2px;">${esc(sub)}</div>` : ''}
  </div>`;

  function showTooltip(html, e) {
    tooltip.innerHTML = html;
    tooltip.style.display = 'block';
    let x = e.clientX + 14, y = e.clientY + 14;
    const r = tooltip.getBoundingClientRect();
    if (x + r.width > window.innerWidth - 10) x = e.clientX - r.width - 14;
    if (y + r.height > window.innerHeight - 10) y = e.clientY - r.height - 14;
    tooltip.style.left = x + 'px'; tooltip.style.top = y + 'px';
  }
  function hideTooltip() { tooltip.style.display = 'none'; }

  function drawBubble(bubbles){
    const svg = document.getElementById('bubble');
    svg.innerHTML = '';
    const w = svg.clientWidth || 1100, h = 500;
    svg.setAttribute('viewBox', `0 0 ${w} ${h}`);
    const padL=58, padR=30, padT=30, padB=44;

    // Eksen çizgileri + başlıklar
    const axes = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    axes.innerHTML = `
      <line x1="${padL}" y1="${h-padB}" x2="${w-padR}" y2="${h-padB}" stroke="#cbd5e1" stroke-width="1"/>
      <line x1="${padL}" y1="${padT}" x2="${padL}" y2="${h-padB}" stroke="#cbd5e1" stroke-width="1"/>
      <text x="${padL+8}" y="${padT-8}" font-size="11" font-weight="600" fill="#475569">↑ Bütçe Kullanımı %</text>
      <text x="${w-padR}" y="${h-padB+30}" font-size="11" font-weight="600" fill="#475569" text-anchor="end">İlerleme % →</text>
    `;
    svg.appendChild(axes);

    // Izgara çizgileri + 4 kadran arka planı
    const grid = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    // Sol-üst (riskli) ve sağ-alt (ideal) gölgelendirme
    const midX = padL + (w-padL-padR) * 0.5;
    const midY = padT + (h-padT-padB) * 0.5;
    grid.innerHTML += `
      <rect x="${padL}" y="${padT}" width="${midX-padL}" height="${midY-padT}" fill="#fee2e2" opacity="0.25"/>
      <rect x="${midX}" y="${midY}" width="${w-padR-midX}" height="${h-padB-midY}" fill="#dcfce7" opacity="0.30"/>
      <text x="${padL+10}" y="${padT+18}" font-size="10" fill="#991b1b" opacity="0.7">⚠ Riskli</text>
      <text x="${w-padR-10}" y="${h-padB-8}" font-size="10" fill="#166534" opacity="0.7" text-anchor="end">✓ İdeal</text>
    `;
    for (let p of [0,25,50,75,100]) {
      const y = padT + (h-padT-padB) * (1 - p/100);
      grid.innerHTML += `<line x1="${padL}" y1="${y}" x2="${w-padR}" y2="${y}" stroke="#f1f5f9" stroke-width="1"/>
        <text x="${padL-6}" y="${y+3}" font-size="9" fill="#94a3b8" text-anchor="end">${p}</text>`;
      const x = padL + (w-padL-padR) * (p/100);
      grid.innerHTML += `<text x="${x}" y="${h-padB+14}" font-size="9" fill="#94a3b8" text-anchor="middle">${p}</text>`;
    }
    svg.appendChild(grid);

    // Baloncuklar
    const maxBudget = Math.max(...bubbles.map(b => b.budget_total), 1);
    bubbles.forEach(b => {
      const x = padL + (w-padL-padR) * (Math.min(100, b.progress_pct)/100);
      const y = padT + (h-padT-padB) * (1 - Math.min(b.budget_usage_pct,100)/100);
      const r = Math.max(10, Math.min(46, 10 + Math.sqrt(b.budget_total / maxBudget) * 36));
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.style.cursor = 'pointer';
      g.innerHTML = `
        <circle cx="${x}" cy="${y}" r="${r}" fill="${b.color}" opacity="${b.opacity || 0.7}" stroke="#fff" stroke-width="2"/>
        <text x="${x}" y="${y+r+12}" font-size="9.5" fill="#475569" text-anchor="middle" font-weight="600">${esc(b.code || '')}</text>`;
      svg.appendChild(g);
      g.addEventListener('mouseenter', (e) => {
        showTooltip(`
          <b>${esc(b.code || '')} · ${esc(b.name)}</b><br>
          Durum: <b>${esc(trStatus(b.status))}</b> · Öncelik: <b style="color:${b.color}">${esc(trPriority(b.priority))}</b><br>
          Toplam bütçe: <b>₺${fmt(b.budget_total)}</b><br>
          Harcanan: <b>₺${fmt(b.budget_spent)}</b> (%${b.budget_usage_pct})<br>
          İlerleme: <b>%${b.progress_pct}</b><br>
          Süre: ${b.start_year}-${b.end_year}
        `, e);
      });
      g.addEventListener('mousemove', (e) => { tooltip.style.left = (e.clientX+14)+'px'; tooltip.style.top = (e.clientY+14)+'px'; });
      g.addEventListener('mouseleave', hideTooltip);
      g.addEventListener('click', () => { window.location.href = '/sp/initiatives'; });
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
        statCard('Toplam Girişim',    s.total, '#0f172a'),
        statCard('Toplam Bütçe',      '₺'+fmt(s.total_budget), '#0ea5e9'),
        statCard('Harcanan Bütçe',    '₺'+fmt(s.total_spent),  '#f59e0b', 'kullanım %'+Math.round(s.total_spent/Math.max(s.total_budget,1)*100)),
        statCard('Ortalama İlerleme', s.avg_progress+'%',       '#10b981'),
      ].join('');
      drawBubble(j.bubbles || []);
      document.getElementById('tbl').innerHTML = (j.bubbles || []).map(b => `
        <tr style="border-bottom:1px solid #f1f5f9;">
          <td style="padding:8px; color:#0f172a; font-weight:600; font-family:monospace;">${esc(b.code || '—')}</td>
          <td style="padding:8px; color:#1e293b;">${esc(b.name)}</td>
          <td style="padding:8px; color:#475569;">${esc(trStatus(b.status))}</td>
          <td style="padding:8px;"><span style="background:${b.color}; color:#fff; padding:2px 8px; border-radius:6px; font-size:10.5px; font-weight:700;">${esc(trPriority(b.priority))}</span></td>
          <td style="padding:8px; text-align:right; color:#475569;">₺${fmt(b.budget_total)}</td>
          <td style="padding:8px; text-align:right; color:#475569;">₺${fmt(b.budget_spent)}</td>
          <td style="padding:8px; text-align:right; color:${b.budget_usage_pct > 100 ? '#dc2626' : '#475569'}; font-weight:${b.budget_usage_pct > 100 ? '700' : '400'};">%${b.budget_usage_pct}</td>
          <td style="padding:8px; text-align:right; color:#10b981; font-weight:600;">%${b.progress_pct}</td>
          <td style="padding:8px; text-align:right; color:#64748b;">${b.start_year}-${b.end_year}</td>
        </tr>`).join('');
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err = document.getElementById('error'); err.style.display='block'; err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
