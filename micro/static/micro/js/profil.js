/* Micro — Profil sayfası JS */

document.addEventListener('DOMContentLoaded', function () {
    // Fotoğraf yükleme
    var photoInput = document.getElementById('profilePhotoInput');
    var profileData = document.querySelector('[data-upload-url]');
    var uploadUrl = profileData ? profileData.dataset.uploadUrl : null;

    if (photoInput && uploadUrl) {
        photoInput.addEventListener('change', function () {
            var file = this.files[0];
            if (!file) return;

            var formData = new FormData();
            formData.append('file', file);

            var csrfToken = document.querySelector('meta[name="csrf-token"]').content;

            fetch(uploadUrl, {
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken },
                body: formData
            })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                if (data.success) {
                    var img = document.getElementById('profilePhotoImg');
                    var placeholder = document.getElementById('profilePhotoPlaceholder');
                    if (img) {
                        img.src = data.photo_url;
                    } else if (placeholder) {
                        var newImg = document.createElement('img');
                        newImg.id = 'profilePhotoImg';
                        newImg.src = data.photo_url;
                        newImg.alt = 'Profil';
                        newImg.className = 'w-20 h-20 rounded-full object-cover border-2 border-indigo-200';
                        placeholder.replaceWith(newImg);
                    }
                    Swal.fire({
                        icon: 'success',
                        title: 'Başarılı',
                        text: 'Profil fotoğrafı güncellendi.',
                        confirmButtonColor: '#4F46E5',
                        timer: 2000,
                        showConfirmButton: false
                    });
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Hata',
                        text: data.message || 'Fotoğraf yüklenemedi.',
                        confirmButtonColor: '#4F46E5'
                    });
                }
            })
            .catch(function () {
                Swal.fire({
                    icon: 'error',
                    title: 'Hata',
                    text: 'Sunucuya bağlanılamadı.',
                    confirmButtonColor: '#4F46E5'
                });
            });
        });
    }

    // Form submit — şifre eşleşme kontrolü
    var form = document.getElementById('profileForm');
    if (form) {
        form.addEventListener('submit', function (e) {
            var newPwd = document.getElementById('new_password').value;
            var confirmPwd = document.getElementById('confirm_password').value;

            if (newPwd && newPwd !== confirmPwd) {
                e.preventDefault();
                Swal.fire({
                    icon: 'error',
                    title: 'Hata',
                    text: 'Yeni şifreler eşleşmiyor.',
                    confirmButtonColor: '#4F46E5'
                });
            }
        });
    }
});
