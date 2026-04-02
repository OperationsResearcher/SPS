/**
 * kurum.js — Kurum Paneli modülü JS
 * Kural: alert()/confirm()/prompt() YASAK — yalnızca SweetAlert2
 * Kural: Jinja2 {{ }} bu dosyada YASAK — veri data-* ile gelir
 */

(function () {
  "use strict";

  const root = document.getElementById("kurum-root");
  if (!root) return;

  const UPDATE_STRATEGY_URL = root.dataset.updateStrategyUrl;
  const ADD_STRATEGY_URL    = root.dataset.addStrategyUrl;
  const ADD_SUB_URL         = root.dataset.addSubUrl;
  const UPDATE_MAIN_BASE    = root.dataset.updateMainBase;
  const DELETE_MAIN_BASE    = root.dataset.deleteMainBase;
  const UPDATE_SUB_BASE     = root.dataset.updateSubBase;
  const DELETE_SUB_BASE     = root.dataset.deleteSubBase;
  const OVERVIEW_URL        = root.dataset.overviewUrl || "";
  const CAN_EDIT            = root.dataset.canEdit === "true";

  // ── Yardımcılar ─────────────────────────────────────────────────────────
  function getCsrf() {
    const m = document.querySelector('meta[name="csrf-token"]');
    return m ? m.content : "";
  }

  async function postJson(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrf() },
      body: JSON.stringify(body),
    });
    return res.json();
  }

  function toastSuccess(msg) {
    Swal.fire({
      toast: true, position: "top-end", icon: "success",
      title: msg, showConfirmButton: false, timer: 2500, timerProgressBar: true,
    });
  }

  function showError(msg) {
    Swal.fire({ icon: "error", title: "Hata", text: msg, confirmButtonColor: "#dc2626" });
  }

  async function confirmDelete(title, text) {
    const r = await Swal.fire({
      title: title, text: text, icon: "warning", showCancelButton: true,
      confirmButtonColor: "#dc2626", cancelButtonColor: "#6b7280",
      confirmButtonText: "Evet, sil", cancelButtonText: "İptal",
    });
    return r.isConfirmed;
  }

  function escHtml(s) {
    if (!s) return "";
    return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
  }

  function reload() { setTimeout(() => location.reload(), 1200); }

  // ── Özet grafikleri (Chart.js — base.html) ─────────────────────────────
  window.kurumOverviewCharts = window.kurumOverviewCharts || [];

  function destroyKurumOverviewCharts() {
    (window.kurumOverviewCharts || []).forEach((c) => {
      try { c.destroy(); } catch (_e) { /* ignore */ }
    });
    window.kurumOverviewCharts = [];
  }

  function chartTextColors() {
    const dark = document.documentElement.classList.contains("dark");
    return {
      tick: dark ? "#94a3b8" : "#64748b",
      grid: dark ? "rgba(148,163,184,0.15)" : "rgba(100,116,139,0.12)",
      legend: dark ? "#cbd5e1" : "#475569",
    };
  }

  function readOvNum(key) {
    const el = root.querySelector(`[data-ov="${key}"]`);
    const t = el ? el.textContent.trim().replace(/\s/g, "") : "0";
    const n = parseInt(t, 10);
    return Number.isFinite(n) ? n : 0;
  }

  /** Akordeon içi canvas gizliyken boyut 0 olur; yalnızca görünür olanlarda Chart oluşturulur. */
  function canvasVisible(canvasEl) {
    if (!canvasEl) return false;
    const r = canvasEl.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }

  function renderKurumOverviewCharts() {
    if (typeof Chart === "undefined") return;
    destroyKurumOverviewCharts();
    const tc = chartTextColors();
    const push = (ch) => { window.kurumOverviewCharts.push(ch); };

    const pc = readOvNum("process_count");
    const pPg = readOvNum("processes_with_pg");
    const pNoStr = readOvNum("processes_without_strategy");
    const activePg = readOvNum("active_pg_count");
    const pKpi30 = readOvNum("processes_with_kpi_data_30d");
    const openAct = readOvNum("open_process_activities");
    const actMonth = readOvNum("activity_tracks_done_this_month");

    const projN = readOvNum("project_count");
    const endSoon = readOvNum("projects_end_soon");
    const endOver = readOvNum("projects_overdue_end");
    const openT = readOvNum("open_tasks");
    const ovT = readOvNum("overdue_tasks");
    const due7 = readOvNum("tasks_due_next_7_days");
    const raid = readOvNum("open_raid_items");
    const lowH = readOvNum("low_health_projects");

    const donutCommon = {
      type: "doughnut",
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "58%",
        plugins: {
          legend: {
            position: "bottom",
            labels: { color: tc.legend, boxWidth: 10, padding: 10, font: { size: 10 } },
          },
        },
      },
    };

    const elPg = document.getElementById("kurum-chart-process-pg");
    if (elPg && canvasVisible(elPg)) {
      let labels; let data; let colors;
      if (pc <= 0) {
        labels = ["Erişilebilir süreç yok"];
        data = [1];
        colors = ["#94a3b8"];
      } else {
        const withoutPg = Math.max(0, pc - pPg);
        labels = ["PG tanımlı", "PG yok"];
        data = [pPg, withoutPg];
        colors = ["#10b981", "#e2e8f0"];
      }
      push(new Chart(elPg, {
        ...donutCommon,
        data: { labels, datasets: [{ data, backgroundColor: colors, borderWidth: 0 }] },
      }));
    }

    const elSt = document.getElementById("kurum-chart-process-strategy");
    if (elSt && canvasVisible(elSt)) {
      let labels; let data; let colors;
      if (pc <= 0) {
        labels = ["Veri yok"];
        data = [1];
        colors = ["#94a3b8"];
      } else {
        const linked = Math.max(0, pc - pNoStr);
        labels = ["Stratejiye bağlı", "Bağlantı yok"];
        data = [linked, pNoStr];
        colors = ["#8b5cf6", "#fbbf24"];
      }
      push(new Chart(elSt, {
        ...donutCommon,
        data: { labels, datasets: [{ data, backgroundColor: colors, borderWidth: 0 }] },
      }));
    }

    const elAct = document.getElementById("kurum-chart-process-activity");
    if (elAct && canvasVisible(elAct)) {
      push(new Chart(elAct, {
        type: "bar",
        data: {
          labels: ["Aktif PG", "30g veri (süreç)", "Açık faaliyet", "Bu ay takip"],
          datasets: [{
            label: "Adet",
            data: [activePg, pKpi30, openAct, actMonth],
            backgroundColor: ["#059669", "#34d399", "#6ee7b7", "#a7f3d0"],
            borderRadius: 6,
            borderSkipped: false,
          }],
        },
        options: {
          indexAxis: "y",
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: {
              beginAtZero: true,
              ticks: { color: tc.tick, precision: 0, font: { size: 10 } },
              grid: { color: tc.grid },
            },
            y: {
              ticks: { color: tc.tick, font: { size: 10 } },
              grid: { display: false },
            },
          },
        },
      }));
    }

    const stalePg = readOvNum("stale_pg_count");
    const odAct = readOvNum("overdue_activities");
    const incDef = readOvNum("pg_incomplete_definition");
    const elProcRisk = document.getElementById("kurum-chart-process-risk");
    if (elProcRisk && canvasVisible(elProcRisk)) {
      push(new Chart(elProcRisk, {
        type: "bar",
        data: {
          labels: ["Bayat veri (PG)", "Geciken faaliyet", "Eksik tanım (PG)"],
          datasets: [{
            label: "Adet",
            data: [stalePg, odAct, incDef],
            backgroundColor: ["#e11d48", "#fb7185", "#fda4af"],
            borderRadius: 6,
            borderSkipped: false,
          }],
        },
        options: {
          indexAxis: "y",
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: {
              beginAtZero: true,
              ticks: { color: tc.tick, precision: 0, font: { size: 10 } },
              grid: { color: tc.grid },
            },
            y: {
              ticks: { color: tc.tick, font: { size: 10 } },
              grid: { display: false },
            },
          },
        },
      }));
    }

    const lowSc = readOvNum("pg_low_score_count");
    const scored = readOvNum("pg_scored_count");
    const elProcScore = document.getElementById("kurum-chart-process-score");
    if (elProcScore && canvasVisible(elProcScore)) {
      let labels; let data; let colors;
      if (activePg <= 0) {
        labels = ["Aktif PG yok"];
        data = [1];
        colors = ["#94a3b8"];
      } else {
        const okScored = Math.max(0, scored - lowSc);
        const noScore = Math.max(0, activePg - scored);
        labels = ["Düşük skor (<50)", "Skorlu (≥50)", "Skorsuz"];
        data = [lowSc, okScored, noScore];
        colors = ["#f43f5e", "#22c55e", "#cbd5e1"];
      }
      push(new Chart(elProcScore, {
        ...donutCommon,
        data: { labels, datasets: [{ data, backgroundColor: colors, borderWidth: 0 }] },
      }));
    }

    const elTim = document.getElementById("kurum-chart-project-timeline");
    if (elTim && canvasVisible(elTim)) {
      let labels; let data; let colors;
      if (projN <= 0) {
        labels = ["Aktif proje yok"];
        data = [1];
        colors = ["#94a3b8"];
      } else {
        const other = Math.max(0, projN - endOver - endSoon);
        labels = ["Bitiş gecikti", "30 gün içinde", "Diğer"];
        data = [endOver, endSoon, other];
        colors = ["#f43f5e", "#f59e0b", "#6366f1"];
      }
      push(new Chart(elTim, {
        ...donutCommon,
        data: { labels, datasets: [{ data, backgroundColor: colors, borderWidth: 0 }] },
      }));
    }

    const elTk = document.getElementById("kurum-chart-project-tasks");
    if (elTk && canvasVisible(elTk)) {
      let labels; let data; let colors;
      if (openT <= 0) {
        labels = ["Açık görev yok"];
        data = [1];
        colors = ["#cbd5e1"];
      } else {
        const rest = Math.max(0, openT - ovT - due7);
        labels = ["Vadesi geçti", "7 gün içinde", "Diğer açık"];
        data = [ovT, due7, rest];
        colors = ["#ef4444", "#f97316", "#818cf8"];
      }
      push(new Chart(elTk, {
        ...donutCommon,
        data: { labels, datasets: [{ data, backgroundColor: colors, borderWidth: 0 }] },
      }));
    }

    const elRisk = document.getElementById("kurum-chart-project-risk");
    if (elRisk && canvasVisible(elRisk)) {
      push(new Chart(elRisk, {
        type: "bar",
        data: {
          labels: ["Geciken görev", "7 gün vadesi", "Açık RAID", "Sağlık <50"],
          datasets: [{
            label: "Sayı",
            data: [ovT, due7, raid, lowH],
            backgroundColor: ["#dc2626", "#ea580c", "#ca8a04", "#9333ea"],
            borderRadius: 6,
            borderSkipped: false,
          }],
        },
        options: {
          indexAxis: "y",
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: {
              beginAtZero: true,
              ticks: { color: tc.tick, precision: 0, font: { size: 10 } },
              grid: { color: tc.grid },
            },
            y: {
              ticks: { color: tc.tick, font: { size: 10 } },
              grid: { display: false },
            },
          },
        },
      }));
    }
  }

  function applyOverviewPayload(d) {
    if (!d || !d.success || !d.overview) return;
    const o = d.overview;
    const p = o.process || {};
    const j = o.project || {};
    const flat = {
      user_count: d.user_count,
      strategy_count: d.strategy_count,
      process_count: p.process_count,
      processes_with_pg: p.processes_with_pg,
      active_pg_count: p.active_pg_count,
      processes_without_strategy: p.processes_without_strategy,
      kpi_data_rows_30d: p.kpi_data_rows_30d,
      processes_with_kpi_data_30d: p.processes_with_kpi_data_30d,
      open_process_activities: p.open_process_activities,
      activity_tracks_done_this_month: p.activity_tracks_done_this_month,
      stale_pg_count: p.stale_pg_count,
      overdue_activities: p.overdue_activities,
      pg_incomplete_definition: p.pg_incomplete_definition,
      pg_scored_count: p.pg_scored_count,
      pg_low_score_count: p.pg_low_score_count,
      project_count: j.project_count,
      projects_end_soon: j.projects_end_soon,
      projects_overdue_end: j.projects_overdue_end,
      open_tasks: j.open_tasks,
      overdue_tasks: j.overdue_tasks,
      tasks_due_next_7_days: j.tasks_due_next_7_days,
      open_raid_items: j.open_raid_items,
      low_health_projects: j.low_health_projects,
    };
    Object.keys(flat).forEach((k) => {
      const v = flat[k];
      const text = v === undefined || v === null ? "0" : String(v);
      root.querySelectorAll(`[data-ov="${k}"]`).forEach((el) => {
        el.textContent = text;
      });
    });
    const a = p.pg_avg_calculated_score;
    const avgText = a === null || a === undefined ? "—" : String(a);
    root.querySelectorAll('[data-ov="pg_avg_calculated_score"]').forEach((el) => {
      el.textContent = avgText;
    });

    const pt = o.process_tenant;
    if (pt && typeof pt === "object") {
      Object.keys(pt).forEach((k) => {
        const v = pt[k];
        const text =
          k === "pg_avg_calculated_score"
            ? (v === null || v === undefined ? "—" : String(v))
            : v === null || v === undefined
              ? "0"
              : String(v);
        root.querySelectorAll(`[data-ov-t="${k}"]`).forEach((el) => {
          el.textContent = k === "pg_avg_calculated_score" && (v === null || v === undefined) ? "—" : text;
        });
      });
    }

    const pjt = o.project_tenant;
    if (pjt && typeof pjt === "object") {
      Object.keys(pjt).forEach((k) => {
        const v = pjt[k];
        const text = v === null || v === undefined ? "0" : String(v);
        root.querySelectorAll(`[data-ov-pt="${k}"]`).forEach((el) => {
          el.textContent = text;
        });
      });
    }

    renderKurumOverviewCharts();
  }

  async function refreshOverview() {
    if (!OVERVIEW_URL) return;
    try {
      const res = await fetch(OVERVIEW_URL, { credentials: "same-origin" });
      const d = await res.json();
      applyOverviewPayload(d);
    } catch (_e) {
      /* yarı-gerçek zamanlı yenileme — sessiz */
    }
  }

  if (OVERVIEW_URL) {
    window.setInterval(refreshOverview, 90000);
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible") refreshOverview();
    });
  }

  document.addEventListener("micro-theme-changed", () => {
    renderKurumOverviewCharts();
  });

  function scheduleRedrawCharts() {
    requestAnimationFrame(() => {
      renderKurumOverviewCharts();
    });
  }
  window.__kurumRedrawCharts = scheduleRedrawCharts;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => { scheduleRedrawCharts(); });
  } else {
    scheduleRedrawCharts();
  }

  function readSkField(key) {
    const el = document.querySelector(`#kurum-root [data-sk-field="${key}"]`);
    if (!el) return "";
    const t = el.textContent.trim();
    return t === "—" ? "" : t;
  }

  // ── Düzenleme (yalnızca tenant_admin / executive_manager) ────────────────
  if (CAN_EDIT) {
  // ── Stratejik Kimlik Düzenle ─────────────────────────────────────────────
  document.getElementById("btn-identity-edit")?.addEventListener("click", async () => {
    const valsPurpose = readSkField("purpose");
    const valsVision = readSkField("vision");
    const valsValues = readSkField("core_values");
    const valsEthics = readSkField("code_of_ethics");
    const valsQuality = readSkField("quality_policy");

    const { value: form } = await Swal.fire({
      title: "Stratejik Kimlik Düzenle",
      width: 640,
      html: `<div class="text-left space-y-3 text-sm">
        <div><label class="block text-xs text-gray-500 mb-1">Amaç</label>
          <textarea id="sk-purpose" class="swal2-textarea" rows="2">${escHtml(valsPurpose)}</textarea></div>
        <div><label class="block text-xs text-gray-500 mb-1">Vizyon</label>
          <textarea id="sk-vision" class="swal2-textarea" rows="2">${escHtml(valsVision)}</textarea></div>
        <div><label class="block text-xs text-gray-500 mb-1">Temel Değerler</label>
          <textarea id="sk-values" class="swal2-textarea" rows="2">${escHtml(valsValues)}</textarea></div>
        <div><label class="block text-xs text-gray-500 mb-1">Etik Kurallar</label>
          <textarea id="sk-ethics" class="swal2-textarea" rows="2">${escHtml(valsEthics)}</textarea></div>
        <div><label class="block text-xs text-gray-500 mb-1">Kalite Politikası</label>
          <textarea id="sk-quality" class="swal2-textarea" rows="2">${escHtml(valsQuality)}</textarea></div>
      </div>`,
      focusConfirm: false, showCancelButton: true,
      confirmButtonText: "Kaydet", cancelButtonText: "İptal", confirmButtonColor: "#4f46e5",
      preConfirm: () => ({
        purpose:       document.getElementById("sk-purpose").value.trim(),
        vision:        document.getElementById("sk-vision").value.trim(),
        core_values:   document.getElementById("sk-values").value.trim(),
        code_of_ethics: document.getElementById("sk-ethics").value.trim(),
        quality_policy: document.getElementById("sk-quality").value.trim(),
      }),
    });
    if (!form) return;
    try {
      const d = await postJson(UPDATE_STRATEGY_URL, form);
      if (d.success) { toastSuccess("Stratejik kimlik güncellendi."); reload(); }
      else showError(d.message || "Güncelleme başarısız.");
    } catch (e) { showError("Sunucu hatası: " + e.message); }
  });

  // ── Strateji modalları: SP (/sp) ile aynı mc-modal-form-global + openMcFormModal ──
  function kurumOpenMcFormModal(opts) {
    if (typeof window.openMcFormModal !== "function") {
      showError("Modal bileşeni yüklenemedi. Sayfayı yenileyin.");
      return Promise.resolve(null);
    }
    return window.openMcFormModal(opts);
  }

  async function onKurumAddStrategyClick() {
    const vals = await kurumOpenMcFormModal({
      title: "Yeni Strateji Ekle",
      iconClass: "fas fa-plus-circle",
      bodyHtml: `<div class="tm-grid-2">
          <div class="tm-field tm-full">
            <label class="mc-form-label">Başlık <span class="req">*</span></label>
            <input id="sp-modal-add-title" type="text" class="mc-form-input" placeholder="Strateji başlığı">
          </div>
          <div class="tm-field tm-full">
            <label class="mc-form-label">Kod</label>
            <input id="sp-modal-add-code" type="text" class="mc-form-input" placeholder="Örn: ST1">
          </div>
          <div class="tm-field tm-full">
            <label class="mc-form-label">Açıklama</label>
            <textarea id="sp-modal-add-desc" class="mc-form-input" rows="4" placeholder="Kısa açıklama"></textarea>
          </div>
        </div>`,
      confirmText: "Kaydet",
      onConfirm: function (ctx) {
        var title = document.getElementById("sp-modal-add-title").value.trim();
        if (!title) { ctx.showValidation("Başlık zorunludur."); return false; }
        return {
          title: title,
          code: document.getElementById("sp-modal-add-code").value.trim() || null,
          description: document.getElementById("sp-modal-add-desc").value.trim() || null,
        };
      },
    });
    if (vals === null) return;
    try {
      const d = await postJson(ADD_STRATEGY_URL, vals);
      if (d.success) { toastSuccess("Strateji eklendi."); setTimeout(() => location.reload(), 1200); }
      else showError(d.message || "Kayıt başarısız.");
    } catch (e) { showError("Sunucu hatası: " + e.message); }
  }

  document.getElementById("btn-strategy-add")?.addEventListener("click", onKurumAddStrategyClick);
  document.getElementById("btn-strategy-add-empty")?.addEventListener("click", onKurumAddStrategyClick);

  /* Bubble dinleyicisi kullanılamaz: şablonda @click.stop olayın root’a çıkmasını engelliyor.
     Capture fazında dinleyerek düğmeye inmeden önce yakalıyoruz (stopPropagation kullanmıyoruz). */
  root.addEventListener(
    "click",
    async (e) => {
    // Alt strateji ekle
    const btnSubAdd = e.target.closest(".btn-sub-add");
    if (btnSubAdd && root.contains(btnSubAdd)) {
      const strategyId = btnSubAdd.dataset.strategyId;
      const vals = await kurumOpenMcFormModal({
        title: "Alt Strateji Ekle",
        iconClass: "fas fa-layer-group",
        bodyHtml: `<div class="tm-grid-2">
          <div class="tm-field tm-full">
            <label class="mc-form-label">Başlık <span class="req">*</span></label>
            <input id="sp-modal-sub-add-title" type="text" class="mc-form-input" placeholder="Alt strateji başlığı">
          </div>
          <div class="tm-field tm-full">
            <label class="mc-form-label">Kod</label>
            <input id="sp-modal-sub-add-code" type="text" class="mc-form-input" placeholder="Örn: ST1.1">
          </div>
        </div>`,
        confirmText: "Kaydet",
        onConfirm: function (ctx) {
          var title = document.getElementById("sp-modal-sub-add-title").value.trim();
          if (!title) { ctx.showValidation("Başlık zorunludur."); return false; }
          return {
            strategy_id: strategyId,
            title: title,
            code: document.getElementById("sp-modal-sub-add-code").value.trim() || null,
          };
        },
      });
      if (vals === null) return;
      try {
        const d = await postJson(ADD_SUB_URL, vals);
        if (d.success) { toastSuccess("Alt strateji eklendi."); setTimeout(() => location.reload(), 1200); }
        else showError(d.message || "Kayıt başarısız.");
      } catch (err) { showError("Sunucu hatası: " + err.message); }
      return;
    }

    // Ana strateji düzenle
    const btnMainEdit = e.target.closest(".btn-main-edit");
    if (btnMainEdit && root.contains(btnMainEdit)) {
      const sid = btnMainEdit.dataset.strategyId;
      const currentTitle = btnMainEdit.dataset.title || "";
      const currentCode = btnMainEdit.dataset.code || "";
      const currentDesc = btnMainEdit.dataset.description || "";
      const vals = await kurumOpenMcFormModal({
        title: "Ana strateji düzenle",
        iconClass: "fas fa-chess",
        bodyHtml: `<div class="tm-grid-2">
          <div class="tm-field tm-full">
            <label class="mc-form-label">Başlık <span class="req">*</span></label>
            <input id="sp-modal-main-title" type="text" class="mc-form-input" value="${escHtml(currentTitle)}" placeholder="Strateji başlığı">
          </div>
          <div class="tm-field tm-full">
            <label class="mc-form-label">Kod</label>
            <input id="sp-modal-main-code" type="text" class="mc-form-input" value="${escHtml(currentCode)}" placeholder="Örn: ST1">
          </div>
          <div class="tm-field tm-full">
            <label class="mc-form-label">Açıklama</label>
            <textarea id="sp-modal-main-desc" class="mc-form-input" rows="4" placeholder="Kısa açıklama">${escHtml(currentDesc)}</textarea>
          </div>
        </div>`,
        confirmText: "Güncelle",
        onConfirm: function (ctx) {
          var title = document.getElementById("sp-modal-main-title").value.trim();
          if (!title) { ctx.showValidation("Başlık zorunludur."); return false; }
          return {
            title: title,
            code: document.getElementById("sp-modal-main-code").value.trim() || null,
            description: document.getElementById("sp-modal-main-desc").value.trim() || null,
          };
        },
      });
      if (vals === null) return;
      try {
        const d = await postJson(`${UPDATE_MAIN_BASE}${sid}`, vals);
        if (d.success) { toastSuccess(d.message || "Güncellendi."); setTimeout(() => location.reload(), 800); }
        else showError(d.message || "Güncelleme başarısız.");
      } catch (err) { showError("Sunucu hatası: " + err.message); }
      return;
    }

    // Ana strateji sil
    const btnMainDel = e.target.closest(".btn-main-delete");
    if (btnMainDel && root.contains(btnMainDel)) {
      const ok = await confirmDelete("Strateji silinsin mi?", `"${btnMainDel.dataset.title}" pasife alınacak.`);
      if (!ok) return;
      try {
        const d = await postJson(`${DELETE_MAIN_BASE}${btnMainDel.dataset.strategyId}`, {});
        if (d.success) { toastSuccess("Strateji silindi."); setTimeout(() => location.reload(), 1200); }
        else showError(d.message || "Silme başarısız.");
      } catch (err) { showError("Sunucu hatası: " + err.message); }
      return;
    }

    // Alt strateji düzenle
    const btnSubEdit = e.target.closest(".btn-sub-edit");
    if (btnSubEdit && root.contains(btnSubEdit)) {
      const subId = btnSubEdit.dataset.subId;
      const currentTitle = btnSubEdit.dataset.title || "";
      const currentCode = btnSubEdit.dataset.code || "";
      const vals = await kurumOpenMcFormModal({
        title: "Alt Strateji Düzenle",
        iconClass: "fas fa-pen-to-square",
        bodyHtml: `<div class="tm-grid-2">
          <div class="tm-field tm-full">
            <label class="mc-form-label">Başlık <span class="req">*</span></label>
            <input id="sp-modal-sub-edit-title" type="text" class="mc-form-input" value="${escHtml(currentTitle)}">
          </div>
          <div class="tm-field tm-full">
            <label class="mc-form-label">Kod</label>
            <input id="sp-modal-sub-edit-code" type="text" class="mc-form-input" value="${escHtml(currentCode)}">
          </div>
        </div>`,
        confirmText: "Güncelle",
        onConfirm: function (ctx) {
          var title = document.getElementById("sp-modal-sub-edit-title").value.trim();
          if (!title) { ctx.showValidation("Başlık zorunludur."); return false; }
          return {
            title: title,
            code: document.getElementById("sp-modal-sub-edit-code").value.trim() || null,
          };
        },
      });
      if (vals === null) return;
      try {
        const d = await postJson(`${UPDATE_SUB_BASE}${subId}`, vals);
        if (d.success) { toastSuccess("Alt strateji güncellendi."); setTimeout(() => location.reload(), 1200); }
        else showError(d.message || "Güncelleme başarısız.");
      } catch (err) { showError("Sunucu hatası: " + err.message); }
      return;
    }

    // Alt strateji sil
    const btnSubDel = e.target.closest(".btn-sub-delete");
    if (btnSubDel && root.contains(btnSubDel)) {
      const ok = await confirmDelete("Alt strateji silinsin mi?", `"${btnSubDel.dataset.title}" pasife alınacak.`);
      if (!ok) return;
      try {
        const d = await postJson(`${DELETE_SUB_BASE}${btnSubDel.dataset.subId}`, {});
        if (d.success) { toastSuccess("Alt strateji silindi."); setTimeout(() => location.reload(), 1200); }
        else showError(d.message || "Silme başarısız.");
      } catch (err) { showError("Sunucu hatası: " + err.message); }
    }
    },
    true
  );

  } /* CAN_EDIT */

})();
