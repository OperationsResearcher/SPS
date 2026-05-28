(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  async function load(){
    try {
      const j = await (await fetch('/raporlar/api/sektor-benchmark',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const d=j.data;
      document.getElementById('header').innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;">
          <div>
            <div style="font-size:11px;color:#065f46;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">SEKTÖR: ${esc((d.sektor_key||'').toUpperCase())}</div>
            <div style="font-size:20px;font-weight:800;color:#0f172a;margin-top:3px;">${esc(d.tenant_name)}</div>
            <div style="font-size:12px;color:#64748b;margin-top:3px;">Sektör: ${esc(d.sector)}</div>
          </div>
          <div style="text-align:right;font-size:12px;color:#64748b;">
            <div>${d.tenant_summary.process_count} süreç · ${d.tenant_summary.kpi_count} PG · ${d.tenant_summary.user_count} çalışan</div>
          </div>
        </div>`;
      document.getElementById('bench-list').innerHTML = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;">' +
        Object.entries(d.benchmark).map(([k,v]) => `
          <div style="padding:12px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;">
            <div style="font-size:11px;color:#64748b;font-weight:600;margin-bottom:4px;">${esc(k)}</div>
            <div style="font-size:18px;font-weight:700;color:#0d9488;">${esc(v)}</div>
          </div>`).join('') + '</div>';
      document.getElementById('ai-comment').textContent = d.ai_comment;
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error');err.style.display='block';err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
