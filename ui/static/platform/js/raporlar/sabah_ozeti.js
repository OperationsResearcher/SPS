(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const metric = (label, value, color, icon, code) => `
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;display:flex;align-items:center;gap:12px;"${code?` data-card-code="${code}"`:''}>
      <div style="width:38px;height:38px;border-radius:10px;background:${color}22;display:flex;align-items:center;justify-content:center;color:${color};font-size:16px;">
        <i class="fas ${icon}"></i>
      </div>
      <div>
        <div class="mc-stat-label" style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:0.04em;">${esc(label)}</div>
        <div style="font-size:22px;font-weight:700;color:#0f172a;line-height:1.1;">${esc(value)}</div>
      </div>
    </div>`;

  function fmtDt(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    return d.toLocaleString('tr-TR', {dateStyle: 'short', timeStyle: 'short'});
  }

  async function load(){
    try {
      const j = await (await fetch('/k-report/api/morning-summary',{credentials:'same-origin'})).json();
      if (!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const today = new Date(j.today).toLocaleDateString('tr-TR', {weekday:'long', day:'numeric', month:'long', year:'numeric'});
      document.getElementById('today-banner').innerHTML = `
        <div><i class="fas fa-calendar-day" style="margin-right:8px;"></i><b>${today}</b></div>
        <div>Günaydın · ${j.metrics.measurements_today} ölçüm bugün girildi</div>`;
      const m = j.metrics;
      document.getElementById('metrics').innerHTML = [
        metric('Geciken Faaliyet', m.overdue_activities, '#dc2626', 'fa-exclamation-circle', 'raporlar_sabah_ozeti.geciken_faaliyet'),
        metric('Bugün Bitiş', m.today_due_activities, '#f59e0b', 'fa-flag-checkered', 'raporlar_sabah_ozeti.bugun_bitis'),
        metric('Önümüzdeki 7 Gün', m.upcoming_7d_activities, '#0ea5e9', 'fa-calendar-week', 'raporlar_sabah_ozeti.onumuzdeki_7_gun'),
        metric('Son 7 Gün Tamamlanan', m.completed_7d_activities, '#10b981', 'fa-check-circle', 'raporlar_sabah_ozeti.son_7_gun_tamamlanan'),
        metric('Bugün Ölçüm', m.measurements_today, '#8b5cf6', 'fa-chart-line', 'raporlar_sabah_ozeti.bugun_olcum'),
        metric('Son 7 Gün Ölçüm', m.measurements_7d, '#6366f1', 'fa-database', 'raporlar_sabah_ozeti.son_7_gun_olcum'),
      ].join('');

      document.getElementById('recent').innerHTML = (j.recent_entries || []).length === 0
        ? '<div style="color:#94a3b8;font-style:italic;font-size:13px;padding:8px;">Henüz veri girişi yok.</div>'
        : '<div style="display:grid;gap:8px;">'+j.recent_entries.map(r => `
            <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;border:1px solid #e2e8f0;border-radius:6px;background:#f8fafc;font-size:12.5px;gap:10px;flex-wrap:wrap;">
              <div style="min-width:0;flex:1;">
                <div style="font-weight:600;color:#0f172a;">${esc(r.kpi_code||'')} · ${esc(r.kpi_name||'')}</div>
                <div style="font-size:11px;color:#64748b;">Giren: ${esc(r.who)} · ${esc(fmtDt(r.when))}</div>
              </div>
              <div style="font-weight:700;color:#0d9488;font-size:14px;">${esc(r.value)}</div>
            </div>`).join('')+'</div>';
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err = document.getElementById('error'); err.style.display='block'; err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
