/**
 * admin.js — Admin modülü JS
 * Kural: alert()/confirm()/prompt() YASAK — yalnızca SweetAlert2
 * Kural: Jinja2 {{ }} bu dosyada YASAK — veri data-* ile gelir
 */

(function () {
  "use strict";

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
    Swal.fire({ toast: true, position: "top-end", icon: "success",
      title: msg, showConfirmButton: false, timer: 2500, timerProgressBar: true });
  }

  function showError(msg) {
    Swal.fire({ icon: "error", title: "Hata", text: msg, confirmButtonColor: "#dc2626" });
  }

  async function confirmAction(title, text, confirmText, color) {
    const r = await Swal.fire({
      title, text, icon: "warning", showCancelButton: true,
      confirmButtonColor: color || "#dc2626", cancelButtonColor: "#6b7280",
      confirmButtonText: confirmText || "Evet", cancelButtonText: "İptal",
    });
    return r.isConfirmed;
  }

  function escHtml(s) {
    if (!s) return "";
    return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
  }

  function reload() { setTimeout(() => location.reload(), 1200); }

  // ── Rol / Kurum seçenekleri yardımcısı ──────────────────────────────────
  function buildRoleOptions(selectedId) {
    const meta = document.getElementById("admin-meta");
    if (!meta) return "<option value=''>— Rol Seç —</option>";
    const ids   = JSON.parse(meta.dataset.roles    || "[]");
    const names = JSON.parse(meta.dataset.roleNames || "[]");
    return ids.map((id, i) =>
      `<option value="${id}" ${String(id) === String(selectedId) ? "selected" : ""}>${escHtml(names[i])}</option>`
    ).join("");
  }

  function buildTenantOptions(selectedId) {
    const meta = document.getElementById("admin-meta");
    if (!meta) return "";
    const ids   = JSON.parse(meta.dataset.tenants     || "[]");
    const names = JSON.parse(meta.dataset.tenantNames || "[]");
    if (!ids.length) return "";
    return `<div><label class="block text-xs text-gray-500 mb-1">Kurum</label>
      <select id="u-tenant" class="swal2-select">
        <option value="">— Kurum Seç —</option>
        ${ids.map((id, i) => `<option value="${id}" ${String(id) === String(selectedId) ? "selected" : ""}>${escHtml(names[i])}</option>`).join("")}
      </select></div>`;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // KULLANICI YÖNETİMİ
  // ═══════════════════════════════════════════════════════════════════════════
  const usersRoot = document.getElementById("admin-users-root");
  if (usersRoot) {
    const ADD_URL     = usersRoot.dataset.addUrl;
    const EDIT_BASE   = usersRoot.dataset.editBase;
    const TOGGLE_BASE = usersRoot.dataset.toggleBase;
    const BULK_URL    = usersRoot.dataset.bulkImportUrl;

    document.getElementById("btn-user-add")?.addEventListener("click", async () => {
      const tenantHtml = buildTenantOptions("");
      const { value: vals } = await Swal.fire({
        title: "Yeni Kullanıcı Ekle", width: 560,
        html: `<div class="text-left space-y-3">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
            <div><label class="block text-xs text-gray-500 mb-1">Ad</label>
              <input id="u-fname" class="swal2-input" placeholder="Ad"></div>
            <div><label class="block text-xs text-gray-500 mb-1">Soyad</label>
              <input id="u-lname" class="swal2-input" placeholder="Soyad"></div>
          </div>
          <div><label class="block text-xs text-gray-500 mb-1">E-posta <span style="color:#dc2626">*</span></label>
            <input id="u-email" class="swal2-input" type="email" placeholder="ornek@kurum.com"></div>
          <div><label class="block text-xs text-gray-500 mb-1">Şifre</label>
            <input id="u-pass" class="swal2-input" type="password" placeholder="Boş = varsayılan atanır"></div>
          <div><label class="block text-xs text-gray-500 mb-1">Rol</label>
            <select id="u-role" class="swal2-select">${buildRoleOptions("")}</select></div>
          ${tenantHtml}
        </div>`,
        focusConfirm: false, showCancelButton: true,
        confirmButtonText: "Kaydet", cancelButtonText: "İptal", confirmButtonColor: "#4f46e5",
        preConfirm: () => {
          const email = document.getElementById("u-email").value.trim();
          if (!email) { Swal.showValidationMessage("E-posta zorunludur."); return false; }
          return {
            email,
            first_name: document.getElementById("u-fname").value.trim(),
            last_name:  document.getElementById("u-lname").value.trim(),
            password:   document.getElementById("u-pass").value || null,
            role_id:    document.getElementById("u-role").value || null,
            tenant_id:  document.getElementById("u-tenant")?.value || null,
          };
        },
      });
      if (!vals) return;
      try {
        const d = await postJson(ADD_URL, vals);
        if (d.success) { toastSuccess("Kullanıcı oluşturuldu."); reload(); }
        else showError(d.message || "Kayıt başarısız.");
      } catch (e) { showError("Sunucu hatası: " + e.message); }
    });

    document.getElementById("btn-bulk-import")?.addEventListener("click", async () => {
      const { value: file } = await Swal.fire({
        title: "Toplu Kullanıcı İçe Aktar",
        html: `<p style="font-size:12px;color:#64748b;margin-bottom:8px;">CSV formatı: email, first_name, last_name</p>
               <input id="bulk-file" type="file" accept=".csv" class="swal2-file">`,
        focusConfirm: false, showCancelButton: true,
        confirmButtonText: "İçe Aktar", cancelButtonText: "İptal", confirmButtonColor: "#4f46e5",
        preConfirm: () => {
          const f = document.getElementById("bulk-file").files[0];
          if (!f) { Swal.showValidationMessage("Dosya seçiniz."); return false; }
          return f;
        },
      });
      if (!file) return;
      const fd = new FormData();
      fd.append("file", file);
      try {
        const res = await fetch(BULK_URL, { method: "POST", headers: { "X-CSRFToken": getCsrf() }, body: fd });
        const d = await res.json();
        if (d.success) { toastSuccess(d.message); reload(); }
        else showError(d.message || "İçe aktarma başarısız.");
      } catch (e) { showError("Sunucu hatası: " + e.message); }
    });

    document.addEventListener("click", async (e) => {
      const btnEdit = e.target.closest(".btn-user-edit");
      if (btnEdit) {
        const { userId, firstName, lastName, jobTitle, department, roleId, email } = btnEdit.dataset;
        const { value: vals } = await Swal.fire({
          title: "Kullanıcı Düzenle", width: 520,
          html: `<div class="text-left space-y-3">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
              <div><label class="block text-xs text-gray-500 mb-1">Ad</label>
                <input id="ue-fname" class="swal2-input" value="${escHtml(firstName)}"></div>
              <div><label class="block text-xs text-gray-500 mb-1">Soyad</label>
                <input id="ue-lname" class="swal2-input" value="${escHtml(lastName)}"></div>
            </div>
            <div><label class="block text-xs text-gray-500 mb-1">E-posta</label>
              <input id="ue-email" class="swal2-input" type="email" value="${escHtml(email)}" readonly style="background:#f1f5f9;color:#64748b;"></div>
            <div><label class="block text-xs text-gray-500 mb-1">Unvan</label>
              <input id="ue-title" class="swal2-input" value="${escHtml(jobTitle)}"></div>
            <div><label class="block text-xs text-gray-500 mb-1">Departman</label>
              <input id="ue-dept" class="swal2-input" value="${escHtml(department)}"></div>
            <div><label class="block text-xs text-gray-500 mb-1">Rol</label>
              <select id="ue-role" class="swal2-select">${buildRoleOptions(roleId)}</select></div>
            <div><label class="block text-xs text-gray-500 mb-1">Yeni Şifre (boş = değişmez)</label>
              <input id="ue-pass" class="swal2-input" type="password" placeholder="Değiştirmek için girin"></div>
          </div>`,
          focusConfirm: false, showCancelButton: true,
          confirmButtonText: "Güncelle", cancelButtonText: "İptal", confirmButtonColor: "#4f46e5",
          preConfirm: () => ({
            first_name: document.getElementById("ue-fname").value.trim(),
            last_name:  document.getElementById("ue-lname").value.trim(),
            job_title:  document.getElementById("ue-title").value.trim() || null,
            department: document.getElementById("ue-dept").value.trim() || null,
            role_id:    document.getElementById("ue-role").value || null,
            password:   document.getElementById("ue-pass").value || null,
          }),
        });
        if (!vals) return;
        try {
          const d = await postJson(`${EDIT_BASE}${userId}`, vals);
          if (d.success) { toastSuccess("Kullanıcı güncellendi."); reload(); }
          else showError(d.message || "Güncelleme başarısız.");
        } catch (e) { showError("Sunucu hatası: " + e.message); }
        return;
      }

      const btnToggle = e.target.closest(".btn-user-toggle");
      if (btnToggle) {
        const isActive = btnToggle.dataset.active === "true";
        const ok = await confirmAction(
          isActive ? "Kullanıcı pasife alınsın mı?" : "Kullanıcı aktifleştirilsin mi?",
          `"${btnToggle.dataset.name}"`,
          isActive ? "Evet, pasife al" : "Evet, aktifleştir",
          isActive ? "#dc2626" : "#059669"
        );
        if (!ok) return;
        try {
          const d = await postJson(`${TOGGLE_BASE}${btnToggle.dataset.userId}`, {});
          if (d.success) { toastSuccess(d.message); reload(); }
          else showError(d.message || "İşlem başarısız.");
        } catch (e) { showError("Sunucu hatası: " + e.message); }
      }
    });

    const userSearch = document.getElementById("user-search");
    if (userSearch) {
      userSearch.addEventListener("input", function () {
        const q = this.value.toLowerCase().trim();
        document.querySelectorAll("#users-table tbody tr[data-search]").forEach(row => {
          row.style.display = !q || row.dataset.search.includes(q) ? "" : "none";
        });
      });
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // KURUM YÖNETİMİ
  // ═══════════════════════════════════════════════════════════════════════════
  const tenantsRoot = document.getElementById("admin-tenants-root");
  if (tenantsRoot) {
    const ADD_URL     = tenantsRoot.dataset.addUrl;
    const EDIT_BASE   = tenantsRoot.dataset.editBase;
    const TOGGLE_BASE = tenantsRoot.dataset.toggleBase;

    // ── Native modal — hem Ekle hem Düzenle ─────────────────────────────────
    const editModal = document.getElementById("tenant-edit-modal");
    let _editTenantId = null; // null = yeni ekleme modu

    function openTenantModal(data) {
      _editTenantId = data ? (data.tenantId || null) : null;
      const isEdit = !!_editTenantId;
      document.getElementById("edit-modal-heading").textContent = isEdit ? (data.name || "Kurum Düzenle") : "Yeni Kurum Ekle";
      document.getElementById("em-name").value     = (data && data.name)          || "";
      document.getElementById("em-short").value    = (data && data.shortName)     || "";
      document.getElementById("em-sector").value   = (data && data.sector)        || "";
      document.getElementById("em-activity").value = (data && data.activityArea)  || "";
      document.getElementById("em-email").value    = (data && data.contactEmail)  || "";
      document.getElementById("em-phone").value    = (data && data.phoneNumber)   || "";
      document.getElementById("em-web").value      = (data && data.websiteUrl)    || "";
      document.getElementById("em-emp").value      = (data && data.employeeCount) || "";
      document.getElementById("em-maxu").value     = (data && data.maxUserCount)  || "";
      document.getElementById("em-lic").value      = (data && data.licenseEndDate)|| "";
      document.getElementById("em-taxoff").value   = (data && data.taxOffice)     || "";
      document.getElementById("em-taxno").value    = (data && data.taxNumber)     || "";
      const pkgSel = document.getElementById("em-package");
      if (pkgSel) pkgSel.value = (data && data.packageId) || "";
      editModal.classList.add("open");
      document.getElementById("em-name").focus();
    }

    function closeTenantModal() {
      editModal.classList.remove("open");
      _editTenantId = null;
    }

    document.getElementById("btn-tenant-add")?.addEventListener("click", () => openTenantModal(null));

    if (editModal) {
      document.getElementById("btn-edit-modal-close")?.addEventListener("click", closeTenantModal);
      document.getElementById("btn-edit-modal-cancel")?.addEventListener("click", closeTenantModal);
      editModal.addEventListener("click", (e) => { if (e.target === editModal) closeTenantModal(); });

      document.getElementById("btn-edit-modal-save")?.addEventListener("click", async () => {
        const name = document.getElementById("em-name").value.trim();
        if (!name) { showError("Kurum adı zorunludur."); document.getElementById("em-name").focus(); return; }
        const payload = {
          name,
          short_name:       document.getElementById("em-short").value.trim()    || null,
          sector:           document.getElementById("em-sector").value.trim()   || null,
          activity_area:    document.getElementById("em-activity").value.trim() || null,
          contact_email:    document.getElementById("em-email").value.trim()    || null,
          phone_number:     document.getElementById("em-phone").value.trim()    || null,
          website_url:      document.getElementById("em-web").value.trim()      || null,
          employee_count:   document.getElementById("em-emp").value             || null,
          max_user_count:   document.getElementById("em-maxu").value            || null,
          license_end_date: document.getElementById("em-lic").value             || null,
          tax_office:       document.getElementById("em-taxoff").value.trim()   || null,
          tax_number:       document.getElementById("em-taxno").value.trim()    || null,
          package_id:       document.getElementById("em-package")?.value        || null,
        };
        const url = _editTenantId ? `${EDIT_BASE}${_editTenantId}` : ADD_URL;
        const msg = _editTenantId ? "Kurum güncellendi." : "Kurum oluşturuldu.";
        try {
          const d = await postJson(url, payload);
          if (d.success) { closeTenantModal(); toastSuccess(msg); reload(); }
          else showError(d.message || "İşlem başarısız.");
        } catch (e) { showError("Sunucu hatası: " + e.message); }
      });
    }

    // ── Detay modal ──────────────────────────────────────────────────────────
    const detailModal = document.getElementById("tenant-detail-modal");
    if (detailModal) {
      document.getElementById("btn-close-detail")?.addEventListener("click", () => {
        detailModal.classList.remove("open");
      });
      detailModal.addEventListener("click", (e) => {
        if (e.target === detailModal) detailModal.classList.remove("open");
      });
    }

    // ── Arşiv filtresi ───────────────────────────────────────────────────────
    let _showArchived = false;
    const btnToggleArchived = document.getElementById("btn-toggle-archived");
    function applyArchivedFilter() {
      document.querySelectorAll("#tenants-table tbody tr[data-archived]").forEach(row => {
        if (row.dataset.archived === "true") {
          row.style.display = _showArchived ? "" : "none";
        }
      });
      if (btnToggleArchived) {
        btnToggleArchived.innerHTML = _showArchived
          ? '<i class="fas fa-eye-slash"></i> Arşivlenenleri Gizle'
          : '<i class="fas fa-archive"></i> Arşivlenenleri Göster';
      }
    }
    applyArchivedFilter();
    btnToggleArchived?.addEventListener("click", () => {
      _showArchived = !_showArchived;
      applyArchivedFilter();
    });

    document.addEventListener("click", async (e) => {
      // Detay görüntüle
      const btnDetail = e.target.closest(".btn-tenant-detail");
      if (btnDetail && detailModal) {
        const row = btnDetail.closest("tr");
        const editBtn = row?.querySelector(".btn-tenant-edit");
        const d = editBtn ? editBtn.dataset : {};
        const name = d.name || "—";
        document.getElementById("detail-modal-title").textContent = name;
        document.getElementById("detail-modal-body").innerHTML = `
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
            <div><div style="font-size:11px;color:#94a3b8;margin-bottom:2px;">Kurum Adı</div><div style="font-weight:500;">${escHtml(d.name||"—")}</div></div>
            <div><div style="font-size:11px;color:#94a3b8;margin-bottom:2px;">Kısa Ad</div><div>${escHtml(d.shortName||"—")}</div></div>
            <div><div style="font-size:11px;color:#94a3b8;margin-bottom:2px;">Sektör</div><div>${escHtml(d.sector||"—")}</div></div>
            <div><div style="font-size:11px;color:#94a3b8;margin-bottom:2px;">Faaliyet Alanı</div><div>${escHtml(d.activityArea||"—")}</div></div>
            <div><div style="font-size:11px;color:#94a3b8;margin-bottom:2px;">Çalışan Sayısı</div><div>${escHtml(d.employeeCount||"—")}</div></div>
            <div><div style="font-size:11px;color:#94a3b8;margin-bottom:2px;">Maks. Kullanıcı</div><div>${escHtml(d.maxUserCount||"—")}</div></div>
            <div><div style="font-size:11px;color:#94a3b8;margin-bottom:2px;">E-posta</div><div>${escHtml(d.contactEmail||"—")}</div></div>
            <div><div style="font-size:11px;color:#94a3b8;margin-bottom:2px;">Telefon</div><div>${escHtml(d.phoneNumber||"—")}</div></div>
            <div><div style="font-size:11px;color:#94a3b8;margin-bottom:2px;">Web Adresi</div><div>${escHtml(d.websiteUrl||"—")}</div></div>
            <div><div style="font-size:11px;color:#94a3b8;margin-bottom:2px;">Vergi Dairesi</div><div>${escHtml(d.taxOffice||"—")}</div></div>
            <div><div style="font-size:11px;color:#94a3b8;margin-bottom:2px;">Vergi No</div><div>${escHtml(d.taxNumber||"—")}</div></div>
            <div><div style="font-size:11px;color:#94a3b8;margin-bottom:2px;">Lisans Bitiş</div><div>${escHtml(d.licenseEndDate||"—")}</div></div>
            <div><div style="font-size:11px;color:#94a3b8;margin-bottom:2px;">Abonelik Paketi</div><div>${escHtml(d.packageName||"—")}</div></div>
          </div>`;
        detailModal.classList.add("open");
        return;
      }

      // Kurum düzenle — native modal
      const btnEdit = e.target.closest(".btn-tenant-edit");
      if (btnEdit) {
        openTenantModal(btnEdit.dataset);
        return;
      }

      // Kurum toggle
      const btnToggle = e.target.closest(".btn-tenant-toggle");
      if (btnToggle) {
        const isActive = btnToggle.dataset.active === "true";
        const ok = await confirmAction(
          isActive ? "Kurum arşivlensin mi?" : "Kurum aktifleştirilsin mi?",
          `"${btnToggle.dataset.name}"`,
          isActive ? "Evet, arşivle" : "Evet, aktifleştir",
          isActive ? "#dc2626" : "#059669"
        );
        if (!ok) return;
        try {
          const d = await postJson(`${TOGGLE_BASE}${btnToggle.dataset.tenantId}`, {});
          if (d.success) { toastSuccess(d.message); reload(); }
          else showError(d.message || "İşlem başarısız.");
        } catch (e) { showError("Sunucu hatası: " + e.message); }
      }
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // PAKET & MODÜL YÖNETİMİ
  // ═══════════════════════════════════════════════════════════════════════════
  const pkgRoot = document.getElementById("admin-packages-root");
  if (pkgRoot) {
    const SYNC_URL        = pkgRoot.dataset.syncUrl;
    const PKG_ADD_URL     = pkgRoot.dataset.pkgAddUrl;
    const PKG_EDIT_BASE   = pkgRoot.dataset.pkgEditBase;
    const PKG_TOGGLE_BASE = pkgRoot.dataset.pkgToggleBase;
    const MOD_ADD_URL     = pkgRoot.dataset.modAddUrl;
    const MOD_TOGGLE_BASE = pkgRoot.dataset.modToggleBase;

    document.getElementById("btn-sync-components")?.addEventListener("click", async () => {
      const ok = await confirmAction("Bileşenler senkronize edilsin mi?",
        "Tüm Flask route'ları taranacak.", "Evet, senkronize et", "#f59e0b");
      if (!ok) return;
      try {
        const d = await postJson(SYNC_URL, {});
        if (d.success) toastSuccess(d.message);
        else showError(d.message || "Senkronizasyon başarısız.");
      } catch (e) { showError("Sunucu hatası: " + e.message); }
    });

    document.getElementById("btn-pkg-add")?.addEventListener("click", async () => {
      const { value: vals } = await Swal.fire({
        title: "Yeni Paket Ekle",
        html: `<div class="text-left space-y-3">
          <div><label class="block text-xs text-gray-500 mb-1">Paket Adı <span style="color:#dc2626">*</span></label>
            <input id="pkg-name" class="swal2-input" placeholder="Örn: Başlangıç Paketi"></div>
          <div><label class="block text-xs text-gray-500 mb-1">Kod <span style="color:#dc2626">*</span></label>
            <input id="pkg-code" class="swal2-input" placeholder="Örn: starter"></div>
          <div><label class="block text-xs text-gray-500 mb-1">Açıklama</label>
            <input id="pkg-desc" class="swal2-input" placeholder="Kısa açıklama"></div>
        </div>`,
        focusConfirm: false, showCancelButton: true,
        confirmButtonText: "Kaydet", cancelButtonText: "İptal", confirmButtonColor: "#4f46e5",
        preConfirm: () => {
          const name = document.getElementById("pkg-name").value.trim();
          const code = document.getElementById("pkg-code").value.trim();
          if (!name || !code) { Swal.showValidationMessage("Ad ve kod zorunludur."); return false; }
          return { name, code, description: document.getElementById("pkg-desc").value.trim() || null };
        },
      });
      if (!vals) return;
      try {
        const d = await postJson(PKG_ADD_URL, vals);
        if (d.success) { toastSuccess("Paket oluşturuldu."); reload(); }
        else showError(d.message || "Kayıt başarısız.");
      } catch (e) { showError("Sunucu hatası: " + e.message); }
    });

    document.getElementById("btn-mod-add")?.addEventListener("click", async () => {
      const { value: vals } = await Swal.fire({
        title: "Yeni Modül Ekle",
        html: `<div class="text-left space-y-3">
          <div><label class="block text-xs text-gray-500 mb-1">Modül Adı <span style="color:#dc2626">*</span></label>
            <input id="mod-name" class="swal2-input" placeholder="Örn: Süreç Yönetimi"></div>
          <div><label class="block text-xs text-gray-500 mb-1">Kod <span style="color:#dc2626">*</span></label>
            <input id="mod-code" class="swal2-input" placeholder="Örn: process_management"></div>
          <div><label class="block text-xs text-gray-500 mb-1">Açıklama</label>
            <input id="mod-desc" class="swal2-input" placeholder="Kısa açıklama"></div>
        </div>`,
        focusConfirm: false, showCancelButton: true,
        confirmButtonText: "Kaydet", cancelButtonText: "İptal", confirmButtonColor: "#4f46e5",
        preConfirm: () => {
          const name = document.getElementById("mod-name").value.trim();
          const code = document.getElementById("mod-code").value.trim();
          if (!name || !code) { Swal.showValidationMessage("Ad ve kod zorunludur."); return false; }
          return { name, code, description: document.getElementById("mod-desc").value.trim() || null };
        },
      });
      if (!vals) return;
      try {
        const d = await postJson(MOD_ADD_URL, vals);
        if (d.success) { toastSuccess("Modül oluşturuldu."); reload(); }
        else showError(d.message || "Kayıt başarısız.");
      } catch (e) { showError("Sunucu hatası: " + e.message); }
    });

    document.addEventListener("click", async (e) => {
      const btnPkgEdit = e.target.closest(".btn-pkg-edit");
      if (btnPkgEdit) {
        const { pkgId, name: curName, description: curDesc } = btnPkgEdit.dataset;
        const { value: vals } = await Swal.fire({
          title: "Paket Düzenle",
          html: `<div class="text-left space-y-3">
            <div><label class="block text-xs text-gray-500 mb-1">Paket Adı <span style="color:#dc2626">*</span></label>
              <input id="pke-name" class="swal2-input" value="${escHtml(curName)}"></div>
            <div><label class="block text-xs text-gray-500 mb-1">Açıklama</label>
              <input id="pke-desc" class="swal2-input" value="${escHtml(curDesc)}"></div>
          </div>`,
          focusConfirm: false, showCancelButton: true,
          confirmButtonText: "Güncelle", cancelButtonText: "İptal", confirmButtonColor: "#4f46e5",
          preConfirm: () => {
            const name = document.getElementById("pke-name").value.trim();
            if (!name) { Swal.showValidationMessage("Paket adı zorunludur."); return false; }
            return { name, description: document.getElementById("pke-desc").value.trim() || null };
          },
        });
        if (!vals) return;
        try {
          const d = await postJson(`${PKG_EDIT_BASE}${pkgId}`, vals);
          if (d.success) { toastSuccess("Paket güncellendi."); reload(); }
          else showError(d.message || "Güncelleme başarısız.");
        } catch (e) { showError("Sunucu hatası: " + e.message); }
        return;
      }

      const btnPkgToggle = e.target.closest(".btn-pkg-toggle");
      if (btnPkgToggle) {
        const isActive = btnPkgToggle.dataset.active === "true";
        const ok = await confirmAction(
          isActive ? "Paket pasife alınsın mı?" : "Paket aktifleştirilsin mi?",
          `"${btnPkgToggle.dataset.name}"`,
          isActive ? "Evet, pasife al" : "Evet, aktifleştir",
          isActive ? "#dc2626" : "#059669"
        );
        if (!ok) return;
        try {
          const d = await postJson(`${PKG_TOGGLE_BASE}${btnPkgToggle.dataset.pkgId}`, {});
          if (d.success) { toastSuccess(d.message); reload(); }
          else showError(d.message || "İşlem başarısız.");
        } catch (e) { showError("Sunucu hatası: " + e.message); }
        return;
      }

      const btnModToggle = e.target.closest(".btn-mod-toggle");
      if (btnModToggle) {
        const isActive = btnModToggle.dataset.active === "true";
        const ok = await confirmAction(
          isActive ? "Modül pasife alınsın mı?" : "Modül aktifleştirilsin mi?",
          `"${btnModToggle.dataset.name}"`,
          isActive ? "Evet, pasife al" : "Evet, aktifleştir",
          isActive ? "#dc2626" : "#059669"
        );
        if (!ok) return;
        try {
          const d = await postJson(`${MOD_TOGGLE_BASE}${btnModToggle.dataset.modId}`, {});
          if (d.success) { toastSuccess(d.message); reload(); }
          else showError(d.message || "İşlem başarısız.");
        } catch (e) { showError("Sunucu hatası: " + e.message); }
      }
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // BİLDİRİM MERKEZİ YÖNETİMİ
  // ═══════════════════════════════════════════════════════════════════════════
  const notifRoot = document.getElementById("admin-notifications-root");
  if (notifRoot) {
    const BROADCAST_URL = notifRoot.dataset.broadcastUrl;
    const DELETE_BASE   = notifRoot.dataset.deleteBase;

    document.getElementById("btn-broadcast")?.addEventListener("click", async () => {
      const meta        = document.getElementById("notif-meta");
      const tenantIds   = JSON.parse(meta?.dataset.tenants     || "[]");
      const tenantNames = JSON.parse(meta?.dataset.tenantNames || "[]");

      let tenantHtml = "";
      if (tenantIds.length) {
        tenantHtml = `<div><label class="block text-xs text-gray-500 mb-1">Hedef Kurum (boş = tümü)</label>
          <select id="bc-tenant" class="swal2-select">
            <option value="">— Tüm Kurumlar —</option>
            ${tenantIds.map((id, i) => `<option value="${id}">${escHtml(tenantNames[i])}</option>`).join("")}
          </select></div>`;
      }

      const { value: vals } = await Swal.fire({
        title: "Toplu Bildirim Gönder", width: 560,
        html: `<div class="text-left space-y-3">
          <div><label class="block text-xs text-gray-500 mb-1">Başlık <span style="color:#dc2626">*</span></label>
            <input id="bc-title" class="swal2-input" placeholder="Bildirim başlığı"></div>
          <div><label class="block text-xs text-gray-500 mb-1">Mesaj <span style="color:#dc2626">*</span></label>
            <textarea id="bc-message" class="swal2-textarea" placeholder="Bildirim mesajı" rows="3"></textarea></div>
          <div><label class="block text-xs text-gray-500 mb-1">Bağlantı (opsiyonel)</label>
            <input id="bc-link" class="swal2-input" placeholder="/micro/..."></div>
          ${tenantHtml}
        </div>`,
        focusConfirm: false, showCancelButton: true,
        confirmButtonText: "Gönder", cancelButtonText: "İptal", confirmButtonColor: "#4f46e5",
        preConfirm: () => {
          const title   = document.getElementById("bc-title").value.trim();
          const message = document.getElementById("bc-message").value.trim();
          if (!title || !message) { Swal.showValidationMessage("Başlık ve mesaj zorunludur."); return false; }
          return {
            title, message,
            link:      document.getElementById("bc-link")?.value.trim() || null,
            tenant_id: document.getElementById("bc-tenant")?.value || null,
            type:      "system_broadcast",
          };
        },
      });
      if (!vals) return;
      try {
        const d = await postJson(BROADCAST_URL, vals);
        if (d.success) { toastSuccess(d.message); reload(); }
        else showError(d.message || "Gönderim başarısız.");
      } catch (e) { showError("Sunucu hatası: " + e.message); }
    });

    document.addEventListener("click", async (e) => {
      const btnDel = e.target.closest(".btn-notif-delete");
      if (!btnDel) return;
      const ok = await confirmAction(
        "Bildirim silinsin mi?",
        `"${btnDel.dataset.title}" bildirimi okundu olarak işaretlenecek.`,
        "Evet, sil", "#dc2626"
      );
      if (!ok) return;
      try {
        const d = await postJson(`${DELETE_BASE}${btnDel.dataset.notifId}`, {});
        if (d.success) { toastSuccess("Bildirim silindi."); reload(); }
        else showError(d.message || "İşlem başarısız.");
      } catch (e) { showError("Sunucu hatası: " + e.message); }
    });

    function applyNotifFilters() {
      const q      = (document.getElementById("notif-search")?.value || "").toLowerCase().trim();
      const type   = document.getElementById("notif-filter-type")?.value || "";
      const status = document.getElementById("notif-filter-status")?.value || "";
      document.querySelectorAll("#notifications-table tbody tr[data-search]").forEach(row => {
        const matchQ      = !q      || row.dataset.search.includes(q);
        const matchType   = !type   || row.dataset.type === type;
        const matchStatus = !status || row.dataset.status === status;
        row.style.display = (matchQ && matchType && matchStatus) ? "" : "none";
      });
    }
    document.getElementById("notif-search")?.addEventListener("input", applyNotifFilters);
    document.getElementById("notif-filter-type")?.addEventListener("change", applyNotifFilters);
    document.getElementById("notif-filter-status")?.addEventListener("change", applyNotifFilters);
  }

})();
