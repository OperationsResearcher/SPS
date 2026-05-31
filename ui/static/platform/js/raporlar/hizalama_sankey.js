/* Stratejik Akış Haritası — 5 katman, tooltip, hover vurgu, drill-down, yıl + strateji filtresi */
(function(){
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

  const yearSel  = document.getElementById('hs-year-select');
  const stratSel = document.getElementById('hs-strat-select');
  const svg      = document.getElementById('hs-sankey');
  const tooltip  = document.getElementById('hs-tooltip');
  const colHeadersEl = document.getElementById('hs-col-headers');

  let currentData = null;
  let activeStrategyFilter = 'all';

  function statCard(label, value, color, sub) {
    return `<div class="mc-card" style="padding:12px 14px;">
      <div style="font-size:10.5px; color:#64748b; font-weight:600; text-transform:uppercase;">${esc(label)}</div>
      <div style="font-size:22px; font-weight:800; color:${color}; margin-top:3px;">${esc(value)}</div>
      ${sub ? `<div style="font-size:11px; color:#94a3b8;">${esc(sub)}</div>` : ''}
    </div>`;
  }

  // Etiketi maksimum char/satır göre kelime kıracak şekilde böl
  function wrapLines(text, maxChars) {
    const words = String(text || '').split(/\s+/);
    const lines = [];
    let cur = '';
    for (const w of words) {
      if (!cur) { cur = w; continue; }
      if ((cur + ' ' + w).length > maxChars) { lines.push(cur); cur = w; }
      else cur += ' ' + w;
    }
    if (cur) lines.push(cur);
    return lines.slice(0, 3); // maks 3 satır
  }

  function showTooltip(html, x, y) {
    tooltip.innerHTML = html;
    tooltip.style.display = 'block';
    const rect = tooltip.getBoundingClientRect();
    let tx = x + 14, ty = y + 14;
    if (tx + rect.width > window.innerWidth - 10)  tx = x - rect.width - 14;
    if (ty + rect.height > window.innerHeight - 10) ty = y - rect.height - 14;
    tooltip.style.left = tx + 'px';
    tooltip.style.top  = ty + 'px';
  }
  function hideTooltip() { tooltip.style.display = 'none'; }

  function drawSankey(nodes, links, levelLabels) {
    svg.innerHTML = '';
    const width  = svg.clientWidth || 1100;
    const height = 780;
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);

    const levels = [0, 1, 2, 3, 4];
    const colWidth = 165;
    const totalWidth = colWidth * levels.length;
    const gapX = (width - totalWidth) / (levels.length - 1 || 1);
    const xPos = {};
    levels.forEach(l => { xPos[l] = l * (colWidth + gapX); });

    // Sütun başlıkları (HTML grid'te)
    colHeadersEl.innerHTML = levelLabels.map((lbl, i) => {
      const cols = ['#0f172a','#4f46e5','#8b5cf6','#10b981','#0ea5e9'];
      return `<div style="text-align:center; padding:6px; background:${cols[i]}10; border-bottom:2px solid ${cols[i]}; color:${cols[i]}; font-weight:700; font-size:12px;">${esc(lbl)}</div>`;
    }).join('');

    // Filtre uygula
    const filterFn = (n) => activeStrategyFilter === 'all' || n.id === 'vision'
      || (n.strategy_key && n.strategy_key === activeStrategyFilter) || n.id === activeStrategyFilter;
    const visibleNodes = nodes.filter(filterFn);
    const visibleNodeIds = new Set(visibleNodes.map(n => n.id));

    // Her seviyedeki node'lar
    const byLevel = {};
    levels.forEach(l => byLevel[l] = visibleNodes.filter(n => n.level === l));
    const yMap = {};
    levels.forEach(l => {
      const arr = byLevel[l];
      const padTop = 14, padBot = 14;
      const usableH = height - padTop - padBot;
      const slotH = usableH / Math.max(arr.length, 1);
      arr.forEach((n, i) => {
        const boxH = Math.max(slotH - 8, 30);
        yMap[n.id] = {
          x: xPos[n.level],
          y: padTop + i * slotH + slotH / 2,
          w: colWidth,
          h: boxH,
        };
      });
    });

    // Linkleri çiz (önce arkada)
    const linkPaths = [];
    links.forEach(lk => {
      const s = nodes[lk.source];
      const t = nodes[lk.target];
      if (!s || !t || !visibleNodeIds.has(s.id) || !visibleNodeIds.has(t.id)) return;
      const sp = yMap[s.id], tp = yMap[t.id];
      if (!sp || !tp) return;
      const sx = sp.x + sp.w, sy = sp.y;
      const tx = tp.x, ty = tp.y;
      const mx = (sx + tx) / 2;
      const strokeW = Math.max(1.5, Math.min(lk.value * 0.6, 20));
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', `M${sx},${sy} C${mx},${sy} ${mx},${ty} ${tx},${ty}`);
      path.setAttribute('stroke', s.color || '#94a3b8');
      path.setAttribute('stroke-width', strokeW);
      path.setAttribute('fill', 'none');
      path.setAttribute('opacity', '0.32');
      path.setAttribute('data-strategy', lk.strategy_key || '');
      path.classList.add('hs-link');
      svg.appendChild(path);
      linkPaths.push({el: path, strategy: lk.strategy_key, sourceId: s.id, targetId: t.id});
    });

    // Node'lar (kutu + wrap'li label + skor pill)
    visibleNodes.forEach(n => {
      const p = yMap[n.id]; if (!p) return;
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.classList.add('hs-node');
      g.setAttribute('data-id', n.id);
      g.setAttribute('data-strategy', n.strategy_key || n.id);
      g.style.cursor = n.url ? 'pointer' : 'default';

      const lineCount = Math.max(1, Math.floor((p.h - 18) / 12));
      const lines = wrapLines(n.label, 22).slice(0, lineCount);
      const scoreBadge = (n.score != null && n.score > 0)
        ? `<rect x="${p.x + p.w - 42}" y="${p.y - p.h/2 + 4}" width="38" height="16" rx="8" fill="rgba(255,255,255,0.9)"/>
           <text x="${p.x + p.w - 23}" y="${p.y - p.h/2 + 15}" font-size="10" font-weight="700" fill="${n.color}" text-anchor="middle">%${Math.round(n.score)}</text>`
        : '';
      const weightBadge = (n.weight != null && n.weight > 0)
        ? `<text x="${p.x + 6}" y="${p.y - p.h/2 + 14}" font-size="9.5" fill="#fff" opacity="0.85">w:${n.weight}</text>`
        : '';

      // Yazı: ortalanmış 1-3 satır
      const startY = p.y - ((lines.length - 1) * 6) + 4;
      const textLines = lines.map((ln, i) => `<text x="${p.x + p.w/2}" y="${startY + i*12}" font-size="10.5" font-weight="600" fill="#fff" text-anchor="middle">${esc(ln)}</text>`).join('');

      g.innerHTML = `
        <rect x="${p.x}" y="${p.y - p.h/2}" width="${p.w}" height="${p.h}" rx="6" fill="${n.color}" opacity="0.96"/>
        ${scoreBadge}
        ${weightBadge}
        ${textLines}`;
      svg.appendChild(g);

      // Olaylar
      g.addEventListener('mouseenter', (e) => {
        const tipParts = [
          `<b>${esc(n.label)}</b>`,
          n.score != null ? `Skor: <b>%${n.score}</b>` : '',
          n.weight != null ? `K-Vektör ağırlık: <b>${n.weight}</b>` : '',
          n.url ? `<span style="color:#a5b4fc;">↗ tıkla detaya git</span>` : '',
        ].filter(Boolean).join('<br>');
        showTooltip(tipParts, e.clientX, e.clientY);
        // Vurgu: sadece bu node'un strateji_key'ine ait olanlar belirgin
        const key = n.strategy_key || n.id;
        linkPaths.forEach(lp => {
          lp.el.setAttribute('opacity', (lp.strategy === key || lp.sourceId === n.id || lp.targetId === n.id) ? '0.85' : '0.06');
        });
        svg.querySelectorAll('.hs-node rect').forEach(rect => {
          const nodeG = rect.parentNode;
          const nkey = nodeG.getAttribute('data-strategy');
          const nid  = nodeG.getAttribute('data-id');
          const match = nkey === key || nid === n.id || nid === 'vision';
          rect.setAttribute('opacity', match ? '0.96' : '0.22');
        });
      });
      g.addEventListener('mousemove', (e) => { tooltip.style.left = (e.clientX + 14) + 'px'; tooltip.style.top = (e.clientY + 14) + 'px'; });
      g.addEventListener('mouseleave', () => {
        hideTooltip();
        linkPaths.forEach(lp => lp.el.setAttribute('opacity', '0.32'));
        svg.querySelectorAll('.hs-node rect').forEach(rect => rect.setAttribute('opacity', '0.96'));
      });
      if (n.url) g.addEventListener('click', () => { window.location.href = n.url; });
    });
  }

  function fillStrategyFilter(nodes) {
    const strats = nodes.filter(n => n.level === 1);
    stratSel.innerHTML = '<option value="all">Tümü</option>' +
      strats.map(s => `<option value="${esc(s.id)}">${esc(s.label.substring(0, 36))}</option>`).join('');
  }

  function renderSummary(d) {
    const s = d.summary;
    document.getElementById('hs-summary').innerHTML = [
      statCard('Ana Strateji',  s.strategy_nodes,     '#4f46e5'),
      statCard('Alt Strateji',  s.sub_strategy_nodes, '#8b5cf6'),
      statCard('Süreç',         s.process_nodes,      '#10b981'),
      statCard('PG',            s.pg_nodes,           '#0ea5e9'),
      statCard('Bağlantı',      s.total_links,        '#6366f1'),
      statCard('Hizalanmamış',  s.unaligned_processes, s.unaligned_processes > 0 ? '#dc2626' : '#10b981', 'süreç'),
    ].join('');
  }

  function renderUnaligned(d) {
    const wrap = document.getElementById('hs-unaligned');
    const list = document.getElementById('hs-unaligned-list');
    const items = (d.unaligned && d.unaligned.processes) || [];
    if (!items.length) { wrap.style.display = 'none'; return; }
    wrap.style.display = 'block';
    list.innerHTML = items.map(p => `
      <a href="/process/${p.id}/karne" style="background:#fff; border:1px solid #fde68a; padding:3px 8px; border-radius:4px; text-decoration:none; color:#92400e;">
        ${p.code ? `<b>${esc(p.code)}</b> · ` : ''}${esc(p.name)}
      </a>`).join('');
  }

  async function load() {
    try {
      document.getElementById('hs-loading').style.display = '';
      document.getElementById('hs-content').style.display = 'none';
      document.getElementById('hs-error').style.display = 'none';
      const y = yearSel?.value || '';
      const url = '/raporlar/api/hizalama-sankey' + (y ? '?year=' + encodeURIComponent(y) : '');
      const j = await (await fetch(url, {credentials:'same-origin'})).json();
      if (!j.success) throw new Error(j.message || 'Veri alınamadı');
      currentData = j;
      document.getElementById('hs-loading').style.display = 'none';
      document.getElementById('hs-content').style.display = '';
      renderSummary(j);
      renderUnaligned(j);
      fillStrategyFilter(j.nodes);
      if (j.summary.strategy_nodes === 0) {
        document.getElementById('hs-empty').style.display = '';
        svg.innerHTML = '';
        return;
      }
      drawSankey(j.nodes, j.links, j.level_labels);
    } catch (e) {
      document.getElementById('hs-loading').style.display = 'none';
      const err = document.getElementById('hs-error');
      err.style.display = 'block';
      err.textContent = 'Hata: ' + e.message;
    }
  }

  // Yıl değiştiğinde: önce SP aktif yılı yaz, sonra yükle
  yearSel?.addEventListener('change', async () => {
    const newYear = parseInt(yearSel.value, 10);
    if (!newYear) return;
    try {
      const csrf = document.querySelector('meta[name="csrf-token"]')?.content || '';
      await fetch('/sp/api/plan-years/set-active', {
        method: 'POST', credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
        body: JSON.stringify({ year: newYear })
      });
    } catch (_) {}
    load();
  });

  // Strateji filtresi: sadece redraw
  stratSel?.addEventListener('change', () => {
    activeStrategyFilter = stratSel.value;
    if (currentData) drawSankey(currentData.nodes, currentData.links, currentData.level_labels);
  });

  load();
})();
