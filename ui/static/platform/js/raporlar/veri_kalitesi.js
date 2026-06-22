(function(){
  const esc = s => String(s == null ? "" : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

  function statCard(label, value, color, sub, code) {
    return `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:18px 16px;"${code?` data-card-code="${code}"`:''}>
      <div class="mc-stat-label" style="font-size:11px;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">${esc(label)}</div>
      <div style="font-size:26px;font-weight:700;color:${color};line-height:1.1;">${esc(value)}</div>
      ${sub ? `<div style="font-size:11px;color:#94a3b8;margin-top:4px;">${esc(sub)}</div>` : ''}
    </div>`;
  }

  function renderKpiList(items, container) {
    if (!items.length) {
      container.innerHTML = '<div style="font-size:13px;color:#94a3b8;font-style:italic;padding:8px;">Sorunlu PG yok.</div>';
      return;
    }
    container.innerHTML = '<div style="display:grid;gap:8px;">' + items.map(k => `
      <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;border:1px solid #e2e8f0;border-radius:6px;background:#f8fafc;font-size:12.5px;">
        <div style="min-width:0;flex:1;">
          <a href="/process/${k.process_id}/karne#kpi-${k.id}" style="font-weight:600;color:#0ea5e9;text-decoration:none;">${esc(k.code)} · ${esc(k.name)}</a>
          <div style="font-size:11px;color:#64748b;margin-top:2px;"><a href="/process/${k.process_id}/karne" style="color:#64748b;text-decoration:none;">${esc(k.process_name)}</a>${k.last_data_date ? ` · son: ${esc(k.last_data_date)}` : ''}</div>
        </div>
        <div style="display:flex;gap:4px;flex-wrap:wrap;max-width:50%;justify-content:flex-end;">
          ${k.issues.map(i => `<span style="background:#fee2e2;color:#991b1b;font-size:10.5px;padding:2px 7px;border-radius:8px;font-weight:600;">${esc(i)}</span>`).join('')}
        </div>
      </div>
    `).join('') + '</div>';
  }

  function renderProcessBars(items, container) {
    if (!items.length) { container.innerHTML = '<div style="color:#94a3b8;font-style:italic;">Süreç yok.</div>'; return; }
    container.innerHTML = '<div style="display:grid;gap:6px;">' + items.map(p => {
      const rate = p.fill_rate;
      const color = rate >= 80 ? '#10b981' : rate >= 50 ? '#f59e0b' : '#dc2626';
      return `
        <div style="display:flex;align-items:center;gap:12px;padding:6px 0;font-size:12.5px;">
          <a href="/process/${p.process_id}/karne" style="width:200px;flex-shrink:0;color:#0ea5e9;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-decoration:none;" title="${esc(p.name)}">${esc(p.name)}</a>
          <div style="flex:1;background:#f1f5f9;border-radius:4px;height:18px;position:relative;overflow:hidden;">
            <div style="background:${color};height:100%;width:${rate}%;transition:width .3s;"></div>
          </div>
          <div style="width:90px;text-align:right;color:#0f172a;font-weight:600;font-size:12px;">${p.filled}/${p.total} (%${rate})</div>
        </div>`;
    }).join('') + '</div>';
  }

  async function load() {
    try {
      const sel = document.getElementById('year-select');
      const yr = sel ? sel.value : '';
      const url = '/raporlar/api/veri-kalitesi' + (yr ? ('?year=' + encodeURIComponent(yr)) : '');
      document.getElementById('loading').style.display = 'block';
      document.getElementById('content').style.display = 'none';
      document.getElementById('error').style.display = 'none';
      const res = await fetch(url, {credentials:'same-origin'});
      const j = await res.json();
      if (!j.success) throw new Error(j.message || 'Veri alınamadı');

      document.getElementById('loading').style.display = 'none';
      document.getElementById('content').style.display = 'block';

      const s = j.summary;
      const scoreColor = s.score >= 75 ? '#10b981' : s.score >= 50 ? '#f59e0b' : '#dc2626';
      document.getElementById('summary-cards').innerHTML = [
        statCard('Genel Skor', '%' + s.score, scoreColor, s.plan_year ? `Plan yılı: ${s.plan_year}` : '', 'raporlar_veri_kalitesi.genel_skor'),
        statCard('Toplam PG', s.total_kpi, '#0f172a', '', 'raporlar_veri_kalitesi.toplam_pg'),
        statCard('Kritik', s.kritik_count, '#dc2626', 'acil ilgilenilmesi gerekli', 'raporlar_veri_kalitesi.kritik'),
        statCard('Orta Risk', s.orta_count, '#f59e0b', 'eksik alanlar var', 'raporlar_veri_kalitesi.orta_risk'),
        statCard('Sağlıklı', s.iyi_count, '#10b981', 'tam tanımlı', 'raporlar_veri_kalitesi.saglikli'),
      ].join('');

      renderKpiList(j.categories.kritik, document.getElementById('kritik-list'));
      renderKpiList(j.categories.orta, document.getElementById('orta-list'));
      renderProcessBars(j.by_process, document.getElementById('process-bars'));
    } catch (e) {
      document.getElementById('loading').style.display = 'none';
      const err = document.getElementById('error');
      err.style.display = 'block';
      err.textContent = 'Hata: ' + e.message;
    }
  }
  const _sel = document.getElementById('year-select');
  if (_sel) _sel.addEventListener('change', load);

  const _titles = {
    'Kritik PG\'ler': 'Hiç ölçüm girilmemiş veya 3+ eksik alanı (hedef, birim, başarı aralığı, ölçüm) olan PG\'ler. Acil müdahale gerektirir — veri olmadan bu PG puanlanamaz.',
    'Orta Risk PG\'ler': '1-2 eksik alanı olan PG\'ler (örn. son ölçüm 180 günden eski, hedef tanımsız, birim eksik). Puanlanabilir ama veri kalitesi düşük; eksikler giderilmeli.',
    'Süreç Bazlı Doluluk': 'Her sürecin PG\'lerinden kaçına ölçüm girildiğinin oranı (dolu/toplam). %80+ yeşil (sağlıklı), %50-80 sarı (orta), %50 altı kırmızı (zayıf). Düşük oranlı süreçler veri girişi için öncelikli.'
  };
  document.querySelectorAll('.vk-info').forEach(el => {
    el.addEventListener('click', (e) => {
      e.stopPropagation();
      const h3 = el.closest('h3');
      const title = h3 ? h3.textContent.replace(/\s*i\s*$/, '').trim() : 'Bilgi';
      const body = el.getAttribute('title') || _titles[title] || '';
      if (window.Swal) {
        Swal.fire({title: title, text: body, icon: 'info', confirmButtonText: 'Tamam', confirmButtonColor:'#0369a1'});
      } else {
        alert(title + '\n\n' + body);
      }
    });
  });
  load();
})();
