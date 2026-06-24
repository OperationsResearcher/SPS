/**
 * masaustu.js — komuta merkezi: sekmeler, bildirim okundu, widget sırası, karalama (localStorage)
 */
(function () {
  "use strict";

  const STORAGE_ORDER = "kokpitim_masaustu_widget_order_v1";
  // Gizleme artık kart kimliği (data-card-code) bazlı — yeni standartla uyumlu.
  // Eski (widget-id bazlı) v1 key'i bilinçli terk edildi; localStorage kişisel/geçici.
  const STORAGE_HIDDEN = "kokpitim_masaustu_card_hidden_v1";
  const SCRATCH_KEY = "kokpitim_masaustu_scratch_v1";

  const root = document.getElementById("masaustu-root");
  if (!root) return;

  const markReadTemplate = root.dataset.markReadUrlTemplate || "";

  function getCsrf() {
    const m = document.querySelector('meta[name="csrf-token"]');
    return m ? m.content : "";
  }

  function restoreWidgetOrder() {
    const sortRoot = document.getElementById("masaustu-sortable-root");
    if (!sortRoot) return;
    try {
      const order = JSON.parse(localStorage.getItem(STORAGE_ORDER) || "null");
      if (!Array.isArray(order)) return;
      order.forEach((id) => {
        const el = sortRoot.querySelector(`[data-widget-id="${id}"]`);
        if (el) sortRoot.appendChild(el);
      });
    } catch (e) {
      /* ignore */
    }
  }

  function saveWidgetOrder() {
    const sortRoot = document.getElementById("masaustu-sortable-root");
    if (!sortRoot) return;
    const ids = Array.from(sortRoot.querySelectorAll("[data-widget-id]")).map(
      (el) => el.getAttribute("data-widget-id")
    );
    try {
      localStorage.setItem(STORAGE_ORDER, JSON.stringify(ids));
    } catch (e) {
      /* ignore */
    }
  }

  function readHidden() {
    try {
      const h = JSON.parse(localStorage.getItem(STORAGE_HIDDEN) || "[]");
      return Array.isArray(h) ? h : [];
    } catch (e) {
      return [];
    }
  }

  function applyHiddenWidgets() {
    readHidden().forEach((code) => {
      const el = document.querySelector(`[data-card-code="${code}"]`);
      if (el) el.style.display = "none";
    });
  }

  // Sayfadaki tüm kartları (data-card-code) topla; etiket = kartın görünen başlığı.
  function collectCards() {
    const out = [];
    const seen = new Set();
    document.querySelectorAll("[data-card-code]").forEach((el) => {
      const code = el.getAttribute("data-card-code");
      if (!code || seen.has(code)) return;
      seen.add(code);
      // başlık: kartın kendi mc-card-title / mc-stat-label'i (torun kartınki değil)
      let label = code;
      const cands = el.querySelectorAll(".mc-card-title, .mc-stat-label, .mc-card-header h3, .mc-card-header h2");
      for (let i = 0; i < cands.length; i++) {
        if (cands[i].closest("[data-card-code]") === el) {
          label = cands[i].textContent.replace(/\s+/g, " ").trim() || code;
          break;
        }
      }
      out.push({ code: code, label: label });
    });
    return out;
  }

  function initSortable() {
    const sortRoot = document.getElementById("masaustu-sortable-root");
    if (!sortRoot || typeof Sortable === "undefined") return;
    sortRoot.classList.add("masaustu-sortable-root");
    Sortable.create(sortRoot, {
      animation: 150,
      handle: ".mc-card-header",
      ghostClass: "masaustu-sortable-ghost",
      onEnd: saveWidgetOrder,
    });
    restoreWidgetOrder();
  }

  function escAttr(s) {
    return String(s || "").replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  function openWidgetManager() {
    const cards = collectCards();
    if (!cards.length) {
      Swal.fire({ icon: "info", title: t("Kart bulunamadı"), text: t("Bu sayfada yönetilebilir kart yok.") });
      return;
    }
    const hidden = readHidden();

    const checks = cards
      .map((c) => {
        const on = !hidden.includes(c.code);
        return `<label style="display:flex;align-items:center;gap:8px;margin:6px 0;font-size:13px;cursor:pointer;">
          <input type="checkbox" data-code="${escAttr(c.code)}" ${on ? "checked" : ""}/>
          <span>${escAttr(c.label)}</span>
        </label>`;
      })
      .join("");

    Swal.fire({
      title: t("Kart yönetimi"),
      html: `<div class="text-left" style="max-height:55vh;overflow-y:auto;">
          <div style="display:flex;gap:8px;margin-bottom:10px;">
            <button type="button" id="kk-wm-all" class="mc-btn mc-btn-sm mc-btn-secondary">${t("Tümünü aç")}</button>
            <button type="button" id="kk-wm-none" class="mc-btn mc-btn-sm mc-btn-secondary">${t("Tümünü kapat")}</button>
          </div>
          ${checks}
          <p class="mc-page-subtitle" style="margin-top:12px;">${t("Kapatılan kartlar sayfadan gizlenir (yalnız bu tarayıcıda). Sıralamayı kart başlığından sürükleyerek değiştirebilirsiniz.")}</p>
        </div>`,
      showCancelButton: true,
      confirmButtonText: t("Kaydet"),
      cancelButtonText: t("İptal"),
      confirmButtonColor: "#4f46e5",
      didOpen: () => {
        const pop = Swal.getPopup();
        const boxes = pop.querySelectorAll("input[type=checkbox][data-code]");
        pop.querySelector("#kk-wm-all")?.addEventListener("click", () =>
          boxes.forEach((b) => { b.checked = true; }));
        pop.querySelector("#kk-wm-none")?.addEventListener("click", () =>
          boxes.forEach((b) => { b.checked = false; }));
      },
      preConfirm: () => {
        const nextHidden = [];
        Swal.getPopup().querySelectorAll("input[type=checkbox][data-code]").forEach((cb) => {
          if (!cb.checked) nextHidden.push(cb.getAttribute("data-code"));
        });
        return nextHidden;
      },
    }).then((r) => {
      if (!r.isConfirmed || !Array.isArray(r.value)) return;
      try {
        localStorage.setItem(STORAGE_HIDDEN, JSON.stringify(r.value));
      } catch (e) {
        /* ignore */
      }
      window.location.reload();
    });
  }

  function initMasamTabs() {
    const tabs = document.querySelectorAll(".masaustu-tab");
    if (!tabs.length) return;
    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        const name = tab.getAttribute("data-tab");
        tabs.forEach((t) => {
          t.classList.toggle("is-active", t === tab);
          t.setAttribute("aria-selected", t === tab ? "true" : "false");
        });
        document.querySelectorAll(".masaustu-tab-panel").forEach((p) => {
          p.classList.toggle("is-active", p.id === `masam-panel-${name}`);
        });
      });
    });
  }

  function markReadUrl(notifId) {
    if (markReadTemplate) return markReadTemplate.replace("888888", String(notifId));
    return `/notification/api/mark-read/${notifId}`;
  }

  function initMarkRead() {
    document.querySelectorAll(".masaustu-mark-read").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const id = btn.getAttribute("data-notif-id");
        if (!id) return;
        btn.disabled = true;
        try {
          const res = await fetch(markReadUrl(id), {
            method: "POST",
            headers: { "X-CSRFToken": getCsrf() },
            credentials: "same-origin",
          });
          const data = await res.json();
          if (data.success) {
            const row = btn.closest(".masaustu-notif-row");
            if (row) row.remove();
            Swal.fire({
              toast: true,
              position: "top-end",
              icon: "success",
              title: t("Okundu"),
              showConfirmButton: false,
              timer: 1800,
            });
          } else {
            btn.disabled = false;
            Swal.fire({ icon: "error", title: t("Hata"), text: data.message || t("İşlem başarısız") });
          }
        } catch (e) {
          btn.disabled = false;
          Swal.fire({ icon: "error", title: t("Hata"), text: String(e.message || e) });
        }
      });
    });
  }

  function initScratch() {
    const ta = document.getElementById("masaustu-scratch-body");
    const saveBtn = document.getElementById("masaustu-scratch-save");
    if (!ta || !saveBtn) return;
    try {
      ta.value = localStorage.getItem(SCRATCH_KEY) || "";
    } catch (e) {
      /* ignore */
    }
    saveBtn.addEventListener("click", () => {
      try {
        localStorage.setItem(SCRATCH_KEY, ta.value);
        Swal.fire({
          toast: true,
          position: "top-end",
          icon: "success",
          title: t("Not kaydedildi"),
          showConfirmButton: false,
          timer: 2000,
        });
      } catch (e) {
        Swal.fire({ icon: "error", title: t("Kaydedilemedi"), text: String(e) });
      }
    });
  }

  function initCalendar() {
    const calEl = document.getElementById("masaustu-calendar");
    if (!calEl || typeof FullCalendar === "undefined") return;
    const loadingEl = document.getElementById("masaustu-calendar-loading");
    const eventsUrl = root.dataset.calendarEventsUrl || "/api/calendar/events";

    const calendar = new FullCalendar.Calendar(calEl, {
      locale: "tr",
      timeZone: "Europe/Istanbul",
      initialView: "dayGridMonth",
      firstDay: 1,
      height: "auto",
      headerToolbar: {
        left: "prev,next today",
        center: "title",
        right: "dayGridMonth,timeGridWeek,timeGridDay",
      },
      buttonText: {
        today: t("Bugün"),
        month: t("Ay"),
        week: t("Hafta"),
        day: t("Gün"),
      },
      events: async function (fetchInfo, successCallback, failureCallback) {
        try {
          const url = `${eventsUrl}?start=${encodeURIComponent(fetchInfo.startStr)}&end=${encodeURIComponent(fetchInfo.endStr)}`;
          const res = await fetch(url, {
            credentials: "same-origin",
            headers: { Accept: "application/json" },
          });
          const contentType = String(res.headers.get("content-type") || "").toLowerCase();
          let data = null;
          if (contentType.includes("application/json")) {
            data = await res.json();
          } else {
            const raw = await res.text();
            throw new Error(
              res.status >= 500
                ? `${t("Sunucu hatası")} (HTTP ${res.status})`
                : `${t("Beklenmeyen yanıt")} (HTTP ${res.status}): ${raw.slice(0, 120)}`
            );
          }
          if (!res.ok || !data.success) {
            throw new Error((data && data.message) || `HTTP ${res.status}`);
          }
          if (loadingEl) loadingEl.style.display = "none";
          successCallback(data.events || []);
        } catch (err) {
          if (loadingEl) loadingEl.innerHTML = `<span style="color:#dc2626;">${t("Takvim yüklenemedi:")} ${String(err.message || err)}</span>`;
          failureCallback(err);
        }
      },
      eventClick: function (info) {
        const u = info.event.url || (info.event.extendedProps && info.event.extendedProps.url);
        if (u) {
          info.jsEvent.preventDefault();
          window.location.href = u;
        }
      },
      eventTimeFormat: {
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
      },
    });

    calendar.render();
  }

  applyHiddenWidgets();
  initMasamTabs();
  initSocketRefresh();
  initMarkRead();
  initScratch();
  initCalendar();
  initSortable();
  initMorningSummary();

  document.getElementById("masaustu-widget-manage")?.addEventListener("click", openWidgetManager);

  function initSocketRefresh() {
    if (typeof io === "undefined") return;
    const socket = io({ transports: ["websocket", "polling"] });
    socket.on("morning_summary_refresh", () => {
      const widget = document.querySelector("[data-widget-id='morning-summary']");
      if (!widget) return;
      const url = widget.dataset.morningUrl;
      const body = document.getElementById("morning-summary-body");
      if (!url || !body) return;
      fetch(url).then(r => r.json()).then(res => {
        if (res.success) {
          const badge = document.querySelector("[data-morning-badge]");
          if (badge) badge.textContent = res.data.counts.kpis_critical + res.data.counts.activities_overdue;
        }
      }).catch(() => {});
    });
  }

  function initMorningSummary() {
    const widget = document.querySelector("[data-widget-id='morning-summary']");
    if (!widget) return;
    const url = widget.dataset.morningUrl;
    const body = document.getElementById("morning-summary-body");
    const dateEl = document.getElementById("morning-summary-date");
    if (!url || !body) return;

    fetch(url)
      .then(r => r.json())
      .then(res => {
        if (!res.success) { body.innerHTML = `<p style="color:#ef4444">${t("Özet yüklenemedi.")}</p>`; return; }
        const d = res.data;
        if (dateEl) dateEl.textContent = d.date || "";

        const statusColor = d.counts.kpis_critical > 0 || d.counts.activities_overdue > 0 || d.counts.projects_overdue > 0
          ? "#ef4444" : "#10b981";

        let html = `<div style="padding:8px 0 14px;">
          <p style="margin:0 0 14px; font-size:13px; font-weight:600; color:${statusColor};">
            <i class="fas fa-${statusColor === '#ef4444' ? 'triangle-exclamation' : 'circle-check'}"></i>
            ${d.summary_text}
          </p>
          <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:10px; margin-bottom:16px;">
            <div style="background:#fef2f2; border-radius:8px; padding:10px; text-align:center;">
              <div style="font-size:22px; font-weight:700; color:#ef4444;">${d.counts.kpis_critical}</div>
              <div style="font-size:11px; color:#64748b;">${t("Kritik KPI")}</div>
            </div>
            <div style="background:#fff7ed; border-radius:8px; padding:10px; text-align:center;">
              <div style="font-size:22px; font-weight:700; color:#f59e0b;">${d.counts.activities_overdue}</div>
              <div style="font-size:11px; color:#64748b;">${t("Geciken Faaliyet")}</div>
            </div>
            <div style="background:#f0fdf4; border-radius:8px; padding:10px; text-align:center;">
              <div style="font-size:22px; font-weight:700; color:#10b981;">${d.counts.activities_upcoming}</div>
              <div style="font-size:11px; color:#64748b;">${t("Bu Hafta Faaliyet")}</div>
            </div>
            <div style="background:#eff6ff; border-radius:8px; padding:10px; text-align:center;">
              <div style="font-size:22px; font-weight:700; color:#3b82f6;">${d.counts.projects_overdue}</div>
              <div style="font-size:11px; color:#64748b;">${t("Geciken Proje")}</div>
            </div>
          </div>`;

        if (d.kpis_below_target.length > 0) {
          html += `<div style="margin-bottom:12px;">
            <p style="font-size:12px; font-weight:600; color:#ef4444; margin:0 0 6px;">
              <i class="fas fa-chart-line-down"></i> ${t("Hedef Altı KPI'lar")}
            </p>
            <ul style="margin:0; padding-left:16px; font-size:12px; color:#475569;">`;
          d.kpis_below_target.forEach(k => {
            html += `<li><strong>${k.kpi_name}</strong> (${k.process_name}) — ${t("Gerçekleşen:")} ${k.actual} / ${t("Hedef:")} ${k.target} <span style="color:#ef4444;">(${k.ratio_pct}%)</span></li>`;
          });
          html += `</ul></div>`;
        }

        if (d.overdue_activities.length > 0) {
          html += `<div style="margin-bottom:12px;">
            <p style="font-size:12px; font-weight:600; color:#f59e0b; margin:0 0 6px;">
              <i class="fas fa-clock"></i> ${t("Geciken Faaliyetler")}
            </p>
            <ul style="margin:0; padding-left:16px; font-size:12px; color:#475569;">`;
          d.overdue_activities.forEach(a => {
            html += `<li>${a.name} — <span style="color:#ef4444;">${a.days_overdue} ${t("gün gecikti")}</span></li>`;
          });
          html += `</ul></div>`;
        }

        if (d.overdue_projects.length > 0) {
          html += `<div>
            <p style="font-size:12px; font-weight:600; color:#3b82f6; margin:0 0 6px;">
              <i class="fas fa-diagram-project"></i> ${t("Geciken Projeler")}
            </p>
            <ul style="margin:0; padding-left:16px; font-size:12px; color:#475569;">`;
          d.overdue_projects.forEach(p => {
            html += `<li>${p.name} — <span style="color:#ef4444;">${p.days_overdue} ${t("gün gecikti")}</span></li>`;
          });
          html += `</ul></div>`;
        }

        html += `</div>`;
        body.innerHTML = html;
      })
      .catch(() => { body.innerHTML = `<p style="color:#94a3b8; font-size:12px;">${t("Özet yüklenemedi.")}</p>`; });
  }

  // ── KOE Yapı-Danışmanı: opsiyonel LLM zenginleştirme (lazy, butonla) ──────
  (function initKoeAi() {
    const box = document.getElementById("koe-danisman-box");
    const btn = document.getElementById("koe-ai-btn");
    if (!box || !btn) return;
    const url = box.dataset.aiUrl;
    const label = btn.querySelector("[data-koe-ai-label]");

    function escapeHtmlKoe(s) {
      return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }

    btn.addEventListener("click", async () => {
      if (btn.disabled) return;
      btn.disabled = true;
      const original = label.textContent;
      label.textContent = t("Hazırlanıyor…");
      try {
        const res = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrf() },
          credentials: "same-origin",
        });
        const d = await res.json();
        if (!d.success) {
          label.textContent = original;
          btn.disabled = false;
          Swal.fire({ icon: "error", title: t("Hata"), text: d.message || t("AI danışman çağrılamadı.") });
          return;
        }
        const anlatiEl = box.querySelector("[data-koe-anlati]");
        if (anlatiEl && d.anlati) {
          anlatiEl.innerHTML =
            '<i class="fas fa-robot" style="color:#10b981; margin-right:6px;"></i>' +
            escapeHtmlKoe(d.anlati);
        }
        const oneriEls = box.querySelectorAll("[data-koe-oneri]");
        (d.oncelikler || []).forEach((o, i) => {
          if (oneriEls[i] && o.oneri) oneriEls[i].textContent = " — " + o.oneri;
        });
        if (d.kaynak === "llm") {
          label.textContent = "✓ " + t("AI ile zenginleştirildi");
          btn.style.color = "#94a3b8";
        } else {
          label.textContent = original;
          btn.disabled = false;
          Swal.fire({
            toast: true, position: "top-end", icon: "info",
            title: t("AI sağlayıcı yapılandırılmamış; mevcut öneriler gösteriliyor."),
            showConfirmButton: false, timer: 3500, timerProgressBar: true,
          });
        }
      } catch (e) {
        label.textContent = original;
        btn.disabled = false;
        Swal.fire({ icon: "error", title: t("Hata"), text: String(e.message || e) });
      }
    });
  })();
})();
