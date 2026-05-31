(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const yearSel = document.getElementById('op-year-select');
  const stat = (l,v,c,sub) => `<div class="mc-card" style="padding:12px 14px;">
    <div style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;">${esc(l)}</div>
    <div style="font-size:22px;font-weight:800;color:${c};margin-top:3px;">${esc(v)}</div>
    ${sub ? `<div style="font-size:11px;color:#94a3b8;margin-top:2px;">${esc(sub)}</div>` : ''}
  </div>`;
  async function load(){
    try {
      document.getElementById('loading').style.display='';
      document.getElementById('content').style.display='none';
      const y = yearSel?.value || '';
      const url = '/raporlar/api/operasyon-istatistik' + (y ? '?year=' + encodeURIComponent(y) : '');
      const j = await (await fetch(url,{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const s=j.summary;
      document.getElementById('summary').innerHTML=[
        stat('Toplam Süreç', s.total_processes, '#0f172a', s.plan_year ? `${s.plan_year} yılı` : ''),
        stat('Toplam PG', s.total_kpis, '#0ea5e9'),
        stat('Toplam Faaliyet', s.total_activities, '#0d9488'),
      ].join('');
      document.getElementById('tbl').innerHTML = j.processes.map(p => `
        <tr style="border-bottom:1px solid #f1f5f9;">
          <td style="padding:10px;color:#0f172a;font-weight:600;font-family:monospace;">${esc(p.code||'-')}</td>
          <td style="padding:10px;color:#1e293b;"><a href="/process/${p.id}/karne" style="color:inherit; text-decoration:none;">${esc(p.name)}</a></td>
          <td style="padding:10px;"><span style="background:${p.status==='Aktif'?'#dcfce7':'#fef3c7'};color:${p.status==='Aktif'?'#166534':'#92400e'};padding:2px 8px;border-radius:6px;font-size:11px;font-weight:600;">${esc(p.status||'-')}</span></td>
          <td style="padding:10px;text-align:right;color:#0ea5e9;font-weight:700;">${p.kpi_count}</td>
          <td style="padding:10px;text-align:right;color:#0d9488;font-weight:700;">${p.activity_count}</td>
        </tr>`).join('');
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error');err.style.display='block';err.textContent='Hata: '+e.message;
    }
  }
  yearSel?.addEventListener('change', async () => {
    const newYear = parseInt(yearSel.value, 10);
    if (!newYear) return;
    try {
      const csrf = document.querySelector('meta[name="csrf-token"]')?.content || '';
      await fetch('/sp/api/plan-years/set-active', {
        method:'POST', credentials:'same-origin',
        headers: {'Content-Type':'application/json', 'X-CSRFToken': csrf},
        body: JSON.stringify({year: newYear})
      });
    } catch(_) {}
    load();
  });
  load();
})();
