(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const fmt = n => '₺' + new Intl.NumberFormat('tr-TR').format(Math.round(n||0));
  const stat = (l,v,c,sub) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;"><div style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div><div style="font-size:20px;font-weight:700;color:${c};line-height:1.2;">${esc(v)}</div>${sub?'<div style="font-size:11px;color:#94a3b8;margin-top:2px;">'+esc(sub)+'</div>':''}</div>`;
  async function load(){
    try {
      const j = await (await fetch('/raporlar/api/cfo-dashboard',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const m=j.metrics;
      document.getElementById('kpis').innerHTML=[
        stat('Toplam Bütçe', fmt(m.total_budget), '#0f172a', m.initiative_count+' girişim'),
        stat('Harcanan', fmt(m.total_spent), '#f59e0b', '%'+m.usage_pct+' kullanım'),
        stat('Kalan', fmt(m.remaining), '#10b981'),
        stat('Bütçe Aşan', m.over_budget_count, m.over_budget_count>0?'#dc2626':'#10b981'),
        stat('LLM Maliyet (30g)', '$'+m.llm_cost_30d_usd.toFixed(2), '#6366f1', m.llm_calls_30d+' çağrı'),
        stat('Recurring Task', m.recurring_count, '#0ea5e9'),
      ].join('');
      document.getElementById('top5').innerHTML = j.top_initiatives.map(i => `
        <div style="display:flex;align-items:center;gap:12px;padding:10px;border:1px solid #e2e8f0;border-radius:6px;margin-bottom:6px;font-size:12.5px;">
          <div style="flex:1;min-width:0;">
            <div style="font-weight:600;color:#0f172a;">${esc(i.code||'')} ${esc(i.name)}</div>
            <div style="font-size:11px;color:#64748b;margin-top:2px;">${esc(i.status||'')} · %${i.progress} ilerleme</div>
          </div>
          <div style="text-align:right;">
            <div style="font-weight:700;color:#0f172a;">${fmt(i.budget)}</div>
            <div style="font-size:10.5px;color:${i.usage_pct>100?'#dc2626':'#64748b'};">${fmt(i.spent)} kullanıldı (%${i.usage_pct})</div>
          </div>
        </div>`).join('') || '<div style="color:#94a3b8;font-style:italic;">Stratejik girişim yok.</div>';
      document.getElementById('status-list').innerHTML = Object.entries(j.by_status).map(([s,c]) => `
        <div style="display:flex;justify-content:space-between;padding:6px 8px;border-bottom:1px solid #f1f5f9;font-size:12.5px;">
          <span style="color:#475569;">${esc(s)}</span>
          <span style="font-weight:700;color:#0f172a;">${c}</span>
        </div>`).join('') || '<div style="color:#94a3b8;font-style:italic;">Veri yok.</div>';
      document.getElementById('strat-table').innerHTML = j.by_strategy.length===0?'<div style="color:#94a3b8;font-style:italic;">Strateji bazlı atıf yok.</div>':
        '<table style="width:100%;border-collapse:collapse;font-size:12.5px;"><thead><tr style="background:#f8fafc;border-bottom:2px solid #e2e8f0;"><th style="padding:8px;text-align:left;">Strateji</th><th style="padding:8px;text-align:right;">Bütçe</th><th style="padding:8px;text-align:right;">Harcanan</th><th style="padding:8px;text-align:right;">Kullanım %</th><th style="padding:8px;text-align:right;">Stratejik Girişim</th></tr></thead><tbody>'+
        j.by_strategy.map(s => `<tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:8px;color:#0f172a;font-weight:600;">${esc(s.label)}</td><td style="padding:8px;text-align:right;">${fmt(s.budget)}</td><td style="padding:8px;text-align:right;">${fmt(s.spent)}</td><td style="padding:8px;text-align:right;color:${s.usage_pct>90?'#dc2626':'#475569'};font-weight:600;">%${s.usage_pct}</td><td style="padding:8px;text-align:right;">${s.count}</td></tr>`).join('')+'</tbody></table>';
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error');err.style.display='block';err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
