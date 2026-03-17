/* ═══════════════════════════════════════════════════════
   Bildirim Merkezi — bildirim.js
   Kural 5: Tüm JS harici dosyada, Jinja2 {{ }} yasak.
   Veri aktarımı data-* attribute ile yapılır.
   ═══════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {

    /* ── Tekil satıra tıklama: okundu işaretle + linke git ── */
    document.querySelectorAll('.bildirim-row').forEach(function (row) {
        row.addEventListener('click', function () {
            var id      = row.getAttribute('data-id');
            var isRead  = row.getAttribute('data-read') === 'true';
            var markUrl = row.getAttribute('data-mark-url');
            var link    = row.getAttribute('data-link');

            function navigate() {
                if (link) window.location.href = link;
            }

            if (!isRead && markUrl) {
                var csrf = document.querySelector('meta[name="csrf-token"]');
                fetch(markUrl, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrf ? csrf.content : '' }
                })
                .then(function (r) { return r.json(); })
                .then(function (res) {
                    if (res.success) {
                        row.classList.remove('bildirim-unread');
                        row.setAttribute('data-read', 'true');
                        var dot = document.getElementById('bildirim-dot-' + id);
                        if (dot) dot.remove();
                        var iconEl = row.querySelector('.bildirim-icon');
                        if (iconEl) iconEl.classList.remove('bildirim-icon-unread');
                        var bellEl = row.querySelector('.bildirim-bell');
                        if (bellEl) bellEl.classList.remove('bildirim-bell-unread');
                        var titleEl = row.querySelector('.bildirim-title');
                        if (titleEl) titleEl.classList.remove('bildirim-title-unread');
                        _decrementBadge();
                    }
                    navigate();
                })
                .catch(function () { navigate(); });
            } else {
                navigate();
            }
        });
    });

    /* ── Tümünü Okundu İşaretle butonu ── */
    var btnAll = document.getElementById('btn-mark-all-read');
    if (btnAll) {
        btnAll.addEventListener('click', function () {
            var url  = btnAll.getAttribute('data-url');
            var csrf = document.querySelector('meta[name="csrf-token"]');

            MicroUI.onayla(
                'Tüm bildirimler okundu olarak işaretlenecek.',
                function () {
                    MicroUI.yukleniyor('İşleniyor...');
                    fetch(url, {
                        method: 'POST',
                        headers: { 'X-CSRFToken': csrf ? csrf.content : '' }
                    })
                    .then(function (r) { return r.json(); })
                    .then(function (res) {
                        MicroUI.kapat();
                        if (res.success) {
                            /* Tüm satırları okundu görünümüne al */
                            document.querySelectorAll('.bildirim-row').forEach(function (r) {
                                r.classList.remove('bildirim-unread');
                                r.setAttribute('data-read', 'true');
                                var dot = r.querySelector('.bildirim-dot');
                                if (dot) dot.remove();
                                var iconEl = r.querySelector('.bildirim-icon');
                                if (iconEl) iconEl.classList.remove('bildirim-icon-unread');
                                var bellEl = r.querySelector('.bildirim-bell');
                                if (bellEl) bellEl.classList.remove('bildirim-bell-unread');
                                var titleEl = r.querySelector('.bildirim-title');
                                if (titleEl) titleEl.classList.remove('bildirim-title-unread');
                            });
                            /* Badge sıfırla */
                            var badge = document.getElementById('notif-badge');
                            if (badge) badge.style.display = 'none';
                            btnAll.style.display = 'none';
                            MicroUI.basari('Tüm bildirimler okundu olarak işaretlendi.');
                        } else {
                            MicroUI.hata(res.message || 'İşlem başarısız.');
                        }
                    })
                    .catch(function () {
                        MicroUI.kapat();
                        MicroUI.hata('Sunucu bağlantı hatası.');
                    });
                },
                'Tümünü Okundu İşaretle',
                'Evet, işaretle'
            );
        });
    }

    /* ── Badge sayacını 1 azalt ── */
    function _decrementBadge() {
        var badge = document.getElementById('notif-badge');
        if (!badge || badge.style.display === 'none') return;
        var current = parseInt(badge.textContent, 10);
        if (isNaN(current)) return;
        var next = current - 1;
        if (next <= 0) {
            badge.style.display = 'none';
        } else {
            badge.textContent = next > 99 ? '99+' : next;
        }
    }

});
