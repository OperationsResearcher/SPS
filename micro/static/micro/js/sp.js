/**
 * sp.js — Stratejik Planlama modülü JS
 * Kural: alert()/confirm()/prompt() YASAK — yalnızca SweetAlert2
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
      headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrf() },
      body: JSON.stringify(body),
    });
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
    const ADD_SUB_URL         = spRoot.dataset.addSubStrategyUrl;
    const UPDATE_SUB_BASE     = spRoot.dataset.updateSubStrategyBase;
    const DELETE_SUB_BASE     = spRoot.dataset.deleteSubStrategyBase;

    // Ana strateji ekle
    document.getElementById("btn-strategy-add")?.addEventListener("click", async () => {
      const { value: vals } = await Swal.fire({
        title: "Yeni Strateji Ekle",
        html: `<div class="text-left space-y-3">
          <div><label class="block text-xs text-gray-600 mb-1">Başlık <span class="text-red-500">*</span></label>
            <input id="sw-title" class="swal2-input" placeholder="Strateji başlığı"></div>
          <div><label class="block text-xs text-gray-600 mb-1">Kod</label>
            <input id="sw-code" class="swal2-input" placeholder="Örn: ST1"></div>
          <div><label class="block text-xs text-gray-600 mb-1">Açıklama</label>
            <textarea id="sw-desc" class="swal2-textarea" placeholder="Kısa açıklama"></textarea></div>
        </div>`,
        focusConfirm: false, showCancelButton: true,
        confirmButtonText: "Kaydet", cancelButtonText: "İptal", confirmButtonColor: "#4f46e5",
        preConfirm: () => {
          const title = document.getElementById("sw-title").value.trim();
          if (!title) { Swal.showValidationMessage("Başlık zorunludur."); return false; }
          return { title, code: document.getElementById("sw-code").value.trim() || null,
                   description: document.getElementById("sw-desc").value.trim() || null };
        },
      });
      if (!vals) return;
      try {
        const d = await postJson(ADD_STRATEGY_URL, vals);
        if (d.success) { toastSuccess("Strateji eklendi."); setTimeout(() => location.reload(), 1200); }
        else showError(d.message || "Kayıt başarısız.");
      } catch (e) { showError("Sunucu hatası: " + e.message); }
    });

    // Alt strateji ekle
    document.addEventListener("click", async (e) => {
      const btn = e.target.closest(".btn-sub-add");
      if (!btn) return;
      const strategyId = btn.dataset.strategyId;
      const { value: vals } = await Swal.fire({
        title: "Alt Strateji Ekle",
        html: `<div class="text-left space-y-3">
          <div><label class="block text-xs text-gray-600 mb-1">Başlık <span class="text-red-500">*</span></label>
            <input id="sw-sub-title" class="swal2-input" placeholder="Alt strateji başlığı"></div>
          <div><label class="block text-xs text-gray-600 mb-1">Kod</label>
            <input id="sw-sub-code" class="swal2-input" placeholder="Örn: ST1.1"></div>
        </div>`,
        focusConfirm: false, showCancelButton: true,
        confirmButtonText: "Kaydet", cancelButtonText: "İptal", confirmButtonColor: "#4f46e5",
        preConfirm: () => {
          const title = document.getElementById("sw-sub-title").value.trim();
          if (!title) { Swal.showValidationMessage("Başlık zorunludur."); return false; }
          return { strategy_id: strategyId, title,
                   code: document.getElementById("sw-sub-code").value.trim() || null };
        },
      });
      if (!vals) return;
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
      const { value: vals } = await Swal.fire({
        title: "Alt Strateji Düzenle",
        html: `<div class="text-left space-y-3">
          <div><label class="block text-xs text-gray-600 mb-1">Başlık <span class="text-red-500">*</span></label>
            <input id="sw-edit-title" class="swal2-input" value="${escHtml(currentTitle)}"></div>
          <div><label class="block text-xs text-gray-600 mb-1">Kod</label>
            <input id="sw-edit-code" class="swal2-input" value="${escHtml(currentCode)}"></div>
        </div>`,
        focusConfirm: false, showCancelButton: true,
        confirmButtonText: "Güncelle", cancelButtonText: "İptal", confirmButtonColor: "#4f46e5",
        preConfirm: () => {
          const title = document.getElementById("sw-edit-title").value.trim();
          if (!title) { Swal.showValidationMessage("Başlık zorunludur."); return false; }
          return { title, code: document.getElementById("sw-edit-code").value.trim() || null };
        },
      });
      if (!vals) return;
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
