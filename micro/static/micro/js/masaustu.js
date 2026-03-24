/**
 * masaustu.js — komuta merkezi: sekmeler, bildirim okundu, widget sırası, karalama (localStorage)
 */
(function () {
  "use strict";

  const STORAGE_ORDER = "kokpitim_masaustu_widget_order_v1";
  const STORAGE_HIDDEN = "kokpitim_masaustu_widget_hidden_v1";
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

  function applyHiddenWidgets() {
    let hidden = [];
    try {
      hidden = JSON.parse(localStorage.getItem(STORAGE_HIDDEN) || "[]");
    } catch (e) {
      hidden = [];
    }
    if (!Array.isArray(hidden)) return;
    hidden.forEach((id) => {
      const el = document.querySelector(`[data-widget-id="${id}"]`);
      if (el) el.style.display = "none";
    });
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

  const WIDGET_LABELS = {
    calendar: "Takvimim",
    quick: "Hızlı işlemler",
    masam: "Benim Masam",
    alerts: "Dikkat (aylık PG)",
    scratch: "Karalama defteri",
    lists: "PG & faaliyet listeleri",
    surecpg: "Süreç PG",
    notif: "Bildirimler",
    strat: "Stratejik hedefler",
  };

  function openWidgetManager() {
    const ids = Object.keys(WIDGET_LABELS);
    let hidden = [];
    try {
      hidden = JSON.parse(localStorage.getItem(STORAGE_HIDDEN) || "[]");
    } catch (e) {
      hidden = [];
    }
    if (!Array.isArray(hidden)) hidden = [];

    const checks = ids
      .map((id) => {
        const on = !hidden.includes(id);
        return `<label style="display:flex;align-items:center;gap:8px;margin:6px 0;font-size:13px;">
          <input type="checkbox" data-wid="${id}" ${on ? "checked" : ""}/> ${WIDGET_LABELS[id] || id}
        </label>`;
      })
      .join("");

    Swal.fire({
      title: "Widget yönetimi",
      html: `<div class="text-left">${checks}<p class="mc-page-subtitle" style="margin-top:12px;">Gizlenen kartlar sayfadan kaldırılır. Sıralamayı kart başlığından sürükleyerek değiştirebilirsiniz.</p></div>`,
      showCancelButton: true,
      confirmButtonText: "Kaydet",
      cancelButtonText: "İptal",
      confirmButtonColor: "#4f46e5",
      preConfirm: () => {
        const nextHidden = [];
        Swal.getPopup().querySelectorAll("input[type=checkbox][data-wid]").forEach((cb) => {
          if (!cb.checked) nextHidden.push(cb.getAttribute("data-wid"));
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
    return `/bildirim/api/mark-read/${notifId}`;
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
              title: "Okundu",
              showConfirmButton: false,
              timer: 1800,
            });
          } else {
            btn.disabled = false;
            Swal.fire({ icon: "error", title: "Hata", text: data.message || "İşlem başarısız" });
          }
        } catch (e) {
          btn.disabled = false;
          Swal.fire({ icon: "error", title: "Hata", text: String(e.message || e) });
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
          title: "Not kaydedildi",
          showConfirmButton: false,
          timer: 2000,
        });
      } catch (e) {
        Swal.fire({ icon: "error", title: "Kaydedilemedi", text: String(e) });
      }
    });
  }

  function initCalendar() {
    if (typeof KokpitimCalendarQuickCreate === "undefined") return;
    KokpitimCalendarQuickCreate.boot({
      root,
      calendarId: "masaustu-calendar",
      loadingId: "masaustu-calendar-loading",
    });
  }

  applyHiddenWidgets();
  initMasamTabs();
  initMarkRead();
  initScratch();
  initCalendar();
  initSortable();

  document.getElementById("masaustu-widget-manage")?.addEventListener("click", openWidgetManager);
})();
