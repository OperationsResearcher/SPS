(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const stat = (l,v,c,code) => `<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px;"${code?` data-card-code="${code}"`:''}><div class="mc-stat-label" style="font-size:10.5px;color:#64748b;font-weight:600;text-transform:uppercase;margin-bottom:4px;">${esc(l)}</div><div style="font-size:22px;font-weight:700;color:${c};">${esc(v)}</div></div>`;
  async function load(){
    try {
      const j = await (await fetch('/k-report/api/carbon-trend',{credentials:'same-origin'})).json();
      if(!j.success) throw new Error(j.message);
      document.getElementById('loading').style.display='none';
      document.getElementById('content').style.display='block';
      const s=j.summary;
      const delta = s.latest_total - s.first_total;
      const deltaC = delta<=0?'#10b981':'#dc2626';
      document.getElementById('summary').innerHTML=[
        stat('Metrik Sayısı',s.metrics_count,'#0f172a','raporlar_carbon_trend.metrik_sayisi'),
        stat('Veri Yılı',s.years_with_data,'#0ea5e9','raporlar_carbon_trend.veri_yili'),
        stat('Son Yıl Toplam',s.latest_total.toFixed(1)+' tCO₂e','#10b981','raporlar_carbon_trend.son_yil_toplam'),
        stat('İlk Yıla Göre',(delta>0?'+':'')+delta.toFixed(1),deltaC,'raporlar_carbon_trend.ilk_yila_gore'),
      ].join('');
      if(j.trend.length===0){
        document.getElementById('empty-note').style.display='block';
        document.getElementById('chart').innerHTML='';
        return;
      }
      const w=900, h=320, padL=50, padR=20, padT=20, padB=40;
      const maxV = Math.max(...j.trend.map(t=>t.total), 1);
      const colors = {scope1:'#dc2626',scope2:'#f59e0b',scope3:'#0ea5e9'};
      const barW = (w-padL-padR)/j.trend.length - 6;
      let html = `<svg width="100%" height="${h}" viewBox="0 0 ${w} ${h}" style="overflow:visible;">`;
      html += `<line x1="${padL}" y1="${h-padB}" x2="${w-padR}" y2="${h-padB}" stroke="#cbd5e1"/>`;
      html += `<line x1="${padL}" y1="${padT}" x2="${padL}" y2="${h-padB}" stroke="#cbd5e1"/>`;
      j.trend.forEach((t,i) => {
        const x = padL + i * ((w-padL-padR)/j.trend.length) + 3;
        let yBase = h-padB;
        ['scope1','scope2','scope3'].forEach(sc => {
          const v = t[sc] || 0;
          if(v>0){
            const ht = (v/maxV) * (h-padT-padB);
            yBase -= ht;
            html += `<rect x="${x}" y="${yBase}" width="${barW}" height="${ht}" fill="${colors[sc]}" opacity="0.85"><title>${sc.toUpperCase()}: ${v.toFixed(1)} tCO₂e</title></rect>`;
          }
        });
        html += `<text x="${x+barW/2}" y="${h-padB+15}" font-size="11" fill="#64748b" text-anchor="middle">${t.year}</text>`;
        html += `<text x="${x+barW/2}" y="${yBase-4}" font-size="10" fill="#0f172a" text-anchor="middle" font-weight="600">${t.total.toFixed(1)}</text>`;
      });
      html += '</svg>';
      document.getElementById('chart').innerHTML = html;
    } catch(e){
      document.getElementById('loading').style.display='none';
      const err=document.getElementById('error');err.style.display='block';err.textContent='Hata: '+e.message;
    }
  }
  load();
})();
