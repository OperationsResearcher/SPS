(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const stat = (l,v,c,code) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;"${code?` data-card-code="${code}"`:''}><div class="mc-stat-label" style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div><div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div></div>`;
  async function load(){
    try {
      const j = await (await fetch('/k-report/api/okr-cascade',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const s = j.summary;
      document.getElementById('summary').innerHTML = [
        stat('Objective', s.total_objectives, '#0d9488', 'raporlar_okr_cascade.objective'),
        stat('Key Result', s.total_krs, '#0ea5e9', 'raporlar_okr_cascade.key_result'),
        stat('Ort. Tamamlanma', '%'+s.avg_completion, s.avg_completion>=70?'#10b981':s.avg_completion>=40?'#f59e0b':'#dc2626', 'raporlar_okr_cascade.ort_tamamlanma'),
        stat('Plan Yılı', s.plan_year||'—', '#64748b', 'raporlar_okr_cascade.plan_yili'),
      ].join('');
      document.getElementById('list').innerHTML = j.objectives.length===0?'<div style="font-size:13px;color:#94a3b8;text-align:center;padding:30px;font-style:italic;">OKR objesi yok.</div>':j.objectives.map(o => {
        const ringColor = o.avg_progress>=70?'#10b981':o.avg_progress>=40?'#f59e0b':'#dc2626';
        return `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:18px;border-left:4px solid ${ringColor};">
          <div style="display:flex;justify-content:space-between;align-items:start;gap:14px;flex-wrap:wrap;margin-bottom:10px;">
            <div>
              <div style="font-size:14px;font-weight:700;color:#0f172a;">${esc(o.title)}</div>
              <div style="font-size:11.5px;color:#64748b;margin-top:2px;">
                ${o.quarter?'Q'+o.quarter+' · ':''}${o.owner?esc(o.owner)+' · ':''}${o.strategy?'<span style="background:#eef2ff;color:#4338ca;padding:1px 7px;border-radius:6px;">'+esc(o.strategy)+'</span>':''}
              </div>
            </div>
            <div style="text-align:right;">
              <div style="font-size:24px;font-weight:700;color:${ringColor};">%${o.avg_progress}</div>
              <div style="font-size:10.5px;color:#94a3b8;">${o.kr_count} KR</div>
            </div>
          </div>
          ${o.key_results.map(k => `
            <div style="background:#f8fafc;border-radius:6px;padding:8px 12px;margin-top:6px;display:flex;align-items:center;gap:12px;font-size:12px;">
              <div style="flex:1;min-width:0;">
                <div style="color:#475569;">${esc(k.title)} ${k.metric?'<span style="color:#94a3b8;">('+esc(k.metric)+')</span>':''}</div>
                <div style="font-size:10.5px;color:#94a3b8;">${k.start||'-'} → ${k.current||'-'} / ${k.target||'-'}</div>
              </div>
              <div style="width:100px;background:#e2e8f0;border-radius:4px;height:8px;overflow:hidden;">
                <div style="background:${(k.progress_pct||0)>=70?'#10b981':'#f59e0b'};height:100%;width:${Math.min(k.progress_pct||0,100)}%;"></div>
              </div>
              <div style="width:42px;text-align:right;font-weight:600;color:#0f172a;">%${k.progress_pct==null?'—':k.progress_pct}</div>
            </div>`).join('')}
        </div>`;
      }).join('');
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error');err.style.display='block';err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
