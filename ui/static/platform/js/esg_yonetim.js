/**
 * esg_yonetim.js — ESG metrik + değer yönetimi (L3 Dal 4)
 *
 * Metrikleri E/S/G gruplar; ekle/düzenle/sil + her metriğe yıl-değer girişi.
 * Kural: alert/confirm YASAK → SweetAlert2. Jinja {{ }} YASAK → data-*.
 */
(function () {
  "use strict";

  const root = document.getElementById("esg-root");
  if (!root) return;

  const LIST_URL = root.dataset.listUrl;
  const ADD_URL = root.dataset.addUrl;
  const UPDATE_BASE = root.dataset.updateBase; // /reports/api/esg/metrics/
  const CAN_EDIT = root.dataset.canEdit === "true";

  const CAT_META = {
    E: { label: t("Çevresel (Environment)"), icon: "fa-leaf", color: "#22c55e" },
    S: { label: t("Sosyal (Social)"), icon: "fa-users", color: "#3b82f6" },
    G: { label: t("Yönetişim (Governance)"), icon: "fa-scale-balanced", color: "#8b5cf6" },
  };
  const SCOPE_LABELS = { "": "—", scope1: t("Kapsam 1"), scope2: t("Kapsam 2"), scope3: t("Kapsam 3") };

  const loadingEl = document.getElementById("esg-loading");
  const groupsEl = document.getElementById("esg-groups");
  const emptyEl = document.getElementById("esg-empty");
  const addBtn = document.getElementById("esg-add");

  let METRICS = [];

  function getCsrf() {
    const m = document.querySelector('meta[name="csrf-token"]');
    return m ? m.content : "";
  }
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function showError(msg) { Swal.fire({ icon: "error", title: t("Hata"), text: msg, confirmButtonColor: "#dc2626" }); }
  function toast(msg) {
    Swal.fire({ toast: true, position: "top-end", icon: "success", title: msg,
      showConfirmButton: false, timer: 2000, timerProgressBar: true });
  }

  async function postJson(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrf() },
      credentials: "same-origin", body: JSON.stringify(body || {}),
    });
    return res.json();
  }

  function valueRows(m) {
    const vals = m.values || [];
    if (!vals.length) return `<div style="font-size:12px;color:#94a3b8;padding:4px 0;">${t("Değer girilmemiş.")}</div>`;
    return vals.map((v) => `
      <div style="display:flex;align-items:center;gap:8px;font-size:12.5px;padding:3px 0;">
        <span style="font-weight:700;color:var(--text-default);min-width:42px;">${v.year}</span>
        <span style="flex:1;color:var(--text-default);">${v.value == null ? "—" : esc(v.value)} ${esc(m.unit || "")}</span>
        ${v.source ? `<span style="font-size:11px;color:#94a3b8;">${esc(v.source)}</span>` : ""}
        ${CAN_EDIT ? `<button type="button" class="esg-val-del" data-vid="${v.id}"
          style="background:none;border:none;color:#cbd5e1;cursor:pointer;" title="${t("Sil")}"><i class="fas fa-times"></i></button>` : ""}
      </div>`).join("");
  }

  function metricCard(m) {
    const meta = CAT_META[m.category] || { color: "#94a3b8" };
    const target = m.target_value == null ? "" :
      `<span style="font-size:11px;color:#64748b;">${t("Hedef:")} ${esc(m.target_value)} ${esc(m.unit || "")}</span>`;
    return `<div class="mc-card" data-metric-id="${m.id}" style="border-left:3px solid ${meta.color};">
      <div class="mc-card-body" style="padding:12px 14px;">
        <div style="display:flex;align-items:flex-start;gap:10px;">
          <div style="flex:1;min-width:0;">
            <div style="font-size:14px;font-weight:700;color:var(--text-default);">
              ${esc(m.name)} ${m.code ? `<span class="process-code-badge">${esc(m.code)}</span>` : ""}
            </div>
            <div style="font-size:11.5px;color:#94a3b8;margin-top:2px;">
              ${esc(SCOPE_LABELS[m.scope] || m.scope || "—")}
              ${m.unit ? " · " + esc(m.unit) : ""}
              ${m.sdg_codes ? " · " + t("SDG:") + " " + esc(m.sdg_codes) : ""}
              ${target ? " · " : ""}${target}
            </div>
            ${m.description ? `<div style="font-size:12px;color:#64748b;margin-top:4px;">${esc(m.description)}</div>` : ""}
          </div>
          ${CAN_EDIT ? `<div style="display:flex;gap:4px;flex:none;">
            <button type="button" class="esg-edit" data-id="${m.id}" style="background:none;border:none;color:#94a3b8;cursor:pointer;padding:3px;" title="${t("Düzenle")}"><i class="fas fa-pen"></i></button>
            <button type="button" class="esg-del" data-id="${m.id}" data-name="${esc(m.name)}" style="background:none;border:none;color:#f87171;cursor:pointer;padding:3px;" title="${t("Sil")}"><i class="fas fa-trash"></i></button>
          </div>` : ""}
        </div>
        <div style="margin-top:8px;padding-top:8px;border-top:1px solid #eef2f7;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
            <span style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;color:#94a3b8;">${t("Yıllık Değerler")}</span>
            ${CAN_EDIT ? `<button type="button" class="esg-val-add" data-id="${m.id}"
              style="font-size:11.5px;font-weight:600;color:${meta.color};background:none;border:none;cursor:pointer;">
              <i class="fas fa-plus" style="font-size:9px;"></i> ${t("Değer gir")}</button>` : ""}
          </div>
          ${valueRows(m)}
        </div>
      </div>
    </div>`;
  }

  function render() {
    if (!METRICS.length) {
      groupsEl.innerHTML = "";
      emptyEl.style.display = "block";
      return;
    }
    emptyEl.style.display = "none";
    groupsEl.innerHTML = ["E", "S", "G"].map((cat) => {
      const items = METRICS.filter((m) => m.category === cat);
      if (!items.length) return "";
      const meta = CAT_META[cat];
      return `<div>
        <h3 style="font-size:15px;font-weight:700;color:var(--text-default);margin:0 0 10px;">
          <i class="fas ${meta.icon}" style="color:${meta.color};"></i> ${meta.label} <span style="color:#94a3b8;font-weight:600;">(${items.length})</span>
        </h3>
        <div style="display:flex;flex-direction:column;gap:10px;">${items.map(metricCard).join("")}</div>
      </div>`;
    }).join("");
  }

  function metricFormHtml(m) {
    m = m || {};
    const catOpt = (v) => ["E", "S", "G"].map((c) =>
      `<option value="${c}" ${m.category === c ? "selected" : ""}>${c}</option>`).join("");
    const scopeOpt = (v) => Object.keys(SCOPE_LABELS).map((s) =>
      `<option value="${s}" ${m.scope === s ? "selected" : ""}>${SCOPE_LABELS[s]}</option>`).join("");
    return `<div style="text-align:left;font-size:13px;display:flex;flex-direction:column;gap:8px;">
      <div><label style="font-size:12px;color:#64748b;">${t("Ad")} *</label>
        <input id="esg-f-name" class="swal2-input" style="margin:2px 0;" value="${esc(m.name || "")}" placeholder="${t("Örn: Toplam karbon emisyonu")}"></div>
      <div style="display:flex;gap:8px;">
        <div style="flex:1;"><label style="font-size:12px;color:#64748b;">${t("Kategori")} *</label>
          <select id="esg-f-cat" class="swal2-select" style="width:100%;margin:2px 0;">${catOpt()}</select></div>
        <div style="flex:1;"><label style="font-size:12px;color:#64748b;">${t("Kapsam")}</label>
          <select id="esg-f-scope" class="swal2-select" style="width:100%;margin:2px 0;">${scopeOpt()}</select></div>
      </div>
      <div style="display:flex;gap:8px;">
        <div style="flex:1;"><label style="font-size:12px;color:#64748b;">${t("Kod")}</label>
          <input id="esg-f-code" class="swal2-input" style="margin:2px 0;" value="${esc(m.code || "")}" placeholder="CARBON-SC1"></div>
        <div style="flex:1;"><label style="font-size:12px;color:#64748b;">${t("Birim")}</label>
          <input id="esg-f-unit" class="swal2-input" style="margin:2px 0;" value="${esc(m.unit || "")}" placeholder="tCO2e"></div>
      </div>
      <div style="display:flex;gap:8px;">
        <div style="flex:1;"><label style="font-size:12px;color:#64748b;">${t("Hedef değer")}</label>
          <input id="esg-f-target" type="number" step="any" class="swal2-input" style="margin:2px 0;" value="${m.target_value == null ? "" : m.target_value}"></div>
        <div style="flex:1;"><label style="font-size:12px;color:#64748b;">${t("Baz yıl")}</label>
          <input id="esg-f-byear" type="number" class="swal2-input" style="margin:2px 0;" value="${m.baseline_year == null ? "" : m.baseline_year}"></div>
      </div>
      <div><label style="font-size:12px;color:#64748b;">${t("SDG kodları (virgülle)")}</label>
        <input id="esg-f-sdg" class="swal2-input" style="margin:2px 0;" value="${esc(m.sdg_codes || "")}" placeholder="SDG7, SDG13"></div>
      <div><label style="font-size:12px;color:#64748b;">${t("Açıklama")}</label>
        <textarea id="esg-f-desc" class="swal2-textarea" style="margin:2px 0;">${esc(m.description || "")}</textarea></div>
    </div>`;
  }

  function readMetricForm() {
    const name = document.getElementById("esg-f-name").value.trim();
    if (!name) { Swal.showValidationMessage(t("Ad zorunludur.")); return false; }
    return {
      name,
      category: document.getElementById("esg-f-cat").value,
      scope: document.getElementById("esg-f-scope").value,
      code: document.getElementById("esg-f-code").value.trim(),
      unit: document.getElementById("esg-f-unit").value.trim(),
      target_value: document.getElementById("esg-f-target").value,
      baseline_year: document.getElementById("esg-f-byear").value,
      sdg_codes: document.getElementById("esg-f-sdg").value.trim(),
      description: document.getElementById("esg-f-desc").value.trim(),
    };
  }

  async function openMetricModal(m) {
    const editing = !!m;
    const { value: vals } = await Swal.fire({
      title: editing ? t("Metrik düzenle") : t("Yeni ESG metriği"),
      width: 560, html: metricFormHtml(m), focusConfirm: false, showCancelButton: true,
      confirmButtonText: editing ? t("Güncelle") : t("Ekle"), cancelButtonText: t("İptal"),
      confirmButtonColor: "#22c55e", preConfirm: readMetricForm,
    });
    if (!vals) return;
    try {
      const d = editing
        ? await postJson(`${UPDATE_BASE}${m.id}`, vals)
        : await postJson(ADD_URL, vals);
      if (d.success) { toast(editing ? t("Güncellendi.") : t("Eklendi.")); load(); }
      else showError(d.message || t("İşlem başarısız."));
    } catch (e) { showError(t("Sunucu hatası:") + " " + e.message); }
  }

  async function openValueModal(metricId) {
    const m = METRICS.find((x) => x.id === metricId) || {};
    const { value: vals } = await Swal.fire({
      title: t("Yıllık değer gir"),
      width: 460,
      html: `<div style="text-align:left;font-size:13px;display:flex;flex-direction:column;gap:8px;">
        <div style="font-size:12px;color:#64748b;">${esc(m.name || "")}</div>
        <div style="display:flex;gap:8px;">
          <div style="flex:1;"><label style="font-size:12px;color:#64748b;">${t("Yıl")} *</label>
            <input id="esg-v-year" type="number" class="swal2-input" style="margin:2px 0;" placeholder="2026"></div>
          <div style="flex:1;"><label style="font-size:12px;color:#64748b;">${t("Değer")} (${esc(m.unit || "")})</label>
            <input id="esg-v-val" type="number" step="any" class="swal2-input" style="margin:2px 0;"></div>
        </div>
        <div><label style="font-size:12px;color:#64748b;">${t("Kaynak")}</label>
          <input id="esg-v-src" class="swal2-input" style="margin:2px 0;" placeholder="${t("Ölçüm / tahmin / fatura")}"></div>
        <div><label style="font-size:12px;color:#64748b;">${t("Not")}</label>
          <textarea id="esg-v-notes" class="swal2-textarea" style="margin:2px 0;"></textarea></div>
      </div>`,
      focusConfirm: false, showCancelButton: true, confirmButtonText: t("Kaydet"),
      cancelButtonText: t("İptal"), confirmButtonColor: "#22c55e",
      preConfirm: () => {
        const year = document.getElementById("esg-v-year").value.trim();
        if (!year) { Swal.showValidationMessage(t("Yıl zorunludur.")); return false; }
        return {
          year, value: document.getElementById("esg-v-val").value,
          source: document.getElementById("esg-v-src").value.trim(),
          notes: document.getElementById("esg-v-notes").value.trim(),
        };
      },
    });
    if (!vals) return;
    try {
      const d = await postJson(`${UPDATE_BASE}${metricId}/value`, vals);
      if (d.success) { toast(t("Değer kaydedildi.")); load(); }
      else showError(d.message || t("Kaydedilemedi."));
    } catch (e) { showError(t("Sunucu hatası:") + " " + e.message); }
  }

  async function delMetric(id, name) {
    const r = await Swal.fire({
      title: t("Metrik silinsin mi?"), text: `"${name}" ${t("ve değerleri pasife alınacak.")}`,
      icon: "warning", showCancelButton: true, confirmButtonColor: "#dc2626",
      confirmButtonText: t("Evet, sil"), cancelButtonText: t("İptal"),
    });
    if (!r.isConfirmed) return;
    try {
      const d = await postJson(`${UPDATE_BASE}${id}/delete`, {});
      if (d.success) { toast(t("Silindi.")); load(); }
      else showError(d.message || t("Silinemedi."));
    } catch (e) { showError(t("Sunucu hatası:") + " " + e.message); }
  }

  async function delValue(vid) {
    try {
      const d = await postJson(`/reports/api/esg/values/${vid}/delete`, {});
      if (d.success) { toast(t("Değer silindi.")); load(); }
      else showError(d.message || t("Silinemedi."));
    } catch (e) { showError(t("Sunucu hatası:") + " " + e.message); }
  }

  if (addBtn) addBtn.addEventListener("click", () => openMetricModal(null));

  groupsEl.addEventListener("click", (e) => {
    const edit = e.target.closest(".esg-edit");
    if (edit) { openMetricModal(METRICS.find((m) => m.id === parseInt(edit.dataset.id, 10))); return; }
    const del = e.target.closest(".esg-del");
    if (del) { delMetric(parseInt(del.dataset.id, 10), del.dataset.name); return; }
    const vadd = e.target.closest(".esg-val-add");
    if (vadd) { openValueModal(parseInt(vadd.dataset.id, 10)); return; }
    const vdel = e.target.closest(".esg-val-del");
    if (vdel) { delValue(parseInt(vdel.dataset.vid, 10)); return; }
  });

  async function load() {
    try {
      const res = await fetch(LIST_URL, { credentials: "same-origin" });
      const d = await res.json();
      loadingEl.style.display = "none";
      if (!d.success) { showError(d.message || t("ESG verisi alınamadı.")); return; }
      METRICS = d.metrics || [];
      render();
    } catch (e) {
      loadingEl.style.display = "none";
      showError(t("Sunucu hatası:") + " " + e.message);
    }
  }

  load();
})();
