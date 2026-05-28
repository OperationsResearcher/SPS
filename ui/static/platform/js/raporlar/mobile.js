(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  async function load(){
    try {
      const j = await (await fetch('/raporlar/api/mobile/snapshot',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const d=j.data;
      document.getElementById('hdr-tenant').textContent = d.tenant;
      document.getElementById('hdr-user').textContent = 'Merhaba ' + d.user.split(' ')[0];
      const vColor = d.vision_score>=70?'#10b981':d.vision_score>=50?'#f59e0b':d.vision_score==null?'#94a3b8':'#dc2626';
      document.getElementById('vision-card').innerHTML = `
        <div style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;">VİZYON SKORU</div>
        <div style="font-size:42px;font-weight:800;color:${vColor};line-height:1.1;margin:8px 0;">${d.vision_score==null?'—':d.vision_score}</div>
        <div style="font-size:11px;color:#94a3b8;">${d.plan_year?'Plan yılı '+d.plan_year:''}</div>`;
      const m=d.metrics;
      const tile = (label, val, c, ico) => `
        <div style="background:${c}11;border:1px solid ${c}33;border-radius:10px;padding:14px;text-align:center;">
          <i class="fas ${ico}" style="color:${c};font-size:18px;margin-bottom:6px;"></i>
          <div style="font-size:22px;font-weight:800;color:${c};line-height:1.1;">${val}</div>
          <div style="font-size:10.5px;color:#64748b;margin-top:2px;">${esc(label)}</div>
        </div>`;
      document.getElementById('metrics').innerHTML = [
        tile('Bugün Bitiş', m.today_due, '#f59e0b', 'fa-flag-checkered'),
        tile('Geciken', m.overdue, '#dc2626', 'fa-exclamation-circle'),
        tile('7 Gün İçinde', m.upcoming_7d, '#0ea5e9', 'fa-calendar-week'),
        tile('Hedeflerim', m.my_pgs, '#8b5cf6', 'fa-bullseye'),
      ].join('');
    } catch(e){ document.getElementById('loading').style.display='none'; const er=document.getElementById('error'); er.style.display='block'; er.textContent='Hata: '+e.message; }
  }
  load();
})();
