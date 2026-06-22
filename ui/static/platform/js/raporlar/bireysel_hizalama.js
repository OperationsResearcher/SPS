(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const stat = (l,v,c,code) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;"${code?` data-card-code="${code}"`:''}><div class="mc-stat-label" style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div><div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div></div>`;
  async function load(){
    try {
      const j = await (await fetch('/raporlar/api/bireysel-hizalama',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const s=j.summary;
      const overC = s.overall_alignment_pct>=70?'#10b981':s.overall_alignment_pct>=40?'#f59e0b':'#dc2626';
      document.getElementById('summary').innerHTML=[
        stat('Genel Hizalama','%'+s.overall_alignment_pct,overC,'raporlar_bireysel_hizalama.genel_hizalama'),
        stat('PG\'si Olan Kullanıcı',s.users_with_pg,'#0ea5e9','raporlar_bireysel_hizalama.pg_si_olan_kullanici'),
        stat('Toplam Kullanıcı',s.total_users,'#0f172a','raporlar_bireysel_hizalama.toplam_kullanici'),
      ].join('');
      document.getElementById('tbl').innerHTML = j.users.length===0?'<tr><td colspan="5" style="padding:30px;text-align:center;color:#94a3b8;font-style:italic;">Bireysel PG\'si olan kullanıcı yok.</td></tr>':
        j.users.map(u => {
          const c = u.alignment_pct>=70?'#10b981':u.alignment_pct>=40?'#f59e0b':'#dc2626';
          return `<tr style="border-bottom:1px solid #f1f5f9;">
            <td style="padding:10px;color:#0f172a;font-weight:600;">${esc(u.name)}<div style="font-size:10.5px;color:#94a3b8;font-weight:400;">${esc(u.email)}</div></td>
            <td style="padding:10px;color:#475569;">${esc(u.department||'—')}</td>
            <td style="padding:10px;text-align:right;color:#475569;">${u.total_pgs}</td>
            <td style="padding:10px;text-align:right;color:#475569;font-weight:600;">${u.aligned_pgs}</td>
            <td style="padding:10px;text-align:right;color:${c};font-weight:700;font-size:14px;">%${u.alignment_pct}</td>
          </tr>`;
        }).join('');
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error');err.style.display='block';err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
