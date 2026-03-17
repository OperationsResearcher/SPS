/**
 * surec.js — Süreç Yönetimi modülü JS
 * Kural: alert()/confirm()/prompt() YASAK — yalnızca SweetAlert2
 * Kural: Jinja2 {{ }} bu dosyada YASAK — veri data-* ile gelir
 */

(function () {
  "use strict";

  // ── Yardımcı: CSRF token ──────────────────────────────────────────────────
  function getCsrf() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.content : "";
  }

  // ── Yardımcı: JSON POST ───────────────────────────────────────────────────
  async function postJson(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrf(),
      },
      body: JSON.stringify(body),
    });
    return res.json();
  }

  // ── Yardımcı: Başarı toast ────────────────────────────────────────────────
  function toastSuccess(msg) {
    Swal.fire({
      toast: true,
      position: "top-end",
      icon: "success",
      title: msg,
      showConfirmButton: false,
      timer: 2500,
      timerProgressBar: true,
    });
  }

  // ── Yardımcı: Hata dialog ─────────────────────────────────────────────────
  function showError(msg) {
    Swal.fire({
      icon: "error",
      title: "Hata",
      text: msg,
      confirmButtonColor: "#dc2626",
    });
  }

  // ── Yardımcı: Silme onayı ─────────────────────────────────────────────────
  async function confirmDelete(title, text) {
    const result = await Swal.fire({
      title: title || "Emin misiniz?",
      text: text || "Bu işlem geri alınamaz.",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#dc2626",
      cancelButtonColor: "#6b7280",
      confirmButtonText: "Evet, sil",
      cancelButtonText: "İptal",
    });
    return result.isConfirmed;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // KARNE SAYFASI
  // ═══════════════════════════════════════════════════════════════════════════

  const karneRoot = document.getElementById("karne-root");
  if (!karneRoot) return; // Karne sayfasında değilsek çık

  const PROCESS_ID = karneRoot.dataset.processId;
  const KARNE_API = karneRoot.dataset.karneApiUrl;
  const KPI_DATA_ADD_URL = karneRoot.dataset.kpiDataAddUrl;
  const ACT_TRACK_BASE = karneRoot.dataset.activityTrackUrlBase;
  const KPI_DELETE_BASE = karneRoot.dataset.kpiDeleteUrlBase;
  const ACT_DELETE_BASE = karneRoot.dataset.activityDeleteUrlBase;

  const yearSelect = document.getElementById("year-select");
  const processSelect = document.getElementById("process-select");
  const kpiTbody = document.getElementById("kpi-tbody");
  const actTbody = document.getElementById("activity-tbody");
  const loadingEl = document.getElementById("karne-loading");

  const MONTHS = ["Oca","Şub","Mar","Nis","May","Haz","Tem","Ağu","Eyl","Eki","Kas","Ara"];

  // ── Karne verisi yükle ────────────────────────────────────────────────────
  async function loadKarne() {
    const year = yearSelect.value;
    if (loadingEl) loadingEl.style.display = "";
    kpiTbody.innerHTML = "";
    actTbody.innerHTML = "";

    try {
      const res = await fetch(`${KARNE_API}?year=${year}`);
      const data = await res.json();
      if (!data.success) throw new Error(data.message || "Veri alınamadı.");
      cachedKpis = data.kpis || [];
      updateStats(data.kpis, data.activities);
      populateTrendSelect(data.kpis);
      renderKpiTable(data.kpis, data.favorite_kpi_ids, year);
      renderActivityTable(data.activities, year);
    } catch (err) {
      showError("Karne verileri yüklenirken hata oluştu: " + err.message);
    } finally {
      if (loadingEl) loadingEl.style.display = "none";
    }
  }

  // ── İstatistik kartları güncelle ──────────────────────────────────────────
  function updateStats(kpis, activities) {
    const totalPg = kpis ? kpis.length : 0;
    let filledPg = 0;
    if (kpis) {
      kpis.forEach(k => {
        const hasData = Object.values(k.entries || {}).some(v => v);
        if (hasData) filledPg++;
      });
    }
    const totalAct = activities ? activities.length : 0;
    let doneAct = 0;
    if (activities) {
      activities.forEach(a => {
        const vals = Object.values(a.monthly_tracks || {});
        if (vals.some(v => v === true)) doneAct++;
      });
    }
    const pct = totalAct > 0 ? Math.round((doneAct / totalAct) * 100) : 0;

    const el = (id) => document.getElementById(id);
    if (el('stat-total-pg'))   el('stat-total-pg').textContent   = totalPg;
    if (el('stat-filled-pg'))  el('stat-filled-pg').textContent  = filledPg;
    if (el('stat-activities')) el('stat-activities').textContent = totalAct;
    if (el('stat-done-pct'))   el('stat-done-pct').textContent   = pct + '%';
  }

  // ── Trend KPI seçici doldur ───────────────────────────────────────────────
  let trendChart = null;
  function populateTrendSelect(kpis) {
    const sel = document.getElementById('trend-kpi-select');
    if (!sel) return;
    sel.innerHTML = '<option value="">— PG Seçin —</option>';
    (kpis || []).forEach(k => {
      const opt = document.createElement('option');
      opt.value = k.id;
      opt.textContent = k.name;
      sel.appendChild(opt);
    });
  }

  function renderTrendChart(kpi) {
    const canvas = document.getElementById('trend-chart');
    const empty  = document.getElementById('trend-empty');
    if (!canvas) return;
    if (!kpi) {
      canvas.style.display = 'none';
      if (empty) empty.style.display = '';
      return;
    }
    canvas.style.display = '';
    if (empty) empty.style.display = 'none';

    const labels = ['Oca','Şub','Mar','Nis','May','Haz','Tem','Ağu','Eyl','Eki','Kas','Ara'];
    const data = labels.map((_, i) => {
      const val = kpi.entries[`aylik_${i + 1}`];
      return val ? parseFloat(val) : null;
    });

    if (trendChart) trendChart.destroy();
    trendChart = new Chart(canvas, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: kpi.name,
          data,
          borderColor: '#6366f1',
          backgroundColor: 'rgba(99,102,241,0.08)',
          borderWidth: 2,
          pointBackgroundColor: '#6366f1',
          pointRadius: 4,
          tension: 0.3,
          fill: true,
          spanGaps: true,
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: { mode: 'index', intersect: false }
        },
        scales: {
          y: { beginAtZero: false, grid: { color: 'rgba(0,0,0,0.05)' } },
          x: { grid: { display: false } }
        }
      }
    });
  }

  // Trend seçici değişimi
  let cachedKpis = [];
  document.getElementById('trend-kpi-select')?.addEventListener('change', function () {
    const kpi = cachedKpis.find(k => String(k.id) === this.value);
    renderTrendChart(kpi || null);
  });

  // ── KPI tablosu render ────────────────────────────────────────────────────
  function renderKpiTable(kpis, favoriteIds, year) {
    if (!kpis || kpis.length === 0) {
      kpiTbody.innerHTML = `<tr><td colspan="17" class="text-center py-8 text-gray-400">Henüz performans göstergesi eklenmemiş.</td></tr>`;
      return;
    }

    kpiTbody.innerHTML = kpis.map((k, i) => {
      const isFav = favoriteIds.includes(k.id);
      const monthCells = Array.from({ length: 12 }, (_, idx) => {
        const key = `aylik_${idx + 1}`;
        const val = k.entries[key];
        const cls = val ? "has-data" : "no-data";
        const display = val || "—";
        return `<td class="px-2 py-2 text-center ${cls}" data-kpi-id="${k.id}" data-month="${idx + 1}">
          <button class="btn-enter-data hover:underline" data-kpi-id="${k.id}" data-month="${idx + 1}" data-year="${year}" title="Veri gir">${display}</button>
        </td>`;
      }).join("");

      return `<tr data-kpi-id="${k.id}">
        <td class="px-3 py-2 text-gray-400">${i + 1}</td>
        <td class="px-3 py-2">
          <div class="flex items-center gap-1.5">
            <button class="btn-favorite ${isFav ? "active" : ""}" data-kpi-id="${k.id}" title="Favori">★</button>
            <span class="font-medium text-gray-800 dark:text-gray-100">${escHtml(k.name)}</span>
            ${k.code ? `<span class="process-code-badge">${escHtml(k.code)}</span>` : ""}
          </div>
          <div class="text-gray-400 text-xs mt-0.5">${escHtml(k.sub_strategy_title || "")}</div>
        </td>
        <td class="px-3 py-2 text-center font-medium">${escHtml(k.target_value || "—")}</td>
        <td class="px-3 py-2 text-center text-gray-500">${escHtml(k.unit || "—")}</td>
        ${monthCells}
        <td class="px-3 py-2 text-center">
          <button class="btn-kpi-delete text-red-400 hover:text-red-600 text-xs" data-kpi-id="${k.id}" title="Sil">
            <i class="fas fa-trash"></i>
          </button>
        </td>
      </tr>`;
    }).join("");
  }

  // ── Faaliyet tablosu render ───────────────────────────────────────────────
  function renderActivityTable(activities, year) {
    if (!activities || activities.length === 0) {
      actTbody.innerHTML = `<tr><td colspan="16" class="text-center py-8 text-gray-400">Henüz faaliyet eklenmemiş.</td></tr>`;
      return;
    }

    actTbody.innerHTML = activities.map((a, i) => {
      const monthCells = Array.from({ length: 12 }, (_, idx) => {
        const month = idx + 1;
        const done = a.monthly_tracks[month] === true;
        return `<td class="px-2 py-2 text-center">
          <input type="checkbox" class="track-checkbox w-4 h-4 accent-emerald-600 cursor-pointer"
                 data-act-id="${a.id}" data-month="${month}" data-year="${year}"
                 ${done ? "checked" : ""}>
        </td>`;
      }).join("");

      const statusColor = {
        "Tamamlandı": "text-emerald-600",
        "Devam Ediyor": "text-blue-600",
        "Planlandı": "text-gray-500",
        "İptal": "text-red-400",
      }[a.status] || "text-gray-500";

      return `<tr data-act-id="${a.id}">
        <td class="px-3 py-2 text-gray-400">${i + 1}</td>
        <td class="px-3 py-2">
          <span class="font-medium text-gray-800 dark:text-gray-100">${escHtml(a.name)}</span>
        </td>
        <td class="px-3 py-2 text-center text-xs ${statusColor}">${escHtml(a.status || "—")}</td>
        ${monthCells}
        <td class="px-3 py-2 text-center">
          <button class="btn-act-delete text-red-400 hover:text-red-600 text-xs" data-act-id="${a.id}" title="Sil">
            <i class="fas fa-trash"></i>
          </button>
        </td>
      </tr>`;
    }).join("");
  }

  // ── Veri girişi modal ─────────────────────────────────────────────────────
  async function openDataEntryModal(kpiId, month, year) {
    const { value: actualValue } = await Swal.fire({
      title: `${MONTHS[month - 1]} ${year} — Veri Gir`,
      input: "text",
      inputLabel: "Gerçekleşen Değer",
      inputPlaceholder: "Örn: 95.5",
      showCancelButton: true,
      confirmButtonText: "Kaydet",
      cancelButtonText: "İptal",
      confirmButtonColor: "#4f46e5",
      inputValidator: (v) => !v && "Değer boş bırakılamaz.",
    });
    if (!actualValue) return;

    const body = {
      kpi_id: kpiId,
      year: parseInt(year),
      period_type: "aylik",
      period_no: month,
      actual_value: actualValue,
    };

    try {
      const data = await postJson(KPI_DATA_ADD_URL, body);
      if (data.success) {
        toastSuccess("Veri kaydedildi.");
        loadKarne();
      } else {
        showError(data.message || "Kayıt başarısız.");
      }
    } catch (err) {
      showError("Sunucu hatası: " + err.message);
    }
  }

  // ── Event delegation ──────────────────────────────────────────────────────
  document.addEventListener("click", async (e) => {
    // Veri gir
    const btnEnter = e.target.closest(".btn-enter-data");
    if (btnEnter) {
      openDataEntryModal(btnEnter.dataset.kpiId, btnEnter.dataset.month, btnEnter.dataset.year);
      return;
    }

    // KPI sil
    const btnKpiDel = e.target.closest(".btn-kpi-delete");
    if (btnKpiDel) {
      const ok = await confirmDelete("Performans göstergesi silinsin mi?", "Bu PG ve tüm verileri pasife alınacak.");
      if (!ok) return;
      try {
        const data = await postJson(`${KPI_DELETE_BASE}${btnKpiDel.dataset.kpiId}`, {});
        if (data.success) { toastSuccess("Performans göstergesi silindi."); loadKarne(); }
        else showError(data.message);
      } catch (err) { showError(err.message); }
      return;
    }

    // Faaliyet sil
    const btnActDel = e.target.closest(".btn-act-delete");
    if (btnActDel) {
      const ok = await confirmDelete("Faaliyet silinsin mi?", "Faaliyet pasife alınacak.");
      if (!ok) return;
      try {
        const data = await postJson(`${ACT_DELETE_BASE}${btnActDel.dataset.actId}`, {});
        if (data.success) { toastSuccess("Faaliyet silindi."); loadKarne(); }
        else showError(data.message);
      } catch (err) { showError(err.message); }
      return;
    }
  });

  // ── Faaliyet takip checkbox ───────────────────────────────────────────────
  document.addEventListener("change", async (e) => {
    const cb = e.target.closest(".track-checkbox");
    if (!cb) return;
    const body = {
      year: parseInt(cb.dataset.year),
      month: parseInt(cb.dataset.month),
      completed: cb.checked,
    };
    try {
      const data = await postJson(`${ACT_TRACK_BASE}${cb.dataset.actId}`, body);
      if (!data.success) {
        cb.checked = !cb.checked; // geri al
        showError(data.message || "Takip güncellenemedi.");
      }
    } catch (err) {
      cb.checked = !cb.checked;
      showError(err.message);
    }
  });

  // ── Yıl / süreç değişimi ──────────────────────────────────────────────────
  yearSelect.addEventListener("change", loadKarne);

  processSelect.addEventListener("change", () => {
    const pid = processSelect.value;
    window.location.href = `/micro/surec/${pid}/karne`;
  });

  // ── HTML escape yardımcısı ────────────────────────────────────────────────
  function escHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  // ── İlk yükleme ───────────────────────────────────────────────────────────
  loadKarne();

})();

