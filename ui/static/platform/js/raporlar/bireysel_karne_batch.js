(function(){
  async function load(){
    try {
      const j = await (await fetch('/raporlar/api/bireysel-karne-batch/preview',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const p=j.preview;
      document.getElementById('title').textContent = `${p.users_with_pg} kişi için karne (${p.total_users} aktif çalışandan)`;
      document.getElementById('meta').textContent = `Format: ${p.format} · Tahmini boyut: ~${p.estimated_size_mb} MB`;
    } catch(e){ document.getElementById('loading').style.display='none'; const er=document.getElementById('error'); er.style.display='block'; er.textContent='Hata: '+e.message; }
  }
  document.getElementById('dl').addEventListener('click', async()=>{
    const b=document.getElementById('dl'); const o=b.innerHTML; b.disabled=true; b.innerHTML='<i class="fas fa-spinner fa-spin"></i> ZIP hazırlanıyor (10-60sn)…';
    try {
      const r=await fetch('/raporlar/api/bireysel-karne-batch/generate',{credentials:'same-origin'});
      if(!r.ok) throw new Error('HTTP '+r.status);
      const blob=await r.blob(); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url;
      const cd=r.headers.get('Content-Disposition')||''; const m=cd.match(/filename="?([^";]+)"?/);
      a.download = m ? m[1] : 'bireysel_karne_batch.zip'; a.click(); URL.revokeObjectURL(url);
      b.innerHTML='<i class="fas fa-check"></i> İndirildi'; setTimeout(()=>{b.innerHTML=o; b.disabled=false;}, 2500);
    } catch(e){ Swal.fire({icon:'error',title:'Hata',text:e.message}); b.innerHTML=o; b.disabled=false; }
  });
  load();
})();
