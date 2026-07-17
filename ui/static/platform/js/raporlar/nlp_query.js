(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

  function renderResult(j){
    const el = document.getElementById('result');
    if(!j.success){ el.innerHTML = '<div style="color:#dc2626;padding:30px;text-align:center;">Hata: '+esc(j.message||'')+'</div>'; return; }
    let html = `<div style="font-size:11px;color:#7c3aed;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px;">${esc(j.summary||'')}</div>`;
    if(j.type === 'table'){
      html += '<table style="width:100%;border-collapse:collapse;font-size:12.5px;"><thead><tr style="background:#f8fafc;border-bottom:2px solid #e2e8f0;">';
      (j.columns||[]).forEach(c => html += `<th style="padding:8px 10px;text-align:left;color:#475569;font-weight:600;">${esc(c)}</th>`);
      html += '</tr></thead><tbody>';
      (j.rows||[]).forEach(row => {
        html += '<tr style="border-bottom:1px solid #f1f5f9;">';
        row.forEach(v => html += `<td style="padding:8px 10px;color:#0f172a;">${esc(v)}</td>`);
        html += '</tr>';
      });
      html += '</tbody></table>';
      if(!j.rows || j.rows.length===0) html += '<div style="text-align:center;padding:30px;color:#94a3b8;font-style:italic;">Veri bulunamadı.</div>';
    } else if(j.type === 'text'){
      html += `<div style="font-size:14px;color:#0f172a;line-height:1.7;background:#faf5ff;padding:16px;border-radius:8px;border-left:4px solid #7c3aed;">${esc(j.text)}</div>`;
    }
    el.innerHTML = html;
  }

  async function runPattern(pid){
    document.getElementById('result').innerHTML = '<div style="text-align:center;padding:60px;color:#64748b;"><i class="fas fa-spinner fa-spin" style="font-size:20px;"></i></div>';
    const r = await fetch('/reports/api/nlp-query?pattern_id=' + encodeURIComponent(pid), {credentials:'same-origin'});
    const j = await r.json();
    renderResult(j);
  }

  async function runFree(){
    const q = document.getElementById('free-q').value.trim();
    if(!q){ Swal.fire({icon:'info',title:'Soru gerekli',text:'Lütfen bir soru yazın.',timer:1800,showConfirmButton:false}); return; }
    document.getElementById('result').innerHTML = '<div style="text-align:center;padding:60px;color:#64748b;"><i class="fas fa-spinner fa-spin" style="font-size:20px;"></i> AI düşünüyor…</div>';
    const r = await fetch('/reports/api/nlp-query?query=' + encodeURIComponent(q), {credentials:'same-origin'});
    const j = await r.json();
    renderResult(j);
  }

  async function loadPatterns(){
    const r = await fetch('/k-report/api/nlp-query/patterns',{credentials:'same-origin'});
    const j = await r.json();
    if(!j.success) return;
    document.getElementById('patterns').innerHTML = j.patterns.map(p => `
      <button data-pid="${p.id}" style="text-align:left;padding:10px 12px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;cursor:pointer;font-size:12.5px;color:#0f172a;display:flex;align-items:center;gap:10px;transition:background .15s;"
        onmouseover="this.style.background='#eef2ff'" onmouseout="this.style.background='#f8fafc'">
        <i class="fas ${p.icon}" style="color:#7c3aed;width:18px;text-align:center;"></i>
        <span>${esc(p.label)}</span>
      </button>`).join('');
    document.querySelectorAll('#patterns button').forEach(b => {
      b.addEventListener('click', () => runPattern(b.getAttribute('data-pid')));
    });
  }

  document.getElementById('ask-btn').addEventListener('click', runFree);
  loadPatterns();
})();
