(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const stat = (l,v,c,sub,code) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;"${code?` data-card-code="${code}"`:''}><div class="mc-stat-label" style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div><div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div>${sub?'<div style="font-size:11px;color:#94a3b8;margin-top:2px;">'+esc(sub)+'</div>':''}</div>`;
  async function load(){
    try {
      const j = await (await fetch('/reports/api/chro-dashboard',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const m=j.metrics;
      document.getElementById('kpis').innerHTML=[
        stat('Çalışan',m.total_users,'#0f172a','','raporlar_chro_dashboard.calisan'),
        stat('Departman',m.total_departments,'#db2777','','raporlar_chro_dashboard.departman'),
        stat('Bireysel PG',m.total_pgs,'#8b5cf6',m.users_with_pg+' kişide','raporlar_chro_dashboard.bireysel_pg'),
        stat('Ort. PG / Kişi',m.avg_pg_per_user,'#0ea5e9','','raporlar_chro_dashboard.ort_pg_kisi'),
        stat('2FA Oranı','%'+m.totp_pct,m.totp_pct>=80?'#10b981':m.totp_pct>=40?'#f59e0b':'#dc2626','','raporlar_chro_dashboard.2fa_orani'),
      ].join('');
      const maxD = Math.max(...j.departments.map(d=>d.count),1);
      document.getElementById('depts').innerHTML = j.departments.map(d => `
        <div style="display:flex;align-items:center;gap:8px;padding:4px 0;font-size:12px;">
          <div style="width:170px;color:#475569;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${esc(d.dept)}</div>
          <div style="flex:1;background:#f1f5f9;border-radius:4px;height:16px;overflow:hidden;">
            <div style="background:#db2777;height:100%;width:${d.count/maxD*100}%;"></div>
          </div>
          <div style="width:36px;text-align:right;color:#0f172a;font-weight:700;">${d.count}</div>
        </div>`).join('');
      document.getElementById('roles').innerHTML = j.roles.map(r => `
        <div style="display:flex;justify-content:space-between;padding:8px 10px;border-bottom:1px solid #f1f5f9;font-size:12.5px;">
          <span style="color:#0f172a;font-weight:500;">${esc(r.role)}</span>
          <span style="font-weight:700;color:#db2777;">${r.count}</span>
        </div>`).join('');
      document.getElementById('top-users').innerHTML = j.top_users_by_pg.length===0?'<div style="color:#94a3b8;font-style:italic;font-size:12.5px;">Bireysel PG\'si olan kullanıcı yok.</div>':
        '<div style="display:grid;gap:6px;">' + j.top_users_by_pg.map((u,i) => `
          <div style="display:flex;align-items:center;gap:10px;padding:8px 10px;background:#f8fafc;border-radius:6px;font-size:12.5px;">
            <div style="width:24px;height:24px;border-radius:50%;background:#8b5cf6;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:11px;flex-shrink:0;">${i+1}</div>
            <div style="flex:1;min-width:0;">
              <div style="font-weight:600;color:#0f172a;">${esc(u.name)}</div>
              <div style="font-size:10.5px;color:#94a3b8;">${esc(u.department||'—')}</div>
            </div>
            <div style="font-weight:700;color:#8b5cf6;">${u.pg_count}</div>
          </div>`).join('') + '</div>';
      document.getElementById('most-loaded').innerHTML = j.most_loaded_in_processes.length===0?'<div style="color:#94a3b8;font-style:italic;font-size:12.5px;">Süreç üyeliği verisi yok.</div>':
        '<div style="display:grid;gap:6px;">' + j.most_loaded_in_processes.map((u,i) => `
          <div style="display:flex;align-items:center;gap:10px;padding:8px 10px;background:#f8fafc;border-radius:6px;font-size:12.5px;">
            <div style="width:24px;height:24px;border-radius:50%;background:#0d9488;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:11px;flex-shrink:0;">${i+1}</div>
            <div style="flex:1;font-weight:600;color:#0f172a;">${esc(u.name)}</div>
            <div style="font-weight:700;color:#0d9488;">${u.process_count} süreç</div>
          </div>`).join('') + '</div>';
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error');err.style.display='block';err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
