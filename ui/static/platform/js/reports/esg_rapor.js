document.getElementById('dl').addEventListener('click', async()=>{
  const b=document.getElementById('dl'); const o=b.innerHTML; b.disabled=true; b.innerHTML='<i class="fas fa-spinner fa-spin"></i> Üretiliyor…';
  try {
    const r=await fetch('/k-report/api/esg-report/generate',{credentials:'same-origin'});
    if(!r.ok) throw new Error('HTTP '+r.status);
    const blob=await r.blob(); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url;
    const cd=r.headers.get('Content-Disposition')||''; const m=cd.match(/filename="?([^";]+)"?/);
    a.download = m ? m[1] : 'ESG_Raporu.pdf'; a.click(); URL.revokeObjectURL(url);
    b.innerHTML='<i class="fas fa-check"></i> İndirildi'; setTimeout(()=>{b.innerHTML=o; b.disabled=false;}, 2500);
  } catch(e){ Swal.fire({icon:'error',title:'Hata',text:e.message}); b.innerHTML=o; b.disabled=false; }
});
