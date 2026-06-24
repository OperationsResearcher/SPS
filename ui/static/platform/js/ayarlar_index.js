(function () {
  // Tema kartı
  const themeEl = document.getElementById('ayarlar-stat-theme');
  if (themeEl) {
    const t = document.documentElement.getAttribute('data-theme') || 'light';
    themeEl.textContent = t === 'dark' ? window.t('Karanlık') : window.t('Aydınlık');
  }

  // Zamanlanmış rapor sayısı
  fetch('/api/scheduled-reports').then(r => r.ok ? r.json() : null).then(j => {
    if (!j || !j.success) return;
    const s = j.subscriptions || {};
    let n = 0;
    Object.values(s).forEach(v => { if (v && v.enabled) n++; });
    const el = document.getElementById('ayarlar-stat-sched');
    if (el) el.textContent = n;
  }).catch(() => {});

  // Arama filtresi
  const search  = document.getElementById('ayarlar-search');
  const countLbl = document.getElementById('ayarlar-count-label');
  if (!search) return;

  function apply() {
    const q = search.value.trim().toLowerCase();
    let shown = 0;
    document.querySelectorAll('.ayarlar-tile').forEach(t => {
      const hay = (t.dataset.search || '') + ' ' + t.textContent.toLowerCase();
      const ok = !q || hay.includes(q);
      t.style.display = ok ? '' : 'none';
      if (ok) shown++;
    });
    document.querySelectorAll('.ayarlar-grid').forEach(grid => {
      const anyVisible = Array.from(grid.querySelectorAll('.ayarlar-tile')).some(t => t.style.display !== 'none');
      grid.style.display = anyVisible ? '' : 'none';
      const prevH = grid.previousElementSibling;
      if (prevH && prevH.tagName === 'H3') prevH.style.display = anyVisible ? '' : 'none';
    });
    if (countLbl) countLbl.textContent = q ? `${shown} ${window.t('ayar')}` : '';
  }

  search.addEventListener('input', apply);
})();
