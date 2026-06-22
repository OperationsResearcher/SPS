(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  async function load(){
    try {
      const j = await (await fetch('/reports/api/investor-presentation/preview',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const p=j.preview;
      document.getElementById('title').textContent = `${p.tenant_name} — Yatırımcı Sunumu`;
      document.getElementById('meta').textContent = `${p.slide_count} slayt · ${p.format}`;
      document.getElementById('slides').innerHTML = p.slides.map(s => `
        <div style="display:flex;align-items:center;gap:12px;padding:9px 14px;border:1px solid #e2e8f0;border-radius:6px;background:#f0f9ff;">
          <div style="width:30px;height:30px;border-radius:50%;background:#0ea5e9;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:11px;flex-shrink:0;">${s.no}</div>
          <div style="flex:1;"><div style="font-weight:600;color:#0f172a;font-size:13px;">${esc(s.title)}</div><div style="font-size:11px;color:#64748b;">${esc(s.content)}</div></div>
        </div>`).join('');
    } catch(e){ document.getElementById('loading').style.display='none'; const er=document.getElementById('error'); er.style.display='block'; er.textContent='Hata: '+e.message; }
  }
  document.getElementById('dl').addEventListener('click', async()=>{
    const b=document.getElementById('dl'); const o=b.innerHTML; b.disabled=true; b.innerHTML='<i class="fas fa-spinner fa-spin"></i> Üretiliyor…';
    try {
      const r=await fetch('/reports/api/investor-presentation/generate',{credentials:'same-origin'});
      if(!r.ok) throw new Error('HTTP '+r.status);
      const blob=await r.blob(); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url;
      const cd=r.headers.get('Content-Disposition')||''; const m=cd.match(/filename="?([^";]+)"?/);
      a.download = m ? m[1] : 'yatirimci_sunum.pptx'; a.click(); URL.revokeObjectURL(url);
      b.innerHTML='<i class="fas fa-check"></i> İndirildi'; setTimeout(()=>{b.innerHTML=o; b.disabled=false;}, 2500);
    } catch(e){ Swal.fire({icon:'error',title:'Hata',text:e.message}); b.innerHTML=o; b.disabled=false; }
  });
  load();
})();
