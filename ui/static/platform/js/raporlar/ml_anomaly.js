(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const stat = (l,v,c) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;"><div style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div><div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div></div>`;
  async function load(){
    try {
      const j = await (await fetch('/k-report/api/ml-anomaly',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const s=j.summary;
      document.getElementById('summary').innerHTML=[
        stat('Analiz Edilen PG',s.kpis_analyzed,'#0f172a'),
        stat('Atlanan (yetersiz veri)',s.kpis_skipped,'#94a3b8'),
        stat('Anomali Sayısı',s.anomalies_found,s.anomalies_found>0?'#dc2626':'#10b981'),
      ].join('');
      if(j.anomalies.length===0){
        document.getElementById('anomalies').innerHTML='<div style="text-align:center;padding:40px;color:#10b981;font-size:13px;"><i class="fas fa-check-circle" style="font-size:24px;margin-bottom:8px;display:block;"></i>Anomali tespit edilmedi — KPI ölçümleriniz normal dağılımda.</div>';
        return;
      }
      document.getElementById('anomalies').innerHTML = '<div style="display:grid;gap:8px;">' + j.anomalies.map(a => `
        <div style="display:flex;align-items:center;gap:12px;padding:12px;background:#fef2f2;border:1px solid #fecaca;border-left:4px solid #dc2626;border-radius:0 6px 6px 0;font-size:12.5px;">
          <div style="flex:1;min-width:0;">
            <div style="font-weight:600;color:#0f172a;">${esc(a.kpi_code)} · ${esc(a.kpi_name)}</div>
            <div style="font-size:11px;color:#64748b;margin-top:2px;">${esc(a.process_name)} · ${esc(a.date||'—')}</div>
          </div>
          <div style="text-align:right;">
            <div style="font-weight:700;color:#dc2626;font-size:14px;">${a.value}</div>
            <div style="font-size:10.5px;color:#94a3b8;">Anomaly score: ${a.anomaly_score}</div>
          </div>
        </div>`).join('') + '</div>';
    } catch(e){ document.getElementById('loading').style.display='none'; const er=document.getElementById('error'); er.style.display='block'; er.textContent='Hata: '+e.message; }
  }
  load();
})();
