/* Micro — Login sayfası JS */

document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('loginForm');
    if (!form) return;

    form.addEventListener('submit', function (e) {
        var email = document.getElementById('email').value.trim();
        var password = document.getElementById('password').value;

        if (!email || !password) {
            e.preventDefault();
            Swal.fire({
                icon: 'warning',
                title: t('Eksik Bilgi'),
                text: t('Lütfen e-posta ve şifrenizi girin.'),
                confirmButtonColor: '#4F46E5',
                confirmButtonText: t('Tamam')
            });
            return;
        }
        // Geçerli → çift gönderimi önle, "Giriş yapılıyor" durumu göster
        var btn = form.querySelector('button[type="submit"]');
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ' + t('Giriş yapılıyor…');
        }
    });
});
