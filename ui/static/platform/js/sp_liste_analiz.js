/**
 * sp_liste_analiz.js — SWOT / TOWS / PESTEL ortak liste editörü (L3 Dal 2)
 *
 * Desen: kategoriler × madde listesi. Her kategori bir kart; madde ekle/sil; tek
 * "Kaydet" butonu tüm kategorileri upsert eder. Plan-year bazlı (API yönetir).
 *
 * Kural: alert/confirm YASAK → SweetAlert2. Jinja {{ }} YASAK → data-* attribute.
 *
 * Konfig (root data-*):
 *   data-get-url   : GET endpoint (success.data = {kategori_key: [string,...]})
 *   data-save-url  : POST endpoint (body = {kategori_key: [string,...]})
 *   data-keys      : JSON [{key, label, icon, color}] — kategori tanımları
 *   data-can-edit  : "true"/"false"
 */
(function () {
  "use strict";

  const root = document.getElementById("sp-liste-analiz");
  if (!root) return;

  const GET_URL = root.dataset.getUrl;
  const SAVE_URL = root.dataset.saveUrl;
  const CAN_EDIT = root.dataset.canEdit === "true";
  let KEYS = [];
  try { KEYS = JSON.parse(root.dataset.keys || "[]"); } catch (_e) { KEYS = []; }

  const grid = document.getElementById("sla-grid");
  const saveBtn = document.getElementById("sla-save");

  // Bellekteki durum: { key: [string,...] }
  const state = {};

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
    Swal.fire({ icon: "error", title: "Hata", text: msg, confirmButtonColor: "#dc2626" });
  }
  function toast(msg) {
    Swal.fire({
      toast: true, position: "top-end", icon: "success", title: msg,
      showConfirmButton: false, timer: 2200, timerProgressBar: true,
    });
  }

  function renderKategori(def) {
    const items = state[def.key] || [];
    const lis = items.map((t, i) => `
      <li class="sla-item" style="display:flex;align-items:flex-start;gap:8px;padding:6px 0;border-bottom:1px solid var(--border-subtle,#eef2f7);">
        <span style="flex:1;font-size:13px;line-height:1.5;color:var(--text-default);">${esc(t)}</span>
        ${CAN_EDIT ? `<button type="button" class="sla-del" data-key="${def.key}" data-idx="${i}"
            style="flex:none;background:none;border:none;color:#cbd5e1;cursor:pointer;padding:2px 4px;"
            title="Sil"><i class="fas fa-times"></i></button>` : ""}
      </li>`).join("");

    return `
      <div class="mc-card" style="border-top:3px solid ${def.color};">
        <div class="mc-card-header" style="display:flex;align-items:center;gap:8px;">
          <i class="fas ${def.icon}" style="color:${def.color};"></i>
          <span class="mc-card-title">${esc(def.label)}</span>
          <span style="margin-left:auto;font-size:11px;color:#94a3b8;">${items.length}</span>
        </div>
        <div class="mc-card-body" style="padding:10px 14px;">
          <ul style="list-style:none;margin:0 0 8px;padding:0;">${lis || '<li style="color:#94a3b8;font-size:12px;padding:6px 0;">Madde yok.</li>'}</ul>
          ${CAN_EDIT ? `<button type="button" class="sla-add" data-key="${def.key}"
              style="font-size:12px;font-weight:600;color:${def.color};background:none;border:none;cursor:pointer;padding:2px 0;">
              <i class="fas fa-plus" style="font-size:10px;"></i> Madde ekle</button>` : ""}
        </div>
      </div>`;
  }

  function render() {
    grid.innerHTML = KEYS.map(renderKategori).join("");
  }

  async function onAdd(key) {
    const { value: txt } = await Swal.fire({
      title: "Madde ekle", input: "textarea",
      inputPlaceholder: "Madde metni…", showCancelButton: true,
      confirmButtonText: "Ekle", cancelButtonText: "İptal", confirmButtonColor: "#4f46e5",
      inputValidator: (v) => (!v || !v.trim()) ? "Boş olamaz." : undefined,
    });
    if (!txt || !txt.trim()) return;
    (state[key] = state[key] || []).push(txt.trim());
    render();
  }

  function onDel(key, idx) {
    if (!state[key]) return;
    state[key].splice(idx, 1);
    render();
  }

  async function save() {
    if (!CAN_EDIT) return;
    saveBtn.disabled = true;
    const original = saveBtn.innerHTML;
    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Kaydediliyor…';
    try {
      const body = {};
      KEYS.forEach((d) => { body[d.key] = state[d.key] || []; });
      const res = await fetch(SAVE_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrf() },
        credentials: "same-origin", body: JSON.stringify(body),
      });
      const d = await res.json();
      if (d.success) toast("Kaydedildi.");
      else showError(d.message || "Kaydedilemedi.");
    } catch (e) {
      showError("Sunucu hatası: " + e.message);
    } finally {
      saveBtn.disabled = false;
      saveBtn.innerHTML = original;
    }
  }

  // Delege olaylar
  grid.addEventListener("click", (e) => {
    const add = e.target.closest(".sla-add");
    if (add) { onAdd(add.dataset.key); return; }
    const del = e.target.closest(".sla-del");
    if (del) { onDel(del.dataset.key, parseInt(del.dataset.idx, 10)); return; }
  });
  if (saveBtn) saveBtn.addEventListener("click", save);

  async function load() {
    try {
      const res = await fetch(GET_URL, { credentials: "same-origin" });
      const d = await res.json();
      if (!d.success) { showError(d.message || "Veri alınamadı."); return; }
      KEYS.forEach((def) => { state[def.key] = Array.isArray(d.data[def.key]) ? d.data[def.key] : []; });
      render();
    } catch (e) {
      showError("Sunucu hatası: " + e.message);
    }
  }

  load();
})();
