(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const stat = (l,v,c,sub) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;"><div style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div><div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div>${sub?'<div style="font-size:11px;color:#94a3b8;margin-top:2px;">'+esc(sub)+'</div>':''}</div>`;
  const scoreColor = s => s==null?'#94a3b8':s>=70?'#10b981':s>=50?'#f59e0b':'#dc2626';
  async function load(){
    try {
      const j = await (await fetch('/raporlar/api/coo-dashboard',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const m=j.metrics;
      document.getElementById('kpis').innerHTML=[
        stat('Süreç',m.total_processes,'#0f172a'),
        stat('Ort. Sağlık',m.avg_score||'—',scoreColor(m.avg_score)),
        stat('Geciken Faaliyet',m.overdue_activities,m.overdue_activities>0?'#dc2626':'#10b981'),
        stat('Aktif Darboğaz',m.active_bottlenecks,m.active_bottlenecks>0?'#f59e0b':'#10b981'),
        stat('Ort. CMMI',m.avg_cmmi_level||'—','#6366f1'),
      ].join('');
      const d=j.distribution;
      const total = d.good+d.medium+d.low+d.no_data || 1;
      document.getElementById('dist-bars').innerHTML = `
        <div style="display:flex;gap:8px;height:34px;border-radius:6px;overflow:hidden;">
          <div style="flex:${d.good};background:#10b981;display:flex;align-items:center;justify-content:center;color:#fff;font-size:12px;font-weight:700;">${d.good>0?d.good+' iyi':''}</div>
          <div style="flex:${d.medium};background:#f59e0b;display:flex;align-items:center;justify-content:center;color:#fff;font-size:12px;font-weight:700;">${d.medium>0?d.medium+' orta':''}</div>
          <div style="flex:${d.low};background:#dc2626;display:flex;align-items:center;justify-content:center;color:#fff;font-size:12px;font-weight:700;">${d.low>0?d.low+' düşük':''}</div>
          <div style="flex:${d.no_data};background:#cbd5e1;display:flex;align-items:center;justify-content:center;color:#0f172a;font-size:12px;font-weight:700;">${d.no_data>0?d.no_data+' veri yok':''}</div>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:11px;color:#64748b;margin-top:6px;">
          <span>İyi (≥70)</span><span>Orta</span><span>Düşük (<50)</span><span>Veri yok</span>
        </div>`;
      document.getElementById('proc-grid').innerHTML = j.processes.map(p => `
        <div style="border:1px solid #e2e8f0;border-left:4px solid ${scoreColor(p.score)};border-radius:6px;padding:8px 12px;background:#f8fafc;font-size:12px;">
          <div style="font-weight:600;color:#0f172a;">${esc(p.code||'')} ${esc(p.name||'')}</div>
          <div style="display:flex;justify-content:space-between;margin-top:4px;">
            <span style="font-size:10.5px;color:#94a3b8;">w=${p.weight||0}</span>
            <span style="font-weight:700;color:${scoreColor(p.score)};">${p.score==null?'—':p.score}</span>
          </div>
        </div>`).join('') || '<div style="color:#94a3b8;font-style:italic;">Süreç yok.</div>';
      const bnActive = j.bottlenecks.filter(b => !b.resolved);
      document.getElementById('bn-list').innerHTML = bnActive.length===0?'<div style="color:#10b981;font-size:12.5px;">✓ Aktif darboğaz yok.</div>':
        bnActive.map(b => `
          <div style="padding:8px 10px;border-left:3px solid #dc2626;background:#fef2f2;border-radius:0 6px 6px 0;margin-bottom:6px;font-size:12px;">
            <div style="font-weight:600;color:#0f172a;">${esc(b.severity||'—')}</div>
            <div style="color:#475569;margin-top:2px;font-size:11px;">${esc(b.note||'')}</div>
            ${b.triggered_at?'<div style="color:#94a3b8;font-size:10.5px;margin-top:2px;">'+esc(b.triggered_at.substring(0,10))+'</div>':''}
          </div>`).join('');
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error');err.style.display='block';err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
