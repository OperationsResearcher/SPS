/* ═══════════════════════════════════════════════════════
   Micro Platform — Tema + Dropdown + Sidebar + MicroUI
   (Alpine.js kaldırıldı — TASK-236, CSP unsafe-eval)
   ═══════════════════════════════════════════════════════ */

/* Ortak HTML kaçış (saklı XSS önlemi): kullanıcı verisini innerHTML'e basmadan önce */
window.mcEsc = function (s) {
    if (s === null || s === undefined) return '';
    return String(s).replace(/[&<>"']/g, function (c) {
        return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c];
    });
};

/* ── Tema (dark mode) — eski microApp() davranışı birebir ── */
(function () {
    'use strict';
    // Tek tema kaynağı: hem System A (micro_dark/class="dark") hem System B
    // (kk_theme/data-theme) anahtarlarını oku ki eski kullanıcılar da senkron olsun.
    var darkMode = (localStorage.getItem('micro_dark') === 'true') || (localStorage.getItem('kk_theme') === 'dark');

    function applyDarkClass() {
        document.documentElement.classList.toggle('dark', darkMode);
        if (document.body) document.body.classList.toggle('dark', darkMode);
        document.querySelectorAll('[data-kk-dark-label]').forEach(function (el) {
            el.textContent = darkMode ? el.dataset.labelLight : el.dataset.labelDark;
        });
    }

    function toggleDark() {
        darkMode = !darkMode;
        localStorage.setItem('micro_dark', darkMode);
        // System B (data-theme/kk_theme + sunucu senkron) ile birlikte uygula —
        // aksi halde [data-theme="dark"] kuralları hiç aktive olmuyordu.
        try {
            if (window.KKTheme) {
                window.KKTheme.apply(darkMode ? 'dark' : 'light');
            } else {
                var t = darkMode ? 'dark' : 'light';
                localStorage.setItem('kk_theme', t);
                document.documentElement.setAttribute('data-theme', t);
                document.body.setAttribute('data-theme', t);
            }
        } catch (e) { /* ignore */ }
        try {
            document.dispatchEvent(new CustomEvent('micro-theme-changed', { detail: { dark: darkMode } }));
        } catch (e) { /* ignore */ }
        applyDarkClass();
    }

    document.addEventListener('DOMContentLoaded', function () {
        applyDarkClass();
        document.querySelectorAll('[data-kk-toggle-dark]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                toggleDark();
                if (btn.hasAttribute('data-kk-dd-close')) {
                    var panel = btn.closest('[data-kk-dd-panel]');
                    if (panel) panel.style.display = 'none';
                }
            });
        });
    });
})();

/* ── Dropdown'lar (Alpine x-data/{open} yerine) ──
   data-kk-dropdown konteyner; data-kk-dd-toggle buton (veya data-kk-dd-self:
   konteynerin kendisi toggle'dır); data-kk-dd-panel panel. Dışarı tıklama kapatır. */
