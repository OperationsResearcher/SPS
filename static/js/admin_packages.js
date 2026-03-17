/**
 * Admin Packages - Bileşenler sekmesi: Rota senkronizasyonu ve bileşen slug güncelleme.
 * Anayasa: No inline JS/CSS, SweetAlert2, credentials: same-origin, data-* ile URL aktarımı.
 */
(function () {
    "use strict";

    var pane = document.getElementById("components-pane");
    if (!pane) return;

    var syncUrl = pane.dataset.syncUrl;
    var updateUrl = pane.dataset.updateUrl;
    if (!syncUrl || !updateUrl) return;

    var metaCsrf = document.querySelector('meta[name="csrf-token"]');
    var csrfToken = metaCsrf ? metaCsrf.getAttribute('content') || '' : '';

    function notify(title, text, icon) {
        if (typeof Swal !== "undefined") {
            Swal.fire({ title: title, text: text, icon: icon || "info", confirmButtonText: "Tamam" });
        }
    }

    function notifyToast(title, icon) {
        if (typeof Swal !== "undefined") {
            Swal.fire({
                title: title,
                icon: icon || "success",
                toast: true,
                position: "top-end",
                showConfirmButton: false,
                timer: 2500
            });
        }
    }

    var btnSync = document.getElementById("btnComponentsSync");
    if (btnSync) {
        btnSync.addEventListener("click", function () {
            btnSync.disabled = true;
            btnSync.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Taranıyor...';
            fetch(syncUrl, {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": csrfToken || ""
                }
            })
                .then(function (r) {
                    var ct = r.headers.get("Content-Type") || "";
                    if (!ct.includes("application/json")) {
                        throw new Error("Sunucu JSON yerine HTML döndü. Oturum süresi dolmuş veya yetki hatası olabilir. Sayfayı yenileyip tekrar deneyin.");
                    }
                    return r.json();
                })
                .then(function (data) {
                    btnSync.disabled = false;
                    btnSync.innerHTML = '<i class="fas fa-sync-alt me-1"></i> Sistemi Tarayıp Yenile';
                    if (data && data.success) {
                        notifyToast(data.message || data.added + " yeni rota eklendi.", "success");
                        window.location.reload();
                    } else {
                        notify("Uyarı", (data && data.message) || "Senkronizasyon tamamlandı.", "info");
                        window.location.reload();
                    }
                })
                .catch(function (err) {
                    btnSync.disabled = false;
                    btnSync.innerHTML = '<i class="fas fa-sync-alt me-1"></i> Sistemi Tarayıp Yenile';
                    notify("Hata", "İşlem sırasında stratejik bir hata saptandı: " + (err.message || "Bağlantı hatası."), "error");
                });
        });
    }

    document.querySelectorAll(".btn-save-slug").forEach(function (btn) {
        btn.addEventListener("click", function () {
            var rid = btn.dataset.routeId;
            var row = btn.closest("tr");
            var input = row ? row.querySelector(".component-slug-input") : null;
            var slug = input ? (input.value || "").trim() || null : null;

            fetch(updateUrl, {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": csrfToken || ""
                },
                body: JSON.stringify({ id: parseInt(rid, 10), component_slug: slug })
            })
                .then(function (r) {
                    var ct = r.headers.get("Content-Type") || "";
                    if (!ct.includes("application/json")) {
                        throw new Error("Sunucu JSON yerine HTML döndü. Oturum süresi dolmuş veya yetki hatası olabilir. Sayfayı yenileyip tekrar deneyin.");
                    }
                    return r.json();
                })
                .then(function (data) {
                    if (data && data.success) {
                        notifyToast(data.message || "Bileşen adı kaydedildi.", "success");
                    } else {
                        notify("Hata", (data && data.message) || "Güncelleme yapılamadı.", "error");
                    }
                })
                .catch(function (err) {
                    notify("Hata", "İşlem sırasında stratejik bir hata saptandı: " + (err.message || "Bağlantı hatası."), "error");
                });
        });
    });
})();