// ═══════════════════════════════════════════════════════════════════════════
// INDEX SAYFASI — Süreç listesi CRUD
// ═══════════════════════════════════════════════════════════════════════════
(function () {
  "use strict";

  const indexRoot = document.getElementById("surec-index");
  if (!indexRoot) return;

  const ADD_URL = indexRoot.dataset.addUrl;
  const DELETE_BASE = indexRoot.dataset.deleteUrlBase;

  function getCsrf() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.content : "";
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
    Swal.fire({ toast: true, position: "top-end", icon: "success", title: msg,
      showConfirmButton: false, timer: 2500, timerProgressBar: true });
  }

  function showError(msg) {
    Swal.fire({ icon: "error", title: "Hata", text: msg, confirmButtonColor: "#dc2626" });
  }

  // ── Yeni süreç ekle ───────────────────────────────────────────────────────
  async function openAddModal() {
    const { value: formValues } = await Swal.fire({
      title: "Yeni Süreç Ekle",
      html: `
        <div class="text-left space-y-3">
          <div>
            <label class="block text-xs text-gray-600 mb-1">Süreç Adı <span class="text-red-500">*</span></label>
            <input id="swal-name" class="swal2-input" placeholder="Süreç adı">
          </div>
          <div>
            <label class="block text-xs text-gray-600 mb-1">Kod</label>
            <input id="swal-code" class="swal2-input" placeholder="Örn: SR1">
          </div>
          <div>
            <label class="block text-xs text-gray-600 mb-1">Açıklama</label>
            <textarea id="swal-desc" class="swal2-textarea" placeholder="Kısa açıklama"></textarea>
          </div>
        </div>`,
      focusConfirm: false,
      showCancelButton: true,
      confirmButtonText: "Kaydet",
      cancelButtonText: "İptal",
      confirmButtonColor: "#4f46e5",
      preConfirm: () => {
        const name = document.getElementById("swal-name").value.trim();
        if (!name) { Swal.showValidationMessage("Süreç adı zorunludur."); return false; }
        return {
          name,
          code: document.getElementById("swal-code").value.trim() || null,
          description: document.getElementById("swal-desc").value.trim() || null,
        };
      },
    });

    if (!formValues) return;

    try {
      const data = await postJson(ADD_URL, formValues);
      if (data.success) {
        toastSuccess("Süreç oluşturuldu.");
        setTimeout(() => location.reload(), 1200);
      } else {
        showError(data.message || "Kayıt başarısız.");
      }
    } catch (err) {
      showError("Sunucu hatası: " + err.message);
    }
  }

  // ── Süreç sil ─────────────────────────────────────────────────────────────
  async function deleteSurec(id, name) {
    const result = await Swal.fire({
      title: "Süreç silinsin mi?",
      text: `"${name}" pasife alınacak.`,
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#dc2626",
      cancelButtonColor: "#6b7280",
      confirmButtonText: "Evet, sil",
      cancelButtonText: "İptal",
    });
    if (!result.isConfirmed) return;

    try {
      const data = await postJson(`${DELETE_BASE}${id}`, {});
      if (data.success) {
        toastSuccess("Süreç silindi.");
        setTimeout(() => location.reload(), 1200);
      } else {
        showError(data.message || "Silme başarısız.");
      }
    } catch (err) {
      showError("Sunucu hatası: " + err.message);
    }
  }

  // ── Event listener'lar ────────────────────────────────────────────────────
  document.getElementById("btn-surec-add")?.addEventListener("click", openAddModal);
  document.getElementById("btn-surec-add-empty")?.addEventListener("click", openAddModal);

  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".btn-surec-delete");
    if (!btn) return;
    deleteSurec(btn.dataset.surecId, btn.dataset.surecName);
  });

})();
