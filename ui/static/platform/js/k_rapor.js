/* K-Rapor — Kurumsal Raporlama Merkezi */
"use strict";

(function () {
  const ROOT = document.getElementById("kr-root");
  if (!ROOT) return;

  let year = parseInt(ROOT.dataset.year) || new Date().getFullYear();

  // ── Yardımcılar ──────────────────────────────────────────────────────────────
  function apiUrl(name) {
    // data-api-surec-pg → dataset.apiSurecPg
    const key = "api" + name.split("-").map(s => s[0].toUpperCase() + s.slice(1)).join("");
    return ROOT.dataset[key] || "";
  }

  function esc(s) {
    return String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  function scoreColor(v) {
    if (v == null) return "#94a3b8";
    if (v >= 80)   return "#10b981";
    if (v >= 50)   return "#f59e0b";
    return "#ef4444";
  }

  function scoreClass(v) {
    if (v == null) return "";
    if (v >= 80)   return "high";
    if (v >= 50)   return "mid";
    return "low";
  }

  function heatClass(val) {
    if (val == null) return "no-data";
    if (val < 25)   return "heat-0";
    if (val < 50)   return "heat-1";
    if (val < 75)   return "heat-2";
    if (val < 95)   return "heat-3";
    return "heat-4";
  }

  function setHtml(id, html) {
    const el = document.getElementById(id);
    if (el) el.innerHTML = html;
  }

  function errHtml(e) {
    return `<div class="kr-loading" style="color:#ef4444;">Hata: ${esc(String(e))}</div>`;
  }
  function errRow(n, e) {
    return `<tr><td colspan="${n}" style="text-align:center;padding:16px;color:#ef4444;font-size:11px;">Hata: ${esc(String(e))}</td></tr>`;
  }

  const EMPTY_HTML    = '<div class="kr-loading">Veri yok.</div>';
  const ERROR_HTML    = '<div class="kr-loading" style="color:#ef4444;">Yüklenemedi.</div>';
  const EMPTY_ROW_1   = n => `<tr><td colspan="${n}" style="text-align:center;padding:24px;color:#94a3b8;">Kayıt yok.</td></tr>`;
  const ERROR_ROW_1   = n => `<tr><td colspan="${n}" style="text-align:center;padding:24px;color:#ef4444;">Yüklenemedi.</td></tr>`;

  function fetchJson(url, params) {
    if (!url) return Promise.reject(new Error("empty url"));
    const u = new URL(url, location.origin);
    if (params) Object.entries(params).forEach(([k, v]) => u.searchParams.set(k, v));
    return fetch(u).then(r => r.json());
  }

  // ── Tab Yönetimi ─────────────────────────────────────────────────────────────
  const loaded = {};
  let faaliyetChart    = null;
  let denetimChart     = null;
  let kvektorChart     = null;

  // Sekme kartı = anchor link (?tab=…). Tarayıcı navigation yapacak — JS müdahale etmez.
  // URL'den ?tab okuyup uygun paneli aktive et, grid'i gizle, back-bar göster.
  const urlTab = new URLSearchParams(window.location.search).get("tab");
  const grid = document.getElementById("kr-tab-grid");
  const backBar = document.getElementById("kr-back-bar");
  const searchBar = document.getElementById("kr-search-bar");
  const activeTitleEl = document.getElementById("kr-active-tab-title");

  const TABS_NO_YEAR = new Set(["risk", "denetim", "bildirim-analiz", "swot-trend"]);
  const yearLabel = document.getElementById("kr-year-label");

  function activatePanel(tab) {
    document.querySelectorAll(".kr-panel").forEach(p => p.classList.toggle("active", p.id === "kr-panel-" + tab));
    if (yearLabel) yearLabel.style.display = TABS_NO_YEAR.has(tab) ? "none" : "";
    if (!loaded[tab]) { loaded[tab] = true; loadTab(tab); }
  }

  // ── Yıl Seçici ───────────────────────────────────────────────────────────────
  // Yeni davranış: seçilen yıl tüm SP modüllerine yayılsın (set-active) ve
  // server-render edilen üst KPI kartları + tüm sekmeler doğru yıl için
  // gelsin diye sayfayı tek seferde yeniden yükle.
  const yearSel = document.getElementById("kr-year-select");
  if (yearSel) {
    yearSel.addEventListener("change", async () => {
      const newYear = parseInt(yearSel.value);
      if (!newYear) return;
      yearSel.disabled = true;
      try {
        const csrf = document.querySelector('meta[name="csrf-token"]')?.content || "";
        await fetch("/sp/api/plan-years/set-active", {
          method: "POST",
          credentials: "same-origin",
          headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
          body: JSON.stringify({ year: newYear })
        });
      } catch (e) { /* sessiz */ }
      // Mevcut ?tab= parametresini koruyarak reload
      const params = new URLSearchParams(window.location.search);
      params.set("year", newYear);
      window.location.href = window.location.pathname + "?" + params.toString();
    });
  }

  // İlk yükleme — URL'den oku
  if (urlTab) {
    // Tek sekme görünümü: grid + arama bar gizle, back-bar göster
    if (grid) grid.style.display = "none";
    if (searchBar) searchBar.style.display = "none";
    if (backBar) backBar.style.display = "";
    const card = document.querySelector(`.kr-tab-card[data-tab="${urlTab}"]`);
    if (card && activeTitleEl) {
      const name = card.dataset.name || urlTab;
      activeTitleEl.innerHTML = `<i class="fas fa-chevron-right" style="color:#cbd5e1; margin-right:6px; font-size:11px;"></i>${name}`;
    }
    activatePanel(urlTab);
  } else {
    // Grid görünümü — hiçbir panel aktif değil
    document.querySelectorAll(".kr-panel").forEach(p => p.classList.remove("active"));
  }

  function loadTab(tab) {
    switch (tab) {
      case "kurumsal":    loadKurumsal();   break;
      case "surec-pg":    loadSurecPg();    break;
      case "uyum":        loadUyum();       break;
      case "faaliyet":    loadFaaliyet();   break;
      case "bireysel":    loadBireysel();   break;
      case "veri-durumu": loadVeriDurumu(); break;
      case "risk":             loadRisk();            break;
      case "denetim":          loadDenetim();         break;
      case "uyari":            loadUyari();           break;
      case "k-vektor":         loadKVektor();         break;
      case "evm":              loadEvm();             break;
      case "stratejik-analiz": loadStratejikAnaliz(); break;
      case "paydas":           loadPaydas();          break;
      case "rekabet":          loadRekabet();         break;
      case "pg-dagilim":        loadPgDagilim();       break;
      case "faaliyet-matris":   loadFaaliyetMatris();  break;
      case "aktivite-takvim":   loadAktiviteTakvim();  break;
      case "kurum-karsilastirma": loadKurumKarsilastirma(); break;
      case "strateji-kapsama":  loadStratejiKapsama(); break;
      case "sorumlu-analiz":    loadSorumluAnaliz();   break;
      case "swot-trend":        loadSwotTrend();       break;
      case "bildirim-analiz":   loadBildirimAnaliz();  break;
    }
  }

  // ── Rapor 1: Kurumsal ────────────────────────────────────────────────────────
  function loadKurumsal() {
    fetchJson(apiUrl("kurumsal"), { year })
      .then(res => {
        const loadingEl = document.getElementById("kr-vizyon-loading");
        if (loadingEl) loadingEl.style.display = "none";

        if (!res.success) {
          setHtml("kr-vizyon-gauge", "—");
          setHtml("kr-strateji-bars", `<div class="kr-loading" style="color:#ef4444;">${esc(res.message || "Yüklenemedi.")}</div>`);
          setHtml("kr-top5",    ERROR_HTML);
          setHtml("kr-bottom5", ERROR_HTML);
          return;
        }

        const d = res.data;

        // Vizyon skoru + mini gauge ring
        const gauge = document.getElementById("kr-vizyon-gauge");
        if (gauge) {
          const score = d.vision_score ?? 0;
          gauge.textContent = score.toFixed(1);
          gauge.style.color = scoreColor(score);
        }

        // Strateji barları — artık kod+başlık geliyor
        const barsEl = document.getElementById("kr-strateji-bars");
        if (barsEl) {
          const detail = d.strategy_scores_detail || [];
          if (!detail.length) {
            barsEl.innerHTML = EMPTY_HTML;
          } else {
            barsEl.innerHTML = detail.map(r => `
              <div class="kr-bar-row">
                <div class="kr-bar-label" title="${esc(r.title)}">${esc((r.code ? r.code + " " : "") + r.title)}</div>
                <div class="kr-bar-track"><div class="kr-bar-fill" style="width:${Math.min(100, r.score)}%;"></div></div>
                <div class="kr-bar-pct" style="color:${scoreColor(r.score)}">${r.score.toFixed(1)}</div>
              </div>`).join("");
          }
        }

        // PG Sağlık
        const saglik = d.pg_saglik;
        if (saglik && saglik.toplam) {
          setHtml("kr-pg-saglik", `
            <div class="mc-stat-card mc-stat-emerald" data-card-code="k_rapor_kurumsal.hedefte">
              <div class="mc-stat-icon"><i class="fas fa-circle-check"></i></div>
              <div class="mc-stat-label">Hedefte</div>
              <div class="mc-stat-value">${saglik.yesil}</div>
              <div class="mc-stat-sub">≥%80 başarı (${Math.round(saglik.yesil/saglik.toplam*100)}%)</div>
            </div>
            <div class="mc-stat-card mc-stat-amber" data-card-code="k_rapor_kurumsal.riskli">
              <div class="mc-stat-icon"><i class="fas fa-circle-half-stroke"></i></div>
              <div class="mc-stat-label">Riskli</div>
              <div class="mc-stat-value">${saglik.sari}</div>
              <div class="mc-stat-sub">%50–79 başarı (${Math.round(saglik.sari/saglik.toplam*100)}%)</div>
            </div>
            <div class="mc-stat-card" style="background:#fef2f2;" data-card-code="k_rapor_kurumsal.kritik">
              <div class="mc-stat-icon" style="color:#ef4444;"><i class="fas fa-circle-xmark"></i></div>
              <div class="mc-stat-label">Kritik</div>
              <div class="mc-stat-value" style="color:#ef4444;">${saglik.kirmizi}</div>
              <div class="mc-stat-sub">&lt;%50 başarı (${Math.round(saglik.kirmizi/saglik.toplam*100)}%)</div>
            </div>`);
        } else {
          setHtml("kr-pg-saglik", "");
        }

        // Top5 / Bottom5
        renderRankList("kr-top5",    d.top5    || []);
        renderRankList("kr-bottom5", d.bottom5 || []);
      })
      .catch(() => {
        const loadingEl = document.getElementById("kr-vizyon-loading");
        if (loadingEl) loadingEl.style.display = "none";
        setHtml("kr-vizyon-gauge", "—");
        setHtml("kr-strateji-bars", ERROR_HTML);
        setHtml("kr-top5",    ERROR_HTML);
        setHtml("kr-bottom5", ERROR_HTML);
      });
  }

  function renderRankList(elId, items) {
    const el = document.getElementById(elId);
    if (!el) return;
    if (!items.length) { el.innerHTML = EMPTY_HTML; return; }
    el.innerHTML = items.map((item, i) => `
      <div class="kr-rank-item">
        <div class="kr-rank-no">${i + 1}</div>
        <div class="kr-rank-code">${esc(item.code)}</div>
        <div class="kr-rank-name" title="${esc(item.name)}">${esc(item.name)}</div>
        <div class="kr-rank-score ${scoreClass(item.score)}">${item.score}</div>
      </div>`).join("");
  }

  // ── Rapor 2: Süreç-PG Isı Haritası ──────────────────────────────────────────
  function loadSurecPg() {
    const period = document.getElementById("kr-pg-period")?.value || "ceyrek";
    setHtml("kr-heat-table", '<div class="kr-loading" style="padding:24px;">Yükleniyor…</div>');
    fetchJson(apiUrl("surec-pg"), { year, period })
      .then(res => {
        if (!res.success) { setHtml("kr-heat-table", `<div class="kr-loading" style="padding:24px;color:#ef4444;">${esc(res.message || "Yüklenemedi.")}</div>`); return; }
        renderHeatMap(res.data, res.labels);
      })
      .catch(() => setHtml("kr-heat-table", `<div class="kr-loading" style="padding:24px;color:#ef4444;">Yüklenemedi.</div>`));
  }

  const pgPeriod = document.getElementById("kr-pg-period");
  if (pgPeriod) pgPeriod.addEventListener("change", () => { delete loaded["surec-pg"]; loadSurecPg(); });

  function renderHeatMap(rows, labels) {
    const el = document.getElementById("kr-heat-table");
    if (!el) return;
    if (!rows || !rows.length) { el.innerHTML = '<div class="kr-loading" style="padding:24px;">Süreç verisi yok.</div>'; return; }
    const thead = `<tr><th class="kr-ht-proc">Süreç</th>${(labels || []).map(l => `<th>${esc(l)}</th>`).join("")}<th>PG</th></tr>`;
    const tbody = rows.map(row => {
      const cells = (row.cells || []).map(c => {
        if (!c.has_data) return `<td><span class="kr-heat-cell no-data">—</span></td>`;
        return `<td><span class="kr-heat-cell ${heatClass(c.avg_val)}" title="${c.count} veri · Ort: ${c.avg_val}">${c.avg_val ?? "—"}</span></td>`;
      }).join("");
      return `<tr>
        <td class="kr-ht-proc-name">
          <span class="kr-ht-proc-link" data-proc-id="${row.id}" title="Trend görüntüle">${esc((row.code ? row.code + " " : "") + row.name)}</span>
        </td>
        ${cells}
        <td style="text-align:center;font-size:11px;color:#94a3b8;">${row.kpi_count}</td>
      </tr>`;
    }).join("");
    el.innerHTML = `<table class="kr-heat-table"><thead>${thead}</thead><tbody>${tbody}</tbody></table>`;

    // Süreç adına tıklayınca trend modal aç
    el.querySelectorAll(".kr-ht-proc-link").forEach(link => {
      link.addEventListener("click", () => openTrendModal(link.dataset.procId, link.textContent.trim()));
    });
  }

  // ── Trend Modal ───────────────────────────────────────────────────────────────
  let trendChart = null;
  function openTrendModal(procId, procName) {
    const overlay = document.getElementById("kr-trend-modal");
    if (!overlay) return;
    document.getElementById("kr-trend-modal-title").textContent = procName;
    setHtml("kr-trend-modal-body", '<div class="kr-loading" style="padding:32px;">Yükleniyor…</div>');
    overlay.classList.add("open");

    const trendBase = ROOT.dataset.apiTrend || "";
    // trend API: /k-rapor/api/trend/<kpi_id> — süreç için ilk KPI'ı çek
    // Önce surec-pg verisinden kpi_id bul, yoksa mesaj göster
    fetchJson(apiUrl("surec-pg"), { year, period: "aylik" })
      .then(res => {
        if (!res.success) throw new Error(res.message);
        const proc = (res.data || []).find(r => String(r.id) === String(procId));
        if (!proc || !proc.kpi_ids || !proc.kpi_ids.length) {
          setHtml("kr-trend-modal-body", '<div class="kr-loading">Bu süreç için PG verisi yok.</div>');
          return;
        }
        return fetchJson(`/k-rapor/api/trend/${proc.kpi_ids[0]}`, { frequency: "monthly" });
      })
      .then(res => {
        if (!res) return;
        if (!res.success) { setHtml("kr-trend-modal-body", ERROR_HTML); return; }
        const tData = res.data || {};
        const labels  = tData.labels  || [];
        const actuals = tData.actuals || [];
        const targets = tData.targets || [];
        setHtml("kr-trend-modal-body", `
          <div style="font-size:12px;color:#64748b;margin-bottom:8px;">${esc(res.kpi_code || "")} — ${esc(res.kpi_name || "")}</div>
          <canvas id="kr-trend-canvas" height="180"></canvas>`);
        const canvas = document.getElementById("kr-trend-canvas");
        if (canvas) {
          if (trendChart) trendChart.destroy();
          trendChart = new Chart(canvas, {
            type: "line",
            data: {
              labels,
              datasets: [
                { label: "Gerçekleşen", data: actuals, borderColor: "#6366f1", backgroundColor: "rgba(99,102,241,0.1)", tension: 0.3, fill: true, pointRadius: 4 },
                { label: "Hedef",       data: targets, borderColor: "#10b981", borderDash: [5,4], tension: 0.3, fill: false, pointRadius: 0 },
              ]
            },
            options: { responsive: true, plugins: { legend: { position: "bottom" } }, scales: { y: { beginAtZero: false } } }
          });
        }
      })
      .catch(() => setHtml("kr-trend-modal-body", ERROR_HTML));
  }

  // Trend modal kapat
  document.getElementById("kr-trend-modal-close")?.addEventListener("click", () => {
    document.getElementById("kr-trend-modal")?.classList.remove("open");
    if (trendChart) { trendChart.destroy(); trendChart = null; }
  });
  document.getElementById("kr-trend-modal")?.addEventListener("click", e => {
    if (e.target === e.currentTarget) {
      e.currentTarget.classList.remove("open");
      if (trendChart) { trendChart.destroy(); trendChart = null; }
    }
  });

  // ── Rapor 4: Stratejik Uyum Ağacı ────────────────────────────────────────────
  function loadUyum() {
    setHtml("kr-uyum-tree", '<div class="kr-loading">Yükleniyor…</div>');
    fetchJson(apiUrl("uyum"), { year })
      .then(res => {
        const badge = document.getElementById("kr-uyum-vizyon");
        if (!res.success) {
          setHtml("kr-uyum-tree", `<div class="kr-loading" style="color:#ef4444;">${esc(res.message || "Yüklenemedi.")}</div>`);
          return;
        }
        if (badge) badge.textContent = `Vizyon Skoru: ${(res.vision_score || 0).toFixed(1)}`;
        const el = document.getElementById("kr-uyum-tree");
        if (!el) return;
        if (!res.data || !res.data.length) { el.innerHTML = EMPTY_HTML; return; }
        el.innerHTML = res.data.map(buildStrategyNode).join("");
        el.querySelectorAll(".kr-tree-s-header").forEach(h => h.addEventListener("click", () => h.nextElementSibling.classList.toggle("open")));
        el.querySelectorAll(".kr-tree-ss-header").forEach(h => h.addEventListener("click", () => h.nextElementSibling.classList.toggle("open")));
      })
      .catch(() => setHtml("kr-uyum-tree", ERROR_HTML));
  }

  function buildStrategyNode(s) {
    const subHtml = (s.sub_strategies || []).map(ss => {
      const procs = (ss.processes || []).map(p => `
        <span class="kr-tree-proc-chip">
          <span>${esc(p.code || "")}</span>
          <span>${esc(p.name)}</span>
          <span class="score" style="color:${scoreColor(p.score)}">${p.score}</span>
        </span>`).join("");
      return `<div class="kr-tree-substrat">
        <div class="kr-tree-ss-header">
          <span class="kr-tree-ss-code">${esc(ss.code)}</span>
          <span class="kr-tree-ss-title">${esc(ss.title)}</span>
          <span class="kr-tree-ss-score" style="color:${scoreColor(ss.score)}">${ss.score}</span>
        </div>
        <div class="kr-tree-proc-list">${procs || '<span style="font-size:11px;color:#94a3b8;">Bağlı süreç yok</span>'}</div>
      </div>`;
    }).join("");
    return `<div class="kr-tree-strategy">
      <div class="kr-tree-s-header">
        <span class="kr-tree-s-code">${esc(s.code)}</span>
        <span class="kr-tree-s-title">${esc(s.title)}</span>
        <span class="kr-tree-s-score" style="color:${scoreColor(s.score)}">${s.score}</span>
      </div>
      <div class="kr-tree-s-body">${subHtml || EMPTY_HTML}</div>
    </div>`;
  }

  // ── Rapor 5: Faaliyet ────────────────────────────────────────────────────────
  function loadFaaliyet() {
    setHtml("kr-fal-stats", '<div class="kr-loading" style="grid-column:span 4;padding:24px;">Yükleniyor…</div>');
    fetchJson(apiUrl("faaliyet"), { year })
      .then(res => {
        if (!res.success) {
          setHtml("kr-fal-stats", `<div class="kr-loading" style="grid-column:span 4;color:#ef4444;">${esc(res.message || "Yüklenemedi.")}</div>`);
          setHtml("kr-geciken-body", ERROR_ROW_1(4));
          return;
        }
        const d = res.data;

        setHtml("kr-fal-stats", `
          <div class="mc-stat-card mc-stat-emerald" data-card-code="k_rapor_faaliyet.tamamlanan">
            <div class="mc-stat-label">Tamamlanan</div>
            <div class="mc-stat-value">${d.tamamlanan}</div>
            <div class="mc-stat-sub">%${d.tamamlanma_orani} tamamlandı</div>
          </div>
          <div class="mc-stat-card mc-stat-amber" data-card-code="k_rapor_faaliyet.devam_ediyor">
            <div class="mc-stat-label">Devam Ediyor</div>
            <div class="mc-stat-value">${d.devam}</div>
            <div class="mc-stat-sub">Aktif faaliyet</div>
          </div>
          <div class="mc-stat-card" style="background:#fef2f2;" data-card-code="k_rapor_faaliyet.geciken">
            <div class="mc-stat-label">Geciken</div>
            <div class="mc-stat-value" style="color:#ef4444;">${d.geciken}</div>
            <div class="mc-stat-sub">Teslim tarihi geçmiş</div>
          </div>
          <div class="mc-stat-card mc-stat-indigo" data-card-code="k_rapor_faaliyet.toplam">
            <div class="mc-stat-label">Toplam</div>
            <div class="mc-stat-value">${d.toplam}</div>
            <div class="mc-stat-sub">Tüm faaliyetler</div>
          </div>`);

        const canvas = document.getElementById("kr-fal-chart");
        if (canvas) {
          if (faaliyetChart) faaliyetChart.destroy();
          faaliyetChart = new Chart(canvas, {
            type: "bar",
            data: {
              labels: ["Oca","Şub","Mar","Nis","May","Haz","Tem","Ağu","Eyl","Eki","Kas","Ara"],
              datasets: [{ label: "Tamamlanan", data: d.aylik_tamamlanan || [], backgroundColor: "rgba(99,102,241,0.7)", borderRadius: 4 }]
            },
            options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } }
          });
        }

        const tbody = document.getElementById("kr-geciken-body");
        if (tbody) {
          tbody.innerHTML = (d.geciken_liste || []).map(a => `
            <tr>
              <td>${esc(a.name)}</td>
              <td>${esc(a.surec)}</td>
              <td style="white-space:nowrap;">${esc(a.end_date)}</td>
              <td><span class="mc-badge mc-badge-warning">${esc(a.status)}</span></td>
            </tr>`).join("") || EMPTY_ROW_1(4);
        }

        // Proje portföy
        const oz = d.proje_ozet || {};
        const badges = document.getElementById("kr-proje-ozet-badges");
        if (badges && oz.toplam) {
          badges.innerHTML = `
            <span class="mc-badge mc-badge-indigo">Toplam: ${oz.toplam}</span>
            <span class="mc-badge mc-badge-success">Tamamlanan: ${oz.tamamlanan}</span>
            <span class="mc-badge mc-badge-warning">Devam: ${oz.devam}</span>
            ${oz.geciken ? `<span class="mc-badge mc-badge-danger">Geciken: ${oz.geciken}</span>` : ""}`;
        }
        const projBody = document.getElementById("kr-proje-body");
        if (projBody) {
          const projs = d.projeler || [];
          projBody.innerHTML = projs.map(p => {
            const stCls = p.status === "Tamamlandı" ? "mc-badge-success"
                        : p.status === "Devam Ediyor" ? "mc-badge-info" : "mc-badge-warning";
            return `<tr>
              <td>${esc(p.name)}</td>
              <td><span class="mc-badge ${stCls}">${esc(p.status)}</span></td>
              <td><div class="kr-perf-bar-wrap">
                <div class="kr-perf-bar-track"><div class="kr-perf-bar-fill" style="width:${p.progress}%;background:${scoreColor(p.progress)};"></div></div>
                <div class="kr-perf-pct" style="color:${scoreColor(p.progress)}">${p.progress}%</div>
              </div></td>
              <td style="font-size:11px;">${esc(p.start_date || "—")}</td>
              <td style="font-size:11px;">${esc(p.end_date || "—")}</td>
            </tr>`;
          }).join("") || EMPTY_ROW_1(5);
        }
      })
      .catch(() => {
        setHtml("kr-fal-stats", `<div class="kr-loading" style="grid-column:span 4;color:#ef4444;">Yüklenemedi.</div>`);
        setHtml("kr-geciken-body", ERROR_ROW_1(4));
        setHtml("kr-proje-body", ERROR_ROW_1(5));
      });
  }

  // ── Rapor 6: Bireysel ────────────────────────────────────────────────────────
  function loadBireysel() {
    setHtml("kr-bireysel-body", `<tr><td colspan="8" style="text-align:center;padding:24px;color:#94a3b8;">Yükleniyor…</td></tr>`);
    setHtml("kr-ipi-body", `<tr><td colspan="7" style="text-align:center;padding:24px;color:#94a3b8;">Yükleniyor…</td></tr>`);
    setHtml("kr-bir-saglik", `<div class="kr-loading" style="grid-column:span 4;padding:12px;">Yükleniyor…</div>`);
    fetchJson(apiUrl("bireysel"), { year })
      .then(res => {
        if (!res.success) {
          setHtml("kr-bireysel-body", ERROR_ROW_1(8));
          setHtml("kr-ipi-body", ERROR_ROW_1(7));
          setHtml("kr-bir-saglik", "");
          return;
        }

        // Sağlık özeti
        const sk = res.saglik || {};
        const toplam = res.toplam_pg || 0;
        setHtml("kr-bir-saglik", toplam ? `
          <div class="mc-stat-card mc-stat-emerald">
            <div class="mc-stat-label">Hedefte (≥%80)</div>
            <div class="mc-stat-value">${sk.yesil || 0}</div>
          </div>
          <div class="mc-stat-card mc-stat-amber">
            <div class="mc-stat-label">Riskli (%50–79)</div>
            <div class="mc-stat-value">${sk.sari || 0}</div>
          </div>
          <div class="mc-stat-card" style="background:#fef2f2;">
            <div class="mc-stat-label" style="color:#ef4444;">Kritik (&lt;%50)</div>
            <div class="mc-stat-value" style="color:#ef4444;">${sk.kirmizi || 0}</div>
          </div>
          <div class="mc-stat-card mc-stat-indigo">
            <div class="mc-stat-label">Toplam PG</div>
            <div class="mc-stat-value">${toplam}</div>
            <div class="mc-stat-sub">${sk.veri_yok || 0} veri yok</div>
          </div>` : "");

        const birToplam = document.getElementById("kr-bir-toplam");
        if (birToplam) birToplam.textContent = `${res.ipi_detail?.length || 0} PG`;

        // Kullanıcı özet
        if (!res.data || !res.data.length) {
          setHtml("kr-bireysel-body", EMPTY_ROW_1(8));
        } else {
          setHtml("kr-bireysel-body", res.data.map((row, i) => {
            const pct = row.ort_basari;
            const bar = pct != null
              ? `<div class="kr-perf-bar-wrap"><div class="kr-perf-bar-track"><div class="kr-perf-bar-fill" style="width:${Math.min(100,pct)}%;background:${scoreColor(pct)};"></div></div><div class="kr-perf-pct" style="color:${scoreColor(pct)}">${pct}%</div></div>`
              : `<span style="color:#94a3b8;font-size:12px;">—</span>`;
            const tamamPct = row.pg_sayisi ? Math.round(row.veri_girilmis / row.pg_sayisi * 100) : 0;
            return `<tr>
              <td style="color:#94a3b8;font-size:12px;">${i+1}</td>
              <td>
                <div style="font-weight:500;">${esc(row.ad)}</div>
                <div style="font-size:11px;color:#94a3b8;">${esc(row.email)}</div>
              </td>
              <td style="text-align:center;">${row.pg_sayisi}</td>
              <td style="text-align:center;">
                ${row.veri_girilmis}
                <span style="font-size:10px;color:${tamamPct===100?'#10b981':'#94a3b8'};"> (%${tamamPct})</span>
              </td>
              <td style="text-align:center;font-weight:600;color:#6366f1;">${row.toplam_giris}</td>
              <td style="font-size:11px;white-space:nowrap;">${esc(row.son_giris || "—")}</td>
              <td style="text-align:center;font-weight:600;color:${scoreColor(pct)}">${pct != null ? pct + "%" : "—"}</td>
              <td style="min-width:120px;">${bar}</td>
            </tr>`;
          }).join(""));
        }

        // IPI detay
        const detail = res.ipi_detail || [];
        setHtml("kr-ipi-body", detail.map(r => {
          const pct = r.pct;
          const badge = pct == null ? `<span style="color:#94a3b8;">—</span>`
            : `<span style="font-weight:700;color:${scoreColor(pct)}">${pct}%</span>`;
          return `<tr>
            <td style="font-size:12px;">${esc(r.ad)}</td>
            <td style="font-size:11px;color:#6366f1;">${esc(r.code)}</td>
            <td>${esc(r.name)}</td>
            <td style="font-size:11px;">${esc(r.hedef ?? "—")}</td>
            <td style="font-size:11px;font-weight:500;">${esc(r.gercek ?? "—")}</td>
            <td>${badge}</td>
            <td style="font-size:11px;color:#94a3b8;">${esc(r.source)}</td>
          </tr>`;
        }).join("") || EMPTY_ROW_1(7));
      })
      .catch(() => {
        setHtml("kr-bireysel-body", ERROR_ROW_1(8));
        setHtml("kr-ipi-body", ERROR_ROW_1(7));
        setHtml("kr-bir-saglik", "");
      });
  }

  // ── Rapor 7: Veri Giriş Durumu ───────────────────────────────────────────────
  function loadVeriDurumu() {
    setHtml("kr-vd-stats", '<div class="kr-loading" style="grid-column:span 3;padding:24px;">Yükleniyor…</div>');
    fetchJson(apiUrl("veri-durumu"), { year })
      .then(res => {
        if (!res.success) {
          setHtml("kr-vd-stats", `<div class="kr-loading" style="grid-column:span 3;color:#ef4444;">${esc(res.message || "Yüklenemedi.")}</div>`);
          setHtml("kr-vd-girilen", ERROR_ROW_1(6));
          setHtml("kr-vd-girilmeyen", ERROR_ROW_1(3));
          return;
        }
        const d = res.data;

        setHtml("kr-vd-stats", `
          <div class="mc-stat-card mc-stat-indigo" data-card-code="k_rapor_veri_durumu.toplam_pg">
            <div class="mc-stat-label">Toplam PG</div>
            <div class="mc-stat-value">${d.toplam}</div>
          </div>
          <div class="mc-stat-card mc-stat-emerald" data-card-code="k_rapor_veri_durumu.veri_girilmis">
            <div class="mc-stat-label">Veri Girilmiş</div>
            <div class="mc-stat-value">${d.girilen_sayisi}</div>
            <div class="mc-stat-sub">%${d.tamamlanma_orani} tamamlandı</div>
          </div>
          <div class="mc-stat-card mc-stat-amber" data-card-code="k_rapor_veri_durumu.eksik">
            <div class="mc-stat-label">Eksik</div>
            <div class="mc-stat-value">${d.girilmeyen_sayisi}</div>
            <div class="mc-stat-sub">Veri girilmemiş PG</div>
          </div>`);

        const cntGir = document.getElementById("kr-vd-girilen-cnt");
        const cntGir2 = document.getElementById("kr-vd-girilmeyen-cnt");
        if (cntGir) cntGir.textContent = d.girilen_sayisi;
        if (cntGir2) cntGir2.textContent = d.girilmeyen_sayisi;

        setHtml("kr-vd-girilen", (d.girilen || []).map(r => `
          <tr>
            <td style="font-size:11px;color:#6366f1;">${esc(r.kpi_code)}</td>
            <td>${esc(r.kpi_name)}</td>
            <td style="font-size:11px;">${esc(r.surec_name)}</td>
            <td style="white-space:nowrap;font-size:11px;">${esc(r.son_tarih || "")}</td>
            <td style="font-weight:600;">${esc(r.son_deger ?? "")}</td>
            <td style="font-size:11px;">${esc(r.giren || "")}</td>
          </tr>`).join("") || EMPTY_ROW_1(6));

        setHtml("kr-vd-girilmeyen", (d.girilmeyen || []).map(r => `
          <tr>
            <td style="font-size:11px;color:#ef4444;">${esc(r.kpi_code)}</td>
            <td>${esc(r.kpi_name)}</td>
            <td style="font-size:11px;">${esc(r.surec_name)}</td>
          </tr>`).join("") || `<tr><td colspan="3" style="text-align:center;padding:20px;color:#94a3b8;">Eksik PG yok.</td></tr>`);
      })
      .catch(() => {
        setHtml("kr-vd-stats", `<div class="kr-loading" style="grid-column:span 3;color:#ef4444;">Yüklenemedi.</div>`);
        setHtml("kr-vd-girilen", ERROR_ROW_1(6));
        setHtml("kr-vd-girilmeyen", ERROR_ROW_1(3));
      });
  }

  // ── Rapor 8: Risk ────────────────────────────────────────────────────────────
  function loadRisk() {
    setHtml("kr-risk-body",    `<tr><td colspan="5" style="text-align:center;padding:24px;color:#94a3b8;">Yükleniyor…</td></tr>`);
    setHtml("kr-olgunluk-list", '<div class="kr-loading" style="padding:24px;">Yükleniyor…</div>');
    setHtml("kr-bn-body",      `<tr><td colspan="5" style="text-align:center;padding:24px;color:#94a3b8;">Yükleniyor…</td></tr>`);

    fetchJson(apiUrl("risk"))
      .then(res => {
        if (!res.success) {
          setHtml("kr-risk-body", ERROR_ROW_1(6));
          setHtml("kr-olgunluk-list", ERROR_HTML);
          setHtml("kr-bn-body", ERROR_ROW_1(5));
          return;
        }
        const d = res.data;

        setHtml("kr-risk-body", (d.risk_listesi || []).map(r => {
          const rpn = r.rpn || 0;
          const rpnColor = rpn >= 15 ? "#ef4444" : rpn >= 8 ? "#f59e0b" : "#10b981";
          const rpnLabel = rpn >= 15 ? "Kritik" : rpn >= 8 ? "Yüksek" : rpn >= 4 ? "Orta" : "Düşük";
          const statusClass = r.status === "Açık" ? "mc-badge-danger" : r.status === "Azaltıldı" ? "mc-badge-warning" : "mc-badge-success";
          return `<tr>
            <td>${esc(r.title)}</td>
            <td style="text-align:center;">${r.probability} <span style="font-size:10px;color:#94a3b8;">/5</span></td>
            <td style="text-align:center;">${r.impact} <span style="font-size:10px;color:#94a3b8;">/5</span></td>
            <td style="text-align:center;"><span style="font-weight:700;color:${rpnColor}">${rpn}</span> <span style="font-size:10px;color:#94a3b8;">(${rpnLabel})</span></td>
            <td><span class="mc-badge ${statusClass}">${esc(r.status)}</span></td>
            <td style="font-size:11px;color:#64748b;">${esc(r.source_type)}</td>
          </tr>`;
        }).join("") || EMPTY_ROW_1(6));

        setHtml("kr-bn-body", (d.darbogaz || []).map(b => {
          const sevClass = b.severity === "Yüksek" ? "mc-badge-danger" : b.severity === "Orta" ? "mc-badge-warning" : "mc-badge-info";
          return `<tr>
            <td>${esc(b.surec)}</td>
            <td><span class="mc-badge ${sevClass}">${esc(b.severity)}</span></td>
            <td style="font-size:11px;">${esc(b.note)}</td>
            <td style="white-space:nowrap;font-size:11px;">${esc(b.triggered_at || "")}</td>
            <td>${b.cozuldu ? `<span style="color:#10b981;">${esc(b.resolved_at || "Çözüldü")}</span>` : '<span style="color:#f59e0b;">Açık</span>'}</td>
          </tr>`;
        }).join("") || EMPTY_ROW_1(5));

        const olgunlukEl = document.getElementById("kr-olgunluk-list");
        if (olgunlukEl) {
          olgunlukEl.innerHTML = (d.olgunluk || []).map(m => {
            const dots = [1,2,3,4,5].map(n => `<span class="kr-olg-dot ${n <= (m.maturity_level || 0) ? "filled" : ""}"></span>`).join("");
            return `<div class="kr-olgunluk-item">
              <div class="kr-olg-name" title="${esc(m.surec)}">${esc(m.surec)}</div>
              <div class="kr-olg-level">${dots}</div>
            </div>`;
          }).join("") || EMPTY_HTML;
        }
      })
      .catch(() => {
        setHtml("kr-risk-body", ERROR_ROW_1(5));
        setHtml("kr-olgunluk-list", ERROR_HTML);
        setHtml("kr-bn-body", ERROR_ROW_1(5));
      });
  }

  // ── Rapor 9: Denetim ─────────────────────────────────────────────────────────
  function loadDenetim() {
    const gun = document.getElementById("kr-denetim-gun")?.value || 30;
    setHtml("kr-aktif-users",  '<div class="kr-loading" style="padding:24px;">Yükleniyor…</div>');
    setHtml("kr-denetim-body", `<tr><td colspan="5" style="text-align:center;padding:24px;color:#94a3b8;">Yükleniyor…</td></tr>`);

    fetchJson(apiUrl("denetim"), { gun })
      .then(res => {
        if (!res.success) {
          setHtml("kr-aktif-users", ERROR_HTML);
          setHtml("kr-denetim-body", ERROR_ROW_1(5));
          return;
        }
        const d = res.data;

        const canvas = document.getElementById("kr-denetim-chart");
        if (canvas) {
          if (denetimChart) denetimChart.destroy();
          const labels = Object.keys(d.action_dagilim || {});
          const vals   = Object.values(d.action_dagilim || {});
          if (labels.length) {
            const colors = ["#6366f1","#10b981","#f59e0b","#ef4444","#3b82f6","#8b5cf6","#ec4899","#14b8a6","#f97316","#84cc16"];
            denetimChart = new Chart(canvas, {
              type: "doughnut",
              data: { labels, datasets: [{ data: vals, backgroundColor: colors.slice(0, labels.length) }] },
              options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: "bottom", labels: { font: { size: 11 } } } } }
            });
          }
        }

        const usersEl = document.getElementById("kr-aktif-users");
        if (usersEl) {
          const list = d.aktif_kullanicilar || [];
          const maxCnt = list[0]?.islem_sayisi || 1;
          usersEl.innerHTML = list.map(u => `
            <div class="kr-user-bar-row">
              <div class="kr-user-name" title="${esc(u.kullanici)}">${esc(u.kullanici)}</div>
              <div class="kr-user-track"><div class="kr-user-fill" style="width:${Math.round(u.islem_sayisi / maxCnt * 100)}%;"></div></div>
              <div class="kr-user-cnt">${u.islem_sayisi}</div>
            </div>`).join("") || EMPTY_HTML;
        }

        setHtml("kr-denetim-body", (d.kayitlar || []).map(r => `
          <tr>
            <td style="white-space:nowrap;font-size:11px;">${esc(r.tarih || "")}</td>
            <td style="font-size:12px;">${esc(r.kullanici)}</td>
            <td><span class="mc-badge mc-badge-info">${esc(r.action)}</span></td>
            <td style="font-size:11px;">${esc(r.resource_type)}</td>
            <td style="font-size:11px;">${esc(r.description)}</td>
          </tr>`).join("") || EMPTY_ROW_1(5));
      })
      .catch(() => {
        setHtml("kr-aktif-users", ERROR_HTML);
        setHtml("kr-denetim-body", ERROR_ROW_1(5));
      });
  }

  const denetimGun = document.getElementById("kr-denetim-gun");
  if (denetimGun) denetimGun.addEventListener("change", () => { loaded["denetim"] = true; loadDenetim(); });

  // ── Rapor 10: Uyarı Merkezi ──────────────────────────────────────────────────
  function loadUyari() {
    setHtml("kr-uyari-stats",       `<div class="kr-loading" style="grid-column:span 3;padding:12px;">Yükleniyor…</div>`);
    setHtml("kr-kritik-pg-body",    `<tr><td colspan="6" style="text-align:center;padding:20px;color:#94a3b8;">Yükleniyor…</td></tr>`);
    setHtml("kr-geciken-faal-body", `<tr><td colspan="6" style="text-align:center;padding:20px;color:#94a3b8;">Yükleniyor…</td></tr>`);
    setHtml("kr-uyari-risk-body",   `<tr><td colspan="5" style="text-align:center;padding:20px;color:#94a3b8;">Yükleniyor…</td></tr>`);

    fetchJson(apiUrl("uyari"), { year })
      .then(res => {
        if (!res.success) {
          setHtml("kr-uyari-stats", ERROR_HTML);
          setHtml("kr-kritik-pg-body", ERROR_ROW_1(6));
          setHtml("kr-geciken-faal-body", ERROR_ROW_1(6));
          setHtml("kr-uyari-risk-body", ERROR_ROW_1(5));
          return;
        }
        const d = res.data;
        const oz = d.ozet || {};

        setHtml("kr-uyari-stats", `
          <div class="mc-stat-card" style="background:#fef2f2;" data-card-code="k_rapor_uyari.kritik_pg">
            <div class="mc-stat-icon" style="color:#ef4444;"><i class="fas fa-circle-exclamation"></i></div>
            <div class="mc-stat-label">Kritik PG</div>
            <div class="mc-stat-value" style="color:#ef4444;">${oz.kritik_pg_sayisi || 0}</div>
            <div class="mc-stat-sub">Başarı &lt;%50</div>
          </div>
          <div class="mc-stat-card mc-stat-amber" data-card-code="k_rapor_uyari.geciken_faaliyet">
            <div class="mc-stat-icon"><i class="fas fa-hourglass-end"></i></div>
            <div class="mc-stat-label">Geciken Faaliyet</div>
            <div class="mc-stat-value">${oz.geciken_faaliyet_sayisi || 0}</div>
            <div class="mc-stat-sub">Bitiş tarihi geçmiş</div>
          </div>
          <div class="mc-stat-card mc-stat-amber" data-card-code="k_rapor_uyari.yuksek_risk">
            <div class="mc-stat-icon"><i class="fas fa-fire"></i></div>
            <div class="mc-stat-label">Yüksek Risk</div>
            <div class="mc-stat-value">${oz.yuksek_risk_sayisi || 0}</div>
            <div class="mc-stat-sub">RPN &gt; 10</div>
          </div>`);

        setHtml("kr-kritik-pg-body", (d.kritik_pg || []).map(r => `
          <tr>
            <td style="font-size:11px;color:#6366f1;">${esc(r.code)}</td>
            <td>${esc(r.name)}</td>
            <td style="font-size:11px;">${esc(r.surec)}</td>
            <td style="font-size:11px;">${esc(r.hedef ?? "—")}</td>
            <td style="font-size:11px;font-weight:600;">${esc(r.gercek ?? "—")}</td>
            <td><span style="font-weight:700;color:#ef4444;">${r.pct}%</span></td>
          </tr>`).join("") || EMPTY_ROW_1(6));

        setHtml("kr-uyari-risk-body", (d.yuksek_risk || []).map(r => {
          const c = r.rpn >= 20 ? "#ef4444" : "#f59e0b";
          return `<tr>
            <td style="font-size:12px;">${esc(r.title)}</td>
            <td style="text-align:center;">${r.probability}</td>
            <td style="text-align:center;">${r.impact}</td>
            <td style="text-align:center;font-weight:700;color:${c}">${r.rpn}</td>
            <td><span class="mc-badge mc-badge-info">${esc(r.status)}</span></td>
          </tr>`;
        }).join("") || EMPTY_ROW_1(5));

        setHtml("kr-geciken-faal-body", (d.geciken_faaliyetler || []).map(a => `
          <tr>
            <td style="font-size:12px;">${esc(a.name)}</td>
            <td style="font-size:11px;">${esc(a.surec)}</td>
            <td style="white-space:nowrap;font-size:11px;">${esc(a.end_date)}</td>
            <td style="font-weight:700;color:#ef4444;">${a.gecikme_gun} gün</td>
            <td><span class="mc-badge mc-badge-warning">${esc(a.status)}</span></td>
            <td>
              <div class="kr-perf-bar-wrap" style="min-width:80px;">
                <div class="kr-perf-bar-track"><div class="kr-perf-bar-fill" style="width:${a.progress}%;background:#6366f1;"></div></div>
                <div class="kr-perf-pct">${a.progress}%</div>
              </div>
            </td>
          </tr>`).join("") || EMPTY_ROW_1(6));
      })
      .catch(() => {
        setHtml("kr-uyari-stats", ERROR_HTML);
        setHtml("kr-kritik-pg-body", ERROR_ROW_1(6));
        setHtml("kr-geciken-faal-body", ERROR_ROW_1(6));
        setHtml("kr-uyari-risk-body", ERROR_ROW_1(5));
      });
  }

  // ── Rapor 11: K-Vektör ───────────────────────────────────────────────────────
  function loadKVektor() {
    setHtml("kr-kv-bars", '<div class="kr-loading" style="padding:24px;">Yükleniyor…</div>');
    fetchJson(apiUrl("k-vektor"), { year })
      .then(res => {
        if (!res.success) { setHtml("kr-kv-bars", ERROR_HTML); setHtml("kr-kv-sub-body", ERROR_ROW_1(3)); return; }
        const d = res.data;
        const strats = d.strateji || [];

        // Donut chart
        const canvas = document.getElementById("kr-kv-chart");
        if (canvas && strats.length) {
          if (kvektorChart) kvektorChart.destroy();
          const colors = ["#6366f1","#10b981","#f59e0b","#ef4444","#3b82f6","#8b5cf6","#ec4899","#14b8a6","#f97316","#84cc16"];
          kvektorChart = new Chart(canvas, {
            type: "doughnut",
            data: {
              labels: strats.map(s => (s.code ? s.code + " " : "") + s.title),
              datasets: [{ data: strats.map(s => s.pct), backgroundColor: colors.slice(0, strats.length), borderWidth: 2 }]
            },
            options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: "bottom", labels: { font: { size: 11 } } } } }
          });
        }

        // Bar listesi
        const barsEl = document.getElementById("kr-kv-bars");
        if (barsEl) {
          barsEl.innerHTML = strats.length ? strats.map(s => `
            <div class="kr-bar-row" style="padding:8px 16px;">
              <div class="kr-bar-label" style="min-width:90px;">${esc((s.code ? s.code + " " : "") + s.title)}</div>
              <div class="kr-bar-track"><div class="kr-bar-fill" style="width:${s.pct}%;"></div></div>
              <div class="kr-bar-pct">%${s.pct}</div>
            </div>`).join("") : EMPTY_HTML;
        }

        // Alt strateji tablosu
        const subs = d.alt_strateji || [];
        setHtml("kr-kv-sub-body", subs.map(s => `
          <tr>
            <td style="font-size:11px;color:#6366f1;">${esc(s.parent_code ? s.parent_code + "." : "")}${esc(s.code)}</td>
            <td>${esc(s.title)}</td>
            <td style="font-weight:600;color:${scoreColor(s.score)}">${s.score}</td>
          </tr>`).join("") || EMPTY_ROW_1(3));
      })
      .catch(() => { setHtml("kr-kv-bars", ERROR_HTML); setHtml("kr-kv-sub-body", ERROR_ROW_1(3)); });
  }

  function loadEvm() {
    setHtml("kr-evm-body", `<tr><td colspan="8" style="text-align:center;padding:24px;color:#94a3b8;">Yükleniyor…</td></tr>`);
    fetchJson(apiUrl("evm"), { year })
      .then(res => {
        if (!res.success) { setHtml("kr-evm-body", ERROR_ROW_1(8)); return; }
        const rows = res.data || [];
        setHtml("kr-evm-body", rows.map(r => {
          const spiColor = r.spi == null ? "#94a3b8" : r.spi >= 1 ? "#10b981" : r.spi >= 0.8 ? "#f59e0b" : "#ef4444";
          const cpiColor = r.cpi == null ? "#94a3b8" : r.cpi >= 1 ? "#10b981" : r.cpi >= 0.8 ? "#f59e0b" : "#ef4444";
          return `<tr>
            <td style="white-space:nowrap;font-size:11px;">${esc(r.snapshot_date)}</td>
            <td style="font-size:12px;">${esc(r.project_name || "#" + r.project_id)}</td>
            <td style="font-size:12px;">${r.pv ?? "—"}</td>
            <td style="font-size:12px;">${r.ev ?? "—"}</td>
            <td style="font-size:12px;">${r.ac ?? "—"}</td>
            <td style="font-weight:700;color:${spiColor}">${r.spi ?? "—"}</td>
            <td style="font-weight:700;color:${cpiColor}">${r.cpi ?? "—"}</td>
            <td style="font-size:11px;color:#94a3b8;">${r.spi != null ? (r.spi >= 1 ? "Zamanında" : "Geride") : "—"}</td>
          </tr>`;
        }).join("") || `<tr><td colspan="8" style="text-align:center;padding:24px;color:#94a3b8;">Kayıt yok.</td></tr>`);
      })
      .catch(() => setHtml("kr-evm-body", ERROR_ROW_1(8)));
  }

  // ── Rapor 12: Stratejik Analiz ───────────────────────────────────────────────
  function loadStratejikAnaliz() {
    setHtml("kr-sa-swot",   '<div class="kr-loading">Yükleniyor…</div>');
    setHtml("kr-sa-tows",   '<div class="kr-loading">Yükleniyor…</div>');
    setHtml("kr-sa-pestel", '<div class="kr-loading">Yükleniyor…</div>');
    setHtml("kr-sa-porter", '<div class="kr-loading">Yükleniyor…</div>');
    fetchJson(apiUrl("stratejik-analiz"), { year })
      .then(res => {
        if (!res.success) {
          ["kr-sa-swot","kr-sa-tows","kr-sa-pestel","kr-sa-porter"].forEach(id => setHtml(id, ERROR_HTML));
          return;
        }
        const d = res.data;

        // SWOT
        const sw = d.swot;
        const swotEl = document.getElementById("kr-sa-swot");
        const swotDate = document.getElementById("kr-sa-swot-date");
        if (swotDate) swotDate.textContent = sw.year_label ? `${sw.year_label} — ${sw.guncelleme || ""}` : (sw.guncelleme || "");
        if (swotEl) {
          swotEl.innerHTML = sw.mevcut ? `<div class="mc-grid-2" style="gap:8px;">
            ${[["Güçlü Yön","strengths","#10b981"],["Zayıf Yön","weaknesses","#ef4444"],["Fırsat","opportunities","#3b82f6"],["Tehdit","threats","#f59e0b"]].map(([lbl,k,c]) =>
              `<div style="text-align:center;padding:16px;border-radius:8px;background:#f8fafc;">
                <div style="font-size:24px;font-weight:700;color:${c};">${sw[k]}</div>
                <div style="font-size:12px;color:#64748b;margin-top:4px;">${lbl}</div>
              </div>`).join("")}
          </div>` : '<div style="text-align:center;padding:24px;color:#94a3b8;font-size:13px;">Bu yıl için SWOT analizi yok.</div>';
        }

        // TOWS
        const tw = d.tows;
        const towsEl = document.getElementById("kr-sa-tows");
        const towsDate = document.getElementById("kr-sa-tows-date");
        if (towsDate) towsDate.textContent = tw.year_label ? `${tw.year_label} — ${tw.guncelleme || ""}` : (tw.guncelleme || "");
        if (towsEl) {
          towsEl.innerHTML = tw.mevcut ? `<div class="mc-grid-2" style="gap:8px;">
            ${[["SO Stratejileri","so","#10b981"],["ST Stratejileri","st","#6366f1"],["WO Stratejileri","wo","#3b82f6"],["WT Stratejileri","wt","#ef4444"]].map(([lbl,k,c]) =>
              `<div style="text-align:center;padding:16px;border-radius:8px;background:#f8fafc;">
                <div style="font-size:24px;font-weight:700;color:${c};">${tw[k]}</div>
                <div style="font-size:12px;color:#64748b;margin-top:4px;">${lbl}</div>
              </div>`).join("")}
          </div>` : '<div style="text-align:center;padding:24px;color:#94a3b8;font-size:13px;">Bu yıl için TOWS matrisi yok.</div>';
        }

        // PESTEL
        const pe = d.pestel;
        const pestelEl = document.getElementById("kr-sa-pestel");
        const pestelDate = document.getElementById("kr-sa-pestel-date");
        if (pestelDate) pestelDate.textContent = pe.year_label ? `${pe.year_label} — ${pe.guncelleme || ""}` : (pe.guncelleme || "");
        if (pestelEl) {
          pestelEl.innerHTML = pe.mevcut ? [
            ["P","political","Siyasi","#6366f1"],["E","economic","Ekonomik","#10b981"],
            ["S","social","Sosyal","#f59e0b"],["T","technological","Teknolojik","#3b82f6"],
            ["E","environmental","Çevresel","#84cc16"],["L","legal","Yasal","#ef4444"]
          ].map(([abbr,k,lbl,c]) => `
            <div class="kr-bar-row" style="padding:6px 12px;">
              <div class="kr-bar-label" style="min-width:100px;"><span style="font-weight:700;color:${c};">${abbr}</span> ${lbl}</div>
              <div class="kr-bar-track"><div class="kr-bar-fill" style="width:${Math.min(100, (pe[k] || 0) * 20)}%;background:${c};"></div></div>
              <div class="kr-bar-pct">${pe[k]}</div>
            </div>`).join("") : '<div style="text-align:center;padding:24px;color:#94a3b8;font-size:13px;">Bu yıl için PESTEL analizi yok.</div>';
        }

        // Porter
        const po = d.porter;
        const porterEl = document.getElementById("kr-sa-porter");
        const porterDate = document.getElementById("kr-sa-porter-date");
        if (porterDate) porterDate.textContent = po.year_label ? `${po.year_label} — ${po.guncelleme || ""}` : (po.guncelleme || "");
        if (porterEl) {
          porterEl.innerHTML = po.mevcut ? [
            ["rivalry","Rekabet Yoğunluğu"],["supplier","Tedarikçi Gücü"],["buyer","Alıcı Gücü"],
            ["new_entrant","Yeni Giriş Tehdidi"],["substitute","İkame Tehdidi"]
          ].map(([k,lbl]) => {
            const sc = po[k];
            const w = sc != null ? sc / 5 * 100 : 0;
            const c = sc == null ? "#94a3b8" : sc >= 4 ? "#ef4444" : sc >= 3 ? "#f59e0b" : "#10b981";
            return `<div class="kr-bar-row" style="padding:6px 12px;">
              <div class="kr-bar-label" style="min-width:160px;">${lbl}</div>
              <div class="kr-bar-track"><div class="kr-bar-fill" style="width:${w}%;background:${c};"></div></div>
              <div class="kr-bar-pct" style="color:${c}">${sc ?? "—"}</div>
            </div>`;
          }).join("") : '<div style="text-align:center;padding:24px;color:#94a3b8;font-size:13px;">Bu yıl için Porter analizi yok.</div>';
        }
      })
      .catch(() => ["kr-sa-swot","kr-sa-tows","kr-sa-pestel","kr-sa-porter"].forEach(id => setHtml(id, ERROR_HTML)));
  }

  // ── Rapor 13: Paydaş ─────────────────────────────────────────────────────────
  function loadPaydas() {
    setHtml("kr-pd-body",  `<tr><td colspan="5" style="text-align:center;padding:24px;color:#94a3b8;">Yükleniyor…</td></tr>`);
    setHtml("kr-pd-anket", '<div class="kr-loading">Yükleniyor…</div>');
    fetchJson(apiUrl("paydas"), { year })
      .then(res => {
        if (!res.success) { setHtml("kr-pd-body", ERROR_ROW_1(5)); setHtml("kr-pd-anket", ERROR_HTML); return; }
        const d = res.data;

        const toplam = document.getElementById("kr-pd-toplam");
        if (toplam) toplam.textContent = `${d.toplam_paydas} paydaş`;
        const anketToplam = document.getElementById("kr-pd-anket-toplam");
        if (anketToplam) anketToplam.textContent = `${d.toplam_anket} anket`;

        setHtml("kr-pd-body", (d.paydas_listesi || []).map(s => {
          const infBar = s.influence != null ? `<div style="display:flex;align-items:center;gap:4px;"><div style="height:6px;border-radius:3px;background:#6366f1;width:${s.influence * 10}px;"></div><span style="font-size:11px;">${s.influence}</span></div>` : "—";
          const intBar = s.interest != null ? `<div style="display:flex;align-items:center;gap:4px;"><div style="height:6px;border-radius:3px;background:#10b981;width:${s.interest * 10}px;"></div><span style="font-size:11px;">${s.interest}</span></div>` : "—";
          return `<tr>
            <td style="font-weight:500;">${esc(s.name)}</td>
            <td style="font-size:11px;">${esc(s.role)}</td>
            <td>${infBar}</td>
            <td>${intBar}</td>
            <td style="font-size:11px;">${esc(s.strategy)}</td>
          </tr>`;
        }).join("") || EMPTY_ROW_1(5));

        const anketEl = document.getElementById("kr-pd-anket");
        if (anketEl) {
          const list = d.anket_ozeti || [];
          anketEl.innerHTML = list.length ? list.map(a => `
            <div class="kr-bar-row" style="padding:8px 16px;">
              <div class="kr-bar-label" style="min-width:120px;">${esc(a.tip)}</div>
              <div class="kr-bar-track"><div class="kr-bar-fill" style="width:${a.ort_skor * 20}%;background:${scoreColor(a.ort_skor * 20)};"></div></div>
              <div class="kr-bar-pct" style="color:${scoreColor(a.ort_skor * 20)}">${a.ort_skor} <span style="font-size:10px;color:#94a3b8;">(${a.sayi})</span></div>
            </div>`).join("") : '<div style="text-align:center;padding:24px;color:#94a3b8;font-size:13px;">Anket verisi yok.</div>';
        }
      })
      .catch(() => { setHtml("kr-pd-body", ERROR_ROW_1(5)); setHtml("kr-pd-anket", ERROR_HTML); });
  }

  // ── Rapor 14: Rekabet & A3 ───────────────────────────────────────────────────
  function loadRekabet() {
    setHtml("kr-rek-content", '<div class="kr-loading" style="padding:24px;">Yükleniyor…</div>');
    setHtml("kr-a3-body", `<tr><td colspan="4" style="text-align:center;padding:24px;color:#94a3b8;">Yükleniyor…</td></tr>`);
    fetchJson(apiUrl("rekabet"), { year })
      .then(res => {
        if (!res.success) { setHtml("kr-rek-content", ERROR_HTML); setHtml("kr-a3-body", ERROR_ROW_1(4)); return; }
        const d = res.data;

        const rekToplam = document.getElementById("kr-rek-toplam");
        if (rekToplam) rekToplam.textContent = `${d.toplam_rakip} rakip`;
        const a3Toplam = document.getElementById("kr-a3-toplam");
        if (a3Toplam) a3Toplam.textContent = `${d.toplam_a3} rapor`;

        const rekEl = document.getElementById("kr-rek-content");
        if (rekEl) {
          const list = d.rekabet_listesi || [];
          if (!list.length) {
            rekEl.innerHTML = '<div style="text-align:center;padding:24px;color:#94a3b8;font-size:13px;">Rekabetçi analiz verisi yok.</div>';
          } else {
            rekEl.innerHTML = list.map(c => `
              <div style="padding:12px 16px;border-bottom:1px solid #f1f5f9;">
                <div style="font-weight:600;margin-bottom:6px;">${esc(c.competitor)}</div>
                <div style="display:flex;flex-wrap:wrap;gap:8px;">
                  ${(c.dimensions || []).map(dim => `
                    <div style="font-size:11px;background:#f8fafc;border-radius:6px;padding:4px 10px;">
                      <span style="color:#64748b;">${esc(dim.dimension)}:</span>
                      <span style="font-weight:600;color:#6366f1;">${dim.our_score ?? "—"}</span>
                      <span style="color:#94a3b8;"> vs </span>
                      <span style="font-weight:600;color:#ef4444;">${dim.their_score ?? "—"}</span>
                    </div>`).join("")}
                </div>
              </div>`).join("");
          }
        }

        setHtml("kr-a3-body", (d.a3_listesi || []).map(r => `
          <tr>
            <td style="font-size:12px;">${esc(r.problem)}</td>
            <td style="font-size:11px;">${esc(r.source_type)}</td>
            <td style="font-size:11px;">${esc(r.countermeasures)}</td>
            <td style="white-space:nowrap;font-size:11px;">${esc(r.tarih || "")}</td>
          </tr>`).join("") || EMPTY_ROW_1(4));
      })
      .catch(() => { setHtml("kr-rek-content", ERROR_HTML); setHtml("kr-a3-body", ERROR_ROW_1(4)); });
  }

  const denetimGun2 = document.getElementById("kr-denetim-gun");
  if (denetimGun2) denetimGun2.addEventListener("change", () => { delete loaded["denetim"]; loadDenetim(); });

  // ── Excel Export ─────────────────────────────────────────────────────────────
  function getActiveTab() {
    const btn = document.querySelector(".kr-tab.active");
    return btn ? btn.dataset.tab : "kurumsal";
  }

  function exportExcel() {
    const tab       = getActiveTab();
    const exportUrl = ROOT.dataset.apiExportExcel || "";
    if (!exportUrl) return;
    const u = new URL(exportUrl, location.origin);
    u.searchParams.set("year", year);
    u.searchParams.set("tab",  tab);
    window.location.href = u.toString();
  }

  document.getElementById("kr-export-btn")?.addEventListener("click", exportExcel);

