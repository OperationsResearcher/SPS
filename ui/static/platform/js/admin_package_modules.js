/**
 * admin_package_modules.js — Paket ↔ Modül atama (paket içeriği yönetimi)
 *
 * Pakete tıkla ("Modüller") → açılır panel: tüm modüller (içerdikleri işaretli)
 * + her modülün bileşen önizlemesi. Checkbox toggle → paket-modül bağı.
 * Kural: alert/confirm YASAK → SweetAlert2. Jinja {{ }} YASAK → data-*.
 */
(function () {
  "use strict";

  const root = document.getElementById("admin-packages-root");
  if (!root) return;
  const BASE = root.dataset.pkgModulesBase; // /admin/packages/

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
      showConfirmButton: false, timer: 1600, timerProgressBar: true });
  }

  function panelFor(pkgId) {
    return document.querySelector(`.pkg-modules-panel[data-pkg-id="${pkgId}"]`);
  }

  function moduleRow(pkgId, m) {
    const comps = (m.components || []);
    const compPreview = comps.length
      ? `<div style="font-size:10.5px;color:#94a3b8;margin-top:2px;">${comps.length} ${t("bileşen")}: ${esc(comps.slice(0, 5).join(", "))}${comps.length > 5 ? "…" : ""}</div>`
      : `<div style="font-size:10.5px;color:#cbd5e1;margin-top:2px;">${t("bileşen yok")}</div>`;
    return `<label style="display:flex;align-items:flex-start;gap:8px;padding:7px 0;border-bottom:1px solid #eef2f7;cursor:pointer;">
      <input type="checkbox" class="pkg-mod-cb" data-pkg-id="${pkgId}" data-mod-id="${m.id}"
             ${m.in_package ? "checked" : ""} style="margin-top:3px;">
      <div style="flex:1;min-width:0;">
        <div style="font-size:12.5px;font-weight:500;color:var(--text-default);">${esc(m.name)}</div>
        <div style="font-size:10.5px;color:#94a3b8;font-family:monospace;">${esc(m.code)}</div>
        ${compPreview}
      </div>
    </label>`;
  }

  async function loadPanel(pkgId, pkgName) {
    const panel = panelFor(pkgId);
    if (!panel) return;
    panel.innerHTML = '<div style="padding:10px 0;color:#94a3b8;font-size:12px;"><i class="fas fa-spinner fa-spin"></i> ' + t("Yükleniyor…") + '</div>';
    try {
      const res = await fetch(`${BASE}${pkgId}/modules`, { credentials: "same-origin" });
      const d = await res.json();
      if (!d.success) { panel.innerHTML = `<div style="color:#dc2626;font-size:12px;">${esc(d.message || t("Hata"))}</div>`; return; }
      const inCount = d.modules.filter((m) => m.in_package).length;
      panel.innerHTML =
        `<div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;color:#64748b;padding:8px 0 4px;">
           ${esc(pkgName)} — ${t("içerdiği modüller")} (${inCount}/${d.modules.length})
         </div>` +
        d.modules.map((m) => moduleRow(pkgId, m)).join("");
    } catch (e) {
      panel.innerHTML = `<div style="color:#dc2626;font-size:12px;">${t("Sunucu hatası")}: ${esc(e.message)}</div>`;
    }
  }

  async function toggleModule(pkgId, modId, checkbox) {
    checkbox.disabled = true;
    try {
      const res = await fetch(`${BASE}${pkgId}/modules/${modId}/toggle`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrf() },
        credentials: "same-origin",
      });
      const d = await res.json();
      if (d.success) {
        checkbox.checked = d.in_package;
        toast(d.message || t("Güncellendi."));
      } else {
        checkbox.checked = !checkbox.checked; // geri al
        showError(d.message || t("İşlem başarısız."));
      }
    } catch (e) {
      checkbox.checked = !checkbox.checked;
      showError(t("Sunucu hatası") + ": " + e.message);
    } finally {
      checkbox.disabled = false;
    }
  }

  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".btn-pkg-modules");
    if (btn) {
      const pkgId = btn.dataset.pkgId;
      const panel = panelFor(pkgId);
      if (!panel) return;
      if (panel.style.display === "none" || !panel.style.display) {
        panel.style.display = "block";
        loadPanel(pkgId, btn.dataset.pkgName);
      } else {
        panel.style.display = "none";
      }
    }
  });

  document.addEventListener("change", (e) => {
    const cb = e.target.closest(".pkg-mod-cb");
    if (cb) toggleModule(cb.dataset.pkgId, cb.dataset.modId, cb);
  });
})();
