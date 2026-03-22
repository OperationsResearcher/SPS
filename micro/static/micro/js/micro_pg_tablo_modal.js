/**
 * micro_pg_tablo_modal.js — Kök karne «Performans Göstergeleri» tablosunun Micro modal kopyası.
 * Endpoint'ler Micro URL'leri; kök process_karne.js mantığına uyumlu.
 */
(function (global) {
  "use strict";

  function coerceBasariAralikStr(v) {
    if (v == null) return null;
    if (typeof v === "object" && !Array.isArray(v)) {
      const r = v.aralik ?? v.range;
      if (r == null || String(r).trim() === "") return null;
      return String(r).trim();
    }
    const s = String(v).trim();
    return s || null;
  }

  function hesaplaBasariPuani(pct, araliklar) {
    if (!araliklar || typeof araliklar !== "object") return null;
    for (let puan = 1; puan <= 5; puan++) {
      const raw = araliklar[puan] || araliklar[String(puan)];
      const aralik = coerceBasariAralikStr(raw);
      if (!aralik) continue;
      const parts = aralik.split("-");
      const min = parseFloat(parts[0]) || 0;
      const max = parts[1] !== undefined ? parseFloat(parts[1]) : Infinity;
      if (pct >= min && pct <= max) return puan;
    }
    return null;
  }

  function _normPeriyot(s) {
    return (s || "")
      .toLowerCase()
      .replace(/ı/g, "i")
      .replace(/ü/g, "u")
      .replace(/ö/g, "o")
      .replace(/ç/g, "c")
      .replace(/ğ/g, "g")
      .trim();
  }

  function computeYillikHedef(targetValue, olcumPeriyodu, hesaplamaYontemi) {
    const tv = parseFloat(targetValue);
    if (Number.isNaN(tv) || tv <= 0) return null;
    if (hesaplamaYontemi !== "Toplama" && hesaplamaYontemi !== "Toplam") return tv;
    const olcumCarpan = { yillik: 1, ceyrek: 4, ceyreklik: 4, aylik: 12, haftalik: 52, gunluk: 365 };
    const olcumNorm = _normPeriyot(olcumPeriyodu);
    const carpan =
      olcumCarpan[olcumNorm] ??
      (olcumNorm.includes("yil")
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

  function computeCellTarget(targetValue, olcumPeriyodu, hesaplamaYontemi, gosterimPeriyodu, _periodKey) {
    const tv = parseFloat(targetValue);
    if (Number.isNaN(tv) || tv <= 0) return null;
    if (hesaplamaYontemi === "Ortalama" || hesaplamaYontemi === "Son Değer" || !hesaplamaYontemi) return tv;
    if (hesaplamaYontemi !== "Toplama" && hesaplamaYontemi !== "Toplam") return tv;
    const yillikHedef = computeYillikHedef(targetValue, olcumPeriyodu, hesaplamaYontemi);
    if (yillikHedef === null) return null;
    const gosterimBolum = { yillik: 1, ceyrek: 4, aylik: 12, haftalik: 52, gunluk: 365, alti_ay: 2 };
    const bolum = gosterimBolum[gosterimPeriyodu] || 4;
    return Math.round((yillikHedef / bolum) * 1000) / 1000;
  }

  const AYLAR_TR_FULL = [
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

  function haftalikRangeLabelTr(year, month, week) {
    const y = parseInt(year, 10);
    const m = parseInt(month, 10);
    const w = parseInt(week, 10);
    if (!y || m < 1 || m > 12 || w < 1 || w > 5) return null;
    const lastDay = new Date(y, m, 0).getDate();
    const startD = (w - 1) * 7 + 1;
    if (startD > lastDay) return null;
    const endD = Math.min(w * 7, lastDay);
    const mn = AYLAR_TR_FULL[m - 1];
    if (startD === endD) return `${startD} ${mn}`;
    return `${startD} ${mn} – ${endD} ${mn}`;
  }

  function buildHaftalikPeriods(year) {
    const arr = [];
    for (let m = 1; m <= 12; m++) {
      for (let w = 1; w <= 5; w++) {
        const label = haftalikRangeLabelTr(year, m, w);
        if (!label) continue;
        arr.push({ key: `haftalik_${w}_${m}`, label });
      }
    }
    return arr;
  }

  const ALTI_AY_PERIODS = [
    { key: "halfyear_1", label: "Ocak – Haziran" },
    { key: "halfyear_2", label: "Temmuz – Aralık" },
  ];

  const PERIOD_CONFIG = {
    ceyrek: [
      { key: "ceyrek_1", label: "I. Çeyrek" },
      { key: "ceyrek_2", label: "II. Çeyrek" },
      { key: "ceyrek_3", label: "III. Çeyrek" },
      { key: "ceyrek_4", label: "IV. Çeyrek" },
    ],
    yillik: [{ key: "yillik_1", label: "Yıl Sonu" }],
    aylik: [
      { key: "aylik_1", label: "Ocak" },
      { key: "aylik_2", label: "Şubat" },
      { key: "aylik_3", label: "Mart" },
      { key: "aylik_4", label: "Nisan" },
      { key: "aylik_5", label: "Mayıs" },
      { key: "aylik_6", label: "Haziran" },
      { key: "aylik_7", label: "Temmuz" },
      { key: "aylik_8", label: "Ağustos" },
      { key: "aylik_9", label: "Eylül" },
      { key: "aylik_10", label: "Ekim" },
      { key: "aylik_11", label: "Kasım" },
      { key: "aylik_12", label: "Aralık" },
    ],
  };

  function initMicroPgTabloModal(ctx) {
    const {
      escHtml,
      showError,
      toastSuccess,
      postJson,
      karneApiUrl,
      kpiDetailUrl,
      kpiProjeUrl,
      expandKpiDataRowUrl,
      kpiDataUpdateTemplate,
      kpiDataDeleteTemplate,
      kpiDataRowPlaceholder,
      openAddKpiModal,
      onAfterMutation,
      canCrudPg,
    } = ctx;

    const overlay = document.getElementById("modal-micro-pg-tablo");
    const thead = document.getElementById("micro-performansTableHead");
    const tbody = document.getElementById("micro-performansTbody");
    const yilSel = document.getElementById("micro-pg-yil-select");
    const periyotSel = document.getElementById("micro-pg-periyot-select");
    const navLabel = document.getElementById("micro-pg-periyot-nav-label");
    const navSub = document.getElementById("micro-pg-periyot-nav-sub");
    const veriDetayOverlay = document.getElementById("modal-micro-veri-detay");
    const veriDetayContent = document.getElementById("micro-veri-detay-content");
    const veriDuzenleOverlay = document.getElementById("modal-micro-veri-duzenle");

    let currentPeriyot = "ceyrek";
    let currentOffset = 0;
    let gunlukViewYear = new Date().getFullYear();
    let gunlukViewMonth = new Date().getMonth() + 1;
    let highlightKpiId = null;
    let _veriDetayKpiId = null;
    let _veriDetayPeriodKey = "";

    function getBaseYearFromSelect() {
      const v = yilSel ? parseInt(yilSel.value, 10) : NaN;
      return Number.isNaN(v) ? new Date().getFullYear() : v;
    }

    function getViewedYear() {
      if (currentPeriyot === "gunluk") return gunlukViewYear;
      return getBaseYearFromSelect() + currentOffset;
    }

    function getViewedMonth() {
      if (currentPeriyot !== "gunluk") return null;
      return gunlukViewMonth;
    }

    function getPeriodsForPeriyot() {
      const viewedYear = getViewedYear();
      if (currentPeriyot === "gunluk") {
        const viewedMonth = gunlukViewMonth;
        const lastDay = new Date(viewedYear, viewedMonth, 0).getDate();
        const arr = [];
        for (let d = 1; d <= lastDay; d++) {
          arr.push({ key: `gunluk_${d}_${viewedMonth}`, label: String(d), isDay: true });
        }
        return arr;
      }
      if (currentPeriyot === "yillik") return [{ key: "yillik_1", label: "Yıl Sonu" }];
      if (currentPeriyot === "ceyrek") return PERIOD_CONFIG.ceyrek;
      if (currentPeriyot === "aylik") return PERIOD_CONFIG.aylik;
      if (currentPeriyot === "alti_ay") return ALTI_AY_PERIODS;
      if (currentPeriyot === "haftalik") return buildHaftalikPeriods(viewedYear);
      return PERIOD_CONFIG.ceyrek;
    }

    function updatePeriyotLabel() {
      if (!navLabel) return;
      const names = {
        ceyrek: "Çeyreklik",
        yillik: "Yıllık",
        aylik: "Aylık",
        haftalik: "Haftalık",
        gunluk: "Günlük",
        alti_ay: "6 aylık",
      };
      const y = getViewedYear();
      if (currentPeriyot === "gunluk") {
        navLabel.textContent = `${gunlukViewYear} — ${AYLAR_TR_FULL[gunlukViewMonth - 1]} — Günlük`;
      } else {
        navLabel.textContent = `${y} — ${names[currentPeriyot] || currentPeriyot} görünümü`;
      }
      if (navSub) {
        let sub = "—";
        if (typeof globalThis.kokpitimKarneBadgeDetail === "function") {
          const gm = currentPeriyot === "gunluk" ? gunlukViewMonth : undefined;
          sub = globalThis.kokpitimKarneBadgeDetail(String(y), currentPeriyot, gm);
        }
        navSub.textContent = sub;
      }
    }

    function applyColumnVisibility() {
      const mapping = [
        { id: "micro-col-code-chk", selector: ".col-code" },
        { id: "micro-col-strategy-chk", selector: ".col-strategy" },
        { id: "micro-col-weight-chk", selector: ".col-weight" },
        { id: "micro-col-unit-chk", selector: ".col-unit" },
        { id: "micro-col-period-chk", selector: ".col-period" },
        { id: "micro-col-target-chk", selector: ".col-target-main" },
      ];
      mapping.forEach(({ id, selector }) => {
        const chk = document.getElementById(id);
        if (!chk) return;
        const show = chk.checked;
        document.querySelectorAll("#micro-performansTable " + selector).forEach((el) => {
          el.style.display = show ? "" : "none";
        });
      });
    }

    function rebuildPGTableByPeriyot(kpis, favoriteKpiIds) {
      if (!thead || !tbody) return;
      const favSet = new Set(favoriteKpiIds || []);
      const periods = getPeriodsForPeriyot();
      const isGunluk = currentPeriyot === "gunluk" && periods.length > 0 && periods[0].isDay;
      const aylar = [
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
      const monthName = isGunluk ? aylar[(getViewedMonth() || 1) - 1] : "";

      if (isGunluk) {
        let row1 =
          '<tr><th rowspan="2" class="col-code">Kodu</th><th rowspan="2" class="col-strategy">Ana Strateji</th><th rowspan="2" class="col-strategy">Alt Strateji</th><th rowspan="2">Performans Adı</th><th rowspan="2" class="col-weight">Ağırlık (%)</th><th rowspan="2" class="col-unit">Birim</th><th rowspan="2" class="col-period">Ölçüm Per.</th><th rowspan="2" class="col-target-main">Yıllık Hedef</th>';
        row1 += `<th colspan="${periods.length}" class="text-center">${escHtml(monthName)}</th>`;
        row1 +=
          '<th rowspan="2" class="col-target">Başarı Puanı</th><th rowspan="2" class="col-actions no-print">İşlemler</th></tr><tr>';
        periods.forEach((p) => {
          row1 += `<th class="col-quarter text-center kpi-day-col">${escHtml(p.label)}</th>`;
        });
        row1 += "</tr>";
        thead.innerHTML = row1;
      } else {
        let thRow1 =
          '<tr><th rowspan="2" class="col-code">Kodu</th><th rowspan="2" class="col-strategy">Ana Strateji</th><th rowspan="2" class="col-strategy">Alt Strateji</th><th rowspan="2">Performans Adı</th><th rowspan="2" class="col-weight">Ağırlık (%)</th><th rowspan="2" class="col-unit">Birim</th><th rowspan="2" class="col-period">Ölçüm Per.</th><th rowspan="2" class="col-target-main">Yıllık Hedef</th>';
        let thRow2 = "<tr>";
        periods.forEach((p) => {
          thRow1 += `<th colspan="3" class="text-center">${escHtml(p.label)}</th>`;
          thRow2 += '<th class="col-quarter">Hedef</th><th class="col-quarter">Gerç.</th><th class="col-quarter">Durum</th>';
        });
        thRow1 +=
          '<th rowspan="2" class="col-target">Başarı Puanı</th><th rowspan="2" class="col-actions no-print">İşlemler</th></tr>';
        thead.innerHTML = thRow1 + thRow2;
      }

      if (!kpis || kpis.length === 0) {
        const periodCols = isGunluk ? periods.length : periods.length * 3;
        const colspan = 8 + periodCols + 2;
        tbody.innerHTML = `<tr><td colspan="${colspan}" class="micro-pg-empty-cell">Henüz performans göstergesi yok.</td></tr>`;
        applyColumnVisibility();
        return;
      }

      const rows = kpis.map((k) => {
        let basariAraliklari = null;
        try {
          basariAraliklari = k.basari_puani_araliklari
            ? typeof k.basari_puani_araliklari === "string"
              ? JSON.parse(k.basari_puani_araliklari)
              : k.basari_puani_araliklari
            : null;
        } catch (_e) {
          basariAraliklari = null;
        }

        const strategyTitle = (k.strategy_title || "-").toString().substring(0, 20);
        const subStrategyTitle = (k.sub_strategy_title || "-").toString().substring(0, 20);
        const kpiName = escHtml((k.name || "-").toString());
        const targetValRaw = k.target_value || "-";
        const hesaplamaYontemi = k.data_collection_method || "Ortalama";
        const olcumPeriyodu = k.period || "";
        const yillikHedef = computeYillikHedef(k.target_value, olcumPeriyodu, hesaplamaYontemi);
        const yillikHedefDisplay =
          yillikHedef !== null
            ? Number.isInteger(yillikHedef)
              ? yillikHedef
              : yillikHedef.toFixed(2)
            : targetValRaw;
        const isFav = k.is_favorite || favSet.has(k.id);
        const favIconClass = isFav ? "fas fa-star" : "far fa-star";

        let fixedCols = `<td class="col-code">${escHtml(k.code || "")}</td><td class="col-strategy small">${escHtml(strategyTitle)}${(k.strategy_title || "").length > 20 ? "…" : ""}</td><td class="col-strategy small">${escHtml(subStrategyTitle)}${(k.sub_strategy_title || "").length > 20 ? "…" : ""}</td><td class="fw-medium">${kpiName}</td><td class="col-weight text-center">${escHtml(k.weight != null ? String(k.weight) : "-")}</td><td class="col-unit text-center">${escHtml(k.unit || "-")}</td><td class="col-period text-center"><span class="micro-pg-badge-period">${escHtml(olcumPeriyodu || "-")}</span></td><td class="col-target-main text-center fw-bold micro-pg-target-main">${escHtml(String(yillikHedefDisplay))}</td>`;

        const entries = k.entries || {};
        let periodCells = "";
        if (isGunluk) {
          periods.forEach((p) => {
            const val = entries[p.key];
            const hasVal = val !== undefined && val !== null && val !== "";
            const dataCls = hasVal ? "micro-pg-cell--filled" : "";
            const disp = hasVal ? (typeof val === "number" ? String(val) : String(val)) : "—";
            periodCells += `<td class="col-quarter text-center micro-kpi-data-cell ${dataCls}" data-kpi="${k.id}" data-period="${escHtml(p.key)}">${escHtml(disp)}</td>`;
          });
        } else {
          periods.forEach((p) => {
            const val = entries[p.key];
            const hasVal = val !== undefined && val !== null && val !== "";
            const cellTarget = computeCellTarget(k.target_value, olcumPeriyodu, hesaplamaYontemi, currentPeriyot, p.key);
            const target = cellTarget !== null ? cellTarget : parseFloat(k.target_value);
            const actual = parseFloat(val);
            let durumHtml = "—";
            if (hasVal && !Number.isNaN(target) && !Number.isNaN(actual) && target > 0) {
              const ratio =
                k.direction === "Decreasing" ? (actual > 0 ? target / actual : 0) : actual / target;
              const pct = Math.round(ratio * 100);
              const cls = ratio >= 1 ? "micro-pg-ok" : ratio >= 0.8 ? "micro-pg-warn" : "micro-pg-bad";
              durumHtml = `<span class="${cls} fw-bold">%${pct}</span>`;
            }
            const hedefDisplay =
              cellTarget !== null
                ? Number.isInteger(cellTarget)
                  ? cellTarget
                  : cellTarget.toFixed(2)
                : targetValRaw;
            const dataCls = hasVal ? "micro-pg-cell--filled" : "";
            const disp = hasVal ? (typeof val === "number" ? String(val) : String(val)) : "—";
            periodCells += `<td class="col-quarter text-center">${escHtml(String(hedefDisplay))}</td><td class="col-quarter text-center micro-kpi-data-cell ${dataCls}" data-kpi="${k.id}" data-period="${escHtml(p.key)}">${escHtml(disp)}</td><td class="col-quarter text-center">${durumHtml}</td>`;
          });
        }

        const allVals = Object.values(entries)
          .map((v) => parseFloat(v))
          .filter((v) => !Number.isNaN(v));
        let skorHtml = "—";
        const skorTarget = yillikHedef !== null ? yillikHedef : parseFloat(k.target_value);
        if (allVals.length > 0 && !Number.isNaN(skorTarget) && skorTarget > 0) {
          const compareVal =
            hesaplamaYontemi === "Toplama" || hesaplamaYontemi === "Toplam"
              ? allVals.reduce((a, b) => a + b, 0)
              : allVals[allVals.length - 1];
          let pct = Math.round((compareVal / skorTarget) * 100);
          if (k.direction === "Decreasing") pct = compareVal > 0 ? Math.round((skorTarget / compareVal) * 100) : 0;
          if (basariAraliklari) {
            const puan = hesaplaBasariPuani(pct, basariAraliklari);
            if (puan !== null) {
              const cls = puan >= 4 ? "micro-pg-ok" : puan >= 3 ? "micro-pg-warn" : "micro-pg-bad";
              skorHtml = `<span class="${cls} fw-bold">${puan}/5</span>`;
            } else {
              skorHtml = `<span class="${pct >= 100 ? "micro-pg-ok" : pct >= 80 ? "micro-pg-warn" : "micro-pg-bad"} fw-bold">%${pct}</span>`;
            }
          } else {
            skorHtml = `<span class="${pct >= 100 ? "micro-pg-ok" : pct >= 80 ? "micro-pg-warn" : "micro-pg-bad"} fw-bold">%${pct}</span>`;
          }
        }

        const delName = (k.name || "").replace(/\\/g, "\\\\").replace(/'/g, "\\'");
        const actions = canCrudPg
          ? `<div class="micro-pg-row-actions">
            <button type="button" class="mc-btn mc-btn-secondary mc-btn-sm karne-fav-kpi-btn ${isFav ? "karne-fav-kpi-btn--on" : ""}" data-kpi-id="${k.id}" title="Favori"><i class="${favIconClass}" aria-hidden="true"></i></button>
            <button type="button" class="mc-btn mc-btn-secondary mc-btn-sm btn-kpi-edit" data-kpi-id="${k.id}" title="Düzenle"><i class="fas fa-pen" aria-hidden="true"></i></button>
            <button type="button" class="mc-btn mc-btn-secondary mc-btn-sm btn-kpi-delete" data-kpi-id="${k.id}" title="Sil"><i class="fas fa-trash" aria-hidden="true"></i></button>
          </div>`
          : `<button type="button" class="mc-btn mc-btn-secondary mc-btn-sm karne-fav-kpi-btn ${isFav ? "karne-fav-kpi-btn--on" : ""}" data-kpi-id="${k.id}" title="Favori"><i class="${favIconClass}" aria-hidden="true"></i></button>`;

        const hl = highlightKpiId && Number(k.id) === Number(highlightKpiId) ? " micro-pg-row--highlight" : "";
        return `<tr class="micro-pg-data-row${hl}" data-kpi-id="${k.id}">${fixedCols}${periodCells}<td class="col-target text-center">${skorHtml}</td><td class="col-actions no-print">${actions}</td></tr>`;
      });

      tbody.innerHTML = rows.join("");
      applyColumnVisibility();

      if (highlightKpiId) {
        const row = tbody.querySelector(`tr[data-kpi-id="${highlightKpiId}"]`);
        if (row) {
          row.scrollIntoView({ behavior: "smooth", block: "center" });
          setTimeout(() => row.classList.remove("micro-pg-row--highlight"), 4000);
        }
        highlightKpiId = null;
      }
    }

    async function loadKarneData() {
      if (!karneApiUrl) return;
      const viewedYear = getViewedYear();
      const url = `${karneApiUrl}?year=${viewedYear}`;
      try {
        const r = await fetch(url, { credentials: "same-origin", headers: { Accept: "application/json" } });
        const res = await r.json();
        if (!res.success) return;
        rebuildPGTableByPeriyot(res.kpis || [], res.favorite_kpi_ids || []);
      } catch (e) {
        console.error(e);
        showError("Karne verisi yüklenemedi.");
      }
    }

    function syncFiltersFromMainPage() {
      const mainYear = document.getElementById("year-select");
      const mainPeriyot = document.getElementById("pg-periyot-select");
      const mainAy = document.getElementById("pg-gunluk-ay-select");
      const cy = new Date().getFullYear();
      const cm = new Date().getMonth() + 1;
      if (yilSel && mainYear) {
        yilSel.innerHTML = "";
        Array.from(mainYear.options).forEach((o) => {
          yilSel.appendChild(new Option(o.textContent, o.value, false, o.selected));
        });
        const yNow = String(cy);
        if ([...yilSel.options].some((o) => o.value === yNow)) yilSel.value = yNow;
        else if (yilSel.options.length) yilSel.selectedIndex = 0;
      }
      const modalAllowed = new Set(["yillik", "alti_ay", "ceyrek", "aylik", "haftalik", "gunluk"]);
      if (periyotSel && mainPeriyot) {
        const mv = mainPeriyot.value || "ceyrek";
        const use = modalAllowed.has(mv) ? mv : "ceyrek";
        if ([...periyotSel.options].some((o) => o.value === use)) periyotSel.value = use;
        else periyotSel.value = "ceyrek";
        currentPeriyot = periyotSel.value;
      } else if (periyotSel) {
        currentPeriyot = periyotSel.value || "ceyrek";
      }
      gunlukViewYear = getBaseYearFromSelect();
      gunlukViewMonth = mainAy
        ? Math.max(1, Math.min(12, parseInt(mainAy.value, 10) || cm))
        : cm;
      currentOffset = 0;
    }

    function openModal(kpiId) {
      highlightKpiId = kpiId != null ? Number(kpiId) : null;
      currentOffset = 0;
      syncFiltersFromMainPage();
      updatePeriyotLabel();
      if (overlay) {
        overlay.classList.add("open");
        overlay.setAttribute("aria-hidden", "false");
      }
      loadKarneData();
    }

    function closeModal() {
      if (overlay) {
        overlay.classList.remove("open");
        overlay.setAttribute("aria-hidden", "true");
      }
      closeVeriNested();
    }

    function closeVeriNested() {
      if (veriDuzenleOverlay) {
        veriDuzenleOverlay.classList.remove("open");
        veriDuzenleOverlay.setAttribute("aria-hidden", "true");
      }
      if (veriDetayOverlay) {
        veriDetayOverlay.classList.remove("open");
        veriDetayOverlay.setAttribute("aria-hidden", "true");
      }
    }

    function openVeriDetayModal() {
      if (!veriDetayOverlay) return;
      veriDetayOverlay.classList.add("open");
      veriDetayOverlay.setAttribute("aria-hidden", "false");
    }

    function periodLabelForKey(periodKey, yearForHafta) {
      const map = {
        ceyrek_1: "I. Çeyrek",
        ceyrek_2: "II. Çeyrek",
        ceyrek_3: "III. Çeyrek",
        ceyrek_4: "IV. Çeyrek",
        yillik_1: "Yıl Sonu",
        halfyear_1: "Ocak – Haziran",
        halfyear_2: "Temmuz – Aralık",
      };
      if (map[periodKey]) return map[periodKey];
      const hm = periodKey.match(/^haftalik_(\d+)_(\d+)$/);
      if (hm) {
        const y = yearForHafta != null ? yearForHafta : getViewedYear();
        const lbl = haftalikRangeLabelTr(y, parseInt(hm[2], 10), parseInt(hm[1], 10));
        return lbl || periodKey;
      }
      const aylar = ["", ...AYLAR_TR_FULL];
      if (periodKey.startsWith("gunluk_")) {
        const p = periodKey.split("_");
        return `${p[1] || ""} ${aylar[parseInt(p[2], 10)] || ""}`;
      }
      return periodKey;
    }

    async function loadVeriDetayContent(kpiId, periodKey) {
      if (!veriDetayContent || !kpiDetailUrl) return;
      veriDetayContent.innerHTML = '<p class="karne-field-hint">Yükleniyor…</p>';
      _veriDetayKpiId = kpiId;
      _veriDetayPeriodKey = periodKey;
      const y = getViewedYear();
      const url = `${kpiDetailUrl}?kpi_id=${encodeURIComponent(kpiId)}&period_key=${encodeURIComponent(periodKey)}&year=${y}`;
      try {
        const r = await fetch(url, { credentials: "same-origin", headers: { Accept: "application/json" } });
        const res = await r.json();
        if (!res.success) {
          veriDetayContent.innerHTML = `<p class="karne-field-hint">${escHtml(res.message || "Hata")}</p>`;
          return;
        }
        const pl = periodLabelForKey(periodKey, y);
        let html = `<h6 class="micro-veri-detay-head">${escHtml(res.kpi_name)} — <span class="micro-pg-badge-period">${escHtml(pl)}</span> <span class="micro-pg-year-badge">${y}</span></h6>`;

        if (res.entries && res.entries.length > 0) {
          html += '<div class="micro-pg-table-scroll"><table class="micro-pg-mini-table"><thead><tr><th>Veri tarihi</th><th>Giriş</th><th>Gerçekleşen</th><th>Açıklama</th><th>Kullanıcı</th><th></th></tr></thead><tbody>';
          res.entries.forEach((e) => {
            const vd = e.data_date ? new Date(e.data_date).toLocaleDateString("tr-TR") : "—";
            const gd = e.created_at ? new Date(e.created_at).toLocaleString("tr-TR") : "—";
            html += `<tr data-entry-id="${e.id}">
              <td><small>${escHtml(vd)}</small></td>
              <td><small>${escHtml(gd)}</small></td>
              <td><strong>${escHtml(String(e.actual_value ?? ""))}</strong></td>
              <td><small>${escHtml(String(e.description || "—"))}</small></td>
              <td><small>${escHtml(String(e.user || ""))}</small></td>
              <td>
                <button type="button" class="mc-btn mc-btn-secondary mc-btn-sm micro-btn-edit-veri" data-entry-id="${e.id}" data-actual="${String(e.actual_value ?? "").replace(/"/g, "&quot;")}" data-desc="${String(e.description ?? "").replace(/"/g, "&quot;")}">Düzenle</button>
                <button type="button" class="mc-btn mc-btn-secondary mc-btn-sm micro-btn-del-veri" data-entry-id="${e.id}">Sil</button>
              </td>
            </tr>`;
          });
          html += "</tbody></table></div>";
        } else {
          html += '<p class="karne-field-hint">Bu periyot için kayıt yok.</p>';
        }

        if (res.audits && res.audits.length > 0) {
          html += '<h6 class="micro-veri-audit-head">İşlem geçmişi</h6><div class="micro-pg-table-scroll"><table class="micro-pg-mini-table"><thead><tr><th>Tarih</th><th>İşlem</th><th>Kullanıcı</th><th>Eski</th><th>Yeni</th></tr></thead><tbody>';
          res.audits.forEach((a) => {
            const d = a.created_at ? new Date(a.created_at).toLocaleString("tr-TR") : "—";
            html += `<tr><td><small>${escHtml(d)}</small></td><td>${escHtml(a.action_label || a.action_type)}</td><td>${escHtml(a.user || "")}</td><td><small>${escHtml(String(a.old_value ?? "—"))}</small></td><td><small>${escHtml(String(a.new_value ?? "—"))}</small></td></tr>`;
          });
          html += "</tbody></table></div>";
        }

        html += '<p class="karne-field-hint micro-proje-gorev-hint"><strong>Proje görevleri:</strong> <span id="micro-pg-proje-list">…</span></p>';
        veriDetayContent.innerHTML = html;
        const listEl = document.getElementById("micro-pg-proje-list");
        if (listEl && kpiProjeUrl) {
          fetch(`${kpiProjeUrl}?kpi_id=${kpiId}&year=${y}&period_key=${encodeURIComponent(periodKey)}`, { credentials: "same-origin" })
            .then((x) => x.json())
            .then((pr) => {
              if (pr.success && pr.gorevler && pr.gorevler.length) {
                listEl.textContent = pr.gorevler.map((g) => g.title || g.ad || "Görev").join(", ");
              } else listEl.textContent = "Bağlı görev yok.";
            })
            .catch(() => {
              listEl.textContent = "Yüklenemedi.";
            });
        }
      } catch (_e) {
        veriDetayContent.innerHTML = '<p class="karne-field-hint">Yükleme hatası.</p>';
      }
    }

    function expandDataUrl(tpl, rowId) {
      if (!tpl || !kpiDataRowPlaceholder) return "";
      return tpl.split(kpiDataRowPlaceholder).join(String(rowId));
    }

    if (tbody) {
      tbody.addEventListener("click", (e) => {
        const cell = e.target.closest(".micro-kpi-data-cell");
        if (!cell) return;
        const kid = cell.dataset.kpi;
        const pk = cell.dataset.period;
        if (!kid || !pk) return;
        openVeriDetayModal();
        loadVeriDetayContent(parseInt(kid, 10), pk);
      });
    }

    if (veriDetayContent) {
      veriDetayContent.addEventListener("click", (e) => {
        const ed = e.target.closest(".micro-btn-edit-veri");
        if (ed) {
          e.preventDefault();
          const id = parseInt(ed.dataset.entryId, 10);
          const act = ed.dataset.actual || "";
          const desc = ed.dataset.desc || "";
          const aEl = document.getElementById("micro-veri-duzenle-actual");
          const dEl = document.getElementById("micro-veri-duzenle-desc");
          if (aEl) aEl.value = act;
          if (dEl) dEl.value = desc;
          if (veriDuzenleOverlay) {
            veriDuzenleOverlay.dataset.editEntryId = String(id);
            veriDuzenleOverlay.classList.add("open");
            veriDuzenleOverlay.setAttribute("aria-hidden", "false");
          }
          return;
        }
        const del = e.target.closest(".micro-btn-del-veri");
        if (del) {
          e.preventDefault();
          const id = parseInt(del.dataset.entryId, 10);
          if (!id) return;
          Swal.fire({
            title: "Veriyi pasifleştir?",
            icon: "warning",
            showCancelButton: true,
            confirmButtonText: "Evet",
            cancelButtonText: "İptal",
            confirmButtonColor: "#b45309",
          }).then(async (r) => {
            if (!r.isConfirmed) return;
            const url = expandDataUrl(kpiDataDeleteTemplate, id);
            if (!url) return;
            const out = await postJson(url, {});
            if (out.success) {
              toastSuccess(out.message || "Silindi.");
              loadVeriDetayContent(_veriDetayKpiId, _veriDetayPeriodKey);
              loadKarneData();
              if (typeof onAfterMutation === "function") onAfterMutation();
            } else showError(out.message || "Hata");
          });
        }
      });
    }

    document.getElementById("btn-micro-veri-duzenle-save")?.addEventListener("click", async () => {
      const modal = veriDuzenleOverlay;
      const id = modal ? parseInt(modal.dataset.editEntryId, 10) : NaN;
      if (!id) return;
      const av = (document.getElementById("micro-veri-duzenle-actual")?.value || "").trim();
      const ds = (document.getElementById("micro-veri-duzenle-desc")?.value || "").trim();
      const url = expandDataUrl(kpiDataUpdateTemplate, id);
      if (!url) return;
      const out = await postJson(url, { actual_value: av, description: ds });
      if (out.success) {
        toastSuccess(out.message || "Güncellendi.");
        modal.classList.remove("open");
        modal.setAttribute("aria-hidden", "true");
        loadVeriDetayContent(_veriDetayKpiId, _veriDetayPeriodKey);
        loadKarneData();
        if (typeof onAfterMutation === "function") onAfterMutation();
      } else showError(out.message || "Hata");
    });

    document.getElementById("btn-micro-veri-duzenle-cancel")?.addEventListener("click", () => {
      veriDuzenleOverlay?.classList.remove("open");
      veriDuzenleOverlay?.setAttribute("aria-hidden", "true");
    });
    document.getElementById("btn-micro-veri-duzenle-close")?.addEventListener("click", () => {
      veriDuzenleOverlay?.classList.remove("open");
      veriDuzenleOverlay?.setAttribute("aria-hidden", "true");
    });

    document.getElementById("btn-micro-veri-detay-close")?.addEventListener("click", closeVeriNested);
    document.getElementById("btn-micro-veri-detay-footer-close")?.addEventListener("click", closeVeriNested);

    document.getElementById("btn-micro-pg-tablo-close")?.addEventListener("click", closeModal);
    document.getElementById("btn-micro-pg-tablo-footer-close")?.addEventListener("click", closeModal);
    overlay?.addEventListener("click", (e) => {
      if (e.target === overlay) closeModal();
    });
    veriDetayOverlay?.addEventListener("click", (e) => {
      if (e.target === veriDetayOverlay) closeVeriNested();
    });
    veriDuzenleOverlay?.addEventListener("click", (e) => {
      if (e.target === veriDuzenleOverlay) {
        veriDuzenleOverlay.classList.remove("open");
        veriDuzenleOverlay.setAttribute("aria-hidden", "true");
      }
    });

    document.getElementById("btn-micro-pg-tablo-add-pg")?.addEventListener("click", () => {
      if (typeof openAddKpiModal === "function") openAddKpiModal();
    });

    yilSel?.addEventListener("change", () => {
      currentOffset = 0;
      if (currentPeriyot === "gunluk") gunlukViewYear = getBaseYearFromSelect();
      updatePeriyotLabel();
      loadKarneData();
    });
    periyotSel?.addEventListener("change", () => {
      currentPeriyot = periyotSel.value;
      currentOffset = 0;
      if (currentPeriyot === "gunluk") {
        gunlukViewYear = getBaseYearFromSelect();
        gunlukViewMonth = new Date().getMonth() + 1;
      }
      updatePeriyotLabel();
      loadKarneData();
    });

    document.getElementById("micro-pg-nav-prev")?.addEventListener("click", () => {
      if (currentPeriyot === "gunluk") {
        if (gunlukViewMonth > 1) gunlukViewMonth -= 1;
        else {
          gunlukViewMonth = 12;
          gunlukViewYear -= 1;
        }
        if (yilSel && [...yilSel.options].some((o) => o.value === String(gunlukViewYear))) {
          yilSel.value = String(gunlukViewYear);
        }
      } else {
        currentOffset -= 1;
      }
      updatePeriyotLabel();
      loadKarneData();
    });
    document.getElementById("micro-pg-nav-next")?.addEventListener("click", () => {
      if (currentPeriyot === "gunluk") {
        if (gunlukViewMonth < 12) gunlukViewMonth += 1;
        else {
          gunlukViewMonth = 1;
          gunlukViewYear += 1;
        }
        if (yilSel && [...yilSel.options].some((o) => o.value === String(gunlukViewYear))) {
          yilSel.value = String(gunlukViewYear);
        }
      } else {
        currentOffset += 1;
      }
      updatePeriyotLabel();
      loadKarneData();
    });

    ["micro-col-code-chk", "micro-col-strategy-chk", "micro-col-weight-chk", "micro-col-unit-chk", "micro-col-period-chk", "micro-col-target-chk"].forEach((id) => {
      document.getElementById(id)?.addEventListener("change", applyColumnVisibility);
    });

    return { open: openModal, close: closeModal, reload: loadKarneData };
  }

  global.initMicroPgTabloModal = initMicroPgTabloModal;
})(typeof window !== "undefined" ? window : this);
