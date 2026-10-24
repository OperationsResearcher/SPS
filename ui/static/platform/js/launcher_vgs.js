/**
 * launcher_vgs.js — Masaüstü launcher Yeni Veri Giriş Sihirbazı
 * Kaskad: plan yılı → yetkili süreçler → PG. Kayıt mevcut VGS API'leriyle.
 */
(function () {
  "use strict";

  const root = document.getElementById("lvgs-root");
  if (!root) return;

  const overlay = document.getElementById("lvgs-overlay");
  const openBtn = document.getElementById("lvgs-open");
  const yearSel = document.getElementById("lvgs-year");
  const procSel = document.getElementById("lvgs-process");
  const kpiSel = document.getElementById("lvgs-kpi");
  const dateEl = document.getElementById("lvgs-date");
  const valEl = document.getElementById("lvgs-value");
  const descEl = document.getElementById("lvgs-desc");
  const sealedHint = document.getElementById("lvgs-sealed-hint");
  const form = document.getElementById("lvgs-form");

  const CATALOG_URL = root.dataset.catalogUrl || "";
  const KPI_LIST_TPL = root.dataset.kpiListUrlTemplate || "";
  const KPI_ADD_URL = root.dataset.kpiDataAddUrl || "";
  const HISTORY_TPL = root.dataset.historyUrlTemplate || "";
  const ENSURE_URL = root.dataset.bireyselEnsureUrl || "";
  const BIREYSEL_ADD_URL = root.dataset.bireyselAddUrl || "";
  const KPI_PLACEHOLDER = String(root.dataset.kpiIdPlaceholder || "900000001");
  const DEFAULT_YEAR = parseInt(root.dataset.defaultYear, 10) || new Date().getFullYear();

  let yearsMeta = [];
  try {
    const el = document.getElementById("lvgs-years-json");
    yearsMeta = el ? JSON.parse(el.textContent || "[]") : [];
  } catch (_) {
    yearsMeta = [];
  }

  let kpisCache = [];
  let lastHistoryRows = [];
  let sealed = false;

  function getCsrf() {
    const el = document.querySelector('meta[name="csrf-token"]');
    return el ? el.getAttribute("content") : "";
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
    return res.json();
  }

  async function getJson(url) {
    const res = await fetch(url, { credentials: "same-origin", headers: { Accept: "application/json" } });
    return res.json();
  }

  function showError(msg) {
    const saved = overlay ? overlay.style.zIndex : "";
    if (overlay) overlay.style.zIndex = "1";
    Swal.fire({
      icon: "error",
      title: t("Hata"),
      text: msg,
      confirmButtonColor: "#dc2626",
    }).then(() => {
      if (overlay) overlay.style.zIndex = saved;
    });
  }

  function toastOk(msg) {
    Swal.fire({
      toast: true,
      position: "top-end",
      icon: "success",
      title: msg,
      showConfirmButton: false,
      timer: 2500,
    });
  }

  function expandKpi(tpl, id) {
    if (!tpl) return "";
    return tpl.split(KPI_PLACEHOLDER).join(String(id));
  }

  function fillSelect(sel, items, placeholder) {
    if (!sel) return;
    const opts = [`<option value="">${placeholder}</option>`];
    (items || []).forEach((it) => {
      opts.push(`<option value="${it.id}">${esc(it.label || it.name)}</option>`);
    });
    sel.innerHTML = opts.join("");
  }

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function selectedYear() {
    return parseInt(yearSel && yearSel.value, 10) || 0;
  }

  function constrainDate() {
    const y = selectedYear();
    if (!dateEl || !y) return;
    dateEl.min = `${y}-01-01`;
    dateEl.max = `${y}-12-31`;
    const today = new Date();
    const cy = today.getFullYear();
    const def = y === cy
      ? `${cy}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`
      : `${y}-12-31`;
    const cur = dateEl.value;
    if (!cur || cur.slice(0, 4) !== String(y)) dateEl.value = def;
  }

  function inferPeriodFamily(periodStr) {
    const s = (periodStr || "").toLowerCase();
    if (s.includes("yıll") || s.includes("yill")) return "yillik";
    if (s.includes("çeyrek") || s.includes("ceyrek")) return "ceyrek";
    if (s.includes("6") && s.includes("ay")) return "halfyear";
    if (s.includes("hafta")) return "haftalik";
    if (s.includes("günl") || s.includes("gunl")) return "gunluk";
    if (s.includes("ay")) return "aylik";
    return "ceyrek";
  }

  function parseIsoDate(s) {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(s || "").trim());
    if (!m) return null;
    const y = parseInt(m[1], 10);
    const mon = parseInt(m[2], 10);
    const day = parseInt(m[3], 10);
    const d = new Date(y, mon - 1, day);
    if (d.getFullYear() !== y || d.getMonth() !== mon - 1 || d.getDate() !== day) return null;
    return { y, mon, day };
  }

  function derivePeriodFromEntryDate(dateStr, family) {
    const d = parseIsoDate(dateStr);
    if (!d) return null;
    const { y, mon, day } = d;
    let period_type;
    let period_no;
    let period_month = null;
    if (family === "yillik") {
      period_type = "yillik";
      period_no = 1;
    } else if (family === "ceyrek") {
      period_type = "ceyrek";
      period_no = Math.floor((mon - 1) / 3) + 1;
    } else if (family === "aylik") {
      period_type = "aylik";
      period_no = mon;
    } else if (family === "halfyear") {
      period_type = "halfyear";
      period_no = mon <= 6 ? 1 : 2;
    } else if (family === "haftalik") {
      period_type = "haftalik";
      period_month = mon;
      period_no = Math.min(5, Math.max(1, Math.ceil(day / 7)));
    } else if (family === "gunluk") {
      period_type = "gunluk";
      period_month = mon;
      period_no = day;
    } else {
      period_type = "ceyrek";
      period_no = Math.floor((mon - 1) / 3) + 1;
    }
    return { year: y, period_type, period_no, period_month, data_date: String(dateStr).trim() };
  }

  function apiPeriodFromVgs(periodType, periodNo) {
    const pt = (periodType || "").toLowerCase();
    if (pt === "halfyear") return { period_type: "ceyrek", period_no: periodNo === 2 ? 4 : 2 };
    return { period_type: pt, period_no: periodNo };
  }

  function selectedKpi() {
    const id = parseInt(kpiSel && kpiSel.value, 10);
    if (!id) return null;
    return kpisCache.find((k) => Number(k.id) === id) || { id: id, period: "Çeyreklik" };
  }

  async function loadProcesses() {
    const y = selectedYear();
    fillSelect(procSel, [], t("Süreç seçin"));
    fillSelect(kpiSel, [], t("Önce süreç seçin"));
    kpisCache = [];
    resetHistory();
    if (!y || !CATALOG_URL) return;
    const data = await getJson(`${CATALOG_URL}?year=${encodeURIComponent(y)}`);
    if (!data.success) {
      showError(data.message || t("Süreçler yüklenemedi."));
      return;
    }
    sealed = !!data.sealed;
    if (sealedHint) sealedHint.classList.toggle("is-hidden", !sealed);
    const saveBtn = document.getElementById("lvgs-save");
    if (saveBtn) saveBtn.disabled = sealed;
    fillSelect(procSel, data.processes || [], t("Süreç seçin"));
    constrainDate();
  }

  async function loadKpis() {
    const pid = parseInt(procSel && procSel.value, 10);
    const y = selectedYear();
    fillSelect(kpiSel, [], t("PG seçin"));
    kpisCache = [];
    resetHistory();
    if (!pid) return;
    let url = expandKpi(KPI_LIST_TPL, pid);
    if (y) url += (url.indexOf("?") >= 0 ? "&" : "?") + "year=" + encodeURIComponent(y);
    const data = await getJson(url);
    if (!data.success) {
      showError(data.message || t("PG listesi yüklenemedi."));
      return;
    }
    kpisCache = data.kpis || [];
    const items = kpisCache.map((k) => ({
      id: k.id,
      label: k.code ? `${k.code} — ${k.name}` : k.name,
    }));
    fillSelect(kpiSel, items, t("PG seçin"));
  }

  function fmtDt(iso) {
    if (window.formatLocalDateTime) return window.formatLocalDateTime(iso);
    if (!iso) return "—";
    const d = new Date(iso);
    return Number.isNaN(d.getTime()) ? String(iso) : d.toLocaleString("tr-TR");
  }

  function fmtD(iso) {
    if (window.formatLocalDate) return window.formatLocalDate(iso);
    if (!iso) return "—";
    const d = new Date(iso);
    return Number.isNaN(d.getTime()) ? String(iso) : d.toLocaleDateString("tr-TR");
  }

  function resetHistory() {
    lastHistoryRows = [];
    const wrap = document.getElementById("lvgs-history-table-wrap");
    const empty = document.getElementById("lvgs-history-empty");
    const err = document.getElementById("lvgs-history-error");
    const load = document.getElementById("lvgs-history-loading");
    if (wrap) wrap.innerHTML = "";
    empty && empty.classList.add("is-hidden");
    err && err.classList.add("is-hidden");
    load && load.classList.add("is-hidden");
  }

  function renderHistory(rows) {
    lastHistoryRows = rows || [];
    const wrap = document.getElementById("lvgs-history-table-wrap");
    const empty = document.getElementById("lvgs-history-empty");
    if (!wrap) return;
    if (!lastHistoryRows.length) {
      wrap.innerHTML = "";
      empty && empty.classList.remove("is-hidden");
      return;
    }
    empty && empty.classList.add("is-hidden");
    const body = lastHistoryRows
      .map((r) => {
        const status = r.is_active
          ? `<span class="vgs-history-badge vgs-history-badge--ok">${t("Aktif")}</span>`
          : `<span class="vgs-history-badge vgs-history-badge--off">${t("Silindi")}</span>`;
        return `<tr>
          <td>${esc(fmtD(r.data_date))}</td>
          <td>${esc(r.recorded_at ? fmtDt(r.recorded_at) : "—")}</td>
          <td>${esc(String(r.actual_value ?? ""))}</td>
          <td>${esc(r.entered_by_name || "—")}</td>
          <td>${status}</td>
        </tr>`;
      })
      .join("");
    wrap.innerHTML =
      `<table class="vgs-history-table"><thead><tr>` +
      `<th>${t("Veri tarihi")}</th><th>${t("Veri girişi")}</th><th>${t("Değer")}</th>` +
      `<th>${t("Giren")}</th><th>${t("Durum")}</th></tr></thead><tbody>${body}</tbody></table>`;
  }

  async function loadHistory() {
    const kpi = selectedKpi();
    const wrap = document.getElementById("lvgs-history-table-wrap");
    const load = document.getElementById("lvgs-history-loading");
    const err = document.getElementById("lvgs-history-error");
    const empty = document.getElementById("lvgs-history-empty");
    if (!kpi || !HISTORY_TPL) {
      resetHistory();
      return;
    }
    load && load.classList.remove("is-hidden");
    err && err.classList.add("is-hidden");
    empty && empty.classList.add("is-hidden");
    if (wrap) wrap.innerHTML = "";
    try {
      const data = await getJson(expandKpi(HISTORY_TPL, kpi.id));
      load && load.classList.add("is-hidden");
      if (!data.success) {
        if (err) {
          err.textContent = data.message || t("Geçmiş yüklenemedi.");
          err.classList.remove("is-hidden");
        }
        return;
      }
      renderHistory(data.data || []);
    } catch (e) {
      load && load.classList.add("is-hidden");
      if (err) {
        err.textContent = t("Geçmiş yüklenemedi.");
        err.classList.remove("is-hidden");
      }
    }
  }

  function openModal() {
    if (!overlay) return;
    fillYears();
    if (yearSel) yearSel.value = String(DEFAULT_YEAR);
    if (valEl) valEl.value = "";
    if (descEl) descEl.value = "";
    loadProcesses();
    if (overlay.parentElement !== document.body) document.body.appendChild(overlay);
    overlay.style.display = "flex";
    overlay.style.zIndex = "2147483000";
    overlay.classList.add("open");
    overlay.setAttribute("aria-hidden", "false");
  }

  function closeModal() {
    if (!overlay) return;
    overlay.classList.remove("open");
    overlay.setAttribute("aria-hidden", "true");
    overlay.style.display = "";
  }

  function fillYears() {
    if (!yearSel) return;
    const opts = yearsMeta.map((py) => {
      const y = py.year;
      const lock = py.sealed || py.muhurlu ? " 🔒" : "";
      const name = py.name ? ` — ${esc(py.name)}` : "";
      const sel = y === DEFAULT_YEAR ? " selected" : "";
      return `<option value="${y}"${sel}>${y}${name}${lock}</option>`;
    });
    yearSel.innerHTML = opts.join("") || `<option value="${DEFAULT_YEAR}">${DEFAULT_YEAR}</option>`;
  }

  async function onSave(e) {
    e.preventDefault();
    const kpi = selectedKpi();
    const rawDate = (dateEl && dateEl.value || "").trim();
    const val = (valEl && valEl.value || "").trim();
    if (!selectedYear()) {
      showError(t("Plan yılını seçin."));
      return;
    }
    if (!procSel || !procSel.value) {
      showError(t("Süreç seçin."));
      return;
    }
    if (!kpi) {
      showError(t("Performans göstergesi seçin."));
      return;
    }
    if (!parseIsoDate(rawDate)) {
      showError(t("Geçerli bir veri tarihi seçin."));
      return;
    }
    if (!val) {
      showError(t("Gerçekleşen değer zorunludur."));
      return;
    }
    const family = inferPeriodFamily(kpi.period);
    const p = derivePeriodFromEntryDate(rawDate, family);
    if (!p) {
      showError(t("Tarih işlenemedi."));
      return;
    }
    const apiP = apiPeriodFromVgs(p.period_type, p.period_no);
    const desc = (descEl && descEl.value || "").trim();
    const bodyKpi = {
      kpi_id: kpi.id,
      year: p.year,
      period_type: apiP.period_type,
      period_no: apiP.period_no,
      actual_value: val,
      data_date: p.data_date,
    };
    if (p.period_month != null) bodyKpi.period_month = p.period_month;
    if (desc) bodyKpi.description = desc;
    if (kpi.target_value) bodyKpi.target_value = String(kpi.target_value);

    const btn = document.getElementById("lvgs-save");
    if (btn) btn.disabled = true;
    try {
      let indivPgId = null;
      if (ENSURE_URL) {
        const ens = await postJson(ENSURE_URL, { process_kpi_id: kpi.id });
        if (!ens.success) {
          showError(ens.message || ens.mesaj || t("Bireysel PG eşlemesi oluşturulamadı."));
          return;
        }
        indivPgId = ens.id;
      }
      const data = await postJson(KPI_ADD_URL, bodyKpi);
      if (!data.success) {
        showError(data.message || data.mesaj || t("Süreç verisi kaydedilemedi."));
        return;
      }
      if (BIREYSEL_ADD_URL && indivPgId) {
        const bodyInd = {
          pg_id: indivPgId,
          year: p.year,
          period_type: apiP.period_type,
          period_no: apiP.period_no,
          actual_value: val,
          data_date: p.data_date,
        };
        if (p.period_month != null) bodyInd.period_month = p.period_month;
        if (desc) bodyInd.description = desc;
        const d2 = await postJson(BIREYSEL_ADD_URL, bodyInd);
        if (!d2.success) {
          showError(d2.message || d2.mesaj || t("Süreç verisi kaydedildi; bireysel karne kaydı başarısız."));
          await loadHistory();
          return;
        }
      }
      toastOk(t("Veri kaydedildi (süreç + bireysel)."));
      if (valEl) valEl.value = "";
      if (descEl) descEl.value = "";
      await loadHistory();
    } catch (err) {
      showError(t("Sunucu hatası:") + " " + (err && err.message ? err.message : String(err)));
    } finally {
      if (btn) btn.disabled = false;
    }
  }

  function fillYearsOnBoot() {
    fillYears();
  }

  fillYearsOnBoot();

  openBtn && openBtn.addEventListener("click", openModal);
  document.getElementById("lvgs-close")?.addEventListener("click", closeModal);
  document.getElementById("lvgs-cancel")?.addEventListener("click", closeModal);
  overlay && overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeModal();
  });
  yearSel && yearSel.addEventListener("change", () => loadProcesses());
  procSel && procSel.addEventListener("change", () => loadKpis());
  kpiSel && kpiSel.addEventListener("change", () => {
    const panel = document.getElementById("lvgs-history-panel");
    if (panel && !panel.classList.contains("is-collapsed")) loadHistory();
    else resetHistory();
  });
  form && form.addEventListener("submit", onSave);

  const histBtn = document.getElementById("lvgs-history-toggle");
  histBtn && histBtn.addEventListener("click", () => {
    const panel = document.getElementById("lvgs-history-panel");
    if (!panel) return;
    const open = panel.classList.contains("is-collapsed");
    panel.classList.toggle("is-collapsed", !open);
    histBtn.setAttribute("aria-expanded", open ? "true" : "false");
    histBtn.classList.toggle("is-open", open);
    if (open) loadHistory();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && overlay && overlay.classList.contains("open")) closeModal();
  });
})();
