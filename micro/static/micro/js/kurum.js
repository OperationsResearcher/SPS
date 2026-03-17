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

  // ── Stratejik Kimlik Düzenle ─────────────────────────────────────────────
  document.getElementById("btn-identity-edit")?.addEventListener("click", async () => {
    // Mevcut değerleri sayfadan oku
    const cells = document.querySelectorAll("#kurum-root .grid p");
    const vals = Array.from(cells).map(p => p.textContent.trim() === "—" ? "" : p.textContent.trim());

    const { value: form } = await Swal.fire({
      title: "Stratejik Kimlik Düzenle",
      width: 640,
      html: `<div class="text-left space-y-3 text-sm">
        <div><label class="block text-xs text-gray-500 mb-1">Amaç</label>
          <textarea id="sk-purpose" class="swal2-textarea" rows="2">${escHtml(vals[0])}</textarea></div>
        <div><label class="block text-xs text-gray-500 mb-1">Vizyon</label>
          <textarea id="sk-vision" class="swal2-textarea" rows="2">${escHtml(vals[1])}</textarea></div>
        <div><label class="block text-xs text-gray-500 mb-1">Temel Değerler</label>
          <textarea id="sk-values" class="swal2-textarea" rows="2">${escHtml(vals[2])}</textarea></div>
        <div><label class="block text-xs text-gray-500 mb-1">Etik Kurallar</label>
          <textarea id="sk-ethics" class="swal2-textarea" rows="2">${escHtml(vals[3])}</textarea></div>
        <div><label class="block text-xs text-gray-500 mb-1">Kalite Politikası</label>
          <textarea id="sk-quality" class="swal2-textarea" rows="2">${escHtml(vals[4])}</textarea></div>
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

  // ── Ana Strateji Ekle ────────────────────────────────────────────────────
  document.getElementById("btn-strategy-add")?.addEventListener("click", async () => {
    const { value: vals } = await Swal.fire({
      title: "Yeni Strateji Ekle",
      html: `<div class="text-left space-y-3">
        <div><label class="block text-xs text-gray-500 mb-1">Başlık <span class="text-red-500">*</span></label>
          <input id="st-title" class="swal2-input" placeholder="Strateji başlığı"></div>
        <div><label class="block text-xs text-gray-500 mb-1">Kod</label>
          <input id="st-code" class="swal2-input" placeholder="Örn: ST1"></div>
      </div>`,
      focusConfirm: false, showCancelButton: true,
      confirmButtonText: "Kaydet", cancelButtonText: "İptal", confirmButtonColor: "#4f46e5",
      preConfirm: () => {
        const title = document.getElementById("st-title").value.trim();
        if (!title) { Swal.showValidationMessage("Başlık zorunludur."); return false; }
        return { title, code: document.getElementById("st-code").value.trim() || null };
      },
    });
    if (!vals) return;
    try {
      const d = await postJson(ADD_STRATEGY_URL, vals);
      if (d.success) { toastSuccess("Strateji eklendi."); reload(); }
      else showError(d.message || "Kayıt başarısız.");
    } catch (e) { showError("Sunucu hatası: " + e.message); }
  });

  // ── Event delegation ─────────────────────────────────────────────────────
  document.addEventListener("click", async (e) => {

    // Alt strateji ekle
    const btnSubAdd = e.target.closest(".btn-sub-add");
    if (btnSubAdd) {
      const strategyId = btnSubAdd.dataset.strategyId;
      const { value: vals } = await Swal.fire({
        title: "Alt Strateji Ekle",
        html: `<div class="text-left space-y-3">
          <div><label class="block text-xs text-gray-500 mb-1">Başlık <span class="text-red-500">*</span></label>
            <input id="ss-title" class="swal2-input" placeholder="Alt strateji başlığı"></div>
          <div><label class="block text-xs text-gray-500 mb-1">Kod</label>
            <input id="ss-code" class="swal2-input" placeholder="Örn: ST1.1"></div>
        </div>`,
        focusConfirm: false, showCancelButton: true,
        confirmButtonText: "Kaydet", cancelButtonText: "İptal", confirmButtonColor: "#4f46e5",
        preConfirm: () => {
          const title = document.getElementById("ss-title").value.trim();
          if (!title) { Swal.showValidationMessage("Başlık zorunludur."); return false; }
          return { strategy_id: strategyId, title, code: document.getElementById("ss-code").value.trim() || null };
        },
      });
      if (!vals) return;
      try {
        const d = await postJson(ADD_SUB_URL, vals);
        if (d.success) { toastSuccess("Alt strateji eklendi."); reload(); }
        else showError(d.message || "Kayıt başarısız.");
      } catch (e) { showError("Sunucu hatası: " + e.message); }
      return;
    }

    // Ana strateji düzenle
    const btnMainEdit = e.target.closest(".btn-main-edit");
    if (btnMainEdit) {
      const { strategyId, title: curTitle, code: curCode } = btnMainEdit.dataset;
      const { value: vals } = await Swal.fire({
        title: "Strateji Düzenle",
        html: `<div class="text-left space-y-3">
          <div><label class="block text-xs text-gray-500 mb-1">Başlık <span class="text-red-500">*</span></label>
            <input id="me-title" class="swal2-input" value="${escHtml(curTitle)}"></div>
          <div><label class="block text-xs text-gray-500 mb-1">Kod</label>
            <input id="me-code" class="swal2-input" value="${escHtml(curCode)}"></div>
        </div>`,
        focusConfirm: false, showCancelButton: true,
        confirmButtonText: "Güncelle", cancelButtonText: "İptal", confirmButtonColor: "#4f46e5",
        preConfirm: () => {
          const title = document.getElementById("me-title").value.trim();
          if (!title) { Swal.showValidationMessage("Başlık zorunludur."); return false; }
          return { title, code: document.getElementById("me-code").value.trim() || null };
        },
      });
      if (!vals) return;
      try {
        const d = await postJson(`${UPDATE_MAIN_BASE}${strategyId}`, vals);
        if (d.success) { toastSuccess("Strateji güncellendi."); reload(); }
        else showError(d.message || "Güncelleme başarısız.");
      } catch (e) { showError("Sunucu hatası: " + e.message); }
      return;
    }

    // Ana strateji sil
    const btnMainDel = e.target.closest(".btn-main-delete");
    if (btnMainDel) {
      const ok = await confirmDelete("Strateji silinsin mi?", `"${btnMainDel.dataset.title}" pasife alınacak.`);
      if (!ok) return;
      try {
        const d = await postJson(`${DELETE_MAIN_BASE}${btnMainDel.dataset.strategyId}`, {});
        if (d.success) { toastSuccess("Strateji silindi."); reload(); }
        else showError(d.message || "Silme başarısız.");
      } catch (e) { showError("Sunucu hatası: " + e.message); }
      return;
    }

    // Alt strateji düzenle
    const btnSubEdit = e.target.closest(".btn-sub-edit");
    if (btnSubEdit) {
      const { subId, title: curTitle, code: curCode } = btnSubEdit.dataset;
      const { value: vals } = await Swal.fire({
        title: "Alt Strateji Düzenle",
        html: `<div class="text-left space-y-3">
          <div><label class="block text-xs text-gray-500 mb-1">Başlık <span class="text-red-500">*</span></label>
            <input id="se-title" class="swal2-input" value="${escHtml(curTitle)}"></div>
          <div><label class="block text-xs text-gray-500 mb-1">Kod</label>
            <input id="se-code" class="swal2-input" value="${escHtml(curCode)}"></div>
        </div>`,
        focusConfirm: false, showCancelButton: true,
        confirmButtonText: "Güncelle", cancelButtonText: "İptal", confirmButtonColor: "#4f46e5",
        preConfirm: () => {
          const title = document.getElementById("se-title").value.trim();
          if (!title) { Swal.showValidationMessage("Başlık zorunludur."); return false; }
          return { title, code: document.getElementById("se-code").value.trim() || null };
        },
      });
      if (!vals) return;
      try {
        const d = await postJson(`${UPDATE_SUB_BASE}${subId}`, vals);
        if (d.success) { toastSuccess("Alt strateji güncellendi."); reload(); }
        else showError(d.message || "Güncelleme başarısız.");
      } catch (e) { showError("Sunucu hatası: " + e.message); }
      return;
    }

    // Alt strateji sil
    const btnSubDel = e.target.closest(".btn-sub-delete");
    if (btnSubDel) {
      const ok = await confirmDelete("Alt strateji silinsin mi?", `"${btnSubDel.dataset.title}" pasife alınacak.`);
      if (!ok) return;
      try {
        const d = await postJson(`${DELETE_SUB_BASE}${btnSubDel.dataset.subId}`, {});
        if (d.success) { toastSuccess("Alt strateji silindi."); reload(); }
        else showError(d.message || "Silme başarısız.");
      } catch (e) { showError("Sunucu hatası: " + e.message); }
    }
  });

})();
