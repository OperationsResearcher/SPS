(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const statCard = (l,v,c) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;">
    <div style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div>
    <div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div></div>`;

  async function load(){
    try {
      const j = await (await fetch('/raporlar/api/hedef-revizyon',{credentials:'same-origin'})).json();
      if (!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const s = j.summary;
      document.getElementById('summary').innerHTML = [
        statCard('Toplam Yıl', s.total_years, '#0f172a'),
        statCard('Revize Olmuş Yıl', s.years_with_revisions, '#16a34a'),
        statCard('Toplam Revizyon', s.total_revisions, '#f59e0b'),
      ].join('');

      // Yıl bar chart
      const maxRev = Math.max(...j.by_year.map(y => y.revised_count), 1);
      document.getElementById('year-bars').innerHTML = j.by_year.map(y => `
        <div style="display:flex;align-items:center;gap:10px;padding:5px 0;font-size:12.5px;">
          <div style="width:80px;font-weight:600;color:#0f172a;">${y.year}</div>
          <div style="width:80px;font-size:11px;color:#64748b;">${esc(y.status)}</div>
          <div style="flex:1;background:#f1f5f9;border-radius:4px;height:18px;overflow:hidden;">
            <div style="background:#16a34a;height:100%;width:${y.revised_count/maxRev*100}%;"></div>
          </div>
          <div style="width:80px;text-align:right;color:#475569;font-weight:600;">${y.revised_count} revize</div>
        </div>`).join('');

      // KPI listesi
      const list = j.revised_kpis;
      if (!list.length) {
        document.getElementById('kpi-list').innerHTML = '<div style="color:#94a3b8;font-style:italic;font-size:13px;padding:8px;">Hiç PG revize edilmemiş — hedefler yıldan yıla aynı kalmış.</div>';
      } else {
        document.getElementById('kpi-list').innerHTML = '<div style="display:grid;gap:8px;">'+list.map(k => `
          <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;border:1px solid #e2e8f0;border-radius:6px;background:#f8fafc;font-size:12.5px;flex-wrap:wrap;gap:6px;">
            <div style="min-width:0;flex:1;">
              <div style="font-weight:600;color:#0f172a;">${k.year} — ${esc(k.kpi_code)} · ${esc(k.kpi_name)}</div>
              <div style="font-size:11px;color:#64748b;margin-top:2px;">
                Değişen: ${k.diff_fields.map(d => `<span style="background:#dcfce7;color:#166534;padding:1px 6px;border-radius:6px;font-weight:600;margin-right:3px;">${esc(d)}</span>`).join(' ')}
              </div>
            </div>
            <div style="display:flex;align-items:center;gap:6px;font-size:11.5px;color:#475569;">
              <span style="color:#94a3b8;">${esc(k.base_target || '')}</span>
              <span>→</span>
              <span style="font-weight:700;color:#16a34a;">${esc(k.year_target || '')}</span>
            </div>
          </div>`).join('')+'</div>';
      }
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err = document.getElementById('error'); err.style.display='block'; err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
