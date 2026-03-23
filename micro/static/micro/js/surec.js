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
  function isLikelyLoginRedirect(res) {
    try {
      const finalUrl = String(res?.url || "").toLowerCase();
      return res?.redirected && finalUrl.includes("/login");
    } catch (_) {
      return false;
    }
  }

  function redirectToLogin() {
    const next = `${window.location.pathname}${window.location.search || ""}`;
    window.location.href = `/login?next=${encodeURIComponent(next)}`;
  }

  async function parseJsonOrThrow(res) {
    if (isLikelyLoginRedirect(res) || res.status === 401) {
      const err = new Error("Oturum süresi doldu. Lütfen yeniden giriş yapın.");
      err.code = "AUTH_REQUIRED";
      throw err;
    }
    const contentType = String(res.headers.get("content-type") || "").toLowerCase();
    if (!contentType.includes("application/json")) {
      throw new Error("Sunucudan beklenmeyen yanıt alındı.");
    }
    return res.json();
  }

  async function postJson(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrf(),
      },
      credentials: "same-origin",
      body: JSON.stringify(body),
    });
    return parseJsonOrThrow(res);
  }

  async function getJson(url) {
    const res = await fetch(url, {
      method: "GET",
      headers: { Accept: "application/json" },
      credentials: "same-origin",
    });
    const data = await parseJsonOrThrow(res);
    if (!res.ok) {
      throw new Error(data.message || `HTTP ${res.status}`);
    }
    return data;
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
  // KARNE veya FAALİYETLER SAYFASI
  // ═══════════════════════════════════════════════════════════════════════════

  const viewRoot = document.getElementById("karne-root") || document.getElementById("faaliyet-root");
  if (!viewRoot) return;
  const currentProcessId = parseInt(viewRoot.dataset.processId || "0", 10) || 0;

  const PAGE_MODE = viewRoot.dataset.pageMode || "karne";
  const INITIAL_TAB = (viewRoot.dataset.initialTab || "").toLowerCase();

  const KARNE_API = viewRoot.dataset.karneApiUrl;
  const KARNE_EXPORT_XLSX_URL = viewRoot.dataset.karneExportXlsxUrl || "";
  const KPI_DATA_ADD_URL = viewRoot.dataset.kpiDataAddUrl || "";
  const ACT_TRACK_BASE = viewRoot.dataset.activityTrackUrlBase || "";
  const KPI_DELETE_BASE = viewRoot.dataset.kpiDeleteUrlBase || "";
  const KPI_ADD_URL = viewRoot.dataset.kpiAddUrl || "";
  const KPI_GET_TEMPLATE = viewRoot.dataset.kpiGetUrlTemplate || "";
  const KPI_UPDATE_TEMPLATE = viewRoot.dataset.kpiUpdateUrlTemplate || "";
  const KPI_ID_PLACEHOLDER = String(viewRoot.dataset.kpiIdPlaceholder || "900000001");
  const KPI_DATA_HISTORY_URL_TEMPLATE = viewRoot.dataset.kpiDataHistoryUrlTemplate || "";
  const KPI_DATA_UPDATE_URL_TEMPLATE = viewRoot.dataset.kpiDataUpdateUrlTemplate || "";
  const KPI_DATA_DELETE_URL_TEMPLATE = viewRoot.dataset.kpiDataDeleteUrlTemplate || "";
  const KPI_DATA_ROW_PLACEHOLDER = String(viewRoot.dataset.kpiDataRowPlaceholder || "800000001");

  /** @param {string} template @param {number|string} id */
  function expandKpiUrl(template, id) {
    if (!template) return "";
    return template.split(KPI_ID_PLACEHOLDER).join(String(id));
  }

  /** @param {string} template @param {number|string} dataRowId */
  function expandKpiDataRowUrl(template, dataRowId) {
    if (!template) return "";
    return template.split(KPI_DATA_ROW_PLACEHOLDER).join(String(dataRowId));
  }
  const ACT_DELETE_BASE = viewRoot.dataset.activityDeleteUrlBase || "";
  const FAVORITE_TOGGLE_URL = viewRoot.dataset.favoriteToggleUrl || "";
  const BIREYSEL_ENSURE_PG_URL = viewRoot.dataset.bireyselEnsurePgUrl || "";
  const BIREYSEL_VERI_ADD_URL = viewRoot.dataset.bireyselVeriAddUrl || "";

  const yearSelect = document.getElementById("year-select");
  /** PG kartı: açık periyot (çeyrek/ay/hafta…); null iken takvim varsayılanı; günlükte gün/ay/yıl */
  let karneNavPeriodKey = null;
  let karneNavDataYear = null;
  let karneGunlukViewYear = null;
  let karneGunlukViewMonth = null;
  let karneGunlukViewDay = null;

  function getPgKarneView() {
    return document.getElementById("pg-periyot-select")?.value || "ceyrek";
  }

  function getDataYearForKarneLoad() {
    const base = yearSelect ? parseInt(yearSelect.value, 10) || new Date().getFullYear() : new Date().getFullYear();
    const view = getPgKarneView();
    if (view === "gunluk") {
      return karneGunlukViewYear != null ? karneGunlukViewYear : base;
    }
    if (karneNavDataYear != null) return karneNavDataYear;
    return base;
  }

  function syncPgKarneYilFromBanner() {
    const pgY = document.getElementById("pg-karne-yil-select");
    if (pgY && yearSelect && yearSelect.value) pgY.value = yearSelect.value;
  }

  function syncPgGunlukAyHiddenSelect() {
    const aySel = document.getElementById("pg-gunluk-ay-select");
    if (!aySel) return;
    const m =
      karneGunlukViewMonth != null
        ? karneGunlukViewMonth
        : Math.max(1, Math.min(12, parseInt(aySel.value, 10) || new Date().getMonth() + 1));
    aySel.value = String(m);
  }

  function updateKarneKanbanNavLabel() {
    const line1El = document.getElementById("pg-karne-nav-label");
    const subEl = document.getElementById("pg-karne-nav-sub");
    if (!line1El) return;
    const view = getPgKarneView();
    const names = {
      ceyrek: "Çeyreklik",
      yillik: "Yıllık",
      aylik: "Aylık",
      haftalik: "Haftalık",
      gunluk: "Günlük",
      alti_ay: "6 aylık",
    };
    const y = getDataYearForKarneLoad();
    const ctx = getKanbanPeriodContextForMain(String(y), view);
    if (view === "gunluk") {
      const m = karneGunlukViewMonth != null ? karneGunlukViewMonth : new Date().getMonth() + 1;
      line1El.textContent = `${y} — ${AYLAR_TR_FULL_KB[m - 1]} — Günlük`;
    } else {
      line1El.textContent = `${y} — ${names[view] || view} görünümü`;
    }
    if (subEl) subEl.textContent = formatPeriodBadgeSubline(ctx, view, y);
  }

  function resetKarneKanbanNavForViewChange(view) {
    karneNavPeriodKey = null;
    karneNavDataYear = null;
    if (view === "gunluk") {
      const base = yearSelect ? parseInt(yearSelect.value, 10) || new Date().getFullYear() : new Date().getFullYear();
      const cy = new Date().getFullYear();
      const cm = new Date().getMonth() + 1;
      const cd = new Date().getDate();
      karneGunlukViewYear = base;
      karneGunlukViewMonth = base === cy ? cm : 1;
      karneGunlukViewDay = base === cy && karneGunlukViewMonth === cm ? cd : 1;
    } else {
      karneGunlukViewYear = null;
      karneGunlukViewMonth = null;
      karneGunlukViewDay = null;
    }
    syncPgGunlukAyHiddenSelect();
  }

  /** PG listesi (VGS + trend); loadKarne ile doldurulur */
  let cachedKpis = [];
  const processSelect = document.getElementById("process-select");
  const actTbody = document.getElementById("activity-tbody");
  const activityTableWrap = document.getElementById("activity-table-wrap");
  const activityKanbanRoot = document.getElementById("activity-kanban-root");
  const activityViewModeSelect = document.getElementById("activity-view-mode");
  const loadingEl = document.getElementById("karne-loading");

  const MONTHS = ["Oca","Şub","Mar","Nis","May","Haz","Tem","Ağu","Eyl","Eki","Kas","Ara"];
  const AYLAR_TR_FULL_KB = [
    "Ocak",
    "Şubat",
    "Mart",
    "Nisan",
    "Mayıs",
    "Haziran",
    "Temmuz",
    "Ağustos",
    "Eylül",
    "Ekim",
    "Kasım",
    "Aralık",
  ];

  function haftalikRangeLabelKb(year, month, week) {
    const y = parseInt(year, 10);
    const m = parseInt(month, 10);
    const w = parseInt(week, 10);
    if (!y || m < 1 || m > 12 || w < 1 || w > 5) return null;
    const lastDay = new Date(y, m, 0).getDate();
    const startD = (w - 1) * 7 + 1;
    if (startD > lastDay) return null;
    const endD = Math.min(w * 7, lastDay);
    const mn = AYLAR_TR_FULL_KB[m - 1];
    if (startD === endD) return `${startD} ${mn}`;
    return `${startD} ${mn} – ${endD} ${mn}`;
  }

  function buildHaftalikPeriodsForYear(year) {
    const arr = [];
    const y = parseInt(year, 10) || new Date().getFullYear();
    for (let m = 1; m <= 12; m++) {
      for (let w = 1; w <= 5; w++) {
        const label = haftalikRangeLabelKb(y, m, w);
        if (!label) continue;
        arr.push({ key: `haftalik_${w}_${m}`, label });
      }
    }
    return arr;
  }

  /** Kök pgTabloCard — çeyrek anahtarları (KpiData → entries) */
  const QUARTER_PERIODS = [
    { key: "ceyrek_1", label: "I. Çeyrek", periodNo: 1 },
    { key: "ceyrek_2", label: "II. Çeyrek", periodNo: 2 },
    { key: "ceyrek_3", label: "III. Çeyrek", periodNo: 3 },
    { key: "ceyrek_4", label: "IV. Çeyrek", periodNo: 4 },
  ];

  const YARIYIL_PERIODS = [
    { key: "halfyear_1", label: "Ocak – Haziran" },
    { key: "halfyear_2", label: "Temmuz – Aralık" },
  ];

  let lastFavoriteKpiIds = [];

  /** Günlük görünüm: seçilen ayın günleri */
  function buildGunlukPeriods(year, month) {
    const y = parseInt(year, 10);
    const m = Math.max(1, Math.min(12, parseInt(month, 10) || 1));
    const lastDay = new Date(y, m, 0).getDate();
    const arr = [];
    for (let d = 1; d <= lastDay; d++) {
      arr.push({ key: `gunluk_${d}_${m}`, label: String(d), isDay: true });
    }
    return arr;
  }

  /**
   * Aktif tablo periyotları (kök process_karne.js ile uyumlu anahtarlar).
   * @returns {{ periods: Array, isGunluk: boolean, gosterimPeriyot: string, gunlukAy: number }}
   */
  function getPeriodsBundleForTable() {
    const sel = document.getElementById("pg-periyot-select");
    const aySel = document.getElementById("pg-gunluk-ay-select");
    const periyot = (sel && sel.value) || "ceyrek";
    const dataYear = getDataYearForKarneLoad();
    const year = String(dataYear);
    const gunlukAy =
      periyot === "gunluk" && karneGunlukViewMonth != null
        ? karneGunlukViewMonth
        : aySel
          ? Math.max(1, Math.min(12, parseInt(aySel.value, 10) || 1))
          : 1;

    if (periyot === "gunluk") {
      return {
        periods: buildGunlukPeriods(dataYear, gunlukAy),
        isGunluk: true,
        gosterimPeriyot: "gunluk",
        gunlukAy,
        isVirtualHalf: false,
      };
    }
    if (periyot === "yillik") {
      return {
        periods: [{ key: "yillik_1", label: "Yıl Sonu" }],
        isGunluk: false,
        gosterimPeriyot: "yillik",
        gunlukAy,
        isVirtualHalf: false,
      };
    }
    if (periyot === "aylik") {
      return {
        periods: MONTHS.map((lab, i) => ({ key: `aylik_${i + 1}`, label: lab })),
        isGunluk: false,
        gosterimPeriyot: "aylik",
        gunlukAy,
        isVirtualHalf: false,
      };
    }
    if (periyot === "haftalik") {
      return {
        periods: buildHaftalikPeriodsForYear(year),
        isGunluk: false,
        gosterimPeriyot: "haftalik",
        gunlukAy,
        isVirtualHalf: false,
      };
    }
    if (periyot === "alti_ay") {
      return {
        periods: YARIYIL_PERIODS,
        isGunluk: false,
        gosterimPeriyot: "alti_ay",
        gunlukAy,
        isVirtualHalf: false,
      };
    }
    return {
      periods: QUARTER_PERIODS.map((p) => ({ key: p.key, label: p.label, periodNo: p.periodNo })),
      isGunluk: false,
      gosterimPeriyot: "ceyrek",
      gunlukAy,
      isVirtualHalf: false,
    };
  }

  function parsePeriodKeyForApi(periodKey) {
    if (!periodKey || String(periodKey).startsWith("__half_")) return null;
    if (periodKey === "halfyear_1") {
      return { period_type: "halfyear", period_no: 1 };
    }
    if (periodKey === "halfyear_2") {
      return { period_type: "halfyear", period_no: 2 };
    }
    if (periodKey.startsWith("ceyrek_")) {
      return { period_type: "ceyrek", period_no: parseInt(periodKey.split("_")[1], 10) };
    }
    if (periodKey.startsWith("yillik_")) {
      return { period_type: "yillik", period_no: parseInt(periodKey.split("_")[1], 10) || 1 };
    }
    if (periodKey.startsWith("aylik_")) {
      return { period_type: "aylik", period_no: parseInt(periodKey.split("_")[1], 10) };
    }
    const hm = periodKey.match(/^haftalik_(\d+)_(\d+)$/);
    if (hm) {
      return {
        period_type: "haftalik",
        period_no: parseInt(hm[1], 10),
        period_month: parseInt(hm[2], 10),
      };
    }
    const gm = periodKey.match(/^gunluk_(\d+)_(\d+)$/);
    if (gm) {
      return {
        period_type: "gunluk",
        period_no: parseInt(gm[1], 10),
        period_month: parseInt(gm[2], 10),
      };
    }
    return null;
  }

  function aggregateMonthlyForHalf(entries, half, method) {
    const months = half === 1 ? [1, 2, 3, 4, 5, 6] : [7, 8, 9, 10, 11, 12];
    const methodNorm = (method || "Ortalama").toLowerCase();
    const nums = [];
    months.forEach((m) => {
      const v = parseNum(entries[`aylik_${m}`]);
      if (v != null) nums.push(v);
    });
    if (!nums.length) return { hasVal: false, display: "—", val: null };
    let val;
    if (methodNorm === "toplama" || methodNorm === "toplam") {
      val = nums.reduce((a, b) => a + b, 0);
    } else {
      val = Math.round((nums.reduce((a, b) => a + b, 0) / nums.length) * 1000) / 1000;
    }
    return { hasVal: true, display: String(val), val };
  }

  let canCrudPg = viewRoot.dataset.canCrudPg === "true";
  let canEnterPgv = viewRoot.dataset.canEnterPgv === "true";
  let canCrudActivity = viewRoot.dataset.canCrudActivity === "true";
  let canTrackActivity = viewRoot.dataset.canTrackActivity === "true";
  let cachedProcessUsers = [];
  let cachedActivities = [];
  let activityViewMode = "kanban";

  function applyPermissionUi() {
    const bk = document.getElementById("btn-kpi-add");
    if (bk) bk.style.display = canCrudPg ? "" : "none";
    const ba = document.getElementById("btn-activity-add");
    if (ba) ba.style.display = canCrudActivity ? "" : "none";
  }
  applyPermissionUi();

  function resolveActivityViewMode() {
    const selected = String(activityViewModeSelect?.value || activityViewMode || "kanban").toLowerCase();
    return selected === "table" ? "table" : "kanban";
  }

  function applyActivityViewUi() {
    activityViewMode = resolveActivityViewMode();
    if (activityKanbanRoot) activityKanbanRoot.style.display = activityViewMode === "kanban" ? "" : "none";
    if (activityTableWrap) activityTableWrap.style.display = activityViewMode === "table" ? "" : "none";
  }

  function buildKpiOptionsHtml(selectedId) {
    const list = Array.isArray(cachedKpis) ? cachedKpis : [];
    const opts = ['<option value="">Bağımsız</option>'];
    list.forEach((k) => {
      const sel = String(selectedId || "") === String(k.id) ? " selected" : "";
      const code = (k.code || "").trim();
      const title = (k.name || "").trim();
      const label = `${code ? code + " " : ""}${title}`.trim() || `KPI #${k.id}`;
      opts.push(`<option value="${k.id}"${sel}>${escHtml(label)}</option>`);
    });
    return opts.join("");
  }

  function buildAssigneeCheckboxHtml(selectedIds) {
    const list = Array.isArray(cachedProcessUsers) ? cachedProcessUsers : [];
    const selected = new Set((selectedIds || []).map((x) => String(x)));
    const rows = [];
    list.forEach((u) => {
      const checked = selected.has(String(u.id)) ? " checked" : "";
      const label = u.full_name || u.email || `#${u.id}`;
      rows.push(
        `<label style="display:flex;align-items:center;gap:8px;padding:6px 8px;border:1px solid #e2e8f0;border-radius:8px;background:#fff;">
          <input class="mc-act-assignee-chk" type="checkbox" value="${u.id}"${checked}>
          <span style="font-size:13px;">${escHtml(label)}</span>
        </label>`
      );
    });
    if (!rows.length) {
      return `<div style="font-size:12px;color:#94a3b8;">Süreçte atanabilir kullanıcı bulunamadı.</div>`;
    }
    return `<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px;max-height:220px;overflow:auto;padding:4px;">${rows.join("")}</div>`;
  }

  function getCheckedReminderOffsets(prefix = "mc-act-rem-") {
    const ids = ["60", "1440", "4320", "7200"];
    return ids
      .map((v) => document.getElementById(`${prefix}${v}`))
      .filter((el) => el && el.checked)
      .map((el) => parseInt(el.value, 10))
      .filter((v) => !Number.isNaN(v));
  }

  async function openAddActivityModal() {
    if (!canCrudActivity) {
      showError("Faaliyet ekleme yetkiniz yok.");
      return;
    }
    if (typeof window.openMcFormModal !== "function") {
      showError("Form modali yüklenemedi.");
      return;
    }
    if ((!Array.isArray(cachedKpis) || cachedKpis.length === 0) || (!Array.isArray(cachedProcessUsers) || cachedProcessUsers.length === 0)) {
      try {
        const r = await fetch(`${KARNE_API}?year=${getDataYearForKarneLoad()}`);
        const d = await r.json();
        if (d.success) {
          cachedKpis = d.kpis || [];
          cachedProcessUsers = d.process_users || [];
        }
      } catch (_) {}
    }
    const bodyHtml = `
      <div style="display:flex;flex-direction:column;gap:12px;">
        <div class="mc-form-field" style="width:100%;">
          <label class="mc-form-label">Faaliyet Adı *</label>
          <input id="mc-act-name" class="mc-form-input" type="text" placeholder="Örn: Müşteri Ziyareti">
        </div>
        <div class="mc-form-field" style="width:100%;">
          <label class="mc-form-label">İlişkili PG</label>
          <select id="mc-act-kpi" class="mc-form-input">${buildKpiOptionsHtml("")}</select>
        </div>
        <div class="mc-form-field" style="width:100%;">
          <label class="mc-form-label">Atananlar *</label>
          ${buildAssigneeCheckboxHtml([currentUserId])}
          <small style="color:#94a3b8;">Süreç lideri birden fazla kişi seçebilir.</small>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
        <div class="mc-form-field" style="width:100%;">
          <label class="mc-form-label">Başlangıç Tarihi</label>
          <input id="mc-act-start" class="mc-form-input" type="datetime-local">
        </div>
        <div class="mc-form-field" style="width:100%;">
          <label class="mc-form-label">Bitiş Tarihi</label>
          <input id="mc-act-end" class="mc-form-input" type="datetime-local">
        </div>
        </div>
        <div class="mc-form-field">
          <label class="mc-form-label">Hatırlatmalar (başlangıca göre)</label>
          <div style="display:flex;flex-wrap:wrap;gap:8px;">
            <label><input id="mc-act-rem-60" type="checkbox" value="60"> 1 saat önce</label>
            <label><input id="mc-act-rem-1440" type="checkbox" value="1440"> 1 gün önce</label>
            <label><input id="mc-act-rem-4320" type="checkbox" value="4320"> 3 gün önce</label>
            <label><input id="mc-act-rem-7200" type="checkbox" value="7200"> 5 gün önce</label>
          </div>
        </div>
        <div class="mc-form-field">
          <label class="mc-form-label"><input id="mc-act-notify-email" type="checkbox"> E-posta da gönder</label>
        </div>
        <div class="mc-form-field" style="width:100%;">
          <label class="mc-form-label">Durum</label>
          <select id="mc-act-status" class="mc-form-input">
            <option value="Planlandı">Planlandı</option>
            <option value="Devam Ediyor">Devam Ediyor</option>
            <option value="Tamamlandı">Tamamlandı</option>
            <option value="İptal">İptal</option>
          </select>
        </div>
        <div class="mc-form-field" style="width:100%;">
          <label class="mc-form-label">Açıklama</label>
          <textarea id="mc-act-desc" class="mc-form-input" rows="3" placeholder="Opsiyonel"></textarea>
        </div>
      </div>
    `;

    const payload = await window.openMcFormModal({
      title: "Yeni Faaliyet",
      iconClass: "fas fa-list-check",
      bodyHtml,
      confirmText: "Kaydet",
      onConfirm: ({ showValidation }) => {
        const name = (document.getElementById("mc-act-name")?.value || "").trim();
        if (!name) {
          showValidation("Faaliyet adı zorunludur.");
          return false;
        }
        const startAt = document.getElementById("mc-act-start")?.value || null;
        const endAt = document.getElementById("mc-act-end")?.value || null;
        if (!startAt || !endAt) {
          showValidation("Başlangıç ve bitiş tarih/saat zorunludur.");
          return false;
        }
        if (endAt < startAt) {
          showValidation("Bitiş tarihi başlangıç tarihinden önce olamaz.");
          return false;
        }
        const assigneeIds = Array.from(document.querySelectorAll(".mc-act-assignee-chk:checked"))
          .map((o) => parseInt(o.value, 10))
          .filter((x) => !Number.isNaN(x));
        if (!assigneeIds.length) {
          showValidation("En az bir atanan seçiniz.");
          return false;
        }
        return {
          process_id: Number(currentProcessId || viewRoot.dataset.processId || 0),
          name,
          process_kpi_id: document.getElementById("mc-act-kpi")?.value || null,
          start_at: startAt,
          end_at: endAt,
          status: document.getElementById("mc-act-status")?.value || "Planlandı",
          description: (document.getElementById("mc-act-desc")?.value || "").trim(),
          assignee_ids: assigneeIds,
          reminder_offsets: getCheckedReminderOffsets("mc-act-rem-"),
          notify_email: !!document.getElementById("mc-act-notify-email")?.checked,
        };
      },
    });

    if (!payload) return;
    try {
      const data = await postJson("/process/api/activity/add", payload);
      if (!data.success) throw new Error(data.message || "Faaliyet kaydedilemedi.");
      toastSuccess(data.message || "Faaliyet eklendi.");
      await loadKarne();
    } catch (err) {
      showError(err.message || "Faaliyet eklenemedi.");
    }
  }

  const btnActivityAdd = document.getElementById("btn-activity-add");
  if (btnActivityAdd) {
    btnActivityAdd.addEventListener("click", (e) => {
      e.preventDefault();
      openAddActivityModal();
    });
  }

  const currentUserId = parseInt(
    document.querySelector('[data-current-user-id]')?.getAttribute('data-current-user-id') ||
    viewRoot.dataset.currentUserId ||
    "0",
    10
  ) || 0;

  function escHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  // ── Veri yükle (aynı API; sayfaya göre tablolar) ───────────────────────────
  async function loadKarne() {
    const year = String(getDataYearForKarneLoad());
    if (loadingEl) loadingEl.style.display = "";
    if (actTbody) actTbody.innerHTML = "";

    try {
      const data = await getJson(`${KARNE_API}?year=${year}`);
      if (!data.success) throw new Error(data.message || "Veri alınamadı.");
      if (data.permissions) {
        canCrudPg = !!data.permissions.can_crud_pg;
        canEnterPgv = !!data.permissions.can_enter_pgv;
        canCrudActivity = !!data.permissions.can_crud_activity;
        canTrackActivity = !!data.permissions.can_track_activity;
        applyPermissionUi();
      }
      cachedKpis = data.kpis || [];
      cachedProcessUsers = data.process_users || [];
      lastFavoriteKpiIds = data.favorite_kpi_ids || [];
      if (PAGE_MODE === "karne") {
        updateStatsKarne(data.kpis);
        renderKarneOverview(data.kpis, data.activities || []);
        populateTrendSelect(data.kpis);
        renderKanbanGauge(data.kpis, lastFavoriteKpiIds, year);
        syncPgGunlukAyHiddenSelect();
        updateKarneKanbanNavLabel();
      }
      // Faaliyet kartı hem karne hem faaliyet görünümünde ortak render edilir.
      cachedActivities = data.activities || [];
      updateStatsFaaliyet(cachedActivities);
      renderActivityKanban(cachedActivities);
      renderActivityTable(cachedActivities, year);
      applyActivityViewUi();
    } catch (err) {
      if (err && err.code === "AUTH_REQUIRED") {
        redirectToLogin();
        return;
      }
      showError("Veriler yüklenirken hata oluştu: " + err.message);
    } finally {
      if (loadingEl) loadingEl.style.display = "none";
    }
  }

  function kpiHasAnyEntry(k) {
    const e = k.entries || {};
    if (Object.values(e).some((v) => v != null && String(v).trim() !== "")) return true;
    return false;
  }

  function updateStatsKarne(kpis) {
    const totalPg = kpis ? kpis.length : 0;
    let filledPg = 0;
    if (kpis) {
      kpis.forEach((k) => {
        if (kpiHasAnyEntry(k)) filledPg++;
      });
    }
    const el = (id) => document.getElementById(id);
    if (el("stat-total-pg")) el("stat-total-pg").textContent = totalPg;
    if (el("stat-filled-pg")) el("stat-filled-pg").textContent = filledPg;
    const sum = document.getElementById("karne-pg-summary");
    if (sum) {
      sum.textContent =
        totalPg === 0
          ? "Henüz PG tanımlı değil"
          : `${totalPg} PG · ${filledPg} tanesinde seçili yılda veri var`;
    }
  }

  function parseNum(v) {
    if (v == null || v === "") return null;
    const n = parseFloat(String(v).replace(",", "."));
    return Number.isFinite(n) ? n : null;
  }

  /* ── Kök process_karne.js — yıllık / çeyrek hücre hedefi ── */
  function _normPeriyotMicro(s) {
    return (s || "")
      .toLowerCase()
      .replace(/ı/g, "i")
      .replace(/ü/g, "u")
      .replace(/ö/g, "o")
      .replace(/ç/g, "c")
      .replace(/ğ/g, "g")
      .trim();
  }

  function computeYillikHedefMicro(targetValue, olcumPeriyodu, hesaplamaYontemi) {
    const tv = parseFloat(targetValue);
    if (isNaN(tv) || tv <= 0) return null;
    if (hesaplamaYontemi !== "Toplama" && hesaplamaYontemi !== "Toplam") return tv;
    const olcumCarpan = {
      yillik: 1,
      ceyrek: 4,
      ceyreklik: 4,
      aylik: 12,
      haftalik: 52,
      gunluk: 365,
      "6 ay": 2,
      "6ay": 2,
    };
    const olcumNorm = _normPeriyotMicro(olcumPeriyodu);
    const is6ay = /^6\s*ay\b/.test(olcumNorm) || olcumNorm === "6ay" || olcumNorm.startsWith("6 ay");
    const carpan =
      olcumCarpan[olcumNorm] ??
      (is6ay
        ? 2
        : olcumNorm.includes("yil")
          ? 1
          : olcumNorm.includes("ceyrek")
            ? 4
            : olcumNorm.includes("ay")
              ? 12
              : olcumNorm.includes("hafta")
                ? 52
                : olcumNorm.includes("gun")
                  ? 365
                  : 1);
    return tv * carpan;
  }

  function computeCellTargetMicro(targetValue, olcumPeriyodu, hesaplamaYontemi, gosterimPeriyot) {
    const tv = parseFloat(targetValue);
    if (isNaN(tv) || tv <= 0) return null;
    if (
      hesaplamaYontemi === "Ortalama" ||
      hesaplamaYontemi === "Son Değer" ||
      !hesaplamaYontemi
    ) {
      return tv;
    }
    if (hesaplamaYontemi !== "Toplama" && hesaplamaYontemi !== "Toplam") return tv;
    const yillikHedef = computeYillikHedefMicro(targetValue, olcumPeriyodu, hesaplamaYontemi);
    if (yillikHedef === null) return null;
    const gp = (gosterimPeriyot || "ceyrek").toLowerCase();
    const gosterimBolum = {
      yillik: 1,
      ceyrek: 4,
      aylik: 12,
      haftalik: 52,
      gunluk: 365,
      alti_ay: 2,
    };
    const bolum = gosterimBolum[gp] || 4;
    return Math.round((yillikHedef / bolum) * 1000) / 1000;
  }

  function coerceBasariAralikStrMicro(v) {
    if (v == null) return null;
    if (typeof v === "object" && !Array.isArray(v)) {
      const r = v.aralik ?? v.range;
      if (r == null || String(r).trim() === "") return null;
      return String(r).trim();
    }
    const s = String(v).trim();
    return s || null;
  }

  function hesaplaBasariPuaniMicro(pct, araliklar) {
    if (!araliklar || typeof araliklar !== "object") return null;
    for (let puan = 1; puan <= 5; puan++) {
      const raw = araliklar[puan] || araliklar[String(puan)];
      const aralik = coerceBasariAralikStrMicro(raw);
      if (!aralik) continue;
      const parts = aralik.split("-");
      const minStr = parts[0];
      const maxStr = parts.length > 1 ? parts.slice(1).join("-") : undefined;
      const min = parseFloat(minStr) || 0;
      const max = maxStr !== undefined && String(maxStr).trim() !== "" ? parseFloat(maxStr) : Infinity;
      if (pct >= min && pct <= max) return puan;
    }
    return null;
  }

  function parseBasariAraliklarObjectMicro(k) {
    if (!k.basari_puani_araliklari) return null;
    try {
      return typeof k.basari_puani_araliklari === "string"
        ? JSON.parse(k.basari_puani_araliklari)
        : k.basari_puani_araliklari;
    } catch (e) {
      return null;
    }
  }

  /** Seçenek A: yıllık hedef sayısını 12’ye böl → aylık hedef (PG hedefi yıllık kabul) */
  function annualToMonthlyTarget(k) {
    const t = parseNum(k.target_value);
    if (t == null || t === 0) return null;
    return t / 12;
  }

  /**
   * Veri olan aylar için: (gerçek − aylık_hedef) / aylık_hedef × 100 ortalaması.
   * Azalan yönde (↑ kötü) sapma işareti ters çevrilir: hedefin altı “iyi” → pozitif tarafa yaklaştırılır.
   */
  function computeKpiAvgDeviationPct(k) {
    const mt = annualToMonthlyTarget(k);
    if (mt == null || mt === 0) return null;
    const decreasing = String(k.direction || "").toLowerCase() === "decreasing";
    const parts = [];
    for (let m = 1; m <= 12; m++) {
      const a = parseNum((k.entries || {})[`aylik_${m}`]);
      if (a == null) continue;
      let pct = ((a - mt) / mt) * 100;
      if (decreasing) pct = -pct;
      parts.push(pct);
    }
    if (!parts.length) return null;
    const avg = parts.reduce((s, x) => s + x, 0) / parts.length;
    return Math.round(avg * 10) / 10;
  }

  function sapmaCellHtml(pct) {
    if (pct == null) {
      return `<span class="karne-sapma karne-sapma--na" title="Hedef sayısal değil veya veri yok">—</span>`;
    }
    const sign = pct > 0 ? "+" : "";
    const cls =
      pct >= 3 ? "karne-sapma karne-sapma--good" : pct <= -3 ? "karne-sapma karne-sapma--bad" : "karne-sapma karne-sapma--mid";
    return `<span class="${cls}" title="Yıllık hedef ÷ 12 ile aylık hedef; verili ayların ortalama sapması">${sign}${pct}%</span>`;
  }

  /** Seçili yıl aylık girişlerinden özet + hedefe göre başarı yüzdesi */
  function computeKpiYearlyMetrics(k) {
    const target = parseNum(k.target_value);
    const vals = [];
    for (let m = 1; m <= 12; m++) {
      const x = parseNum((k.entries || {})[`aylik_${m}`]);
      if (x != null) vals.push(x);
    }
    if (vals.length === 0) {
      for (let q = 1; q <= 4; q++) {
        const x = parseNum((k.entries || {})[`ceyrek_${q}`]);
        if (x != null) vals.push(x);
      }
    }
    const yearlyActual =
      vals.length === 0 ? null : vals.reduce((a, b) => a + b, 0) / vals.length;
    let successPct = null;
    if (target != null && target !== 0 && yearlyActual != null) {
      const dec = String(k.direction || "Increasing").toLowerCase() === "decreasing";
      successPct = dec
        ? Math.min(100, Math.round((target / yearlyActual) * 100))
        : Math.min(100, Math.round((yearlyActual / target) * 100));
    }
    return { target, yearlyActual, successPct, monthCount: vals.length };
  }

  function healthBand(score) {
    if (score == null) return { label: "Veri yok", cls: "karne-health-na" };
    if (score >= 85) return { label: "Çok iyi", cls: "karne-health-high" };
    if (score >= 70) return { label: "İyi", cls: "karne-health-good" };
    if (score >= 50) return { label: "Orta", cls: "karne-health-mid" };
    return { label: "Geliştirilmeli", cls: "karne-health-low" };
  }

  function successPillClass(pct) {
    if (pct == null) return "karne-pct-pill karne-pct-na";
    if (pct >= 80) return "karne-pct-pill karne-pct-high";
    if (pct >= 50) return "karne-pct-pill karne-pct-mid";
    return "karne-pct-pill karne-pct-low";
  }

  let kpiDonutChart = null;

  function renderKarneOverview(kpis, activities) {
    const list = kpis || [];
    const metrics = list.map((k) => ({ k, m: computeKpiYearlyMetrics(k) }));
    const scored = metrics.filter((x) => x.m.successPct != null).map((x) => x.m.successPct);
    const health =
      scored.length === 0
        ? null
        : Math.round(scored.reduce((a, b) => a + b, 0) / scored.length);

    const hv = document.getElementById("karne-health-value");
    const hb = document.getElementById("karne-health-badge");
    if (hv) hv.textContent = health == null ? "—" : String(health);
    if (hb) {
      const b = healthBand(health);
      hb.textContent = b.label;
      hb.className = "karne-health-badge " + b.cls;
    }

    let basarili = 0;
    let orta = 0;
    let kritik = 0;
    let belirsiz = 0;
    metrics.forEach(({ m }) => {
      if (m.successPct == null) {
        belirsiz++;
        return;
      }
      if (m.successPct >= 70) basarili++;
      else if (m.successPct >= 40) orta++;
      else kritik++;
    });

    const legend = document.getElementById("kpi-donut-legend");
    if (legend) {
      legend.innerHTML = [
        `<li><span class="lgd lgd--ok"></span> Başarılı (≥70%): <strong>${basarili}</strong></li>`,
        `<li><span class="lgd lgd--mid"></span> Orta (40–69%): <strong>${orta}</strong></li>`,
        `<li><span class="lgd lgd--bad"></span> Kritik (&lt;40%): <strong>${kritik}</strong></li>`,
        `<li><span class="lgd lgd--na"></span> Hedef/veri eksik: <strong>${belirsiz}</strong></li>`,
      ].join("");
    }

    const canvas = document.getElementById("kpi-donut-chart");
    if (canvas && typeof Chart !== "undefined") {
      const dataVals = [basarili, orta, kritik, belirsiz];
      const sumV = dataVals.reduce((a, b) => a + b, 0);
      if (kpiDonutChart) kpiDonutChart.destroy();
      if (sumV === 0) {
        kpiDonutChart = null;
        const ctx = canvas.getContext("2d");
        if (ctx) {
          ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
      } else {
        kpiDonutChart = new Chart(canvas, {
          type: "doughnut",
          data: {
            labels: ["Başarılı", "Orta", "Kritik", "Tanımsız"],
            datasets: [
              {
                data: dataVals,
                backgroundColor: ["#10b981", "#f59e0b", "#ef4444", "#cbd5e1"],
                borderWidth: 0,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: "62%",
            plugins: {
              legend: { display: false },
            },
          },
        });
      }
    }

    const acts = activities || [];
    const actPct =
      acts.length === 0
        ? 0
        : Math.round(acts.reduce((s, a) => s + (Number(a.progress) || 0), 0) / acts.length);
    const barA = document.getElementById("karne-bar-activities");
    const pctA = document.getElementById("karne-pct-activities");
    if (barA) barA.style.width = actPct + "%";
    if (pctA) pctA.textContent = actPct + "%";

    let filledCells = 0;
    const totalCells = list.length * 12;
    list.forEach((k) => {
      for (let m = 1; m <= 12; m++) {
        const raw = (k.entries || {})[`aylik_${m}`];
        if (raw != null && String(raw).trim() !== "") filledCells++;
      }
    });
    const kpiFill = totalCells === 0 ? 0 : Math.round((filledCells / totalCells) * 100);
    const barK = document.getElementById("karne-bar-kpi-fill");
    const pctK = document.getElementById("karne-pct-kpi-fill");
    if (barK) barK.style.width = kpiFill + "%";
    if (pctK) pctK.textContent = kpiFill + "%";

    const hint = document.getElementById("karne-activity-counts");
    if (hint) {
      const done = acts.filter((a) => (Number(a.progress) || 0) >= 100).length;
      hint.textContent =
        acts.length === 0
          ? "Tanımlı faaliyet yok"
          : `${acts.length} faaliyet · ${done} tamamlanmış (ilerleme %100)`;
    }
  }

  const modalKpiAdd = document.getElementById("modal-kpi-add");
  const formKpiAdd = document.getElementById("form-kpi-add");
  const modalKpiDataEntry = document.getElementById("modal-kpi-data-entry");
  const formKpiDataEntry = document.getElementById("form-kpi-data-entry");

  /** @type {number|null} */
  let editingKpiId = null;

  const cachedKpisRef = {
    get kpis() {
      return cachedKpis;
    },
  };

  const safeNoop = () => {};
  const defaultVgsApi = {
    openDataEntryModal: safeNoop,
    closeKpiDataEntryModal: safeNoop,
    closeVgsHistoryNestedModals: safeNoop,
  };
  const vgsApi =
    typeof globalThis.initSurecVgs === "function"
      ? globalThis.initSurecVgs({
          MONTHS,
          parsePeriodKeyForApi,
          escHtml,
          showError,
          toastSuccess,
          postJson,
          viewRoot,
          modalKpiDataEntry,
          formKpiDataEntry,
          getCanEnterPgv: () => canEnterPgv,
          cachedKpisRef,
          KPI_DATA_ADD_URL,
          KPI_DATA_HISTORY_URL_TEMPLATE,
          KPI_DATA_UPDATE_URL_TEMPLATE,
          KPI_DATA_DELETE_URL_TEMPLATE,
          expandKpiUrl,
          expandKpiDataRowUrl,
          BIREYSEL_ENSURE_PG_URL,
          BIREYSEL_VERI_ADD_URL,
          loadKarne,
        })
      : defaultVgsApi;
  const {
    openDataEntryModal = safeNoop,
    closeKpiDataEntryModal = safeNoop,
    closeVgsHistoryNestedModals = safeNoop,
  } = vgsApi || defaultVgsApi;

  /** Kök karne «Performans Göstergeleri» tablosu — PG kartına tıklanınca */
  let microPgTablo = null;
  if (typeof globalThis.initMicroPgTabloModal === "function" && PAGE_MODE === "karne") {
    microPgTablo = globalThis.initMicroPgTabloModal({
      escHtml,
      showError,
      toastSuccess,
      postJson,
      karneApiUrl: KARNE_API,
      kpiDetailUrl: viewRoot.dataset.kpiDataDetailUrl || "",
      kpiProjeUrl: viewRoot.dataset.kpiDataProjeUrl || "",
      expandKpiDataRowUrl,
      kpiDataUpdateTemplate: KPI_DATA_UPDATE_URL_TEMPLATE,
      kpiDataDeleteTemplate: KPI_DATA_DELETE_URL_TEMPLATE,
      kpiDataRowPlaceholder: KPI_DATA_ROW_PLACEHOLDER,
      openAddKpiModal: () => openAddKpiModal(),
      onAfterMutation: () => loadKarne(),
      canCrudPg,
    });
  }

  function toggleKpiAddBasariPanel() {
    const chk = document.getElementById("kpi-add-basari-enable");
    const body = document.getElementById("kpi-add-basari-body");
    if (body) body.hidden = !(chk && chk.checked);
  }

  function setKpiAddModalMode(isEdit) {
    const titleEl = document.getElementById("modal-kpi-add-title-text");
    const iconEl = document.getElementById("btn-kpi-add-modal-save-icon");
    const saveText = document.getElementById("btn-kpi-add-modal-save-text");
    if (titleEl) {
      titleEl.textContent = isEdit ? "Performans göstergesini düzenle" : "Yeni Performans Göstergesi";
    }
    if (iconEl) {
      iconEl.className = isEdit ? "fas fa-save" : "fas fa-plus-circle";
      iconEl.setAttribute("aria-hidden", "true");
    }
    if (saveText) saveText.textContent = isEdit ? "Güncelle" : "Kaydet";
  }

  /** KPI API’den gelen başarı puanı JSON / objesini forma yazar */
  function fillBasariFromKpi(bpRaw) {
    let obj = null;
    if (bpRaw != null && typeof bpRaw === "string" && String(bpRaw).trim()) {
      try {
        obj = JSON.parse(bpRaw);
      } catch (_) {
        obj = null;
      }
    } else if (bpRaw != null && typeof bpRaw === "object") {
      obj = bpRaw;
    }
    const hasAny = obj && typeof obj === "object" && Object.keys(obj).length > 0;
    const chk = document.getElementById("kpi-add-basari-enable");
    if (chk) chk.checked = !!hasAny;
    toggleKpiAddBasariPanel();
    for (let i = 1; i <= 5; i++) {
      const arEl = document.getElementById(`kpi-add-bp-aralik-${i}`);
      const acEl = document.getElementById(`kpi-add-bp-aciklama-${i}`);
      const entry = obj ? obj[i] ?? obj[String(i)] : null;
      let ar = "";
      let ac = "";
      if (entry != null) {
        if (typeof entry === "object" && entry !== null) {
          ar = entry.aralik != null ? String(entry.aralik) : "";
          ac = entry.aciklama != null ? String(entry.aciklama) : "";
        } else {
          ar = String(entry);
        }
      }
      if (arEl) arEl.value = ar;
      if (acEl) acEl.value = ac;
    }
  }

  function openAddKpiModal() {
    if (!canCrudPg || !KPI_ADD_URL || !modalKpiAdd || !formKpiAdd) return;
    editingKpiId = null;
    formKpiAdd.reset();
    fillBasariFromKpi(null);
    setKpiAddModalMode(false);
    toggleKpiAddBasariPanel();
    modalKpiAdd.classList.add("open");
    modalKpiAdd.setAttribute("aria-hidden", "false");
    const first = document.getElementById("kpi-add-name");
    if (first) setTimeout(() => first.focus(), 50);
  }

  async function openEditKpiModal(kpiId) {
    if (!canCrudPg || !modalKpiAdd || !formKpiAdd) return;
    const id = parseInt(String(kpiId), 10);
    if (Number.isNaN(id)) return;
    const url = expandKpiUrl(KPI_GET_TEMPLATE, id);
    if (!url) {
      showError("Düzenleme adresi tanımlı değil.");
      return;
    }
    try {
      const res = await getJson(url);
      if (!res.success || !res.kpi) {
        showError(res.message || "PG bilgisi alınamadı.");
        return;
      }
      const k = res.kpi;
      editingKpiId = id;
      formKpiAdd.reset();
      setKpiAddModalMode(true);

      const setVal = (idEl, v) => {
        const el = document.getElementById(idEl);
        if (el) el.value = v != null && v !== "" ? String(v) : "";
      };
      setVal("kpi-add-name", k.name);
      setVal("kpi-add-code", k.code);
      setVal("kpi-add-target", k.target_value);
      setVal("kpi-add-unit", k.unit);
      setVal("kpi-add-weight", k.weight != null ? String(k.weight) : "");
      const per = document.getElementById("kpi-add-period");
      if (per && k.period) per.value = k.period;
      const dir = document.getElementById("kpi-add-direction");
      if (dir && k.direction) dir.value = k.direction;
      const coll = document.getElementById("kpi-add-collection");
      if (coll && k.data_collection_method) coll.value = k.data_collection_method;
      const gt = document.getElementById("kpi-add-gosterge-turu");
      if (gt) gt.value = k.gosterge_turu != null ? String(k.gosterge_turu) : "";
      const tm = document.getElementById("kpi-add-target-method");
      if (tm) tm.value = k.target_method != null ? String(k.target_method) : "";
      const ss = document.getElementById("kpi-add-substrategy");
      if (ss) ss.value = k.sub_strategy_id != null ? String(k.sub_strategy_id) : "";
      setVal("kpi-add-description", k.description);
      if (k.onceki_yil_ortalamasi != null && k.onceki_yil_ortalamasi !== "") {
        setVal("kpi-add-prev-year", String(k.onceki_yil_ortalamasi));
      } else {
        setVal("kpi-add-prev-year", "");
      }
      fillBasariFromKpi(k.basari_puani_araliklari);

      modalKpiAdd.classList.add("open");
      modalKpiAdd.setAttribute("aria-hidden", "false");
      const first = document.getElementById("kpi-add-name");
      if (first) setTimeout(() => first.focus(), 50);
    } catch (err) {
      showError(err.message || "PG yüklenemedi.");
    }
  }

  function closeAddKpiModal() {
    if (!modalKpiAdd) return;
    editingKpiId = null;
    setKpiAddModalMode(false);
    modalKpiAdd.classList.remove("open");
    modalKpiAdd.setAttribute("aria-hidden", "true");
  }

  async function submitAddKpiModal() {
    if (!canCrudPg || !KPI_ADD_URL || !formKpiAdd) return;
    const pid = viewRoot.dataset.processId;
    const nameEl = document.getElementById("kpi-add-name");
    const name = nameEl ? nameEl.value.trim() : "";
    if (!name) {
      showError("Gösterge adı zorunludur.");
      if (nameEl) nameEl.focus();
      return;
    }
    const ssEl = document.getElementById("kpi-add-substrategy");
    const ss = ssEl && ssEl.value ? ssEl.value : "";
    const prevYearRaw = (document.getElementById("kpi-add-prev-year")?.value || "").trim();
    const gosterge = (document.getElementById("kpi-add-gosterge-turu")?.value || "").trim();
    const targetMethod = (document.getElementById("kpi-add-target-method")?.value || "").trim();

    let basariAraliklari = null;
    const basariChk = document.getElementById("kpi-add-basari-enable");
    if (basariChk && basariChk.checked) {
      const o = {};
      for (let i = 1; i <= 5; i++) {
        const ar = document.getElementById(`kpi-add-bp-aralik-${i}`)?.value?.trim() || "";
        const ac = document.getElementById(`kpi-add-bp-aciklama-${i}`)?.value?.trim() || "";
        if (ar || ac) {
          if (ac) o[i] = { aralik: ar, aciklama: ac };
          else o[i] = ar;
        }
      }
      if (Object.keys(o).length > 0) basariAraliklari = JSON.stringify(o);
    }

    const body = {
      process_id: parseInt(pid, 10),
      name,
      code: (document.getElementById("kpi-add-code")?.value || "").trim() || null,
      target_value: (document.getElementById("kpi-add-target")?.value || "").trim() || null,
      unit: (document.getElementById("kpi-add-unit")?.value || "").trim() || null,
      weight: parseFloat(document.getElementById("kpi-add-weight")?.value) || 0,
      period: document.getElementById("kpi-add-period")?.value || "Çeyreklik",
      direction: document.getElementById("kpi-add-direction")?.value || "Increasing",
      data_collection_method: document.getElementById("kpi-add-collection")?.value || "Ortalama",
      gosterge_turu: gosterge || null,
      target_method: targetMethod || null,
      description: (document.getElementById("kpi-add-description")?.value || "").trim() || null,
      onceki_yil_ortalamasi:
        prevYearRaw === ""
          ? null
          : (() => {
              const n = parseFloat(prevYearRaw);
              return Number.isFinite(n) ? n : null;
            })(),
      basari_puani_araliklari: basariAraliklari,
    };
    body.sub_strategy_id = ss ? parseInt(ss, 10) : null;
    if (body.weight < 0 || body.weight > 100) {
      showError("Skor ağırlığı 0 ile 100 arasında olmalıdır.");
      document.getElementById("kpi-add-weight")?.focus();
      return;
    }
    const isEdit = editingKpiId != null;
    const postUrl = isEdit ? expandKpiUrl(KPI_UPDATE_TEMPLATE, editingKpiId) : KPI_ADD_URL;
    if (isEdit && !postUrl) {
      showError("Güncelleme adresi tanımlı değil.");
      return;
    }
    const payload = { ...body };
    if (isEdit) {
      delete payload.process_id;
    }
    const saveBtn = document.getElementById("btn-kpi-add-modal-save");
    if (saveBtn) saveBtn.disabled = true;
    try {
      const data = await postJson(postUrl, payload);
      if (data.success) {
        closeAddKpiModal();
        toastSuccess(isEdit ? "Performans göstergesi güncellendi." : "Performans göstergesi eklendi.");
        loadKarne();
      } else {
        showError(data.message || "Kayıt başarısız.");
      }
    } catch (err) {
      showError(err.message || "Sunucu hatası.");
    } finally {
      if (saveBtn) saveBtn.disabled = false;
    }
  }

  function updateStatsFaaliyet(activities) {
    const totalAct = activities ? activities.length : 0;
    let doneAct = 0;
    if (activities) {
      activities.forEach((a) => {
        const vals = Object.values(a.monthly_tracks || {});
        if (vals.some((v) => v === true)) doneAct++;
      });
    }
    const pct = totalAct > 0 ? Math.round((doneAct / totalAct) * 100) : 0;
    const el = (id) => document.getElementById(id);
    if (el("stat-activities")) el("stat-activities").textContent = totalAct;
    if (el("stat-done-pct")) el("stat-done-pct").textContent = pct + "%";
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
  document.getElementById('trend-kpi-select')?.addEventListener('change', function () {
    const kpi = cachedKpis.find(k => String(k.id) === this.value);
    renderTrendChart(kpi || null);
  });

  // ── Kanban + gauge (PG kartları) ──────────────────────────────────────────
  function formatTargetDisplay(cellTarget, targetValRaw) {
    if (cellTarget != null) {
      return Number.isInteger(cellTarget)
        ? String(cellTarget)
        : String(Math.round(cellTarget * 1000) / 1000);
    }
    return escHtml(String(targetValRaw ?? "—"));
  }

  /** Eski PG tablosu ile aynı başarı yüzdesi (kolon ayrımı için); veri yok → null */
  function computeKpiKanbanScorePct(k) {
    const entries = k.entries || {};
    const hesap = k.data_collection_method || "Ortalama";
    const olcumPer = k.period || "";
    const yillikHedef = computeYillikHedefMicro(k.target_value, olcumPer, hesap);
    const allVals = Object.values(entries)
      .map((v) => parseNum(v))
      .filter((v) => v != null);
    const skorTarget = yillikHedef != null ? yillikHedef : parseNum(k.target_value);
    if (allVals.length === 0 || skorTarget == null || Number.isNaN(skorTarget) || skorTarget <= 0) {
      return null;
    }
    const compareVal =
      hesap === "Toplama" || hesap === "Toplam"
        ? allVals.reduce((a, b) => a + b, 0)
        : allVals[allVals.length - 1];
    let pct = Math.round((compareVal / skorTarget) * 100);
    if (k.direction === "Decreasing") {
      pct = compareVal > 0 ? Math.round((skorTarget / compareVal) * 100) : 0;
    }
    return Math.max(0, Math.min(100, pct));
  }

  /** Kolon eşiği aynı; yay rengi skora göre kırmızı(0°) → sarı → yeşil(120°) HSL geçişi */
  function kanbanBucketFromPct(pctRaw) {
    if (pctRaw === null || pctRaw === undefined || Number.isNaN(pctRaw)) {
      return { col: "risk", pctFill: 0, valText: "—", scoreHue: null };
    }
    const p = Math.max(0, Math.min(100, Math.round(pctRaw)));
    const scoreHue = p * 1.2;
    if (p >= 80) {
      return { col: "hedefte", pctFill: p, valText: `%${p}`, scoreHue };
    }
    if (p >= 50) {
      return { col: "risk", pctFill: p, valText: `%${p}`, scoreHue };
    }
    return { col: "disi", pctFill: p, valText: `%${p}`, scoreHue };
  }

  /** @param {number} pctFill @param {boolean} useSpectrum */
  function buildKanbanGaugeSvg(pctFill, useSpectrum) {
    const p = Math.max(0, Math.min(100, pctFill));
    const dolu = Math.round((p / 100) * 58);
    const bos = 58 - dolu;
    const arcClass = useSpectrum ? "kb-gauge-arc kb-gauge-arc--spectrum" : "kb-gauge-arc kb-gauge-arc--neutral";
    return `<svg class="kb-gauge-svg" width="48" height="26" viewBox="0 0 48 26" aria-hidden="true">
      <path class="kb-gauge-track" d="M 4 22 A 20 20 0 0 1 44 22" pathLength="58" />
      <path class="${arcClass}" d="M 4 22 A 20 20 0 0 1 44 22" pathLength="58" stroke-dasharray="${dolu} ${bos}" />
    </svg>`;
  }

  function getDefaultPeriodContextForKanban(yearStr, view, gunlukAy) {
    const y = parseInt(yearStr, 10);
    const now = new Date();
    const cy = now.getFullYear();
    const cm = now.getMonth() + 1;
    const cd = now.getDate();

    if (view === "yillik") {
      return {
        periodKey: "yillik_1",
        label: `Yıl sonu ${y}`,
        gosterimPeriyot: "yillik",
        metaPeriodLabel: "Yıllık",
      };
    }
    if (view === "ceyrek") {
      let q;
      if (y < cy) q = 4;
      else if (y > cy) q = 1;
      else q = Math.floor((cm - 1) / 3) + 1;
      const qi = Math.max(1, Math.min(4, q));
      return {
        periodKey: `ceyrek_${qi}`,
        label: `${QUARTER_PERIODS[qi - 1].label} ${y}`,
        gosterimPeriyot: "ceyrek",
        metaPeriodLabel: QUARTER_PERIODS[qi - 1].label,
      };
    }
    if (view === "aylik") {
      let m;
      if (y < cy) m = 12;
      else if (y > cy) m = 1;
      else m = cm;
      return {
        periodKey: `aylik_${m}`,
        label: `${MONTHS[m - 1]} ${y}`,
        gosterimPeriyot: "aylik",
        metaPeriodLabel: MONTHS[m - 1],
      };
    }
    if (view === "gunluk") {
      const mo = Math.max(1, Math.min(12, gunlukAy || 1));
      let d;
      if (y === cy && mo === cm) d = cd;
      else d = 1;
      return {
        periodKey: `gunluk_${d}_${mo}`,
        label: `Gün ${d} — ${MONTHS[mo - 1]} ${y}`,
        gosterimPeriyot: "gunluk",
        metaPeriodLabel: `Günlük · ${MONTHS[mo - 1]}`,
      };
    }
    if (view === "haftalik") {
      let m;
      if (y < cy) m = 12;
      else if (y > cy) m = 1;
      else m = cm;
      let w;
      if (y === cy && m === cm) w = Math.min(5, Math.floor((cd - 1) / 7) + 1);
      else w = 1;
      const hLbl = haftalikRangeLabelKb(y, m, w) || `${MONTHS[m - 1]} H${w}`;
      return {
        periodKey: `haftalik_${w}_${m}`,
        label: `${hLbl} ${y}`,
        gosterimPeriyot: "haftalik",
        metaPeriodLabel: hLbl,
      };
    }
    if (view === "alti_ay") {
      let halfKey;
      let meta;
      if (y < cy) {
        halfKey = "halfyear_2";
        meta = "2. yarıyıl";
      } else if (y > cy) {
        halfKey = "halfyear_1";
        meta = "1. yarıyıl";
      } else {
        halfKey = cm <= 6 ? "halfyear_1" : "halfyear_2";
        meta = cm <= 6 ? "1. yarıyıl" : "2. yarıyıl";
      }
      return {
        periodKey: halfKey,
        label: `${meta} ${y}`,
        gosterimPeriyot: "alti_ay",
        metaPeriodLabel: meta,
      };
    }
    return getDefaultPeriodContextForKanban(yearStr, "ceyrek", gunlukAy);
  }

  /** Rozet alt satırı: hangi çeyrek / ay / hafta aralığı / yarıyıl vb. */
  function formatPeriodBadgeSubline(ctx, view, dataYearNum) {
    if (!ctx || !view) return "—";
    if (view === "yillik") return "Yıl sonu";
    if (view === "aylik" && ctx.periodKey) {
      const mm = ctx.periodKey.match(/^aylik_(\d+)$/);
      if (mm) return AYLAR_TR_FULL_KB[parseInt(mm[1], 10) - 1];
    }
    if (view === "gunluk" && ctx.periodKey) {
      const gm = ctx.periodKey.match(/^gunluk_(\d+)_(\d+)$/);
      if (gm) {
        const day = parseInt(gm[1], 10);
        const mo = parseInt(gm[2], 10);
        return `${day} ${AYLAR_TR_FULL_KB[mo - 1]}`;
      }
    }
    if (view === "ceyrek" && ctx.periodKey) {
      const qq = ctx.periodKey.match(/^ceyrek_(\d+)$/);
      if (qq) {
        const qi = parseInt(qq[1], 10);
        const p = QUARTER_PERIODS[qi - 1];
        return p ? p.label : ctx.metaPeriodLabel || "—";
      }
    }
    if (view === "alti_ay") {
      if (ctx.periodKey === "halfyear_1") return "Ocak – Haziran";
      if (ctx.periodKey === "halfyear_2") return "Temmuz – Aralık";
    }
    if (view === "haftalik" && ctx.periodKey) {
      const hm = ctx.periodKey.match(/^haftalik_(\d+)_(\d+)$/);
      if (hm && dataYearNum != null && !Number.isNaN(dataYearNum)) {
        const lbl = haftalikRangeLabelKb(dataYearNum, parseInt(hm[2], 10), parseInt(hm[1], 10));
        if (lbl) return lbl;
      }
    }
    return ctx.metaPeriodLabel || "—";
  }

  function buildGunlukKanbanCtx(y, m, d) {
    const mo = Math.max(1, Math.min(12, m));
    const ld = new Date(y, mo, 0).getDate();
    const day = Math.max(1, Math.min(ld, d));
    return {
      periodKey: `gunluk_${day}_${mo}`,
      label: `Gün ${day} — ${MONTHS[mo - 1]} ${y}`,
      gosterimPeriyot: "gunluk",
      metaPeriodLabel: `Günlük · ${MONTHS[mo - 1]}`,
    };
  }

  function getPeriodContextExplicit(dataYear, view, periodKey) {
    const y = dataYear;
    const yStr = String(y);
    if (view === "yillik") {
      return {
        periodKey: "yillik_1",
        label: `Yıl sonu ${y}`,
        gosterimPeriyot: "yillik",
        metaPeriodLabel: "Yıllık",
      };
    }
    if (view === "ceyrek") {
      const m = periodKey && periodKey.match(/^ceyrek_(\d+)$/);
      const qi = m ? parseInt(m[1], 10) : 1;
      const qix = Math.max(1, Math.min(4, qi));
      const p = QUARTER_PERIODS[qix - 1];
      return {
        periodKey: `ceyrek_${qix}`,
        label: `${p.label} ${y}`,
        gosterimPeriyot: "ceyrek",
        metaPeriodLabel: p.label,
      };
    }
    if (view === "aylik") {
      const m = periodKey && periodKey.match(/^aylik_(\d+)$/);
      const mi = m ? parseInt(m[1], 10) : 1;
      const mm = Math.max(1, Math.min(12, mi));
      return {
        periodKey: `aylik_${mm}`,
        label: `${MONTHS[mm - 1]} ${y}`,
        gosterimPeriyot: "aylik",
        metaPeriodLabel: MONTHS[mm - 1],
      };
    }
    if (view === "alti_ay") {
      const is2 = periodKey === "halfyear_2";
      const meta = is2 ? "2. yarıyıl" : "1. yarıyıl";
      return {
        periodKey: is2 ? "halfyear_2" : "halfyear_1",
        label: `${meta} ${y}`,
        gosterimPeriyot: "alti_ay",
        metaPeriodLabel: meta,
      };
    }
    if (view === "haftalik") {
      const hm = periodKey && periodKey.match(/^haftalik_(\d+)_(\d+)$/);
      if (hm) {
        const w = parseInt(hm[1], 10);
        const mo = parseInt(hm[2], 10);
        const hLbl = haftalikRangeLabelKb(y, mo, w) || "";
        return {
          periodKey,
          label: `${hLbl} ${y}`,
          gosterimPeriyot: "haftalik",
          metaPeriodLabel: hLbl,
        };
      }
    }
    if (view === "gunluk") {
      const gm = periodKey && periodKey.match(/^gunluk_(\d+)_(\d+)$/);
      if (gm) {
        const d0 = parseInt(gm[1], 10);
        const mo = parseInt(gm[2], 10);
        return buildGunlukKanbanCtx(y, mo, d0);
      }
    }
    return getDefaultPeriodContextForKanban(yStr, view, 1);
  }

  function stepHaftalikPeriodKey(pk, year, delta) {
    function weeksOf(yr) {
      return buildHaftalikPeriodsForYear(String(yr));
    }
    let y = year;
    let arr = weeksOf(y);
    if (!arr.length) return { periodKey: pk, year: y };
    let idx = arr.findIndex((p) => p.key === pk);
    if (idx < 0) idx = 0;
    let i = idx + delta;
    const maxGuard = 500;
    let guard = 0;
    while (i < 0 && guard++ < maxGuard) {
      y -= 1;
      arr = weeksOf(y);
      if (arr.length) i += arr.length;
      else i = 0;
    }
    guard = 0;
    while (i >= arr.length && guard++ < maxGuard) {
      i -= arr.length;
      y += 1;
      arr = weeksOf(y);
      if (!arr.length) {
        y += 1;
        arr = weeksOf(y);
      }
    }
    if (!arr.length || i < 0 || i >= arr.length) return { periodKey: pk, year };
    return { periodKey: arr[i].key, year: y };
  }

  function stepNonGunlukPeriodKey(pk, view, y, delta) {
    if (view === "yillik") {
      return { periodKey: "yillik_1", year: y + delta };
    }
    if (view === "ceyrek") {
      const m = pk && pk.match(/^ceyrek_(\d+)$/);
      let q = m ? parseInt(m[1], 10) : 1;
      q += delta;
      let yy = y;
      while (q < 1) {
        q += 4;
        yy -= 1;
      }
      while (q > 4) {
        q -= 4;
        yy += 1;
      }
      return { periodKey: `ceyrek_${q}`, year: yy };
    }
    if (view === "aylik") {
      const m = pk && pk.match(/^aylik_(\d+)$/);
      let mo = m ? parseInt(m[1], 10) : 1;
      mo += delta;
      let yy = y;
      while (mo < 1) {
        mo += 12;
        yy -= 1;
      }
      while (mo > 12) {
        mo -= 12;
        yy += 1;
      }
      return { periodKey: `aylik_${mo}`, year: yy };
    }
    if (view === "alti_ay") {
      let half = pk === "halfyear_2" ? 2 : 1;
      half += delta;
      let yy = y;
      while (half < 1) {
        half += 2;
        yy -= 1;
      }
      while (half > 2) {
        half -= 2;
        yy += 1;
      }
      return { periodKey: half === 2 ? "halfyear_2" : "halfyear_1", year: yy };
    }
    if (view === "haftalik") {
      return stepHaftalikPeriodKey(pk, y, delta);
    }
    return { periodKey: pk, year: y };
  }

  function karneNavSyncYearSelect(y) {
    if (!yearSelect) return;
    if ([...yearSelect.options].some((o) => o.value === String(y))) {
      yearSelect.value = String(y);
    }
    syncPgKarneYilFromBanner();
  }

  function ensureKarneNavCursorFromDefault() {
    const view = getPgKarneView();
    if (view === "gunluk") return;
    if (karneNavPeriodKey != null && karneNavDataYear != null) return;
    const base = yearSelect ? parseInt(yearSelect.value, 10) || new Date().getFullYear() : new Date().getFullYear();
    const ctx = getDefaultPeriodContextForKanban(String(base), view, 1);
    karneNavPeriodKey = ctx.periodKey;
    karneNavDataYear = base;
  }

  function getKanbanPeriodContextForMain(dataYearStr, view) {
    const base = yearSelect ? parseInt(yearSelect.value, 10) || new Date().getFullYear() : new Date().getFullYear();
    if (view === "gunluk") {
      const y = karneGunlukViewYear != null ? karneGunlukViewYear : parseInt(dataYearStr, 10) || base;
      const m =
        karneGunlukViewMonth != null
          ? karneGunlukViewMonth
          : Math.max(
              1,
              Math.min(12, parseInt(document.getElementById("pg-gunluk-ay-select")?.value, 10) || new Date().getMonth() + 1)
            );
      let d = karneGunlukViewDay;
      if (d == null) {
        const tmp = getDefaultPeriodContextForKanban(String(y), "gunluk", m);
        const gm = tmp.periodKey.match(/^gunluk_(\d+)_(\d+)$/);
        d = gm ? parseInt(gm[1], 10) : 1;
      }
      const ld = new Date(y, m, 0).getDate();
      d = Math.max(1, Math.min(ld, d));
      return buildGunlukKanbanCtx(y, m, d);
    }
    if (karneNavPeriodKey != null && karneNavDataYear != null) {
      return getPeriodContextExplicit(karneNavDataYear, view, karneNavPeriodKey);
    }
    return getDefaultPeriodContextForKanban(String(base), view, 1);
  }

  function gunlukKarneStep(delta) {
    let y = karneGunlukViewYear != null ? karneGunlukViewYear : parseInt(yearSelect.value, 10);
    let m =
      karneGunlukViewMonth != null
        ? karneGunlukViewMonth
        : Math.max(1, Math.min(12, parseInt(document.getElementById("pg-gunluk-ay-select")?.value, 10) || new Date().getMonth() + 1));
    let d = karneGunlukViewDay;
    if (d == null) {
      const tmp = getDefaultPeriodContextForKanban(String(y), "gunluk", m);
      const gm = tmp.periodKey.match(/^gunluk_(\d+)_(\d+)$/);
      d = gm ? parseInt(gm[1], 10) : 1;
    }
    const ld = (yy, mo) => new Date(yy, mo, 0).getDate();
    d += delta;
    if (delta < 0) {
      while (d < 1) {
        if (m > 1) {
          m -= 1;
          d += ld(y, m);
        } else {
          y -= 1;
          m = 12;
          d += ld(y, m);
        }
      }
    } else {
      while (d > ld(y, m)) {
        d -= ld(y, m);
        if (m < 12) m += 1;
        else {
          m = 1;
          y += 1;
        }
      }
    }
    karneGunlukViewYear = y;
    karneGunlukViewMonth = m;
    karneGunlukViewDay = d;
    karneNavSyncYearSelect(y);
  }

  globalThis.kokpitimKarneBadgeDetail = function (yearStr, view, gunlukMonthOpt, gunlukDayOpt) {
    const yNum = parseInt(yearStr, 10);
    if (view === "gunluk") {
      const gAy = gunlukMonthOpt != null ? gunlukMonthOpt : new Date().getMonth() + 1;
      let d = gunlukDayOpt;
      if (d == null) {
        const ctx0 = getDefaultPeriodContextForKanban(yearStr, view, gAy);
        const gm = ctx0.periodKey.match(/^gunluk_(\d+)_(\d+)$/);
        d = gm ? parseInt(gm[1], 10) : 1;
      }
      const ctx = buildGunlukKanbanCtx(yNum, gAy, d);
      return formatPeriodBadgeSubline(ctx, view, yNum);
    }
    const ctx = getDefaultPeriodContextForKanban(yearStr, view, gunlukMonthOpt != null ? gunlukMonthOpt : 1);
    return formatPeriodBadgeSubline(ctx, view, yNum);
  };

  function getMetaGercekKanban(k, view, periodKey) {
    const ent = k.entries || {};
    const hesap = k.data_collection_method || "Ortalama";
    if (view === "alti_ay") {
      const v = ent[periodKey];
      if (v !== undefined && v !== null && String(v).trim() !== "") return escHtml(String(v));
      const half = periodKey === "halfyear_2" ? 2 : 1;
      const agg = aggregateMonthlyForHalf(ent, half, hesap);
      return agg.hasVal ? escHtml(String(agg.display)) : "—";
    }
    const v = ent[periodKey];
    if (v !== undefined && v !== null && String(v).trim() !== "") return escHtml(String(v));
    return "—";
  }

  function getMetaHedefKanban(k, view, gosterimPeriyot) {
    const hesap = k.data_collection_method || "Ortalama";
    const olcumPer = k.period || "";
    const gp = view === "alti_ay" ? "alti_ay" : gosterimPeriyot;
    const ct = computeCellTargetMicro(k.target_value, olcumPer, hesap, gp);
    return formatTargetDisplay(ct, k.target_value || "—");
  }

  function renderKanbanGauge(kpis, favoriteIds, year) {
    const colH = document.getElementById("kb-col-hedefte");
    const colR = document.getElementById("kb-col-risk");
    const colD = document.getElementById("kb-col-disi");
    const emptyEl = document.getElementById("kb-kanban-empty");
    const gridEl = document.getElementById("kb-kanban-grid");
    if (!colH || !colR || !colD) return;

    const sel = document.getElementById("pg-periyot-select");
    const view = (sel && sel.value) || "ceyrek";
    const ctx = getKanbanPeriodContextForMain(String(year), view);

    colH.innerHTML = "";
    colR.innerHTML = "";
    colD.innerHTML = "";

    if (!kpis || kpis.length === 0) {
      if (gridEl) gridEl.classList.add("is-hidden");
      if (emptyEl) emptyEl.classList.remove("is-hidden");
      return;
    }
    if (gridEl) gridEl.classList.remove("is-hidden");
    if (emptyEl) emptyEl.classList.add("is-hidden");

    const favSet = new Set(favoriteIds || []);
    const counts = { hedefte: 0, risk: 0, disi: 0 };

    const appendCard = (colEl, html) => {
      colEl.insertAdjacentHTML("beforeend", html);
    };

    kpis.forEach((k) => {
      const pctRaw = computeKpiKanbanScorePct(k);
      const bucket = kanbanBucketFromPct(pctRaw);
      counts[bucket.col] += 1;

      const w = k.weight != null && k.weight !== "" ? Number(k.weight) : null;
      const wDisplay = w != null && !Number.isNaN(w) ? String(w) : "—";
      const isFav = favSet.has(k.id);
      const favBtn = FAVORITE_TOGGLE_URL
        ? `<button type="button" class="mc-btn mc-btn-sm mc-btn-secondary karne-fav-kpi-btn ${isFav ? "karne-fav-kpi-btn--on" : ""}" data-kpi-id="${k.id}" title="Favori"><i class="fas fa-star"></i></button>`
        : `<button type="button" class="mc-btn mc-btn-sm mc-btn-secondary" disabled title="Favori"><i class="fas fa-star"></i></button>`;
      const editBtn =
        canCrudPg && KPI_GET_TEMPLATE
          ? `<button type="button" class="mc-btn mc-btn-sm mc-btn-secondary btn-kpi-edit" data-kpi-id="${k.id}" title="Düzenle"><i class="fas fa-pen text-slate-600 dark:text-slate-300"></i></button>`
          : "";
      const delBtn = canCrudPg
        ? `<button type="button" class="mc-btn mc-btn-sm mc-btn-secondary btn-kpi-delete" data-kpi-id="${k.id}" title="Sil"><i class="fas fa-trash text-red-500"></i></button>`
        : "";

      const subCode = (k.sub_strategy_code && String(k.sub_strategy_code).trim()) || "";
      const subTitle = escHtml(k.sub_strategy_title || "—");
      const subLine = subCode
        ? `<div class="kb-substr-row"><span class="kb-sub-code">${escHtml(subCode)}</span><span>${subTitle}</span></div>`
        : `<div class="kb-substr-row"><span>${subTitle}</span></div>`;

      const hedefMeta = getMetaHedefKanban(k, view, ctx.gosterimPeriyot);
      const gercekMeta = getMetaGercekKanban(k, view, ctx.periodKey);
      const hasSpectrum = bucket.scoreHue != null;
      const gaugeWrapStyle = hasSpectrum ? ` style="--gauge-h:${bucket.scoreHue}deg"` : "";
      const valCls = hasSpectrum ? "kb-gauge-val kb-gauge-val--spectrum" : "kb-gauge-val kb-gauge-val--neutral";
      const safeKey = String(ctx.periodKey).replace(/"/g, "&quot;");
      const safeLabel = String(ctx.label).replace(/"/g, "&quot;");
      const vgsBtn = canEnterPgv
        ? `<button type="button" class="mc-btn mc-btn-sm mc-btn-secondary btn-kpi-vgs" data-kpi-id="${k.id}" data-year="${year}" data-period-key="${safeKey}" data-label="${safeLabel}" title="Veri Girişi Sihirbazı (VGS)"><i class="fas fa-wand-magic-sparkles" aria-hidden="true"></i></button>`
        : "";

      const cardInner = `
      <div class="kb-card" data-kpi-id="${k.id}">
        <div class="kb-card-top">
          <div class="kb-card-name-block">
            <div>
              <span class="kb-code-badge">${escHtml(k.code || "—")}</span>
              <span class="kb-card-name">${escHtml(k.name || "—")}</span>
            </div>
            ${subLine}
          </div>
          <div class="kb-card-actions no-print">${favBtn}${editBtn}${delBtn}${vgsBtn}</div>
          <div class="kb-gauge-wrap"${gaugeWrapStyle}>
            ${buildKanbanGaugeSvg(bucket.pctFill, hasSpectrum)}
            <div class="${valCls}">${bucket.valText}</div>
          </div>
        </div>
        <div class="kb-card-divider"></div>
        <div class="kb-card-meta">
          <div class="kb-card-meta-item">
            <span class="kb-meta-label">Hedef</span>
            <span class="kb-meta-val">${hedefMeta}</span>
          </div>
          <div class="kb-card-meta-item">
            <span class="kb-meta-label">Gerçekleşen</span>
            <span class="kb-meta-val">${gercekMeta}</span>
          </div>
          <div class="kb-card-meta-item">
            <span class="kb-meta-label">Birim</span>
            <span class="kb-meta-val">${escHtml(k.unit || "—")}</span>
          </div>
          <div class="kb-card-meta-item">
            <span class="kb-meta-label">Periyot</span>
            <span class="kb-meta-val">${escHtml(k.period || "—")}</span>
          </div>
        </div>
        <div class="kb-card-weight">Ağırlık: ${wDisplay === "—" ? "—" : `${escHtml(wDisplay)} %`}</div>
      </div>`;

      if (bucket.col === "hedefte") appendCard(colH, cardInner);
      else if (bucket.col === "risk") appendCard(colR, cardInner);
      else appendCard(colD, cardInner);
    });

    const ch = document.getElementById("kb-count-hedefte");
    const cr = document.getElementById("kb-count-risk");
    const cd = document.getElementById("kb-count-disi");
    if (ch) ch.textContent = String(counts.hedefte);
    if (cr) cr.textContent = String(counts.risk);
    if (cd) cd.textContent = String(counts.disi);
  }

  function renderActivityKanban(activities) {
    const colPlan = document.getElementById("act-col-plan");
    const colProgress = document.getElementById("act-col-progress");
    const colDone = document.getElementById("act-col-done");
    const emptyEl = document.getElementById("activity-kanban-empty");
    if (!colPlan || !colProgress || !colDone) return;
    colPlan.innerHTML = "";
    colProgress.innerHTML = "";
    colDone.innerHTML = "";

    if (!activities || activities.length === 0) {
      if (emptyEl) emptyEl.classList.remove("is-hidden");
      document.getElementById("act-count-plan").textContent = "0";
      document.getElementById("act-count-progress").textContent = "0";
      document.getElementById("act-count-done").textContent = "0";
      return;
    }
    if (emptyEl) emptyEl.classList.add("is-hidden");

    const counts = { plan: 0, progress: 0, done: 0 };
    const normalizeStatusText = (status) =>
      String(status || "")
        .toLowerCase()
        .replace(/ı/g, "i")
        .replace(/İ/g, "i")
        .replace(/ç/g, "c")
        .replace(/ğ/g, "g")
        .replace(/ö/g, "o")
        .replace(/ş/g, "s")
        .replace(/ü/g, "u")
        .replace(/�/g, "");
    const statusBucket = (status) => {
      const s = normalizeStatusText(status);
      if (s.includes("devam")) return "progress";
      if (s.includes("gercek") || s.includes("tamam") || s.includes("iptal")) return "done";
      return "plan";
    };

    activities.forEach((a) => {
      const bucket = statusBucket(a.status);
      counts[bucket] += 1;
      const plan = [a.start_at || a.start_date || "—", a.end_at || a.end_date || "—"].join(" → ");
      const assignees = Array.isArray(a.assignees) && a.assignees.length
        ? a.assignees.map((u) => u.full_name || u.email || `#${u.id}`).join(", ")
        : "Atama yok";
      const kpiLabel = a.process_kpi_name || "Bağımsız faaliyet";
      const card = `
        <div class="kb-card" data-act-id="${a.id}">
          <div class="kb-card-top">
            <div class="kb-card-name-block">
              <div><span class="kb-code-badge">FAALİYET</span> <span class="kb-card-name">${escHtml(a.name || "—")}</span></div>
              <div class="kb-card-subline">${escHtml(a.status || "Planlandı")}</div>
            </div>
            <div class="kb-card-actions no-print">
              ${canCrudActivity ? `<button type="button" class="btn-act-postpone text-amber-500 hover:text-amber-700 text-xs" data-act-id="${a.id}" title="Ertele"><i class="fas fa-clock"></i></button>` : ""}
              ${canCrudActivity ? `<button type="button" class="btn-act-cancel text-red-400 hover:text-red-600 text-xs" data-act-id="${a.id}" title="İptal"><i class="fas fa-ban"></i></button>` : ""}
              ${canCrudActivity ? `<button type="button" class="btn-act-delete text-red-400 hover:text-red-600 text-xs" data-act-id="${a.id}" title="Sil"><i class="fas fa-trash"></i></button>` : ""}
            </div>
          </div>
          <div class="kb-card-divider"></div>
          <div class="kb-card-meta">
            <div class="kb-card-meta-item"><span class="kb-meta-label">Plan</span><span class="kb-meta-val">${escHtml(plan)}</span></div>
            <div class="kb-card-meta-item"><span class="kb-meta-label">Atanan</span><span class="kb-meta-val">${escHtml(assignees)}</span></div>
            <div class="kb-card-meta-item"><span class="kb-meta-label">İlişkili PG</span><span class="kb-meta-val">${escHtml(kpiLabel)}</span></div>
            <div class="kb-card-meta-item"><span class="kb-meta-label">Hatırlatma</span><span class="kb-meta-val">${(a.reminder_offsets || []).length || 0} kayıt</span></div>
          </div>
        </div>`;
      if (bucket === "plan") colPlan.insertAdjacentHTML("beforeend", card);
      else if (bucket === "progress") colProgress.insertAdjacentHTML("beforeend", card);
      else colDone.insertAdjacentHTML("beforeend", card);
    });
    document.getElementById("act-count-plan").textContent = String(counts.plan);
    document.getElementById("act-count-progress").textContent = String(counts.progress);
    document.getElementById("act-count-done").textContent = String(counts.done);
  }

  // ── Faaliyet tablosu render ───────────────────────────────────────────────
  function renderActivityTable(activities, year) {
    if (!actTbody) return;
    if (!activities || activities.length === 0) {
      actTbody.innerHTML = `<tr><td colspan="16" class="text-center py-8 text-gray-400">Henüz faaliyet eklenmemiş.</td></tr>`;
      return;
    }

    actTbody.innerHTML = activities.map((a, i) => {
      const monthCells = Array.from({ length: 12 }, (_, idx) => {
        const month = idx + 1;
        const done = a.monthly_tracks[month] === true;
        const dis = canTrackActivity ? "" : " disabled";
        return `<td class="px-2 py-2 text-center">
          <input type="checkbox" class="track-checkbox w-4 h-4 accent-emerald-600 cursor-pointer"
                 data-act-id="${a.id}" data-month="${month}" data-year="${year}"
                 ${done ? "checked" : ""}${dis}>
        </td>`;
      }).join("");

      const sNorm = String(a.status || "")
        .toLowerCase()
        .replace(/ı/g, "i")
        .replace(/İ/g, "i")
        .replace(/ç/g, "c")
        .replace(/ğ/g, "g")
        .replace(/ö/g, "o")
        .replace(/ş/g, "s")
        .replace(/ü/g, "u")
        .replace(/�/g, "");
      const statusColor =
        sNorm.includes("gercek") || sNorm.includes("tamam")
          ? "text-emerald-600"
          : sNorm.includes("devam")
            ? "text-blue-600"
            : sNorm.includes("iptal")
              ? "text-red-400"
              : "text-gray-500";

      return `<tr data-act-id="${a.id}">
        <td class="px-3 py-2 text-gray-400">${i + 1}</td>
        <td class="px-3 py-2">
          <span class="font-medium text-gray-800 dark:text-gray-100">${escHtml(a.name)}</span>
        </td>
        <td class="px-3 py-2 text-center text-xs ${statusColor}">${escHtml(a.status || "—")}</td>
        ${monthCells}
        <td class="px-3 py-2 text-center">${
          canCrudActivity
            ? `<button type="button" class="btn-act-delete text-red-400 hover:text-red-600 text-xs" data-act-id="${a.id}" title="Sil">
            <i class="fas fa-trash"></i>
          </button>`
            : "—"
        }</td>
      </tr>`;
    }).join("");
  }

  function toDateTimeLocalValue(input) {
    if (!input) return "";
    const s = String(input).replace(" ", "T");
    return s.length >= 16 ? s.slice(0, 16) : s;
  }

  async function openPostponeActivityModal(actId) {
    if (!canCrudActivity) return;
    const activity = (cachedActivities || []).find((a) => String(a.id) === String(actId));
    const startVal = toDateTimeLocalValue(activity?.start_at || activity?.start_date || "");
    const endVal = toDateTimeLocalValue(activity?.end_at || activity?.end_date || "");
    if (typeof window.openMcFormModal !== "function") {
      showError("Form modali yüklenemedi.");
      return;
    }
    const payload = await window.openMcFormModal({
      title: "Faaliyet Ertele",
      iconClass: "fas fa-clock",
      confirmText: "Ertele",
      bodyHtml: `
        <div style="display:flex;flex-direction:column;gap:12px;">
          <div class="mc-form-field">
            <label class="mc-form-label">Yeni Başlangıç</label>
            <input id="mc-postpone-start" class="mc-form-input" type="datetime-local" value="${escHtml(startVal)}">
          </div>
          <div class="mc-form-field">
            <label class="mc-form-label">Yeni Bitiş</label>
            <input id="mc-postpone-end" class="mc-form-input" type="datetime-local" value="${escHtml(endVal)}">
          </div>
        </div>
      `,
      onConfirm: ({ showValidation }) => {
        const startAt = document.getElementById("mc-postpone-start")?.value || "";
        const endAt = document.getElementById("mc-postpone-end")?.value || "";
        if (!startAt || !endAt) {
          showValidation("Başlangıç ve bitiş zorunludur.");
          return false;
        }
        if (endAt <= startAt) {
          showValidation("Bitiş başlangıçtan sonra olmalıdır.");
          return false;
        }
        return { start_at: startAt, end_at: endAt };
      },
    });
    if (!payload) return;
    try {
      const data = await postJson(`/process/api/activity/postpone/${actId}`, payload);
      if (!data.success) throw new Error(data.message || "Faaliyet ertelenemedi.");
      toastSuccess(data.message || "Faaliyet ertelendi.");
      await loadKarne();
    } catch (err) {
      showError(err.message || "Erteleme işlemi başarısız.");
    }
  }

  // ── Event delegation ──────────────────────────────────────────────────────
  document.addEventListener("click", async (e) => {
    const btnKpiEdit = e.target.closest(".btn-kpi-edit");
    if (btnKpiEdit) {
      e.preventDefault();
      e.stopPropagation();
      if (!canCrudPg) return;
      openEditKpiModal(btnKpiEdit.dataset.kpiId);
      return;
    }

    const btnKpiVgs = e.target.closest(".btn-kpi-vgs");
    if (btnKpiVgs) {
      e.preventDefault();
      e.stopPropagation();
      if (!canEnterPgv) return;
      openDataEntryModal(btnKpiVgs.dataset.kpiId, btnKpiVgs.dataset.year, {
        periodKey: btnKpiVgs.dataset.periodKey || undefined,
        label: btnKpiVgs.dataset.label || "Dönem",
      });
      return;
    }

    const kbCardTablo = e.target.closest(".kb-card");
    if (kbCardTablo && PAGE_MODE === "karne" && microPgTablo && !e.target.closest(".kb-card-actions")) {
      e.preventDefault();
      e.stopPropagation();
      const kid = kbCardTablo.dataset.kpiId;
      if (kid) microPgTablo.open(parseInt(kid, 10));
      return;
    }

    const favBtn = e.target.closest(".karne-fav-kpi-btn");
    if (favBtn && FAVORITE_TOGGLE_URL) {
      e.preventDefault();
      try {
        const data = await postJson(FAVORITE_TOGGLE_URL, { kpi_id: parseInt(favBtn.dataset.kpiId, 10) });
        if (data.success) {
          toastSuccess(data.message || "Güncellendi.");
          loadKarne();
        } else showError(data.message || "İşlem başarısız.");
      } catch (err) {
        showError(err.message || "Sunucu hatası.");
      }
      return;
    }

    // KPI sil
    const btnKpiDel = e.target.closest(".btn-kpi-delete");
    if (btnKpiDel) {
      if (!canCrudPg) return;
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
      if (!canCrudActivity) return;
      const ok = await confirmDelete("Faaliyet silinsin mi?", "Faaliyet pasife alınacak.");
      if (!ok) return;
      try {
        const data = await postJson(`${ACT_DELETE_BASE}${btnActDel.dataset.actId}`, {});
        if (data.success) { toastSuccess("Faaliyet silindi."); loadKarne(); }
        else showError(data.message);
      } catch (err) { showError(err.message); }
      return;
    }

    const btnActCancel = e.target.closest(".btn-act-cancel");
    if (btnActCancel) {
      if (!canCrudActivity) return;
      const ok = await confirmDelete("Faaliyet iptal edilsin mi?", "Faaliyet durumu 'İptal' olarak güncellenecek.");
      if (!ok) return;
      try {
        const data = await postJson(`/process/api/activity/cancel/${btnActCancel.dataset.actId}`, {});
        if (!data.success) throw new Error(data.message || "Faaliyet iptal edilemedi.");
        toastSuccess(data.message || "Faaliyet iptal edildi.");
        loadKarne();
      } catch (err) {
        showError(err.message || "İşlem başarısız.");
      }
      return;
    }

    const btnActPostpone = e.target.closest(".btn-act-postpone");
    if (btnActPostpone) {
      if (!canCrudActivity) return;
      await openPostponeActivityModal(btnActPostpone.dataset.actId);
      return;
    }
  });

  // ── Faaliyet takip checkbox ───────────────────────────────────────────────
  document.addEventListener("change", async (e) => {
    const cb = e.target.closest(".track-checkbox");
    if (!cb) return;
    if (!canTrackActivity) {
      cb.checked = !cb.checked;
      return;
    }
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

  async function exportKarneExcel() {
    if (PAGE_MODE !== "karne" || !yearSelect) return;
    if (!KARNE_EXPORT_XLSX_URL) {
      showError("Excel dışa aktarma adresi tanımlı değil.");
      return;
    }
    const year = String(getDataYearForKarneLoad());
    const kpis = cachedKpis || [];
    const bundle = getPeriodsBundleForTable();
    const { periods, isGunluk, isVirtualHalf, gosterimPeriyot } = bundle;

    const headers = [
      "Kod",
      "Ana_Strateji",
      "Alt_Strateji",
      "PG_Adi",
      "Yillik_hedef",
      "Birim",
      "Gosterim",
    ];
    periods.forEach((p) => {
      const slug = String(p.label).replace(/\s+/g, "_").replace(/[()–]/g, "");
      if (isGunluk) headers.push(`Gun_${slug}`);
      else headers.push(`${slug}_Hedef`, `${slug}_Gercek`);
    });
    const rows = [];
    kpis.forEach((k) => {
      const ent = k.entries || {};
      const hesap = k.data_collection_method || "Ortalama";
      const row = [];
      row.push(k.code ? String(k.code) : "");
      row.push(k.strategy_title || "");
      row.push(k.sub_strategy_title || "");
      row.push(k.name || "");
      row.push(
        k.target_value != null && String(k.target_value).trim() !== ""
          ? String(k.target_value).replace(",", ".")
          : ""
      );
      row.push(k.unit || "");
      row.push(gosterimPeriyot);
      periods.forEach((p) => {
        if (isGunluk) {
          const v = ent[p.key];
          row.push(v != null && String(v).trim() !== "" ? String(v).replace(",", ".") : "");
          return;
        }
        if (isVirtualHalf && p.half) {
          const agg = aggregateMonthlyForHalf(ent, p.half, hesap);
          const ct = computeCellTargetMicro(k.target_value, k.period || "", hesap, gosterimPeriyot);
          row.push(ct != null ? String(ct).replace(",", ".") : "");
          row.push(agg.hasVal && agg.val != null ? String(agg.val).replace(",", ".") : "");
          return;
        }
        const ct = computeCellTargetMicro(k.target_value, k.period || "", hesap, gosterimPeriyot);
        const v = ent[p.key];
        row.push(ct != null ? String(ct).replace(",", ".") : "");
        row.push(v != null && String(v).trim() !== "" ? String(v).replace(",", ".") : "");
      });
      rows.push(row);
    });

    const xbtn = document.getElementById("btn-karne-excel");
    if (xbtn) xbtn.disabled = true;
    try {
      const res = await fetch(KARNE_EXPORT_XLSX_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrf(),
          Accept: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/json",
        },
        body: JSON.stringify({
          year: parseInt(year, 10) || year,
          headers,
          rows,
        }),
        credentials: "same-origin",
      });
      const ct = (res.headers.get("Content-Type") || "").toLowerCase();
      if (!res.ok) {
        let msg = "Dışa aktarılamadı.";
        if (ct.includes("json")) {
          try {
            const j = await res.json();
            if (j.message) msg = j.message;
          } catch (_) {
            /* ignore */
          }
        }
        showError(msg);
        return;
      }
      const blob = await res.blob();
      const rawName = viewRoot.dataset.processName || "karne";
      const safeName = String(rawName)
        .replace(/[^\w\u00C0-\u024F\u0400-\u04FF-]+/gi, "_")
        .replace(/_+/g, "_")
        .slice(0, 60);
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `surec_karne_${safeName}_${year}.xlsx`;
      a.click();
      setTimeout(() => URL.revokeObjectURL(a.href), 5000);
      toastSuccess("Excel dosyası indirildi.");
    } catch (err) {
      showError(err.message || "Sunucu hatası.");
    } finally {
      if (xbtn) xbtn.disabled = false;
    }
  }

  function openKarneDataWizard() {
    if (PAGE_MODE !== "karne") return;
    if (!canEnterPgv) {
      showError("PG verisi girme yetkiniz yok.");
      return;
    }
    document.getElementById("kpi-section")?.scrollIntoView({ behavior: "smooth", block: "start" });
    const first = document.querySelector("#kanban-gauge-root .btn-kpi-vgs");
    if (first) {
      Swal.fire({
        icon: "info",
        title: "Veri giriş sihirbazı",
        html: "Üstteki <strong>Görünüm periyodu</strong> seçimi, VGS’de kaydedeceğiniz verinin <strong>hangi döneme</strong> yazılacağını belirler. Ardından ilgili PG kartında, favori / düzenle / sil ikonlarının yanındaki <strong>asa (sihirbaz)</strong> simgesine tıklayın.",
        confirmButtonText: "Tamam",
        confirmButtonColor: "#4f46e5",
      });
    } else {
      Swal.fire({
        icon: "info",
        title: "Veri giriş sihirbazı",
        text: "Önce bu sürece performans göstergesi ekleyin; veri girişi için PG kartındaki sihirbaz ikonunu kullanın.",
        confirmButtonColor: "#4f46e5",
      });
    }
  }

  // ── Yıl / süreç değişimi ──────────────────────────────────────────────────
  yearSelect.addEventListener("change", () => {
    karneNavPeriodKey = null;
    karneNavDataYear = null;
    if (getPgKarneView() === "gunluk") {
      const y = parseInt(yearSelect.value, 10) || new Date().getFullYear();
      const cy = new Date().getFullYear();
      const cm = new Date().getMonth() + 1;
      const cd = new Date().getDate();
      karneGunlukViewYear = y;
      karneGunlukViewMonth = y === cy ? cm : 1;
      karneGunlukViewDay = y === cy && karneGunlukViewMonth === cm ? cd : 1;
    }
    syncPgKarneYilFromBanner();
    syncPgGunlukAyHiddenSelect();
    updateKarneKanbanNavLabel();
    loadKarne();
  });

  processSelect.addEventListener("change", () => {
    const pid = processSelect.value;
    const wantsActivities = (() => {
      const q = new URLSearchParams(window.location.search);
      const tab = (q.get("tab") || INITIAL_TAB || "").toLowerCase();
      return tab === "activities";
    })();
    const qs = wantsActivities ? "?tab=activities" : "";
    window.location.href = `/process/${pid}/karne${qs}`;
  });

  document.getElementById("btn-kpi-add")?.addEventListener("click", openAddKpiModal);
  document.getElementById("btn-kpi-add-modal-close")?.addEventListener("click", closeAddKpiModal);
  document.getElementById("btn-kpi-add-modal-cancel")?.addEventListener("click", closeAddKpiModal);
  document.getElementById("btn-kpi-add-modal-save")?.addEventListener("click", () => submitAddKpiModal());
  document.getElementById("kpi-add-basari-enable")?.addEventListener("change", toggleKpiAddBasariPanel);
  formKpiAdd?.addEventListener("submit", (e) => {
    e.preventDefault();
    submitAddKpiModal();
  });
  modalKpiAdd?.addEventListener("click", (e) => {
    if (e.target === modalKpiAdd) closeAddKpiModal();
  });
  document.getElementById("btn-kpi-data-entry-close")?.addEventListener("click", closeKpiDataEntryModal);
  document.getElementById("btn-kpi-data-entry-cancel")?.addEventListener("click", closeKpiDataEntryModal);
  modalKpiDataEntry?.addEventListener("click", (e) => {
    if (e.target !== modalKpiDataEntry) return;
    if (document.getElementById("modal-vgs-history-edit")?.classList?.contains("open")) return;
    if (document.getElementById("modal-vgs-history-delete")?.classList?.contains("open")) return;
    closeKpiDataEntryModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    const microVeriDuz = document.getElementById("modal-micro-veri-duzenle");
    if (microVeriDuz?.classList?.contains("open")) {
      microVeriDuz.classList.remove("open");
      microVeriDuz.setAttribute("aria-hidden", "true");
      return;
    }
    const microVeriDet = document.getElementById("modal-micro-veri-detay");
    if (microVeriDet?.classList?.contains("open")) {
      microVeriDet.classList.remove("open");
      microVeriDet.setAttribute("aria-hidden", "true");
      return;
    }
    if (document.getElementById("modal-vgs-history-edit")?.classList?.contains("open")) {
      closeVgsHistoryNestedModals();
      return;
    }
    if (document.getElementById("modal-vgs-history-delete")?.classList?.contains("open")) {
      closeVgsHistoryNestedModals();
      return;
    }
    if (modalKpiDataEntry?.classList?.contains("open")) {
      closeKpiDataEntryModal();
      return;
    }
    const microPgTabloEl = document.getElementById("modal-micro-pg-tablo");
    if (microPgTabloEl?.classList?.contains("open") && microPgTablo && typeof microPgTablo.close === "function") {
      microPgTablo.close();
      return;
    }
    if (modalKpiAdd?.classList?.contains("open")) closeAddKpiModal();
  });
  document.getElementById("btn-karne-excel")?.addEventListener("click", () => {
    exportKarneExcel();
  });
  document.getElementById("btn-karne-wizard")?.addEventListener("click", openKarneDataWizard);
  document.getElementById("btn-karne-print")?.addEventListener("click", () => window.print());
  document.getElementById("btn-karne-tablo-gorunumu")?.addEventListener("click", () => {
    if (PAGE_MODE !== "karne") return;
    if (microPgTablo && typeof microPgTablo.open === "function") {
      microPgTablo.open(null);
    } else {
      showError("Tablo görünümü şu an kullanılamıyor.");
    }
  });

  function updatePgPeriyotGunlukAyVisibility() {
    const wrap = document.getElementById("pg-gunluk-ay-wrap");
    if (wrap) wrap.classList.add("is-hidden");
  }

  function exportActivitiesCsv() {
    const rows = (cachedActivities || []).map((a) => ({
      id: a.id ?? "",
      faaliyet: a.name ?? "",
      durum: a.status ?? "",
      baslangic: a.start_at || a.start_date || "",
      bitis: a.end_at || a.end_date || "",
      iliskili_pg: a.process_kpi_name || "",
      atananlar: (a.assignees || []).map((u) => u.full_name || u.email || `#${u.id}`).join(", "),
      hatirlatma: (a.reminder_offsets || []).join(", "),
    }));
    const headers = ["ID", "Faaliyet", "Durum", "Başlangıç", "Bitiş", "İlişkili PG", "Atananlar", "Hatırlatmalar (dk)"];
    const lines = [headers.join(";")];
    rows.forEach((r) => {
      const vals = [r.id, r.faaliyet, r.durum, r.baslangic, r.bitis, r.iliskili_pg, r.atananlar, r.hatirlatma]
        .map((v) => `"${String(v ?? "").replace(/"/g, '""')}"`);
      lines.push(vals.join(";"));
    });
    const blob = new Blob(["\uFEFF" + lines.join("\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const y = yearSelect ? yearSelect.value : String(new Date().getFullYear());
    a.download = `surec-faaliyetleri-${currentProcessId}-${y}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  document.getElementById("pg-karne-yil-select")?.addEventListener("change", (e) => {
    if (!yearSelect || PAGE_MODE !== "karne") return;
    yearSelect.value = e.target.value;
    karneNavPeriodKey = null;
    karneNavDataYear = null;
    if (getPgKarneView() === "gunluk") {
      const y = parseInt(yearSelect.value, 10) || new Date().getFullYear();
      const cy = new Date().getFullYear();
      const cm = new Date().getMonth() + 1;
      const cd = new Date().getDate();
      karneGunlukViewYear = y;
      karneGunlukViewMonth = y === cy ? cm : 1;
      karneGunlukViewDay = y === cy && karneGunlukViewMonth === cm ? cd : 1;
    }
    syncPgGunlukAyHiddenSelect();
    updateKarneKanbanNavLabel();
    loadKarne();
  });

  activityViewModeSelect?.addEventListener("change", () => {
    applyActivityViewUi();
  });

  document.getElementById("btn-activity-excel")?.addEventListener("click", () => {
    exportActivitiesCsv();
    toastSuccess("Faaliyet listesi dışa aktarıldı.");
  });
  document.getElementById("btn-activity-print")?.addEventListener("click", () => window.print());

  document.getElementById("pg-periyot-select")?.addEventListener("change", () => {
    updatePgPeriyotGunlukAyVisibility();
    resetKarneKanbanNavForViewChange(getPgKarneView());
    updateKarneKanbanNavLabel();
    if (PAGE_MODE === "karne" && yearSelect) {
      loadKarne();
    }
  });

  document.getElementById("pg-karne-nav-prev")?.addEventListener("click", () => {
    if (PAGE_MODE !== "karne" || !yearSelect) return;
    const view = getPgKarneView();
    if (view === "gunluk") {
      gunlukKarneStep(-1);
    } else {
      ensureKarneNavCursorFromDefault();
      const res = stepNonGunlukPeriodKey(karneNavPeriodKey, view, karneNavDataYear, -1);
      karneNavPeriodKey = res.periodKey;
      karneNavDataYear = res.year;
      karneNavSyncYearSelect(karneNavDataYear);
    }
    syncPgGunlukAyHiddenSelect();
    updateKarneKanbanNavLabel();
    loadKarne();
  });

  document.getElementById("pg-karne-nav-next")?.addEventListener("click", () => {
    if (PAGE_MODE !== "karne" || !yearSelect) return;
    const view = getPgKarneView();
    if (view === "gunluk") {
      gunlukKarneStep(1);
    } else {
      ensureKarneNavCursorFromDefault();
      const res = stepNonGunlukPeriodKey(karneNavPeriodKey, view, karneNavDataYear, 1);
      karneNavPeriodKey = res.periodKey;
      karneNavDataYear = res.year;
      karneNavSyncYearSelect(karneNavDataYear);
    }
    syncPgGunlukAyHiddenSelect();
    updateKarneKanbanNavLabel();
    loadKarne();
  });

  updatePgPeriyotGunlukAyVisibility();
  (function initKarnePgToolbar() {
    const sel = document.getElementById("pg-gunluk-ay-select");
    if (sel) sel.value = String(new Date().getMonth() + 1);
    if (PAGE_MODE === "karne") {
      syncPgKarneYilFromBanner();
      resetKarneKanbanNavForViewChange(getPgKarneView());
      updateKarneKanbanNavLabel();
    }
  })();

  // ── İlk yükleme ───────────────────────────────────────────────────────────
  function applyTabLayout() {
    if (PAGE_MODE !== "karne") return;
    const q = new URLSearchParams(window.location.search);
    const tab = (q.get("tab") || INITIAL_TAB || "kpi").toLowerCase();
    const isActivities = tab === "activities";
    const kpiSection = document.getElementById("kpi-section");
    const trendSection = document.getElementById("trend-chart-card");
    const activityStats = document.getElementById("faaliyet-stats");
    const activitySection = document.getElementById("activity-section");
    if (kpiSection) kpiSection.style.display = isActivities ? "none" : "";
    if (trendSection) trendSection.style.display = isActivities ? "none" : "";
    if (activityStats) activityStats.style.display = isActivities ? "" : "none";
    if (activitySection) activitySection.style.display = isActivities ? "" : "none";
  }

  applyTabLayout();
  loadKarne();
  if (PAGE_MODE === "karne") {
    const q = new URLSearchParams(window.location.search);
    const tab = (q.get("tab") || INITIAL_TAB || "").toLowerCase();
    if (tab === "activities") {
      setTimeout(() => {
        document.getElementById("activity-section")?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 120);
    }
  }

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
  const GET_URL_BASE = indexRoot.dataset.getUrlBase || "";
  const UPDATE_URL_BASE = indexRoot.dataset.updateUrlBase || "";
  const CAN_CRUD_PROCESS = indexRoot.dataset.canCrudProcess === "true";

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

  function readUsersPickJson() {
    const raw = document.getElementById("users-pick-json");
    if (!raw) return [];
    try {
      return JSON.parse(raw.textContent || "[]");
    } catch (e) {
      return [];
    }
  }

  function fillUserSelect(sel, users) {
    if (!sel) return;
    sel.innerHTML = "";
    const sorted = [...users].sort((a, b) => (a.label || "").localeCompare(b.label || "", "tr"));
    sorted.forEach((u) => {
      const o = document.createElement("option");
      o.value = String(u.id);
      o.textContent = u.label || String(u.id);
      sel.appendChild(o);
    });
  }

  /** Çift liste: seçilen id’ler sağda, diğerleri solda */
  function fillDualFromSelection(allUsers, selectedIds, sourceId, selectedId) {
    const set = new Set((selectedIds || []).map((x) => Number(x)));
    const src = document.getElementById(sourceId);
    const dst = document.getElementById(selectedId);
    if (!src || !dst) return;
    src.innerHTML = "";
    dst.innerHTML = "";
    const sorted = [...allUsers].sort((a, b) => (a.label || "").localeCompare(b.label || "", "tr"));
    sorted.forEach((u) => {
      const o = document.createElement("option");
      o.value = String(u.id);
      o.textContent = u.label || String(u.id);
      if (set.has(Number(u.id))) dst.appendChild(o);
      else src.appendChild(o);
    });
  }

  function setModalUiAddMode() {
    const hid = document.getElementById("surec-edit-id");
    if (hid) hid.value = "";
    const icon = document.getElementById("modal-surec-title-icon");
    if (icon) icon.className = "fas fa-plus-circle";
    const tit = document.getElementById("modal-surec-title-text");
    if (tit) tit.textContent = "Yeni Süreç Oluştur";
    const st = document.getElementById("btn-surec-save-text");
    if (st) st.textContent = "Süreci Kaydet";
    const sel = document.getElementById("surec-parent-id");
    if (sel) {
      [...sel.options].forEach((o) => {
        o.disabled = false;
      });
    }
  }

  function setModalUiEditMode() {
    const icon = document.getElementById("modal-surec-title-icon");
    if (icon) icon.className = "fas fa-pen-to-square";
    const tit = document.getElementById("modal-surec-title-text");
    if (tit) tit.textContent = "Süreci Düzenle";
    const st = document.getElementById("btn-surec-save-text");
    if (st) st.textContent = "Değişiklikleri Kaydet";
  }

  function applyParentSelectSelfDisable(processId) {
    const sel = document.getElementById("surec-parent-id");
    if (!sel || !processId) return;
    const pid = Number(processId);
    [...sel.options].forEach((o) => {
      if (!o.value) {
        o.disabled = false;
        return;
      }
      o.disabled = Number(o.value) === pid;
    });
  }

  function transferMultiOptions(fromId, toId) {
    const from = document.getElementById(fromId);
    const to = document.getElementById(toId);
    if (!from || !to) return;
    const picked = [...from.selectedOptions];
    if (!picked.length) return;
    picked.forEach((opt) => {
      to.appendChild(opt);
    });
  }

  function populateSubStrategyPicker() {
    const box = document.getElementById("surec-substrategy-box");
    const raw = document.getElementById("strategies-json");
    if (!box || !raw) return;
    let strategies = [];
    try {
      strategies = JSON.parse(raw.textContent || "[]");
    } catch (e) {
      strategies = [];
    }
    box.innerHTML = "";
    strategies.forEach((st) => {
      const subs = st.sub_strategies || [];
      if (!subs.length) return;
      const h = document.createElement("div");
      h.style.marginBottom = "10px";
      h.innerHTML = `<div style="font-size:11px; font-weight:700; color:#64748b; margin-bottom:6px;">${(st.code || "") + " " + (st.title || "")}</div>`;
      const wrap = document.createElement("div");
      wrap.style.display = "flex";
      wrap.style.flexDirection = "column";
      wrap.style.gap = "4px";
      subs.forEach((ss) => {
        const id = `ss-${ss.id}`;
        const row = document.createElement("label");
        row.style.display = "flex";
        row.style.alignItems = "center";
        row.style.gap = "8px";
        row.style.fontSize = "13px";
        row.style.cursor = "pointer";
        row.innerHTML = `<input type="checkbox" class="ss-check" id="${id}" value="${ss.id}"> <span>${(ss.code || "·") + " — " + (ss.title || "")}</span>`;
        wrap.appendChild(row);
      });
      h.appendChild(wrap);
      box.appendChild(h);
    });
  }

  function resetNewProcessModal() {
    setModalUiAddMode();
    const users = readUsersPickJson();
    fillUserSelect(document.getElementById("surec-lider-source"), users);
    fillUserSelect(document.getElementById("surec-uye-source"), users);
    const ls = document.getElementById("surec-lider-selected");
    const us = document.getElementById("surec-uye-selected");
    if (ls) ls.innerHTML = "";
    if (us) us.innerHTML = "";

    const setVal = (id, v) => {
      const el = document.getElementById(id);
      if (el) el.value = v;
    };
    setVal("surec-name", "");
    setVal("surec-code", "");
    setVal("surec-status", "Aktif");
    setVal("surec-doc-no", "");
    setVal("surec-rev-no", "");
    setVal("surec-revision-date", "");
    setVal("surec-first-publish-date", "");
    setVal("surec-parent-id", "");
    setVal("surec-start-boundary", "");
    setVal("surec-end-boundary", "");
    setVal("surec-description", "");
  }

  function openAddModal() {
    if (!CAN_CRUD_PROCESS) return;
    resetNewProcessModal();
    populateSubStrategyPicker();
    const modal = document.getElementById("modal-surec-add");
    if (modal) modal.style.display = "flex";
  }

  function canOpenProcessEdit(triggerEl) {
    if (CAN_CRUD_PROCESS) return true;
    return !!(triggerEl && triggerEl.dataset && triggerEl.dataset.processEditable === "true");
  }

  async function openEditModal(processId, triggerEl) {
    if (!canOpenProcessEdit(triggerEl) || !GET_URL_BASE) return;
    const id = parseInt(processId, 10);
    if (Number.isNaN(id)) return;
    try {
      const res = await fetch(`${GET_URL_BASE}${id}`);
      const data = await res.json();
      if (!data.success) throw new Error(data.message || "Süreç bilgisi alınamadı.");
      const p = data.process;
      setModalUiEditMode();
      const hid = document.getElementById("surec-edit-id");
      if (hid) hid.value = String(id);

      populateSubStrategyPicker();
      const linkIds = (p.sub_strategy_links || []).map((l) => Number(l.sub_strategy_id));
      document.querySelectorAll("#modal-surec-add .ss-check").forEach((cb) => {
        cb.checked = linkIds.includes(parseInt(cb.value, 10));
      });

      const users = readUsersPickJson();
      fillDualFromSelection(users, p.leader_ids || [], "surec-lider-source", "surec-lider-selected");
      fillDualFromSelection(users, p.member_ids || [], "surec-uye-source", "surec-uye-selected");

      const setVal = (elId, v) => {
        const el = document.getElementById(elId);
        if (el) el.value = v != null && v !== undefined ? String(v) : "";
      };
      setVal("surec-name", p.name || "");
      setVal("surec-code", p.code || "");
      setVal("surec-status", p.status || "Aktif");
      setVal("surec-doc-no", p.document_no || "");
      setVal("surec-rev-no", p.revision_no || "");
      setVal("surec-revision-date", (p.revision_date || "").slice(0, 10));
      setVal("surec-first-publish-date", (p.first_publish_date || "").slice(0, 10));
      setVal("surec-parent-id", p.parent_id != null ? p.parent_id : "");
      setVal("surec-start-boundary", p.start_boundary || "");
      setVal("surec-end-boundary", p.end_boundary || "");
      setVal("surec-description", p.description || "");

      applyParentSelectSelfDisable(id);

      const modal = document.getElementById("modal-surec-add");
      if (modal) modal.style.display = "flex";
    } catch (err) {
      showError(err.message || "Süreç yüklenemedi.");
    }
  }

  function closeAddModal() {
    const modal = document.getElementById("modal-surec-add");
    if (modal) modal.style.display = "none";
  }

  function collectSelectedUserIds(selectId) {
    const sel = document.getElementById(selectId);
    if (!sel) return [];
    return [...sel.options].map((o) => parseInt(o.value, 10)).filter((n) => !Number.isNaN(n));
  }

  let processSaveInFlight = false;

  /** Sunucu tek adımda yanıt verdiği için yüzde kabaca simüle edilir; kullanıcıya geri bildirim verir. */
  function openProcessSaveProgressSwal() {
    let pct = 0;
    let progressTimer = null;
    Swal.fire({
      title: "Süreç kaydediliyor",
      html:
        '<p style="margin:0 0 10px;font-size:14px;color:#64748b;line-height:1.45;">İstek sunucuya gönderiliyor. Tamamlanınca liste yenilenecek.</p>' +
        '<div style="height:10px;background:#e2e8f0;border-radius:6px;overflow:hidden;">' +
        '<div id="surec-save-progress-bar" style="height:100%;width:0%;background:linear-gradient(90deg,#6366f1,#8b5cf6);transition:width 0.2s ease-out;"></div></div>' +
        '<p id="surec-save-progress-pct" style="margin:12px 0 0;font-size:18px;font-weight:700;color:#334155;">0%</p>',
      allowOutsideClick: false,
      allowEscapeKey: false,
      showConfirmButton: false,
      didOpen: () => {
        progressTimer = window.setInterval(() => {
          pct = Math.min(88, pct + 3 + Math.random() * 9);
          const rounded = Math.round(pct);
          const bar = document.getElementById("surec-save-progress-bar");
          const lab = document.getElementById("surec-save-progress-pct");
          if (bar) bar.style.width = `${rounded}%`;
          if (lab) lab.textContent = `${rounded}%`;
        }, 120);
      },
      willClose: () => {
        if (progressTimer != null) {
          window.clearInterval(progressTimer);
          progressTimer = null;
        }
      },
    });
    return {
      stopTimer() {
        if (progressTimer != null) {
          window.clearInterval(progressTimer);
          progressTimer = null;
        }
      },
      async finishSuccess() {
        this.stopTimer();
        const bar = document.getElementById("surec-save-progress-bar");
        const lab = document.getElementById("surec-save-progress-pct");
        if (bar) bar.style.width = "100%";
        if (lab) lab.textContent = "100%";
        await new Promise((r) => setTimeout(r, 280));
        Swal.close();
      },
      finishError() {
        this.stopTimer();
        Swal.close();
      },
    };
  }

  async function saveProcessForm() {
    if (processSaveInFlight) return;

    const name = document.getElementById("surec-name")?.value.trim();
    if (!name) {
      showError("Süreç adı zorunludur.");
      return;
    }
    const checked = [...document.querySelectorAll("#modal-surec-add .ss-check:checked")].map((cb) =>
      parseInt(cb.value, 10)
    );
    if (!checked.length) {
      showError("En az bir alt strateji seçmelisiniz.");
      return;
    }
    const parentRaw = document.getElementById("surec-parent-id")?.value;
    const body = {
      name,
      code: document.getElementById("surec-code")?.value.trim() || null,
      description: document.getElementById("surec-description")?.value.trim() || null,
      document_no: document.getElementById("surec-doc-no")?.value.trim() || null,
      revision_no: document.getElementById("surec-rev-no")?.value.trim() || null,
      status: document.getElementById("surec-status")?.value || "Aktif",
      /* İlerleme modalda yok: yeni süreçte API 0; güncellemede progress gönderilmez → mevcut değer korunur */
      start_boundary: document.getElementById("surec-start-boundary")?.value.trim() || null,
      end_boundary: document.getElementById("surec-end-boundary")?.value.trim() || null,
      parent_id: parentRaw ? parseInt(parentRaw, 10) : null,
      leader_ids: collectSelectedUserIds("surec-lider-selected"),
      member_ids: collectSelectedUserIds("surec-uye-selected"),
      sub_strategy_links: checked.map((sid) => ({ sub_strategy_id: sid })),
    };
    const rd = document.getElementById("surec-revision-date")?.value;
    const fd = document.getElementById("surec-first-publish-date")?.value;
    if (rd) body.revision_date = rd;
    if (fd) body.first_publish_date = fd;

    const editId = document.getElementById("surec-edit-id")?.value.trim();
    const modalTitle = document.getElementById("modal-surec-title-text")?.textContent?.trim() || "";
    const looksLikeEditMode = modalTitle.indexOf("Düzenle") !== -1;
    if (!editId && !CAN_CRUD_PROCESS) {
      showError("Yeni süreç oluşturma yetkiniz yok.");
      return;
    }
    if (!editId && CAN_CRUD_PROCESS && looksLikeEditMode) {
      showError("Düzenleme oturumu eksik (süreç kimliği bulunamadı). Modalı kapatıp «Düzenle» ile yeniden açın.");
      return;
    }
    const saveBtn = document.getElementById("btn-surec-save");
    const progressUi = openProcessSaveProgressSwal();
    processSaveInFlight = true;
    if (saveBtn) saveBtn.disabled = true;

    try {
      let data;
      if (editId && UPDATE_URL_BASE) {
        data = await postJson(`${UPDATE_URL_BASE}${editId}`, body);
      } else {
        data = await postJson(ADD_URL, body);
      }

      if (data.success) {
        await progressUi.finishSuccess();
        closeAddModal();
        toastSuccess(editId ? "Süreç güncellendi." : "Süreç oluşturuldu.");
        setTimeout(() => location.reload(), 450);
      } else {
        progressUi.finishError();
        showError(data.message || (editId ? "Güncelleme başarısız." : "Kayıt başarısız."));
      }
    } catch (err) {
      progressUi.finishError();
      showError("Sunucu hatası: " + (err && err.message ? err.message : String(err)));
    } finally {
      processSaveInFlight = false;
      if (saveBtn) saveBtn.disabled = false;
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
  document.getElementById("modal-surec-close")?.addEventListener("click", closeAddModal);
  document.getElementById("modal-surec-cancel")?.addEventListener("click", closeAddModal);
  document.getElementById("modal-surec-add")?.addEventListener("click", (e) => {
    if (e.target.id === "modal-surec-add") closeAddModal();
  });
  document.getElementById("btn-surec-save")?.addEventListener("click", saveProcessForm);

  document.getElementById("btn-surec-lider-add")?.addEventListener("click", () => {
    transferMultiOptions("surec-lider-source", "surec-lider-selected");
  });
  document.getElementById("btn-surec-lider-remove")?.addEventListener("click", () => {
    transferMultiOptions("surec-lider-selected", "surec-lider-source");
  });
  document.getElementById("btn-surec-uye-add")?.addEventListener("click", () => {
    transferMultiOptions("surec-uye-source", "surec-uye-selected");
  });
  document.getElementById("btn-surec-uye-remove")?.addEventListener("click", () => {
    transferMultiOptions("surec-uye-selected", "surec-uye-source");
  });

  document.addEventListener("click", (e) => {
    const del = e.target.closest(".btn-surec-delete");
    if (del) {
      deleteSurec(del.dataset.surecId, del.dataset.surecName);
      return;
    }
    const ed = e.target.closest(".btn-surec-edit");
    if (ed && ed.dataset.surecId) {
      openEditModal(ed.dataset.surecId, ed);
    }
  });

})();
