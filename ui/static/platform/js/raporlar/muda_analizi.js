(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const stat = (l,v,c) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;"><div style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div><div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div></div>`;
  async function load(){
    try {
      const j = await (await fetch('/raporlar/api/muda-analizi',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const s = j.summary;
      document.getElementById('summary').innerHTML=[
        stat('Analiz Edilen Süreç', s.total_processes_analyzed, '#0f172a'),
        stat('Bulgu Olan Süreç', s.processes_with_findings, '#f59e0b'),
        stat('Toplam Bulgu', s.total_findings, '#dc2626'),
      ].join('');
      const max = Math.max(...j.by_muda.map(m=>m.count), 1);
      document.getElementById('by-muda').innerHTML = j.by_muda.length===0 ? '<div style="color:#94a3b8;font-style:italic;">Muda bulgusu yok.</div>' :
        j.by_muda.map(m => `
          <div style="display:flex;align-items:center;gap:12px;font-size:12.5px;padding:5px 0;">
            <div style="width:140px;color:#0f172a;font-weight:600;">${esc(m.label)}</div>
            <div style="flex:1;background:#f1f5f9;border-radius:4px;height:18px;overflow:hidden;">
              <div style="background:#16a34a;height:100%;width:${m.count/max*100}%;"></div>
            </div>
            <div style="width:60px;text-align:right;font-weight:600;color:#475569;">${m.count}</div>
          </div>`).join('');
      document.getElementById('by-process').innerHTML = j.by_process.length===0 ? '<div style="color:#94a3b8;font-style:italic;">Bulgu olan süreç yok — Lean göstergeleriniz iyi.</div>' :
        '<div style="display:grid;gap:8px;">' + j.by_process.slice(0,15).map(p => `
          <div style="padding:10px 12px;border:1px solid #e2e8f0;border-radius:6px;background:#f8fafc;font-size:12.5px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
              <span style="font-weight:600;color:#0f172a;">${esc(p.code||'')} ${esc(p.name)}</span>
              <span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:6px;font-size:11px;font-weight:600;">${p.findings_count} bulgu</span>
            </div>
            ${(p.findings||[]).slice(0,3).map(f=>`<div style="font-size:11px;color:#64748b;margin-left:6px;">• ${esc(f.message||f.description||JSON.stringify(f).substring(0,80))}</div>`).join('')}
          </div>`).join('') + '</div>';
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error');err.style.display='block';err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
