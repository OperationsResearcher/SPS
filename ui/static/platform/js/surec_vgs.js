/**
 * surec_vgs.js — Süreç karnesi Veri Girişi Sihirbazı (VGS)
 * surec.js içinden IIFE ile sarılmış bağlamda çağrılır: initSurecVgs(ctx)
 * Periyot kullanıcıdan istenmez; kullanıcının seçtiği veri tarihine göre yıl ve periyot türetilir.
 */
(function (global) {
  "use strict";

  function initSurecVgs(ctx) {
    const {
      MONTHS,
      parsePeriodKeyForApi,
      escHtml,
      showError,
      toastSuccess,
      postJson,
      viewRoot,
      modalKpiDataEntry,
      formKpiDataEntry,
      getCanEnterPgv,
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
    } = ctx;

    function canEnterPgvNow() {
      if (typeof getCanEnterPgv === "function") return !!getCanEnterPgv();
      return !!ctx.canEnterPgv;
    }

    let vgsState = null;
    /** Son yüklenen geçmiş satırları (düzenleme için) */
    let lastHistoryRows = [];
    let historyEditUpdateUrl = "";
    let historyDeleteUrl = "";

    function lastDayOfMonthJs(y, m) {
      return new Date(y, m, 0).getDate();
    }

    function formatYmd(y, mon, day) {
      const mm = String(mon).padStart(2, "0");
      const dd = String(day).padStart(2, "0");
      return `${y}-${mm}-${dd}`;
    }

    function todayYmdLocal() {
      const n = new Date();
      return formatYmd(n.getFullYear(), n.getMonth() + 1, n.getDate());
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

    function computeVgsEndDateIso(year, periodType, periodNo, periodMonth) {
      const y = parseInt(year, 10);
      const pt = (periodType || "").toLowerCase();
      const pn = parseInt(periodNo, 10) || 1;
      const pm = periodMonth != null ? parseInt(periodMonth, 10) : null;
      if (pt === "yillik") return formatYmd(y, 12, 31);
      if (pt === "ceyrek") {
        const monthEnd = { 1: 3, 2: 6, 3: 9, 4: 12 }[pn] || 12;
        const ld = lastDayOfMonthJs(y, monthEnd);
        return formatYmd(y, monthEnd, ld);
      }
      if (pt === "aylik") {
        const m = Math.max(1, Math.min(12, pn));
        const ld = lastDayOfMonthJs(y, m);
        return formatYmd(y, m, ld);
      }
      if (pt === "halfyear") {
        if (pn === 1) return formatYmd(y, 6, 30);
        return formatYmd(y, 12, 31);
      }
      if (pt === "haftalik" && pm) {
        const ld = lastDayOfMonthJs(y, pm);
        const day = Math.min(Math.max(1, pn * 7), ld);
        return formatYmd(y, pm, day);
      }
      if (pt === "gunluk" && pm) {
        const ld = lastDayOfMonthJs(y, pm);
        const day = Math.min(Math.max(1, pn), ld);
        return formatYmd(y, pm, day);
      }
      return formatYmd(y, 12, 31);
    }

    function apiPeriodFromVgs(periodType, periodNo) {
      const pt = (periodType || "").toLowerCase();
      if (pt === "halfyear") {
        return { period_type: "ceyrek", period_no: periodNo === 2 ? 4 : 2 };
      }
      return { period_type: pt, period_no: periodNo };
    }

    function parseIsoDate(s) {
      const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(s || "").trim());
      if (!m) return null;
      const y = parseInt(m[1], 10);
      const mon = parseInt(m[2], 10);
      const day = parseInt(m[3], 10);
      if (mon < 1 || mon > 12 || day < 1 || day > 31) return null;
      const d = new Date(y, mon - 1, day);
      if (d.getFullYear() !== y || d.getMonth() !== mon - 1 || d.getDate() !== day) return null;
      return { y, mon, day };
    }

    function derivePeriodFromEntryDate(dateStr, family) {
      const d = parseIsoDate(dateStr);
      if (!d) return null;
      const { y, mon, day } = d;
      const year = y;
      let period_type;
      let period_no;
      let period_month = null;
      let periodLabel;

      if (family === "yillik") {
        period_type = "yillik";
        period_no = 1;
        periodLabel = `${year} (yıllık)`;
      } else if (family === "ceyrek") {
        const q = Math.floor((mon - 1) / 3) + 1;
        period_type = "ceyrek";
        period_no = q;
        periodLabel = `${q}. çeyrek ${year}`;
      } else if (family === "aylik") {
        period_type = "aylik";
        period_no = mon;
        periodLabel = `${MONTHS[mon - 1] || "Ay " + mon} ${year}`;
      } else if (family === "halfyear") {
        period_type = "halfyear";
        period_no = mon <= 6 ? 1 : 2;
        periodLabel = period_no === 1 ? `1. yarıyıl ${year}` : `2. yarıyıl ${year}`;
      } else if (family === "haftalik") {
        period_type = "haftalik";
        period_month = mon;
        period_no = Math.min(5, Math.max(1, Math.ceil(day / 7)));
        periodLabel = `H${period_no} · ${MONTHS[mon - 1] || mon} ${year}`;
      } else if (family === "gunluk") {
        period_type = "gunluk";
        period_month = mon;
        period_no = day;
        periodLabel = `${day}.${String(mon).padStart(2, "0")}.${year}`;
      } else {
        const q = Math.floor((mon - 1) / 3) + 1;
        period_type = "ceyrek";
        period_no = q;
        periodLabel = `${q}. çeyrek ${year}`;
      }
      return {
        year,
        period_type,
        period_no,
        period_month,
        periodLabel,
        data_date: String(dateStr).trim(),
      };
    }

    function validateVgsEntryDate() {
      const raw = (document.getElementById("vgs-data-date")?.value || "").trim();
      if (!raw) {
        showError("Veri tarihini seçin.");
        document.getElementById("vgs-data-date")?.focus();
        return false;
      }
      if (!parseIsoDate(raw)) {
        showError("Geçerli bir tarih seçin.");
        document.getElementById("vgs-data-date")?.focus();
        return false;
      }
      const p = derivePeriodFromEntryDate(raw, vgsState.periodFamily);
      if (!p) {
        showError("Tarih işlenemedi.");
        return false;
      }
      return true;
    }

    function validateVgsValue() {
      const valEl = document.getElementById("kpi-data-entry-value");
      const raw = valEl ? valEl.value.trim() : "";
      if (!raw) {
        showError("Gerçekleşen değer zorunludur.");
        valEl?.focus();
        return false;
      }
      return true;
    }

    function validateVgsForm() {
      return validateVgsEntryDate() && validateVgsValue();
    }

    // ── Kayıt geçmişi (accordion) ───────────────────────────────────────────

    function resetHistoryAccordion() {
      const btn = document.getElementById("vgs-history-toggle");
      const panel = document.getElementById("vgs-history-panel");
      const wrap = document.getElementById("vgs-history-table-wrap");
      const err = document.getElementById("vgs-history-error");
      const empty = document.getElementById("vgs-history-empty");
      const load = document.getElementById("vgs-history-loading");
      if (btn) {
        btn.setAttribute("aria-expanded", "false");
        btn.classList.remove("is-open");
      }
      if (panel) panel.classList.add("is-collapsed");
      if (wrap) wrap.innerHTML = "";
      if (err) {
        err.textContent = "";
        err.classList.add("is-hidden");
      }
      if (empty) empty.classList.add("is-hidden");
      if (load) load.classList.add("is-hidden");
      lastHistoryRows = [];
    }

    function formatTrDate(isoOrDateStr) {
      if (!isoOrDateStr) return "—";
      try {
        const d = new Date(isoOrDateStr);
        if (Number.isNaN(d.getTime())) return String(isoOrDateStr);
        return d.toLocaleDateString("tr-TR", { day: "2-digit", month: "2-digit", year: "numeric" });
      } catch (_) {
        return String(isoOrDateStr);
      }
    }

    function formatTrDateTime(isoStr) {
      if (!isoStr) return "—";
      try {
        const d = new Date(isoStr);
        if (Number.isNaN(d.getTime())) return String(isoStr);
        return d.toLocaleString("tr-TR", {
          day: "2-digit",
          month: "2-digit",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        });
      } catch (_) {
        return String(isoStr);
      }
    }

    function renderVgsHistory(rows) {
      lastHistoryRows = rows || [];
      const wrap = document.getElementById("vgs-history-table-wrap");
      const empty = document.getElementById("vgs-history-empty");
      if (!wrap) return;
      if (!lastHistoryRows.length) {
        wrap.innerHTML = "";
        empty?.classList.remove("is-hidden");
        return;
      }
      empty?.classList.add("is-hidden");
      const head =
        "<thead><tr>" +
        "<th>Veri tarihi</th><th>Veri girişi</th><th>Değer</th><th>Giren</th>" +
        "<th>Son güncelleme</th><th>Durum</th><th>Silinme bilgisi</th><th class=\"vgs-history-actions\">İşlem</th>" +
        "</tr></thead>";
      const body =
        "<tbody>" +
        lastHistoryRows
          .map((r) => {
            const status = r.is_active
              ? '<span class="vgs-history-badge vgs-history-badge--ok">Aktif</span>'
              : '<span class="vgs-history-badge vgs-history-badge--off">Silindi</span>';
            const delLine =
              !r.is_active && r.deleted_at
                ? `${escHtml(formatTrDateTime(r.deleted_at))} — ${escHtml(r.deleted_by_name || "—")}`
                : "—";
            const updLine = r.last_updated_at
              ? `${escHtml(formatTrDateTime(r.last_updated_at))} — ${escHtml(r.last_updated_by_name || "—")}`
              : "—";
            let actions = "";
            if (r.can_edit) {
              actions += `<button type="button" class="mc-btn mc-btn-secondary mc-btn-sm vgs-history-edit" data-row-id="${r.id}">Düzenle</button> `;
            }
            if (r.can_delete) {
              actions += `<button type="button" class="mc-btn mc-btn-secondary mc-btn-sm vgs-history-del" data-row-id="${r.id}">Sil</button>`;
            }
            if (!actions) actions = "—";
            const entryLine = r.recorded_at
              ? escHtml(formatTrDateTime(r.recorded_at))
              : "—";
            return `<tr class="${r.is_active ? "" : "vgs-history-row--deleted"}">
            <td>${escHtml(formatTrDate(r.data_date))}</td>
            <td class="vgs-history-entrycell">${entryLine}</td>
            <td>${escHtml(String(r.actual_value ?? ""))}</td>
            <td>${escHtml(r.entered_by_name || "—")}</td>
            <td class="vgs-history-updcell">${updLine}</td>
            <td>${status}</td>
            <td class="vgs-history-delcell">${delLine}</td>
            <td class="vgs-history-actions">${actions}</td>
          </tr>`;
          })
          .join("") +
        "</tbody>";
      wrap.innerHTML = `<table class="vgs-history-table">${head}${body}</table>`;
    }

    async function loadVgsHistory() {
      if (!vgsState || !KPI_DATA_HISTORY_URL_TEMPLATE || typeof expandKpiUrl !== "function") return;
      const url = expandKpiUrl(KPI_DATA_HISTORY_URL_TEMPLATE, vgsState.kpiId);
      if (!url) return;
      const load = document.getElementById("vgs-history-loading");
      const errEl = document.getElementById("vgs-history-error");
      const empty = document.getElementById("vgs-history-empty");
      if (load) load.classList.remove("is-hidden");
      if (errEl) {
        errEl.classList.add("is-hidden");
        errEl.textContent = "";
      }
      if (empty) empty.classList.add("is-hidden");
      try {
        const res = await fetch(url, {
          credentials: "same-origin",
          headers: { Accept: "application/json" },
        });
        const data = await res.json();
        if (!res.ok || !data.success) {
          throw new Error(data.message || `HTTP ${res.status}`);
        }
        renderVgsHistory(data.data || []);
      } catch (e) {
        if (errEl) {
          errEl.textContent = "Geçmiş yüklenemedi: " + (e.message || String(e));
          errEl.classList.remove("is-hidden");
        }
        renderVgsHistory([]);
      } finally {
        if (load) load.classList.add("is-hidden");
      }
    }

    function onHistoryToggleClick() {
      const btn = document.getElementById("vgs-history-toggle");
      const panel = document.getElementById("vgs-history-panel");
      if (!btn || !panel) return;
      const open = btn.getAttribute("aria-expanded") === "true";
      if (open) {
        btn.setAttribute("aria-expanded", "false");
        btn.classList.remove("is-open");
        panel.classList.add("is-collapsed");
      } else {
        btn.setAttribute("aria-expanded", "true");
        btn.classList.add("is-open");
        panel.classList.remove("is-collapsed");
        loadVgsHistory();
      }
    }

    const modalHistoryEdit = document.getElementById("modal-vgs-history-edit");
    const modalHistoryDelete = document.getElementById("modal-vgs-history-delete");

    function closeHistoryEditModal() {
      historyEditUpdateUrl = "";
      if (!modalHistoryEdit) return;
      modalHistoryEdit.classList.remove("open");
      modalHistoryEdit.setAttribute("aria-hidden", "true");
    }

    function closeHistoryDeleteModal() {
      historyDeleteUrl = "";
      if (!modalHistoryDelete) return;
      modalHistoryDelete.classList.remove("open");
      modalHistoryDelete.setAttribute("aria-hidden", "true");
    }

    function closeVgsHistoryNestedModals() {
      closeHistoryEditModal();
      closeHistoryDeleteModal();
    }

    function openHistoryEditModal(row) {
      const u = expandKpiDataRowUrl(KPI_DATA_UPDATE_URL_TEMPLATE, row.id);
      if (!u || !modalHistoryEdit) {
        showError("Güncelleme penceresi veya adres yüklenemedi.");
        return;
      }
      historyEditUpdateUrl = u;
      const meta = document.getElementById("vgs-history-edit-meta");
      if (meta) {
        const entryTs = row.recorded_at ? formatTrDateTime(row.recorded_at) : "—";
        meta.textContent = `Veri tarihi: ${formatTrDate(row.data_date)} · Veri girişi: ${entryTs} · Giren: ${row.entered_by_name || "—"}`;
      }
      const av = document.getElementById("vgs-history-edit-actual");
      const dc = document.getElementById("vgs-history-edit-desc");
      if (av) av.value = row.actual_value != null ? String(row.actual_value) : "";
      if (dc) dc.value = row.description != null ? String(row.description) : "";
      modalHistoryEdit.classList.add("open");
      modalHistoryEdit.setAttribute("aria-hidden", "false");
      setTimeout(() => av?.focus(), 50);
    }

    function openHistoryDeleteModal(rowId) {
      const row = lastHistoryRows.find((x) => Number(x.id) === Number(rowId));
      const u = expandKpiDataRowUrl(KPI_DATA_DELETE_URL_TEMPLATE, rowId);
      if (!u || !modalHistoryDelete) {
        showError("Silme penceresi veya adres yüklenemedi.");
        return;
      }
      historyDeleteUrl = u;
      const meta = document.getElementById("vgs-history-delete-meta");
      if (meta && row) {
        const entryTs = row.recorded_at ? formatTrDateTime(row.recorded_at) : "—";
        meta.textContent = `Veri tarihi: ${formatTrDate(row.data_date)} · Veri girişi: ${entryTs} · Değer: ${row.actual_value ?? "—"} · Giren: ${row.entered_by_name || "—"}`;
      } else if (meta) meta.textContent = "";
      modalHistoryDelete.classList.add("open");
      modalHistoryDelete.setAttribute("aria-hidden", "false");
    }

    async function submitHistoryEdit() {
      const avEl = document.getElementById("vgs-history-edit-actual");
      const av = avEl ? avEl.value.trim() : "";
      if (!av) {
        showError("Gerçekleşen değer zorunludur.");
        avEl?.focus();
        return;
      }
      if (!historyEditUpdateUrl) return;
      const desc = (document.getElementById("vgs-history-edit-desc")?.value || "").trim();
      const btn = document.getElementById("btn-vgs-history-edit-save");
      if (btn) btn.disabled = true;
      try {
        const out = await postJson(historyEditUpdateUrl, {
          actual_value: av,
          description: desc,
        });
        if (!out.success) {
          showError(out.message || "Güncellenemedi.");
          return;
        }
        closeHistoryEditModal();
        toastSuccess("Kayıt güncellendi.");
        await loadVgsHistory();
        loadKarne();
      } catch (err) {
        showError(err.message || "Sunucu hatası.");
      } finally {
        if (btn) btn.disabled = false;
      }
    }

    async function submitHistoryDelete() {
      if (!historyDeleteUrl) return;
      const btn = document.getElementById("btn-vgs-history-delete-confirm");
      if (btn) btn.disabled = true;
      try {
        const out = await postJson(historyDeleteUrl, {});
        if (!out.success) {
          showError(out.message || "Silinemedi.");
          return;
        }
        closeHistoryDeleteModal();
        toastSuccess("Kayıt pasifleştirildi.");
        await loadVgsHistory();
        loadKarne();
      } catch (err) {
        showError(err.message || "Sunucu hatası.");
      } finally {
        if (btn) btn.disabled = false;
      }
    }

    function openEditHistoryRow(rowId) {
      const row = lastHistoryRows.find((x) => Number(x.id) === Number(rowId));
      if (!row) {
        showError("Düzenlenecek satır bulunamadı.");
        return;
      }
      openHistoryEditModal(row);
    }

    function confirmDeleteHistoryRow(rowId) {
      openHistoryDeleteModal(rowId);
    }

    function onHistoryTableClick(e) {
      const ed = e.target.closest(".vgs-history-edit");
      if (ed && ed.dataset.rowId) {
        e.preventDefault();
        openEditHistoryRow(ed.dataset.rowId);
        return;
      }
      const del = e.target.closest(".vgs-history-del");
      if (del && del.dataset.rowId) {
        e.preventDefault();
        confirmDeleteHistoryRow(del.dataset.rowId);
      }
    }

    // ── Modal ────────────────────────────────────────────────────────────────

    function closeKpiDataEntryModal() {
      closeVgsHistoryNestedModals();
      if (!modalKpiDataEntry) return;
      modalKpiDataEntry.classList.remove("open");
      modalKpiDataEntry.setAttribute("aria-hidden", "true");
      modalKpiDataEntry.style.display = "";
      modalKpiDataEntry.style.zIndex = "";
      vgsState = null;
      if (formKpiDataEntry) formKpiDataEntry.reset();
      resetHistoryAccordion();
    }

    function syncVgsSelectedKpi(selectedId) {
      if (!vgsState) return false;
      const allKpis = cachedKpisRef.kpis || [];
      const k = allKpis.find((x) => String(x.id) === String(selectedId));
      if (!k) return false;
      vgsState.kpiId = String(k.id);
      vgsState.kpiName = k.name || "PG";
      vgsState.kpiCode = k.code || "";
      vgsState.kpiPeriod = k.period || "";
      vgsState.kpiTarget = k.target_value != null ? String(k.target_value) : "";
      vgsState.periodFamily = inferPeriodFamily(k.period);
      return true;
    }

    function renderVgsKpiSelect(selectedId) {
      const sel = document.getElementById("vgs-kpi-select");
      if (!sel) return;
      const allKpis = cachedKpisRef.kpis || [];
      const opts = allKpis.map((k) => {
        const code = String(k.code || "").trim();
        const name = String(k.name || `PG #${k.id}`).trim();
        const label = code ? `${code} - ${name}` : name;
        const selected = String(k.id) === String(selectedId) ? " selected" : "";
        return `<option value="${String(k.id)}"${selected}>${escHtml(label)}</option>`;
      });
      sel.innerHTML = opts.join("");
      if (!sel.value && allKpis.length) sel.value = String(allKpis[0].id);
    }

    function openDataEntryModal(kpiId, year, opts) {
      if (!canEnterPgvNow()) {
        showError("PG verisi girme yetkiniz yok.");
        return;
      }
      if (!modalKpiDataEntry || !formKpiDataEntry) {
        showError("Veri girişi penceresi yüklenemedi.");
        return;
      }
      const kpis = cachedKpisRef.kpis || [];
      const k = kpis.find((x) => String(x.id) === String(kpiId)) || (kpis.length ? kpis[0] : null);
      if (!k) {
        showError("PG bulunamadı; sayfayı yenileyin.");
        return;
      }
      const procName = viewRoot.dataset.processName || "Süreç";
      const family = inferPeriodFamily(k.period);
      const yearNum = parseInt(String(year), 10) || new Date().getFullYear();
      resetHistoryAccordion();
      vgsState = {
        kpiId: String(k.id),
        processId: String(viewRoot.dataset.processId || ""),
        processName: procName,
        kpiName: k.name || "PG",
        kpiCode: k.code || "",
        kpiPeriod: k.period || "",
        kpiTarget: k.target_value != null ? String(k.target_value) : "",
        periodFamily: family,
      };
      formKpiDataEntry.reset();
      const descEl = document.getElementById("vgs-description");
      if (descEl) descEl.value = "";
      const valEl = document.getElementById("kpi-data-entry-value");
      if (valEl) valEl.value = "";

      let presetYmd = todayYmdLocal();
      if (opts && opts.periodKey) {
        const parsed = parsePeriodKeyForApi(String(opts.periodKey));
        if (parsed) {
          presetYmd = computeVgsEndDateIso(
            yearNum,
            parsed.period_type,
            parsed.period_no,
            parsed.period_month
          );
        }
      }
      const dEl = document.getElementById("vgs-data-date");
      if (dEl) dEl.value = presetYmd;

      const pl = document.getElementById("vgs-process-label");
      if (pl) pl.textContent = procName;
      renderVgsKpiSelect(String(k.id));

      const keepTableModalOpen = !!(opts && opts.keepTableModalOpen);
      if (!keepTableModalOpen) {
        const microPgModal = document.getElementById("modal-micro-pg-tablo");
        if (microPgModal && microPgModal.classList.contains("open")) {
          microPgModal.classList.remove("open");
          microPgModal.setAttribute("aria-hidden", "true");
        }
      }

      // Overlay'i body sonuna taşı: parent stacking context etkilerinden bağımsız olsun.
      if (modalKpiDataEntry.parentElement !== document.body) {
        document.body.appendChild(modalKpiDataEntry);
      }

      // Farklı tema/css kombinasyonlarında daima üstte görünmesi için zorla.
      modalKpiDataEntry.style.display = "flex";
      modalKpiDataEntry.style.zIndex = "2147483000";
      modalKpiDataEntry.classList.add("open");
      modalKpiDataEntry.setAttribute("aria-hidden", "false");
      document.getElementById("kpi-data-entry-value")?.focus();
    }

    function attachPeriodMonthIfNeeded(body, p) {
      if (p.period_month != null && !Number.isNaN(p.period_month)) {
        body.period_month = p.period_month;
      }
    }

    async function onVgsSave() {
      if (!vgsState || !KPI_DATA_ADD_URL) return;
      if (!validateVgsForm()) return;

      const rawDate = (document.getElementById("vgs-data-date")?.value || "").trim();
      const p = derivePeriodFromEntryDate(rawDate, vgsState.periodFamily);
      if (!p) {
        showError("Tarih işlenemedi.");
        return;
      }

      const val = (document.getElementById("kpi-data-entry-value")?.value || "").trim();
      const desc = (document.getElementById("vgs-description")?.value || "").trim();
      const endIso = p.data_date;
      const apiP = apiPeriodFromVgs(p.period_type, p.period_no);
      const bodyKpi = {
        kpi_id: parseInt(vgsState.kpiId, 10),
        year: p.year,
        period_type: apiP.period_type,
        period_no: apiP.period_no,
        actual_value: val,
        data_date: endIso,
      };
      attachPeriodMonthIfNeeded(bodyKpi, p);
      if (desc) bodyKpi.description = desc;
      if (vgsState.kpiTarget && String(vgsState.kpiTarget).trim())
        bodyKpi.target_value = String(vgsState.kpiTarget).trim();

      const btn = document.getElementById("btn-vgs-confirm");
      if (btn) btn.disabled = true;
      try {
        let indivPgId = null;
        if (BIREYSEL_ENSURE_PG_URL) {
          const ens = await postJson(BIREYSEL_ENSURE_PG_URL, {
            process_kpi_id: parseInt(vgsState.kpiId, 10),
          });
          if (!ens.success) {
            showError(ens.message || "Bireysel PG eşlemesi oluşturulamadı.");
            return;
          }
          indivPgId = ens.id;
        }

        const data = await postJson(KPI_DATA_ADD_URL, bodyKpi);
        if (!data.success) {
          showError(data.message || "Süreç verisi kaydedilemedi.");
          return;
        }

        if (BIREYSEL_VERI_ADD_URL && indivPgId) {
          const bodyInd = {
            pg_id: indivPgId,
            year: p.year,
            period_type: apiP.period_type,
            period_no: apiP.period_no,
            actual_value: val,
            data_date: endIso,
          };
          attachPeriodMonthIfNeeded(bodyInd, p);
          if (desc) bodyInd.description = desc;
          if (vgsState.kpiTarget && String(vgsState.kpiTarget).trim())
            bodyInd.target_value = String(vgsState.kpiTarget).trim();
          const d2 = await postJson(BIREYSEL_VERI_ADD_URL, bodyInd);
          if (!d2.success) {
            showError(
              d2.message ||
                "Süreç verisi kaydedildi; bireysel karne kaydı başarısız. Bireysel modülünü kontrol edin."
            );
            closeKpiDataEntryModal();
            loadKarne();
            return;
          }
        }

        closeKpiDataEntryModal();
        toastSuccess("Veri kaydedildi (süreç + bireysel).");
        loadKarne();
      } catch (err) {
        showError("Sunucu hatası: " + (err && err.message ? err.message : String(err)));
      } finally {
        if (btn) btn.disabled = false;
      }
    }

    formKpiDataEntry?.addEventListener("submit", (e) => {
      e.preventDefault();
      onVgsSave();
    });

    document.getElementById("vgs-kpi-select")?.addEventListener("change", (e) => {
      const nextId = String(e.target?.value || "").trim();
      if (!nextId) return;
      if (!syncVgsSelectedKpi(nextId)) {
        showError("Seçilen PG bulunamadı.");
        return;
      }
      resetHistoryAccordion();
    });

    document.getElementById("vgs-history-toggle")?.addEventListener("click", onHistoryToggleClick);
    document.getElementById("vgs-history-table-wrap")?.addEventListener("click", onHistoryTableClick);

    document.getElementById("btn-vgs-history-edit-close")?.addEventListener("click", closeHistoryEditModal);
    document.getElementById("btn-vgs-history-edit-cancel")?.addEventListener("click", closeHistoryEditModal);
    document.getElementById("btn-vgs-history-edit-save")?.addEventListener("click", () => submitHistoryEdit());
    modalHistoryEdit?.addEventListener("click", (e) => {
      if (e.target === modalHistoryEdit) closeHistoryEditModal();
    });

    document.getElementById("btn-vgs-history-delete-close")?.addEventListener("click", closeHistoryDeleteModal);
    document.getElementById("btn-vgs-history-delete-cancel")?.addEventListener("click", closeHistoryDeleteModal);
    document.getElementById("btn-vgs-history-delete-confirm")?.addEventListener("click", () => submitHistoryDelete());
    modalHistoryDelete?.addEventListener("click", (e) => {
      if (e.target === modalHistoryDelete) closeHistoryDeleteModal();
    });

    return { openDataEntryModal, closeKpiDataEntryModal, closeVgsHistoryNestedModals };
  }

  global.initSurecVgs = initSurecVgs;
})(typeof window !== "undefined" ? window : globalThis);
