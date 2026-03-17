/* ═══════════════════════════════════════════════════════
   E-posta Ayarları — ayarlar_eposta.js
   Kural 5: Tüm JS harici dosyada, Jinja2 {{ }} yasak.
   Veri aktarımı data-* attribute ile yapılır.
   ═══════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {

    var wrap       = document.querySelector('.eposta-page-wrap');
    var saveUrl    = wrap.getAttribute('data-save-url');
    var testUrl    = wrap.getAttribute('data-test-url');
    var sendTestUrl = wrap.getAttribute('data-send-test-url');

    var toggleEl   = document.getElementById('use_custom_smtp');
    var smtpFields = document.getElementById('smtp-fields');

    /* ── SMTP alanlarını toggle ── */
    toggleEl.addEventListener('change', function () {
        if (this.checked) {
            smtpFields.classList.remove('eposta-hidden');
        } else {
            smtpFields.classList.add('eposta-hidden');
        }
    });

    /* ── TLS / SSL birbirini dışlar ── */
    var tlsEl = document.getElementById('smtp_use_tls');
    var sslEl = document.getElementById('smtp_use_ssl');
    tlsEl.addEventListener('change', function () { if (this.checked) sslEl.checked = false; });
    sslEl.addEventListener('change', function () { if (this.checked) tlsEl.checked = false; });

    /* ── Form verilerini topla ── */
    function _collectData() {
        return {
            use_custom_smtp:          toggleEl.checked,
            smtp_host:                document.getElementById('smtp_host').value.trim(),
            smtp_port:                parseInt(document.getElementById('smtp_port').value) || 587,
            smtp_use_tls:             tlsEl.checked,
            smtp_use_ssl:             sslEl.checked,
            smtp_username:            document.getElementById('smtp_username').value.trim(),
            smtp_password:            document.getElementById('smtp_password').value,
            sender_name:              document.getElementById('sender_name').value.trim(),
            sender_email:             document.getElementById('sender_email').value.trim(),
            notify_on_process_assign: document.getElementById('notify_on_process_assign').checked,
            notify_on_kpi_change:     document.getElementById('notify_on_kpi_change').checked,
            notify_on_activity_add:   document.getElementById('notify_on_activity_add').checked,
            notify_on_task_assign:    document.getElementById('notify_on_task_assign').checked,
        };
    }

    /* ── Bağlantı Testi ── */
    document.getElementById('btn-test-conn').addEventListener('click', function () {
        var data = _collectData();
        if (!data.smtp_host || !data.smtp_username) {
            MicroUI.uyari('Sunucu adresi ve kullanıcı adı zorunludur.');
            return;
        }
        var resultEl = document.getElementById('test-conn-result');
        resultEl.textContent = 'Test ediliyor...';
        resultEl.className = 'eposta-test-result';

        MicroUI.yukleniyor('SMTP bağlantısı test ediliyor...');
        MicroUI.post(testUrl, data,
            function (res) {
                MicroUI.kapat();
                resultEl.textContent = '✓ ' + res.message;
                resultEl.className = 'eposta-test-result eposta-test-ok';
            },
            function (res) {
                MicroUI.kapat();
                resultEl.textContent = '✗ ' + (res.message || 'Bağlantı başarısız.');
                resultEl.className = 'eposta-test-result eposta-test-fail';
            }
        );
    });

    /* ── Kaydet ── */
    document.getElementById('btn-save').addEventListener('click', function () {
        var data = _collectData();
        if (data.use_custom_smtp && (!data.smtp_host || !data.smtp_username)) {
            MicroUI.uyari('Özel SMTP aktifken sunucu adresi ve kullanıcı adı zorunludur.');
            return;
        }
        MicroUI.yukleniyor('Kaydediliyor...');
        MicroUI.post(saveUrl, data,
            function (res) {
                MicroUI.kapat();
                MicroUI.basari(res.message || 'Ayarlar kaydedildi.');
            },
            function (res) {
                MicroUI.kapat();
                MicroUI.hata(res.message || 'Kayıt başarısız.');
            }
        );
    });

    /* ── Test Maili Gönder ── */
    document.getElementById('btn-send-test').addEventListener('click', function () {
        MicroUI.onayla(
            'Kayıtlı ayarlarla kendi e-posta adresinize test maili gönderilecek.',
            function () {
                MicroUI.yukleniyor('Mail gönderiliyor...');
                MicroUI.post(sendTestUrl, {},
                    function (res) {
                        MicroUI.kapat();
                        MicroUI.basari(res.message);
                    },
                    function (res) {
                        MicroUI.kapat();
                        MicroUI.hata(res.message || 'Mail gönderilemedi.');
                    }
                );
            },
            'Test Maili',
            'Gönder'
        );
    });

});
