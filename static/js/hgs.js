/**
 * HGS - Hızlı Giriş Ekranı
 * Arama, sekmeler ve rol filtreleme.
 */
(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        const quickAra = document.getElementById("quickAra");
        const roleButtons = document.querySelectorAll(".role-filter");

        function getSearchableText(card) {
            return (card.textContent || "").toLowerCase();
        }

        function applySearch(term) {
            const activePane = document.querySelector(".tab-pane.active");
            if (!activePane) return;
            activePane.querySelectorAll(".user-card").forEach(function (card) {
                const text = getSearchableText(card);
                card.style.display = text.includes(term) ? "" : "none";
            });
        }

        function applyRoleFilter(role) {
            const activePane = document.querySelector(".tab-pane.active");
            if (!activePane) return;
            activePane.querySelectorAll(".user-card").forEach(function (card) {
                const cardRole = (card.dataset.role || "").toLowerCase();
                let match = false;
                if (role === "all") match = true;
                else if (role === "user") {
                    match = ["user", "tenantadmin"].indexOf(cardRole) !== -1;
                } else {
                    match = cardRole === role;
                }
                card.style.display = match ? "" : "none";
            });
        }

        if (quickAra) {
            quickAra.addEventListener("input", function () {
                applySearch(this.value.toLowerCase());
            });
        }

        document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(function (tab) {
            tab.addEventListener("shown.bs.tab", function () {
                if (quickAra && quickAra.value.length > 0) {
                    applySearch(quickAra.value.toLowerCase());
                }
                var activeRoleBtn = document.querySelector(".role-filter.active");
                if (activeRoleBtn) {
                    applyRoleFilter(activeRoleBtn.dataset.role || "all");
                }
            });
        });

        roleButtons.forEach(function (btn) {
            btn.addEventListener("click", function () {
                roleButtons.forEach(function (b) {
                    b.classList.remove("active");
                });
                this.classList.add("active");
                applyRoleFilter(this.dataset.role || "all");
            });
        });
    });
})();
