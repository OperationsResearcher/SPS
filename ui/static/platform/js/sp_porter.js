/**
 * sp_porter.js — Porter 5 Güç editörü (L3 Dal 3)
 *
 * Her kuvvet: 1-5 skor (baskı düzeyi) + madde listesi. Tek "Kaydet" upsert eder.
 * Kural: alert/confirm YASAK → SweetAlert2. Jinja {{ }} YASAK → data-*.
 */
(function () {
  "use strict";

  const root = document.getElementById("sp-porter");
  if (!root) return;

  const GET_URL = root.dataset.getUrl;
  const SAVE_URL = root.dataset.saveUrl;
  const CAN_EDIT = root.dataset.canEdit === "true";
  let FORCES = [];
  try { FORCES = JSON.parse(root.dataset.forces || "[]"); } catch (_e) { FORCES = []; }

  const grid = document.getElementById("porter-grid");
  const saveBtn = document.getElementById("porter-save");

  // state: { key: {score: 1-5|null, items: [string,...]} }
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
    Swal.fire({ toast: true, position: "top-end", icon: "success", title: msg,
      showConfirmButton: false, timer: 2200, timerProgressBar: true });
  }

  function scoreButtons(key, score) {
    let html = '<div class="porter-score" style="display:flex;gap:4px;margin:6px 0 10px;">';
    for (let n = 1; n <= 5; n++) {
      const active = score === n;
      html += `<button type="button" class="porter-score-btn" data-key="${key}" data-score="${n}"
        ${CAN_EDIT ? "" : "disabled"}
        style="flex:1;padding:5px 0;border-radius:6px;border:1px solid ${active ? "#ea580c" : "#e2e8f0"};
        background:${active ? "#ea580c" : "var(--bg-default,#fff)"};color:${active ? "#fff" : "#64748b"};
        font-weight:700;font-size:13px;cursor:${CAN_EDIT ? "pointer" : "default"};">${n}</button>`;
    }
    return html + "</div>";
  }

  function renderForce(def) {
    const f = state[def.key] || { score: null, items: [] };
    const items = f.items || [];
    const lis = items.map((t, i) => `
      <li style="display:flex;align-items:flex-start;gap:8px;padding:5px 0;border-bottom:1px solid #eef2f7;">
        <span style="flex:1;font-size:13px;line-height:1.5;color:var(--text-default);">${esc(t)}</span>
        ${CAN_EDIT ? `<button type="button" class="porter-del" data-key="${def.key}" data-idx="${i}"
          style="flex:none;background:none;border:none;color:#cbd5e1;cursor:pointer;" title="Sil"><i class="fas fa-times"></i></button>` : ""}
      </li>`).join("");

    return `
      <div class="mc-card" style="border-top:3px solid ${def.color};">
        <div class="mc-card-header" style="display:flex;align-items:center;gap:8px;">
          <i class="fas ${def.icon}" style="color:${def.color};"></i>
          <span class="mc-card-title">${esc(def.label)}</span>
          <span style="margin-left:auto;font-size:11px;color:#94a3b8;">${f.score ? "Baskı " + f.score + "/5" : "—"}</span>
        </div>
        <div class="mc-card-body" style="padding:10px 14px;">
          ${scoreButtons(def.key, f.score)}
          <ul style="list-style:none;margin:0 0 8px;padding:0;">${lis || '<li style="color:#94a3b8;font-size:12px;padding:5px 0;">Madde yok.</li>'}</ul>
          ${CAN_EDIT ? `<button type="button" class="porter-add" data-key="${def.key}"
            style="font-size:12px;font-weight:600;color:${def.color};background:none;border:none;cursor:pointer;padding:2px 0;">
            <i class="fas fa-plus" style="font-size:10px;"></i> Madde ekle</button>` : ""}
        </div>
      </div>`;
  }

  function render() {
    grid.innerHTML = FORCES.map(renderForce).join("");
  }

  async function onAdd(key) {
    const { value: txt } = await Swal.fire({
      title: "Madde ekle", input: "textarea", inputPlaceholder: "Gözlem / faktör…",
      showCancelButton: true, confirmButtonText: "Ekle", cancelButtonText: "İptal",
      confirmButtonColor: "#ea580c",
      inputValidator: (v) => (!v || !v.trim()) ? "Boş olamaz." : undefined,
    });
    if (!txt || !txt.trim()) return;
    const f = (state[key] = state[key] || { score: null, items: [] });
    f.items.push(txt.trim());
    render();
  }

  async function save() {
    if (!CAN_EDIT) return;
    saveBtn.disabled = true;
    const orig = saveBtn.innerHTML;
    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Kaydediliyor…';
    try {
      const body = {};
      FORCES.forEach((d) => { body[d.key] = state[d.key] || { score: null, items: [] }; });
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
      saveBtn.innerHTML = orig;
    }
  }

  grid.addEventListener("click", (e) => {
    const sb = e.target.closest(".porter-score-btn");
    if (sb && CAN_EDIT) {
      const key = sb.dataset.key;
      const n = parseInt(sb.dataset.score, 10);
      const f = (state[key] = state[key] || { score: null, items: [] });
      f.score = (f.score === n) ? null : n;  // tekrar tıkla = temizle
      render();
      return;
    }
    const add = e.target.closest(".porter-add");
    if (add) { onAdd(add.dataset.key); return; }
    const del = e.target.closest(".porter-del");
    if (del) {
      const f = state[del.dataset.key];
      if (f) { f.items.splice(parseInt(del.dataset.idx, 10), 1); render(); }
      return;
    }
  });
  if (saveBtn) saveBtn.addEventListener("click", save);

  async function load() {
    try {
      const res = await fetch(GET_URL, { credentials: "same-origin" });
      const d = await res.json();
      if (!d.success) { showError(d.message || "Veri alınamadı."); return; }
      FORCES.forEach((def) => {
        const v = d.data[def.key] || {};
        state[def.key] = { score: v.score || null, items: Array.isArray(v.items) ? v.items : [] };
      });
      render();
    } catch (e) {
      showError("Sunucu hatası: " + e.message);
    }
  }

  load();
})();
