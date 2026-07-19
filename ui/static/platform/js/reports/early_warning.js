(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const stat = (l,v,c) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;"><div style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div><div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div></div>`;
  async function load(){
    try {
      const j = await (await fetch('/k-report/api/early-warning',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const s=j.summary;
      document.getElementById('summary').innerHTML=[
        stat('Kontrol Edilen PG',s.total_kpis_checked,'#0f172a'),
        stat('Uyarı Sayısı',s.warnings_count,s.warnings_count>0?'#dc2626':'#10b981'),
        stat('Yüksek Öncelik',s.high_severity,'#dc2626'),
      ].join('');
      const warnings = j.warnings;
      if(warnings.length===0){
        document.getElementById('warnings').innerHTML = '<div style="color:#10b981;font-size:13px;padding:12px;background:#ecfdf5;border-radius:6px;"><i class="fas fa-check-circle"></i> Şu an erken uyarı yok — tüm PG\'ler kabul edilebilir performansta.</div>';
        return;
      }
      document.getElementById('warnings').innerHTML = '<div style="display:grid;gap:8px;">' + warnings.map(w => {
        const c = w.severity==='high'?'#dc2626':'#f59e0b';
        return `<div style="border-left:4px solid ${c};background:#fef2f2;padding:12px 14px;border-radius:0 6px 6px 0;font-size:12.5px;">
          <div style="display:flex;justify-content:space-between;align-items:start;flex-wrap:wrap;gap:8px;">
            <div>
              <div style="font-weight:600;color:#0f172a;">${esc(w.kpi_code||'')} ${esc(w.kpi_name||'')}</div>
              <div style="font-size:11px;color:#64748b;margin-top:2px;">${esc(w.process_name||'?')}</div>
            </div>
            <span style="background:${c};color:#fff;font-size:10.5px;font-weight:700;padding:2px 8px;border-radius:8px;">${w.severity==='high'?'YÜKSEK':'ORTA'}</span>
          </div>
          <div style="font-size:11px;color:#475569;margin-top:6px;">Son 3 başarı puanı: <b>${w.last_scores.map(s=>'%'+s).join(' → ')}</b></div>
        </div>`;
      }).join('') + '</div>';
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error');err.style.display='block';err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
