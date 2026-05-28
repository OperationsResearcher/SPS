(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const stat = (l,v,c) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;"><div style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div><div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div></div>`;
  const LEVEL_COLOR = {1:'#dc2626',2:'#f59e0b',3:'#0ea5e9',4:'#10b981',5:'#6366f1'};
  async function load(){
    try {
      const j = await (await fetch('/raporlar/api/cmmi-heatmap',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const s=j.summary;
      document.getElementById('summary').innerHTML=[
        stat('Toplam Süreç', s.total_processes, '#0f172a'),
        stat('Ortalama Seviye', s.avg_level, '#6366f1'),
        stat('Optimizing (L5)', s.level_5_count, '#10b981'),
      ].join('');
      const max = Math.max(...j.distribution.map(d=>d.count), 1);
      document.getElementById('dist').innerHTML = j.distribution.map(d => `
        <div style="display:flex;align-items:center;gap:12px;padding:5px 0;font-size:12.5px;">
          <div style="width:32px;height:32px;border-radius:8px;background:${LEVEL_COLOR[d.level]};color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0;">L${d.level}</div>
          <div style="width:180px;color:#0f172a;font-weight:600;">${esc(d.label)}</div>
          <div style="flex:1;background:#f1f5f9;border-radius:4px;height:18px;overflow:hidden;">
            <div style="background:${LEVEL_COLOR[d.level]};height:100%;width:${d.count/max*100}%;"></div>
          </div>
          <div style="width:60px;text-align:right;color:#475569;font-weight:600;">${d.count} süreç</div>
        </div>`).join('');
      document.getElementById('grid').innerHTML = j.processes.length===0 ? '<div style="color:#94a3b8;font-style:italic;grid-column:1/-1;">Olgunluk verisi yok.</div>' :
        j.processes.map(p => `
          <div style="background:#f8fafc;border:1px solid #e2e8f0;border-left:4px solid ${LEVEL_COLOR[p.level]};border-radius:6px;padding:8px 12px;font-size:12px;">
            <div style="font-weight:600;color:#0f172a;">${esc(p.code||'')} ${esc(p.name||'')}</div>
            <div style="font-size:10.5px;color:${LEVEL_COLOR[p.level]};font-weight:700;margin-top:2px;">L${p.level}</div>
          </div>`).join('');
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error');err.style.display='block';err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
