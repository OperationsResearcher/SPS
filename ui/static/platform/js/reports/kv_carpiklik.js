(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

  function statCard(label, value, color, sub) {
    return `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:18px 16px;">
      <div style="font-size:11px;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">${esc(label)}</div>
      <div style="font-size:26px;font-weight:700;color:${color};line-height:1.1;">${esc(value)}</div>
      ${sub ? `<div style="font-size:11px;color:#94a3b8;margin-top:4px;">${esc(sub)}</div>` : ''}
    </div>`;
  }

  function renderBars(rows) {
    // her satır için 2 çubuk yan yana
    const html = rows.map(r => {
      const w = r.weight_pct || 0;
      const s = r.avg_score == null ? 0 : r.avg_score;
      return `
        <div style="margin-bottom:14px;">
          <div style="font-size:12.5px;font-weight:600;color:#0f172a;margin-bottom:4px;">
            ${esc(r.code)} · ${esc(r.title)}
            <span style="float:right;font-weight:400;color:#64748b;font-size:11.5px;">${esc(r.skew_label)}</span>
          </div>
          <div style="display:grid;gap:3px;">
            <div style="display:flex;align-items:center;gap:8px;">
              <div style="width:64px;font-size:11px;color:#64748b;">Ağırlık</div>
              <div style="flex:1;background:#f1f5f9;border-radius:4px;height:14px;overflow:hidden;">
                <div style="background:#8b5cf6;height:100%;width:${w}%;"></div>
              </div>
              <div style="width:50px;text-align:right;font-size:11.5px;color:#475569;font-weight:600;">%${w}</div>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
              <div style="width:64px;font-size:11px;color:#64748b;">Skor</div>
              <div style="flex:1;background:#f1f5f9;border-radius:4px;height:14px;overflow:hidden;">
                <div style="background:#10b981;height:100%;width:${s}%;"></div>
              </div>
              <div style="width:50px;text-align:right;font-size:11.5px;color:#475569;font-weight:600;">${r.avg_score == null ? '—' : r.avg_score}</div>
            </div>
          </div>
        </div>`;
    }).join('');
    document.getElementById('bars').innerHTML = html;
  }

  function renderTable(rows) {
    document.getElementById('tbl').innerHTML = rows.map(r => {
      let skewColor = '#64748b';
      let skewSym = '—';
      if (r.skew != null) {
        if (r.skew > 10) { skewColor = '#dc2626'; skewSym = '+' + r.skew; }
        else if (r.skew < -10) { skewColor = '#0ea5e9'; skewSym = r.skew; }
        else { skewColor = '#10b981'; skewSym = (r.skew >= 0 ? '+' : '') + r.skew; }
      }
      return `<tr style="border-bottom:1px solid #f1f5f9;">
        <td style="padding:10px;color:#0f172a;font-weight:600;">${esc(r.code)} · ${esc(r.title)}</td>
        <td style="padding:10px;text-align:right;color:#475569;">%${r.weight_pct}</td>
        <td style="padding:10px;text-align:right;color:#475569;">${r.avg_score == null ? '—' : r.avg_score}</td>
        <td style="padding:10px;text-align:right;color:${skewColor};font-weight:700;">${skewSym}</td>
        <td style="padding:10px;color:${skewColor};font-size:11.5px;">${esc(r.skew_label)}</td>
        <td style="padding:10px;text-align:right;color:#64748b;">${r.related_process_count}</td>
      </tr>`;
    }).join('');
  }

  function currentYear() {
    const sel = document.getElementById('kvc-year-select');
    return sel?.value || '';
  }

  async function load() {
    try {
      const y = currentYear();
      const url = '/k-report/api/k-vector-skewness' + (y ? ('?year=' + encodeURIComponent(y)) : '');
      // İçeriği yükleme moduna al
      document.getElementById('loading').style.display = '';
      document.getElementById('content').style.display = 'none';
      const res = await fetch(url, {credentials:'same-origin'});
      const j = await res.json();
      if (!j.success) throw new Error(j.message || 'Hata');

      document.getElementById('loading').style.display = 'none';
      document.getElementById('content').style.display = 'block';

      const s = j.summary;
      document.getElementById('summary').innerHTML = [
        statCard('Toplam Strateji', s.total_strategies, '#0f172a'),
        statCard('Dengeli', s.balanced, '#10b981', '|çarpıklık| ≤ 10'),
        statCard('Dengesiz', s.unbalanced, '#dc2626', 'ağırlık ≠ performans'),
        statCard(t('Plan Yılı'), s.plan_year || '—', '#0ea5e9'),
      ].join('');

      renderBars(j.strategies);
      renderTable(j.strategies);
    } catch (e) {
      document.getElementById('loading').style.display = 'none';
      const err = document.getElementById('error');
      err.style.display = 'block';
      err.textContent = 'Hata: ' + e.message;
    }
  }
  // Yıl seçici: değişince aktif SP yılını da güncelle ve veriyi yeniden yükle
  document.getElementById('kvc-year-select')?.addEventListener('change', async (e) => {
    const newYear = parseInt(e.target.value, 10);
    if (!newYear) return;
    try {
      const csrf = document.querySelector('meta[name="csrf-token"]')?.content || '';
      await fetch(window.KK.api.planYearsSetActive, {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
        body: JSON.stringify({ year: newYear })
      });
    } catch (_) {}
    load();
  });

  load();
})();
