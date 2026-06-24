(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const statCard = (l,v,c,sub,code) => `<div class="mc-card" style="padding:12px 14px;"${code?` data-card-code="${code}"`:''}>
    <div class="mc-stat-label" style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;">${esc(l)}</div>
    <div style="font-size:22px;font-weight:800;color:${c};margin-top:3px;">${esc(v)}</div>
    ${sub ? `<div style="font-size:11px;color:#94a3b8;margin-top:2px;">${esc(sub)}</div>` : ''}
  </div>`;

  // Plan yıl durumu için Türkçe karşılıklar
  const STATUS_TR = {
    'active':    { label: 'Aktif',     color: '#10b981', bg: '#dcfce7' },
    'closed':    { label: 'Kapalı',    color: '#64748b', bg: '#f1f5f9' },
    'draft':     { label: 'Taslak',    color: '#f59e0b', bg: '#fef3c7' },
    'archived':  { label: 'Arşiv',     color: '#94a3b8', bg: '#f8fafc' },
    'planned':   { label: 'Planlandı', color: '#0ea5e9', bg: '#e0f2fe' },
  };
  const statusBadge = (s) => {
    const t = STATUS_TR[s] || { label: s || '—', color: '#64748b', bg: '#f1f5f9' };
    return `<span style="background:${t.bg}; color:${t.color}; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:600;">${esc(t.label)}</span>`;
  };

  // Değişen alanlar için anlamlı Türkçe etiket
  const DIFF_TR = {
    'hedef':   { label: 'Hedef değeri',   color: '#16a34a', bg: '#dcfce7' },
    'ağırlık': { label: 'PG ağırlığı',    color: '#8b5cf6', bg: '#ede9fe' },
    'periyot': { label: 'Ölçüm periyodu', color: '#0ea5e9', bg: '#dbeafe' },
  };
  const diffChip = (d) => {
    const t = DIFF_TR[d] || { label: d, color: '#64748b', bg: '#f1f5f9' };
    return `<span style="background:${t.bg}; color:${t.color}; padding:2px 8px; border-radius:6px; font-weight:600; margin-right:3px; font-size:11px;">${esc(t.label)}</span>`;
  };

  async function load(){
    try {
      const j = await (await fetch('/reports/api/target-revision',{credentials:'same-origin'})).json();
      if (!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const s = j.summary;
      document.getElementById('summary').innerHTML = [
        statCard('Toplam Plan Dönemi', s.total_years, '#0f172a', 'kayıtlı tüm yıllar', 'raporlar_hedef_revizyon.toplam_plan_donemi'),
        statCard('Revizyon Yapılan Yıl', s.years_with_revisions, '#16a34a', 'en az 1 PG değişti', 'raporlar_hedef_revizyon.revizyon_yapilan_yil'),
        statCard('Toplam Revizyon',    s.total_revisions, '#f59e0b', 'hedef · ağırlık · periyot', 'raporlar_hedef_revizyon.toplam_revizyon'),
      ].join('');

      // Yıl çubukları — durumla birlikte
      const maxRev = Math.max(...j.by_year.map(y => y.revised_count), 1);
      // En yeni yıl üstte
      const yearsSorted = j.by_year.slice().sort((a,b) => b.year - a.year);
      document.getElementById('year-bars').innerHTML = yearsSorted.map(y => `
        <div style="display:flex; align-items:center; gap:10px; padding:7px 0; font-size:12.5px; border-bottom:1px solid #f1f5f9;">
          <div style="width:54px; font-weight:700; color:#0f172a;">${y.year}</div>
          <div style="width:90px;">${statusBadge(y.status)}</div>
          <div style="flex:1; background:#f1f5f9; border-radius:4px; height:18px; overflow:hidden; min-width:120px;">
            <div style="background:${y.revised_count > 0 ? '#16a34a' : '#cbd5e1'}; height:100%; width:${y.revised_count/maxRev*100}%; transition:width 0.3s;"></div>
          </div>
          <div style="width:120px; text-align:right; color:#475569; font-weight:600;">
            ${y.revised_count > 0 ? `<span style="color:#16a34a;">${y.revised_count}</span> revizyon` : '<span style="color:#94a3b8;">değişiklik yok</span>'}
          </div>
        </div>`).join('');

      // PG listesi
      const list = j.revised_kpis || [];
      if (!list.length) {
        document.getElementById('kpi-list').innerHTML = '<div style="text-align:center; padding:24px; color:#94a3b8;"><i class="fas fa-check-circle" style="color:#10b981; font-size:28px;"></i><div style="margin-top:8px;">Hiç PG revize edilmemiş — hedefler yıldan yıla aynı kalmış.</div></div>';
      } else {
        // En yeniden eskiye
        list.sort((a,b) => b.year - a.year);
        document.getElementById('kpi-list').innerHTML =
          '<div style="display:grid; gap:8px;">' +
          list.map(k => `
            <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 12px; border:1px solid #e2e8f0; border-radius:6px; background:#fafbfc; font-size:12.5px; flex-wrap:wrap; gap:8px;">
              <div style="min-width:0; flex:1;">
                <div style="font-weight:600; color:#0f172a;">
                  <span style="background:#eef2ff; color:#4338ca; padding:1px 7px; border-radius:4px; font-size:11px; margin-right:6px;">${k.year}</span>
                  <span style="font-family:monospace; color:#64748b;">${esc(k.kpi_code)}</span> · ${esc(k.kpi_name)}
                </div>
                <div style="font-size:11.5px; color:#64748b; margin-top:4px;">
                  Revize edilen alanlar: ${k.diff_fields.map(diffChip).join(' ')}
                </div>
              </div>
              <div style="display:flex; align-items:center; gap:8px; font-size:11.5px; color:#475569;">
                <span style="color:#94a3b8;" title="Süreçteki temel hedef">Esas: <b>${esc(k.base_target || '—')}</b></span>
                <span style="color:#cbd5e1;">→</span>
                <span style="color:#16a34a;" title="Bu yıl için override edilen hedef">${k.year} yılı: <b>${esc(k.year_target || '—')}</b></span>
              </div>
            </div>`).join('') +
          '</div>';
      }
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err = document.getElementById('error'); err.style.display='block'; err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
