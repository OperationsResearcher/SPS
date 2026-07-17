/* CMMI Olgunluk Isı Haritası — yıl seçici + detaylı açıklamalar + tıklanabilir grid */
(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const yearSel = document.getElementById('cmmi-year-select');

  function statCard(label, value, color, sub, code) {
    return `<div class="mc-card" style="padding:12px 14px;"${code ? ` data-card-code="${code}"` : ''}>
      <div class="mc-stat-label" style="font-size:10.5px; color:#64748b; font-weight:600; text-transform:uppercase;">${esc(label)}</div>
      <div style="font-size:24px; font-weight:800; color:${color}; margin-top:3px;">${esc(value)}</div>
      ${sub ? `<div style="font-size:11px; color:#94a3b8; margin-top:2px;">${esc(sub)}</div>` : ''}
    </div>`;
  }

  function renderOverall(s) {
    const el = document.getElementById('cmmi-overall');
    el.style.borderLeftColor = s.overall_color;
    el.innerHTML = `
      <div style="display:flex; align-items:center; gap:18px; flex-wrap:wrap;">
        <div style="flex-shrink:0;">
          <div style="font-size:11px; color:#64748b; text-transform:uppercase; font-weight:600;">Ortalama Olgunluk</div>
          <div style="font-size:42px; font-weight:800; color:${s.overall_color}; line-height:1;">${s.avg_level}</div>
          <div style="font-size:11px; color:#94a3b8;">/ 5.0</div>
        </div>
        <div style="flex:1; min-width:240px;">
          <div style="font-size:15px; font-weight:700; color:${s.overall_color}; margin-bottom:4px;">${esc(s.overall_label)}</div>
          <div style="font-size:13px; color:#475569; line-height:1.55;">${esc(s.overall_advice)}</div>
        </div>
      </div>`;
  }

  function renderDistribution(dist) {
    const html = dist.map(d => `
        <div style="display:flex; gap:12px; align-items:center; padding:10px 12px; background:#fafbfc; border:1px solid #e2e8f0; border-radius:8px;">
          <div style="width:36px; height:36px; border-radius:8px; background:${d.color}; display:flex; align-items:center; justify-content:center; color:#fff; font-weight:800; font-size:16px; flex-shrink:0;">${d.level}</div>
          <div style="flex:1; min-width:0;">
            <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
              <span style="font-size:13.5px; font-weight:700; color:#0f172a;">${esc(d.label)}</span>
              <span style="font-size:11px; color:#94a3b8;">(${esc(d.en)})</span>
              <span style="margin-left:auto; font-size:12.5px; font-weight:700; color:${d.color};">${d.count} süreç · %${d.pct}</span>
            </div>
            <div style="font-size:12px; color:#64748b; margin:4px 0 6px; line-height:1.5;">${esc(d.desc)}</div>
            <div style="height:6px; background:#f1f5f9; border-radius:3px; overflow:hidden;">
              <div style="height:100%; width:${d.pct}%; background:${d.color};"></div>
            </div>
          </div>
        </div>`).join('');
    document.getElementById('cmmi-dist').innerHTML = html;
  }

  function renderGrid(procs, dist) {
    const colorMap = {}, labelMap = {};
    dist.forEach(d => { colorMap[d.level] = d.color; labelMap[d.level] = d.label; });
    if (!procs.length) {
      document.getElementById('cmmi-grid').innerHTML = '<div style="grid-column:1/-1; padding:20px; text-align:center; color:#94a3b8;">Bu yıl için olgunluk kaydı bulunmuyor.</div>';
      return;
    }
    procs.sort((a, b) => b.level - a.level);
    document.getElementById('cmmi-grid').innerHTML = procs.map(p => `
      <a href="/k-plan/process/${p.id}/karne" style="display:flex; align-items:center; gap:10px; padding:10px 12px; background:#fff; border:1px solid #e2e8f0; border-radius:8px; text-decoration:none; color:#1e293b;">
        <div style="width:32px; height:32px; border-radius:6px; background:${colorMap[p.level]}; color:#fff; font-weight:800; font-size:14px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">${p.level}</div>
        <div style="flex:1; min-width:0;">
          <div style="font-size:12.5px; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${p.code ? `<span style="font-family:monospace; color:#64748b;">${esc(p.code)}</span> ` : ''}${esc(p.name)}</div>
          <div style="font-size:11px; color:${colorMap[p.level]};">${esc(labelMap[p.level])}</div>
        </div>
      </a>`).join('');
  }

  function renderUnmeasured(items) {
    const wrap = document.getElementById('cmmi-unmeasured');
    const list = document.getElementById('cmmi-unmeasured-list');
    if (!items || !items.length) { wrap.style.display = 'none'; return; }
    wrap.style.display = 'block';
    list.innerHTML = items.map(p => `
      <a href="/k-plan/process/${p.id}/karne" style="background:#fff; border:1px solid #fde68a; padding:3px 8px; border-radius:4px; text-decoration:none; color:#92400e;">
        ${p.code ? `<b>${esc(p.code)}</b> · ` : ''}${esc(p.name)}
      </a>`).join('');
  }

  async function load() {
    try {
      document.getElementById('cmmi-loading').style.display = '';
      document.getElementById('cmmi-content').style.display = 'none';
      document.getElementById('cmmi-error').style.display = 'none';
      const y = yearSel?.value || '';
      const url = '/k-report/api/cmmi-heatmap' + (y ? '?year=' + encodeURIComponent(y) : '');
      const j = await (await fetch(url, {credentials:'same-origin'})).json();
      if (!j.success) throw new Error(j.message || 'Veri alınamadı');
      document.getElementById('cmmi-loading').style.display = 'none';
      document.getElementById('cmmi-content').style.display = '';
      const s = j.summary;
      document.getElementById('cmmi-summary').innerHTML = [
        statCard('Ölçülen Süreç',       s.total_processes, '#6366f1', `${s.tenant_process_count} toplam`, 'raporlar_cmmi_heatmap.olculen_surec'),
        statCard('Ölçülmemiş',          s.unmeasured_count, s.unmeasured_count > 0 ? '#f59e0b' : '#10b981', 'değerlendirme bekliyor', 'raporlar_cmmi_heatmap.olculmemis'),
        statCard('Ortalama Seviye',     s.avg_level, s.overall_color, '/ 5.0', 'raporlar_cmmi_heatmap.ortalama_seviye'),
        statCard('Optimize Eden (L5)',  s.level_5_count, '#10b981', 'sınıfın en iyisi', 'raporlar_cmmi_heatmap.optimize_eden_l5'),
        statCard('Düşük Seviye (L1-L2)', s.low_level_count, s.low_level_count > 0 ? '#dc2626' : '#10b981', 'aksiyon önceliği', 'raporlar_cmmi_heatmap.dusuk_seviye_l1_l2'),
      ].join('');
      renderOverall(s);
      renderDistribution(j.distribution);
      renderGrid(j.processes, j.distribution);
      renderUnmeasured(j.unmeasured);
    } catch(e) {
      document.getElementById('cmmi-loading').style.display = 'none';
      const err = document.getElementById('cmmi-error');
      err.style.display = 'block';
      err.textContent = 'Hata: ' + e.message;
    }
  }

  yearSel?.addEventListener('change', async () => {
    const newYear = parseInt(yearSel.value, 10);
    if (!newYear) return;
    try {
      const csrf = document.querySelector('meta[name="csrf-token"]')?.content || '';
      await fetch(window.KK.api.planYearsSetActive, {
        method: 'POST', credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
        body: JSON.stringify({ year: newYear })
      });
    } catch(_) {}
    load();
  });

  load();
})();
