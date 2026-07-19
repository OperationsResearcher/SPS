(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const statCard = (l,v,c,code) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;"${code?` data-card-code="${code}"`:''}>
    <div class="mc-stat-label" style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div>
    <div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div></div>`;
  async function load(){
    try {
      const j = await (await fetch('/k-report/api/department-performance',{credentials:'same-origin'})).json();
      if (!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const s = j.summary;
      document.getElementById('summary').innerHTML = [
        statCard('Departman', s.total_departments, '#0f172a', 'raporlar_departman_performans.departman'),
        statCard('Toplam Çalışan', s.total_users, '#0ea5e9', 'raporlar_departman_performans.toplam_calisan'),
        statCard('Toplam Bireysel PG', s.total_pgs, '#db2777', 'raporlar_departman_performans.toplam_bireysel_pg'),
      ].join('');
      document.getElementById('tbl').innerHTML = j.departments.map(d => {
        const totpC = d.totp_rate >= 80 ? '#10b981' : d.totp_rate >= 30 ? '#f59e0b' : '#dc2626';
        return `<tr style="border-bottom:1px solid #f1f5f9;">
          <td style="padding:10px;color:#0f172a;font-weight:600;">${esc(d.department)}</td>
          <td style="padding:10px;text-align:right;color:#475569;font-weight:600;">${d.user_count}</td>
          <td style="padding:10px;text-align:right;color:#475569;">${d.pg_count}</td>
          <td style="padding:10px;text-align:right;color:#475569;">${d.pg_per_user}</td>
          <td style="padding:10px;text-align:right;color:#db2777;font-weight:600;">${d.important_pg}</td>
          <td style="padding:10px;text-align:right;color:${totpC};font-weight:700;">%${d.totp_rate}</td>
        </tr>`;
      }).join('');
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err = document.getElementById('error'); err.style.display='block'; err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
