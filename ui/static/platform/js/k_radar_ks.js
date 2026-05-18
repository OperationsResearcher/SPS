/* KS-Radar — Hub + Modal + CRUD JS */
"use strict";

(function () {

  // ── Yardımcılar ──────────────────────────────────────────────────────────────
  function esc(s) {
    return String(s ?? "").replace(/[&<>"']/g, c =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }
  function setHtml(id, html) { const el = document.getElementById(id); if (el) el.innerHTML = html; }
  function scoreColor(v) {
    if (v == null) return "#94a3b8";
    if (v >= 80) return "#10b981";
    if (v >= 50) return "#f59e0b";
    return "#ef4444";
  }
  function fetchJson(url) {
    return fetch(url).then(r => r.json());
  }
  const EMPTY_ROW = n => `<tr><td colspan="${n}" style="text-align:center;padding:20px;color:#94a3b8;">Kayıt yok.</td></tr>`;

  // ── Modal Yönetimi ────────────────────────────────────────────────────────────
  function openModal(id) {
    const el = document.getElementById("ks-modal-" + id);
    if (el) el.classList.add("open");
  }
  function closeModal(id) {
    const el = document.getElementById("ks-modal-" + id);
    if (el) el.classList.remove("open");
  }

  // Kapat butonları
  document.querySelectorAll(".ks-modal-close").forEach(btn => {
    btn.addEventListener("click", () => {
      btn.closest(".mc-modal-overlay")?.classList.remove("open");
    });
  });
  // Overlay tıklama ile kapat
  document.querySelectorAll(".mc-modal-overlay").forEach(overlay => {
    overlay.addEventListener("click", e => {
      if (e.target === overlay) overlay.classList.remove("open");
    });
  });

  // ── Hub Sayfası ───────────────────────────────────────────────────────────────
  const hub = document.getElementById("ks-hub-root");
  if (!hub) return;

  const API = {
    ks:       hub.dataset.apiKs,
    swot:     hub.dataset.apiSwot,
    tows:     hub.dataset.apiTows,
    pestle:   hub.dataset.apiPestle,
    gap:      hub.dataset.apiGap,
    strateji: hub.dataset.apiStrateji,
  };

  // Kart tıklama → modal aç + yükle
  const loaded = {};
  document.querySelectorAll(".ks-module-card[data-modal]").forEach(card => {
    card.addEventListener("click", () => {
      const key = card.dataset.modal;
      openModal(key);
      if (!loaded[key]) {
        loaded[key] = true;
        loadModal(key);
      }
    });
  });

  function loadModal(key) {
    switch (key) {
      case "swot":   loadSwotModal();   break;
      case "tows":   loadTowsModal();   break;
      case "pestle": loadPestleModal(); break;
      case "gap":    loadGapModal();    break;
      case "okr":    loadOkrModal();    break;
      case "bsc":    loadBscModal();    break;
    }
  }

  // ── KS Skoru ─────────────────────────────────────────────────────────────────
  fetchJson(API.ks).then(res => {
    if (!res.success) return;
    const d = res.data;
    const el = document.getElementById("ks-skor");
    if (el) { el.textContent = (d.score || 0).toFixed(1); el.style.color = scoreColor(d.score); }
    const band = document.getElementById("ks-band");
    if (band) {
      const labels = { green: "İyi", yellow: "Orta", red: "Kritik" };
      band.textContent = labels[d.band] || d.band;
    }
    const card = document.getElementById("ks-skor-card");
    if (card) card.style.background = d.band === "green" ? "#f0fdf4" : d.band === "yellow" ? "#fffbeb" : "#fef2f2";
  }).catch(() => {});

  // ── SWOT Mini (hub kartı) ─────────────────────────────────────────────────────
  fetchJson(API.swot).then(res => {
    if (!res.success) return;
    const d = res.data;
    const oz = d.ozet || {};
    const total = (oz.S || 0) + (oz.W || 0) + (oz.O || 0) + (oz.T || 0);
    const badge = document.getElementById("ks-swot-badge");
    if (badge) badge.textContent = total ? total + " madde" : "Veri yok";
    ["s","w","o","t"].forEach(k => {
      const el = document.getElementById("ks-swot-" + k);
      if (el) el.textContent = oz[k.toUpperCase()] || 0;
    });
  }).catch(() => {});

  // ── TOWS Mini ────────────────────────────────────────────────────────────────
  fetchJson(API.tows).then(res => {
    if (!res.success) return;
    const d = res.data;
    const oz = d.ozet || {};
    const total = (oz.SO || 0) + (oz.ST || 0) + (oz.WO || 0) + (oz.WT || 0);
    const badge = document.getElementById("ks-tows-badge");
    if (badge) badge.textContent = total ? total + " strateji" : "Veri yok";
    ["so","st","wo","wt"].forEach(k => {
      const el = document.getElementById("ks-tows-" + k);
      if (el) el.textContent = oz[k.toUpperCase()] || 0;
    });
  }).catch(() => {});

  // ── PESTLE Mini ───────────────────────────────────────────────────────────────
  const PESTLE_META = [
    { key: "political",     abbr: "P", color: "#6366f1" },
    { key: "economic",      abbr: "E", color: "#10b981" },
    { key: "social",        abbr: "S", color: "#f59e0b" },
    { key: "technological", abbr: "T", color: "#3b82f6" },
    { key: "environmental", abbr: "E", color: "#84cc16" },
    { key: "legal",         abbr: "L", color: "#ef4444" },
  ];
  fetchJson(API.pestle).then(res => {
    if (!res.success) return;
    const d = res.data;
    const oz = d.ozet || {};
    const total = Object.values(oz).reduce((a, b) => a + b, 0);
    const badge = document.getElementById("ks-pestle-badge");
    if (badge) badge.textContent = total ? total + " faktör" : "Veri yok";
    const miniEl = document.getElementById("ks-pestle-mini");
    if (miniEl) {
      const maxVal = Math.max(...PESTLE_META.map(m => (d[m.key] || []).length), 1);
      miniEl.innerHTML = PESTLE_META.map(m => {
        const cnt = (d[m.key] || []).length;
        const pct = Math.round(cnt / maxVal * 100);
        return `<div class="kr-bar-row" style="padding:2px 0;">
          <div style="flex:0 0 20px;font-size:11px;font-weight:700;color:${m.color};">${m.abbr}</div>
          <div class="kr-bar-track"><div class="kr-bar-fill" style="width:${pct}%;background:${m.color};"></div></div>
          <div style="flex:0 0 20px;font-size:11px;text-align:right;">${cnt}</div>
        </div>`;
      }).join("");
    }
  }).catch(() => {});

  // ── GAP Mini ─────────────────────────────────────────────────────────────────
  fetchJson(API.gap).then(res => {
    if (!res.success) return;
    const d = res.data;
    const pgBasari = document.getElementById("ks-pg-basari");
    if (pgBasari) { pgBasari.textContent = "%" + (d.genel_ort_basari || 0); pgBasari.style.color = scoreColor(d.genel_ort_basari); }
    const pgSub = document.getElementById("ks-pg-sub");
    if (pgSub) pgSub.textContent = `${d.veri_girilen} / ${d.toplam_kpi} PG`;
    const badge = document.getElementById("ks-gap-badge");
    if (badge) badge.textContent = d.toplam_kpi + " PG";
    ["hedefte","riskli","kritik"].forEach(k => {
      const el = document.getElementById("ks-gap-" + k);
      if (el) el.textContent = d[k] || 0;
    });
  }).catch(() => {});

  // ── Strateji Kapsama ─────────────────────────────────────────────────────────
  fetchJson(API.strateji).then(res => {
    if (!res.success) return;
    const d = res.data;
    const kapsamEl = document.getElementById("ks-kapsam-pct");
    if (kapsamEl) { kapsamEl.textContent = "%" + (d.kapsam_pct || 0); kapsamEl.style.color = scoreColor(d.kapsam_pct); }
    const kapsamSub = document.getElementById("ks-kapsam-sub");
    if (kapsamSub) kapsamSub.textContent = `${d.bagli_surec} / ${d.toplam_surec} süreç bağlı`;
    const stratCount = document.getElementById("ks-strat-count");
    if (stratCount) stratCount.textContent = d.toplam_strateji;
    const subCount = document.getElementById("ks-sub-strat-count");
    if (subCount) subCount.textContent = d.toplam_alt_strateji + " alt strateji";
    const badge = document.getElementById("ks-strat-kapsam-badge");
    if (badge) badge.textContent = "%" + d.kapsam_pct + " kapsam";
    const listEl = document.getElementById("ks-strat-list");
    if (listEl && d.stratejiler) {
      listEl.innerHTML = d.stratejiler.map(s => {
        const pct = s.bagli_surec_sayisi > 0 ? Math.round(s.bagli_surec_sayisi / Math.max(1, d.toplam_surec) * 100) : 0;
        const cls = s.bagli_surec_sayisi === 0 ? "low" : s.bagli_surec_sayisi < 3 ? "mid" : "high";
        return `<div class="kr-rank-item">
          <div class="kr-rank-code">${esc(s.code || "—")}</div>
          <div class="kr-rank-name" title="${esc(s.title)}">${esc(s.title)}</div>
          <div style="flex:1;margin:0 12px;">
            <div class="kr-bar-track"><div class="kr-bar-fill" style="width:${Math.min(100,pct)}%;"></div></div>
          </div>
          <div class="kr-rank-score ${cls}">${s.bagli_surec_sayisi} süreç</div>
        </div>`;
      }).join("");
    }
  }).catch(() => {});

  // ══════════════════════════════════════════════════════════════════════════════
  // MODAL İÇERİKLERİ
  // ══════════════════════════════════════════════════════════════════════════════

  function renderSwotList(items, emptyMsg) {
    if (!items || !items.length) return `<div class="ks-swot-empty">${esc(emptyMsg)}</div>`;
    return items.map(item => {
      const text = typeof item === "string" ? item : (item.text || item.content || "");
      return `<li class="ks-swot-item">${esc(text)}</li>`;
    }).join("");
  }

  // ── CRUD Yardımcıları ─────────────────────────────────────────────────────────
  const CSRF = document.querySelector('meta[name="csrf-token"]')?.content || "";

  function postJson(url, data) {
    return fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": CSRF },
      body: JSON.stringify(data),
    }).then(r => r.json());
  }

  function toast(msg, ok) {
    Swal.fire({ toast: true, position: "top-end", icon: ok ? "success" : "error",
      title: msg, showConfirmButton: false, timer: 2200 });
  }

  // Madde listesi render (salt okunur)
  function renderItems(items) {
    if (!items || !items.length) return '<li class="ks-swot-empty">Henüz girilmemiş</li>';
    return items.map((item, i) => {
      const text = typeof item === "string" ? item : (item.text || "");
      return `<li class="ks-swot-item">
        <span class="ks-swot-item-text">${esc(text)}</span>
      </li>`;
    }).join("");
  }

  // Madde listesi render (düzenlenebilir)
  function renderItemsEdit(items, onDelete, onEdit) {
    if (!items || !items.length) return '<li class="ks-swot-empty">Henüz girilmemiş</li>';
    return items.map((item, i) => {
      const text = typeof item === "string" ? item : (item.text || "");
      return `<li class="ks-swot-item ks-swot-item-edit" data-idx="${i}">
        <span class="ks-swot-item-text">${esc(text)}</span>
        <span class="ks-swot-item-actions">
          <button class="ks-item-btn ks-item-edit" data-idx="${i}" title="Düzenle"><i class="fas fa-pen"></i></button>
          <button class="ks-item-btn ks-item-del" data-idx="${i}" title="Sil"><i class="fas fa-trash"></i></button>
        </span>
      </li>`;
    }).join("");
  }

  // Giriş satırı
  function addRowHtml(inputId, btnId, placeholder) {
    return `<div class="ks-add-row">
      <input type="text" id="${inputId}" class="mc-form-input" placeholder="${esc(placeholder)}" style="height:34px;font-size:13px;">
      <button id="${btnId}" class="mc-btn mc-btn-primary mc-btn-sm"><i class="fas fa-plus"></i> Ekle</button>
    </div>`;
  }

  // Kaydet butonu
  function saveRowHtml(btnId) {
    return `<div style="display:flex;justify-content:flex-end;margin-top:10px;">
      <button id="${btnId}" class="mc-btn mc-btn-success mc-btn-sm"><i class="fas fa-save"></i> Kaydet</button>
    </div>`;
  }

  // ── SWOT Modal ────────────────────────────────────────────────────────────────
  function loadSwotModal() {
    const canManage = hub.dataset.canManage === "true";
    setHtml("ks-modal-swot-body", '<div class="kr-loading" style="padding:32px;">Yükleniyor…</div>');

    // State
    const swotState = { s: [], w: [], o: [], t: [] };

    function renderSwotModal() {
      const oz = { S: swotState.s.length, W: swotState.w.length, O: swotState.o.length, T: swotState.t.length };
      const quadrants = [
        { key: "s", cls: "ks-swot-s", icon: "fa-plus-circle",          label: "Güçlü Yönler (S)",  placeholder: "Güçlü yön ekle…" },
        { key: "w", cls: "ks-swot-w", icon: "fa-minus-circle",         label: "Zayıf Yönler (W)",  placeholder: "Zayıf yön ekle…" },
        { key: "o", cls: "ks-swot-o", icon: "fa-arrow-up-right-dots",  label: "Fırsatlar (O)",     placeholder: "Fırsat ekle…" },
        { key: "t", cls: "ks-swot-t", icon: "fa-triangle-exclamation", label: "Tehditler (T)",     placeholder: "Tehdit ekle…" },
      ];
      const matrixHtml = quadrants.map(q => `
        <div class="ks-swot-cell ${q.cls}">
          <div class="ks-swot-cell-header"><i class="fas ${q.icon}"></i> ${q.label}</div>
          <ul class="ks-swot-list" id="ks-swot-list-${q.key}">
            ${canManage ? renderItemsEdit(swotState[q.key]) : renderItems(swotState[q.key])}
          </ul>
          ${canManage ? addRowHtml("ks-swot-inp-" + q.key, "ks-swot-add-" + q.key, q.placeholder) : ""}
        </div>`).join("");

      setHtml("ks-modal-swot-body", `
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;">
          <span class="mc-badge mc-badge-success">S: ${oz.S}</span>
          <span class="mc-badge mc-badge-danger">W: ${oz.W}</span>
          <span class="mc-badge mc-badge-info">O: ${oz.O}</span>
          <span class="mc-badge mc-badge-warning">T: ${oz.T}</span>
        </div>
        <div class="ks-swot-matrix">${matrixHtml}</div>
        ${canManage ? saveRowHtml("ks-swot-save") : ""}`);

      if (!canManage) return;

      // Ekle butonları
      ["s","w","o","t"].forEach(k => {
        const inp = document.getElementById("ks-swot-inp-" + k);
        const btn = document.getElementById("ks-swot-add-" + k);
        const doAdd = () => {
          const val = inp?.value.trim();
          if (!val) return;
          swotState[k].push(val);
          inp.value = "";
          renderSwotModal();
        };
        btn?.addEventListener("click", doAdd);
        inp?.addEventListener("keydown", e => { if (e.key === "Enter") { e.preventDefault(); doAdd(); } });
      });

      // Sil butonları
      document.querySelectorAll("#ks-modal-swot-body .ks-item-del").forEach(btn => {
        btn.addEventListener("click", () => {
          const li = btn.closest("li");
          const listEl = btn.closest("ul");
          const key = listEl.id.replace("ks-swot-list-", "");
          const idx = parseInt(btn.dataset.idx);
          swotState[key].splice(idx, 1);
          renderSwotModal();
        });
      });

      // Düzenle butonları
      document.querySelectorAll("#ks-modal-swot-body .ks-item-edit").forEach(btn => {
        btn.addEventListener("click", () => {
          const listEl = btn.closest("ul");
          const key = listEl.id.replace("ks-swot-list-", "");
          const idx = parseInt(btn.dataset.idx);
          const cur = swotState[key][idx];
          const text = typeof cur === "string" ? cur : (cur.text || "");
          Swal.fire({
            title: "Maddeyi Düzenle",
            input: "text",
            inputValue: text,
            showCancelButton: true,
            confirmButtonText: "Kaydet",
            cancelButtonText: "İptal",
          }).then(r => {
            if (r.isConfirmed && r.value.trim()) {
              swotState[key][idx] = r.value.trim();
              renderSwotModal();
            }
          });
        });
      });

      // Kaydet
      document.getElementById("ks-swot-save")?.addEventListener("click", () => {
        postJson(hub.dataset.apiSwotSave, {
          strengths: swotState.s, weaknesses: swotState.w,
          opportunities: swotState.o, threats: swotState.t,
        }).then(r => {
          toast(r.success ? "SWOT kaydedildi." : (r.message || "Hata"), r.success);
          if (r.success) {
            delete loaded["swot"];
            // Hub mini kartını güncelle
            ["s","w","o","t"].forEach(k => {
              const el = document.getElementById("ks-swot-" + k);
              if (el) el.textContent = swotState[k].length;
            });
            const badge = document.getElementById("ks-swot-badge");
            const total = swotState.s.length + swotState.w.length + swotState.o.length + swotState.t.length;
            if (badge) badge.textContent = total + " madde";
          }
        }).catch(() => toast("Bağlantı hatası.", false));
      });
    }

    fetchJson(API.swot).then(res => {
      if (!res.success) { setHtml("ks-modal-swot-body", '<div style="color:#ef4444;padding:16px;">Yüklenemedi.</div>'); return; }
      const d = res.data;
      swotState.s = (d.strengths     || []).map(i => typeof i === "string" ? i : (i.text || ""));
      swotState.w = (d.weaknesses    || []).map(i => typeof i === "string" ? i : (i.text || ""));
      swotState.o = (d.opportunities || []).map(i => typeof i === "string" ? i : (i.text || ""));
      swotState.t = (d.threats       || []).map(i => typeof i === "string" ? i : (i.text || ""));
      renderSwotModal();
    }).catch(() => setHtml("ks-modal-swot-body", '<div style="color:#ef4444;padding:16px;">Yüklenemedi.</div>'));
  }

  // ── TOWS Modal ────────────────────────────────────────────────────────────────
  function loadTowsModal() {
    const canManage = hub.dataset.canManage === "true";
    setHtml("ks-modal-tows-body", '<div class="kr-loading" style="padding:32px;">Yükleniyor…</div>');

    const towsState = { so: [], st: [], wo: [], wt: [] };

    function renderTowsModal() {
      const oz = { SO: towsState.so.length, ST: towsState.st.length, WO: towsState.wo.length, WT: towsState.wt.length };
      const cells = [
        { key: "so", cls: "ks-tows-so", label: "SO — Saldırgan", placeholder: "SO stratejisi ekle…" },
        { key: "wo", cls: "ks-tows-wo", label: "WO — Dönüşüm",   placeholder: "WO stratejisi ekle…" },
        { key: "st", cls: "ks-tows-st", label: "ST — Savunma",   placeholder: "ST stratejisi ekle…" },
        { key: "wt", cls: "ks-tows-wt", label: "WT — Kaçınma",   placeholder: "WT stratejisi ekle…" },
      ];
      const cellsHtml = (keys) => keys.map(c => `
        <div class="ks-tows-cell ${c.cls}">
          <div class="ks-tows-cell-label">${c.label}</div>
          <ul class="ks-swot-list" id="ks-tows-list-${c.key}">
            ${canManage ? renderItemsEdit(towsState[c.key]) : renderItems(towsState[c.key])}
          </ul>
          ${canManage ? addRowHtml("ks-tows-inp-" + c.key, "ks-tows-add-" + c.key, c.placeholder) : ""}
        </div>`).join("");

      setHtml("ks-modal-tows-body", `
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;">
          <span class="mc-badge mc-badge-success">SO: ${oz.SO}</span>
          <span class="mc-badge mc-badge-indigo">ST: ${oz.ST}</span>
          <span class="mc-badge mc-badge-info">WO: ${oz.WO}</span>
          <span class="mc-badge mc-badge-warning">WT: ${oz.WT}</span>
        </div>
        <div class="ks-tows-matrix">
          <div class="ks-tows-header-row">
            <div class="ks-tows-corner"></div>
            <div class="ks-tows-col-header ks-tows-s-header"><i class="fas fa-plus-circle"></i> Güçlü Yönler (S)</div>
            <div class="ks-tows-col-header ks-tows-w-header"><i class="fas fa-minus-circle"></i> Zayıf Yönler (W)</div>
          </div>
          <div class="ks-tows-row">
            <div class="ks-tows-row-header ks-tows-o-header"><i class="fas fa-arrow-up-right-dots"></i> Fırsatlar</div>
            ${cellsHtml([cells[0], cells[1]])}
          </div>
          <div class="ks-tows-row">
            <div class="ks-tows-row-header ks-tows-t-header"><i class="fas fa-triangle-exclamation"></i> Tehditler</div>
            ${cellsHtml([cells[2], cells[3]])}
          </div>
        </div>
        ${canManage ? saveRowHtml("ks-tows-save") : ""}`);

      if (!canManage) return;

      ["so","st","wo","wt"].forEach(k => {
        const inp = document.getElementById("ks-tows-inp-" + k);
        const btn = document.getElementById("ks-tows-add-" + k);
        const doAdd = () => {
          const val = inp?.value.trim();
          if (!val) return;
          towsState[k].push(val);
          inp.value = "";
          renderTowsModal();
        };
        btn?.addEventListener("click", doAdd);
        inp?.addEventListener("keydown", e => { if (e.key === "Enter") { e.preventDefault(); doAdd(); } });
      });

      document.querySelectorAll("#ks-modal-tows-body .ks-item-del").forEach(btn => {
        btn.addEventListener("click", () => {
          const key = btn.closest("ul").id.replace("ks-tows-list-", "");
          towsState[key].splice(parseInt(btn.dataset.idx), 1);
          renderTowsModal();
        });
      });

      document.querySelectorAll("#ks-modal-tows-body .ks-item-edit").forEach(btn => {
        btn.addEventListener("click", () => {
          const key = btn.closest("ul").id.replace("ks-tows-list-", "");
          const idx = parseInt(btn.dataset.idx);
          Swal.fire({ title: "Maddeyi Düzenle", input: "text", inputValue: towsState[key][idx],
            showCancelButton: true, confirmButtonText: "Kaydet", cancelButtonText: "İptal" })
            .then(r => { if (r.isConfirmed && r.value.trim()) { towsState[key][idx] = r.value.trim(); renderTowsModal(); } });
        });
      });

      document.getElementById("ks-tows-save")?.addEventListener("click", () => {
        postJson(hub.dataset.apiTowsSave, towsState)
          .then(r => {
            toast(r.success ? "TOWS kaydedildi." : (r.message || "Hata"), r.success);
            if (r.success) {
              delete loaded["tows"];
              const badge = document.getElementById("ks-tows-badge");
              const total = towsState.so.length + towsState.st.length + towsState.wo.length + towsState.wt.length;
              if (badge) badge.textContent = total + " strateji";
            }
          }).catch(() => toast("Bağlantı hatası.", false));
      });
    }

    fetchJson(API.tows).then(res => {
      if (!res.success) { setHtml("ks-modal-tows-body", '<div style="color:#ef4444;padding:16px;">Yüklenemedi.</div>'); return; }
      const d = res.data;
      towsState.so = (d.so || []).map(i => typeof i === "string" ? i : (i.text || ""));
      towsState.st = (d.st || []).map(i => typeof i === "string" ? i : (i.text || ""));
      towsState.wo = (d.wo || []).map(i => typeof i === "string" ? i : (i.text || ""));
      towsState.wt = (d.wt || []).map(i => typeof i === "string" ? i : (i.text || ""));
      renderTowsModal();
    }).catch(() => setHtml("ks-modal-tows-body", '<div style="color:#ef4444;padding:16px;">Yüklenemedi.</div>'));
  }

  // ── PESTLE Modal ──────────────────────────────────────────────────────────────
  let pestleChart = null;
  function loadPestleModal() {
    const canManage = hub.dataset.canManage === "true";
    setHtml("ks-modal-pestle-body", '<div class="kr-loading" style="padding:32px;">Yükleniyor…</div>');

    const PESTLE_LABELS = [
      { key: "political",     label: "Siyasi (P)",     color: "#6366f1", placeholder: "Siyasi faktör ekle…" },
      { key: "economic",      label: "Ekonomik (E)",   color: "#10b981", placeholder: "Ekonomik faktör ekle…" },
      { key: "social",        label: "Sosyal (S)",     color: "#f59e0b", placeholder: "Sosyal faktör ekle…" },
      { key: "technological", label: "Teknolojik (T)", color: "#3b82f6", placeholder: "Teknolojik faktör ekle…" },
      { key: "environmental", label: "Çevresel (E)",   color: "#84cc16", placeholder: "Çevresel faktör ekle…" },
      { key: "legal",         label: "Yasal (L)",      color: "#ef4444", placeholder: "Yasal faktör ekle…" },
    ];
    const pestleState = {};
    PESTLE_LABELS.forEach(m => { pestleState[m.key] = []; });

    function renderPestleModal() {
      const cardsHtml = PESTLE_LABELS.map(m => {
        const items = pestleState[m.key];
        const listHtml = items.length
          ? (canManage ? renderItemsEdit(items) : renderItems(items))
          : '<li class="ks-swot-empty">Henüz girilmemiş</li>';
        return `<div class="mc-card" style="border-top:3px solid ${m.color};">
          <div class="mc-card-header" style="padding:10px 14px;">
            <span class="mc-card-title" style="color:${m.color};font-size:13px;">${m.label}</span>
            <span class="mc-badge" style="background:${m.color}20;color:${m.color};">${items.length}</span>
          </div>
          <div class="mc-card-body" style="padding:8px 14px;">
            <ul class="ks-swot-list" id="ks-pestle-list-${m.key}" style="padding:0;">${listHtml}</ul>
            ${canManage ? addRowHtml("ks-pestle-inp-" + m.key, "ks-pestle-add-" + m.key, m.placeholder) : ""}
          </div>
        </div>`;
      }).join("");

      setHtml("ks-modal-pestle-body", `
        <div class="mc-grid-3" style="gap:12px;">${cardsHtml}</div>
        ${canManage ? saveRowHtml("ks-pestle-save") : ""}`);

      if (!canManage) return;

      PESTLE_LABELS.forEach(m => {
        const inp = document.getElementById("ks-pestle-inp-" + m.key);
        const btn = document.getElementById("ks-pestle-add-" + m.key);
        const doAdd = () => {
          const val = inp?.value.trim();
          if (!val) return;
          pestleState[m.key].push(val);
          inp.value = "";
          renderPestleModal();
        };
        btn?.addEventListener("click", doAdd);
        inp?.addEventListener("keydown", e => { if (e.key === "Enter") { e.preventDefault(); doAdd(); } });
      });

      document.querySelectorAll("#ks-modal-pestle-body .ks-item-del").forEach(btn => {
        btn.addEventListener("click", () => {
          const key = btn.closest("ul").id.replace("ks-pestle-list-", "");
          pestleState[key].splice(parseInt(btn.dataset.idx), 1);
          renderPestleModal();
        });
      });

      document.querySelectorAll("#ks-modal-pestle-body .ks-item-edit").forEach(btn => {
        btn.addEventListener("click", () => {
          const key = btn.closest("ul").id.replace("ks-pestle-list-", "");
          const idx = parseInt(btn.dataset.idx);
          Swal.fire({ title: "Maddeyi Düzenle", input: "text", inputValue: pestleState[key][idx],
            showCancelButton: true, confirmButtonText: "Kaydet", cancelButtonText: "İptal" })
            .then(r => { if (r.isConfirmed && r.value.trim()) { pestleState[key][idx] = r.value.trim(); renderPestleModal(); } });
        });
      });

      document.getElementById("ks-pestle-save")?.addEventListener("click", () => {
        postJson(hub.dataset.apiPestleSave, pestleState)
          .then(r => {
            toast(r.success ? "PESTLE kaydedildi." : (r.message || "Hata"), r.success);
            if (r.success) {
              delete loaded["pestle"];
              const total = PESTLE_LABELS.reduce((s, m) => s + pestleState[m.key].length, 0);
              const badge = document.getElementById("ks-pestle-badge");
              if (badge) badge.textContent = total + " faktör";
            }
          }).catch(() => toast("Bağlantı hatası.", false));
      });
    }

    fetchJson(API.pestle).then(res => {
      if (!res.success) { setHtml("ks-modal-pestle-body", '<div style="color:#ef4444;padding:16px;">Yüklenemedi.</div>'); return; }
      const d = res.data;
      PESTLE_LABELS.forEach(m => {
        pestleState[m.key] = (d[m.key] || []).map(i => typeof i === "string" ? i : (i.text || ""));
      });
      renderPestleModal();
    }).catch(() => setHtml("ks-modal-pestle-body", '<div style="color:#ef4444;padding:16px;">Yüklenemedi.</div>'));
  }

  // ── BSC Mini (hub kartı) ─────────────────────────────────────────────────────
  const BSC_API = hub.dataset.apiBsc;
  if (BSC_API) {
    fetchJson(BSC_API).then(res => {
      if (!res.success) return;
      const p = res.perspectives || {};
      const COLORS = { finansal: "#6366f1", musteri: "#10b981", ic_surec: "#f59e0b", ogrenme: "#3b82f6" };
      const IDS    = { finansal: "ks-bsc-fin", musteri: "ks-bsc-mus", ic_surec: "ks-bsc-sur", ogrenme: "ks-bsc-ogr" };
      let total = 0;
      Object.entries(IDS).forEach(([key, elId]) => {
        const el = document.getElementById(elId);
        const sc = p[key]?.score;
        if (el) { el.textContent = sc != null ? sc + "%" : "—"; el.style.color = COLORS[key]; }
        total += p[key]?.kpi_count || 0;
      });
      const badge = document.getElementById("ks-bsc-badge");
      if (badge) badge.textContent = total + " KPI";
    }).catch(() => {});
  }

  // ── OKR Modal ─────────────────────────────────────────────────────────────────
  function loadOkrModal() {
    const canManage = hub.dataset.canManage === "true";
    const OBJ_URL    = hub.dataset.apiOkr;
    const OBJ_CREATE = hub.dataset.apiOkrObjCreate;
    const OBJ_BASE   = hub.dataset.apiOkrObjBase;
    const KR_BASE    = hub.dataset.apiOkrKrBase;

    function krUrl(id)  { return KR_BASE  + id; }
    function objUrl(id) { return OBJ_BASE + id; }

    // ── İç Modal Yardımcıları ─────────────────────────────────────────────────
    const objModal = document.getElementById("ks-okr-obj-modal");
    const krModal  = document.getElementById("ks-okr-kr-modal");

    function openInnerModal(el) { el?.classList.add("open"); }
    function closeInnerModal(el) { el?.classList.remove("open"); }

    function getObjForm() {
      return {
        title:       document.getElementById("okr-obj-title")?.value.trim(),
        quarter:     document.getElementById("okr-obj-quarter")?.value || null,
        owner:       document.getElementById("okr-obj-owner")?.value.trim(),
        description: document.getElementById("okr-obj-desc")?.value.trim(),
      };
    }
    function fillObjForm(d = {}) {
      document.getElementById("okr-obj-title").value   = d.title || "";
      document.getElementById("okr-obj-quarter").value = d.quarter || "";
      document.getElementById("okr-obj-owner").value   = d.owner || "";
      document.getElementById("okr-obj-desc").value    = d.description || "";
    }
    function getKrForm() {
      const toNum = id => { const v = document.getElementById(id)?.value; return v !== "" && v != null ? parseFloat(v) : null; };
      return {
        title:         document.getElementById("okr-kr-title")?.value.trim(),
        metric:        document.getElementById("okr-kr-metric")?.value.trim(),
        start_value:   toNum("okr-kr-start"),
        target_value:  toNum("okr-kr-target"),
        current_value: toNum("okr-kr-current"),
      };
    }
    function fillKrForm(d = {}) {
      document.getElementById("okr-kr-title").value   = d.title || "";
      document.getElementById("okr-kr-metric").value  = d.metric || "";
      document.getElementById("okr-kr-start").value   = d.start_value ?? "";
      document.getElementById("okr-kr-target").value  = d.target_value ?? "";
      document.getElementById("okr-kr-current").value = d.current_value ?? "";
    }

    // Kapat butonları
    document.getElementById("ks-okr-obj-modal-close")?.addEventListener("click",   () => closeInnerModal(objModal));
    document.getElementById("ks-okr-obj-modal-cancel")?.addEventListener("click",  () => closeInnerModal(objModal));
    document.getElementById("ks-okr-kr-modal-close")?.addEventListener("click",    () => closeInnerModal(krModal));
    document.getElementById("ks-okr-kr-modal-cancel")?.addEventListener("click",   () => closeInnerModal(krModal));
    objModal?.addEventListener("click", e => { if (e.target === objModal) closeInnerModal(objModal); });
    krModal?.addEventListener("click",  e => { if (e.target === krModal)  closeInnerModal(krModal); });

    // Callback'ler (save butonuna bağlanacak)
    let _objSaveCb = null;
    let _krSaveCb  = null;

    const objSaveBtn = document.getElementById("ks-okr-obj-modal-save");
    const krSaveBtn  = document.getElementById("ks-okr-kr-modal-save");

    // Önceki listener'ları temizlemek için clone
    function rebindSave(btn, cb) {
      const fresh = btn.cloneNode(true);
      btn.parentNode.replaceChild(fresh, btn);
      fresh.addEventListener("click", cb);
      return fresh;
    }

    // ── Skor Yardımcıları ─────────────────────────────────────────────────────
    function okrScoreColor(pct) {
      if (pct == null) return "#94a3b8";
      if (pct >= 70)  return "#10b981";
      if (pct >= 40)  return "#f59e0b";
      return "#ef4444";
    }
    function okrScoreLabel(pct) {
      if (pct == null) return "Veri yok";
      if (pct >= 70)  return "Başarılı";
      if (pct >= 40)  return "Devam ediyor";
      return "Kritik";
    }

    // ── Render ────────────────────────────────────────────────────────────────
    function renderOkr(data, year) {
      const QUARTERS = { 1: "Ç1", 2: "Ç2", 3: "Ç3", 4: "Ç4" };
      const grouped = {};
      data.forEach(o => {
        const q = o.quarter || "yillik";
        if (!grouped[q]) grouped[q] = [];
        grouped[q].push(o);
      });

      const addObjBtn = canManage ? `
        <div style="margin-bottom:16px;">
          <button id="okr-add-obj-btn" class="mc-btn mc-btn-primary mc-btn-sm">
            <i class="fas fa-plus"></i> Yeni Hedef Ekle
          </button>
        </div>` : "";

      const sectionsHtml = Object.entries(grouped).map(([q, objs]) => {
        const qLabel = q === "yillik" ? "Yıllık Hedefler"
          : `${QUARTERS[parseInt(q)] || q}. Çeyrek Hedefleri`;

        const objsHtml = objs.map(o => {
          const pct = o.avg_progress;
          const krsHtml = o.key_results.map(kr => {
            const kpct = kr.progress_pct;
            const barW = kpct != null ? Math.min(100, kpct) : 0;
            const editBtns = canManage ? `
              <button class="ks-item-btn ks-item-edit okr-kr-edit"
                data-kr-id="${kr.id}" data-title="${esc(kr.title)}"
                data-metric="${esc(kr.metric||'')}" data-start="${kr.start_value??''}"
                data-target="${kr.target_value??''}" data-current="${kr.current_value??''}"
                title="Düzenle"><i class="fas fa-pen"></i></button>
              <button class="ks-item-btn ks-item-del okr-kr-del"
                data-kr-id="${kr.id}" title="Sil"><i class="fas fa-trash"></i></button>` : "";
            return `<div class="okr-kr-row">
              <div class="okr-kr-title">
                <span>${esc(kr.title)}</span>
                ${kr.metric ? `<span class="okr-kr-metric">${esc(kr.metric)}</span>` : ""}
                <span class="okr-kr-values">${kr.start_value??'—'} → <strong>${kr.target_value??'—'}</strong> | Güncel: <strong style="color:${okrScoreColor(kpct)}">${kr.current_value??'—'}</strong></span>
              </div>
              <div class="okr-kr-bar-wrap">
                <div class="okr-kr-bar-track"><div class="okr-kr-bar-fill" style="width:${barW}%;background:${okrScoreColor(kpct)};"></div></div>
                <span class="okr-kr-pct" style="color:${okrScoreColor(kpct)}">${kpct != null ? kpct + "%" : "—"}</span>
              </div>
              <div class="okr-kr-actions">${editBtns}</div>
            </div>`;
          }).join("");

          const addKrBtn = canManage ? `
            <button class="mc-btn mc-btn-secondary mc-btn-sm okr-add-kr-btn"
              data-obj-id="${o.id}" style="margin-top:8px;">
              <i class="fas fa-plus"></i> KR Ekle
            </button>` : "";

          const objEditBtns = canManage ? `
            <button class="ks-item-btn ks-item-edit okr-obj-edit"
              data-obj-id="${o.id}" data-title="${esc(o.title)}"
              data-desc="${esc(o.description||'')}" data-quarter="${o.quarter||''}"
              data-owner="${esc(o.owner||'')}" title="Düzenle"><i class="fas fa-pen"></i></button>
            <button class="ks-item-btn ks-item-del okr-obj-del"
              data-obj-id="${o.id}" title="Sil"><i class="fas fa-trash"></i></button>` : "";

          return `<div class="okr-obj-card">
            <div class="okr-obj-header">
              <div class="okr-obj-title-wrap">
                <span class="okr-obj-icon"><i class="fas fa-bullseye"></i></span>
                <span class="okr-obj-title">${esc(o.title)}</span>
                ${o.owner ? `<span class="okr-obj-owner"><i class="fas fa-user"></i> ${esc(o.owner)}</span>` : ""}
              </div>
              <div style="display:flex;align-items:center;gap:8px;">
                <span class="mc-badge" style="background:${okrScoreColor(pct)}20;color:${okrScoreColor(pct)};">
                  ${pct != null ? pct + "%" : "—"} · ${okrScoreLabel(pct)}
                </span>
                ${objEditBtns}
              </div>
            </div>
            ${o.description ? `<div class="okr-obj-desc">${esc(o.description)}</div>` : ""}
            <div class="okr-kr-list">${krsHtml || '<div style="font-size:12px;color:#94a3b8;padding:8px 0;">Henüz KR eklenmemiş</div>'}</div>
            ${addKrBtn}
          </div>`;
        }).join("");

        return `<div class="okr-section">
          <div class="okr-section-label">${qLabel}</div>
          ${objsHtml}
        </div>`;
      }).join("");

      const emptyHtml = data.length === 0 ? `
        <div class="mc-empty" style="padding:32px;">
          <div class="mc-empty-icon"><i class="fas fa-crosshairs"></i></div>
          <div class="mc-empty-title">Henüz OKR tanımlanmamış</div>
          <div class="mc-empty-text">${year} yılı için ilk hedefinizi ekleyin.</div>
        </div>` : "";

      setHtml("ks-modal-okr-body", `
        <div style="font-size:12px;color:#94a3b8;margin-bottom:12px;">${year} yılı OKR'leri</div>
        ${addObjBtn}${sectionsHtml}${emptyHtml}`);

      if (!canManage) return;

      // ── Objective Ekle ────────────────────────────────────────────────────
      document.getElementById("okr-add-obj-btn")?.addEventListener("click", () => {
        document.getElementById("ks-okr-obj-modal-title").textContent = "Yeni Hedef Ekle";
        fillObjForm();
        const freshSave = rebindSave(
          document.getElementById("ks-okr-obj-modal-save"),
          () => {
            const d = getObjForm();
            if (!d.title) { toast("Başlık zorunludur.", false); return; }
            postJson(OBJ_CREATE, d).then(res => {
              if (res.success) { toast("Hedef eklendi.", true); closeInnerModal(objModal); delete loaded["okr"]; loadOkrModal(); }
              else toast(res.message || "Hata", false);
            }).catch(() => toast("Bağlantı hatası.", false));
          }
        );
        openInnerModal(objModal);
      });

      // ── Objective Düzenle ─────────────────────────────────────────────────
      document.querySelectorAll(".okr-obj-edit").forEach(btn => {
        btn.addEventListener("click", () => {
          document.getElementById("ks-okr-obj-modal-title").textContent = "Hedefi Düzenle";
          fillObjForm({ title: btn.dataset.title, description: btn.dataset.desc,
            quarter: btn.dataset.quarter, owner: btn.dataset.owner });
          rebindSave(
            document.getElementById("ks-okr-obj-modal-save"),
            () => {
              const d = getObjForm();
              if (!d.title) { toast("Başlık zorunludur.", false); return; }
              fetch(objUrl(btn.dataset.objId), {
                method: "PUT",
                headers: { "Content-Type": "application/json", "X-CSRFToken": CSRF },
                body: JSON.stringify(d),
              }).then(r => r.json()).then(res => {
                if (res.success) { toast("Güncellendi.", true); closeInnerModal(objModal); delete loaded["okr"]; loadOkrModal(); }
                else toast(res.message || "Hata", false);
              }).catch(() => toast("Bağlantı hatası.", false));
            }
          );
          openInnerModal(objModal);
        });
      });

      // ── Objective Sil ─────────────────────────────────────────────────────
      document.querySelectorAll(".okr-obj-del").forEach(btn => {
        btn.addEventListener("click", () => {
          Swal.fire({ title: "Hedefi sil?", text: "Bu hedef ve tüm KR'ları silinecek.",
            icon: "warning", showCancelButton: true,
            confirmButtonText: "Sil", cancelButtonText: "İptal", confirmButtonColor: "#ef4444" })
            .then(r => {
              if (!r.isConfirmed) return;
              fetch(objUrl(btn.dataset.objId), { method: "DELETE", headers: { "X-CSRFToken": CSRF } })
                .then(res => res.json()).then(res => {
                  if (res.success) { toast("Silindi.", true); delete loaded["okr"]; loadOkrModal(); }
                  else toast(res.message || "Hata", false);
                }).catch(() => toast("Bağlantı hatası.", false));
            });
        });
      });

      // ── KR Ekle ───────────────────────────────────────────────────────────
      document.querySelectorAll(".okr-add-kr-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          document.getElementById("ks-okr-kr-modal-title").textContent = "Anahtar Sonuç Ekle";
          fillKrForm();
          rebindSave(
            document.getElementById("ks-okr-kr-modal-save"),
            () => {
              const d = getKrForm();
              if (!d.title) { toast("Başlık zorunludur.", false); return; }
              postJson(OBJ_BASE + btn.dataset.objId + "/kr", d).then(res => {
                if (res.success) { toast("KR eklendi.", true); closeInnerModal(krModal); delete loaded["okr"]; loadOkrModal(); }
                else toast(res.message || "Hata", false);
              }).catch(() => toast("Bağlantı hatası.", false));
            }
          );
          openInnerModal(krModal);
        });
      });

      // ── KR Düzenle ────────────────────────────────────────────────────────
      document.querySelectorAll(".okr-kr-edit").forEach(btn => {
        btn.addEventListener("click", () => {
          document.getElementById("ks-okr-kr-modal-title").textContent = "Anahtar Sonucu Düzenle";
          fillKrForm({ title: btn.dataset.title, metric: btn.dataset.metric,
            start_value: btn.dataset.start, target_value: btn.dataset.target,
            current_value: btn.dataset.current });
          rebindSave(
            document.getElementById("ks-okr-kr-modal-save"),
            () => {
              const d = getKrForm();
              if (!d.title) { toast("Başlık zorunludur.", false); return; }
              fetch(krUrl(btn.dataset.krId), {
                method: "PUT",
                headers: { "Content-Type": "application/json", "X-CSRFToken": CSRF },
                body: JSON.stringify(d),
              }).then(r => r.json()).then(res => {
                if (res.success) { toast("KR güncellendi.", true); closeInnerModal(krModal); delete loaded["okr"]; loadOkrModal(); }
                else toast(res.message || "Hata", false);
              }).catch(() => toast("Bağlantı hatası.", false));
            }
          );
          openInnerModal(krModal);
        });
      });

      // ── KR Sil ────────────────────────────────────────────────────────────
      document.querySelectorAll(".okr-kr-del").forEach(btn => {
        btn.addEventListener("click", () => {
          Swal.fire({ title: "KR silinsin mi?", icon: "warning", showCancelButton: true,
            confirmButtonText: "Sil", cancelButtonText: "İptal", confirmButtonColor: "#ef4444" })
            .then(r => {
              if (!r.isConfirmed) return;
              fetch(krUrl(btn.dataset.krId), { method: "DELETE", headers: { "X-CSRFToken": CSRF } })
                .then(res => res.json()).then(res => {
                  if (res.success) { toast("KR silindi.", true); delete loaded["okr"]; loadOkrModal(); }
                  else toast(res.message || "Hata", false);
                }).catch(() => toast("Bağlantı hatası.", false));
            });
        });
      });
    }

    setHtml("ks-modal-okr-body", '<div class="kr-loading" style="padding:32px;">Yükleniyor…</div>');
    fetchJson(OBJ_URL).then(res => {
      if (!res.success) { setHtml("ks-modal-okr-body", '<div style="color:#ef4444;padding:16px;">Yüklenemedi.</div>'); return; }
      renderOkr(res.data || [], res.year);
    }).catch(() => setHtml("ks-modal-okr-body", '<div style="color:#ef4444;padding:16px;">Yüklenemedi.</div>'));
  }

  // ── BSC Modal ─────────────────────────────────────────────────────────────────
  function loadBscModal() {
    const canManage = hub.dataset.canManage === "true";
    const BSC_URL    = hub.dataset.apiBsc;
    const ASSIGN_URL = hub.dataset.apiBscAssign;

    const PERSPECTIVES = [
      { key: "finansal", label: "Finansal",         icon: "fa-coins",          color: "#6366f1", bg: "#eef2ff" },
      { key: "musteri",  label: "Müşteri",           icon: "fa-users",          color: "#10b981", bg: "#d1fae5" },
      { key: "ic_surec", label: "İç Süreçler",       icon: "fa-gears",          color: "#f59e0b", bg: "#fef3c7" },
      { key: "ogrenme",  label: "Öğrenme & Gelişim", icon: "fa-graduation-cap", color: "#3b82f6", bg: "#dbeafe" },
    ];

    // Atama modal
    const assignModal = document.getElementById("ks-bsc-assign-modal");
    document.getElementById("ks-bsc-assign-close")?.addEventListener("click",  () => assignModal?.classList.remove("open"));
    document.getElementById("ks-bsc-assign-cancel")?.addEventListener("click", () => assignModal?.classList.remove("open"));
    assignModal?.addEventListener("click", e => { if (e.target === assignModal) assignModal.classList.remove("open"); });

    let _assignKpiId   = null;
    let _assignKpiName = "";

    function openAssignModal(kpiId, kpiName, currentPersp) {
      _assignKpiId   = kpiId;
      _assignKpiName = kpiName;
      const nameEl = document.getElementById("ks-bsc-assign-kpi-name");
      if (nameEl) nameEl.textContent = kpiName;
      const sel = document.getElementById("ks-bsc-assign-select");
      if (sel) sel.value = currentPersp || "";
      assignModal?.classList.add("open");
    }

    // Kaydet
    const assignSaveBtn = document.getElementById("ks-bsc-assign-save");
    if (assignSaveBtn) {
      const fresh = assignSaveBtn.cloneNode(true);
      assignSaveBtn.parentNode.replaceChild(fresh, assignSaveBtn);
      fresh.addEventListener("click", () => {
        const perspective = document.getElementById("ks-bsc-assign-select")?.value || "";
        postJson(ASSIGN_URL, { kpi_id: _assignKpiId, perspective })
          .then(r => {
            if (r.success) {
              toast(perspective ? "Perspektif atandı." : "Atama kaldırıldı.", true);
              assignModal?.classList.remove("open");
              delete loaded["bsc"];
              loadBscModal();
            } else toast(r.message || "Hata", false);
          }).catch(() => toast("Bağlantı hatası.", false));
      });
    }

    function renderBsc(data) {
      const year = data.year;
      const persp = data.perspectives || {};
      const unassigned = data.unassigned || [];
      const stratMap = data.strategy_map || [];

      // ── Sekmeler ──────────────────────────────────────────────────────────
      const tabs = [
        { id: "bsc-tab-kart",    label: "Kart Görünümü",    icon: "fa-table-cells-large" },
        { id: "bsc-tab-tablo",   label: "KPI Tablosu",      icon: "fa-table" },
        { id: "bsc-tab-harita",  label: "Strateji Haritası", icon: "fa-sitemap" },
        { id: "bsc-tab-atama",   label: "Perspektif Ata",   icon: "fa-tag" },
      ];

      const tabHtml = tabs.map((t, i) => `
        <button class="bsc-tab ${i === 0 ? "active" : ""}" data-bsc-tab="${t.id}">
          <i class="fas ${t.icon}"></i> ${t.label}
        </button>`).join("");

      // ── Kart Görünümü ─────────────────────────────────────────────────────
      const kartsHtml = PERSPECTIVES.map(p => {
        const pd = persp[p.key] || { kpi_count: 0, score: null, kpis: [] };
        const kpiRows = pd.kpis.map(k => {
          const pct = k.perf_pct;
          const barW = pct != null ? Math.min(100, pct) : 0;
          const assignBtn = canManage ? `<button class="ks-item-btn bsc-assign-btn" data-kpi-id="${k.id}" data-kpi-name="${esc(k.name)}" data-current="${esc(k.perspective||'')}" title="Perspektif değiştir"><i class="fas fa-tag"></i></button>` : "";
          return `<div class="bsc-kpi-row">
            <div class="bsc-kpi-info">
              <span class="bsc-kpi-code">${esc(k.code)}</span>
              <span class="bsc-kpi-name" title="${esc(k.name)}">${esc(k.name)}</span>
              <span class="bsc-kpi-proc">${esc(k.process_code)} ${esc(k.process_name)}</span>
            </div>
            <div class="bsc-kpi-perf">
              <div class="kr-perf-bar-track" style="width:80px;"><div class="kr-perf-bar-fill" style="width:${barW}%;background:${scoreColor(pct)};"></div></div>
              <span style="font-size:12px;font-weight:700;color:${scoreColor(pct)};min-width:36px;text-align:right;">${pct != null ? pct + "%" : "—"}</span>
            </div>
            ${assignBtn}
          </div>`;
        }).join("") || `<div style="font-size:12px;color:#94a3b8;padding:8px 0;">Bu perspektife atanmış KPI yok.</div>`;

        return `<div class="bsc-persp-card" style="border-top:3px solid ${p.color};">
          <div class="bsc-persp-header" style="background:${p.bg};">
            <div style="display:flex;align-items:center;gap:8px;">
              <span style="width:32px;height:32px;border-radius:8px;background:${p.color};display:flex;align-items:center;justify-content:center;color:white;font-size:14px;"><i class="fas ${p.icon}"></i></span>
              <span style="font-weight:700;color:${p.color};font-size:14px;">${p.label}</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
              <span class="mc-badge" style="background:${p.color}20;color:${p.color};">${pd.kpi_count} KPI</span>
              ${pd.score != null ? `<span style="font-size:18px;font-weight:800;color:${scoreColor(pd.score)};">${pd.score}%</span>` : ""}
            </div>
          </div>
          <div class="bsc-kpi-list">${kpiRows}</div>
        </div>`;
      }).join("");

      // ── KPI Tablosu ───────────────────────────────────────────────────────
      const allKpis = PERSPECTIVES.flatMap(p => (persp[p.key]?.kpis || []).map(k => ({ ...k, persp_label: p.label, persp_color: p.color })));
      const tableRows = allKpis.map(k => {
        const pct = k.perf_pct;
        const assignBtn = canManage ? `<button class="ks-item-btn bsc-assign-btn" data-kpi-id="${k.id}" data-kpi-name="${esc(k.name)}" data-current="${esc(k.perspective||'')}" title="Perspektif değiştir"><i class="fas fa-tag"></i></button>` : "";
        return `<tr>
          <td><span class="mc-badge" style="background:${k.persp_color}20;color:${k.persp_color};font-size:10px;">${k.persp_label}</span></td>
          <td style="font-size:11px;color:#6366f1;">${esc(k.code)}</td>
          <td style="font-size:12px;">${esc(k.name)}</td>
          <td style="font-size:11px;">${esc(k.process_code)} ${esc(k.process_name)}</td>
          <td style="font-size:11px;">${esc(k.strategy_code||'')} ${esc(k.strategy_title||'—')}</td>
          <td style="font-weight:700;color:${scoreColor(pct)}">${pct != null ? pct + "%" : "—"}</td>
          <td>${assignBtn}</td>
        </tr>`;
      }).join("") || `<tr><td colspan="7" style="text-align:center;padding:20px;color:#94a3b8;">Atanmış KPI yok.</td></tr>`;

      // ── Strateji Haritası ─────────────────────────────────────────────────
      const haritaHtml = stratMap.map(s => {
        const subsHtml = s.sub_strategies.map(ss => {
          const kpiChips = ss.kpis.map(k => {
            const p = PERSPECTIVES.find(p => p.key === k.perspective);
            const pColor = p ? p.color : "#94a3b8";
            const pLabel = p ? p.label : "Atanmamış";
            return `<span class="bsc-map-kpi-chip" style="border-color:${pColor};" title="${esc(k.name)} — ${pLabel}">
              <span style="width:8px;height:8px;border-radius:50%;background:${pColor};display:inline-block;"></span>
              ${esc(k.code || k.name.slice(0,20))}
              ${k.perf_pct != null ? `<span style="color:${scoreColor(k.perf_pct)};font-weight:700;">${k.perf_pct}%</span>` : ""}
            </span>`;
          }).join("");
          return `<div class="bsc-map-sub">
            <div class="bsc-map-sub-header">
              <span class="bsc-map-sub-code">${esc(ss.code)}</span>
              <span class="bsc-map-sub-title">${esc(ss.title)}</span>
              ${ss.score != null ? `<span style="font-size:12px;font-weight:700;color:${scoreColor(ss.score)};">${ss.score}%</span>` : ""}
            </div>
            <div class="bsc-map-kpi-chips">${kpiChips}</div>
          </div>`;
        }).join("");
        return `<div class="bsc-map-strat">
          <div class="bsc-map-strat-header">
            <span class="bsc-map-strat-code">${esc(s.code)}</span>
            <span class="bsc-map-strat-title">${esc(s.title)}</span>
            ${s.score != null ? `<span style="font-size:14px;font-weight:800;color:${scoreColor(s.score)};">${s.score}%</span>` : ""}
          </div>
          <div class="bsc-map-subs">${subsHtml}</div>
        </div>`;
      }).join("") || `<div style="text-align:center;padding:32px;color:#94a3b8;">Strateji bağlantısı olan KPI bulunamadı.</div>`;

      // ── Perspektif Ata ────────────────────────────────────────────────────
      const atamaRows = [...allKpis, ...unassigned.map(k => ({ ...k, persp_label: "—", persp_color: "#94a3b8" }))];
      const atamaHtml = atamaRows.map(k => {
        const p = PERSPECTIVES.find(p => p.key === k.perspective);
        const badge = p
          ? `<span class="mc-badge" style="background:${p.color}20;color:${p.color};font-size:10px;">${p.label}</span>`
          : `<span class="mc-badge mc-badge-gray" style="font-size:10px;">Atanmamış</span>`;
        const btn = canManage ? `<button class="mc-btn mc-btn-secondary mc-btn-sm bsc-assign-btn" data-kpi-id="${k.id}" data-kpi-name="${esc(k.name)}" data-current="${esc(k.perspective||'')}"><i class="fas fa-tag"></i> Ata</button>` : "";
        return `<tr>
          <td>${badge}</td>
          <td style="font-size:11px;color:#6366f1;">${esc(k.code)}</td>
          <td style="font-size:12px;">${esc(k.name)}</td>
          <td style="font-size:11px;">${esc(k.process_code)} ${esc(k.process_name)}</td>
          <td>${btn}</td>
        </tr>`;
      }).join("") || `<tr><td colspan="5" style="text-align:center;padding:20px;color:#94a3b8;">KPI bulunamadı.</td></tr>`;

      // ── Tümünü birleştir ──────────────────────────────────────────────────
      setHtml("ks-modal-bsc-body", `
        <div style="padding:16px 20px 0;">
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;">
            ${PERSPECTIVES.map(p => {
              const pd = persp[p.key] || {};
              return `<span class="mc-badge" style="background:${p.color}20;color:${p.color};">
                <i class="fas ${p.icon}"></i> ${p.label}: ${pd.kpi_count || 0} KPI ${pd.score != null ? "· " + pd.score + "%" : ""}
              </span>`;
            }).join("")}
            <span class="mc-badge mc-badge-gray">${unassigned.length} atanmamış</span>
            <span style="font-size:12px;color:#94a3b8;margin-left:auto;">${year} yılı</span>
          </div>
          <div class="bsc-tabs">${tabHtml}</div>
        </div>
        <div style="padding:16px 20px;">
          <div id="bsc-tab-kart"   class="bsc-panel active"><div class="bsc-persp-grid">${kartsHtml}</div></div>
          <div id="bsc-tab-tablo"  class="bsc-panel">
            <div class="mc-table-wrap"><table class="mc-table">
              <thead><tr><th>Perspektif</th><th>Kod</th><th>KPI</th><th>Süreç</th><th>Strateji</th><th>Başarı</th><th></th></tr></thead>
              <tbody>${tableRows}</tbody>
            </table></div>
          </div>
          <div id="bsc-tab-harita" class="bsc-panel"><div class="bsc-map-wrap">${haritaHtml}</div></div>
          <div id="bsc-tab-atama"  class="bsc-panel">
            <div class="mc-table-wrap"><table class="mc-table">
              <thead><tr><th>Perspektif</th><th>Kod</th><th>KPI</th><th>Süreç</th><th></th></tr></thead>
              <tbody>${atamaHtml}</tbody>
            </table></div>
          </div>
        </div>`);

      // Sekme geçişi
      document.querySelectorAll(".bsc-tab").forEach(btn => {
        btn.addEventListener("click", () => {
          document.querySelectorAll(".bsc-tab").forEach(b => b.classList.remove("active"));
          document.querySelectorAll(".bsc-panel").forEach(p => p.classList.remove("active"));
          btn.classList.add("active");
          document.getElementById(btn.dataset.bscTab)?.classList.add("active");
        });
      });

      // Atama butonları
      document.querySelectorAll(".bsc-assign-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          openAssignModal(btn.dataset.kpiId, btn.dataset.kpiName, btn.dataset.current);
        });
      });
    }

    setHtml("ks-modal-bsc-body", '<div class="kr-loading" style="padding:32px;">Yükleniyor…</div>');
    fetchJson(BSC_URL).then(res => {
      if (!res.success) { setHtml("ks-modal-bsc-body", '<div style="color:#ef4444;padding:16px;">Yüklenemedi.</div>'); return; }
      renderBsc(res);
    }).catch(() => setHtml("ks-modal-bsc-body", '<div style="color:#ef4444;padding:16px;">Yüklenemedi.</div>'));
  }

  // ── GAP Modal ─────────────────────────────────────────────────────────────────
  let gapModalChart = null;
  function loadGapModal() {
    setHtml("ks-modal-gap-body", '<div class="kr-loading" style="padding:32px;">Yükleniyor…</div>');
    fetchJson(API.gap).then(res => {
      if (!res.success) { setHtml("ks-modal-gap-body", '<div style="color:#ef4444;padding:16px;">Yüklenemedi.</div>'); return; }
      const d = res.data;
      const rows = d.surec_gap_listesi || [];
      setHtml("ks-modal-gap-body", `
        <div class="mc-grid-4" style="margin-bottom:16px;">
          <div class="mc-stat-card mc-stat-indigo">
            <div class="mc-stat-label">Toplam PG</div>
            <div class="mc-stat-value">${d.toplam_kpi}</div>
          </div>
          <div class="mc-stat-card mc-stat-emerald">
            <div class="mc-stat-label">Hedefte</div>
            <div class="mc-stat-value">${d.hedefte}</div>
          </div>
          <div class="mc-stat-card mc-stat-amber">
            <div class="mc-stat-label">Riskli</div>
            <div class="mc-stat-value">${d.riskli}</div>
          </div>
          <div class="mc-stat-card" style="background:#fef2f2;">
            <div class="mc-stat-label">Kritik</div>
            <div class="mc-stat-value" style="color:#ef4444;">${d.kritik}</div>
          </div>
        </div>
        <div class="mc-table-wrap"><table class="mc-table">
          <thead><tr><th>Kod</th><th>Süreç</th><th>KPI</th><th>Ort. Başarı</th><th>GAP</th><th>Durum</th></tr></thead>
          <tbody>${rows.map(r => {
            const durumBadge = r.durum === "hedefte"
              ? '<span class="mc-badge mc-badge-success">Hedefte</span>'
              : r.durum === "riskli"
              ? '<span class="mc-badge mc-badge-warning">Riskli</span>'
              : '<span class="mc-badge mc-badge-danger">Kritik</span>';
            const gapColor = r.gap >= 0 ? "#10b981" : r.gap >= -50 ? "#f59e0b" : "#ef4444";
            return `<tr>
              <td style="font-size:11px;color:#6366f1;">${esc(r.code)}</td>
              <td style="font-size:12px;">${esc(r.name)}</td>
              <td style="text-align:center;">${r.kpi_count}</td>
              <td><div class="kr-perf-bar-wrap">
                <div class="kr-perf-bar-track"><div class="kr-perf-bar-fill" style="width:${r.ort_basari}%;background:${scoreColor(r.ort_basari)};"></div></div>
                <div class="kr-perf-pct" style="color:${scoreColor(r.ort_basari)}">${r.ort_basari}%</div>
              </div></td>
              <td style="font-weight:700;color:${gapColor};">${r.gap >= 0 ? "+" : ""}${r.gap}%</td>
              <td>${durumBadge}</td>
            </tr>`;
          }).join("") || EMPTY_ROW(6)}</tbody>
        </table></div>`);

      // Bar chart
      const canvas = document.getElementById("ks-gap-modal-chart");
      if (canvas && rows.length) {
        if (gapModalChart) gapModalChart.destroy();
        const top12 = rows.slice(0, 12);
        gapModalChart = new Chart(canvas, {
          type: "bar",
          data: {
            labels: top12.map(r => (r.code ? r.code + " " : "") + (r.name.length > 18 ? r.name.slice(0,18)+"…" : r.name)),
            datasets: [{ label: "Ort. Başarı %", data: top12.map(r => r.ort_basari),
              backgroundColor: top12.map(r => scoreColor(r.ort_basari) + "cc"), borderRadius: 4 }]
          },
          options: { indexAxis: "y", responsive: true, plugins: { legend: { display: false } },
            scales: { x: { beginAtZero: true, max: 100, ticks: { callback: v => v + "%" } } } }
        });
      }
    }).catch(() => setHtml("ks-modal-gap-body", '<div style="color:#ef4444;padding:16px;">Yüklenemedi.</div>'));
  }

})();
