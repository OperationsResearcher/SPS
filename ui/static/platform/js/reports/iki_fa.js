(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const stat = (l,v,c,code) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;"${code?` data-card-code="${code}"`:''}><div class="mc-stat-label" style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div><div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div></div>`;
  function donut(enabled, disabled) {
    const total = enabled + disabled || 1;
    const pct = enabled / total;
    const r = 80, cx = 100, cy = 100;
    const dash = 2 * Math.PI * r;
    const enabledDash = dash * pct;
    document.getElementById('donut').innerHTML = `
      <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#fee2e2" stroke-width="22"/>
      <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#10b981" stroke-width="22"
              stroke-dasharray="${enabledDash} ${dash}" transform="rotate(-90 ${cx} ${cy})"/>
      <text x="${cx}" y="${cy+8}" text-anchor="middle" font-size="24" font-weight="700" fill="#0f172a">%${Math.round(pct*100)}</text>`;
  }
  async function load(){
    try {
      const j = await (await fetch('/k-report/api/two-fa',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const s=j.summary;
      const pctC = s.enable_pct>=80?'#10b981':s.enable_pct>=40?'#f59e0b':'#dc2626';
      document.getElementById('summary').innerHTML=[
        stat('Toplam Kullanıcı',s.total_users,'#0f172a','raporlar_iki_fa.toplam_kullanici'),
        stat('2FA Etkin',s.totp_enabled,'#10b981','raporlar_iki_fa.2fa_etkin'),
        stat('2FA Yok',s.totp_disabled,'#dc2626','raporlar_iki_fa.2fa_yok'),
        stat('Etkinlik %','%'+s.enable_pct,pctC,'raporlar_iki_fa.etkinlik'),
      ].join('');
      donut(s.totp_enabled, s.totp_disabled);
      document.getElementById('donut-label').innerHTML = `<b>${s.totp_enabled}</b> kullanıcı 2FA etkin · <b>${s.totp_disabled}</b> etkin değil`;
      document.getElementById('admins').innerHTML = s.admins_without_2fa===0?'<div style="color:#10b981;font-size:13px;">✓ Tüm yönetici hesaplarında 2FA etkin.</div>':
        '<div style="display:grid;gap:6px;">' + j.admins_without_2fa.map(a => `
          <div style="display:flex;align-items:center;gap:10px;padding:10px 14px;background:#fef2f2;border:1px solid #fecaca;border-radius:6px;font-size:12.5px;">
            <i class="fas fa-exclamation-triangle" style="color:#dc2626;"></i>
            <div style="flex:1;">
              <div style="font-weight:600;color:#0f172a;">${esc(a.name||a.email)}</div>
              <div style="font-size:11px;color:#991b1b;">${esc(a.email)}</div>
            </div>
          </div>`).join('') + '</div>';
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error');err.style.display='block';err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
