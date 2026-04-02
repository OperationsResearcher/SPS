/**
 * sp.js — Stratejik Planlama modülü JS
 * Kural: alert()/confirm()/prompt() YASAK — SweetAlert2 (toast/hata/onay); formlar openMcFormModal (base.html)
 * Kural: Jinja2 {{ }} bu dosyada YASAK — veri data-* ile gelir
 */

(function () {
  "use strict";

  // ── Yardımcılar ───────────────────────────────────────────────────────────
  function getCsrf() {
    const m = document.querySelector('meta[name="csrf-token"]');
    return m ? m.content : "";
  }

  async function postJson(url, body) {
    const res = await fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrf() },
      body: JSON.stringify(body),
    });
    const ct = res.headers.get("content-type") || "";
    if (!ct.includes("application/json")) {
      const snippet = await res.text();
      const isHtml = snippet.trim().toLowerCase().startsWith("<!doctype") || snippet.includes("<html");
      if (res.status === 400 && isHtml) {
        throw new Error("Oturum veya güvenlik doğrulaması başarısız. Sayfayı yenileyip tekrar deneyin.");
      }
      if (res.status === 302 || res.status === 401 || res.status === 403) {
        throw new Error("Oturum süresi dolmuş olabilir. Yeniden giriş yapın.");
      }
      throw new Error("Sunucu JSON yerine HTML döndü (HTTP " + res.status + ").");
    }
    return res.json();
  }

  function toastSuccess(msg) {
    Swal.fire({
      toast: true, position: "top-end", icon: "success",
      title: msg, showConfirmButton: false, timer: 2500, timerProgressBar: true,
    });
  }

  function showError(msg) {
    Swal.fire({ icon: "error", title: "Hata", text: msg, confirmButtonColor: "#dc2626" });
  }

  async function confirmDelete(title, text) {
    const r = await Swal.fire({
      title: title || "Emin misiniz?", text: text || "Bu işlem geri alınamaz.",
      icon: "warning", showCancelButton: true,
      confirmButtonColor: "#dc2626", cancelButtonColor: "#6b7280",
      confirmButtonText: "Evet, sil", cancelButtonText: "İptal",
    });
    return r.isConfirmed;
  }

  function escHtml(s) {
    if (!s) return "";
    return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // SP INDEX SAYFASI
  // ═══════════════════════════════════════════════════════════════════════════
  const spRoot = document.getElementById("sp-index");
  if (spRoot) {
    const ADD_STRATEGY_URL    = spRoot.dataset.addStrategyUrl;
    const DELETE_STRATEGY_BASE = spRoot.dataset.deleteStrategyBase;
    const UPDATE_STRATEGY_BASE = spRoot.dataset.updateStrategyBase;
    const ADD_SUB_URL         = spRoot.dataset.addSubStrategyUrl;
    const UPDATE_SUB_BASE     = spRoot.dataset.updateSubStrategyBase;
    const DELETE_SUB_BASE     = spRoot.dataset.deleteSubStrategyBase;
    const UPDATE_IDENTITY_URL = spRoot.dataset.updateIdentityUrl;
    const URL_SUREC           = spRoot.dataset.urlSurec;
    const URL_BIREYSEL        = spRoot.dataset.urlBireysel;
    const initialPurpose      = spRoot.dataset.initialPurpose || "";
    const initialVision       = spRoot.dataset.initialVision || "";
    const initialCoreValues   = spRoot.dataset.initialCoreValues || "";
    const initialEthics       = spRoot.dataset.initialEthics || "";
    const KV_ENABLED          = spRoot.dataset.kvEnabled === "true";

    function decodeAttr(s) {
      if (!s) return "";
      const ta = document.createElement("textarea");
      ta.innerHTML = s;
      return ta.value;
    }

    function triggerAddStrategy() {
      const el = document.getElementById("btn-strategy-add") || document.getElementById("btn-strategy-add-empty");
      if (el) el.click();
    }

    function getSpCardHelpMap() {
      const el = document.getElementById("sp-card-help-json");
      if (!el) return {};
      try {
        return JSON.parse(el.textContent);
      } catch (err) {
        return {};
      }
    }

    /** Kart gövdesine tıklanınca kalem ile aynı işlem (modal veya yönlendirme) */
    spRoot.addEventListener("click", (e) => {
      const wrap = e.target.closest(".mc-sp-card-body-trigger");
      if (!wrap) return;
      e.preventDefault();
      e.stopPropagation();
      const kind = wrap.getAttribute("data-sp-body-edit");
      if (!kind) return;
      const card = wrap.closest(".mc-sp-flow-card");
      if (!card) return;
      const editBtn = card.querySelector('.btn-sp-card-edit[data-sp-edit="' + kind + '"]');
      if (editBtn) {
        editBtn.click();
        return;
      }
      const infoBtn = card.querySelector(".btn-sp-card-info[data-sp-help]");
      if (infoBtn) {
        infoBtn.click();
      }
    });

    spRoot.addEventListener("click", async (e) => {
      const infoBtn = e.target.closest(".btn-sp-card-info");
      if (infoBtn) {
        e.preventDefault();
        e.stopPropagation();
        const key = infoBtn.getAttribute("data-sp-help");
        if (!key) return;
        const map = getSpCardHelpMap();
        const h = map[key];
        if (!h || !h.title) return;
        await openMcInfoModal({
          title: h.title,
          bodyHtml: h.html || "",
          iconClass: "fas fa-circle-info",
          confirmText: "Tamam",
        });
        return;
      }
    });

    spRoot.addEventListener("click", async (e) => {
      const editBtn = e.target.closest(".btn-sp-card-edit");
      if (!editBtn) return;
      e.preventDefault();
      e.stopPropagation();
      const kind = editBtn.getAttribute("data-sp-edit");
      if (kind === "misyon") {
        const payload = await openMcFormModal({
          title: "Misyon (Amaç) düzenle",
          iconClass: "fas fa-bullseye",
          bodyHtml: `<div class="tm-field tm-full">
            <label class="mc-form-label">Amaç / Misyon</label>
            <textarea id="sp-modal-mission" class="mc-form-input" rows="8" placeholder="Kurum misyonunu yazın...">${escHtml(decodeAttr(initialPurpose))}</textarea>
          </div>`,
          confirmText: "Kaydet",
          onConfirm: function () {
            var ta = document.getElementById("sp-modal-mission");
            return { purpose: ta ? ta.value : "" };
          },
        });
        if (payload === null) return;
        try {
          const d = await postJson(UPDATE_IDENTITY_URL, payload);
          if (d.success) { toastSuccess(d.message || "Kaydedildi."); setTimeout(() => location.reload(), 800); }
          else showError(d.message || "Kayıt başarısız.");
        } catch (err) { showError("Sunucu hatası: " + err.message); }
        return;
      }
      if (kind === "vizyon") {
        const payload = await openMcFormModal({
          title: "Vizyon düzenle",
          iconClass: "fas fa-binoculars",
          bodyHtml: `<div class="tm-field tm-full">
            <label class="mc-form-label">Vizyon</label>
            <textarea id="sp-modal-vision" class="mc-form-input" rows="8" placeholder="Kurum vizyonunu yazın...">${escHtml(decodeAttr(initialVision))}</textarea>
          </div>`,
          confirmText: "Kaydet",
          onConfirm: function () {
            var ta = document.getElementById("sp-modal-vision");
            return { vision: ta ? ta.value : "" };
          },
        });
        if (payload === null) return;
        try {
          const d = await postJson(UPDATE_IDENTITY_URL, payload);
          if (d.success) { toastSuccess(d.message || "Kaydedildi."); setTimeout(() => location.reload(), 800); }
          else showError(d.message || "Kayıt başarısız.");
        } catch (err) { showError("Sunucu hatası: " + err.message); }
        return;
      }
      if (kind === "degerler") {
        const vals = await openMcFormModal({
          title: "Değerler ve etik kuralları",
          iconClass: "fas fa-heart",
          bodyHtml: `<div class="tm-grid-2">
            <div class="tm-field tm-full">
              <label class="mc-form-label">Temel değerler</label>
              <textarea id="sp-modal-cv" class="mc-form-input" rows="5" placeholder="Değerler...">${escHtml(decodeAttr(initialCoreValues))}</textarea>
            </div>
            <div class="tm-field tm-full">
              <label class="mc-form-label">Etik kurallar</label>
              <textarea id="sp-modal-eth" class="mc-form-input" rows="5" placeholder="Etik kurallar...">${escHtml(decodeAttr(initialEthics))}</textarea>
            </div>
          </div>`,
          confirmText: "Kaydet",
          onConfirm: function () {
            return {
              core_values: document.getElementById("sp-modal-cv").value,
              code_of_ethics: document.getElementById("sp-modal-eth").value,
            };
          },
        });
        if (vals === null) return;
        try {
          const d = await postJson(UPDATE_IDENTITY_URL, vals);
          if (d.success) { toastSuccess(d.message || "Kaydedildi."); setTimeout(() => location.reload(), 800); }
          else showError(d.message || "Kayıt başarısız.");
        } catch (err) { showError("Sunucu hatası: " + err.message); }
        return;
      }
      if (kind === "strateji-listesi") {
        const target = document.getElementById("strategy-list");
        if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
        setTimeout(triggerAddStrategy, 400);
        return;
      }
      if (kind === "surec" || kind === "surec-hedef") {
        if (URL_SUREC) window.location.href = URL_SUREC;
        return;
      }
      if (kind === "bireysel") {
        if (URL_BIREYSEL) window.location.href = URL_BIREYSEL;
      }
    });

    document.addEventListener("click", async (e) => {
      const btn = e.target.closest(".btn-main-edit");
      if (!btn) return;
      e.preventDefault();
      e.stopPropagation();
      const sid = btn.dataset.strategyId;
      const currentTitle = btn.dataset.title || "";
      const currentCode = btn.dataset.code || "";
      const currentDesc = btn.dataset.description || "";
      const kvRawMain = KV_ENABLED ? (btn.dataset.kvWeightRaw || "") : "";
      const kvBlockMain = KV_ENABLED
        ? `<div class="tm-field tm-full">
            <label class="mc-form-label">K-Vektör ham ağırlık (vizyon 1000)</label>
            <input type="number" step="any" id="sp-modal-main-kv-weight" class="mc-form-input" placeholder="Boş = eşit dağıtım" value="${escHtml(kvRawMain)}">
            <p style="font-size:12px;color:#64748b;margin:6px 0 0;line-height:1.4;">Boş bırakırsanız bu ana strateji için eşit dağıtım uygulanır.</p>
          </div>`
        : "";
      const vals = await openMcFormModal({
        title: "Ana strateji düzenle",
        iconClass: "fas fa-chess",
        bodyHtml: `<div class="tm-grid-2">
          <div class="tm-field tm-full">
            <label class="mc-form-label">Başlık <span class="req">*</span></label>
            <input id="sp-modal-main-title" type="text" class="mc-form-input" value="${escHtml(currentTitle)}" placeholder="Strateji başlığı">
          </div>
          <div class="tm-field tm-full">
            <label class="mc-form-label">Kod</label>
            <input id="sp-modal-main-code" type="text" class="mc-form-input" value="${escHtml(currentCode)}" placeholder="Örn: ST1">
          </div>
          <div class="tm-field tm-full">
            <label class="mc-form-label">Açıklama</label>
            <textarea id="sp-modal-main-desc" class="mc-form-input" rows="4" placeholder="Kısa açıklama">${escHtml(currentDesc)}</textarea>
          </div>
          ${kvBlockMain}
        </div>`,
        confirmText: "Güncelle",
        onConfirm: function (ctx) {
          var title = document.getElementById("sp-modal-main-title").value.trim();
          if (!title) { ctx.showValidation("Başlık zorunludur."); return false; }
          var out = {
            title: title,
            code: document.getElementById("sp-modal-main-code").value.trim() || null,
            description: document.getElementById("sp-modal-main-desc").value.trim() || null,
          };
          if (KV_ENABLED) {
            var w = document.getElementById("sp-modal-main-kv-weight");
            if (w) {
              var tw = w.value.trim();
              out.k_vektor_weight_raw = tw === "" ? null : tw;
            }
          }
          return out;
        },
      });
      if (vals === null) return;
      try {
        const d = await postJson(UPDATE_STRATEGY_BASE + sid, vals);
        if (d.success) { toastSuccess(d.message || "Güncellendi."); setTimeout(() => location.reload(), 800); }
        else showError(d.message || "Güncelleme başarısız.");
      } catch (err) { showError("Sunucu hatası: " + err.message); }
    });

    // Ana strateji ekle
    async function onAddStrategyClick() {
      const vals = await openMcFormModal({
        title: "Yeni Strateji Ekle",
        iconClass: "fas fa-plus-circle",
        bodyHtml: `<div class="tm-grid-2">
          <div class="tm-field tm-full">
            <label class="mc-form-label">Başlık <span class="req">*</span></label>
            <input id="sp-modal-add-title" type="text" class="mc-form-input" placeholder="Strateji başlığı">
          </div>
          <div class="tm-field tm-full">
            <label class="mc-form-label">Kod</label>
            <input id="sp-modal-add-code" type="text" class="mc-form-input" placeholder="Örn: ST1">
          </div>
          <div class="tm-field tm-full">
            <label class="mc-form-label">Açıklama</label>
            <textarea id="sp-modal-add-desc" class="mc-form-input" rows="4" placeholder="Kısa açıklama"></textarea>
          </div>
        </div>`,
        confirmText: "Kaydet",
        onConfirm: function (ctx) {
          var title = document.getElementById("sp-modal-add-title").value.trim();
          if (!title) { ctx.showValidation("Başlık zorunludur."); return false; }
          return {
            title: title,
            code: document.getElementById("sp-modal-add-code").value.trim() || null,
            description: document.getElementById("sp-modal-add-desc").value.trim() || null,
          };
        },
      });
      if (vals === null) return;
      try {
        const d = await postJson(ADD_STRATEGY_URL, vals);
        if (d.success) { toastSuccess("Strateji eklendi."); setTimeout(() => location.reload(), 1200); }
        else showError(d.message || "Kayıt başarısız.");
      } catch (e) { showError("Sunucu hatası: " + e.message); }
    }
    document.getElementById("btn-strategy-add")?.addEventListener("click", onAddStrategyClick);
    document.getElementById("btn-strategy-add-empty")?.addEventListener("click", onAddStrategyClick);

    // Alt strateji ekle
    document.addEventListener("click", async (e) => {
      const btn = e.target.closest(".btn-sub-add");
      if (!btn) return;
      const strategyId = btn.dataset.strategyId;
      const vals = await openMcFormModal({
        title: "Alt Strateji Ekle",
        iconClass: "fas fa-layer-group",
        bodyHtml: `<div class="tm-grid-2">
          <div class="tm-field tm-full">
            <label class="mc-form-label">Başlık <span class="req">*</span></label>
            <input id="sp-modal-sub-add-title" type="text" class="mc-form-input" placeholder="Alt strateji başlığı">
          </div>
          <div class="tm-field tm-full">
            <label class="mc-form-label">Kod</label>
            <input id="sp-modal-sub-add-code" type="text" class="mc-form-input" placeholder="Örn: ST1.1">
          </div>
        </div>`,
        confirmText: "Kaydet",
        onConfirm: function (ctx) {
          var title = document.getElementById("sp-modal-sub-add-title").value.trim();
          if (!title) { ctx.showValidation("Başlık zorunludur."); return false; }
          return {
            strategy_id: strategyId,
            title: title,
            code: document.getElementById("sp-modal-sub-add-code").value.trim() || null,
          };
        },
      });
      if (vals === null) return;
      try {
        const d = await postJson(ADD_SUB_URL, vals);
        if (d.success) { toastSuccess("Alt strateji eklendi."); setTimeout(() => location.reload(), 1200); }
        else showError(d.message || "Kayıt başarısız.");
      } catch (e) { showError("Sunucu hatası: " + e.message); }
    });

    // Alt strateji güncelle
    document.addEventListener("click", async (e) => {
      const btn = e.target.closest(".btn-sub-edit");
      if (!btn) return;
      const subId = btn.dataset.subId;
      const currentTitle = btn.dataset.title || "";
      const currentCode  = btn.dataset.code  || "";
      const kvRawSub = KV_ENABLED ? (btn.dataset.kvWeightRaw || "") : "";
      const kvBlockSub = KV_ENABLED
        ? `<div class="tm-field tm-full">
            <label class="mc-form-label">K-Vektör ham ağırlık (vizyon 1000)</label>
            <input type="number" step="any" id="sp-modal-sub-kv-weight" class="mc-form-input" placeholder="Boş = eşit dağıtım" value="${escHtml(kvRawSub)}">
            <p style="font-size:12px;color:#64748b;margin:6px 0 0;line-height:1.4;">Boş bırakırsanız bu alt strateji için eşit dağıtım uygulanır.</p>
          </div>`
        : "";
      const vals = await openMcFormModal({
        title: "Alt Strateji Düzenle",
        iconClass: "fas fa-pen-to-square",
        bodyHtml: `<div class="tm-grid-2">
          <div class="tm-field tm-full">
            <label class="mc-form-label">Başlık <span class="req">*</span></label>
            <input id="sp-modal-sub-edit-title" type="text" class="mc-form-input" value="${escHtml(currentTitle)}">
          </div>
          <div class="tm-field tm-full">
            <label class="mc-form-label">Kod</label>
            <input id="sp-modal-sub-edit-code" type="text" class="mc-form-input" value="${escHtml(currentCode)}">
          </div>
          ${kvBlockSub}
        </div>`,
        confirmText: "Güncelle",
        onConfirm: function (ctx) {
          var title = document.getElementById("sp-modal-sub-edit-title").value.trim();
          if (!title) { ctx.showValidation("Başlık zorunludur."); return false; }
          var out = {
            title: title,
            code: document.getElementById("sp-modal-sub-edit-code").value.trim() || null,
          };
          if (KV_ENABLED) {
            var w = document.getElementById("sp-modal-sub-kv-weight");
            if (w) {
              var tw = w.value.trim();
              out.k_vektor_weight_raw = tw === "" ? null : tw;
            }
          }
          return out;
        },
      });
      if (vals === null) return;
      try {
        const d = await postJson(`${UPDATE_SUB_BASE}${subId}`, vals);
        if (d.success) { toastSuccess("Alt strateji güncellendi."); setTimeout(() => location.reload(), 1200); }
        else showError(d.message || "Güncelleme başarısız.");
      } catch (e) { showError("Sunucu hatası: " + e.message); }
    });

    // Ana strateji sil
    document.addEventListener("click", async (e) => {
      const btn = e.target.closest(".btn-strategy-delete");
      if (!btn) return;
      const ok = await confirmDelete("Strateji silinsin mi?", `"${btn.dataset.title}" pasife alınacak.`);
      if (!ok) return;
      try {
        const d = await postJson(`${DELETE_STRATEGY_BASE}${btn.dataset.strategyId}`, {});
        if (d.success) { toastSuccess("Strateji silindi."); setTimeout(() => location.reload(), 1200); }
        else showError(d.message || "Silme başarısız.");
      } catch (e) { showError("Sunucu hatası: " + e.message); }
    });

    // Alt strateji sil
    document.addEventListener("click", async (e) => {
      const btn = e.target.closest(".btn-sub-delete");
      if (!btn) return;
      const ok = await confirmDelete("Alt strateji silinsin mi?", `"${btn.dataset.title}" pasife alınacak.`);
      if (!ok) return;
      try {
        const d = await postJson(`${DELETE_SUB_BASE}${btn.dataset.subId}`, {});
        if (d.success) { toastSuccess("Alt strateji silindi."); setTimeout(() => location.reload(), 1200); }
        else showError(d.message || "Silme başarısız.");
      } catch (e) { showError("Sunucu hatası: " + e.message); }
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // DİNAMİK GRAF SAYFASI
  // ═══════════════════════════════════════════════════════════════════════════
  const graphRoot = document.getElementById("sp-graph-root");
  if (!graphRoot) return;

  const GRAPH_API = graphRoot.dataset.graphApiUrl;
  const loadingEl  = document.getElementById("graph-loading");
  const containerEl = document.getElementById("graph-container");
  const emptyEl    = document.getElementById("graph-empty");

  // Renk haritası
  const NODE_COLORS = {
    vision:       "#6366f1",
    strategy:     "#7c3aed",
    sub_strategy: "#60a5fa",
    process:      "#10b981",
    kpi:          "#f59e0b",
  };

  async function loadGraph() {
    loadingEl.classList.remove("hidden");
    containerEl.style.display = "none";
    emptyEl.classList.add("hidden");

    try {
      const res = await fetch(GRAPH_API);
      const data = await res.json();
      if (!data.success) throw new Error(data.message || "Graf verisi alınamadı.");
      if (!data.nodes || data.nodes.length === 0) {
        emptyEl.classList.remove("hidden");
        return;
      }
      renderGraph(data.nodes, data.edges);
      containerEl.style.display = "block";
    } catch (err) {
      showError("Graf yüklenirken hata: " + err.message);
    } finally {
      loadingEl.classList.add("hidden");
    }
  }

  function renderGraph(nodes, edges) {
    // Basit SVG tabanlı hiyerarşik render (vis.js bağımlılığı olmadan)
    const canvas = document.getElementById("graph-canvas");
    const W = containerEl.clientWidth || 900;
    const ROW_H = 90;
    const NODE_W = 160;
    const NODE_H = 40;

    // Katmanlara göre grupla
    const layers = { vision: [], strategy: [], sub_strategy: [], process: [], kpi: [] };
    nodes.forEach(n => { if (layers[n.type]) layers[n.type].push(n); });

    const layerOrder = ["vision", "strategy", "sub_strategy", "process", "kpi"];
    const posMap = {};
    let svgRows = [];

    layerOrder.forEach((type, rowIdx) => {
      const group = layers[type];
      if (!group.length) return;
      const totalW = group.length * (NODE_W + 20);
      const startX = Math.max(20, (W - totalW) / 2);
      group.forEach((n, i) => {
        const x = startX + i * (NODE_W + 20);
        const y = rowIdx * ROW_H + 20;
        posMap[n.id] = { x: x + NODE_W / 2, y: y + NODE_H / 2 };
        const color = NODE_COLORS[type] || "#9ca3af";
        svgRows.push(
          `<rect x="${x}" y="${y}" width="${NODE_W}" height="${NODE_H}" rx="8"
                fill="${color}" opacity="0.9"/>
           <text x="${x + NODE_W / 2}" y="${y + NODE_H / 2 + 4}"
                 text-anchor="middle" fill="white" font-size="11"
                 font-family="sans-serif">${escHtml(n.label.substring(0, 22))}</text>`
        );
      });
    });

    // Edge'leri çiz
    const edgeSvg = edges.map(e => {
      const from = posMap[e.from];
      const to   = posMap[e.to];
      if (!from || !to) return "";
      return `<line x1="${from.x}" y1="${from.y}" x2="${to.x}" y2="${to.y}"
                    stroke="#d1d5db" stroke-width="1.5" marker-end="url(#arrow)"/>`;
    }).join("");

    const totalH = layerOrder.filter(t => layers[t].length).length * ROW_H + 60;
    canvas.outerHTML = `<svg id="graph-canvas" width="${W}" height="${totalH}"
        xmlns="http://www.w3.org/2000/svg" style="width:100%;">
      <defs>
        <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
          <path d="M0,0 L0,6 L8,3 z" fill="#9ca3af"/>
        </marker>
      </defs>
      ${edgeSvg}
      ${svgRows.join("")}
    </svg>`;
  }

  document.getElementById("btn-reload-graph")?.addEventListener("click", loadGraph);
  loadGraph();

})();
