document.addEventListener('DOMContentLoaded', function () {
    var kuleForm = document.getElementById('kuleForm');
    var btnKuleGonder = document.getElementById('btnKuleGonder');

    if (kuleForm && btnKuleGonder) {
        btnKuleGonder.addEventListener('click', function () {
            if (!kuleForm.checkValidity()) {
                kuleForm.reportValidity();
                return;
            }

            var formData = new FormData(kuleForm);

            // Set current page url
            var kulePageUrl = document.getElementById('kulePageUrl');
            if (kulePageUrl) kulePageUrl.value = window.location.href;
            formData.set('page_url', window.location.href);

            var csrfTokenInput = document.querySelector('input[name="csrf_token"]');
            var csrfHeader = csrfTokenInput ? csrfTokenInput.value : '';

            Swal.fire({
                title: 'Kule İletişim',
                text: 'Mesajınız Kule\'ye gönderiliyor, lütfen bekleyin...',
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });

            fetch('/kule/send', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfHeader
                },
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Gönderildi',
                            text: 'Mesajınız başarıyla Kule\'ye ulaştı.',
                            confirmButtonText: 'Tamam'
                        }).then(() => {
                            var kuleModal = bootstrap.Modal.getInstance(document.getElementById('kuleModal'));
                            kuleModal.hide();
                            kuleForm.reset();
                        });
                    } else {
                        Swal.fire('Hata', data.message || 'Gönderim sırasında bir hata oluştu.', 'error');
                    }
                })
                .catch(err => {
                    Swal.fire('Bağlantı Hatası', 'Sunucu ile iletişim koptu. Lütfen tekrar deneyin.', 'error');
                });
        });
    }
});
