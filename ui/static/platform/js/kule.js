/* Kule — yardımcı sistem runtime
   Tanım: docs/KULE-TANIM.md
   Bağımlılık: Driver.js (CDN: driver.js.org) */

(function (global) {
  "use strict";

  const API_BASE = "/api/kule/tour";

  const KULE_SVG_URL = (document.querySelector('meta[name="kule-svg-url"]') || {}).content
    || "/m/platform/img/kule.svg";

  let _svgMarkup = null;
  let _currentTour = null;
  let _driverInstance = null;

  // ---- Yardımcılar ----------------------------------------------------------

  async function fetchSvg() {
    if (_svgMarkup) return _svgMarkup;
    try {
      const res = await fetch(KULE_SVG_URL, { credentials: "same-origin" });
      _svgMarkup = await res.text();
    } catch (e) {
      _svgMarkup = '<i class="fas fa-broadcast-tower"></i>';
    }
    return _svgMarkup;
  }

  async function api(method, path, body) {
    const opts = {
      method,
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
    };
    if (body) opts.body = JSON.stringify(body);
    try {
      const res = await fetch(API_BASE + path, opts);
      return await res.json();
    } catch (e) {
      console.warn("[kule] api error", e);
      return { success: false };
    }
  }

  // ---- FAB (sağ alt sabit simge) -------------------------------------------

  async function ensureFab(tourKey) {
    let fab = document.getElementById("kule-fab");
    if (fab) {
      fab.dataset.tourKey = tourKey || "";
      return fab;
    }
    fab = document.createElement("button");
    fab.id = "kule-fab";
    fab.className = "kule-fab";
    fab.type = "button";
    fab.title = "Kule — sayfa yardımı";
    fab.setAttribute("aria-label", "Kule yardımcısını aç");
    fab.dataset.tourKey = tourKey || "";
    fab.innerHTML = await fetchSvg();
    fab.addEventListener("click", onFabClick);
    document.body.appendChild(fab);
    return fab;
  }

  async function onFabClick() {
    const fab = document.getElementById("kule-fab");
    const tourKey = fab && fab.dataset.tourKey;
    if (!tourKey) {
      showStandaloneMessage(
        "Bu sayfa henüz turlu değil",
        "Bu sayfa için Kule turu henüz hazırlanmadı. Stratejik Planlama, Süreçler veya Masaüstü gibi sayfalarda beni dene."
      );
      return;
    }
    // FAB'a tıklayınca turu sıfırla ve yeniden başlat
    const r1 = await api("POST", `/${tourKey}/restart`);
    if (!r1 || !r1.success) {
      showStandaloneMessage(
        "Tur başlatılamadı",
        "Sunucuya ulaşılamadı. Sayfayı yenileyip tekrar dene."
      );
      return;
    }
    await loadAndRun(tourKey, /* force */ true);
  }

  async function showStandaloneMessage(title, body) {
    const old = document.getElementById("kule-welcome");
    if (old) old.remove();
    const svg = await fetchSvg();
    const el = document.createElement("div");
    el.id = "kule-welcome";
    el.className = "kule-welcome";
    el.innerHTML = `
      <div class="kule-welcome-header">
        <div class="kule-welcome-avatar">${svg}</div>
        <div>
          <div class="kule-welcome-prefix">📡 Kule'den</div>
          <div class="kule-welcome-title">${escapeHtml(title)}</div>
        </div>
      </div>
      <div class="kule-welcome-body">${renderBody(body)}</div>
      <div class="kule-welcome-actions">
        <button type="button" class="kule-btn kule-btn-primary" data-kule-action="close">Tamam</button>
      </div>
    `;
    document.body.appendChild(el);
    el.querySelector('[data-kule-action="close"]').addEventListener("click", () => el.remove());
  }

  // ---- Karşılama baloncuğu --------------------------------------------------

  async function showWelcome(tour) {
    // Var olanı kaldır
    const old = document.getElementById("kule-welcome");
    if (old) old.remove();

    const w = tour.welcome || {};
    const svg = await fetchSvg();

    const el = document.createElement("div");
    el.id = "kule-welcome";
    el.className = "kule-welcome";
    el.innerHTML = `
      <div class="kule-welcome-header">
        <div class="kule-welcome-avatar">${svg}</div>
        <div>
          <div class="kule-welcome-prefix">📡 Kule'den</div>
          <div class="kule-welcome-title">${escapeHtml(w.title || tour.title || "Hoş geldin")}</div>
        </div>
      </div>
      <div class="kule-welcome-body">${renderBody(w.body || "")}</div>
      <div class="kule-welcome-actions">
        <button type="button" class="kule-btn kule-btn-secondary" data-kule-action="dismiss">
          ${escapeHtml(w.cta_secondary || "Şimdi değil")}
        </button>
        <button type="button" class="kule-btn kule-btn-primary" data-kule-action="start">
          ${escapeHtml(w.cta_primary || "Başlayalım")}
        </button>
      </div>
    `;
    document.body.appendChild(el);

    el.querySelector('[data-kule-action="start"]').addEventListener("click", () => {
      el.remove();
      startSteps(tour);
    });
    el.querySelector('[data-kule-action="dismiss"]').addEventListener("click", async () => {
      el.remove();
      await api("POST", `/${tour.key}/dismiss`);
    });
  }

  // ---- Driver.js ile adım turu ---------------------------------------------

  function startSteps(tour) {
    // Driver.js IIFE bundle global = window.driver.js.driver
    const driverFn =
      (global.driver && global.driver.js && global.driver.js.driver) ||
      (global.driver && global.driver.driver) ||
      (typeof global.driver === "function" ? global.driver : null);
    if (!driverFn) {
      console.warn("[kule] driver.js yüklü değil — global.driver:", global.driver);
      showStandaloneMessage(
        "Tur kütüphanesi yüklenemedi",
        "Driver.js CDN'i engellenmiş olabilir. İnternet bağlantını veya ağ engellerini kontrol et."
      );
      return;
    }
    const steps = (tour.steps || []).map((s) => ({
      element: s.target,
      popover: {
        title: s.title || "",
        description: renderBody(s.body || ""),
        side: s.placement || "bottom",
        align: "start",
      },
    }));

    if (steps.length === 0) return;

    _driverInstance = driverFn({
      showProgress: true,
      animate: true,
      smoothScroll: true,
      allowClose: true,
      stagePadding: 6,
      popoverClass: "kule-theme",
      nextBtnText: "Devam →",
      prevBtnText: "← Geri",
      doneBtnText: "Tamam",
      progressText: "{{current}} / {{total}}",
      steps: steps,
      onDestroyed: async () => {
        await api("POST", `/${tour.key}/complete`);
        if (tour.finale && tour.finale.body) {
          showFinale(tour);
        }
      },
    });
    _driverInstance.drive();
  }

  async function showFinale(tour) {
    const f = tour.finale || {};
    const svg = await fetchSvg();
    const el = document.createElement("div");
    el.id = "kule-welcome";
    el.className = "kule-welcome";
    el.innerHTML = `
      <div class="kule-welcome-header">
        <div class="kule-welcome-avatar">${svg}</div>
        <div>
          <div class="kule-welcome-prefix">📡 Kule'den</div>
          <div class="kule-welcome-title">${escapeHtml(f.title || "Hazırsın")}</div>
        </div>
      </div>
      <div class="kule-welcome-body">${renderBody(f.body || "")}</div>
      <div class="kule-welcome-actions">
        <button type="button" class="kule-btn kule-btn-primary" data-kule-action="close">Tamam</button>
      </div>
    `;
    document.body.appendChild(el);
    el.querySelector('[data-kule-action="close"]').addEventListener("click", () => el.remove());
    setTimeout(() => { if (el.parentNode) el.remove(); }, 8000);
  }

  // ---- Yükle ve çalıştır ----------------------------------------------------

  async function loadAndRun(tourKey, force) {
    const res = await api("GET", `/${tourKey}`);
    if (!res || !res.success) {
      console.info(`[kule] tur yüklenemedi: ${tourKey}`, res);
      if (force) {
        showStandaloneMessage(
          "Tur yüklenemedi",
          (res && res.message) || "Sunucudan tur tanımı alınamadı."
        );
      }
      return;
    }
    const tour = res.tour;
    const progress = res.progress || {};
    _currentTour = tour;

    // İlk gösterim ise seen_count artır
    api("POST", `/${tourKey}/seen`);

    const shouldShow = force ||
      (tour.auto_show && progress.status === "pending");

    if (shouldShow) {
      if (tour.welcome && (tour.welcome.title || tour.welcome.body)) {
        await showWelcome(tour);
      } else {
        startSteps(tour);
      }
    }
  }

  function escapeHtml(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  // Hafif markdown: **bold**, paragraf (\n\n), satır sonu (\n) ve madde imi (• yada -)
  function renderBody(s) {
    if (!s) return "";
    let escaped = escapeHtml(s);
    escaped = escaped.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    // Madde işaretli satırları <li> içine al
    const lines = escaped.split("\n");
    const out = [];
    let inList = false;
    for (const raw of lines) {
      const line = raw.trim();
      const isBullet = /^[•\-]\s+/.test(line);
      if (isBullet) {
        if (!inList) { out.push("<ul style='margin:6px 0 6px 18px; padding:0;'>"); inList = true; }
        out.push("<li>" + line.replace(/^[•\-]\s+/, "") + "</li>");
      } else {
        if (inList) { out.push("</ul>"); inList = false; }
        out.push(line ? "<p style='margin:6px 0;'>" + line + "</p>" : "");
      }
    }
    if (inList) out.push("</ul>");
    return out.join("");
  }

  // ---- Public API -----------------------------------------------------------

  const Kule = {
    async init(opts) {
      opts = opts || {};
      await ensureFab(opts.tourKey);
      if (opts.tourKey) {
        // Sayfa açılışta otomatik yükleme
        await loadAndRun(opts.tourKey, false);
      }
    },
    start(tourKey) { return loadAndRun(tourKey, true); },
    restart(tourKey) {
      return api("POST", `/${tourKey}/restart`).then(() => loadAndRun(tourKey, true));
    },
  };

  global.Kule = Kule;
})(window);
