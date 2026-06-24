/**
 * admin_hierarchy.js — SaaS 4-katman ağacı + KART/VERİ düzenleme.
 *
 * Ağaç (paket→modül→bileşen→kart→veri). Düzenleme: kart ad/bileşen/sıra,
 * veri kaynağı required_component (hangi pakete tabi) inline dropdown + ekle/sil.
 * "Kartları Keşfet" → template data-card-* tarar.
 * Kural: alert/confirm YASAK → SweetAlert2. Jinja {{ }} YASAK → data-*.
 */
(function () {
  "use strict";

  const root = document.getElementById("hierarchy-root");
  if (!root) return;
  const TREE_URL = root.dataset.treeUrl;
  const DISCOVER_URL = root.dataset.discoverUrl;
  const COMPONENTS_URL = "/admin/api/components/list";

  const loadingEl = document.getElementById("hierarchy-loading");
  const treeEl = document.getElementById("hierarchy-tree");
  const discoverBtn = document.getElementById("btn-discover");

  let COMPONENTS = []; // {code, name}

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
      showConfirmButton: false, timer: 1800, timerProgressBar: true });
  }
  async function postJson(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrf() },
      credentials: "same-origin", body: JSON.stringify(body || {}),
    });
    return res.json();
  }

  function compOptions(selected) {
    return [`<option value="">${t("— kısıtsız —")}</option>`]
      .concat(COMPONENTS.map((c) =>
        `<option value="${esc(c.code)}" ${c.code === selected ? "selected" : ""}>${esc(c.name)}</option>`))
      .join("");
  }

  function dataSourceRow(d) {
    // required_component inline dropdown (değişince çapraz-paket veri kuralı değişir)
    return `<div style="display:flex;align-items:center;gap:6px;font-size:12px;padding:3px 0 3px 16px;">
      <i class="fas fa-database" style="color:#cbd5e1;font-size:9px;"></i>
      <span style="font-family:monospace;color:var(--text-default);min-width:130px;">${esc(d.data_key)}</span>
      ${d.label ? `<span style="color:#94a3b8;">${esc(d.label)}</span>` : ""}
      <span style="color:#64748b;font-size:11px;">${t("tabi:")}</span>
      <select class="ds-required" data-ds-id="${d.id}" style="font-size:11px;padding:2px 4px;max-width:200px;">
        ${compOptions(d.required_component_code)}
      </select>
      <button type="button" class="ds-del" data-ds-id="${d.id}" style="background:none;border:none;color:#f87171;cursor:pointer;" title="${t("Sil")}"><i class="fas fa-times"></i></button>
    </div>`;
  }

  function cardNode(card) {
    const ds = (card.data_sources || []).map(dataSourceRow).join("") ||
      `<div style="font-size:11px;color:#cbd5e1;padding-left:16px;">${t("veri kaynağı yok")}</div>`;
    return `<div style="padding:4px 0 8px 14px;border-left:2px solid #ede9fe;margin-left:6px;" data-card-id="${card.id}">
      <div style="display:flex;align-items:center;gap:6px;font-size:12.5px;font-weight:600;color:#7c3aed;">
        <i class="fas fa-table-cells-large" style="font-size:10px;"></i>${esc(card.name)}
        <span style="font-family:monospace;font-size:10px;color:#a78bfa;font-weight:400;">${esc(card.code)}</span>
        <button type="button" class="card-edit" data-card-id="${card.id}" data-card-name="${esc(card.name)}" data-card-comp=""
          style="background:none;border:none;color:#94a3b8;cursor:pointer;font-size:11px;" title="${t("Kartı düzenle")}"><i class="fas fa-pen"></i></button>
        <button type="button" class="ds-add" data-card-id="${card.id}"
          style="background:none;border:none;color:#7c3aed;cursor:pointer;font-size:11px;" title="${t("Veri ekle")}"><i class="fas fa-plus"></i> ${t("veri")}</button>
      </div>
      ${ds}
    </div>`;
  }

  function componentNode(comp) {
    const cards = (comp.cards || []).map(cardNode).join("") ||
      `<div style="font-size:11px;color:#cbd5e1;padding-left:14px;">${t("kart yok")}</div>`;
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
      `<div style="font-size:11px;color:#cbd5e1;padding-left:14px;">${t("bileşen yok")}</div>`;
    return `<details style="padding:6px 0 6px 12px;border-left:2px solid #e0e7ff;margin-left:4px;">
      <summary style="cursor:pointer;font-size:13.5px;font-weight:600;color:#4f46e5;">
        <i class="fas fa-cube" style="font-size:11px;margin-right:5px;"></i>${esc(mod.name)}
        <span style="font-family:monospace;font-size:10px;color:#a5b4fc;">${esc(mod.code)}</span>
        <span style="font-size:11px;color:#94a3b8;font-weight:400;">· ${(mod.components || []).length} ${t("bileşen")}</span>
      </summary>
      ${comps}
    </details>`;
  }

  function packageNode(pkg) {
    const mods = (pkg.modules || []).map(moduleNode).join("") ||
      `<div style="font-size:12px;color:#94a3b8;padding-left:14px;">${t("modül yok")}</div>`;
    return `<div class="mc-card">
      <details open>
        <summary style="cursor:pointer;padding:12px 16px;font-size:15px;font-weight:700;color:var(--text-default);">
          <i class="fas fa-box" style="color:#6366f1;margin-right:8px;"></i>${esc(pkg.name)}
          <span style="font-family:monospace;font-size:11px;color:#94a3b8;">${esc(pkg.code)}</span>
          <span style="font-size:12px;color:#94a3b8;font-weight:400;">· ${(pkg.modules || []).length} ${t("modül")}</span>
        </summary>
        <div style="padding:0 16px 14px;">${mods}</div>
      </details>
    </div>`;
  }

  async function load() {
    loadingEl.style.display = "block";
    try {
      if (!COMPONENTS.length) {
        const cr = await fetch(COMPONENTS_URL, { credentials: "same-origin" });
        const cd = await cr.json();
        if (cd.success) COMPONENTS = cd.components || [];
      }
      const res = await fetch(TREE_URL, { credentials: "same-origin" });
      const d = await res.json();
      loadingEl.style.display = "none";
      if (!d.success) { showError(d.message || t("Ağaç yüklenemedi.")); return; }
      treeEl.innerHTML = (d.packages || []).map(packageNode).join("");
    } catch (e) {
      loadingEl.style.display = "none";
      showError(t("Sunucu hatası: ") + e.message);
    }
  }

  async function discover() {
    discoverBtn.disabled = true;
    const orig = discoverBtn.innerHTML;
    discoverBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${t("Taranıyor…")}`;
    try {
      const d = await postJson(DISCOVER_URL, {});
      if (d.success) { toast(d.message || t("Keşif tamam.")); load(); }
      else showError(d.message || t("Keşif başarısız."));
    } catch (e) { showError(t("Sunucu hatası: ") + e.message); }
    finally { discoverBtn.disabled = false; discoverBtn.innerHTML = orig; }
  }

  // ── Düzenleme olayları ───────────────────────────────────────────────────
  // Veri kaynağı required_component değişti (inline dropdown)
  treeEl.addEventListener("change", async (e) => {
    const sel = e.target.closest(".ds-required");
    if (!sel) return;
    const d = await postJson(`/admin/api/data-sources/${sel.dataset.dsId}`,
      { required_component_code: sel.value });
    if (d.success) toast(t("Veri eşlemesi güncellendi."));
    else { showError(d.message || t("Güncellenemedi.")); load(); }
  });

  treeEl.addEventListener("click", async (e) => {
    // Veri kaynağı sil
    const del = e.target.closest(".ds-del");
    if (del) {
      const r = await Swal.fire({ title: t("Veri kaynağı silinsin mi?"), icon: "warning",
        showCancelButton: true, confirmButtonColor: "#dc2626", confirmButtonText: t("Sil"), cancelButtonText: t("İptal") });
      if (!r.isConfirmed) return;
      const d = await postJson(`/admin/api/data-sources/${del.dataset.dsId}/delete`, {});
      if (d.success) { toast(t("Silindi.")); load(); } else showError(d.message);
      return;
    }
    // Karta veri ekle
    const add = e.target.closest(".ds-add");
    if (add) {
      const { value: vals } = await Swal.fire({
        title: t("Veri kaynağı ekle"), width: 460, focusConfirm: false, showCancelButton: true,
        confirmButtonText: t("Ekle"), cancelButtonText: t("İptal"), confirmButtonColor: "#7c3aed",
        html: `<div style="text-align:left;font-size:13px;display:flex;flex-direction:column;gap:8px;">
          <div><label style="font-size:12px;color:#64748b;">${t("Veri anahtarı *")}</label>
            <input id="ds-key" class="swal2-input" style="margin:2px 0;" placeholder="${t("örn: pgv_kapsami")}"></div>
          <div><label style="font-size:12px;color:#64748b;">${t("Etiket")}</label>
            <input id="ds-label" class="swal2-input" style="margin:2px 0;"></div>
          <div><label style="font-size:12px;color:#64748b;">${t("Tabi olduğu bileşen (paket)")}</label>
            <select id="ds-req" class="swal2-select" style="width:100%;margin:2px 0;">${compOptions("")}</select></div>
        </div>`,
        preConfirm: () => {
          const k = document.getElementById("ds-key").value.trim();
          if (!k) { Swal.showValidationMessage(t("Veri anahtarı zorunlu.")); return false; }
          return { data_key: k, label: document.getElementById("ds-label").value.trim(),
                   required_component_code: document.getElementById("ds-req").value };
        },
      });
      if (!vals) return;
      const d = await postJson(`/admin/api/cards/${add.dataset.cardId}/data-sources`, vals);
      if (d.success) { toast(t("Eklendi.")); load(); } else showError(d.message);
      return;
    }
    // Kart düzenle (ad + bileşen + sıra)
    const ce = e.target.closest(".card-edit");
    if (ce) {
      const cid = ce.dataset.cardId;
      const { value: vals } = await Swal.fire({
        title: t("Kartı düzenle"), width: 460, focusConfirm: false, showCancelButton: true,
        confirmButtonText: t("Kaydet"), cancelButtonText: t("İptal"), confirmButtonColor: "#7c3aed",
        html: `<div style="text-align:left;font-size:13px;display:flex;flex-direction:column;gap:8px;">
          <div><label style="font-size:12px;color:#64748b;">${t("Kart adı")}</label>
            <input id="c-name" class="swal2-input" style="margin:2px 0;" value="${esc(ce.dataset.cardName)}"></div>
          <div><label style="font-size:12px;color:#64748b;">${t("Bağlı bileşen")}</label>
            <select id="c-comp" class="swal2-select" style="width:100%;margin:2px 0;">${compOptions("")}</select></div>
          <div><label style="font-size:12px;color:#64748b;">${t("Sıra (yer)")}</label>
            <input id="c-sira" type="number" class="swal2-input" style="margin:2px 0;" placeholder="0"></div>
        </div>`,
        preConfirm: () => ({
          name: document.getElementById("c-name").value.trim(),
          component_code: document.getElementById("c-comp").value,
          sira: document.getElementById("c-sira").value || 0,
        }),
      });
      if (!vals) return;
      const d = await postJson(`/admin/api/cards/${cid}`, vals);
      if (d.success) { toast(t("Kart güncellendi.")); load(); } else showError(d.message);
    }
  });

  if (discoverBtn) discoverBtn.addEventListener("click", discover);
  load();
})();
