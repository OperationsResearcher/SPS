/**
 * Ayarlar sayfasi - tema, renk secimi, toast
 */
(function () {
    "use strict";

    var colorLabels = {
        primary: "Mavi (Varsayilan)",
        success: "Yesil",
        info: "Turkuaz",
        warning: "Turuncu",
        danger: "Kirmizi",
        dark: "Koyu"
    };

    function showToast(message, type) {
        var toastEl = document.getElementById("settingsToast");
        var toastMessage = document.getElementById("settingsToastMessage");
        var iconEl = toastEl && toastEl.querySelector(".settings-toast-icon");
        if (!toastEl || !toastMessage) return;
        toastMessage.textContent = message;
        if (iconEl) {
            var iconClass = "fas fa-check-circle text-success me-2 settings-toast-icon";
            if (type === "error") iconClass = "fas fa-exclamation-circle text-danger me-2 settings-toast-icon";
            else if (type === "info") iconClass = "fas fa-info-circle text-info me-2 settings-toast-icon";
            iconEl.className = iconClass;
        }
        var toast = new bootstrap.Toast(toastEl);
        toast.show();
    }

    document.addEventListener("DOMContentLoaded", function () {
        var colorBtns = document.querySelectorAll(".settings-color-btn");
        var primaryColorInput = document.getElementById("primary_color");
        var currentColorLabel = document.getElementById("currentColorLabel");

        colorBtns.forEach(function (btn) {
            btn.addEventListener("click", function () {
                var color = btn.getAttribute("data-color");
                if (primaryColorInput) primaryColorInput.value = color || "primary";
                if (currentColorLabel) {
                    currentColorLabel.textContent = colorLabels[color] || colorLabels.primary;
                    currentColorLabel.className = "badge bg-" + (color || "primary");
                }
                showToast((colorLabels[color] || "Renk") + " secildi.", "success");
            });
        });

        var themeOptions = document.querySelectorAll(".settings-theme-option");
        themeOptions.forEach(function (opt) {
            opt.addEventListener("click", function (e) {
                if (!e.target.closest("input[type=radio]")) {
                    var radio = opt.querySelector('input[type="radio"]');
                    if (radio) radio.checked = true;
                }
            });
        });

        var form = document.getElementById("settingsForm");
        if (form) {
            form.addEventListener("submit", function () {
                showToast("Ayarlar kaydediliyor...", "info");
            });
        }
    });
})();
