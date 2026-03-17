/**
 * Layout Secici - Klasik / Sidebar
 * Madde 4: Her iki layout DOM'da, CSS class ile gosterim.
 * Madde 3: data-* veya window.CONFIG ile veri aktarimi.
 */
(function () {
    "use strict";

    var STORAGE_KEY = "kokpitim_layout";
    var LAYOUT_CLASSIC = "classic";
    var LAYOUT_SIDEBAR = "sidebar";

    function getInitialLayout() {
        var config = window.CONFIG || {};
        if (config.layoutPref) return config.layoutPref;
        var el = document.getElementById("appContextData");
        if (el && el.dataset && el.dataset.layoutPref) return el.dataset.layoutPref;
        return localStorage.getItem(STORAGE_KEY) || LAYOUT_CLASSIC;
    }

    function applyLayout(layout) {
        var body = document.body;
        body.classList.remove("layout-classic", "layout-sidebar");
        body.classList.add("layout-" + (layout === LAYOUT_SIDEBAR ? LAYOUT_SIDEBAR : LAYOUT_CLASSIC));
        updateActiveStates(layout);
    }

    function updateActiveStates(activeLayout) {
        document.querySelectorAll(".layout-option").forEach(function (opt) {
            var layout = opt.dataset.layout;
            if (layout === activeLayout) {
                opt.classList.add("active");
                var check = opt.querySelector(".layout-active-check");
                if (check) check.style.display = "";
            } else {
                opt.classList.remove("active");
                var check = opt.querySelector(".layout-active-check");
                if (check) check.style.display = "none";
            }
        });
    }

    function setLayout(layout) {
        if (layout !== LAYOUT_CLASSIC && layout !== LAYOUT_SIDEBAR) return;
        localStorage.setItem(STORAGE_KEY, layout);
        applyLayout(layout);
        document.querySelectorAll(".layout-menu").forEach(function (m) {
            m.classList.remove("show");
        });
    }

    function toggleLayoutMenu(menuId) {
        var menu = document.getElementById(menuId);
        if (!menu) return;
        document.querySelectorAll(".layout-menu").forEach(function (m) {
            m.classList.remove("show");
        });
        menu.classList.toggle("show");
    }

    document.addEventListener("click", function (e) {
        var btn = e.target.closest("[data-layout-toggle]");
        if (btn) {
            e.preventDefault();
            var menuId = btn.dataset.layoutToggle;
            if (menuId) toggleLayoutMenu(menuId);
            return;
        }
        var opt = e.target.closest(".layout-option");
        if (opt) {
            e.preventDefault();
            var layout = opt.dataset.layout;
            if (layout) setLayout(layout);
            return;
        }
        if (!e.target.closest(".layout-toggle")) {
            document.querySelectorAll(".layout-menu").forEach(function (m) {
                m.classList.remove("show");
            });
        }
    });

    document.addEventListener("DOMContentLoaded", function () {
        var layout = getInitialLayout();
        applyLayout(layout);
    });

    window.setLayout = setLayout;
    window.toggleLayoutMenu = toggleLayoutMenu;
})();
