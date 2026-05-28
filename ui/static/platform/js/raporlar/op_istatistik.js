(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const stat = (l,v,c) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;"><div style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div><div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div></div>`;
  async function load(){
    try {
      const j = await (await fetch('/raporlar/api/operasyon-istatistik',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const s=j.summary;
      document.getElementById('summary').innerHTML=[
        stat('Toplam Süreç',s.total_processes,'#0f172a'),
        stat('Toplam PG',s.total_kpis,'#0ea5e9'),
        stat('Toplam Faaliyet',s.total_activities,'#0d9488'),
      ].join('');
      document.getElementById('tbl').innerHTML = j.processes.map(p => `
        <tr style="border-bottom:1px solid #f1f5f9;">
          <td style="padding:10px;color:#0f172a;font-weight:600;">${esc(p.code||'-')}</td>
          <td style="padding:10px;color:#475569;">${esc(p.name)}</td>
          <td style="padding:10px;"><span style="background:${p.status==='Aktif'?'#dcfce7':'#fef3c7'};color:${p.status==='Aktif'?'#166534':'#92400e'};padding:2px 8px;border-radius:6px;font-size:11px;font-weight:600;">${esc(p.status||'-')}</span></td>
          <td style="padding:10px;text-align:right;color:#0ea5e9;font-weight:700;">${p.kpi_count}</td>
          <td style="padding:10px;text-align:right;color:#0d9488;font-weight:700;">${p.activity_count}</td>
        </tr>`).join('');
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error');err.style.display='block';err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
