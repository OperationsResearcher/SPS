(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const stat = (l,v,c,code) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;"${code?` data-card-code="${code}"`:''}><div class="mc-stat-label" style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div><div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div></div>`;
  const PRIO = {critical:'#dc2626',high:'#f59e0b',medium:'#0ea5e9',low:'#94a3b8'};
  function drawGantt(inits, container){
    if(!inits.length){ container.innerHTML='<div style="text-align:center;padding:30px;color:#94a3b8;font-style:italic;">Stratejik girişim yok.</div>'; return; }
    const minY = Math.min(...inits.map(i=>i.start_year));
    const maxY = Math.max(...inits.map(i=>i.end_year));
    const years = [];
    for(let y=minY;y<=maxY;y++) years.push(y);
    const cellW = 80, rowH = 38, leftW = 280;
    let html = '<div style="min-width:'+(leftW+years.length*cellW)+'px;">';
    // header
    html += '<div style="display:flex;border-bottom:2px solid #e2e8f0;padding-bottom:8px;margin-bottom:6px;font-size:11.5px;font-weight:600;color:#475569;">';
    html += `<div style="width:${leftW}px;flex-shrink:0;">Stratejik Girişim</div>`;
    years.forEach(y => html += `<div style="width:${cellW}px;text-align:center;">${y}</div>`);
    html += '</div>';
    // rows
    inits.forEach(i => {
      const col = PRIO[i.priority] || '#94a3b8';
      const startIdx = years.indexOf(i.start_year);
      const span = (i.end_year - i.start_year + 1) * cellW;
      const opacity = i.status==='completed'?0.5:i.status==='cancelled'?0.25:1;
      html += `<div style="display:flex;align-items:center;height:${rowH}px;border-bottom:1px solid #f1f5f9;">
        <div style="width:${leftW}px;flex-shrink:0;font-size:12px;color:#0f172a;font-weight:500;padding-right:10px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
          <span style="background:${col};color:#fff;font-size:10px;font-weight:700;padding:1px 6px;border-radius:6px;margin-right:5px;">${esc(i.priority||'')}</span>${esc(i.code||'')} ${esc(i.name||'')}
        </div>
        <div style="display:flex;flex:1;">
          ${years.map((y,j)=>`<div style="width:${cellW}px;height:${rowH}px;border-left:1px solid #f8fafc;position:relative;">${j===startIdx?'<div style="position:absolute;left:4px;top:8px;width:'+(span-8)+'px;height:'+(rowH-16)+'px;background:'+col+';opacity:'+opacity+';border-radius:4px;display:flex;align-items:center;padding:0 8px;color:#fff;font-size:11px;font-weight:600;">%'+i.progress_pct+'</div>':''}</div>`).join('')}
        </div>
      </div>`;
    });
    html += '</div>';
    container.innerHTML = html;
  }
  async function load(){
    try {
      const j = await (await fetch('/reports/api/initiative-roadmap',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const s=j.summary;
      document.getElementById('summary').innerHTML=[
        stat('Toplam Stratejik Girişim',s.total,'#0f172a','raporlar_initiative_roadmap.toplam_stratejik_girisim'),
        stat('Yıl Aralığı',s.year_range,'#16a34a','raporlar_initiative_roadmap.yil_araligi'),
        stat('Milestone',s.total_milestones,'#0ea5e9','raporlar_initiative_roadmap.milestone'),
      ].join('');
      drawGantt(j.initiatives, document.getElementById('gantt'));
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error');err.style.display='block';err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
