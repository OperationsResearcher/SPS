(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const stat = (l,v,c,code) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;"${code?` data-card-code="${code}"`:''}><div class="mc-stat-label" style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div><div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div></div>`;
  async function load(){
    try {
      const j = await (await fetch('/k-report/api/ai-coach',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const d = j.data;
      document.getElementById('summary').innerHTML=[
        stat('Analiz Edilen Strateji',d.strategies_analyzed,'#0f172a','raporlar_ai_coach.analiz_edilen_strateji'),
        stat('En Düşük 3',d.bottom3.length,'#dc2626','raporlar_ai_coach.en_dusuk_3'),
      ].join('');
      document.getElementById('bottom3').innerHTML = d.bottom3.length===0?'<div style="color:#10b981;font-size:13px;">✓ Tüm stratejiler dengeli performans gösteriyor.</div>':
        '<div style="display:grid;gap:8px;">' + d.bottom3.map(s => {
          const c = s.score>=50?'#f59e0b':'#dc2626';
          return `<div style="display:flex;align-items:center;gap:12px;padding:10px 14px;background:#fef2f2;border:1px solid #fecaca;border-radius:6px;">
            <div style="width:50px;height:50px;border-radius:8px;background:${c};color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;flex-shrink:0;">${s.score}</div>
            <div><div style="font-weight:600;color:#0f172a;font-size:13px;">${esc(s.code||'')} ${esc(s.title||'')}</div></div>
          </div>`;
        }).join('') + '</div>';
      document.getElementById('advice').textContent = d.coach_advice || '(öneri üretilemedi)';
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error');err.style.display='block';err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
