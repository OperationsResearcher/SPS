/**
 * Kurum Yonetimi - Admin Tenants
 * Modal acma/kapama, form, silme onayi (SweetAlert2)
 */
(function () {
    "use strict";

    var modalEl = document.getElementById("tenantModal");
    var formEl = document.getElementById("tenantForm");
    var addUrl = document.getElementById("tenantManagementData")?.dataset?.addUrl || "/admin/tenants/add";
    var editUrlTemplate = document.getElementById("tenantManagementData")?.dataset?.editUrl || "/admin/tenants/edit/0";
    var archiveUrlTemplate = document.getElementById("tenantManagementData")?.dataset?.archiveUrl || "/admin/tenants/archive/0";

    function getVal(id) {
        var el = document.getElementById(id);
        return el ? el.value.trim() : "";
    }

    function setVal(id, val) {
        var el = document.getElementById(id);
        if (el) el.value = val == null ? "" : val;
    }

    function setValByName(name, val) {
        var el = formEl?.querySelector('[name="' + name + '"]');
        if (el) el.value = val == null ? "" : val;
    }

    function openAddModal() {
        if (!modalEl || !formEl) return;
        document.getElementById("tenantModalLabel").textContent = "Yeni Kurum Ekle";
        formEl.action = addUrl;
        setVal("tenant_id", "");
        setVal("short_name", "");
        setVal("name", "");
        setValByName("activity_area", "");
        setValByName("sector", "");
        setValByName("employee_count", "");
        setValByName("contact_email", "");
        setValByName("phone_number", "");
        setValByName("website_url", "");
        setValByName("tax_office", "");
        setValByName("tax_number", "");
        setVal("package_id", "");
        setValByName("max_user_count", "5");
        setValByName("license_end_date", "");
        new bootstrap.Modal(modalEl).show();
    }

    function openEditModal(tenant) {
        if (!modalEl || !formEl) return;
        document.getElementById("tenantModalLabel").textContent = "Kurum Düzenle";
        formEl.action = editUrlTemplate.replace(/0$/, tenant.id);
        setVal("tenant_id", tenant.id);
        setVal("short_name", tenant.short_name || "");
        setVal("name", tenant.name || "");
        setValByName("activity_area", tenant.activity_area || "");
        setValByName("sector", tenant.sector || "");
        setValByName("employee_count", tenant.employee_count || "");
        setValByName("contact_email", tenant.contact_email || "");
        setValByName("phone_number", tenant.phone_number || "");
        setValByName("website_url", tenant.website_url || "");
        setValByName("tax_office", tenant.tax_office || "");
        setValByName("tax_number", tenant.tax_number || "");
        setVal("package_id", tenant.package_id || "");
        setValByName("max_user_count", tenant.max_user_count || "5");
        setValByName("license_end_date", tenant.license_end_date || "");
        new bootstrap.Modal(modalEl).show();
    }

    function confirmArchive(id, name) {
        Swal.fire({
            title: "Kurumu Arşivle",
            text: '"' + name + '" kurumunu arşivlemek (pasif yapmak) istediğinize emin misiniz?',
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#dc3545",
            cancelButtonColor: "#6c757d",
            confirmButtonText: "Evet, Arşivle",
            cancelButtonText: "Vazgeç"
        }).then(function (result) {
            if (result.isConfirmed) submitArchive(id);
        });
    }

    function submitArchive(id) {
        var form = document.createElement("form");
        form.method = "POST";
        form.action = archiveUrlTemplate.replace(/0$/, id);
        var meta = document.querySelector('meta[name="csrf-token"]');
        if (meta && meta.getAttribute("content")) {
            var input = document.createElement("input");
            input.type = "hidden";
            input.name = "csrf_token";
            input.value = meta.getAttribute("content");
            form.appendChild(input);
        }
        document.body.appendChild(form);
        form.submit();
    }

    document.addEventListener("DOMContentLoaded", function () {
        var btnAdd = document.getElementById("btnNewTenant");
        if (btnAdd) {
            btnAdd.addEventListener("click", openAddModal);
        }

        document.querySelectorAll("[data-tenant-edit]").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var data = btn.dataset;
                openEditModal({
                    id: data.tenantId,
                    name: data.tenantName || "",
                    short_name: data.tenantShortName || "",
                    activity_area: data.tenantActivityArea || "",
                    sector: data.tenantSector || "",
                    employee_count: data.tenantEmployeeCount || "",
                    contact_email: data.tenantContactEmail || "",
                    phone_number: data.tenantPhoneNumber || "",
                    website_url: data.tenantWebsiteUrl || "",
                    tax_office: data.tenantTaxOffice || "",
                    tax_number: data.tenantTaxNumber || "",
                    package_id: data.tenantPackageId || "",
                    max_user_count: data.tenantMaxUserCount || "5",
                    license_end_date: data.tenantLicenseEndDate || "",
                });
            });
        });

        document.querySelectorAll("[data-tenant-archive]").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var id = btn.dataset.tenantId;
                var name = btn.dataset.tenantName || "Bu kurum";
                confirmArchive(id, name);
            });
        });

        var formSubmit = document.getElementById("tenantFormSubmit");
        if (formSubmit && formEl) {
            formSubmit.addEventListener("click", function () {
                if (!getVal("short_name") && !getVal("name")) {
                    Swal.fire({ icon: "warning", title: "Uyarı", text: "Kısa ad veya ticari ünvan zorunludur." });
                    return;
                }
                formEl.submit();
            });
        }
    });

    window.openTenantAddModal = openAddModal;
    window.openTenantEditModal = openEditModal;
})();