// ── Yeni Rapor 1: PG Performans Dağılımı ─────────────────────────────────────

  let pgdHistChart = null, pgdBarChart = null;
  function loadPgDagilim() {
    setHtml("kr-pgd-ozet", '<div class="kr-loading" style="grid-column:span 4;padding:12px;">Yükleniyor…</div>');
    setHtml("kr-pgd-body", '<tr><td colspan="5" style="text-align:center;padding:24px;color:#94a3b8;">Yükleniyor…</td></tr>');
    fetchJson(apiUrl("pg-dagilim"), { year })
      .then(res => {
        if (!res.success) { setHtml("kr-pgd-ozet", ERROR_HTML); setHtml("kr-pgd-body", ERROR_ROW_1(5)); return; }
        const d = res.data;
        const oz = d.ozet || {};
        setHtml("kr-pgd-ozet", oz.toplam ? `
          <div class="mc-stat-card mc-stat-indigo" data-card-code="k_rapor_pg_dagilim.toplam_pg">
            <div class="mc-stat-label">Toplam PG</div>
            <div class="mc-stat-value">${oz.toplam}</div>
            <div class="mc-stat-sub">${oz.veri_yok} veri yok</div>
          </div>
          <div class="mc-stat-card mc-stat-emerald" data-card-code="k_rapor_pg_dagilim.ort_basari">
            <div class="mc-stat-label">Ort. Başarı</div>
            <div class="mc-stat-value" style="color:${scoreColor(oz.ort)}">${oz.ort}%</div>
            <div class="mc-stat-sub">Medyan: ${oz.medyan}%</div>
          </div>
          <div class="mc-stat-card mc-stat-emerald" data-card-code="k_rapor_pg_dagilim.hedefte_80">
            <div class="mc-stat-label">Hedefte (≥%80)</div>
            <div class="mc-stat-value">${oz.yesil}</div>
            <div class="mc-stat-sub">${oz.toplam ? Math.round(oz.yesil/oz.toplam*100) : 0}%</div>
          </div>
          <div class="mc-stat-card" style="background:#fef2f2;" data-card-code="k_rapor_pg_dagilim.kritik_50">
            <div class="mc-stat-label">Kritik (&lt;%50)</div>
            <div class="mc-stat-value" style="color:#ef4444;">${oz.kirmizi}</div>
            <div class="mc-stat-sub">${oz.toplam ? Math.round(oz.kirmizi/oz.toplam*100) : 0}%</div>
          </div>` : '<div class="kr-loading" style="grid-column:span 4;">Veri yok.</div>');

        const buckets = d.buckets || [];
        const hCanvas = document.getElementById("kr-pgd-histogram");
        if (hCanvas && buckets.length) {
          if (pgdHistChart) pgdHistChart.destroy();
          const colors = buckets.map(b => b.min >= 80 ? "rgba(16,185,129,0.8)" : b.min >= 50 ? "rgba(245,158,11,0.8)" : "rgba(239,68,68,0.8)");
          pgdHistChart = new Chart(hCanvas, {
            type: "bar",
            data: { labels: buckets.map(b => b.label), datasets: [{ label: "PG Sayısı", data: buckets.map(b => b.count), backgroundColor: colors, borderRadius: 4 }] },
            options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } }
          });
        }

        const scatter = d.scatter || [];
        const bCanvas = document.getElementById("kr-pgd-bar");
        if (bCanvas && scatter.length) {
          if (pgdBarChart) pgdBarChart.destroy();
          const top20 = scatter.slice(0, 20);
          pgdBarChart = new Chart(bCanvas, {
            type: "bar",
            data: {
              labels: top20.map(r => r.kpi_name.length > 20 ? r.kpi_name.slice(0,20)+"…" : r.kpi_name),
              datasets: [{ label: "Başarı %", data: top20.map(r => r.pct), backgroundColor: top20.map(r => scoreColor(r.pct) + "cc"), borderRadius: 4 }]
            },
            options: { indexAxis: "y", responsive: true, plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true, max: 100 } } }
          });
        }

        const el = document.getElementById("kr-pgd-toplam");
        if (el) el.textContent = scatter.length + " PG";
        setHtml("kr-pgd-body", scatter.slice(0, 30).map(r => `
          <tr>
            <td style="font-size:12px;">${esc(r.kpi_name)}</td>
            <td style="font-size:11px;color:#64748b;">${esc(r.surec)}</td>
            <td style="font-size:11px;">${r.target}</td>
            <td style="font-size:11px;font-weight:600;">${r.actual}</td>
            <td><span style="font-weight:700;color:${scoreColor(r.pct)}">${r.pct}%</span></td>
          </tr>`).join("") || EMPTY_ROW_1(5));
      })
      .catch(() => { setHtml("kr-pgd-ozet", ERROR_HTML); setHtml("kr-pgd-body", ERROR_ROW_1(5)); });
  }

  // ── Yeni Rapor 2: Faaliyet Matris ────────────────────────────────────────────
  let fmChart = null;
  function loadFaaliyetMatris() {
    setHtml("kr-fm-geciken-list", '<div class="kr-loading" style="padding:24px;">Yükleniyor…</div>');
    setHtml("kr-fm-body", '<tr><td colspan="7" style="text-align:center;padding:24px;color:#94a3b8;">Yükleniyor…</td></tr>');
    fetchJson(apiUrl("faaliyet-matris"), { year })
      .then(res => {
        if (!res.success) { setHtml("kr-fm-geciken-list", ERROR_HTML); setHtml("kr-fm-body", ERROR_ROW_1(7)); return; }
        const rows = res.data || [];
        if (!rows.length) { setHtml("kr-fm-geciken-list", EMPTY_HTML); setHtml("kr-fm-body", EMPTY_ROW_1(7)); return; }

        const canvas = document.getElementById("kr-fm-chart");
        if (canvas) {
          if (fmChart) fmChart.destroy();
          const top15 = rows.slice(0, 15);
          fmChart = new Chart(canvas, {
            type: "bar",
            data: {
              labels: top15.map(r => (r.code ? r.code + " " : "") + (r.name.length > 22 ? r.name.slice(0,22)+"…" : r.name)),
              datasets: [
                { label: "Tamamlanan", data: top15.map(r => r.tamamlanan), backgroundColor: "rgba(16,185,129,0.8)", borderRadius: 3 },
                { label: "Devam",      data: top15.map(r => r.devam),      backgroundColor: "rgba(99,102,241,0.8)", borderRadius: 3 },
                { label: "Geciken",    data: top15.map(r => r.geciken),    backgroundColor: "rgba(239,68,68,0.8)",  borderRadius: 3 },
                { label: "Planlandı",  data: top15.map(r => r.planlandi),  backgroundColor: "rgba(148,163,184,0.6)", borderRadius: 3 },
              ]
            },
            options: {
              indexAxis: "y", responsive: true,
              plugins: { legend: { position: "bottom", labels: { font: { size: 11 } } } },
              scales: { x: { stacked: true, beginAtZero: true, ticks: { precision: 0 } }, y: { stacked: true } }
            }
          });
        }

        const geciken = rows.filter(r => r.geciken > 0).sort((a,b) => b.geciken - a.geciken).slice(0, 8);
        const gecEl = document.getElementById("kr-fm-geciken-list");
        if (gecEl) {
          gecEl.innerHTML = geciken.length ? geciken.map(r => `
            <div class="kr-rank-item">
              <div class="kr-rank-code">${esc(r.code)}</div>
              <div class="kr-rank-name" title="${esc(r.name)}">${esc(r.name)}</div>
              <div class="kr-rank-score low">${r.geciken} geciken</div>
            </div>`).join("") : '<div class="kr-loading">Geciken faaliyet yok.</div>';
        }

        setHtml("kr-fm-body", rows.map(r => {
          const pctColor = scoreColor(r.tamamlanma_pct);
          return `<tr>
            <td><span style="font-size:11px;color:#6366f1;">${esc(r.code)}</span> ${esc(r.name)}</td>
            <td style="text-align:center;">${r.toplam}</td>
            <td style="text-align:center;color:#10b981;font-weight:600;">${r.tamamlanan}</td>
            <td style="text-align:center;color:#6366f1;">${r.devam}</td>
            <td style="text-align:center;color:#ef4444;font-weight:${r.geciken>0?'700':'400'};">${r.geciken}</td>
            <td style="text-align:center;color:#94a3b8;">${r.iptal}</td>
            <td><div class="kr-perf-bar-wrap">
              <div class="kr-perf-bar-track"><div class="kr-perf-bar-fill" style="width:${r.tamamlanma_pct}%;background:${pctColor};"></div></div>
              <div class="kr-perf-pct" style="color:${pctColor}">${r.tamamlanma_pct}%</div>
            </div></td>
          </tr>`;
        }).join("") || EMPTY_ROW_1(7));
      })
      .catch(() => { setHtml("kr-fm-geciken-list", ERROR_HTML); setHtml("kr-fm-body", ERROR_ROW_1(7)); });
  }

  // ── Yeni Rapor 3: Aktivite Takvimi ───────────────────────────────────────────
  let atChart = null;
  function loadAktiviteTakvim() {
    setHtml("kr-at-stats", '<div class="kr-loading" style="grid-column:span 3;padding:12px;">Yükleniyor…</div>');
    setHtml("kr-at-heatmap", '<div class="kr-loading" style="padding:24px;">Yükleniyor…</div>');
    fetchJson(apiUrl("aktivite-takvim"), { year })
      .then(res => {
        if (!res.success) { setHtml("kr-at-stats", ERROR_HTML); setHtml("kr-at-heatmap", ERROR_HTML); return; }
        const d = res.data;
        setHtml("kr-at-stats", `
          <div class="mc-stat-card mc-stat-indigo" data-card-code="k_rapor_aktivite_takvim.toplam_giris">
            <div class="mc-stat-label">Toplam Giriş</div>
            <div class="mc-stat-value">${d.toplam_giris}</div>
            <div class="mc-stat-sub">${year} yılı</div>
          </div>
          <div class="mc-stat-card mc-stat-emerald" data-card-code="k_rapor_aktivite_takvim.aktif_gun">
            <div class="mc-stat-label">Aktif Gün</div>
            <div class="mc-stat-value">${d.toplam_gun}</div>
            <div class="mc-stat-sub">Veri girilen gün sayısı</div>
          </div>
          <div class="mc-stat-card mc-stat-amber" data-card-code="k_rapor_aktivite_takvim.gunluk_ort">
            <div class="mc-stat-label">Günlük Ort.</div>
            <div class="mc-stat-value">${d.toplam_gun ? Math.round(d.toplam_giris / d.toplam_gun) : 0}</div>
            <div class="mc-stat-sub">Aktif günlerde</div>
          </div>`);

        // GitHub tarzı takvim heatmap
        const daily = d.daily || {};
        const maxVal = d.max_val || 1;
        const calEl = document.getElementById("kr-at-heatmap");
        if (calEl) {
          const startDate = new Date(year, 0, 1);
          const endDate   = new Date(year, 11, 31);
          // Haftaları oluştur
          let html = '<div class="kr-cal-grid">';
          // Ay etiketleri
          const months = ["Oca","Şub","Mar","Nis","May","Haz","Tem","Ağu","Eyl","Eki","Kas","Ara"];
          html += '<div class="kr-cal-months">';
          for (let m = 0; m < 12; m++) {
            html += `<span>${months[m]}</span>`;
          }
          html += '</div><div class="kr-cal-days">';
          // Gün hücreleri
          let cur = new Date(startDate);
          // Haftanın başına hizala (Pazartesi=1)
          const firstDay = (cur.getDay() + 6) % 7; // 0=Pzt
          for (let i = 0; i < firstDay; i++) html += '<span class="kr-cal-cell kr-cal-empty"></span>';
          while (cur <= endDate) {
            const key = cur.toISOString().slice(0, 10);
            const cnt = daily[key] || 0;
            const intensity = cnt === 0 ? 0 : Math.ceil(cnt / maxVal * 4);
            html += `<span class="kr-cal-cell kr-cal-l${intensity}" title="${key}: ${cnt} giriş"></span>`;
            cur.setDate(cur.getDate() + 1);
          }
          html += '</div></div>';
          // Renk skalası
          html += '<div class="kr-cal-legend"><span style="font-size:11px;color:#94a3b8;">Az</span>';
          for (let i = 0; i <= 4; i++) html += `<span class="kr-cal-cell kr-cal-l${i}"></span>`;
          html += '<span style="font-size:11px;color:#94a3b8;">Çok</span></div>';
          calEl.innerHTML = html;
        }

        // Son 30 gün trend chart
        const today = new Date();
        const labels = [], vals = [];
        for (let i = 29; i >= 0; i--) {
          const d2 = new Date(today); d2.setDate(today.getDate() - i);
          const key = d2.toISOString().slice(0, 10);
          labels.push(key.slice(5));
          vals.push(daily[key] || 0);
        }
        const canvas = document.getElementById("kr-at-chart");
        if (canvas) {
          if (atChart) atChart.destroy();
          atChart = new Chart(canvas, {
            type: "line",
            data: { labels, datasets: [{ label: "Giriş", data: vals, borderColor: "#6366f1", backgroundColor: "rgba(99,102,241,0.1)", fill: true, tension: 0.3, pointRadius: 2 }] },
            options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } }, x: { ticks: { maxTicksLimit: 10 } } } }
          });
        }
      })
      .catch(() => { setHtml("kr-at-stats", ERROR_HTML); setHtml("kr-at-heatmap", ERROR_HTML); });
  }

  // ── Yeni Rapor 4: Kurum Karşılaştırma ────────────────────────────────────────
  let kkChart = null;
  function loadKurumKarsilastirma() {
    setHtml("kr-kk-body", '<tr><td colspan="8" style="text-align:center;padding:24px;color:#94a3b8;">Yükleniyor…</td></tr>');
    fetchJson(apiUrl("kurum-karsilastirma"), { year })
      .then(res => {
        if (!res.success) { setHtml("kr-kk-body", ERROR_ROW_1(8)); return; }
        const rows = res.data || [];
        const badge = document.getElementById("kr-kk-badge");
        if (badge) badge.textContent = rows.length + " kurum";

        const canvas = document.getElementById("kr-kk-chart");
        if (canvas && rows.length) {
          if (kkChart) kkChart.destroy();
          const colors = rows.map(r => scoreColor(r.ort_basari));
          kkChart = new Chart(canvas, {
            type: "bar",
            data: {
              labels: rows.map(r => r.name),
              datasets: [{ label: "Ort. Başarı %", data: rows.map(r => r.ort_basari ?? 0), backgroundColor: colors.map(c => c + "cc"), borderRadius: 6 }]
            },
            options: {
              responsive: true,
              plugins: { legend: { display: false } },
              scales: { y: { beginAtZero: true, max: 100, ticks: { callback: v => v + "%" } } }
            }
          });
        }

        setHtml("kr-kk-body", rows.map((r, i) => {
          const pct = r.ort_basari;
          return `<tr>
            <td style="color:#94a3b8;font-size:12px;">${i+1}</td>
            <td style="font-weight:500;">${esc(r.name)}</td>
            <td style="text-align:center;">${r.pg_sayisi}</td>
            <td style="text-align:center;">${r.veri_girilen}</td>
            <td style="text-align:center;color:#10b981;font-weight:600;">${r.yesil}</td>
            <td style="text-align:center;color:#f59e0b;">${r.sari}</td>
            <td style="text-align:center;color:#ef4444;font-weight:${r.kirmizi>0?'700':'400'};">${r.kirmizi}</td>
            <td><span style="font-weight:700;font-size:14px;color:${scoreColor(pct)}">${pct != null ? pct + "%" : "—"}</span></td>
          </tr>`;
        }).join("") || EMPTY_ROW_1(8));
      })
      .catch(() => setHtml("kr-kk-body", ERROR_ROW_1(8)));
  }

  // ── Yeni Rapor 5: Strateji Kapsama ───────────────────────────────────────────
  let skChart = null;
  function loadStratejiKapsama() {
    setHtml("kr-sk-ozet", '<div class="kr-loading" style="grid-column:span 3;padding:12px;">Yükleniyor…</div>');
    setHtml("kr-sk-body", '<tr><td colspan="6" style="text-align:center;padding:24px;color:#94a3b8;">Yükleniyor…</td></tr>');
    fetchJson(apiUrl("strateji-kapsama"), { year })
      .then(res => {
        if (!res.success) { setHtml("kr-sk-ozet", ERROR_HTML); setHtml("kr-sk-body", ERROR_ROW_1(6)); return; }
        const d = res.data;
        const oz = d.ozet || {};

        setHtml("kr-sk-ozet", `
          <div class="mc-stat-card mc-stat-emerald" data-card-code="k_rapor_strateji_kapsama.tam_kapsamli">
            <div class="mc-stat-label">Tam Kapsamlı</div>
            <div class="mc-stat-value">${oz.tam_kapsamli}</div>
            <div class="mc-stat-sub">Tüm alt str. bağlı</div>
          </div>
          <div class="mc-stat-card mc-stat-amber" data-card-code="k_rapor_strateji_kapsama.kismi">
            <div class="mc-stat-label">Kısmi</div>
            <div class="mc-stat-value">${oz.kismi_kapsamli}</div>
            <div class="mc-stat-sub">Bazı alt str. boş</div>
          </div>
          <div class="mc-stat-card" style="background:#fef2f2;" data-card-code="k_rapor_strateji_kapsama.bos_strateji">
            <div class="mc-stat-label">Boş Strateji</div>
            <div class="mc-stat-value" style="color:#ef4444;">${oz.bos_strateji}</div>
            <div class="mc-stat-sub">Hiç süreç yok</div>
          </div>`);

        // Donut chart
        const canvas = document.getElementById("kr-sk-chart");
        if (canvas) {
          if (skChart) skChart.destroy();
          skChart = new Chart(canvas, {
            type: "doughnut",
            data: {
              labels: ["Tam Kapsamlı", "Kısmi", "Boş"],
              datasets: [{ data: [oz.tam_kapsamli, oz.kismi_kapsamli, oz.bos_strateji], backgroundColor: ["#10b981","#f59e0b","#ef4444"], borderWidth: 2 }]
            },
            options: { responsive: true, plugins: { legend: { position: "bottom" } } }
          });
        }

        // Stratejisiz süreçler
        const stratejisiz = d.stratejisiz_surecler || [];
        const cntEl = document.getElementById("kr-sk-stratejisiz-cnt");
        if (cntEl) cntEl.textContent = stratejisiz.length;
        const listEl = document.getElementById("kr-sk-stratejisiz-list");
        if (listEl) {
          listEl.innerHTML = stratejisiz.length ? stratejisiz.map(p => `
            <div class="kr-rank-item">
              <div class="kr-rank-code">${esc(p.code)}</div>
              <div class="kr-rank-name">${esc(p.name)}</div>
            </div>`).join("") : '<div class="kr-loading">Tüm süreçler stratejiye bağlı.</div>';
        }

        const stratejiler = d.stratejiler || [];
        setHtml("kr-sk-body", stratejiler.map(s => {
          const durumBadge = s.durum === "tam"
            ? '<span class="mc-badge mc-badge-success">Tam</span>'
            : s.durum === "kismi"
            ? '<span class="mc-badge mc-badge-warning">Kısmi</span>'
            : '<span class="mc-badge mc-badge-danger">Boş</span>';
          return `<tr>
            <td style="font-size:11px;color:#6366f1;font-weight:600;">${esc(s.code)}</td>
            <td>${esc(s.title)}</td>
            <td style="text-align:center;">${s.alt_strateji_sayisi}</td>
            <td style="text-align:center;font-weight:600;color:#10b981;">${s.bagli_surec_sayisi}</td>
            <td style="text-align:center;color:${s.bos_alt_strateji>0?'#ef4444':'#94a3b8'};">${s.bos_alt_strateji}</td>
            <td>${durumBadge}</td>
          </tr>`;
        }).join("") || EMPTY_ROW_1(6));
      })
      .catch(() => { setHtml("kr-sk-ozet", ERROR_HTML); setHtml("kr-sk-body", ERROR_ROW_1(6)); });
  }

  // ── Yeni Rapor 6: Sorumlu Analizi ────────────────────────────────────────────
  let sa2Chart = null;
  function loadSorumluAnaliz() {
    setHtml("kr-sa2-body", '<tr><td colspan="8" style="text-align:center;padding:24px;color:#94a3b8;">Yükleniyor…</td></tr>');
    setHtml("kr-sa2-geciken-list", '<div class="kr-loading" style="padding:24px;">Yükleniyor…</div>');
    fetchJson(apiUrl("sorumlu-analiz"), { year })
      .then(res => {
        if (!res.success) { setHtml("kr-sa2-body", ERROR_ROW_1(8)); setHtml("kr-sa2-geciken-list", ERROR_HTML); return; }
        const rows = res.data || [];
        if (!rows.length) { setHtml("kr-sa2-body", EMPTY_ROW_1(8)); setHtml("kr-sa2-geciken-list", EMPTY_HTML); return; }

        const canvas = document.getElementById("kr-sa2-chart");
        if (canvas) {
          if (sa2Chart) sa2Chart.destroy();
          const top12 = rows.slice(0, 12);
          sa2Chart = new Chart(canvas, {
            type: "bar",
            data: {
              labels: top12.map(r => r.ad.length > 18 ? r.ad.slice(0,18)+"…" : r.ad),
              datasets: [
                { label: "Tamamlanan", data: top12.map(r => r.tamamlanan), backgroundColor: "rgba(16,185,129,0.8)", borderRadius: 3 },
                { label: "Devam",      data: top12.map(r => r.devam),      backgroundColor: "rgba(99,102,241,0.8)", borderRadius: 3 },
                { label: "Geciken",    data: top12.map(r => r.geciken),    backgroundColor: "rgba(239,68,68,0.8)",  borderRadius: 3 },
              ]
            },
            options: {
              indexAxis: "y", responsive: true,
              plugins: { legend: { position: "bottom", labels: { font: { size: 11 } } } },
              scales: { x: { stacked: true, beginAtZero: true, ticks: { precision: 0 } }, y: { stacked: true } }
            }
          });
        }

        const geciken = rows.filter(r => r.geciken > 0).sort((a,b) => b.geciken - a.geciken).slice(0, 8);
        const gecEl = document.getElementById("kr-sa2-geciken-list");
        if (gecEl) {
          gecEl.innerHTML = geciken.length ? geciken.map(r => `
            <div class="kr-rank-item">
              <div class="kr-rank-name">${esc(r.ad)}</div>
              <div class="kr-rank-score low">${r.geciken} geciken</div>
            </div>`).join("") : '<div class="kr-loading">Geciken faaliyet yok.</div>';
        }

        setHtml("kr-sa2-body", rows.map((r, i) => `
          <tr>
            <td style="color:#94a3b8;font-size:12px;">${i+1}</td>
            <td>
              <div style="font-weight:500;">${esc(r.ad)}</div>
              <div style="font-size:11px;color:#94a3b8;">${esc(r.email)}</div>
            </td>
            <td style="text-align:center;font-weight:600;">${r.toplam}</td>
            <td style="text-align:center;color:#10b981;font-weight:600;">${r.tamamlanan}</td>
            <td style="text-align:center;color:#ef4444;font-weight:${r.geciken>0?'700':'400'};">${r.geciken}</td>
            <td style="text-align:center;color:#6366f1;">${r.devam}</td>
            <td><div class="kr-perf-bar-wrap">
              <div class="kr-perf-bar-track"><div class="kr-perf-bar-fill" style="width:${r.tamamlanma_pct}%;background:${scoreColor(r.tamamlanma_pct)};"></div></div>
              <div class="kr-perf-pct" style="color:${scoreColor(r.tamamlanma_pct)}">${r.tamamlanma_pct}%</div>
            </div></td>
            <td style="text-align:center;color:${r.gecikme_pct>20?'#ef4444':'#94a3b8'};">${r.gecikme_pct}%</td>
          </tr>`).join("") || EMPTY_ROW_1(8));
      })
      .catch(() => { setHtml("kr-sa2-body", ERROR_ROW_1(8)); setHtml("kr-sa2-geciken-list", ERROR_HTML); });
  }

  // ── Yeni Rapor 7: SWOT/TOWS Trend ────────────────────────────────────────────
  let stSwotChart = null, stTowsChart = null;
  function loadSwotTrend() {
    setHtml("kr-st-body", '<tr><td colspan="11" style="text-align:center;padding:24px;color:#94a3b8;">Yükleniyor…</td></tr>');
    fetchJson(apiUrl("swot-trend"))
      .then(res => {
        if (!res.success) { setHtml("kr-st-body", ERROR_ROW_1(11)); return; }
        const trend = res.data || [];
        if (!trend.length) { setHtml("kr-st-body", EMPTY_ROW_1(11)); return; }

        const labels = trend.map(t => String(t.year));

        const swotCanvas = document.getElementById("kr-st-swot-chart");
        if (swotCanvas) {
          if (stSwotChart) stSwotChart.destroy();
          stSwotChart = new Chart(swotCanvas, {
            type: "bar",
            data: {
              labels,
              datasets: [
                { label: "Güçlü",  data: trend.map(t => t.strengths),     backgroundColor: "rgba(16,185,129,0.8)",  borderRadius: 3 },
                { label: "Zayıf",  data: trend.map(t => t.weaknesses),    backgroundColor: "rgba(239,68,68,0.8)",   borderRadius: 3 },
                { label: "Fırsat", data: trend.map(t => t.opportunities), backgroundColor: "rgba(59,130,246,0.8)",  borderRadius: 3 },
                { label: "Tehdit", data: trend.map(t => t.threats),       backgroundColor: "rgba(245,158,11,0.8)",  borderRadius: 3 },
              ]
            },
            options: { responsive: true, plugins: { legend: { position: "bottom", labels: { font: { size: 11 } } } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } }
          });
        }

        const towsCanvas = document.getElementById("kr-st-tows-chart");
        if (towsCanvas) {
          if (stTowsChart) stTowsChart.destroy();
          stTowsChart = new Chart(towsCanvas, {
            type: "line",
            data: {
              labels,
              datasets: [
                { label: "SO", data: trend.map(t => t.so), borderColor: "#10b981", tension: 0.3, pointRadius: 4 },
                { label: "ST", data: trend.map(t => t.st), borderColor: "#6366f1", tension: 0.3, pointRadius: 4 },
                { label: "WO", data: trend.map(t => t.wo), borderColor: "#3b82f6", tension: 0.3, pointRadius: 4 },
                { label: "WT", data: trend.map(t => t.wt), borderColor: "#ef4444", tension: 0.3, pointRadius: 4 },
              ]
            },
            options: { responsive: true, plugins: { legend: { position: "bottom", labels: { font: { size: 11 } } } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } }
          });
        }

        setHtml("kr-st-body", trend.map(t => `
          <tr>
            <td style="font-weight:600;">${t.year}</td>
            <td style="color:#10b981;">${t.strengths}</td>
            <td style="color:#ef4444;">${t.weaknesses}</td>
            <td style="color:#3b82f6;">${t.opportunities}</td>
            <td style="color:#f59e0b;">${t.threats}</td>
            <td style="font-weight:600;">${t.swot_toplam}</td>
            <td>${t.so}</td><td>${t.st}</td><td>${t.wo}</td><td>${t.wt}</td>
            <td style="font-weight:600;">${t.tows_toplam}</td>
          </tr>`).join("") || EMPTY_ROW_1(11));
      })
      .catch(() => setHtml("kr-st-body", ERROR_ROW_1(11)));
  }

  // ── Yeni Rapor 8: Bildirim Analizi ───────────────────────────────────────────
  let baPieChart = null, baTrendChart = null;
  function loadBildirimAnaliz() {
    setHtml("kr-ba-stats", '<div class="kr-loading" style="grid-column:span 4;padding:12px;">Yükleniyor…</div>');
    fetchJson(apiUrl("bildirim-analiz"))
      .then(res => {
        if (!res.success) { setHtml("kr-ba-stats", ERROR_HTML); return; }
        const d = res.data;

        const okunmaColor = d.okunma_orani >= 80 ? "#10b981" : d.okunma_orani >= 50 ? "#f59e0b" : "#ef4444";
        setHtml("kr-ba-stats", `
          <div class="mc-stat-card mc-stat-indigo" data-card-code="k_rapor_bildirim_analiz.toplam_bildirim">
            <div class="mc-stat-label">Toplam Bildirim</div>
            <div class="mc-stat-value">${d.toplam}</div>
          </div>
          <div class="mc-stat-card mc-stat-emerald" data-card-code="k_rapor_bildirim_analiz.okunan">
            <div class="mc-stat-label">Okunan</div>
            <div class="mc-stat-value">${d.okunan}</div>
            <div class="mc-stat-sub" style="color:${okunmaColor};">%${d.okunma_orani} okunma oranı</div>
          </div>
          <div class="mc-stat-card mc-stat-amber" data-card-code="k_rapor_bildirim_analiz.okunmayan">
            <div class="mc-stat-label">Okunmayan</div>
            <div class="mc-stat-value">${d.okunmayan}</div>
            <div class="mc-stat-sub">Son 30 günde: ${d.okunmayan_30_gun || 0}</div>
          </div>
          <div class="mc-stat-card mc-stat-purple" data-card-code="k_rapor_bildirim_analiz.son_7_gun">
            <div class="mc-stat-label">Son 7 Gün</div>
            <div class="mc-stat-value">${d.son_7_gun}</div>
            <div class="mc-stat-sub">yeni bildirim</div>
          </div>`);

        const pieCanvas = document.getElementById("kr-ba-pie");
        if (pieCanvas && d.tur_dagilim && d.tur_dagilim.length) {
          if (baPieChart) baPieChart.destroy();
          const colors = ["#6366f1","#10b981","#f59e0b","#ef4444","#3b82f6","#8b5cf6","#ec4899","#14b8a6","#f97316","#84cc16"];
          baPieChart = new Chart(pieCanvas, {
            type: "doughnut",
            data: {
              labels: d.tur_dagilim.map(t => t.tur),
              datasets: [{ data: d.tur_dagilim.map(t => t.sayi), backgroundColor: colors.slice(0, d.tur_dagilim.length) }]
            },
            options: { responsive: true, plugins: { legend: { position: "bottom", labels: { font: { size: 11 } } } } }
          });
        }

        const trendCanvas = document.getElementById("kr-ba-trend");
        if (trendCanvas && d.gunluk && d.gunluk.length) {
          if (baTrendChart) baTrendChart.destroy();
          baTrendChart = new Chart(trendCanvas, {
            type: "bar",
            data: {
              labels: d.gunluk.map(g => g.tarih.slice(5)),
              datasets: [{ label: "Bildirim", data: d.gunluk.map(g => g.sayi), backgroundColor: "rgba(99,102,241,0.7)", borderRadius: 3 }]
            },
            options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } }, x: { ticks: { maxTicksLimit: 10 } } } }
          });
        }

        // Yaşlanma
        const yasEl = document.getElementById("kr-ba-yaslanma");
        if (yasEl) {
          if (!d.yaslanma || !d.yaslanma.length) {
            yasEl.innerHTML = '<div style="color:#10b981;font-size:13px;">Tüm bildirimler okundu.</div>';
          } else {
            const maxYas = Math.max(...d.yaslanma.map(y => y.sayi));
            const ageColors = {"0-3 gün": "#10b981", "4-7 gün": "#f59e0b", "8-30 gün": "#f97316", "30+ gün": "#ef4444"};
            yasEl.innerHTML = d.yaslanma.map(y => {
              const pct = Math.round(y.sayi / maxYas * 100);
              const c = ageColors[y.aralik] || "#6366f1";
              return `<div style="margin-bottom:10px;">
                <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px;">
                  <span style="font-weight:600;color:${c};">${esc(y.aralik)}</span>
                  <span style="color:#64748b;">${y.sayi} bildirim</span>
                </div>
                <div style="background:#f1f5f9;border-radius:4px;height:8px;"><div style="background:${c};width:${pct}%;height:8px;border-radius:4px;transition:width 0.3s;"></div></div>
              </div>`;
            }).join('');
          }
        }

        // Kullanıcı top 10
        const kulEl = document.getElementById("kr-ba-kullanicilar");
        if (kulEl) {
          if (!d.kullanici_top || !d.kullanici_top.length) {
            kulEl.innerHTML = '<div class="kr-loading" style="padding:16px;">Veri yok.</div>';
          } else {
            const maxKul = d.kullanici_top[0].sayi || 1;
            kulEl.innerHTML = d.kullanici_top.map(u => `
              <div class="kr-user-bar-row">
                <div class="kr-user-name" title="${esc(u.kullanici)}">${esc(u.kullanici)}</div>
                <div class="kr-user-track"><div class="kr-user-fill" style="width:${Math.round(u.sayi/maxKul*100)}%;background:#6366f1;"></div></div>
                <div class="kr-user-cnt">${u.sayi}</div>
              </div>`).join('');
          }
        }
      })
      .catch(() => setHtml("kr-ba-stats", ERROR_HTML));
  }

})();
