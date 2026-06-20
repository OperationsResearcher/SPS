/**
 * program_gantt.js — Portföy program zaman çizelgesi (L3 eksik tamamlama)
 *
 * Tüm projeleri tek Gantt'ta gösterir (her proje bir bar). Frappe-Gantt 0.6.1.
 * Veri: #program-gantt-card[data-program] = [{id,name,start,end,score}].
 * Kural: Jinja {{ }} YASAK → data-*.
 */
(function () {
  "use strict";

  const card = document.getElementById("program-gantt-card");
  const svg = document.getElementById("program-gantt");
  const emptyEl = document.getElementById("program-gantt-empty");
  if (!card || !svg) return;

  let projects = [];
  try { projects = JSON.parse(card.dataset.program || "[]"); } catch (_e) { projects = []; }

  if (!projects.length) {
    if (emptyEl) emptyEl.style.display = "block";
    svg.style.display = "none";
    return;
  }
  if (typeof Gantt === "undefined") {
    if (emptyEl) { emptyEl.style.display = "block"; emptyEl.textContent = "Gantt bileşeni yüklenemedi."; }
    return;
  }

  // skor → renk sınıfı (yüksek skor = stratejik öncelik)
  function scoreClass(score) {
    if (score >= 50) return "pg-high";
    if (score >= 30) return "pg-mid";
    return "pg-low";
  }

  const tasks = projects.map((p) => ({
    id: "proj-" + p.id,
    name: p.name + "  (skor " + (p.score || 0) + ")",
    start: p.start,
    end: p.end,
    progress: 0,
    custom_class: scoreClass(p.score || 0),
  }));

  try {
    const g = new Gantt(svg, tasks, {
      view_mode: "Month",
      bar_height: 18,
      padding: 14,
      popup_trigger: "mouseover",
      custom_popup_html: function (task) {
        return '<div style="padding:6px 10px;font-size:12px;">' +
          '<strong>' + task.name + '</strong><br>' +
          task._start.toLocaleDateString("tr-TR") + " – " +
          task._end.toLocaleDateString("tr-TR") + "</div>";
      },
    });
    void g;
  } catch (e) {
    if (emptyEl) { emptyEl.style.display = "block"; emptyEl.textContent = "Çizelge oluşturulamadı: " + e.message; }
  }

  // Skor renkleri (Frappe bar .bar-progress / .bar). Basit renk override.
  const style = document.createElement("style");
  style.textContent =
    "#program-gantt .pg-high .bar{fill:#16a34a;} " +
    "#program-gantt .pg-mid .bar{fill:#f59e0b;} " +
    "#program-gantt .pg-low .bar{fill:#94a3b8;}";
  document.head.appendChild(style);
})();
