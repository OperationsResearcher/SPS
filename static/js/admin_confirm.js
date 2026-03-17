/**
 * FIX: Kural 1 — confirm() yasak; SweetAlert2 zorunlu.
 * Confirmation before submit for forms with data-confirm attribute.
 */
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("form[data-confirm]").forEach(function (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault();
            var self = this;
            Swal.fire({
                title: form.getAttribute("data-confirm"),
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#dc3545",
                cancelButtonColor: "#6c757d",
                confirmButtonText: "Evet, devam et",
                cancelButtonText: "İptal"
            }).then(function (result) {
                if (result.isConfirmed) {
                    self.submit();
                }
            });
        });
    });
});
