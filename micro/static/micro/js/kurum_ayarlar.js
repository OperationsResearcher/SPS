/* ═══════════════════════════════════════════════════════
   Kurum Ayarları — kurum_ayarlar.js
   Kural: JS harici dosya, fetch URL'leri data-* attribute ile alınır.
   ═══════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {
    var wrap = document.querySelector('.kurum-ayarlar-wrap');
    if (!wrap) return;

    var saveUrl = wrap.getAttribute('data-save-url');
    if (!saveUrl) return;

    var elKurumAdi = document.getElementById('kurum_adi');
    var elSektor = document.getElementById('sektor');
    var elVergiNo = document.getElementById('vergi_no');
    var elAdres = document.getElementById('adres');
    var elTelefon = document.getElementById('telefon');
    var elEmail = document.getElementById('email');
    var elWebsite = document.getElementById('website');
    var elLogo = document.getElementById('kurum_logo');
    var btnSave = document.getElementById('btn-save');
    var btnLogoUpload = document.getElementById('btn-logo-upload');

    function _val(el) {
        return el ? (el.value || '').trim() : '';
    }

    function _collectData() {
        return {
            kurum_adi: _val(elKurumAdi),
            sektor: _val(elSektor),
            vergi_no: _val(elVergiNo),
            adres: _val(elAdres),
            telefon: _val(elTelefon),
            email: _val(elEmail),
            website: _val(elWebsite),
        };
    }

    if (btnSave) {
        btnSave.addEventListener('click', function () {
            var data = _collectData();
            if (!data.kurum_adi) {
                MicroUI.uyari('Kurum adı zorunludur.');
                return;
            }

            MicroUI.yukleniyor('Kaydediliyor...');
            MicroUI.post(
                saveUrl,
                data,
                function (res) {
                    MicroUI.kapat();
                    MicroUI.basari(res.message || 'Kurum ayarları kaydedildi.');
                },
                function (res) {
                    MicroUI.kapat();
                    MicroUI.hata(res.message || 'Kayıt başarısız.');
                }
            );
        });
    }

    // Logo yükleme (multipart)
    function _uploadLogo() {
        if (!elLogo || !elLogo.files || !elLogo.files.length) {
            MicroUI.uyari('Lütfen bir logo dosyası seçin.');
            return;
        }

        var file = elLogo.files[0];
        var form = new FormData();
        form.append('logo', file);

        MicroUI.yukleniyor('Logo yükleniyor...');

        var csrfToken = document.querySelector('meta[name="csrf-token"]');
        var csrfValue = csrfToken ? csrfToken.content : '';

        fetch(saveUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfValue
            },
            body: form
        })
            .then(function (r) { return r.json(); })
            .then(function (res) {
                MicroUI.kapat();
                if (res && res.success) {
                    MicroUI.basari(res.message || 'Logo yüklendi.');
                    // Sayfayı yeniden çekip mevcut logoyu güncelle
                    window.location.href = saveUrl;
                } else {
                    MicroUI.hata((res && res.message) ? res.message : 'Logo yükleme başarısız.');
                }
            })
            .catch(function (err) {
                MicroUI.kapat();
                MicroUI.hata('Sunucu bağlantı hatası.');
            });
    }

    if (btnLogoUpload) {
        btnLogoUpload.addEventListener('click', function () {
            _uploadLogo();
        });
    }
});

