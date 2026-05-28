(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const stat = (l,v,c) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;"><div style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div><div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div></div>`;
  const bucketColors = {
    "Sürdürülebilir Rekabet Avantajı":"#10b981",
    "Kullanılmayan Avantaj":"#f59e0b",
    "Geçici Rekabet Avantajı":"#0ea5e9",
    "Rekabet Paritesi":"#64748b",
    "Rekabetçi Dezavantaj":"#dc2626"
  };
  async function load(){
    try {
      const j = await (await fetch('/raporlar/api/vrio-portfoy',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const s = j.summary;
      document.getElementById('summary').innerHTML = [
        stat('Toplam Kaynak', s.total, '#0f172a'),
        stat('Sürdürülebilir', s.sustainable, '#10b981'),
        stat('Geçici', s.temporary, '#0ea5e9'),
        stat('Kullanılmayan', s.unused, '#f59e0b'),
        stat('Dezavantaj', s.disadvantage, '#dc2626'),
      ].join('');
      document.getElementById('buckets').innerHTML = Object.entries(j.buckets).map(([name,items]) => {
        const col = bucketColors[name] || '#64748b';
        return `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:16px;border-top:4px solid ${col};">
          <h3 style="font-size:13px;font-weight:700;color:${col};margin:0 0 10px;">${esc(name)} <span style="background:${col};color:#fff;font-size:11px;padding:2px 8px;border-radius:10px;margin-left:6px;">${items.length}</span></h3>
          ${items.length===0?'<div style="font-size:12px;color:#94a3b8;font-style:italic;">Boş</div>':items.map(r=>`
            <div style="padding:8px 10px;border:1px solid #e2e8f0;border-radius:6px;margin-bottom:6px;font-size:12.5px;">
              <div style="font-weight:600;color:#0f172a;">${esc(r.name)}</div>
              <div style="font-size:10.5px;color:#64748b;margin-top:2px;">
                <span style="color:${r.v?'#10b981':'#94a3b8'};font-weight:600;">V${r.v?'✓':'✗'}</span>
                <span style="color:${r.r?'#10b981':'#94a3b8'};font-weight:600;margin-left:4px;">R${r.r?'✓':'✗'}</span>
                <span style="color:${r.i?'#10b981':'#94a3b8'};font-weight:600;margin-left:4px;">I${r.i?'✓':'✗'}</span>
                <span style="color:${r.o?'#10b981':'#94a3b8'};font-weight:600;margin-left:4px;">O${r.o?'✓':'✗'}</span>
                ${r.category?'<span style="color:#94a3b8;margin-left:6px;">'+esc(r.category)+'</span>':''}
              </div>
            </div>`).join('')}
        </div>`;
      }).join('');
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error');err.style.display='block';err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
