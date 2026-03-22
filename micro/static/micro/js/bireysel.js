/**
 * bireysel.js — Bireysel Performans modülü JS
 * Kural: alert()/confirm()/prompt() YASAK — yalnızca SweetAlert2
 * Kural: Jinja2 {{ }} bu dosyada YASAK — veri data-* ile gelir
 */

(function () {
  "use strict";

  const root = document.getElementById("bireysel-root");
  if (!root) return;

  const KARNE_API = root.dataset.karneApiUrl;
  const PG_ADD_URL = root.dataset.pgAddUrl;
  const VERI_ADD_URL = root.dataset.veriAddUrl;
  const FAALIYET_ADD_URL = root.dataset.faaliyetAddUrl;
  const PG_DEL_BASE = root.dataset.pgDeleteBase;
  const FAALIYET_DEL_BASE = root.dataset.faaliyetDeleteBase;
  const FAALIYET_TRACK_BASE = root.dataset.faaliyetTrackBase;
  const PG_SERIES_TEMPLATE = root.dataset.pgSeriesUrlTemplate || "";

  const yearSelect = document.getElementById("year-select");
  const pgTbody = document.getElementById("pg-tbody");
  const faaliyetTbody = document.getElementById("faaliyet-tbody");
  const loadingEl = document.getElementById("karne-loading");
  const timelineList = document.getElementById("karne-timeline-list");
  const timelineEmpty = document.getElementById("karne-timeline-empty");
  const insightsStrip = document.getElementById("karne-insights-strip");

  let lastPgs = [];
  let lastYear = null;

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
      toast: true,
      position: "top-end",
      icon: "success",
      title: msg,
      showConfirmButton: false,
      timer: 2500,
      timerProgressBar: true,
    });
  }

  function showError(msg) {
    Swal.fire({ icon: "error", title: "Hata", text: msg, confirmButtonColor: "#dc2626" });
  }

  async function confirmDelete(title, text) {
    const r = await Swal.fire({
      title: title,
      text: text,
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#dc2626",
      cancelButtonColor: "#6b7280",
      confirmButtonText: "Evet, sil",
      cancelButtonText: "İptal",
    });
    return r.isConfirmed;
  }

  function escHtml(s) {
    if (!s) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function seriesUrl(pgId, year) {
    if (!PG_SERIES_TEMPLATE) return `/bireysel/api/pg/${pgId}/series?year=${year}`;
    return PG_SERIES_TEMPLATE.replace("999999", String(pgId)) + `?year=${year}`;
  }

  /** Geçmiş/geçerli ay mı (ısı için); gelecek aylarda vurgu yok */
  function monthNeedsHeatGrid(year, month) {
    const now = new Date();
    const cy = now.getFullYear();
    const cm = now.getMonth() + 1;
    if (year > cy) return false;
    if (year < cy) return true;
    return month <= cm;
  }

  function monthHeatClass(year, month, hasVal) {
    if (!monthNeedsHeatGrid(year, month)) return "";
    return hasVal ? "karne-cell-heat-fill" : "karne-cell-heat-empty";
  }

  function renderTimeline(items) {
    if (!timelineList || !timelineEmpty) return;
    timelineList.innerHTML = "";
    if (!items || !items.length) {
      timelineEmpty.style.display = "";
      return;
    }
    timelineEmpty.style.display = "none";
    items.forEach((ev) => {
      const li = document.createElement("li");
      li.className = "karne-timeline-item";
      const dotClass = ev.kind === "faaliyet" ? "karne-timeline-dot--faaliyet" : "karne-timeline-dot--pg";
      const dt = ev.ts ? new Date(ev.ts) : null;
      const timeStr = dt && !Number.isNaN(dt.getTime())
        ? dt.toLocaleString("tr-TR", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })
        : "";
      li.innerHTML = `
        <div class="karne-timeline-dot ${dotClass}" aria-hidden="true"></div>
        <div style="flex:1;min-width:0;">
          <div><strong>${escHtml(ev.title || "")}</strong> ${ev.detail ? `<span style="color:#64748b;">— ${escHtml(ev.detail)}</span>` : ""}</div>
          ${ev.sub ? `<div class="karne-timeline-meta">${escHtml(ev.sub)}</div>` : ""}
          ${timeStr ? `<div class="karne-timeline-meta">${escHtml(timeStr)}</div>` : ""}
        </div>`;
      timelineList.appendChild(li);
    });
  }

  function parseNum(v) {
    if (v == null || v === "") return null;
    const n = parseFloat(String(v).replace(",", "."));
    return Number.isFinite(n) ? n : null;
  }

  function renderInsights(pgs, year) {
    if (!insightsStrip) return;
    insightsStrip.innerHTML = "";
    if (!pgs || !pgs.length) {
      insightsStrip.innerHTML =
        `<span class="karne-insight-pill">Henüz PG yok — ilk göstergenizi ekleyin.</span>`;
      return;
    }

    const monthsHit = new Set();
    let pgNoYearData = 0;
    (pgs || []).forEach((pg) => {
      const ent = pg.entries || {};
      const keys = Object.keys(ent);
      const anyYear = keys.some((k) => k.startsWith("aylik_") && ent[k]);
      if (!anyYear) pgNoYearData += 1;
      for (let m = 1; m <= 12; m++) {
        if (ent[`aylik_${m}`]) monthsHit.add(m);
      }
    });

    const pills = [];
    pills.push({
      cls: "karne-insight-pill",
      html: `<i class="fas fa-calendar-check"></i> ${monthsHit.size}/12 ayda en az bir PG verisi`,
    });
    pills.push({
      cls: pgNoYearData ? "karne-insight-pill karne-insight-pill--warn" : "karne-insight-pill karne-insight-pill--ok",
      html: `<i class="fas fa-bullseye"></i> ${pgNoYearData} gösterge bu yıl henüz veri almadı`,
    });

    let lowSignal = 0;
    (pgs || []).forEach((pg) => {
      const tgt = parseNum(pg.target_value);
      if (tgt == null) return;
      let lastVal = null;
      for (let m = 12; m >= 1; m--) {
        const v = parseNum(pg.entries && pg.entries[`aylik_${m}`]);
        if (v != null) {
          lastVal = v;
          break;
        }
      }
      if (lastVal == null) return;
      const inc = (pg.direction || "Increasing").toLowerCase().includes("increas") || pg.direction === "Increasing";
      const bad = inc ? lastVal < tgt * 0.9 : lastVal > tgt * 1.1;
      if (bad) lowSignal += 1;
    });
    if (lowSignal > 0) {
      pills.push({
        cls: "karne-insight-pill karne-insight-pill--warn",
        html: `<i class="fas fa-triangle-exclamation"></i> ${lowSignal} gösterge son veride hedefe göre zayıf görünüyor
          <small style="display:block;font-weight:500;margin-top:4px;opacity:0.92;">Tahmini göstergedir; resmi performans değerlendirmesi değildir. Hedef ve yön bilgisine bağlıdır.</small>`,
      });
    }

    pills.forEach((p) => {
      const span = document.createElement("span");
      span.className = p.cls;
      span.innerHTML = p.html;
      insightsStrip.appendChild(span);
    });
  }

  function buildSparkHtml(monthly) {
    const vals = [];
    for (let m = 1; m <= 12; m++) {
      const raw = monthly[String(m)] ?? monthly[m];
      vals.push(parseNum(raw));
    }
    const finite = vals.filter((v) => v != null);
    const max = finite.length ? Math.max(...finite.map(Math.abs)) : 1;
    const bars = vals
      .map((v) => {
        if (v == null) {
          return `<div class="karne-spark-bar" style="height:4px;opacity:0.25;background:#94a3b8;"></div>`;
        }
        const h = Math.max(8, Math.round((Math.abs(v) / max) * 56));
        return `<div class="karne-spark-bar" style="height:${h}px" title="${escHtml(String(v))}"></div>`;
      })
      .join("");
    return `<div class="karne-spark-wrap" aria-hidden="true">${bars}</div><div class="mc-page-subtitle" style="margin-top:6px;">Aylık gerçekleşen (mini özet)</div>`;
  }

  async function openPgDetailModal(pg, year) {
    try {
      const res = await fetch(seriesUrl(pg.id, year));
      const data = await res.json();
      if (!data.success) throw new Error(data.message || "Detay alınamadı");
      const rows = (data.series || [])
        .map(
          (r) =>
            `<tr><td>${escHtml(r.data_date || "—")}</td><td><strong>${escHtml(r.actual_value || "—")}</strong></td><td>${escHtml(r.description || "—")}</td></tr>`
        )
        .join("");
      const table = rows
        ? `<table class="mc-table" style="font-size:12px;width:100%;"><thead><tr><th>Tarih</th><th>Değer</th><th>Not</th></tr></thead><tbody>${rows}</tbody></table>`
        : `<p class="mc-page-subtitle">Bu yıl için kayıtlı veri yok.</p>`;
      const spark = buildSparkHtml(data.monthly || {});
      await Swal.fire({
        title: escHtml(data.pg.name || "PG"),
        width: 640,
        html: `<div class="text-left" style="max-height:70vh;overflow:auto;">
          <p class="mc-page-subtitle" style="margin:0 0 8px;">Hedef: <strong>${escHtml(data.pg.target_value || "—")}</strong> ${data.pg.unit ? escHtml(data.pg.unit) : ""}</p>
          ${spark}
          <h4 style="margin:16px 0 8px;font-size:14px;">Kayıtlar</h4>
          ${table}
        </div>`,
        confirmButtonText: "Kapat",
        confirmButtonColor: "#4f46e5",
      });
    } catch (e) {
      showError(e.message || String(e));
    }
  }

  async function loadKarne() {
    const year = parseInt(yearSelect.value, 10);
    lastYear = year;
    if (loadingEl) loadingEl.style.display = "";
    pgTbody.innerHTML = "";
    faaliyetTbody.innerHTML = "";
    try {
      const res = await fetch(`${KARNE_API}?year=${year}`);
      const data = await res.json();
      if (!data.success) throw new Error(data.message || "Veri alınamadı.");
      lastPgs = data.pgs || [];
      updateStats(data.pgs, data.activities);
      renderInsights(data.pgs, year);
      renderTimeline(data.timeline || []);
      renderPgTable(data.pgs, year);
      renderFaaliyetTable(data.activities, year);
    } catch (err) {
      showError("Karne verileri yüklenirken hata: " + err.message);
    } finally {
      if (loadingEl) loadingEl.style.display = "none";
    }
  }

  function updateStats(pgs, activities) {
    const totalPg = pgs ? pgs.length : 0;
    let filledPg = 0;
    (pgs || []).forEach((pg) => {
      if (Object.values(pg.entries || {}).some((v) => v)) filledPg++;
    });
    const totalAct = activities ? activities.length : 0;
    let doneAct = 0;
    (activities || []).forEach((a) => {
      if (Object.values(a.monthly_tracks || {}).some((v) => v === true)) doneAct++;
    });
    const pct = totalAct > 0 ? Math.round((doneAct / totalAct) * 100) : 0;

    const el = (id) => document.getElementById(id);
    if (el("stat-total-pg")) el("stat-total-pg").textContent = totalPg;
    if (el("stat-filled-pg")) el("stat-filled-pg").textContent = filledPg;
    if (el("stat-activities")) el("stat-activities").textContent = totalAct;
    if (el("stat-done-pct")) el("stat-done-pct").textContent = pct + "%";
  }

  function renderPgTable(pgs, year) {
    if (!pgs || !pgs.length) {
      pgTbody.innerHTML = `<tr><td colspan="17" class="text-center py-8 text-gray-400">Henüz PG eklenmemiş.</td></tr>`;
      return;
    }
    pgTbody.innerHTML = pgs
      .map((pg, i) => {
        const monthCells = Array.from({ length: 12 }, (_, idx) => {
          const m = idx + 1;
          const key = `aylik_${m}`;
          const val = pg.entries[key];
          const has = !!val;
          const heat = monthHeatClass(year, m, has);
          return `<td class="px-2 py-2 text-center ${heat}">
          <button type="button" class="btn-veri-gir hover:underline"
                  data-pg-id="${pg.id}" data-month="${m}" data-year="${year}">${val || "—"}</button>
        </td>`;
        }).join("");
        return `<tr class="karne-pg-row" data-pg-id="${pg.id}">
        <td class="px-3 py-2 text-gray-400">${i + 1}</td>
        <td class="px-3 py-2 font-medium text-gray-800 dark:text-gray-100">${escHtml(pg.name)}
          ${pg.code ? `<span class="process-code-badge">${escHtml(pg.code)}</span>` : ""}
        </td>
        <td class="px-3 py-2 text-center">${escHtml(pg.target_value || "—")}</td>
        <td class="px-3 py-2 text-center text-gray-500">${escHtml(pg.unit || "—")}</td>
        ${monthCells}
        <td class="px-3 py-2 text-center">
          <button type="button" class="btn-pg-delete text-red-400 hover:text-red-600" data-pg-id="${pg.id}">
            <i class="fas fa-trash"></i>
          </button>
        </td>
      </tr>`;
      })
      .join("");
  }

  function renderFaaliyetTable(activities, year) {
    if (!activities || !activities.length) {
      faaliyetTbody.innerHTML = `<tr><td colspan="16" class="text-center py-8 text-gray-400">Henüz faaliyet eklenmemiş.</td></tr>`;
      return;
    }
    faaliyetTbody.innerHTML = activities
      .map((a, i) => {
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
          <button type="button" class="btn-faaliyet-delete text-red-400 hover:text-red-600" data-act-id="${a.id}">
            <i class="fas fa-trash"></i>
          </button>
        </td>
      </tr>`;
      })
      .join("");
  }

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
      focusConfirm: false,
      showCancelButton: true,
      confirmButtonText: "Kaydet",
      cancelButtonText: "İptal",
      confirmButtonColor: "#4f46e5",
      preConfirm: () => {
        const name = document.getElementById("pg-name").value.trim();
        if (!name) {
          Swal.showValidationMessage("Ad zorunludur.");
          return false;
        }
        return {
          name,
          target_value: document.getElementById("pg-target").value.trim() || null,
          unit: document.getElementById("pg-unit").value.trim() || null,
        };
      },
    });
    if (!vals) return;
    try {
      const d = await postJson(PG_ADD_URL, vals);
      if (d.success) {
        toastSuccess("PG eklendi.");
        loadKarne();
      } else showError(d.message || "Kayıt başarısız.");
    } catch (e) {
      showError("Sunucu hatası: " + e.message);
    }
  });

  document.getElementById("btn-faaliyet-add")?.addEventListener("click", async () => {
    const { value: vals } = await Swal.fire({
      title: "Yeni Faaliyet",
      html: `<div class="text-left space-y-3">
        <div><label class="block text-xs text-gray-500 mb-1">Ad <span class="text-red-500">*</span></label>
          <input id="fa-name" class="swal2-input" placeholder="Faaliyet adı"></div>
        <div><label class="block text-xs text-gray-500 mb-1">Açıklama</label>
          <textarea id="fa-desc" class="swal2-textarea" placeholder="Kısa açıklama"></textarea></div>
      </div>`,
      focusConfirm: false,
      showCancelButton: true,
      confirmButtonText: "Kaydet",
      cancelButtonText: "İptal",
      confirmButtonColor: "#4f46e5",
      preConfirm: () => {
        const name = document.getElementById("fa-name").value.trim();
        if (!name) {
          Swal.showValidationMessage("Ad zorunludur.");
          return false;
        }
        return { name, description: document.getElementById("fa-desc").value.trim() || null };
      },
    });
    if (!vals) return;
    try {
      const d = await postJson(FAALIYET_ADD_URL, vals);
      if (d.success) {
        toastSuccess("Faaliyet eklendi.");
        loadKarne();
      } else showError(d.message || "Kayıt başarısız.");
    } catch (e) {
      showError("Sunucu hatası: " + e.message);
    }
  });

  document.addEventListener("click", async (e) => {
    const row = e.target.closest(".karne-pg-row");
    if (row && !e.target.closest(".btn-veri-gir") && !e.target.closest(".btn-pg-delete")) {
      const id = parseInt(row.dataset.pgId, 10);
      const pg = (lastPgs || []).find((p) => p.id === id) || { id, name: "PG" };
      openPgDetailModal(pg, lastYear || parseInt(yearSelect.value, 10));
      return;
    }

    const btn = e.target.closest(".btn-veri-gir");
    if (btn) {
      const { value: val } = await Swal.fire({
        title: "Veri Gir",
        input: "text",
        inputLabel: "Gerçekleşen Değer",
        inputPlaceholder: "Örn: 92.5",
        showCancelButton: true,
        confirmButtonText: "Kaydet",
        cancelButtonText: "İptal",
        confirmButtonColor: "#4f46e5",
        inputValidator: (v) => !v && "Değer boş bırakılamaz.",
      });
      if (!val) return;
      try {
        const d = await postJson(VERI_ADD_URL, {
          pg_id: btn.dataset.pgId,
          year: parseInt(btn.dataset.year, 10),
          period_type: "aylik",
          period_no: parseInt(btn.dataset.month, 10),
          actual_value: val,
        });
        if (d.success) {
          toastSuccess("Veri kaydedildi.");
          loadKarne();
        } else showError(d.message || "Kayıt başarısız.");
      } catch (err) {
        showError("Sunucu hatası: " + err.message);
      }
      return;
    }

    const btnPgDel = e.target.closest(".btn-pg-delete");
    if (btnPgDel) {
      const ok = await confirmDelete("PG silinsin mi?", "Performans göstergesi pasife alınacak.");
      if (!ok) return;
      try {
        const d = await postJson(`${PG_DEL_BASE}${btnPgDel.dataset.pgId}`, {});
        if (d.success) {
          toastSuccess("PG silindi.");
          loadKarne();
        } else showError(d.message);
      } catch (err) {
        showError(err.message);
      }
      return;
    }

    const btnFaDel = e.target.closest(".btn-faaliyet-delete");
    if (btnFaDel) {
      const ok = await confirmDelete("Faaliyet silinsin mi?", "Faaliyet pasife alınacak.");
      if (!ok) return;
      try {
        const d = await postJson(`${FAALIYET_DEL_BASE}${btnFaDel.dataset.actId}`, {});
        if (d.success) {
          toastSuccess("Faaliyet silindi.");
          loadKarne();
        } else showError(d.message);
      } catch (err) {
        showError(err.message);
      }
    }
  });

  document.addEventListener("change", async (e) => {
    const cb = e.target.closest(".track-cb");
    if (!cb) return;
    try {
      const d = await postJson(`${FAALIYET_TRACK_BASE}${cb.dataset.actId}`, {
        year: parseInt(cb.dataset.year, 10),
        month: parseInt(cb.dataset.month, 10),
        completed: cb.checked,
      });
      if (!d.success) {
        cb.checked = !cb.checked;
        showError(d.message || "Takip güncellenemedi.");
      }
    } catch (err) {
      cb.checked = !cb.checked;
      showError(err.message);
    }
  });

  yearSelect.addEventListener("change", loadKarne);
  loadKarne();
})();
