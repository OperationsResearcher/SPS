(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const stat = (l,v,c) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;"><div style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div><div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div></div>`;
  function cellColor(p, i) {
    const rpn = p * i;
    if(rpn>=15) return '#dc2626';
    if(rpn>=8) return '#f59e0b';
    if(rpn>=4) return '#fef3c7';
    return '#dcfce7';
  }
  async function load(){
    try {
      const j = await (await fetch('/reports/api/risk-heatmap',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const s=j.summary;
      document.getElementById('summary').innerHTML=[
        stat('Toplam Risk',s.total,'#0f172a'),
        stat('Açık',s.open,'#dc2626'),
        stat('Çözülmüş',s.mitigated,'#10b981'),
        stat('Yüksek RPN',s.high_rpn,'#f59e0b'),
      ].join('');
      // 5×5 grid (probability 5→1 üstten alta, impact 1→5 soldan sağa)
      let html = '<div></div>';
      for(let i=1;i<=5;i++) html += `<div style="text-align:center;font-weight:600;color:#64748b;">${i}</div>`;
      for(let p=5;p>=1;p--){
        html += `<div style="text-align:right;font-weight:600;color:#64748b;padding-right:6px;line-height:60px;">${p}</div>`;
        for(let imp=1;imp<=5;imp++){
          const items = j.grid[p-1][imp-1];
          html += `<div style="background:${cellColor(p,imp)};min-height:60px;border-radius:4px;padding:4px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#0f172a;cursor:default;" title="${items.length} risk: ${items.map(r=>r.title).join(', ').substring(0,100)}">${items.length || ''}</div>`;
        }
      }
      document.getElementById('grid').innerHTML = html;
      document.getElementById('top10').innerHTML = j.top_risks.length===0?'<div style="color:#94a3b8;font-style:italic;">Risk yok.</div>':
        '<div style="display:grid;gap:6px;">' + j.top_risks.map(r => `
          <div style="display:flex;align-items:center;gap:10px;padding:8px;background:#f8fafc;border-radius:6px;font-size:12px;">
            <div style="width:40px;height:30px;background:${cellColor(r.probability||1,r.impact||1)};color:#0f172a;font-weight:700;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:11px;flex-shrink:0;">${r.rpn||0}</div>
            <div style="flex:1;min-width:0;">
              <div style="font-weight:600;color:#0f172a;">${esc(r.title)}</div>
              <div style="font-size:10.5px;color:#64748b;">P=${r.probability} · I=${r.impact} · ${esc(r.status||'Open')}</div>
            </div>
          </div>`).join('') + '</div>';
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error');err.style.display='block';err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
