(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const stat = (l,v,c) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;"><div style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div><div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div></div>`;
  const fmt = n => new Intl.NumberFormat('tr-TR').format(Math.round(n||0));
  async function load(){
    try {
      const j = await (await fetch('/raporlar/api/roi-per-strategy',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const s=j.summary;
      document.getElementById('summary').innerHTML=[
        stat('Toplam Strateji',s.total_strategies,'#0f172a'),
        stat('Toplam Bütçe','₺'+fmt(s.total_budget),'#0ea5e9'),
        stat('Toplam Harcanan','₺'+fmt(s.total_spent),'#f59e0b'),
        stat('Plan Yılı',s.plan_year||'—','#64748b'),
      ].join('');
      document.getElementById('tbl').innerHTML = j.strategies.map(r => {
        const roiC = r.roi_score==null?'#94a3b8':r.roi_score>=10?'#10b981':r.roi_score>=3?'#f59e0b':'#dc2626';
        return `<tr style="border-bottom:1px solid #f1f5f9;">
          <td style="padding:10px;color:#0f172a;font-weight:600;">${esc(r.code||'')} ${esc(r.title||'')}</td>
          <td style="padding:10px;text-align:right;color:#475569;">₺${fmt(r.budget)}</td>
          <td style="padding:10px;text-align:right;color:#475569;">₺${fmt(r.spent)}</td>
          <td style="padding:10px;text-align:right;color:#475569;font-weight:600;">${r.avg_score==null?'—':r.avg_score}</td>
          <td style="padding:10px;text-align:right;color:${roiC};font-weight:700;font-size:14px;">${r.roi_score==null?'—':r.roi_score}</td>
        </tr>`;
      }).join('');
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error');err.style.display='block';err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
