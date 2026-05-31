(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  let seçiliSektor = null;

  // ── Veri yükle ────────────────────────────────────────────────────────────
  async function loadData(sektor){
    document.getElementById('loading').style.display = 'block';
    document.getElementById('content').style.display  = 'none';
    try {
      const url = '/raporlar/api/sektor-benchmark' + (sektor ? '?sektor=' + encodeURIComponent(sektor) : '');
      const j = await (await fetch(url, {credentials:'same-origin'})).json();
      if (!j.success) throw new Error(j.message || 'Veri alınamadı');
      document.getElementById('loading').style.display = 'none';
      document.getElementById('content').style.display = 'block';
      const d = j.data;

      // Sektör seçimi durumu
      seçiliSektor = d.sektor_key;
      renderSektorBar(d);

      // Header
      document.getElementById('sb-header').innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;">
          <div>
            <div style="font-size:11px;color:#065f46;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;">
              <i class="fas fa-industry"></i> ${d.sektor_adi ? 'SEKTÖR: ' + esc(d.sektor_adi) : 'SEKTÖR BELİRLENMEDİ'}
            </div>
            <div style="font-size:20px;font-weight:800;color:#0f172a;">${esc(d.tenant_name)}</div>
          </div>
          <div style="display:flex;gap:16px;flex-wrap:wrap;">
            ${stat('fa-diagram-project','#6366f1', d.tenant_summary.process_count, 'Süreç')}
            ${stat('fa-chart-line','#0ea5e9', d.tenant_summary.kpi_count, 'PG')}
            ${stat('fa-users','#10b981', d.tenant_summary.user_count, 'Çalışan')}
          </div>
        </div>`;

      // Benchmark
      const benchEl = document.getElementById('sb-bench');
      if (d.sektor_secilmedi || !d.benchmark.length) {
        benchEl.innerHTML = '<div style="text-align:center;padding:32px;color:#94a3b8;font-size:13px;"><i class="fas fa-arrow-up" style="display:block;font-size:22px;margin-bottom:8px;"></i>Sektör seçildiğinde benchmark verileri burada görünecek.</div>';
      } else {
        benchEl.innerHTML =
          '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;">' +
          d.benchmark.map(b => `
            <div style="padding:14px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;">
              <div style="font-size:11px;color:#64748b;font-weight:600;margin-bottom:6px;">${esc(b.tr)}</div>
              <div style="font-size:20px;font-weight:700;color:#0d9488;">${esc(b.deger)}</div>
              <div style="font-size:10.5px;color:#94a3b8;margin-top:2px;">${esc(b.birim)} · sektör ort.</div>
            </div>`).join('') + '</div>';
      }

      // AI butonunu aktif/pasif et
      const aiBtn = document.getElementById('sb-ai-btn');
      if (aiBtn) aiBtn.disabled = d.sektor_secilmedi;

    } catch(e) {
      document.getElementById('loading').style.display = 'none';
      const err = document.getElementById('sb-error');
      err.style.display = 'block';
      err.textContent = 'Hata: ' + e.message;
    }
  }

  function renderSektorBar(d) {
    const bar = document.getElementById('sb-sektor-bar');
    if (!bar) return;
    const liste = d.sektor_listesi || [];
    const secim = d.sektor_key;

    if (d.sektor_secilmedi) {
      bar.innerHTML = `
        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:12px 16px;background:#fffbeb;border:1px solid #fde68a;border-radius:10px;margin-bottom:16px;">
          <i class="fas fa-triangle-exclamation" style="color:#d97706;"></i>
          <span style="font-size:13px;color:#92400e;font-weight:600;">Sisteminizde sektör bilgisi girilmemiş.</span>
          <span style="font-size:12.5px;color:#78350f;">Benchmark için lütfen sektörünüzü seçin:</span>
          <select id="sb-sektor-sel" class="mc-year-sel" style="min-width:180px;font-size:13px;padding:5px 10px;">
            <option value="">— Sektör seçin —</option>
            ${liste.map(s => `<option value="${esc(s.key)}">${esc(s.adi)}</option>`).join('')}
          </select>
          <button id="sb-sektor-uygula" class="mc-btn mc-btn-primary mc-btn-sm">Uygula</button>
        </div>`;
    } else {
      bar.innerHTML = `
        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:16px;">
          <span style="font-size:12.5px;color:#475569;">Sektör:</span>
          <select id="sb-sektor-sel" class="mc-year-sel" style="min-width:160px;font-size:13px;padding:5px 10px;">
            ${liste.map(s => `<option value="${esc(s.key)}" ${s.key===secim?'selected':''}>${esc(s.adi)}</option>`).join('')}
          </select>
          <button id="sb-sektor-uygula" class="mc-btn mc-btn-secondary mc-btn-sm"><i class="fas fa-rotate-right"></i> Güncelle</button>
          ${d.sector && d.sector !== '—' ? '' : '<span style="font-size:11.5px;color:#94a3b8;"><i class="fas fa-info-circle"></i> Kurum sektörü sistemde kayıtlı değil; seçim oturuma özel.</span>'}
        </div>`;
    }

    // Event listener
    const btn = document.getElementById('sb-sektor-uygula');
    if (btn) btn.addEventListener('click', () => {
      const sel = document.getElementById('sb-sektor-sel');
      if (sel && sel.value) { seçiliSektor = sel.value; loadData(sel.value); }
    });
  }

  function stat(icon, color, val, lbl){
    return `<div style="text-align:center;">
      <div style="font-size:18px;font-weight:700;color:${esc(color)};">${esc(val)}</div>
      <div style="font-size:10.5px;color:#64748b;margin-top:1px;">${esc(lbl)}</div>
    </div>`;
  }

  // ── Kota durumu ───────────────────────────────────────────────────────────
  async function loadQuota(){
    try {
      const j = await (await fetch('/raporlar/api/ai-status', {credentials:'same-origin'})).json();
      const badge = document.getElementById('sb-ai-badge');
      if (!badge || !j.success) return;
      if (j.byok) {
        badge.innerHTML = `<i class="fas fa-key" style="color:#10b981;"></i> ${esc(j.label)}`;
        badge.style.cssText += ';background:#ecfdf5;border-color:#a7f3d0;color:#065f46;';
      } else if (j.paused) {
        badge.innerHTML = '<i class="fas fa-ban" style="color:#ef4444;"></i> AI erişimi durduruldu';
        badge.style.cssText += ';background:#fef2f2;border-color:#fecaca;color:#991b1b;';
        document.getElementById('sb-ai-btn').disabled = true;
      } else {
        const remain = j.today_remain;
        const color = remain > 10 ? '#065f46' : remain > 3 ? '#92400e' : '#991b1b';
        const bg    = remain > 10 ? '#ecfdf5' : remain > 3 ? '#fffbeb' : '#fef2f2';
        badge.innerHTML = `<i class="fas fa-robot"></i> ${esc(j.label)}`;
        badge.style.cssText += `;background:${bg};color:${color};`;
        if (remain !== null && remain <= 0) {
          document.getElementById('sb-ai-btn').disabled = true;
          badge.innerHTML += ' — <b>Günlük limit doldu</b>';
        }
      }
    } catch(_){}
  }

  // ── AI Yorumu ─────────────────────────────────────────────────────────────
  async function fetchAI(){
    if (!seçiliSektor) {
      Swal && Swal.fire({icon:'warning',title:'Sektör seçilmedi',text:'Lütfen önce bir sektör seçin.',timer:2500,showConfirmButton:false});
      return;
    }
    const btn    = document.getElementById('sb-ai-btn');
    const result = document.getElementById('sb-ai-result');
    const txt    = document.getElementById('sb-ai-text');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> AI yorumu hazırlanıyor…';
    result.style.display = 'none';
    try {
      const j = await (await fetch('/raporlar/api/sektor-benchmark/ai-yorum', {
        method: 'POST', credentials: 'same-origin',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({sektor: seçiliSektor}),
      })).json();
      if (!j.success) throw new Error(j.message || 'AI yanıt vermedi');
      txt.textContent = j.yorum;
      result.style.display = 'block';
      btn.innerHTML = '<i class="fas fa-rotate-right"></i> Yenile';
      loadQuota();
    } catch(e) {
      txt.textContent = 'Hata: ' + e.message;
      result.style.display = 'block';
      btn.innerHTML = '<i class="fas fa-robot"></i> AI Yorumu Al';
    }
    btn.disabled = false;
  }

  document.addEventListener('DOMContentLoaded', function(){
    loadData(null);
    loadQuota();
    document.getElementById('sb-ai-btn')?.addEventListener('click', fetchAI);
  });
})();
