/**
 * bireysel.js — Bireysel Performans modülü JS
 * Kural: alert()/confirm()/prompt() YASAK — yalnızca SweetAlert2
 * Kural: Jinja2 {{ }} bu dosyada YASAK — veri data-* ile gelir
 */

(function () {
  "use strict";

  const root = document.getElementById("bireysel-root");
  if (!root) return;

  const KARNE_API       = root.dataset.karneApiUrl;
  const PG_ADD_URL      = root.dataset.pgAddUrl;
  const VERI_ADD_URL    = root.dataset.veriAddUrl;
  const FAALIYET_ADD_URL = root.dataset.faaliyetAddUrl;
  const PG_DEL_BASE     = root.dataset.pgDeleteBase;
  const FAALIYET_DEL_BASE = root.dataset.faaliyetDeleteBase;
  const FAALIYET_TRACK_BASE = root.dataset.faaliyetTrackBase;

  const yearSelect   = document.getElementById("year-select");
  const pgTbody      = document.getElementById("pg-tbody");
  const faaliyetTbody = document.getElementById("faaliyet-tbody");
  const loadingEl    = document.getElementById("karne-loading");

  // ── Yardımcılar ─────────────────────────────────────────────────────────
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
    Swal.fire({ toast: true, position: "top-end", icon: "success",
      title: msg, showConfirmButton: false, timer: 2500, timerProgressBar: true });
  }

  function showError(msg) {
    Swal.fire({ icon: "error", title: "Hata", text: msg, confirmButtonColor: "#dc2626" });
  }

  async function confirmDelete(title, text) {
    const r = await Swal.fire({
      title: title, text: text, icon: "warning", showCancelButton: true,
      confirmButtonColor: "#dc2626", cancelButtonColor: "#6b7280",
      confirmButtonText: "Evet, sil", cancelButtonText: "İptal",
    });
    return r.isConfirmed;
  }

  function escHtml(s) {
    if (!s) return "";
    return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
  }

  // ── Karne yükle ──────────────────────────────────────────────────────────
  async function loadKarne() {
    const year = yearSelect.value;
    if (loadingEl) { loadingEl.style.display = ""; }
    pgTbody.innerHTML = "";
    faaliyetTbody.innerHTML = "";
    try {
      const res = await fetch(`${KARNE_API}?year=${year}`);
      const data = await res.json();
      if (!data.success) throw new Error(data.message || "Veri alınamadı.");
      updateStats(data.pgs, data.activities);
      renderPgTable(data.pgs, year);
      renderFaaliyetTable(data.activities, year);
    } catch (err) {
      showError("Karne verileri yüklenirken hata: " + err.message);
    } finally {
      if (loadingEl) { loadingEl.style.display = "none"; }
    }
  }

  function updateStats(pgs, activities) {
    const totalPg = pgs ? pgs.length : 0;
    let filledPg = 0;
    (pgs || []).forEach(pg => {
      if (Object.values(pg.entries || {}).some(v => v)) filledPg++;
    });
    const totalAct = activities ? activities.length : 0;
    let doneAct = 0;
    (activities || []).forEach(a => {
      if (Object.values(a.monthly_tracks || {}).some(v => v === true)) doneAct++;
    });
    const pct = totalAct > 0 ? Math.round((doneAct / totalAct) * 100) : 0;

    const el = id => document.getElementById(id);
    if (el("stat-total-pg"))   el("stat-total-pg").textContent   = totalPg;
    if (el("stat-filled-pg"))  el("stat-filled-pg").textContent  = filledPg;
    if (el("stat-activities")) el("stat-activities").textContent = totalAct;
    if (el("stat-done-pct"))   el("stat-done-pct").textContent   = pct + "%";
  }

  function renderPgTable(pgs, year) {
    if (!pgs || !pgs.length) {
      pgTbody.innerHTML = `<tr><td colspan="17" class="text-center py-8 text-gray-400">Henüz PG eklenmemiş.</td></tr>`;
      return;
    }
    pgTbody.innerHTML = pgs.map((pg, i) => {
      const monthCells = Array.from({ length: 12 }, (_, idx) => {
        const key = `aylik_${idx + 1}`;
        const val = pg.entries[key];
        const cls = val ? "has-data" : "no-data";
        return `<td class="px-2 py-2 text-center ${cls}">
          <button class="btn-veri-gir hover:underline"
                  data-pg-id="${pg.id}" data-month="${idx + 1}" data-year="${year}">${val || "—"}</button>
        </td>`;
      }).join("");
      return `<tr>
        <td class="px-3 py-2 text-gray-400">${i + 1}</td>
        <td class="px-3 py-2 font-medium text-gray-800 dark:text-gray-100">${escHtml(pg.name)}
          ${pg.code ? `<span class="process-code-badge">${escHtml(pg.code)}</span>` : ""}
        </td>
        <td class="px-3 py-2 text-center">${escHtml(pg.target_value || "—")}</td>
        <td class="px-3 py-2 text-center text-gray-500">${escHtml(pg.unit || "—")}</td>
        ${monthCells}
        <td class="px-3 py-2 text-center">
          <button class="btn-pg-delete text-red-400 hover:text-red-600" data-pg-id="${pg.id}">
            <i class="fas fa-trash"></i>
          </button>
        </td>
      </tr>`;
    }).join("");
  }

  function renderFaaliyetTable(activities, year) {
    if (!activities || !activities.length) {
      faaliyetTbody.innerHTML = `<tr><td colspan="16" class="text-center py-8 text-gray-400">Henüz faaliyet eklenmemiş.</td></tr>`;
      return;
    }
    faaliyetTbody.innerHTML = activities.map((a, i) => {
      const monthCells = Array.from({ length: 12 }, (_, idx) => {
        const month = idx + 1;
        const done = a.monthly_tracks[month] === true;
        return `<td class="px-2 py-2 text-center">
          <input type="checkbox" class="track-cb w-4 h-4 accent-emerald-600 cursor-pointer"
                 data-act-id="${a.id}" data-month="${month}" data-year="${year}" ${done ? "checked" : ""}>
        </td>`;
      }).join("");
      return `<tr>
        <td class="px-3 py-2 text-gray-400">${i + 1}</td>
        <td class="px-3 py-2 font-medium text-gray-800 dark:text-gray-100">${escHtml(a.name)}</td>
        <td class="px-3 py-2 text-center text-xs text-gray-500">${escHtml(a.status || "—")}</td>
        ${monthCells}
        <td class="px-3 py-2 text-center">
          <button class="btn-faaliyet-delete text-red-400 hover:text-red-600" data-act-id="${a.id}">
            <i class="fas fa-trash"></i>
          </button>
        </td>
      </tr>`;
    }).join("");
  }

  // ── PG Ekle ──────────────────────────────────────────────────────────────
  document.getElementById("btn-pg-add")?.addEventListener("click", async () => {
    const { value: vals } = await Swal.fire({
      title: "Yeni Performans Göstergesi",
      html: `<div class="text-left space-y-3">
        <div><label class="block text-xs text-gray-500 mb-1">Ad <span class="text-red-500">*</span></label>
          <input id="pg-name" class="swal2-input" placeholder="PG adı"></div>
        <div><label class="block text-xs text-gray-500 mb-1">Hedef Değer</label>
          <input id="pg-target" class="swal2-input" placeholder="Örn: 95"></div>
        <div><label class="block text-xs text-gray-500 mb-1">Birim</label>
          <input id="pg-unit" class="swal2-input" placeholder="Örn: %"></div>
      </div>`,
      focusConfirm: false, showCancelButton: true,
      confirmButtonText: "Kaydet", cancelButtonText: "İptal", confirmButtonColor: "#4f46e5",
      preConfirm: () => {
        const name = document.getElementById("pg-name").value.trim();
        if (!name) { Swal.showValidationMessage("Ad zorunludur."); return false; }
        return { name, target_value: document.getElementById("pg-target").value.trim() || null,
                 unit: document.getElementById("pg-unit").value.trim() || null };
      },
    });
    if (!vals) return;
    try {
      const d = await postJson(PG_ADD_URL, vals);
      if (d.success) { toastSuccess("PG eklendi."); loadKarne(); }
      else showError(d.message || "Kayıt başarısız.");
    } catch (e) { showError("Sunucu hatası: " + e.message); }
  });

  // ── Faaliyet Ekle ────────────────────────────────────────────────────────
  document.getElementById("btn-faaliyet-add")?.addEventListener("click", async () => {
    const { value: vals } = await Swal.fire({
      title: "Yeni Faaliyet",
      html: `<div class="text-left space-y-3">
        <div><label class="block text-xs text-gray-500 mb-1">Ad <span class="text-red-500">*</span></label>
          <input id="fa-name" class="swal2-input" placeholder="Faaliyet adı"></div>
        <div><label class="block text-xs text-gray-500 mb-1">Açıklama</label>
          <textarea id="fa-desc" class="swal2-textarea" placeholder="Kısa açıklama"></textarea></div>
      </div>`,
      focusConfirm: false, showCancelButton: true,
      confirmButtonText: "Kaydet", cancelButtonText: "İptal", confirmButtonColor: "#4f46e5",
      preConfirm: () => {
        const name = document.getElementById("fa-name").value.trim();
        if (!name) { Swal.showValidationMessage("Ad zorunludur."); return false; }
        return { name, description: document.getElementById("fa-desc").value.trim() || null };
      },
    });
    if (!vals) return;
    try {
      const d = await postJson(FAALIYET_ADD_URL, vals);
      if (d.success) { toastSuccess("Faaliyet eklendi."); loadKarne(); }
      else showError(d.message || "Kayıt başarısız.");
    } catch (e) { showError("Sunucu hatası: " + e.message); }
  });

  // ── Veri Gir ─────────────────────────────────────────────────────────────
  document.addEventListener("click", async (e) => {
    const btn = e.target.closest(".btn-veri-gir");
    if (btn) {
      const { value: val } = await Swal.fire({
        title: `Veri Gir`,
        input: "text", inputLabel: "Gerçekleşen Değer", inputPlaceholder: "Örn: 92.5",
        showCancelButton: true, confirmButtonText: "Kaydet", cancelButtonText: "İptal",
        confirmButtonColor: "#4f46e5",
        inputValidator: v => !v && "Değer boş bırakılamaz.",
      });
      if (!val) return;
      try {
        const d = await postJson(VERI_ADD_URL, {
          pg_id: btn.dataset.pgId, year: parseInt(btn.dataset.year),
          period_type: "aylik", period_no: parseInt(btn.dataset.month), actual_value: val,
        });
        if (d.success) { toastSuccess("Veri kaydedildi."); loadKarne(); }
        else showError(d.message || "Kayıt başarısız.");
      } catch (e) { showError("Sunucu hatası: " + e.message); }
      return;
    }

    // PG sil
    const btnPgDel = e.target.closest(".btn-pg-delete");
    if (btnPgDel) {
      const ok = await confirmDelete("PG silinsin mi?", "Performans göstergesi pasife alınacak.");
      if (!ok) return;
      try {
        const d = await postJson(`${PG_DEL_BASE}${btnPgDel.dataset.pgId}`, {});
        if (d.success) { toastSuccess("PG silindi."); loadKarne(); }
        else showError(d.message);
      } catch (e) { showError(e.message); }
      return;
    }

    // Faaliyet sil
    const btnFaDel = e.target.closest(".btn-faaliyet-delete");
    if (btnFaDel) {
      const ok = await confirmDelete("Faaliyet silinsin mi?", "Faaliyet pasife alınacak.");
      if (!ok) return;
      try {
        const d = await postJson(`${FAALIYET_DEL_BASE}${btnFaDel.dataset.actId}`, {});
        if (d.success) { toastSuccess("Faaliyet silindi."); loadKarne(); }
        else showError(d.message);
      } catch (e) { showError(e.message); }
    }
  });

  // ── Faaliyet takip checkbox ───────────────────────────────────────────────
  document.addEventListener("change", async (e) => {
    const cb = e.target.closest(".track-cb");
    if (!cb) return;
    try {
      const d = await postJson(`${FAALIYET_TRACK_BASE}${cb.dataset.actId}`, {
        year: parseInt(cb.dataset.year), month: parseInt(cb.dataset.month), completed: cb.checked,
      });
      if (!d.success) { cb.checked = !cb.checked; showError(d.message || "Takip güncellenemedi."); }
    } catch (e) { cb.checked = !cb.checked; showError(e.message); }
  });

  yearSelect.addEventListener("change", loadKarne);
  loadKarne();

})();
