(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  async function load(){
    try {
      const j = await (await fetch('/reports/api/strategy-story',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const d=j.data;
      document.getElementById('header').innerHTML = `
        <div style="font-size:11px;color:#5b21b6;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">STRATEJİK YOLCULUK</div>
        <div style="font-size:22px;font-weight:800;color:#0f172a;">${esc(d.tenant_name)}</div>
        <div style="font-size:13px;color:#64748b;margin-top:4px;">${esc(d.year_range)} dönemi · ${d.snapshots.length} yıllık veri</div>`;
      document.getElementById('narrative').textContent = d.narrative;
      document.getElementById('snapshots').innerHTML = '<table style="width:100%;border-collapse:collapse;font-size:12px;"><thead><tr style="background:#f8fafc;border-bottom:2px solid #e2e8f0;"><th style="padding:8px;text-align:left;">Yıl</th><th style="padding:8px;text-align:right;">Strateji</th><th style="padding:8px;text-align:right;">Süreç</th><th style="padding:8px;text-align:right;">PG</th><th style="padding:8px;text-align:right;">Ölçüm</th></tr></thead><tbody>' +
        d.snapshots.map(s => `<tr style="border-bottom:1px solid #f1f5f9;">
          <td style="padding:8px;color:#0f172a;font-weight:700;">${s.year}</td>
          <td style="padding:8px;text-align:right;">${s.strategy_count}</td>
          <td style="padding:8px;text-align:right;">${s.process_count}</td>
          <td style="padding:8px;text-align:right;">${s.kpi_count}</td>
          <td style="padding:8px;text-align:right;">${s.measurement_count.toLocaleString('tr-TR')}</td>
        </tr>`).join('') + '</tbody></table>';
      document.getElementById('highlights').innerHTML = d.highlights.length===0?'<div style="color:#10b981;font-size:12.5px;">✓ Yapısal değişim yok — istikrarlı plan.</div>':
        d.highlights.map(h => `
          <div style="padding:10px 12px;background:#f5f3ff;border-left:3px solid #7c3aed;border-radius:0 6px 6px 0;margin-bottom:6px;font-size:12px;">
            <div style="font-weight:700;color:#5b21b6;">${h.year}</div>
            <div style="color:#475569;margin-top:2px;">${esc(h.change)}</div>
          </div>`).join('');
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error');err.style.display='block';err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
