/* ═══════════════════════════════════════════════════════
   Micro Platform — Alpine.js global + Sidebar + MicroUI
   ═══════════════════════════════════════════════════════ */

/* ── Alpine.js global data ── */
function microApp() {
    return {
        darkMode: localStorage.getItem('micro_dark') === 'true',
        sidebarOpen: false,

        toggleDark() {
            this.darkMode = !this.darkMode;
            localStorage.setItem('micro_dark', this.darkMode);
            try {
                document.dispatchEvent(new CustomEvent('micro-theme-changed', { detail: { dark: this.darkMode } }));
            } catch (e) { /* ignore */ }
        },

        openSidebar()  { this.sidebarOpen = true;  document.body.style.overflow = 'hidden'; },
        closeSidebar() { this.sidebarOpen = false; document.body.style.overflow = ''; },
        toggleSidebar() {
            this.sidebarOpen ? this.closeSidebar() : this.openSidebar();
        }
    };
}

/* ── Flash mesajları otomatik kapat ── */
document.addEventListener('DOMContentLoaded', function () {
    var flashBox = document.getElementById('flash-messages');
    if (flashBox) {
        setTimeout(function () {
            flashBox.style.transition = 'opacity 0.5s';
            flashBox.style.opacity = '0';
            setTimeout(function () { flashBox.remove(); }, 500);
        }, 4000);
    }

    /* Sidebar: klavye ESC ile kapat */
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            var sidebar = document.querySelector('.micro-sidebar');
            var overlay = document.querySelector('.sidebar-overlay');
            if (sidebar && sidebar.classList.contains('open')) {
                sidebar.classList.remove('open');
                if (overlay) overlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        }
    });

    /* Sidebar hamburger (non-Alpine fallback) */
    var hamburger = document.getElementById('sidebar-hamburger');
    var sidebar   = document.querySelector('.micro-sidebar');
    var overlay   = document.querySelector('.sidebar-overlay');

    if (hamburger && sidebar) {
        hamburger.addEventListener('click', function () {
            sidebar.classList.toggle('open');
            if (overlay) overlay.classList.toggle('active');
            document.body.style.overflow = sidebar.classList.contains('open') ? 'hidden' : '';
        });
    }

    if (overlay) {
        overlay.addEventListener('click', function () {
            if (sidebar) sidebar.classList.remove('open');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
});

/* ═══════════════════════════════════════════════════════
   MicroUI — Ortak SweetAlert2 yardımcıları (Kural 1)
   ═══════════════════════════════════════════════════════ */
var MicroUI = {

    basari: function (mesaj, baslik) {
        Swal.fire({
            icon: 'success',
            title: baslik || 'Başarılı',
            text: mesaj,
            confirmButtonColor: '#6366f1',
            timer: 2500,
            showConfirmButton: false,
            toast: false
        });
    },

    hata: function (mesaj, baslik) {
        Swal.fire({
            icon: 'error',
            title: baslik || 'Hata',
            text: mesaj || 'Bir hata oluştu. Lütfen tekrar deneyin.',
            confirmButtonColor: '#6366f1',
            confirmButtonText: 'Tamam'
        });
    },

    uyari: function (mesaj, baslik) {
        Swal.fire({
            icon: 'warning',
            title: baslik || 'Uyarı',
            text: mesaj,
            confirmButtonColor: '#6366f1',
            confirmButtonText: 'Tamam'
        });
    },

    /**
     * Onay penceresi — varsayılan: soru ikonu (turuncu uyarı değil).
     * opts: { icon, confirmButtonColor } — yıkıcı işlemler için icon:'warning', confirmButtonColor:'#dc2626'
     */
    onayla: function (mesaj, onConfirm, baslik, confirmText, opts) {
        opts = opts || {};
        Swal.fire({
            icon: opts.icon || 'question',
            title: baslik || 'Emin misiniz?',
            text: mesaj,
            showCancelButton: true,
            confirmButtonColor: opts.confirmButtonColor || '#6366f1',
            cancelButtonColor: '#6b7280',
            confirmButtonText: confirmText || 'Evet, devam et',
            cancelButtonText: 'İptal',
            reverseButtons: true
        }).then(function (result) {
            if (result.isConfirmed && typeof onConfirm === 'function') {
                onConfirm();
            }
        });
    },

    yukleniyor: function (mesaj) {
        Swal.fire({
            title: mesaj || 'İşleniyor...',
            allowOutsideClick: false,
            showConfirmButton: false,
            didOpen: function () { Swal.showLoading(); }
        });
    },

    kapat: function () { Swal.close(); },

    /* AJAX POST yardımcısı */
    post: function (url, data, onSuccess, onError) {
        var csrfToken = document.querySelector('meta[name="csrf-token"]');
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken ? csrfToken.content : ''
            },
            body: JSON.stringify(data)
        })
        .then(function (r) {
            var ct = (r.headers.get('content-type') || '');
            if (ct.indexOf('application/json') === -1) {
                return r.text().then(function (t) {
                    throw new Error(r.status === 403 ? 'Bu işlem için yetkiniz yok.' : ('HTTP ' + r.status));
                });
            }
            return r.json();
        })
        .then(function (res) {
            if (res.success) {
                if (typeof onSuccess === 'function') onSuccess(res);
            } else {
                if (typeof onError === 'function') onError(res);
                else MicroUI.hata(res.message || 'İşlem başarısız.');
            }
        })
        .catch(function (err) {
            console.error(err);
            var msg = (err && err.message) ? err.message : 'Sunucu bağlantı hatası.';
            if (typeof onError === 'function') onError({ message: msg });
            else MicroUI.hata(msg);
        });
    }
};


/* ═══════════════════════════════════════════════════════
   Bildirim Badge — Topbar okunmamış sayacı
   ═══════════════════════════════════════════════════════ */
(function () {
    var btn = document.querySelector('.topbar-notif-btn');
    if (!btn) return;

    var badge = document.getElementById('notif-badge');
    var url   = btn.getAttribute('data-unread-url');
    if (!url || !badge) return;

    function refreshBadge() {
        fetch(url)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                var count = data.count || 0;
                if (count > 0) {
                    badge.textContent = count > 99 ? '99+' : count;
                    badge.style.display = 'block';
                } else {
                    badge.style.display = 'none';
                }
            })
            .catch(function () { /* sessizce geç */ });
    }

    // Sayfa yüklenince hemen çek, sonra her 60 sn'de bir yenile
    document.addEventListener('DOMContentLoaded', function () {
        refreshBadge();
        setInterval(refreshBadge, 60000);
    });
})();
