/**
 * admin_hierarchy.js — SaaS 4-katman ağacı (paket→modül→bileşen→kart→veri).
 *
 * Ağaç açılır-kapanır; "Kartları Keşfet" → template data-card-* tarar.
 * Veri kaynaklarında required_component rozeti = çapraz-paket veri farkındalığı.
 * Kural: alert/confirm YASAK → SweetAlert2. Jinja {{ }} YASAK → data-*.
 */
(function () {
  "use strict";

  const root = document.getElementById("hierarchy-root");
  if (!root) return;
  const TREE_URL = root.dataset.treeUrl;
  const DISCOVER_URL = root.dataset.discoverUrl;

  const loadingEl = document.getElementById("hierarchy-loading");
  const treeEl = document.getElementById("hierarchy-tree");
  const discoverBtn = document.getElementById("btn-discover");

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
      showConfirmButton: false, timer: 2600, timerProgressBar: true });
  }

  function dataSourceRow(d) {
    const req = d.required_component_code
      ? `<span style="font-size:10.5px;color:#b45309;background:#fffbeb;border:1px solid #fde68a;border-radius:4px;padding:1px 6px;margin-left:6px;" title="Bu veri yalnızca '${esc(d.required_component_code)}' bileşeni pakette varsa görünür">↳ ${esc(d.required_component_code)}</span>`
      : `<span style="font-size:10.5px;color:#64748b;margin-left:6px;">(kısıtsız)</span>`;
    return `<div style="display:flex;align-items:center;font-size:12px;padding:3px 0 3px 16px;">
      <i class="fas fa-database" style="color:#cbd5e1;font-size:9px;margin-right:6px;"></i>
      <span style="font-family:monospace;color:var(--text-default);">${esc(d.data_key)}</span>
      ${d.label ? `<span style="color:#94a3b8;margin-left:6px;">${esc(d.label)}</span>` : ""}
      ${req}
    </div>`;
  }

  function cardNode(card) {
    const ds = (card.data_sources || []).map(dataSourceRow).join("") ||
      '<div style="font-size:11px;color:#cbd5e1;padding-left:16px;">veri kaynağı yok</div>';
    return `<div style="padding:4px 0 4px 14px;border-left:2px solid #ede9fe;margin-left:6px;">
      <div style="font-size:12.5px;font-weight:600;color:#7c3aed;">
        <i class="fas fa-table-cells-large" style="font-size:10px;margin-right:5px;"></i>${esc(card.name)}
        <span style="font-family:monospace;font-size:10px;color:#a78bfa;">${esc(card.code)}</span>
      </div>
      ${ds}
    </div>`;
  }

  function componentNode(comp) {
    const cards = (comp.cards || []).map(cardNode).join("") ||
      '<div style="font-size:11px;color:#cbd5e1;padding-left:14px;">kart yok</div>';
    return `<div style="padding:5px 0 5px 14px;border-left:2px solid #d1fae5;margin-left:6px;">
      <div style="font-size:13px;font-weight:600;color:#059669;">
        <i class="fas fa-puzzle-piece" style="font-size:10px;margin-right:5px;"></i>${esc(comp.name)}
        <span style="font-family:monospace;font-size:10px;color:#6ee7b7;">${esc(comp.code)}</span>
      </div>
      ${cards}
    </div>`;
  }

  function moduleNode(mod) {
    const comps = (mod.components || []).map(componentNode).join("") ||
      '<div style="font-size:11px;color:#cbd5e1;padding-left:14px;">bileşen yok</div>';
    return `<details style="padding:6px 0 6px 12px;border-left:2px solid #e0e7ff;margin-left:4px;">
      <summary style="cursor:pointer;font-size:13.5px;font-weight:600;color:#4f46e5;">
        <i class="fas fa-cube" style="font-size:11px;margin-right:5px;"></i>${esc(mod.name)}
        <span style="font-family:monospace;font-size:10px;color:#a5b4fc;">${esc(mod.code)}</span>
        <span style="font-size:11px;color:#94a3b8;font-weight:400;">· ${(mod.components || []).length} bileşen</span>
      </summary>
      ${comps}
    </details>`;
  }

  function packageNode(pkg) {
    const mods = (pkg.modules || []).map(moduleNode).join("") ||
      '<div style="font-size:12px;color:#94a3b8;padding-left:14px;">modül yok</div>';
    return `<div class="mc-card">
      <details open>
        <summary style="cursor:pointer;list-style:none;padding:12px 16px;font-size:15px;font-weight:700;color:var(--text-default);">
          <i class="fas fa-box" style="color:#6366f1;margin-right:8px;"></i>${esc(pkg.name)}
          <span style="font-family:monospace;font-size:11px;color:#94a3b8;">${esc(pkg.code)}</span>
          <span style="font-size:12px;color:#94a3b8;font-weight:400;">· ${(pkg.modules || []).length} modül</span>
        </summary>
        <div style="padding:0 16px 14px;">${mods}</div>
      </details>
    </div>`;
  }

  async function load() {
    loadingEl.style.display = "block";
    try {
      const res = await fetch(TREE_URL, { credentials: "same-origin" });
      const d = await res.json();
      loadingEl.style.display = "none";
      if (!d.success) { showError(d.message || "Ağaç yüklenemedi."); return; }
      treeEl.innerHTML = (d.packages || []).map(packageNode).join("");
    } catch (e) {
      loadingEl.style.display = "none";
      showError("Sunucu hatası: " + e.message);
    }
  }

  async function discover() {
    discoverBtn.disabled = true;
    const orig = discoverBtn.innerHTML;
    discoverBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Taranıyor…';
    try {
      const res = await fetch(DISCOVER_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrf() },
        credentials: "same-origin",
      });
      const d = await res.json();
      if (d.success) { toast(d.message || "Keşif tamam."); load(); }
      else showError(d.message || "Keşif başarısız.");
    } catch (e) {
      showError("Sunucu hatası: " + e.message);
    } finally {
      discoverBtn.disabled = false;
      discoverBtn.innerHTML = orig;
    }
  }

  if (discoverBtn) discoverBtn.addEventListener("click", discover);
  load();
})();
