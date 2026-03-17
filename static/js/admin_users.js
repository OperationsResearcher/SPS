/**
 * Kullanici Yonetimi - Admin Users
 * Modal acma/kapama, form, durum degistirme onayi (SweetAlert2)
 */
(function () {
    "use strict";

    var modalEl = document.getElementById("userModal");
    var formEl = document.getElementById("userForm");
    var dataEl = document.getElementById("userManagementData");
    var addUrl = dataEl?.dataset?.addUrl || "/admin/users/add";
    var editUrlTemplate = dataEl?.dataset?.editUrl || "/admin/users/edit/0";
    var toggleUrlTemplate = dataEl?.dataset?.toggleUrl || "/admin/users/toggle/0";

    function getVal(id) {
        var el = document.getElementById(id);
        return el ? el.value.trim() : "";
    }

    function setVal(id, val) {
        var el = document.getElementById(id);
        if (el) el.value = val == null ? "" : val;
    }

    function openAddModal() {
        if (!modalEl || !formEl) return;
        document.getElementById("userModalLabel").textContent = "Yeni Kullanıcı Ekle";
        formEl.action = addUrl;
        formEl.querySelector("input[name='password']")?.removeAttribute("data-optional");
        var hint = document.getElementById("userPasswordHint");
        var req = document.getElementById("userPasswordRequired");
        if (hint) hint.style.display = "none";
        if (req) req.style.display = "";
        setVal("first_name", "");
        setVal("last_name", "");
        setVal("email", "");
        setVal("phone_number", "");
        setVal("job_title", "");
        setVal("department", "");
        setVal("profile_picture", "");
        setVal("tenant_id", "");
        setVal("role_id", "");
        setVal("password", "");
        new bootstrap.Modal(modalEl).show();
    }

    function openEditModal(user) {
        if (!modalEl || !formEl) return;
        document.getElementById("userModalLabel").textContent = "Kullanıcı Düzenle";
        formEl.action = editUrlTemplate.replace(/0$/, user.id);
        formEl.querySelector("input[name='password']")?.setAttribute("data-optional", "1");
        var hint = document.getElementById("userPasswordHint");
        var req = document.getElementById("userPasswordRequired");
        if (hint) hint.style.display = "";
        if (req) req.style.display = "none";
        setVal("first_name", user.first_name || "");
        setVal("last_name", user.last_name || "");
        setVal("email", user.email || "");
        setVal("phone_number", user.phone_number || "");
        setVal("job_title", user.job_title || "");
        setVal("department", user.department || "");
        setVal("profile_picture", user.profile_picture || "");
        setVal("tenant_id", user.tenant_id || "");
        setVal("role_id", user.role_id || "");
        setVal("password", "");
        new bootstrap.Modal(modalEl).show();
    }

    function confirmToggle(id, email, isActivating) {
        var msg = isActivating
            ? '"' + email + '" kullanıcısını tekrar aktif etmek istediğinize emin misiniz?'
            : '"' + email + '" kullanıcısını devre dışı bırakmak istediğinize emin misiniz?';
        Swal.fire({
            title: isActivating ? "Aktif Et" : "Devre Dışı Bırak",
            text: msg,
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: isActivating ? "#198754" : "#dc3545",
            cancelButtonColor: "#6c757d",
            confirmButtonText: "Evet",
            cancelButtonText: "Vazgeç"
        }).then(function (result) {
            if (result.isConfirmed) submitToggle(id);
        });
    }

    function submitToggle(id) {
        var form = document.createElement("form");
        form.method = "POST";
        form.action = toggleUrlTemplate.replace(/0$/, id);
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
        var btnAdd = document.getElementById("btnYeniKullanici");
        if (btnAdd) {
            btnAdd.addEventListener("click", openAddModal);
        }

        document.querySelectorAll(".btn-user-edit").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var d = btn.dataset;
                openEditModal({
                    id: d.userId,
                    email: d.userEmail || "",
                    first_name: d.userFirstName || "",
                    last_name: d.userLastName || "",
                    phone_number: d.userPhoneNumber || "",
                    job_title: d.userJobTitle || "",
                    department: d.userDepartment || "",
                    profile_picture: d.userProfilePicture || "",
                    tenant_id: d.userTenantId || "",
                    role_id: d.userRoleId || "",
                });
            });
        });

        document.querySelectorAll(".btn-user-toggle").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var id = btn.dataset.userId;
                var email = btn.dataset.userEmail || "Bu kullanici";
                var isActivating = btn.classList.contains("btn-outline-success");
                confirmToggle(id, email, isActivating);
            });
        });

        var formSubmit = document.getElementById("userFormSubmit");
        if (formSubmit && formEl) {
            formSubmit.addEventListener("click", function () {
                if (!getVal("email")) {
                    Swal.fire({ icon: "warning", title: "Uyarı", text: "E-posta zorunludur." });
                    return;
                }
                var pwdInput = formEl.querySelector("input[name='password']");
                var isAdd = formEl.action.indexOf("/add") !== -1;
                if (isAdd) {
                    var pwd = getVal("password");
                    if (!pwd || pwd.length < 6) {
                        Swal.fire({ icon: "warning", title: "Uyarı", text: "Şifre en az 6 karakter olmalıdır." });
                        return;
                    }
                }
                formEl.submit();
            });
        }

        var btnSubmitBulkImport = document.getElementById("btnSubmitBulkImport");
        if (btnSubmitBulkImport) {
            btnSubmitBulkImport.addEventListener("click", function () {
                var fileInput = document.getElementById("bulkFile");
                if (!fileInput || !fileInput.files.length) {
                    Swal.fire("Uyarı", "Lütfen yüklenecek dosyayı seçin.", "warning");
                    return;
                }

                var formData = new FormData();
                formData.append("file", fileInput.files[0]);

                var meta = document.querySelector('meta[name="csrf-token"]');
                if (meta) {
                    formData.append("csrf_token", meta.getAttribute("content"));
                }

                Swal.fire({
                    title: 'Yükleniyor...',
                    text: 'Kullanıcılar içe aktarılıyor, lütfen bekleyin.',
                    allowOutsideClick: false,
                    didOpen: () => {
                        Swal.showLoading();
                    }
                });

                fetch("/admin/users/bulk-import", {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-CSRFToken": meta ? meta.getAttribute("content") : ""
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === "success") {
                            Swal.fire({
                                icon: 'success',
                                title: 'Başarılı!',
                                text: data.message,
                            }).then(() => {
                                window.location.reload();
                            });
                        } else {
                            Swal.fire({
                                icon: 'error',
                                title: 'Hata!',
                                text: data.message || "Bir hata oluştu."
                            });
                        }
                    })
                    .catch(error => {
                        Swal.fire({
                            icon: 'error',
                            title: 'Hata!',
                            text: 'Sunucu ile iletişim kurulamadı.'
                        });
                    });
            });
        }
    });

    window.openUserAddModal = openAddModal;
    window.openUserEditModal = openEditModal;
})();
