// Layout & theme helpers
(function() {
    function setLayout(layout) {
        if (!['classic', 'sidebar'].includes(layout)) {
            if (window.showToast) showToast('error', 'Geçersiz layout seçimi', 'Hata');
            return;
        }

        fetch('/api/user/layout', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({layout: layout})
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                localStorage.setItem('layout', layout);
                if (window.showToast) showToast('success', 'Layout tercihiniz kaydedildi. Sayfa yenileniyor...', 'Başarılı');
                setTimeout(() => {
                    const currentUrl = new URL(window.location.href);
                    currentUrl.searchParams.set('layout', layout);
                    window.location.href = currentUrl.toString();
                }, 800);
            } else {
                if (window.showToast) showToast('error', data.message || 'Layout değiştirilemedi', 'Hata');
            }
        })
        .catch(err => {
            console.error('Layout save error:', err);
            if (window.showToast) showToast('error', 'Layout kaydedilirken hata oluştu. Lütfen tekrar deneyin.', 'Hata');
        });
    }

    function loadTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        let theme = savedTheme;
        try {
            const contextEl = document.getElementById('appContextData');
            if (contextEl && contextEl.dataset && contextEl.dataset.themePrefs) {
                const userTheme = JSON.parse(contextEl.dataset.themePrefs);
                if (userTheme && userTheme.theme) theme = userTheme.theme;
            }
        } catch (e) {}
        setTheme(theme, false);
    }

    function setTheme(theme, save) {
        document.documentElement.setAttribute('data-theme', theme);
        const themeIcon = document.getElementById('themeIcon');
        if (themeIcon) {
            themeIcon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        }
        if (save) {
            localStorage.setItem('theme', theme);
            saveThemePreference(theme);
        }
    }

    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        setTheme(newTheme, true);
    }

    function saveThemePreference(theme) {
        fetch('/api/user/theme', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({theme: theme})
        }).catch(err => console.log('Theme save error:', err));
    }

    function toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('mobileOverlay');

        if (sidebar) {
            sidebar.classList.toggle('collapsed');
            if (overlay) overlay.classList.toggle('show');

            if (window.innerWidth <= 992) {
                sidebar.classList.toggle('show');
            }
        }
    }

    function toggleLayoutMenu(event, menuId) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        const menu = document.getElementById(menuId);
        if (!menu) return;

        document.querySelectorAll('.layout-menu').forEach(otherMenu => {
            if (otherMenu.id !== menuId) {
                otherMenu.classList.remove('show');
            }
        });

        menu.classList.toggle('show');
    }

    document.addEventListener('click', function(e) {
        if (!e.target.closest('.layout-toggle')) {
            document.querySelectorAll('.layout-menu').forEach(menu => menu.classList.remove('show'));
        }
    });

    document.addEventListener('DOMContentLoaded', function() {
        loadTheme();

        const contextEl = document.getElementById('appContextData');
        const layoutPref = (contextEl && contextEl.dataset && contextEl.dataset.layoutPref) ? contextEl.dataset.layoutPref : '';
        const userPref = (contextEl && contextEl.dataset && contextEl.dataset.userLayoutPref) ? contextEl.dataset.userLayoutPref : '';
        const isAuthenticated = (contextEl && contextEl.dataset && contextEl.dataset.isAuth) ? (contextEl.dataset.isAuth === '1') : false;
        const currentUrl = new URL(window.location.href);
        const urlLayout = currentUrl.searchParams.get('layout');

        if (isAuthenticated && userPref && urlLayout && userPref === urlLayout) {
            currentUrl.searchParams.delete('layout');
            if (window.location.href !== currentUrl.toString()) {
                window.history.replaceState({}, '', currentUrl.toString());
            }
        }

        if (layoutPref === 'sidebar') {
            console.log('Sidebar layout aktif');
        } else {
            console.log('Classic layout aktif');
        }
    });

    window.setLayout = setLayout;
    window.toggleTheme = toggleTheme;
    window.toggleSidebar = toggleSidebar;
    window.toggleLayoutMenu = toggleLayoutMenu;
})();
