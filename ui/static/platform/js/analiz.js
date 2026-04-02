/**
 * analiz.js — Analiz Merkezi modülü JS
 * Kural: alert()/confirm()/prompt() YASAK — yalnızca SweetAlert2
 * Kural: Jinja2 {{ }} bu dosyada YASAK — veri data-* ile gelir
 */

(function () {
  "use strict";

  const root = document.getElementById("analiz-root");
  if (!root) return;

  const TREND_BASE    = root.dataset.trendBase;
  const HEALTH_BASE   = root.dataset.healthBase;
  const FORECAST_BASE = root.dataset.forecastBase;
  const ANOMALIES_URL = root.dataset.anomaliesUrl;
  const REPORT_BASE   = root.dataset.reportBase;

  const processSelect  = document.getElementById("analiz-process-select");
  const resultsEl      = document.getElementById("analiz-results");
  const anomalySection = document.getElementById("anomaly-results");
  const emptyEl        = document.getElementById("analiz-empty");
  const exportBtn      = document.getElementById("btn-export-report");

  let trendChartInst    = null;
  let forecastChartInst = null;

  function showError(msg) {
    Swal.fire({ icon: "error", title: "Hata", text: msg, confirmButtonColor: "#dc2626" });
  }

  // ── Sağlık skoru rengi ────────────────────────────────────────────────────
  function healthColor(score) {
    if (score >= 80) return "#10b981";
    if (score >= 50) return "#f59e0b";
    return "#ef4444";
  }

  // ── Trend grafiği ─────────────────────────────────────────────────────────
  function renderTrendChart(data) {
    const canvas = document.getElementById("trend-chart");
    const empty  = document.getElementById("trend-empty");
    if (!canvas) return;

    // data: { kpi_name, labels: [...], values: [...] } veya dizi
    const series = Array.isArray(data) ? data : (data ? [data] : []);
    if (!series.length || !series[0].values?.length) {
      canvas.style.display = "none";
      if (empty) empty.style.display = "";
      return;
    }
    canvas.style.display = "";
    if (empty) empty.style.display = "none";

    const colors = ["#6366f1","#10b981","#f59e0b","#ef4444","#8b5cf6","#3b82f6"];
    const datasets = series.map((s, i) => ({
      label: s.kpi_name || s.label || `PG ${i + 1}`,
      data: s.values,
      borderColor: colors[i % colors.length],
      backgroundColor: colors[i % colors.length] + "18",
      borderWidth: 2,
      pointRadius: 4,
      tension: 0.3,
      fill: i === 0,
      spanGaps: true,
    }));

    if (trendChartInst) trendChartInst.destroy();
    trendChartInst = new Chart(canvas, {
      type: "line",
      data: { labels: series[0].labels || [], datasets },
      options: {
        responsive: true,
        plugins: {
          legend: { display: datasets.length > 1 },
          tooltip: { mode: "index", intersect: false },
        },
        scales: {
          y: { beginAtZero: false, grid: { color: "rgba(0,0,0,0.05)" } },
          x: { grid: { display: false } },
        },
      },
    });
  }

  // ── Tahmin grafiği ────────────────────────────────────────────────────────
  function renderForecastChart(data) {
    const canvas = document.getElementById("forecast-chart");
    const empty  = document.getElementById("forecast-empty");
    if (!canvas) return;

    // data: { labels, historical, forecast } veya dizi tahmin değerleri
    const labels     = data.labels     || data.periods     || [];
    const historical = data.historical || [];
    const forecast   = data.forecast   || data.values      || [];

    if (!labels.length && !forecast.length) {
      canvas.style.display = "none";
      if (empty) empty.style.display = "";
      return;
    }
    canvas.style.display = "";
    if (empty) empty.style.display = "none";

    const allLabels = [...(data.hist_labels || []), ...labels];
    const histData  = historical.map(v => v);
    const fcData    = new Array(historical.length).fill(null).concat(forecast);

    if (forecastChartInst) forecastChartInst.destroy();
    forecastChartInst = new Chart(canvas, {
      type: "bar",
      data: {
        labels: allLabels.length ? allLabels : labels,
        datasets: [
          ...(historical.length ? [{
            label: "Gerçekleşen",
            data: histData,
            backgroundColor: "#6366f120",
            borderColor: "#6366f1",
            borderWidth: 2,
            type: "line",
            tension: 0.3,
            pointRadius: 3,
          }] : []),
          {
            label: "Tahmin",
            data: allLabels.length ? fcData : forecast,
            backgroundColor: "#8b5cf640",
            borderColor: "#8b5cf6",
            borderWidth: 2,
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: true },
          tooltip: { mode: "index", intersect: false },
        },
        scales: {
          y: { beginAtZero: false, grid: { color: "rgba(0,0,0,0.05)" } },
          x: { grid: { display: false } },
        },
      },
    });

    // Sonraki dönem tahmini stat kartına yaz
    const nextEl = document.getElementById("forecast-next");
    if (nextEl && forecast.length) {
      const val = forecast[0];
      nextEl.textContent = typeof val === "number" ? val.toFixed(1) : val;
    }
  }

  // ── Anomali listesi render ────────────────────────────────────────────────
  function renderAnomalies(data) {
    const listEl = document.getElementById("anomaly-list");
    const countEl = document.getElementById("anomaly-count");
    if (!listEl) return;

    const items = Array.isArray(data) ? data : (data?.anomalies || []);
    if (countEl) countEl.textContent = items.length;

    if (!items.length) {
      listEl.innerHTML = `<div class="mc-empty" style="padding:30px;">
        <div class="mc-empty-icon"><i class="fas fa-check-circle" style="color:#10b981;"></i></div>
        <div class="mc-empty-title" style="color:#10b981;">Anomali tespit edilmedi</div>
      </div>`;
      return;
    }

    listEl.innerHTML = items.map(item => `
      <div style="display:flex; align-items:flex-start; gap:12px; padding:12px 0; border-bottom:1px solid #f1f5f9;">
        <span class="mc-badge mc-badge-warning" style="flex-shrink:0; margin-top:2px;">
          <i class="fas fa-exclamation-triangle"></i>
        </span>
        <div>
          <div style="font-size:13.5px; font-weight:500; color:#1e293b;">${escHtml(item.kpi_name || item.name || 'Bilinmeyen PG')}</div>
          <div style="font-size:12px; color:#64748b; margin-top:2px;">${escHtml(item.description || item.message || '')}</div>
          ${item.value !== undefined ? `<div style="font-size:12px; color:#f59e0b; margin-top:2px;">Değer: <strong>${item.value}</strong></div>` : ''}
        </div>
      </div>
    `).join("");
  }

  function escHtml(str) {
    if (!str) return "";
    return String(str).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
  }

  // ── Ana analiz yükle ──────────────────────────────────────────────────────
  async function loadAnaliz() {
    const pid = processSelect.value;
    if (!pid) { showError("Lütfen bir süreç seçin."); return; }

    if (emptyEl) emptyEl.style.display = "none";
    if (resultsEl) resultsEl.style.display = "";
    if (anomalySection) anomalySection.style.display = "none";

    // Stat kartlarını sıfırla
    ["health-score-val","trend-direction","forecast-next","anomaly-count"].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.textContent = "…";
    });

    const [healthRes, trendRes, forecastRes] = await Promise.allSettled([
      fetch(`${HEALTH_BASE}${pid}`).then(r => r.json()),
      fetch(`${TREND_BASE}${pid}`).then(r => r.json()),
      fetch(`${FORECAST_BASE}${pid}?periods=3`).then(r => r.json()),
    ]);

    // Sağlık skoru
    if (healthRes.status === "fulfilled" && healthRes.value.success) {
      const score = healthRes.value.data?.score ?? healthRes.value.data;
      const scoreEl = document.getElementById("health-score-val");
      const labelEl = document.getElementById("health-score-label");
      if (scoreEl) {
        const num = typeof score === "number" ? score : parseFloat(score);
        scoreEl.textContent = isNaN(num) ? "—" : num.toFixed(1);
        scoreEl.style.color = isNaN(num) ? "" : healthColor(num);
      }
      if (labelEl) {
        const num = typeof score === "number" ? score : parseFloat(score);
        labelEl.textContent = isNaN(num) ? "" : (num >= 80 ? "İyi" : num >= 50 ? "Orta" : "Düşük");
      }
    }

    // Trend
    if (trendRes.status === "fulfilled" && trendRes.value.success) {
      const trendData = trendRes.value.data;
      renderTrendChart(trendData);

      // Trend yönü
      const dirEl = document.getElementById("trend-direction");
      if (dirEl) {
        const dir = trendData?.direction || trendData?.[0]?.direction;
        dirEl.textContent = dir === "up" ? "↑ Artış" : dir === "down" ? "↓ Düşüş" : "→ Sabit";
        dirEl.style.color = dir === "up" ? "#10b981" : dir === "down" ? "#ef4444" : "#f59e0b";
      }

      if (exportBtn) {
        exportBtn.href = `${REPORT_BASE}${pid}?format=excel`;
        exportBtn.style.display = "";
      }
    } else {
      const canvas = document.getElementById("trend-chart");
      const empty  = document.getElementById("trend-empty");
      if (canvas) canvas.style.display = "none";
      if (empty)  empty.style.display = "";
    }

    // Tahmin
    if (forecastRes.status === "fulfilled" && forecastRes.value.success) {
      renderForecastChart(forecastRes.value.data);
    } else {
      const canvas = document.getElementById("forecast-chart");
      const empty  = document.getElementById("forecast-empty");
      if (canvas) canvas.style.display = "none";
      if (empty)  empty.style.display = "";
    }
  }

  // ── Anomali tara ──────────────────────────────────────────────────────────
  async function loadAnomalies() {
    if (anomalySection) anomalySection.style.display = "";
    const listEl = document.getElementById("anomaly-list");
    if (listEl) listEl.innerHTML = `<div style="text-align:center; padding:20px; color:#94a3b8;"><i class="fas fa-spinner fa-spin"></i> Taranıyor…</div>`;

    try {
      const res  = await fetch(ANOMALIES_URL);
      const data = await res.json();
      if (data.success) {
        renderAnomalies(data.data);
      } else {
        showError(data.message || "Anomali verisi alınamadı.");
        if (listEl) listEl.innerHTML = `<div class="mc-alert mc-alert-danger">Veri alınamadı.</div>`;
      }
    } catch (e) {
      showError("Sunucu hatası: " + e.message);
    }
  }

  document.getElementById("btn-load-analiz")?.addEventListener("click", loadAnaliz);
  document.getElementById("btn-anomalies")?.addEventListener("click", loadAnomalies);

})();
