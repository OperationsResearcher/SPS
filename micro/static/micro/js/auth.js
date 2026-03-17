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
                title: 'Eksik Bilgi',
                text: 'Lütfen e-posta ve şifrenizi girin.',
                confirmButtonColor: '#4F46E5',
                confirmButtonText: 'Tamam'
            });
        }
    });
});
