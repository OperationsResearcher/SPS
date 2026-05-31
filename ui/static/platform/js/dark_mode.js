/* Sprint 32: Dark mode toggle — global utility
 *
 * Kullanım (template'te buton):
 *   <button onclick="KKTheme.toggle()">🌓 Tema</button>
 *
 * localStorage'da `kk_theme` ('light' | 'dark') tutar.
 * Sayfa yüklemede base.html'deki inline script FOUC'u önler.
 */
(function(global) {
    const KEY = "kk_theme";
    const API = "/api/profile/theme";

    function apply(theme, opts) {
        document.documentElement.setAttribute("data-theme", theme);
        document.body.setAttribute("data-theme", theme);
        try { localStorage.setItem(KEY, theme); } catch(e) {}
        document.querySelectorAll("[data-theme-icon]").forEach(el => {
            el.textContent = theme === "dark" ? "☀️" : "🌙";
        });
        if (!opts || !opts.skipServer) syncToServer(theme);
    }

    function syncToServer(theme) {
        try {
            const csrf = document.querySelector('meta[name="csrf-token"]')?.content || "";
            fetch(API, {
                method: "POST",
                credentials: "same-origin",
                headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
                body: JSON.stringify({ theme })
            }).catch(() => {});
        } catch(e) {}
    }

    function get() {
        try { return localStorage.getItem(KEY) || "light"; }
        catch(e) { return "light"; }
    }

    function toggle() {
        const cur = get();
        apply(cur === "dark" ? "light" : "dark");
    }

    function init() {
        // Önce localStorage ile FOUC'suz uygula, sonra sunucudan oku ve gerekiyorsa düzelt
        apply(get(), { skipServer: true });
        try {
            fetch(API, { credentials: "same-origin" })
                .then(r => r.ok ? r.json() : null)
                .then(j => {
                    if (j && j.success && j.theme && j.theme !== get()) {
                        apply(j.theme, { skipServer: true });
                    }
                })
                .catch(() => {});
        } catch(e) {}
    }

    global.KKTheme = { get, apply, toggle, init };

    if (document.readyState !== "loading") {
        init();
    } else {
        document.addEventListener("DOMContentLoaded", init);
    }
})(window);
