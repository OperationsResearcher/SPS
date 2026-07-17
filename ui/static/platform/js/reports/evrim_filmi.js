(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

  let years = [];
  let idx = 0;
  let playing = false;
  let playTimer = null;

  function renderYear(i) {
    if (!years[i]) return;
    const y = years[i];
    document.getElementById('current-year').textContent = y.year + ' (' + y.status + ')';
    document.getElementById('year-slider').value = i;

    const st = y.stats;
    document.getElementById('year-stats').innerHTML = `
      <div><b style="color:#0f172a;">${st.strategy_count}</b> strateji</div>
      <div><b style="color:#0f172a;">${st.sub_count}</b> alt strateji</div>
      <div><b style="color:#0f172a;">${st.process_count}</b> süreç</div>
      <div><b style="color:#0f172a;">${st.kpi_count}</b> PG</div>
      <div><b style="color:#0f172a;">${st.measurement_count.toLocaleString('tr-TR')}</b> ölçüm</div>`;

    // Strateji ağacı renderı
    let html = '<div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:16px;">';
    y.strategies.forEach((s, sIdx) => {
      const colors = ['#4f46e5','#0ea5e9','#10b981','#f59e0b','#ef4444','#8b5cf6','#db2777','#0d9488'];
      const col = colors[sIdx % colors.length];
      html += `
        <div style="border:1px solid #e2e8f0;border-radius:8px;padding:12px;background:#f8fafc;">
          <div style="font-weight:700;color:${col};font-size:13px;margin-bottom:6px;">${esc(s.code)} ${esc(s.title)}</div>
          <div style="display:flex;flex-direction:column;gap:4px;">
            ${s.sub_strategies.map(ss => `
              <div style="font-size:11.5px;color:#475569;padding:4px 8px;background:#fff;border-radius:4px;border-left:3px solid ${col};">
                <div style="font-weight:600;">${esc(ss.code)} ${esc(ss.title)}</div>
                ${ss.process_codes.length ? `<div style="font-size:10.5px;color:#94a3b8;margin-top:2px;">→ ${ss.process_codes.map(esc).join(', ')}</div>` : ''}
              </div>
            `).join('')}
          </div>
        </div>`;
    });
    html += '</div>';
    document.getElementById('year-content').innerHTML = html;

    // Geçiş notu (i > 0 ise önceki yılla farkı göster)
    if (i > 0) {
      const prev = years[i - 1];
      const delta = {
        s: y.stats.strategy_count - prev.stats.strategy_count,
        p: y.stats.process_count - prev.stats.process_count,
        k: y.stats.kpi_count - prev.stats.kpi_count,
      };
      const parts = [];
      if (delta.s !== 0) parts.push((delta.s > 0 ? '+' : '') + delta.s + ' strateji');
      if (delta.p !== 0) parts.push((delta.p > 0 ? '+' : '') + delta.p + ' süreç');
      if (delta.k !== 0) parts.push((delta.k > 0 ? '+' : '') + delta.k + ' PG');
      if (parts.length) {
        const strip = document.getElementById('diff-strip');
        strip.textContent = `${prev.year} → ${y.year} : ${parts.join(', ')}`;
        strip.style.display = 'block';
        clearTimeout(strip._t);
        strip._t = setTimeout(() => strip.style.display = 'none', 2200);
      }
    }
  }

  function tick() {
    idx = (idx + 1) % years.length;
    renderYear(idx);
    if (idx === years.length - 1) {
      // Sona geldik — durdur
      stopPlay();
    }
  }

  function startPlay() {
    if (playing) return;
    playing = true;
    document.getElementById('play-btn').innerHTML = '<i class="fas fa-pause"></i> Durdur';
    if (idx === years.length - 1) idx = 0;  // başa sar
    playTimer = setInterval(tick, 1500);
  }

  function stopPlay() {
    playing = false;
    document.getElementById('play-btn').innerHTML = '<i class="fas fa-play"></i> Oynat';
    if (playTimer) clearInterval(playTimer);
    playTimer = null;
  }

  async function load() {
    try {
      const j = await (await fetch('/k-report/api/evolution-film', {credentials:'same-origin'})).json();
      if (!j.success) throw new Error(j.message);
      years = j.years;
      if (!years.length) {
        document.getElementById('loading').style.display='none';
        document.getElementById('error').style.display='block';
        document.getElementById('error').textContent = 'Henüz plan yılı yok. Önce SP → Dönemler ekranından plan yılı oluşturun.';
        return;
      }
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const slider = document.getElementById('year-slider');
      slider.max = years.length - 1;
      slider.value = 0;
      document.getElementById('year-min').textContent = years[0].year;
      document.getElementById('year-max').textContent = years[years.length - 1].year;
      slider.addEventListener('input', e => { idx = parseInt(e.target.value); renderYear(idx); stopPlay(); });
      document.getElementById('play-btn').addEventListener('click', () => playing ? stopPlay() : startPlay());
      renderYear(0);
    } catch(e) {
      document.getElementById('loading').style.display='none';
      const err = document.getElementById('error');
      err.style.display='block';
      err.textContent = 'Hata: ' + e.message;
    }
  }
  load();
})();
