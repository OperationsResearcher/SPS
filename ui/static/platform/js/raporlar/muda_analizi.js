(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const yearSel = document.getElementById('muda-year-select');
  const stat = (l,v,c,sub,code) => `<div class="mc-card" style="padding:12px 14px;"${code?` data-card-code="${code}"`:''}>
    <div class="mc-stat-label" style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;">${esc(l)}</div>
    <div style="font-size:22px;font-weight:800;color:${c};margin-top:3px;">${esc(v)}</div>
    ${sub ? `<div style="font-size:11px;color:#94a3b8;margin-top:2px;">${esc(sub)}</div>` : ''}
  </div>`;

  async function load(){
    try {
      document.getElementById('loading').style.display='';
      document.getElementById('content').style.display='none';
      const y = yearSel?.value || '';
      const url = '/raporlar/api/muda-analizi' + (y ? '?year=' + encodeURIComponent(y) : '');
      const j = await (await fetch(url,{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const s = j.summary;
      document.getElementById('summary').innerHTML = [
        stat('Analiz Edilen Süreç', s.total_processes_analyzed, '#0f172a', s.plan_year ? `${s.plan_year} yılı` : '', 'raporlar_muda_analizi.analiz_edilen_surec'),
        stat('Bulgu Olan Süreç', s.processes_with_findings, '#f59e0b', s.total_processes_analyzed ? `%${Math.round(s.processes_with_findings/s.total_processes_analyzed*100)} kapsama` : '', 'raporlar_muda_analizi.bulgu_olan_surec'),
        stat('Toplam Bulgu', s.total_findings, '#dc2626', '', 'raporlar_muda_analizi.toplam_bulgu'),
      ].join('');

      const max = Math.max(...j.by_muda.map(m=>m.count), 1);
      document.getElementById('by-muda').innerHTML = j.by_muda.map(m => {
        const pct = m.count > 0 ? Math.round(m.count/max*100) : 0;
        return `
          <div style="padding:12px 14px; background:#fafbfc; border:1px solid #e2e8f0; border-left:4px solid ${m.color}; border-radius:8px;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
              <span style="font-size:14px; font-weight:700; color:#0f172a;">${esc(m.label)}</span>
              <span style="margin-left:auto; background:${m.color}; color:#fff; padding:2px 9px; border-radius:10px; font-size:11.5px; font-weight:700;">${m.count} bulgu</span>
            </div>
            <div style="font-size:12.5px; color:#475569; line-height:1.5; margin-bottom:4px;">${esc(m.desc || '')}</div>
            ${m.ex ? `<div style="font-size:11.5px; color:#94a3b8;"><b style="color:#64748b;">Örnek:</b> ${esc(m.ex)}</div>` : ''}
            ${m.count > 0 ? `<div style="height:5px; background:#f1f5f9; border-radius:3px; overflow:hidden; margin-top:8px;"><div style="height:100%; width:${pct}%; background:${m.color};"></div></div>` : ''}
          </div>`;
      }).join('');

      document.getElementById('by-process').innerHTML = j.by_process.length === 0
        ? `<div style="text-align:center; padding:24px; color:#94a3b8;">
             <i class="fas fa-check-circle" style="color:#10b981; font-size:28px;"></i>
             <div style="margin-top:8px;">Bulgu olan süreç yok — Lean göstergeleriniz iyi durumda.</div>
           </div>`
        : '<div style="display:grid; gap:8px;">' + j.by_process.slice(0,15).map(p => `
          <div style="padding:12px 14px; border:1px solid #e2e8f0; border-radius:6px; background:#fafbfc;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
              <a href="/process/${p.process_id}/karne" style="font-weight:600; color:#0f172a; text-decoration:none;">
                <span style="background:#eef2ff; color:#4338ca; padding:1px 7px; border-radius:4px; font-family:monospace; font-size:11px; margin-right:6px;">${esc(p.code||'')}</span>
                ${esc(p.name)}
              </a>
              <span style="background:#fef3c7; color:#92400e; padding:2px 9px; border-radius:10px; font-size:11.5px; font-weight:700;">${p.findings_count} bulgu</span>
            </div>
            ${(p.findings||[]).slice(0,3).map(f=>`<div style="font-size:11.5px; color:#64748b; margin-left:8px; margin-top:3px;">• ${esc(f.message||f.description||JSON.stringify(f).substring(0,80))}</div>`).join('')}
          </div>`).join('') + '</div>';
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err = document.getElementById('error'); err.style.display='block'; err.textContent='Hata: '+e.message;
    }
  }

  yearSel?.addEventListener('change', async () => {
    const newYear = parseInt(yearSel.value, 10);
    if (!newYear) return;
    try {
      const csrf = document.querySelector('meta[name="csrf-token"]')?.content || '';
      await fetch(window.KK.api.planYearsSetActive, {
        method:'POST', credentials:'same-origin',
        headers:{'Content-Type':'application/json','X-CSRFToken':csrf},
        body: JSON.stringify({year: newYear})
      });
    } catch(_) {}
    load();
  });
  load();
})();
