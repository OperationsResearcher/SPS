(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const statCard = (l,v,c,code) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;"${code?` data-card-code="${code}"`:''}>
    <div class="mc-stat-label" style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div>
    <div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div></div>`;
  async function load(){
    try {
      const j = await (await fetch('/k-report/api/executive-leadership',{credentials:'same-origin'})).json();
      if (!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const s = j.summary;
      if (s.note) {
        const note = document.getElementById('note');
        note.style.display='block';
        note.innerHTML = '<i class="fas fa-info-circle"></i> '+esc(s.note);
      }
      document.getElementById('summary').innerHTML = [
        statCard('Yönetici Sayısı', s.total_leaders, '#0f172a', 'raporlar_yonetici_liderlik.yonetici_sayisi'),
        s.has_leader_data ? statCard('Skor Hesaplanan', s.with_score || 0, '#0ea5e9') : '',
        s.has_leader_data ? statCard('Ortalama Skor', s.avg_score_overall != null ? s.avg_score_overall : '—', '#10b981') : '',
      ].filter(Boolean).join('');
      document.getElementById('tbl').innerHTML = j.leaders.map(l => {
        const scoreColor = l.avg_process_score == null ? '#94a3b8' :
          l.avg_process_score >= 70 ? '#10b981' : l.avg_process_score >= 50 ? '#f59e0b' : '#dc2626';
        return `<tr style="border-bottom:1px solid #f1f5f9;">
          <td style="padding:10px;color:#0f172a;font-weight:600;">${esc(l.name)}<div style="font-size:10.5px;color:#94a3b8;font-weight:400;">${esc(l.email)}</div></td>
          <td style="padding:10px;color:#475569;">${esc(l.department || '—')}</td>
          <td style="padding:10px;text-align:right;color:#475569;font-weight:600;">${l.led_process_count}</td>
          <td style="padding:10px;text-align:right;color:${scoreColor};font-weight:700;font-size:14px;">${l.avg_process_score != null ? l.avg_process_score : '—'}</td>
        </tr>`;
      }).join('') || '<tr><td colspan="4" style="padding:20px;text-align:center;color:#94a3b8;font-style:italic;">Yönetici verisi yok.</td></tr>';
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err = document.getElementById('error'); err.style.display='block'; err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
