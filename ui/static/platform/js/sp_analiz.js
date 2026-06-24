/* SP Stratejik Analizler — SWOT / TOWS / PESTLE */
"use strict";

(function () {
  const card = document.getElementById("sp-analiz-card");
  if (!card) return;

  const canManage = card.dataset.canManage === "true";
  const CSRF = document.querySelector('meta[name="csrf-token"]')?.content || "";

  // ── State ─────────────────────────────────────────────────────────────────
  const state = {
    swot:   { s: [], w: [], o: [], t: [] },
    tows:   { so: [], st: [], wo: [], wt: [] },
    pestle: { political: [], economic: [], social: [], technological: [], environmental: [], legal: [] },
  };

  // ── Yardımcılar ───────────────────────────────────────────────────────────
  function esc(s) {
    return String(s ?? "").replace(/[&<>"']/g, c =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  function renderList(elId, items) {
    const el = document.getElementById(elId);
    if (!el) return;
    if (!items.length) {
      el.innerHTML = '<div style="font-size:12px;color:#94a3b8;padding:6px 0;">' + t("Henüz eklenmemiş") + '</div>';
      return;
    }
    el.innerHTML = items.map((item, i) => {
      const text = typeof item === "string" ? item : (item.text || "");
      return `<div class="sp-analiz-item">
        <span class="sp-analiz-item-text">${esc(text)}</span>
        ${canManage ? `<button class="sp-analiz-del-btn" data-idx="${i}"><i class="fas fa-times"></i></button>` : ""}
      </div>`;
    }).join("");
    if (canManage) {
      el.querySelectorAll(".sp-analiz-del-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          items.splice(parseInt(btn.dataset.idx), 1);
          renderList(elId, items);
        });
      });
    }
  }

  function addItem(inputId, items, listId) {
    const inp = document.getElementById(inputId);
    if (!inp) return;
    const val = inp.value.trim();
    if (!val) return;
    items.push(val);
    inp.value = "";
    renderList(listId, items);
  }

  function postJson(url, data) {
    return fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": CSRF },
      body: JSON.stringify(data),
    }).then(r => r.json());
  }

  function toast(msg, ok) {
    if (typeof Swal !== "undefined") {
      Swal.fire({ toast: true, position: "top-end", icon: ok ? "success" : "error",
        title: msg, showConfirmButton: false, timer: 2500 });
    } else {
      alert(msg);
    }
  }

  // ── Sekme ─────────────────────────────────────────────────────────────────
  card.querySelectorAll(".sp-analiz-tab").forEach(btn => {
    btn.addEventListener("click", () => {
      card.querySelectorAll(".sp-analiz-tab").forEach(b => b.classList.remove("active"));
      card.querySelectorAll(".sp-analiz-panel").forEach(p => p.style.display = "none");
      btn.classList.add("active");
      const panel = document.getElementById("sp-analiz-panel-" + btn.dataset.tab);
      if (panel) panel.style.display = "";
    });
  });

  // ── SWOT ──────────────────────────────────────────────────────────────────
  function renderSwot() {
    ["s","w","o","t"].forEach(q => renderList("sp-swot-" + q + "-list", state.swot[q]));
  }

  card.querySelectorAll(".sp-analiz-add-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const q = btn.dataset.quadrant;
      addItem("sp-swot-" + q + "-input", state.swot[q], "sp-swot-" + q + "-list");
    });
  });

  ["s","w","o","t"].forEach(q => {
    const inp = document.getElementById("sp-swot-" + q + "-input");
    inp?.addEventListener("keydown", e => {
      if (e.key === "Enter") { e.preventDefault(); addItem("sp-swot-" + q + "-input", state.swot[q], "sp-swot-" + q + "-list"); }
    });
  });

  document.getElementById("sp-swot-save-btn")?.addEventListener("click", () => {
    postJson(card.dataset.swotSaveUrl, state.swot)
      .then(r => toast(r.success ? t("SWOT kaydedildi.") : (r.message || t("Hata")), r.success))
      .catch(() => toast(t("Bağlantı hatası."), false));
  });

  fetch(card.dataset.swotUrl).then(r => r.json()).then(res => {
    if (!res.success) return;
    state.swot.s = res.data.strengths     || [];
    state.swot.w = res.data.weaknesses    || [];
    state.swot.o = res.data.opportunities || [];
    state.swot.t = res.data.threats       || [];
    renderSwot();
    const total = state.swot.s.length + state.swot.w.length + state.swot.o.length + state.swot.t.length;
    const badge = document.getElementById("sp-analiz-badge");
    if (badge && total > 0) badge.textContent = `SWOT: ${total} ${t("madde")}`;
  }).catch(() => {});

  // ── TOWS ──────────────────────────────────────────────────────────────────
  function renderTows() {
    ["so","st","wo","wt"].forEach(q => renderList("sp-tows-" + q + "-list", state.tows[q]));
  }

  card.querySelectorAll(".sp-tows-add-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const q = btn.dataset.quadrant;
      addItem("sp-tows-" + q + "-input", state.tows[q], "sp-tows-" + q + "-list");
    });
  });

  ["so","st","wo","wt"].forEach(q => {
    const inp = document.getElementById("sp-tows-" + q + "-input");
    inp?.addEventListener("keydown", e => {
      if (e.key === "Enter") { e.preventDefault(); addItem("sp-tows-" + q + "-input", state.tows[q], "sp-tows-" + q + "-list"); }
    });
  });

  document.getElementById("sp-tows-save-btn")?.addEventListener("click", () => {
    postJson(card.dataset.towsSaveUrl, state.tows)
      .then(r => toast(r.success ? t("TOWS kaydedildi.") : (r.message || t("Hata")), r.success))
      .catch(() => toast(t("Bağlantı hatası."), false));
  });

  fetch(card.dataset.towsUrl).then(r => r.json()).then(res => {
    if (!res.success) return;
    state.tows.so = res.data.so || [];
    state.tows.st = res.data.st || [];
    state.tows.wo = res.data.wo || [];
    state.tows.wt = res.data.wt || [];
    renderTows();
  }).catch(() => {});

  // ── PESTLE ────────────────────────────────────────────────────────────────
  const PESTLE_KEYS = ["political","economic","social","technological","environmental","legal"];

  function renderPestle() {
    PESTLE_KEYS.forEach(k => renderList("sp-pestle-" + k + "-list", state.pestle[k]));
  }

  card.querySelectorAll(".sp-pestle-add-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const k = btn.dataset.factor;
      addItem("sp-pestle-" + k + "-input", state.pestle[k], "sp-pestle-" + k + "-list");
    });
  });

  PESTLE_KEYS.forEach(k => {
    const inp = document.getElementById("sp-pestle-" + k + "-input");
    inp?.addEventListener("keydown", e => {
      if (e.key === "Enter") { e.preventDefault(); addItem("sp-pestle-" + k + "-input", state.pestle[k], "sp-pestle-" + k + "-list"); }
    });
  });

  document.getElementById("sp-pestle-save-btn")?.addEventListener("click", () => {
    postJson(card.dataset.pestleSaveUrl, state.pestle)
      .then(r => toast(r.success ? t("PESTLE kaydedildi.") : (r.message || t("Hata")), r.success))
      .catch(() => toast(t("Bağlantı hatası."), false));
  });

  fetch(card.dataset.pestleUrl).then(r => r.json()).then(res => {
    if (!res.success) return;
    PESTLE_KEYS.forEach(k => { state.pestle[k] = res.data[k] || []; });
    renderPestle();
  }).catch(() => {});

})();
