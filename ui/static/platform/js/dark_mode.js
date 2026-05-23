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

    function apply(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        document.body.setAttribute("data-theme", theme);
        try { localStorage.setItem(KEY, theme); } catch(e) {}
        // Tüm theme-aware butonları güncelle
        document.querySelectorAll("[data-theme-icon]").forEach(el => {
            el.textContent = theme === "dark" ? "☀️" : "🌙";
        });
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
        apply(get());
    }

    global.KKTheme = { get, apply, toggle, init };

    if (document.readyState !== "loading") {
        init();
    } else {
        document.addEventListener("DOMContentLoaded", init);
    }
})(window);
