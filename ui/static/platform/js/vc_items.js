/**
 * vc_items.js — Değer Zinciri faaliyet yönetimi (L3 eksik tamamlama)
 *
 * Porter değer zinciri: birincil (primary) + destek (support) faaliyetler.
 * Her faaliyet: başlık + opsiyonel muda (israf) türü + süreç bağı.
 * Kural: alert/confirm YASAK → SweetAlert2. Jinja {{ }} YASAK → data-*.
 */
(function () {
  "use strict";

  const root = document.getElementById("vc-items-root");
  if (!root) return;

  const LIST_URL = root.dataset.listUrl;
  const ADD_URL = root.dataset.addUrl;
  const UPDATE_BASE = root.dataset.updateBase; // /k-radar/api/kp/deger-zinciri/items/
  const CAN_EDIT = root.dataset.canEdit === "true";

  const CAT_META = {
    primary: { label: "Birincil Faaliyetler", icon: "fa-arrow-right-long", color: "#0891b2" },
    support: { label: "Destek Faaliyetler", icon: "fa-screwdriver-wrench", color: "#7c3aed" },
  };
  const MUDA_LABELS = {
    "": "—", fazla_uretim: "Fazla üretim", bekleme: "Bekleme", tasima: "Taşıma",
    fazla_isleme: "Fazla işleme", stok: "Stok", hareket: "Hareket", hata: "Hata/Düzeltme",
  };

  const loadingEl = document.getElementById("vc-loading");
  const groupsEl = document.getElementById("vc-groups");
  const emptyEl = document.getElementById("vc-empty");
  const addBtn = document.getElementById("vc-add");

  let ITEMS = [];
  let PROCESSES = [];

  function getCsrf() {
    const m = document.querySelector('meta[name="csrf-token"]');
    return m ? m.content : "";
  }
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function showError(msg) { Swal.fire({ icon: "error", title: "Hata", text: msg, confirmButtonColor: "#dc2626" }); }
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

  function procName(pid) {
    const p = PROCESSES.find((x) => x.id === pid);
    return p ? (p.code ? p.code + " · " : "") + p.name : null;
  }

  function itemRow(it) {
    const muda = it.muda_type ? `<span style="font-size:11px;color:#b45309;background:#fffbeb;border:1px solid #fde68a;border-radius:4px;padding:1px 6px;">${esc(MUDA_LABELS[it.muda_type] || it.muda_type)}</span>` : "";
    const proc = it.linked_process_id ? `<span style="font-size:11px;color:#64748b;"><i class="fas fa-gear" style="font-size:9px;"></i> ${esc(procName(it.linked_process_id) || "süreç")}</span>` : "";
    return `<div style="display:flex;align-items:flex-start;gap:8px;padding:8px;border:1px solid #eef2f7;border-radius:6px;background:var(--bg-default,#fff);">
      <div style="flex:1;min-width:0;">
        <div style="font-size:13px;font-weight:600;color:var(--text-default);">${esc(it.title)}</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:3px;align-items:center;">${muda}${proc}</div>
        ${it.note ? `<div style="font-size:12px;color:#64748b;margin-top:3px;">${esc(it.note)}</div>` : ""}
      </div>
      ${CAN_EDIT ? `<div style="display:flex;gap:4px;flex:none;">
        <button type="button" class="vc-edit" data-id="${it.id}" style="background:none;border:none;color:#94a3b8;cursor:pointer;padding:2px;" title="Düzenle"><i class="fas fa-pen"></i></button>
        <button type="button" class="vc-del" data-id="${it.id}" data-title="${esc(it.title)}" style="background:none;border:none;color:#f87171;cursor:pointer;padding:2px;" title="Sil"><i class="fas fa-trash"></i></button>
      </div>` : ""}
    </div>`;
  }

  function render() {
    if (!ITEMS.length) {
      groupsEl.innerHTML = "";
      emptyEl.style.display = "block";
      return;
    }
    emptyEl.style.display = "none";
    groupsEl.innerHTML = ["primary", "support"].map((cat) => {
      const meta = CAT_META[cat];
      const items = ITEMS.filter((i) => i.category === cat);
      const body = items.map(itemRow).join("") ||
        '<div style="color:#94a3b8;font-size:12px;padding:6px 0;">Bu grupta faaliyet yok.</div>';
      return `<div class="mc-card" style="border-top:3px solid ${meta.color};">
        <div class="mc-card-header" style="display:flex;align-items:center;gap:8px;">
          <i class="fas ${meta.icon}" style="color:${meta.color};"></i>
          <span class="mc-card-title">${meta.label}</span>
          <span style="margin-left:auto;font-size:11px;color:#94a3b8;">${items.length}</span>
        </div>
        <div class="mc-card-body" style="padding:10px 12px;display:flex;flex-direction:column;gap:8px;">${body}</div>
      </div>`;
    }).join("");
  }

  function formHtml(it) {
    it = it || {};
    const catOpt = Object.keys(CAT_META).map((c) =>
      `<option value="${c}" ${it.category === c ? "selected" : ""}>${CAT_META[c].label}</option>`).join("");
    const mudaOpt = Object.keys(MUDA_LABELS).map((m) =>
      `<option value="${m}" ${it.muda_type === m ? "selected" : ""}>${MUDA_LABELS[m]}</option>`).join("");
    const procOpt = ['<option value="">— Süreç bağı yok —</option>'].concat(
      PROCESSES.map((p) =>
        `<option value="${p.id}" ${it.linked_process_id === p.id ? "selected" : ""}>${esc((p.code ? p.code + " · " : "") + p.name)}</option>`)
    ).join("");
    return `<div style="text-align:left;font-size:13px;display:flex;flex-direction:column;gap:8px;">
      <div><label style="font-size:12px;color:#64748b;">Başlık *</label>
        <input id="vc-f-title" class="swal2-input" style="margin:2px 0;" value="${esc(it.title || "")}" placeholder="Örn: Gelen lojistik"></div>
      <div style="display:flex;gap:8px;">
        <div style="flex:1;"><label style="font-size:12px;color:#64748b;">Grup *</label>
          <select id="vc-f-cat" class="swal2-select" style="width:100%;margin:2px 0;">${catOpt}</select></div>
        <div style="flex:1;"><label style="font-size:12px;color:#64748b;">Muda (israf) türü</label>
          <select id="vc-f-muda" class="swal2-select" style="width:100%;margin:2px 0;">${mudaOpt}</select></div>
      </div>
      <div><label style="font-size:12px;color:#64748b;">Bağlı süreç</label>
        <select id="vc-f-proc" class="swal2-select" style="width:100%;margin:2px 0;">${procOpt}</select></div>
      <div><label style="font-size:12px;color:#64748b;">Not</label>
        <textarea id="vc-f-note" class="swal2-textarea" style="margin:2px 0;">${esc(it.note || "")}</textarea></div>
    </div>`;
  }

  function readForm() {
    const title = document.getElementById("vc-f-title").value.trim();
    if (!title) { Swal.showValidationMessage("Başlık zorunludur."); return false; }
    return {
      title,
      category: document.getElementById("vc-f-cat").value,
      muda_type: document.getElementById("vc-f-muda").value,
      linked_process_id: document.getElementById("vc-f-proc").value || null,
      note: document.getElementById("vc-f-note").value.trim(),
    };
  }

  async function openModal(it) {
    const editing = !!it;
    const { value: vals } = await Swal.fire({
      title: editing ? "Faaliyet düzenle" : "Yeni değer zinciri faaliyeti",
      width: 520, html: formHtml(it), focusConfirm: false, showCancelButton: true,
      confirmButtonText: editing ? "Güncelle" : "Ekle", cancelButtonText: "İptal",
      confirmButtonColor: "#0891b2", preConfirm: readForm,
    });
    if (!vals) return;
    try {
      const d = editing ? await postJson(`${UPDATE_BASE}${it.id}`, vals) : await postJson(ADD_URL, vals);
      if (d.success) { toast(editing ? "Güncellendi." : "Eklendi."); load(); }
      else showError(d.message || "İşlem başarısız.");
    } catch (e) { showError("Sunucu hatası: " + e.message); }
  }

  async function delItem(id, title) {
    const r = await Swal.fire({
      title: "Faaliyet silinsin mi?", text: `"${title}" pasife alınacak.`,
      icon: "warning", showCancelButton: true, confirmButtonColor: "#dc2626",
      confirmButtonText: "Evet, sil", cancelButtonText: "İptal",
    });
    if (!r.isConfirmed) return;
    try {
      const d = await postJson(`${UPDATE_BASE}${id}/delete`, {});
      if (d.success) { toast("Silindi."); load(); }
      else showError(d.message || "Silinemedi.");
    } catch (e) { showError("Sunucu hatası: " + e.message); }
  }

  if (addBtn) addBtn.addEventListener("click", () => openModal(null));
  groupsEl.addEventListener("click", (e) => {
    const edit = e.target.closest(".vc-edit");
    if (edit) { openModal(ITEMS.find((i) => i.id === parseInt(edit.dataset.id, 10))); return; }
    const del = e.target.closest(".vc-del");
    if (del) { delItem(parseInt(del.dataset.id, 10), del.dataset.title); return; }
  });

  async function load() {
    try {
      const res = await fetch(LIST_URL, { credentials: "same-origin" });
      const d = await res.json();
      loadingEl.style.display = "none";
      if (!d.success) { showError(d.message || "Veri alınamadı."); return; }
      ITEMS = d.items || [];
      PROCESSES = d.processes || [];
      render();
    } catch (e) {
      loadingEl.style.display = "none";
      showError("Sunucu hatası: " + e.message);
    }
  }

  load();
})();
