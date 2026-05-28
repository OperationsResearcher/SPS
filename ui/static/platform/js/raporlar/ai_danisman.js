(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const ACTION_COLOR = {refocus:'#0ea5e9',sunset:'#dc2626',accelerate:'#10b981',new_initiative:'#6366f1',risk_mitigation:'#f59e0b'};
  const ACTION_LABEL = {refocus:'Yeniden Odakla',sunset:'Sonlandır',accelerate:'Hızlandır',new_initiative:'Yeni Girişim',risk_mitigation:'Risk Azalt'};
  async function load(){
    try {
      const j = await (await fetch('/raporlar/api/ai-danisman',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const recs = (j.data && j.data.recommendations) || j.data?.results || [];
      const source = j.data?.source || 'unknown';
      if(recs.length===0){
        document.getElementById('recommendations').innerHTML = '<div style="background:#fffbeb;border:1px solid #fde68a;color:#92400e;padding:14px;border-radius:8px;font-size:13px;"><i class="fas fa-info-circle"></i> AI henüz yeterli veri bulamadı ya da sistem yeterince olgunlaşmamış. Birkaç dönem veri toplandıktan sonra tekrar deneyin.</div>';
        return;
      }
      let html = `<div style="background:#eef2ff;border:1px solid #c7d2fe;color:#4338ca;padding:10px 14px;border-radius:8px;font-size:12px;margin-bottom:14px;"><i class="fas fa-info-circle"></i> ${recs.length} öneri · Kaynak: <b>${esc(source)}</b></div>`;
      html += '<div style="display:grid;gap:12px;">';
      recs.forEach(r => {
        const col = ACTION_COLOR[r.action] || '#64748b';
        const lbl = ACTION_LABEL[r.action] || r.action || '?';
        html += `<div style="background:#fff;border:1px solid #e2e8f0;border-left:4px solid ${col};border-radius:10px;padding:16px;">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;flex-wrap:wrap;gap:8px;">
            <div style="font-size:14px;font-weight:700;color:#0f172a;">${esc(r.title||r.strategy_code||r.summary||'(başlık yok)')}</div>
            <span style="background:${col};color:#fff;font-size:11px;font-weight:700;padding:3px 10px;border-radius:10px;">${esc(lbl)}</span>
          </div>
          <div style="font-size:12.5px;color:#475569;line-height:1.55;">${esc(r.rationale||r.reasoning||r.message||'')}</div>
          ${r.confidence?'<div style="margin-top:6px;font-size:11px;color:#94a3b8;">Güven: %'+Math.round(r.confidence*100)+'</div>':''}
        </div>`;
      });
      html += '</div>';
      document.getElementById('recommendations').innerHTML = html;
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error');err.style.display='block';err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
