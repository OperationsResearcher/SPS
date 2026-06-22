(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const stat = (l,v,c,code) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;"${code?` data-card-code="${code}"`:''}><div class="mc-stat-label" style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div><div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div></div>`;
  async function load(){
    try {
      const j = await (await fetch('/raporlar/api/quarterly-review',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const d=j.data;
      document.getElementById('header').innerHTML = `
        <div style="font-size:11px;color:#065f46;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">${d.year} ÇEYREK ${d.quarter}</div>
        <div style="font-size:20px;font-weight:800;color:#0f172a;">Çeyreklik Review Toplantısı</div>
        <div style="font-size:12.5px;color:#64748b;margin-top:4px;">${esc(d.period_start)} – ${esc(d.period_end)}${d.plan_year?' · Plan yılı '+d.plan_year:''}</div>`;
      document.getElementById('metrics').innerHTML = [
        stat('Ölçüm Hacmi (Q)', d.metrics.measurements_q.toLocaleString('tr-TR'), '#16a34a', 'raporlar_quarterly_review.olcum_hacmi_q'),
        stat('Yeni Stratejik Girişim', d.metrics.new_initiatives, '#0ea5e9', 'raporlar_quarterly_review.yeni_stratejik_girisim'),
        stat('Tamamlanan Stratejik Girişim', d.metrics.completed_initiatives, '#10b981', 'raporlar_quarterly_review.tamamlanan_stratejik_girisim'),
      ].join('');
      document.getElementById('ai-text').textContent = d.ai_summary;
      document.getElementById('agenda').innerHTML = '<ol style="margin:0;padding-left:20px;font-size:12.5px;color:#0f172a;line-height:1.7;">' +
        d.agenda.map(a => '<li style="margin-bottom:6px;">' + esc(a.replace(/^\d+\.\s*/,'')) + '</li>').join('') + '</ol>';
      document.getElementById('prep').innerHTML = '<ul style="margin:0;padding-left:20px;font-size:12.5px;color:#475569;line-height:1.7;">' +
        d.prep_questions.map(q => '<li style="margin-bottom:6px;">' + esc(q) + '</li>').join('') + '</ul>';
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error');err.style.display='block';err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
