/**
 * command_palette.js — Ctrl+K küresel komut paleti
 * - Statik sayfa linkleri (sidebar'dan) + dinamik küresel arama (/api/search)
 * - Klavye gezimi: ↑ ↓ Enter Esc
 * - Son ziyaret edilenler localStorage'da tutulur (B2 ile uyumlu)
 */
(function () {
  "use strict";

  const overlay = document.getElementById("cmd-palette-overlay");
  const input   = document.getElementById("cmd-palette-input");
  const list    = document.getElementById("cmd-palette-list");
  if (!overlay || !input || !list) return;

  const RECENT_KEY = "kk_recent_pages";
  const MAX_RECENT = 8;

  // Statik sayfa katalogu — kullanıcı tıklayınca atlayacak
  const STATIC_PAGES = [
    { title: t("Masaüstü"),                url: "/desktop-launcher", icon: "fa-home",                 group: t("Sayfa") },
    { title: t("Stratejik Planlama"),      url: "/sp",                icon: "fa-bullseye",             group: t("Sayfa") },
    { title: t("Yönetici Paneli"),         url: "/sp/exec-dashboard", icon: "fa-tachometer-alt",       group: t("Sayfa") },
    { title: t("X-Matrix"),                url: "/sp/xmatrix",        icon: "fa-th-large",             group: t("Sayfa") },
    { title: t("Girişimler"),              url: "/sp/initiatives",    icon: "fa-rocket",               group: t("Sayfa") },
    { title: t("Senaryolar"),              url: "/sp/scenarios",      icon: "fa-code-branch",          group: t("Sayfa") },
    { title: t("Çeyreklik Değerlendirme"), url: "/sp/ceyreklik-review", icon: "fa-calendar-check",     group: t("Sayfa") },
    { title: t("Yeniden Planlama Tetikleyicileri"), url: "/sp/replan-triggers", icon: "fa-bell",       group: t("Sayfa") },
    { title: t("Mavi Okyanus"),            url: "/sp/blue-ocean",     icon: "fa-water",                group: t("Sayfa") },
    { title: t("VRIO"),                    url: "/sp/vrio",           icon: "fa-shield-halved",        group: t("Sayfa") },
    { title: t("Strateji Haritası"),       url: "/sp/strategy-map",   icon: "fa-diagram-project",   group: t("Sayfa") },
    { title: t("SP Menüsü"),               url: "/sp/menu",           icon: "fa-th",                   group: t("Sayfa") },
    { title: t("Süreç Yönetimi"),          url: "/process",           icon: "fa-sitemap",              group: t("Sayfa") },
    { title: t("Proje Yönetimi"),          url: "/project",           icon: "fa-folder-open",          group: t("Sayfa") },
    { title: t("Proje Portföyü"),          url: "/project/portfolio", icon: "fa-layer-group",          group: t("Sayfa") },
    { title: t("Proje Gantt"),             url: "/project/gantt",     icon: "fa-stream",               group: t("Sayfa") },
    { title: t("Proje Kanban"),            url: "/project/kanban",    icon: "fa-columns",              group: t("Sayfa") },
    { title: t("K-Radar Araçları"),        url: "/k-radar/ks",        icon: "fa-magnifying-glass-chart", group: t("Sayfa") },
    { title: t("K-Radar"),                 url: "/reports",          icon: "fa-satellite-dish",       group: t("Sayfa") },
    { title: t("Performans Analitiği"),    url: "/analysis",          icon: "fa-chart-bar",            group: t("Sayfa") },
    { title: t("Bireysel Karne"),          url: "/individual/scorecard", icon: "fa-user-check",        group: t("Sayfa") },
    { title: t("Bildirimler"),             url: "/notification",      icon: "fa-bell",                 group: t("Sayfa") },
    { title: t("Kurum Ayarları"),          url: "/organization/settings", icon: "fa-building",          group: t("Sayfa") },
    { title: t("Ayarlar"),                 url: "/settings",          icon: "fa-cog",                  group: t("Sayfa") },
    { title: t("Profil"),                  url: "/profile",           icon: "fa-user",                 group: t("Sayfa") },
    { title: t("Yönetim Paneli"),          url: "/admin/yonetim",     icon: "fa-user-shield",          group: t("Sayfa") },
    { title: t("Kullanıcılar"),            url: "/admin/users",       icon: "fa-users",                group: t("Sayfa") },
  ];

  let activeIdx = 0;
  let currentItems = [];
  let pendingFetch = null;
  let fetchTimer = null;

  function recent() {
    try { return JSON.parse(localStorage.getItem(RECENT_KEY) || "[]"); }
    catch (e) { return []; }
  }

  function recordRecent(item) {
    try {
      const arr = recent().filter(r => r.url !== item.url);
      arr.unshift({ title: item.title, url: item.url, icon: item.icon, group: item.group || item.kind_label });
      localStorage.setItem(RECENT_KEY, JSON.stringify(arr.slice(0, MAX_RECENT)));
    } catch (e) {}
  }

  function open() {
    overlay.style.display = "flex";
    input.value = "";
    activeIdx = 0;
    render([]);
    setTimeout(() => input.focus(), 30);
  }
  function close() {
    overlay.style.display = "none";
    input.value = "";
    list.innerHTML = "";
  }

  function escHtml(s) {
    return String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"})[c]);
  }
  function highlight(text, q) {
    if (!q) return escHtml(text);
    const re = new RegExp("(" + q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig");
    return escHtml(text).replace(re, '<mark style="background:#fef08a; color:#0f172a; padding:0 2px; border-radius:2px;">$1</mark>');
  }

  function render(items, q) {
    currentItems = items;
    if (!items.length) {
      list.innerHTML = `<div style="padding:24px; text-align:center; color:#94a3b8; font-size:13px;">${q ? t("Sonuç bulunamadı.") : t("Yazmaya başlayın…")}</div>`;
      return;
    }
    let lastGroup = "";
    list.innerHTML = items.map((it, i) => {
      const gh = (it.group !== lastGroup) ? `<div style="font-size:10.5px; color:#94a3b8; text-transform:uppercase; font-weight:600; padding:8px 12px 4px; letter-spacing:0.05em;">${escHtml(it.group)}</div>` : "";
      lastGroup = it.group;
      const active = i === activeIdx;
      return gh + `
        <div class="cmd-palette-row" data-idx="${i}" data-url="${escHtml(it.url)}"
             style="display:flex; align-items:center; gap:10px; padding:8px 12px; border-radius:6px; cursor:pointer; ${active ? 'background:#eef2ff;' : ''}">
          <i class="fas ${escHtml(it.icon)} fa-fw" style="color:${active ? '#4338ca' : '#64748b'}; width:18px;"></i>
          <div style="flex:1; min-width:0;">
            <div style="font-size:13.5px; color:#0f172a; ${active ? 'font-weight:600;' : ''}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${highlight(it.title, q)}</div>
            ${it.subtitle ? `<div style="font-size:11.5px; color:#94a3b8; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${escHtml(it.subtitle)}</div>` : ""}
          </div>
          ${active ? '<i class="fas fa-arrow-right" style="color:#4338ca; font-size:11px;"></i>' : ""}
        </div>`;
    }).join("");
  }

  function getInitialItems() {
    const items = [];
    const rec = recent();
    if (rec.length) {
      rec.slice(0, 5).forEach(r => items.push({ ...r, group: t("Son ziyaret edilenler") }));
    }
    items.push(...STATIC_PAGES.slice(0, 12));
    return items;
  }

  function filterStatic(q) {
    const ql = q.toLowerCase();
    return STATIC_PAGES.filter(p =>
      p.title.toLowerCase().includes(ql) ||
      p.url.toLowerCase().includes(ql)
    );
  }

  async function doSearch(q) {
    activeIdx = 0;
    if (!q) { render(getInitialItems(), ""); return; }

    // Anında statik filtre göster
    const staticHits = filterStatic(q);
    render(staticHits, q);

    if (q.length < 2) return;
    if (pendingFetch) pendingFetch.abort();
    const ctrl = new AbortController(); pendingFetch = ctrl;
    try {
      const res = await fetch("/api/search?q=" + encodeURIComponent(q), { signal: ctrl.signal });
      const j = await res.json();
      if (!j.success) return;
      const remote = j.items || [];
      const allItems = [];
      if (staticHits.length) {
        staticHits.forEach(s => allItems.push(s));
      }
      remote.forEach(r => allItems.push({ ...r, group: r.kind_label }));
      activeIdx = 0;
      render(allItems, q);
    } catch (e) { /* abort sessiz */ }
  }

  function goActive() {
    const it = currentItems[activeIdx];
    if (!it || !it.url) return;
    recordRecent(it);
    close();
    window.location.href = it.url;
  }

  // ── Olaylar ────────────────────────────────────────────────────────────
  // Topbar arama butonu (2026-07-15: base.html'de inline onclick="" idi —
  // sahte KeyboardEvent gönderiyordu; artık doğrudan open() çağırıyor).
  const searchBtn = document.querySelector(".topbar-search-btn");
  if (searchBtn) {
    searchBtn.addEventListener("click", () => {
      if (overlay.style.display === "flex") close(); else open();
    });
  }

  document.addEventListener("keydown", (e) => {
    // Ctrl+K (veya Cmd+K)
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      if (overlay.style.display === "flex") close(); else open();
    } else if (e.key === "Escape" && overlay.style.display === "flex") {
      close();
    }
  });

  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) close();
  });

  input.addEventListener("input", () => {
    const q = input.value.trim();
    clearTimeout(fetchTimer);
    fetchTimer = setTimeout(() => doSearch(q), q.length < 2 ? 0 : 180);
  });

  input.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      activeIdx = Math.min(currentItems.length - 1, activeIdx + 1);
      render(currentItems, input.value.trim());
      const row = list.querySelector(`.cmd-palette-row[data-idx="${activeIdx}"]`);
      row?.scrollIntoView({ block: "nearest" });
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      activeIdx = Math.max(0, activeIdx - 1);
      render(currentItems, input.value.trim());
      const row = list.querySelector(`.cmd-palette-row[data-idx="${activeIdx}"]`);
      row?.scrollIntoView({ block: "nearest" });
    } else if (e.key === "Enter") {
      e.preventDefault();
      goActive();
    }
  });

  list.addEventListener("click", (e) => {
    const row = e.target.closest(".cmd-palette-row");
    if (!row) return;
    activeIdx = parseInt(row.dataset.idx, 10) || 0;
    goActive();
  });

  // Mevcut sayfayı "son ziyaret"e ekle (sidebar etiketi yoksa pas geç)
  try {
    const title = document.title?.split(" — ")[0]?.trim();
    if (title && location.pathname && location.pathname !== "/") {
      // Yalnız statik sayfalardan birine denk geliyorsa kayıt et (gürültü azalt)
      const match = STATIC_PAGES.find(p => p.url === location.pathname);
      if (match) recordRecent(match);
    }
  } catch (e) {}
})();
