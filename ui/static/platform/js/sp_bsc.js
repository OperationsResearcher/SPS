/**
 * sp_bsc.js — Dengeli Karne (BSC) görselleştirme + perspektif atama (L3 Dal 2)
 *
 * API: GET /sp/api/bsc → {perspectives:{key:{label,kpi_count,score,kpis[]}}, unassigned[]}
 *      POST /sp/api/bsc/assign {kpi_id, perspective}  (perspective="" → kaldır)
 *      POST /sp/api/bsc/auto-assign
 * Kural: alert/confirm YASAK → SweetAlert2. Jinja {{ }} YASAK → data-*.
 */
(function () {
  "use strict";

  const root = document.getElementById("sp-bsc");
  if (!root) return;

  const GET_URL = root.dataset.getUrl;
  const ASSIGN_URL = root.dataset.assignUrl;
  const AUTO_URL = root.dataset.autoAssignUrl;
  const CAN_EDIT = root.dataset.canEdit === "true";

  const PERSPS = [
    { key: "finansal", label: t("Finansal"), icon: "fa-coins", color: "#10b981" },
    { key: "musteri", label: t("Müşteri"), icon: "fa-users", color: "#3b82f6" },
    { key: "ic_surec", label: t("İç Süreçler"), icon: "fa-gears", color: "#8b5cf6" },
    { key: "ogrenme", label: t("Öğrenme & Gelişim"), icon: "fa-graduation-cap", color: "#f59e0b" },
  ];

  const loadingEl = document.getElementById("bsc-loading");
  const perspGrid = document.getElementById("bsc-perspectives");
  const unassignedWrap = document.getElementById("bsc-unassigned-wrap");
  const unassignedEl = document.getElementById("bsc-unassigned");
  const unassignedCount = document.getElementById("bsc-unassigned-count");
  const autoBtn = document.getElementById("bsc-auto");

  function getCsrf() {
    const m = document.querySelector('meta[name="csrf-token"]');
    return m ? m.content : "";
  }
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function showError(msg) {
    Swal.fire({ icon: "error", title: t("Hata"), text: msg, confirmButtonColor: "#dc2626" });
  }
  function toast(msg) {
    Swal.fire({ toast: true, position: "top-end", icon: "success", title: msg,
      showConfirmButton: false, timer: 2000, timerProgressBar: true });
  }

  function perspLabel(key) {
    const p = PERSPS.find((x) => x.key === key);
    return p ? p.label : key;
  }

  function scoreBadge(score) {
    if (score == null) return `<span style="color:#94a3b8;font-size:12px;">${t("veri yok")}</span>`;
    const c = score >= 75 ? "#10b981" : (score >= 50 ? "#f59e0b" : "#ef4444");
    return `<span style="font-weight:800;font-size:18px;color:${c};">%${score}</span>`;
  }

  function perspSelect(kpiId, current) {
    if (!CAN_EDIT) return "";
    const opts = [`<option value="">${t("— Atama yok —")}</option>`]
      .concat(PERSPS.map((p) =>
        `<option value="${p.key}" ${p.key === current ? "selected" : ""}>${esc(p.label)}</option>`))
      .join("");
    return `<select class="bsc-assign mc-form-input" data-kpi-id="${kpiId}"
      style="font-size:12px;padding:3px 6px;width:auto;">${opts}</select>`;
  }

  function kpiRow(k) {
    const perf = k.perf_pct == null ? "—" : "%" + k.perf_pct;
    return `<div style="display:flex;align-items:center;gap:8px;padding:6px 8px;border:1px solid #eef2f7;border-radius:6px;background:var(--bg-default,#fff);">
      <div style="flex:1;min-width:0;">
        <div style="font-size:12.5px;font-weight:600;color:var(--text-default);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${esc(k.name)}</div>
        <div style="font-size:11px;color:#94a3b8;">${esc(k.process_name || "—")} · ${t("perf")} ${perf}</div>
      </div>
      ${perspSelect(k.id, k.perspective)}
    </div>`;
  }

  function render(data) {
    const persp = data.perspectives || {};
    perspGrid.innerHTML = PERSPS.map((p) => {
      const d = persp[p.key] || { kpi_count: 0, score: null, kpis: [] };
      const kpis = (d.kpis || []).map(kpiRow).join("") ||
        `<div style="color:#94a3b8;font-size:12px;padding:6px 0;">${t("Bu perspektifte gösterge yok.")}</div>`;
      return `<div class="mc-card" style="border-top:3px solid ${p.color};">
        <div class="mc-card-header" style="display:flex;align-items:center;gap:8px;">
          <i class="fas ${p.icon}" style="color:${p.color};"></i>
          <span class="mc-card-title">${esc(p.label)}</span>
          <span style="margin-left:auto;">${scoreBadge(d.score)}</span>
        </div>
        <div class="mc-card-body" style="padding:10px 12px;display:flex;flex-direction:column;gap:6px;">
          <div style="font-size:11px;color:#64748b;">${d.kpi_count || 0} ${t("gösterge")}</div>
          ${kpis}
        </div>
      </div>`;
    }).join("");

    const un = data.unassigned || [];
    if (un.length) {
      unassignedWrap.style.display = "block";
      unassignedCount.textContent = un.length;
      unassignedEl.innerHTML = un.map(kpiRow).join("");
    } else {
      unassignedWrap.style.display = "none";
    }
  }

  async function assign(kpiId, perspective) {
    try {
      const res = await fetch(ASSIGN_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrf() },
        credentials: "same-origin",
        body: JSON.stringify({ kpi_id: kpiId, perspective: perspective }),
      });
      const d = await res.json();
      if (d.success) { toast(perspective ? perspLabel(perspective) + t("'e atandı.") : t("Atama kaldırıldı.")); load(); }
      else showError(d.message || t("Atama başarısız."));
    } catch (e) { showError(t("Sunucu hatası: ") + e.message); }
  }

  async function autoAssign() {
    const r = await Swal.fire({
      title: t("Otomatik sınıflandır?"),
      text: t("Atanmamış göstergeler ad/anahtar kelimeye göre perspektiflere önerilecek. Mevcut atamalar korunur."),
      icon: "question", showCancelButton: true,
      confirmButtonText: t("Evet, sınıflandır"), cancelButtonText: t("İptal"), confirmButtonColor: "#0d9488",
    });
    if (!r.isConfirmed) return;
    try {
      const res = await fetch(AUTO_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrf() },
        credentials: "same-origin", body: "{}",
      });
      const d = await res.json();
      if (d.success) { toast(t("Otomatik sınıflandırma tamam.")); load(); }
      else showError(d.message || t("Sınıflandırma başarısız."));
    } catch (e) { showError(t("Sunucu hatası: ") + e.message); }
  }

  root.addEventListener("change", (e) => {
    const sel = e.target.closest(".bsc-assign");
    if (sel) assign(parseInt(sel.dataset.kpiId, 10), sel.value);
  });
  if (autoBtn) autoBtn.addEventListener("click", autoAssign);

  async function load() {
    try {
      const res = await fetch(GET_URL, { credentials: "same-origin" });
      const d = await res.json();
      loadingEl.style.display = "none";
      if (!d.success) { showError(d.message || t("BSC verisi alınamadı.")); return; }
      render(d);
    } catch (e) {
      loadingEl.style.display = "none";
      showError(t("Sunucu hatası: ") + e.message);
    }
  }

  load();
})();
