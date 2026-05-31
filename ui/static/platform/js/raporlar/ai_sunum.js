(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const dpItem = (lab, val) => `
    <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px;">
      <div style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:3px;">${esc(lab)}</div>
      <div style="font-size:18px;font-weight:700;color:#0f172a;">${esc(val)}</div>
    </div>`;

  async function load(){
    try {
      const j = await (await fetch('/raporlar/api/ai-sunum/preview',{credentials:'same-origin'})).json();
      if (!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const p = j.preview;
      document.getElementById('header-title').textContent = `${p.tenant_name} — ${p.plan_year || 'Yıllık'} Sunumu`;
      document.getElementById('header-meta').textContent = `${p.slides.length} slayt · ~${p.estimated_size_kb} KB · AI özet (Gemini varsa LLM, yoksa şablon)`;

      const d = p.data_points;
      document.getElementById('data-points').innerHTML = [
        dpItem('Strateji', d.strategies),
        dpItem('Süreç', d.processes),
        dpItem('Stratejik Girişim', d.initiatives),
        dpItem('Çalışan', d.users),
        dpItem('KPI Ölçüm', d.kpi_measurements.toLocaleString('tr-TR')),
      ].join('');

      document.getElementById('slides').innerHTML = p.slides.map(s => `
        <div style="display:flex;align-items:center;gap:14px;padding:10px 14px;border:1px solid #e2e8f0;border-radius:6px;background:#fff;">
          <div style="width:32px;height:32px;border-radius:50%;background:#dc2626;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;flex-shrink:0;">${s.no}</div>
          <div style="flex:1;min-width:0;">
            <div style="font-weight:600;color:#0f172a;font-size:13px;">${esc(s.title)}</div>
            <div style="font-size:11.5px;color:#64748b;margin-top:2px;">${esc(s.content)}</div>
          </div>
        </div>`).join('');
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err = document.getElementById('error'); err.style.display='block'; err.textContent='Hata: '+e.message;
    }
  }

  document.getElementById('dl-btn').addEventListener('click', async () => {
    const btn = document.getElementById('dl-btn');
    const orig = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Üretiliyor… (10-30sn)';
    try {
      const r = await fetch('/raporlar/api/ai-sunum/generate', {method:'GET', credentials:'same-origin'});
      if (!r.ok) {
        const j = await r.json().catch(() => ({message:'Üretim başarısız'}));
        throw new Error(j.message || ('HTTP ' + r.status));
      }
      const blob = await r.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const cd = r.headers.get('Content-Disposition') || '';
      const m = cd.match(/filename="?([^";]+)"?/);
      a.download = m ? m[1] : 'yil_sonu_sunum.pptx';
      document.body.appendChild(a);
      a.click();
      setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(url); }, 100);
      btn.innerHTML = '<i class="fas fa-check"></i> İndirildi';
      setTimeout(() => { btn.innerHTML = orig; btn.disabled = false; }, 2500);
    } catch (e) {
      Swal.fire({icon:'error', title:'Hata', text:e.message});
      btn.innerHTML = orig;
      btn.disabled = false;
    }
  });

  load();
})();
