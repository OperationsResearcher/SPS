/**
 * project_kapasite.js — Proje kapasite planlama UI (L3 eksik tamamlama)
 *
 * API (/api/projeler/<id>/kapasite GET/POST, .../<plan_id> DELETE) vardı, UI yoktu.
 * Ekip üyelerine haftalık saat + dönem ata.
 * Kural: alert/confirm YASAK → SweetAlert2. Jinja {{ }} YASAK → data-*.
 */
(function () {
  "use strict";

  const root = document.getElementById("kapasite-root");
  if (!root) return;

  const LIST_URL = root.dataset.listUrl;
  const DELETE_BASE = root.dataset.deleteBase; // /api/projeler/<id>/kapasite/
  let EKIP = [];
  try { EKIP = JSON.parse(root.dataset.ekip || "[]"); } catch (_e) { EKIP = []; }

  const loadingEl = document.getElementById("kap-loading");
  const tableWrap = document.getElementById("kap-table-wrap");
  const tbody = document.getElementById("kap-tbody");
  const emptyEl = document.getElementById("kap-empty");
  const addBtn = document.getElementById("kap-add");

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

  function ekipName(uid) {
    const u = EKIP.find((x) => x.id === uid);
    return u ? u.name : ("Kullanıcı #" + uid);
  }

  function render(plans) {
    if (!plans.length) {
      tableWrap.style.display = "none";
      emptyEl.style.display = "block";
      return;
    }
    emptyEl.style.display = "none";
    tableWrap.style.display = "block";
    tbody.innerHTML = plans.map((p) => `
      <tr>
        <td>${esc(ekipName(p.user_id))}</td>
        <td style="text-align:right;font-weight:600;">${p.weekly_hours == null ? "—" : esc(p.weekly_hours)} sa</td>
        <td>${p.start_date ? esc(p.start_date) : "—"}</td>
        <td>${p.end_date ? esc(p.end_date) : "—"}</td>
        <td style="text-align:right;">
          <button type="button" class="kap-del" data-id="${p.id}" style="background:none;border:none;color:#f87171;cursor:pointer;" title="Sil"><i class="fas fa-trash"></i></button>
        </td>
      </tr>`).join("");
  }

  async function openModal() {
    if (!EKIP.length) {
      showError("Bu projede ekip üyesi yok. Önce projeye lider/üye ekleyin.");
      return;
    }
    const ekipOpt = EKIP.map((u) => `<option value="${u.id}">${esc(u.name)}</option>`).join("");
    const { value: vals } = await Swal.fire({
      title: "Kapasite ekle", width: 460, focusConfirm: false, showCancelButton: true,
      confirmButtonText: "Ekle", cancelButtonText: "İptal", confirmButtonColor: "#0891b2",
      html: `<div style="text-align:left;font-size:13px;display:flex;flex-direction:column;gap:8px;">
        <div><label style="font-size:12px;color:#64748b;">Kişi *</label>
          <select id="kap-f-user" class="swal2-select" style="width:100%;margin:2px 0;">${ekipOpt}</select></div>
        <div><label style="font-size:12px;color:#64748b;">Haftalık saat</label>
          <input id="kap-f-hours" type="number" step="any" class="swal2-input" style="margin:2px 0;" value="40"></div>
        <div style="display:flex;gap:8px;">
          <div style="flex:1;"><label style="font-size:12px;color:#64748b;">Başlangıç</label>
            <input id="kap-f-start" type="date" class="swal2-input" style="margin:2px 0;"></div>
          <div style="flex:1;"><label style="font-size:12px;color:#64748b;">Bitiş</label>
            <input id="kap-f-end" type="date" class="swal2-input" style="margin:2px 0;"></div>
        </div>
      </div>`,
      preConfirm: () => ({
        user_id: parseInt(document.getElementById("kap-f-user").value, 10),
        weekly_hours: document.getElementById("kap-f-hours").value || 40,
        start_date: document.getElementById("kap-f-start").value || null,
        end_date: document.getElementById("kap-f-end").value || null,
      }),
    });
    if (!vals) return;
    try {
      const res = await fetch(LIST_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrf() },
        credentials: "same-origin", body: JSON.stringify(vals),
      });
      const d = await res.json();
      if (d.success) { toast("Kapasite eklendi."); load(); }
      else showError(d.message || "Eklenemedi.");
    } catch (e) { showError("Sunucu hatası: " + e.message); }
  }

  async function delPlan(id) {
    const r = await Swal.fire({
      title: "Kapasite silinsin mi?", icon: "warning", showCancelButton: true,
      confirmButtonColor: "#dc2626", confirmButtonText: "Evet, sil", cancelButtonText: "İptal",
    });
    if (!r.isConfirmed) return;
    try {
      const res = await fetch(`${DELETE_BASE}${id}`, {
        method: "DELETE",
        headers: { "X-CSRFToken": getCsrf() }, credentials: "same-origin",
      });
      const d = await res.json();
      if (d.success) { toast("Silindi."); load(); }
      else showError(d.message || "Silinemedi.");
    } catch (e) { showError("Sunucu hatası: " + e.message); }
  }

  if (addBtn) addBtn.addEventListener("click", openModal);
  tbody.addEventListener("click", (e) => {
    const del = e.target.closest(".kap-del");
    if (del) delPlan(parseInt(del.dataset.id, 10));
  });

  async function load() {
    try {
      const res = await fetch(LIST_URL, { credentials: "same-origin" });
      const d = await res.json();
      loadingEl.style.display = "none";
      if (!d.success) { showError(d.message || "Kapasite verisi alınamadı."); return; }
      render(d.plans || []);
    } catch (e) {
      loadingEl.style.display = "none";
      showError("Sunucu hatası: " + e.message);
    }
  }

  load();
})();
