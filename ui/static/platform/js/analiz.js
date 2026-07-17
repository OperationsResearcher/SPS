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
  const processSearch  = document.getElementById("analiz-process-search");
  const freqSelect     = document.getElementById("analiz-frequency");
  const methodSelect   = document.getElementById("analiz-forecast-method");
  const resultsEl      = document.getElementById("analiz-results");
  const anomalySection = document.getElementById("anomaly-results");
  const emptyEl        = document.getElementById("analiz-empty");
  const exportBtn      = document.getElementById("btn-export-report");

  // Süreç araması: select option'larını filtrele
  const allOptions = processSelect ? Array.from(processSelect.options) : [];
  processSearch?.addEventListener("input", () => {
    const q = processSearch.value.trim().toLowerCase();
    processSelect.innerHTML = "";
    allOptions.forEach(o => {
      if (!o.value || !q || o.text.toLowerCase().includes(q)) {
        processSelect.appendChild(o.cloneNode(true));
      }
    });
  });

  let trendChartInst    = null;
  let forecastChartInst = null;

  function showError(msg) {
    Swal.fire({ icon: "error", title: t("Hata"), text: msg, confirmButtonColor: "#dc2626" });
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
      label: s.kpi_name || s.label || `${t("PG")} ${i + 1}`,
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

    // API sözleşmesi (TASK-256, kanonik forecast_service):
    //   historical_data: [{date, value}]
    //   forecast:        [{date, forecast_value, confidence_low, confidence_high, confidence}]
    // Eskiden düz sayı dizisi bekleniyordu → nesne basılınca "[object Object]".
    const histRows = data.historical_data || data.historical || [];
    const fcRows   = data.forecast        || [];

    // Nesne dizisini {etiket, değer}'e ayır; eski düz-sayı biçimine de tolerans
    const histVals   = histRows.map(r => (typeof r === "number" ? r : r?.value));
    const histLabels = histRows.map(r => (typeof r === "object" ? r?.date : ""));
    const fcVals     = fcRows.map(r => (typeof r === "number" ? r : r?.forecast_value));
    const fcLabels   = fcRows.map(r => (typeof r === "object" ? r?.date : ""));

    if (!histVals.length && !fcVals.length) {
      canvas.style.display = "none";
      if (empty) empty.style.display = "";
      return;
    }
    canvas.style.display = "";
    if (empty) empty.style.display = "none";

    const allLabels = [...histLabels, ...fcLabels];
    const histData  = histVals;
    const forecast  = fcVals;
    const fcData    = new Array(histVals.length).fill(null).concat(fcVals);

    if (forecastChartInst) forecastChartInst.destroy();
    forecastChartInst = new Chart(canvas, {
      type: "bar",
      data: {
        labels: allLabels.length ? allLabels : fcLabels,
        datasets: [
          ...(histData.length ? [{
            label: t("Gerçekleşen"),
            data: histData,
            backgroundColor: "#6366f120",
            borderColor: "#6366f1",
            borderWidth: 2,
            type: "line",
            tension: 0.3,
            pointRadius: 3,
          }] : []),
          {
            label: t("Tahmin"),
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

    // Sonraki dönem tahmini stat kartına yaz. forecast artık düz sayı dizisi
    // (fcVals); yine de null/undefined'a karşı korun — "[object Object]" ya da
    // "undefined" basma.
    const nextEl = document.getElementById("forecast-next");
    if (nextEl) {
      const val = forecast.find(v => typeof v === "number");
      nextEl.textContent = (typeof val === "number") ? val.toFixed(1) : "—";
    }
  }

  // ── Anomali listesi render ────────────────────────────────────────────────
  function renderAnomalies(data) {
    const listEl = document.getElementById("anomaly-list");
    const countEl = document.getElementById("anomaly-count");
    if (!listEl) return;

    const items = Array.isArray(data) ? data : (data?.anomalies || []);
    const scanned = data?.kpis_scanned ?? null;
    const total   = data?.kpis_total ?? null;
    if (countEl) countEl.textContent = items.length;

    const summary = (scanned !== null)
      ? `<div style="font-size:11.5px;color:#64748b;margin-bottom:10px;">
           ${scanned}/${total} ${t("PG tarandı")} · ${t("yöntem:")} <b>${escHtml(data?.method || 'zscore')}</b>
         </div>` : "";

    if (!items.length) {
      listEl.innerHTML = summary + `<div class="mc-empty" style="padding:30px;">
        <div class="mc-empty-icon"><i class="fas fa-check-circle" style="color:#10b981;"></i></div>
        <div class="mc-empty-title" style="color:#10b981;">${t("Anomali tespit edilmedi")}</div>
      </div>`;
      return;
    }

    listEl.innerHTML = summary + items.map(item => `
      <div style="display:flex; align-items:flex-start; gap:12px; padding:12px 0; border-bottom:1px solid #f1f5f9;">
        <span class="mc-badge mc-badge-warning" style="flex-shrink:0; margin-top:2px;">
          <i class="fas fa-exclamation-triangle"></i>
        </span>
        <div style="flex:1; min-width:0;">
          <div style="font-size:13.5px; font-weight:600; color:#1e293b;">${escHtml(item.kpi_name || item.name || t('Bilinmeyen PG'))}</div>
          ${item.description ? `<div style="font-size:12px; color:#64748b; margin-top:2px;">${escHtml(item.description)}</div>` : ''}
          <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:4px; font-size:11.5px; color:#64748b;">
            ${item.value !== undefined && item.value !== null ? `<span>${t("Değer:")} <b style="color:#f59e0b;">${escHtml(String(item.value))}</b></span>` : ''}
            ${item.date ? `<span>${t("Tarih:")} <b>${escHtml(item.date)}</b></span>` : ''}
            ${item.score !== undefined && item.score !== null ? `<span>${t("Z-skor:")} <b>${escHtml(String(Number(item.score).toFixed(2)))}</b></span>` : ''}
            ${item.process_id ? `<a href="/k-plan/process/${item.process_id}/karne" style="color:#6366f1; text-decoration:underline;">${t("Süreç karnesi →")}</a>` : ''}
          </div>
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
    if (!pid) { showError(t("Lütfen bir süreç seçin.")); return; }

    if (emptyEl) emptyEl.style.display = "none";
    if (resultsEl) resultsEl.style.display = "";
    if (anomalySection) anomalySection.style.display = "none";

    // Stat kartlarını sıfırla
    ["health-score-val","trend-direction","forecast-next","anomaly-count"].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.textContent = "…";
    });

    const freq = freqSelect?.value || "monthly";
    const method = methodSelect?.value || "linear";
    const [healthRes, trendRes, forecastRes] = await Promise.allSettled([
      fetch(`${HEALTH_BASE}${pid}`).then(r => r.json()),
      fetch(`${TREND_BASE}${pid}?frequency=${encodeURIComponent(freq)}`).then(r => r.json()),
      fetch(`${FORECAST_BASE}${pid}?periods=3&method=${encodeURIComponent(method)}`).then(r => r.json()),
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
        labelEl.textContent = isNaN(num) ? "" : (num >= 80 ? t("İyi") : num >= 50 ? t("Orta") : t("Düşük"));
      }
    }

    // Trend
    if (trendRes.status === "fulfilled" && trendRes.value.success) {
      const trendData = trendRes.value.data;
      // Yeni shape: { series: [...], direction, kpi_count }
      renderTrendChart(trendData?.series ?? trendData);

      // Trend yönü
      const dirEl = document.getElementById("trend-direction");
      if (dirEl) {
        const dir = trendData?.direction || trendData?.series?.[0]?.direction;
        dirEl.textContent = dir === "up" ? t("↑ Artış") : dir === "down" ? t("↓ Düşüş") : t("→ Sabit");
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
    if (listEl) listEl.innerHTML = `<div style="text-align:center; padding:20px; color:#94a3b8;"><i class="fas fa-spinner fa-spin"></i> ${t("Taranıyor…")}</div>`;

    try {
      const pid = processSelect?.value || "";
      const url = pid ? `${ANOMALIES_URL}?process_id=${pid}` : ANOMALIES_URL;
      const res  = await fetch(url);
      const data = await res.json();
      if (data.success) {
        renderAnomalies(data.data);
      } else {
        showError(data.message || t("Anomali verisi alınamadı."));
        if (listEl) listEl.innerHTML = `<div class="mc-alert mc-alert-danger">${t("Veri alınamadı.")}</div>`;
      }
    } catch (e) {
      showError(t("Sunucu hatası: ") + e.message);
    }
  }

  document.getElementById("btn-load-analiz")?.addEventListener("click", loadAnaliz);
  document.getElementById("btn-anomalies")?.addEventListener("click", loadAnomalies);

})();
