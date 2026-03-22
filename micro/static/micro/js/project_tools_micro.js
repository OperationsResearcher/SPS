/**
 * Proje araçları (Micro) — modal yardımcıları, bilgi penceresi, toast yedekleri.
 * window.toolInfoData → project_tool_info_data.js
 */
(function () {
  "use strict";

  if (typeof window.showToast !== "function") {
    window.showToast = function (type, msg, title) {
      if (typeof Swal !== "undefined") {
        Swal.fire({
          icon:
            type === "error"
              ? "error"
              : type === "success"
                ? "success"
                : "info",
          title: title || "",
          text: msg || "",
          toast: true,
          position: "top-end",
          showConfirmButton: false,
          timer: 3800,
        });
      } else {
        alert((title ? title + ": " : "") + (msg || ""));
      }
    };
  }

  window.mcPtModalOpen = function (id) {
    var el = document.getElementById(id);
    if (!el) return;
    el.classList.remove("hidden");
    el.setAttribute("aria-hidden", "false");
    document.body.classList.add("overflow-hidden");
  };

  window.mcPtModalClose = function (id) {
    var el = document.getElementById(id);
    if (!el) return;
    el.classList.add("hidden");
    el.setAttribute("aria-hidden", "true");
    document.body.classList.remove("overflow-hidden");
  };

  var HEADING_COLORS = {
    primary: "text-indigo-600 dark:text-indigo-400",
    danger: "text-rose-600 dark:text-rose-400",
    warning: "text-amber-600 dark:text-amber-400",
    success: "text-emerald-600 dark:text-emerald-400",
    info: "text-sky-600 dark:text-sky-400",
    secondary: "text-slate-600 dark:text-slate-400",
  };

  window.closeToolInfoModal = function () {
    window.mcPtModalClose("microToolInfoModal");
  };

  window.showToolInfo = function (toolKey) {
    var data = window.toolInfoData || {};
    var tool = data[toolKey];
    if (!tool) return;
    var titleEl = document.getElementById("toolInfoTitle");
    var bodyEl = document.getElementById("toolInfoBody");
    if (!titleEl || !bodyEl) return;
    titleEl.innerHTML =
      '<i class="' + tool.icon + ' me-2"></i>' + (tool.title || "");
    var hc = HEADING_COLORS[tool.color] || HEADING_COLORS.primary;
    var html = "";
    (tool.sections || []).forEach(function (section) {
      html += '<div class="mb-6 last:mb-0">';
      html +=
        '<h4 class="font-semibold ' +
        hc +
        ' mb-2 text-base"><i class="fas fa-chevron-right me-2 text-xs opacity-70"></i>' +
        section.heading +
        "</h4>";
      html +=
        '<div class="tool-info-body text-sm text-slate-700 dark:text-slate-300">' +
        section.content +
        "</div>";
      html += "</div>";
    });
    bodyEl.innerHTML = html;
    window.mcPtModalOpen("microToolInfoModal");
  };
})();
