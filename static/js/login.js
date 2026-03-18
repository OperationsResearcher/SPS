document.addEventListener('DOMContentLoaded', function () {
    const quickLoginCheckbox = document.getElementById('quickLogin');
    const passwordInput = document.getElementById('password');
    const passwordIcon = document.querySelector('.input-with-icon:has(#password) .input-icon');

    if (quickLoginCheckbox) {
        quickLoginCheckbox.addEventListener('change', function () {
            if (this.checked) {
                passwordInput.disabled = true;
                passwordInput.value = '';
                passwordInput.required = false;
                passwordInput.placeholder = 'Şifre (Devre Dışı)';
                passwordInput.style.opacity = '0.5';
                if (passwordIcon) {
                    passwordIcon.classList.remove('fa-lock');
                    passwordIcon.classList.add('fa-lock-open');
                }
            } else {
                passwordInput.disabled = false;
                passwordInput.required = true;
                passwordInput.placeholder = 'Şifrenizi giriniz';
                passwordInput.style.opacity = '1';
                if (passwordIcon) {
                    passwordIcon.classList.remove('fa-lock-open');
                    passwordIcon.classList.add('fa-lock');
                }
            }
        });
    }
});
