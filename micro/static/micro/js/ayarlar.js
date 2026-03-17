/* Micro — Ayarlar sayfası JS */

document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('settingsForm');
    if (!form) return;

    form.addEventListener('submit', function () {
        // Submit sonrası SweetAlert2 ile bildirim (sayfa yenilendikten sonra flash mesaj gösterilir)
        // Burada sadece submit engellenmez, flash mesaj backend'den gelir
    });
});
