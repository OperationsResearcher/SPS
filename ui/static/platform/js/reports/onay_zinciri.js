(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const stat = (l,v,c,code) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;"${code?` data-card-code="${code}"`:''}><div class="mc-stat-label" style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div><div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div></div>`;
  const fmt = n => new Intl.NumberFormat('tr-TR').format(Math.round(n||0));
  async function load(){
    try {
      const j = await (await fetch('/k-report/api/approval-chain',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const s=j.summary;
      document.getElementById('summary').innerHTML=[
        stat('Toplam',s.total,'#0f172a','raporlar_onay_zinciri.toplam'),
        stat('Onay Bekliyor',s.pending,s.pending>0?'#f59e0b':'#94a3b8','raporlar_onay_zinciri.onay_bekliyor'),
        stat('Onaylanmış',s.approved,'#10b981','raporlar_onay_zinciri.onaylanmis'),
        stat('Reddedilen',s.rejected,s.rejected>0?'#dc2626':'#94a3b8','raporlar_onay_zinciri.reddedilen'),
      ].join('');
      const prioColor = {'Kritik':'#dc2626','Yüksek':'#f97316','Orta':'#f59e0b','Düşük':'#94a3b8'};
      document.getElementById('tbl').innerHTML = j.items.map(i => {
        const pc = prioColor[i.priority] || '#64748b';
        const progColor = i.progress >= 80 ? '#10b981' : i.progress >= 40 ? '#f59e0b' : '#ef4444';
        return `<tr style="border-bottom:1px solid #f1f5f9;">
          <td style="padding:10px;color:#6366f1;font-weight:700;font-size:11.5px;">${esc(i.code||'—')}</td>
          <td style="padding:10px;color:#0f172a;font-weight:600;">${esc(i.name)}</td>
          <td style="padding:10px;"><span style="background:${i.approval_color};color:#fff;padding:3px 10px;border-radius:6px;font-size:11px;font-weight:700;">${esc(i.approval)}</span></td>
          <td style="padding:10px;"><span style="color:${pc};font-weight:700;font-size:11.5px;">${esc(i.priority||'—')}</span></td>
          <td style="padding:10px;color:#475569;font-size:11.5px;">${esc(i.owner||'—')}</td>
          <td style="padding:10px;text-align:right;color:#475569;font-size:12px;">₺${fmt(i.budget)}</td>
          <td style="padding:10px;text-align:right;font-weight:700;color:${progColor};font-size:12px;">%${i.progress}</td>
        </tr>`;
      }).join('');
    } catch(e){ document.getElementById('loading').style.display='none'; const er=document.getElementById('error'); er.style.display='block'; er.textContent='Hata: '+e.message; }
  }
  load();
})();
