# -*- coding: utf-8 -*-
"""Şablon `templates/projects/_tool_info_modal.html` içinden veri bloğunu alıp `tool_info_modal.js` üretir."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
text = (root / "templates/projects/_tool_info_modal.html").read_text(encoding="utf-8")
start = text.index("const toolInfoData =")
end = text.index("function showToolInfo", start)
data = text[start:end].replace("const toolInfoData", "var TOOL_INFO_DATA", 1).strip()

footer = r"""
function closeToolInfoModal() {
  var overlay = document.getElementById("tool-info-overlay");
  if (!overlay) return;
  overlay.classList.remove("open");
  overlay.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
}

function showToolInfo(toolKey) {
  var tool = TOOL_INFO_DATA[toolKey];
  if (!tool) return;
  var overlay = document.getElementById("tool-info-overlay");
  var titleEl = document.getElementById("toolInfoTitle");
  var bodyEl = document.getElementById("toolInfoBody");
  if (!overlay || !titleEl || !bodyEl) return;
  titleEl.innerHTML = '<i class="' + tool.icon + '"></i><span>' + tool.title + "</span>";
  var sectionsHtml = "";
  var colors = {
    primary: "#4f46e5",
    danger: "#dc2626",
    warning: "#d97706",
    success: "#16a34a",
    info: "#0284c7",
    secondary: "#64748b",
  };
  var hc = colors[tool.color] || colors.primary;
  tool.sections.forEach(function (section) {
    sectionsHtml +=
      '<div class="tool-info-section"><h5 class="tool-info-section-title" style="color:' +
      hc +
      ';"><i class="fas fa-chevron-right"></i>' +
      section.heading +
      '</h5><div class="tool-info-body-inner">' +
      section.content +
      "</div></div>";
  });
  bodyEl.innerHTML = sectionsHtml;
  overlay.classList.add("open");
  overlay.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
}

document.addEventListener("DOMContentLoaded", function () {
  var overlay = document.getElementById("tool-info-overlay");
  if (!overlay) return;
  overlay.addEventListener("click", function (e) {
    if (e.target === overlay) closeToolInfoModal();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && overlay.classList.contains("open")) closeToolInfoModal();
  });
});
"""

out = '(function () {\n"use strict";\n' + data + "\n" + footer + "\n})();\n"
target = root / "ui/static/platform/js/tool_info_modal.js"
target.write_text(out, encoding="utf-8")
print("Wrote", target, "bytes", len(out))
