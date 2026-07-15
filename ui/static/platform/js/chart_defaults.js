/**
 * Chart.js global varsayılanları — Kokpitim UI Kılavuzu §6.
 *
 * 2026-07-15: base.html içinde inline <script> olarak duruyordu (KURALLAR §3:
 * "Inline <style> veya <script> — harici dosyaya taşı"). Saf JS, Jinja
 * ifadesi içermiyordu → doğrudan taşındı.
 *
 * Chart.js'ten SONRA, grafik çizen sayfa script'lerinden ÖNCE yüklenmeli.
 */
(function () {
  if (!window.Chart) return;

  Chart.defaults.font.family = "'Inter', system-ui, sans-serif";
  Chart.defaults.font.size = 12;
  Chart.defaults.color = '#475569';
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.plugins.legend.labels.padding = 12;
  Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(15,23,42,0.95)';
  Chart.defaults.plugins.tooltip.titleFont = { weight: '600', size: 12 };
  Chart.defaults.plugins.tooltip.padding = 10;
  Chart.defaults.plugins.tooltip.cornerRadius = 6;
  Chart.defaults.elements.line.tension = 0.3;
  Chart.defaults.elements.line.borderWidth = 2;
  Chart.defaults.scale.grid.color = '#f1f5f9';
  Chart.defaults.scale.ticks.color = '#94a3b8';
  Chart.defaults.scale.ticks.font = { size: 11 };

  window.KOKPITIM_CHART_COLORS = [
    '#4f46e5', '#10b981', '#f59e0b', '#0ea5e9',
    '#8b5cf6', '#ef4444', '#06b6d4', '#84cc16',
  ];
})();