(function () {
    'use strict';
    document.addEventListener('DOMContentLoaded', function () {
        function closeAll(except) {
            document.querySelectorAll('[data-kk-dropdown] > [data-kk-dd-panel], [data-kk-dropdown] [data-kk-dd-panel]').forEach(function (p) {
                if (p !== except) p.style.display = 'none';
            });
        }
        document.querySelectorAll('[data-kk-dropdown]').forEach(function (dd) {
            var panel = dd.querySelector('[data-kk-dd-panel]');
            if (!panel) return;
            var toggler = dd.hasAttribute('data-kk-dd-self') ? dd : dd.querySelector('[data-kk-dd-toggle]');
            if (!toggler) return;
            toggler.addEventListener('click', function (e) {
                // panel içi tıklamalar (linkler, dark toggle) toggle sayılmaz
                if (panel.contains(e.target)) return;
                var isOpen = panel.style.display !== 'none';
                closeAll(null);
                panel.style.display = isOpen ? 'none' : '';
                e.stopPropagation();
            });
        });
        document.addEventListener('click', function (e) {
            if (!e.target.closest('[data-kk-dropdown]')) closeAll(null);
        });
    });
})();

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
            title: baslik || t('Başarılı'),
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
            title: baslik || t('Hata'),
            text: mesaj || t('Bir hata oluştu. Lütfen tekrar deneyin.'),
            confirmButtonColor: '#6366f1',
            confirmButtonText: t('Tamam')
        });
    },

    uyari: function (mesaj, baslik) {
        Swal.fire({
            icon: 'warning',
            title: baslik || t('Uyarı'),
            text: mesaj,
            confirmButtonColor: '#6366f1',
            confirmButtonText: t('Tamam')
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
            title: baslik || t('Emin misiniz?'),
            text: mesaj,
            showCancelButton: true,
            confirmButtonColor: opts.confirmButtonColor || '#6366f1',
            cancelButtonColor: '#6b7280',
            confirmButtonText: confirmText || t('Evet, devam et'),
            cancelButtonText: t('İptal'),
            reverseButtons: true
        }).then(function (result) {
            if (result.isConfirmed && typeof onConfirm === 'function') {
                onConfirm();
            }
        });
    },

    yukleniyor: function (mesaj) {
        Swal.fire({
            title: mesaj || t('İşleniyor...'),
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
                return r.text().then(function () {
                    throw new Error(r.status === 403 ? t('Bu işlem için yetkiniz yok.') : ('HTTP ' + r.status));
                });
            }
            return r.json();
        })
        .then(function (res) {
            if (res.success) {
                if (typeof onSuccess === 'function') onSuccess(res);
            } else {
                if (typeof onError === 'function') onError(res);
                else MicroUI.hata(res.message || t('İşlem başarısız.'));
            }
        })
        .catch(function (err) {
            console.error(err);
            var msg = (err && err.message) ? err.message : t('Sunucu bağlantı hatası.');
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

/**
 * Başarı puanı rozeti (Karar 2, Faz 1B). Ölçeğe göre renk:
 *   '1-5'   → ≥4 yeşil, ≥3 sarı, altı kırmızı   (eski aralık formatı)
 *   '0-100' → ≥90 yeşil, ≥70 sarı, altı kırmızı (bant formatı)
 * Sunucu puanı yoksa "—" (JS yedek hesabı kaldırıldı — Karar 3).
 */
(function () {
  "use strict";
  function esc(v) {
    return String(v).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  window.kkBasariPuanHtml = function (puan, olcek) {
    if (puan == null || puan === "" || Number.isNaN(Number(puan))) return "—";
    var n = Number(puan);
    var yuzluk = olcek === "0-100";
    var ok = yuzluk ? 90 : 4;
    var warn = yuzluk ? 70 : 3;
    var cls = n >= ok ? "micro-pg-ok" : n >= warn ? "micro-pg-warn" : "micro-pg-bad";
    var goster = Number.isInteger(n) ? String(n) : n.toFixed(1);
    return '<span class="' + cls + ' fw-bold" title="' + esc(yuzluk ? "0-100" : "1-5") + '">' + esc(goster) + "</span>";
  };
})();

/* ── Modal erişilebilirliği (E-018 / Dalga 4-A) ──────────────────────────
 * .mc-modal-overlay öğelerine role/aria-modal/aria-labelledby, kapat butonuna
 * aria-label; açılınca odak içeri alınır (focus-trap), Escape kapat butonunu
 * tetikler, kapanınca odak açan öğeye döner. Modal açma/kapama kodu değişmez:
 * görünürlük (display) gözlemlenir. */
(function () {
    'use strict';
    var OVERLAY = '.mc-modal-overlay';
    var FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
    var states = new WeakMap();   // overlay -> { open: bool, returnFocus: el|null }
    var stack = [];               // açık overlay'ler (son = en üstte)
    var idSeq = 0;

    function tr(s) { return (typeof window.t === 'function') ? window.t(s) : s; }

    function isOpen(el) {
        return window.getComputedStyle(el).display !== 'none';
    }

    function visibleFocusables(el) {
        return Array.prototype.filter.call(el.querySelectorAll(FOCUSABLE), function (n) {
            return n.getClientRects().length > 0;
        });
    }

    function decorate(overlay) {
        if (!overlay.querySelector('[role="dialog"]')) {
            overlay.setAttribute('role', 'dialog');
            overlay.setAttribute('aria-modal', 'true');
        }
        var title = overlay.querySelector('.mc-modal-header h3');
        if (title && !overlay.hasAttribute('aria-labelledby')) {
            if (!title.id) title.id = 'mc-modal-title-' + (++idSeq);
            overlay.setAttribute('aria-labelledby', title.id);
        }
        Array.prototype.forEach.call(overlay.querySelectorAll('.mc-modal-close:not([aria-label])'), function (b) {
            b.setAttribute('aria-label', tr('Kapat'));
        });
    }

    function onOpen(overlay) {
        var st = states.get(overlay);
        st.returnFocus = document.activeElement && document.activeElement !== document.body ? document.activeElement : null;
        stack.push(overlay);
        // Modal kendi odağını zaten koyduysa (ör. ilk input) dokunma
        if (!overlay.contains(document.activeElement)) {
            var first = visibleFocusables(overlay)[0];
            if (first) first.focus();
        }
    }

    function onClose(overlay) {
        var st = states.get(overlay);
        stack = stack.filter(function (o) { return o !== overlay; });
        var rf = st.returnFocus;
        st.returnFocus = null;
        if (rf && document.contains(rf) && !overlay.contains(rf) &&
            (!document.activeElement || document.activeElement === document.body || overlay.contains(document.activeElement))) {
            try { rf.focus(); } catch (e) { /* odak hedefi artık odaklanılabilir değil */ }
        }
    }

    function sync(overlay) {
        if (!overlay.classList.contains('mc-modal-overlay')) return;
        decorate(overlay);
        var st = states.get(overlay);
        if (!st) { st = { open: false, returnFocus: null }; states.set(overlay, st); }
        var open = isOpen(overlay);
        if (open && !st.open) { st.open = true; onOpen(overlay); }
        else if (!open && st.open) { st.open = false; onClose(overlay); }
    }

    function scan(root) {
        if (!root || root.nodeType !== 1) return;
        if (root.classList && root.classList.contains('mc-modal-overlay')) sync(root);
        Array.prototype.forEach.call(root.querySelectorAll ? root.querySelectorAll(OVERLAY) : [], sync);
    }

    function topmost() {
        for (var i = stack.length - 1; i >= 0; i--) {
            if (document.contains(stack[i]) && isOpen(stack[i])) return stack[i];
        }
        return null;
    }

    document.addEventListener('keydown', function (e) {
        var top = topmost();
        if (!top) return;
        if (e.key === 'Escape') {
            var closeBtn = Array.prototype.filter.call(top.querySelectorAll('.mc-modal-close'), function (b) {
                return b.getClientRects().length > 0;
            })[0];
            if (closeBtn) { e.preventDefault(); closeBtn.click(); }
            return;
        }
        if (e.key !== 'Tab') return;
        var items = visibleFocusables(top);
        if (!items.length) { e.preventDefault(); return; }
        var first = items[0], last = items[items.length - 1];
        var active = document.activeElement;
        var inside = top.contains(active);
        if (e.shiftKey) {
            if (!inside || active === first) { e.preventDefault(); last.focus(); }
        } else {
            if (!inside || active === last) { e.preventDefault(); first.focus(); }
        }
    }, true);

    var observer = new MutationObserver(function (mutations) {
        mutations.forEach(function (m) {
            if (m.type === 'childList') {
                Array.prototype.forEach.call(m.addedNodes, scan);
            } else if (m.type === 'attributes') {
                sync(m.target);
            }
        });
    });

    function init() {
        scan(document.body);
        observer.observe(document.body, {
            childList: true, subtree: true,
            attributes: true, attributeFilter: ['class', 'style']
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
