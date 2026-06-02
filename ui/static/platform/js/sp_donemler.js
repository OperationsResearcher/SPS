/* SP Dönemler sayfası JavaScript — sp/donemler.html'den taşındı */

// ── Dönem işlemleri ────────────────────────────────────────────────────────
(function () {
  "use strict";
  const root = document.getElementById("sp-donemler-root");
  if (!root) return;

  const CREATE_URL     = root.dataset.planYearsCreateUrl    || "";
  const SET_ACTIVE_URL = root.dataset.planYearsSetActiveUrl || "";
  const CAN_MANAGE     = root.dataset.canManage === "true";

  function getCsrf() {
    const el = document.querySelector('meta[name="csrf-token"]');
    return el ? el.getAttribute("content") : "";
  }
  async function postJson(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrf() },
      body: JSON.stringify(body),
    });
    return res.json();
  }
  function toastOk(msg) {
    Swal.fire({ icon: "success", title: msg, timer: 2000, showConfirmButton: false, toast: true, position: "top-end" });
  }
  function toastErr(msg) {
    Swal.fire({ icon: "error", title: "Hata", text: msg });
  }

  document.querySelectorAll(".dpy-set-active").forEach(function (btn) {
    btn.addEventListener("click", async function () {
      const year = parseInt(this.dataset.year, 10);
      try {
        const data = await postJson(SET_ACTIVE_URL, { year });
        if (data.success) { window.location.reload(); }
        else { toastErr(data.message || "Dönem değiştirilemedi."); }
      } catch (e) { toastErr("Bağlantı hatası."); }
    });
  });

  const btnClose = document.getElementById("dpy-btn-close");
  if (btnClose && CAN_MANAGE) {
    btnClose.addEventListener("click", async function () {
      const closeUrl = this.dataset.closeUrl;
      const year = parseInt(this.dataset.year, 10);
      const result = await Swal.fire({
        icon: "warning", title: `${year} Dönemini Kapat`,
        html: `<p>${year} stratejik plan dönemi kapatılacak. Kapalı dönemler artık düzenlenemez.</p><p><strong>Bu işlem geri alınamaz.</strong></p>`,
        showCancelButton: true, confirmButtonText: "Evet, Kapat", cancelButtonText: "Vazgeç", confirmButtonColor: "#dc2626",
      });
      if (!result.isConfirmed) return;
      try {
        const data = await postJson(closeUrl, {});
        if (data.success) { toastOk(data.message || `${year} dönemi kapatıldı.`); setTimeout(() => window.location.reload(), 1200); }
        else { toastErr(data.message || "Dönem kapatılamadı."); }
      } catch (e) { toastErr("Bağlantı hatası."); }
    });
  }

  const modalNew = document.getElementById("dpy-modal-new");
  function openModal()  { if (modalNew) modalNew.classList.add("open"); }
  function closeModal() { if (modalNew) modalNew.classList.remove("open"); }

  ["dpy-btn-new", "dpy-btn-new-empty"].forEach(function (id) {
    const btn = document.getElementById(id);
    if (btn && CAN_MANAGE) btn.addEventListener("click", openModal);
  });
  document.querySelectorAll("[data-modal-close='dpy-modal-new']").forEach(function (el) {
    el.addEventListener("click", closeModal);
  });
  if (modalNew) modalNew.addEventListener("click", function (e) { if (e.target === modalNew) closeModal(); });

  const btnSave = document.getElementById("dpy-btn-save");
  if (btnSave && CAN_MANAGE) {
    btnSave.addEventListener("click", async function () {
      const newYear  = parseInt(document.getElementById("dpy-year")?.value || "", 10);
      const name     = document.getElementById("dpy-name")?.value.trim() || "";
      const fromYear = parseInt(document.getElementById("dpy-from-year")?.value || "", 10) || null;
      if (!newYear || newYear < 2000 || newYear > 2100) { toastErr("Geçerli bir yıl girin (2000-2100)."); return; }
      btnSave.disabled = true;
      try {
        const payload = { year: newYear };
        if (name)     payload.name      = name;
        if (fromYear) payload.from_year = fromYear;
        const data = await postJson(CREATE_URL, payload);
        if (data.success) { toastOk(data.message || `${newYear} dönemi oluşturuldu.`); closeModal(); setTimeout(() => window.location.reload(), 1200); }
        else { toastErr(data.message || "Dönem oluşturulamadı."); }
      } catch (e) { toastErr("Bağlantı hatası."); }
      finally { btnSave.disabled = false; }
    });
  }
})();

// ── Dönem Karşılaştırma ────────────────────────────────────────────────────
(function () {
  "use strict";
  const panel = document.getElementById("dpy-compare-panel");
  if (!panel) return;

  const COMPARE_URL = panel.dataset.compareUrl || "";
  const selY1       = document.getElementById("dpy-cmp-y1");
  const selY2       = document.getElementById("dpy-cmp-y2");
  const btn         = document.getElementById("dpy-cmp-btn");
  const resultBox   = document.getElementById("dpy-cmp-result");

  if (selY1 && selY2 && selY1.options.length >= 2) {
    selY1.selectedIndex = 0;
    selY2.selectedIndex = 1;
  }

  function badge(txt, color) {
    return `<span style="display:inline-block;padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600;background:${color}20;color:${color};">${txt}</span>`;
  }

  // XSS koruması: DB'den gelen kullanıcı-düzenlenebilir değerler innerHTML'e
  // yazılmadan önce escape edilir. Modül kapsamında ki metaRowFn/entityRowFn de erişsin.
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

  function metaRowFn(item) {
    const bg = item.changed ? "background:#fef9c3;" : "";
    return `<tr style="${bg}border-bottom:1px solid #f1f5f9;">
      <td style="padding:8px 12px;font-weight:600;color:#475569;white-space:nowrap;">${item.field}</td>
      <td style="padding:8px 12px;color:#1e293b;">${esc(item.y1)}</td>
      <td style="padding:8px 12px;color:#1e293b;">${esc(item.y2)}</td>
    </tr>`;
  }

  let y1ref = null, y2ref = null;

  function entityRowFn(item) {
    const bg = item.changed ? "background:#fef9c3;" : "";
    const tag = item.only_in_y1
      ? badge("Sadece " + (y1ref ? y1ref.year : "Y1") + "'de", "#f59e0b")
      : item.only_in_y2
        ? badge("Sadece " + (y2ref ? y2ref.year : "Y2") + "'de", "#3b82f6")
        : "";
    if (item.only_in_y1 || item.only_in_y2) {
      return `<tr style="${bg}border-bottom:1px solid #f1f5f9;"><td style="padding:8px 12px;color:#1e293b;" colspan="3">${esc(item.title)} ${tag}</td></tr>`;
    }
    if (!item.changed_fields || item.changed_fields.length === 0) {
      return `<tr style="${bg}border-bottom:1px solid #f1f5f9;">
        <td style="padding:8px 12px;color:#1e293b;">${esc(item.title)}</td>
        <td colspan="2" style="padding:8px 12px;color:#94a3b8;font-size:12px;">Değişiklik yok</td>
      </tr>`;
    }
    return item.changed_fields.map((cf, i) => {
      const rowBg = i === 0 ? bg : "background:#fef9c3;";
      const nameCell = i === 0 ? `<td style="padding:8px 12px;color:#1e293b;vertical-align:top;" rowspan="${item.changed_fields.length}">${esc(item.title)}</td>` : "";
      return `<tr style="${rowBg}border-bottom:1px solid #f1f5f9;">${nameCell}
        <td style="padding:6px 12px;"><span style="font-size:11px;font-weight:600;color:#6366f1;">${cf[0]}:</span><span style="font-size:12px;color:#1e293b;"> ${esc(cf[1])}</span></td>
        <td style="padding:6px 12px;"><span style="font-size:11px;font-weight:600;color:#6366f1;">${cf[0]}:</span><span style="font-size:12px;color:#1e293b;"> ${esc(cf[2])}</span></td>
      </tr>`;
    }).join("");
  }

  function genericSection(title, icon, items, rowFn, emptyMsg) {
    const changed = items.filter(x => x.changed);
    const countBadge = changed.length > 0
      ? `<span style="margin-left:8px;background:#6366f1;color:#fff;border-radius:12px;font-size:11px;padding:1px 8px;">${changed.length} fark</span>`
      : `<span style="margin-left:8px;background:#e2e8f0;color:#64748b;border-radius:12px;font-size:11px;padding:1px 8px;">Fark yok</span>`;
    const rows = items.length > 0 ? items.map(rowFn).join("") : `<tr><td colspan="3" style="text-align:center;padding:16px;color:#94a3b8;font-size:13px;">${emptyMsg}</td></tr>`;
    return `<details ${changed.length > 0 ? "open" : ""} style="margin-bottom:12px;">
      <summary style="cursor:pointer;padding:10px 12px;background:#f8fafc;border-radius:6px;font-size:13px;font-weight:600;color:#1e293b;list-style:none;display:flex;align-items:center;gap:6px;border:1px solid #e2e8f0;">
        <i class="${icon}" style="color:#6366f1;"></i> ${title} ${countBadge}
      </summary>
      <div style="overflow-x:auto;margin-top:6px;">
        <table style="width:100%;border-collapse:collapse;font-size:12.5px;">
          <thead><tr style="background:#f1f5f9;">
            <th style="padding:8px 12px;text-align:left;font-weight:600;color:#475569;">Ad</th>
            <th style="padding:8px 12px;text-align:left;font-weight:600;color:#475569;">${y1ref.year}</th>
            <th style="padding:8px 12px;text-align:left;font-weight:600;color:#475569;">${y2ref.year}</th>
          </tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </details>`;
  }

  function renderResult(data) {
    y1ref = data.y1;
    y2ref = data.y2;
    const { summary, diff } = data;
    const totalChanged = summary.meta_changed + summary.strategies_changed
      + summary.sub_strategies_changed + summary.processes_changed + summary.kpis_changed;
    const summaryColor = totalChanged > 0 ? "#6366f1" : "#16a34a";
    const summaryText = totalChanged > 0
      ? `Toplam <strong>${totalChanged}</strong> farklı alan bulundu.`
      : "İki dönem arasında kayıtlı konfigürasyon farkı yok.";

    const metaChangedCount = diff.meta.filter(m => m.changed).length;
    const metaCountBadge = metaChangedCount > 0
      ? `<span style="margin-left:8px;background:#6366f1;color:#fff;border-radius:12px;font-size:11px;padding:1px 8px;">${metaChangedCount} fark</span>`
      : `<span style="margin-left:8px;background:#e2e8f0;color:#64748b;border-radius:12px;font-size:11px;padding:1px 8px;">Fark yok</span>`;

    const metaSection = `<details open style="margin-bottom:12px;">
      <summary style="cursor:pointer;padding:10px 12px;background:#f8fafc;border-radius:6px;font-size:13px;font-weight:600;color:#1e293b;list-style:none;display:flex;align-items:center;gap:6px;border:1px solid #e2e8f0;">
        <i class="fas fa-info-circle" style="color:#6366f1;"></i> Dönem Bilgileri ${metaCountBadge}
      </summary>
      <div style="overflow-x:auto;margin-top:6px;">
        <table style="width:100%;border-collapse:collapse;font-size:12.5px;">
          <thead><tr style="background:#f1f5f9;">
            <th style="padding:8px 12px;text-align:left;font-weight:600;color:#475569;">Alan</th>
            <th style="padding:8px 12px;text-align:left;font-weight:600;color:#475569;">${y1ref.year}</th>
            <th style="padding:8px 12px;text-align:left;font-weight:600;color:#475569;">${y2ref.year}</th>
          </tr></thead>
          <tbody>${diff.meta.map(metaRowFn).join("")}</tbody>
        </table>
      </div>
    </details>`;

    const ini = diff.initiatives || {}, okr = diff.okr || {}, lnk = diff.links || {};
    const extraChanged = (ini.started_in_y2 || []).length + (ini.ended_before_y2 || []).length;
    const extraBadge = extraChanged > 0
      ? `<span style="margin-left:8px;background:#0ea5e9;color:#fff;border-radius:12px;font-size:11px;padding:1px 8px;">${extraChanged} fark</span>`
      : `<span style="margin-left:8px;background:#e2e8f0;color:#64748b;border-radius:12px;font-size:11px;padding:1px 8px;">Fark yok</span>`;
    const _list = (arr) => (arr && arr.length)
      ? `<ul style="margin:4px 0 0 18px;padding:0;font-size:12.5px;color:#475569;">${arr.map(i => `<li>${esc(i.label)}</li>`).join("")}</ul>`
      : `<span style="font-size:12px;color:#94a3b8;font-style:italic;">—</span>`;

    const html = `<div style="display:flex;align-items:center;gap:10px;padding:12px 16px;border-radius:8px;background:${summaryColor}10;border:1px solid ${summaryColor}30;margin-bottom:16px;flex-wrap:wrap;">
      <i class="fas fa-code-compare" style="color:${summaryColor};font-size:18px;"></i>
      <div>
        <div style="font-size:13px;font-weight:700;color:#1e293b;">${y1ref.year} ↔ ${y2ref.year} Karşılaştırması</div>
        <div style="font-size:12px;color:#475569;margin-top:2px;">${summaryText}</div>
      </div>
    </div>` + metaSection
      + genericSection("Stratejiler", "fas fa-bullseye", diff.strategies, entityRowFn, "Strateji konfigürasyonu yok.")
      + genericSection("Alt Stratejiler", "fas fa-sitemap", diff.sub_strategies, entityRowFn, "Alt strateji konfigürasyonu yok.")
      + `<details ${extraChanged > 0 ? "open" : ""} style="margin-bottom:12px;">
          <summary style="cursor:pointer;padding:10px 12px;background:#f8fafc;border-radius:6px;font-size:13px;font-weight:600;color:#1e293b;list-style:none;display:flex;align-items:center;gap:6px;border:1px solid #e2e8f0;">
            <i class="fas fa-rocket" style="color:#0ea5e9;"></i> Çok Yıllık Stratejik Girişim / OKR / Bağlar ${extraBadge}
          </summary>
          <div style="padding:12px;background:#fff;border:1px solid #e2e8f0;border-radius:0 0 6px 6px;">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;font-size:13px;">
              <div>
                <div style="font-weight:600;color:#0f172a;margin-bottom:6px;">🚀 Stratejik Girişimler</div>
                <div style="color:#64748b;font-size:12px;margin-bottom:8px;">${y1ref.year}: <b>${ini.y1_total||0}</b> · ${y2ref.year}: <b>${ini.y2_total||0}</b> · devam: <b>${ini.continuing||0}</b></div>
                <div style="margin-top:8px;"><b style="color:#065f46;font-size:12px;">${y2ref.year}'de başlayan:</b> ${_list(ini.started_in_y2)}</div>
                <div style="margin-top:8px;"><b style="color:#991b1b;font-size:12px;">${y2ref.year}'den önce biten:</b> ${_list(ini.ended_before_y2)}</div>
              </div>
              <div>
                <div style="font-weight:600;color:#0f172a;margin-bottom:6px;">🎯 OKR Hedefleri</div>
                <div style="color:#64748b;font-size:12px;">${y1ref.year}: <b>${okr.y1_count||0}</b> → ${y2ref.year}: <b>${okr.y2_count||0}</b></div>
                <div style="font-weight:600;color:#0f172a;margin:14px 0 6px;">🔗 Süreç ↔ Alt-Strateji Bağları</div>
                <div style="color:#64748b;font-size:12px;">${y1ref.year}: <b>${lnk.y1_count||0}</b> → ${y2ref.year}: <b>${lnk.y2_count||0}</b></div>
              </div>
            </div>
          </div>
        </details>`;

    resultBox.innerHTML = html;
    resultBox.style.display = "block";
  }

  if (btn) {
    btn.addEventListener("click", async function () {
      const v1 = selY1 ? parseInt(selY1.value, 10) : null;
      const v2 = selY2 ? parseInt(selY2.value, 10) : null;
      if (!v1 || !v2) return;
      if (v1 === v2) {
        Swal.fire({ icon: "warning", title: "Aynı dönem seçildi", text: "Farklı iki dönem seçin.", confirmButtonText: "Tamam" });
        return;
      }
      btn.disabled = true;
      btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Yükleniyor…';
      resultBox.style.display = "none";
      try {
        const data = await (await fetch(`${COMPARE_URL}?y1=${v1}&y2=${v2}`)).json();
        if (data.success) { renderResult(data); }
        else { Swal.fire({ icon: "error", title: "Hata", text: data.message || "Karşılaştırma yapılamadı." }); }
      } catch (e) {
        Swal.fire({ icon: "error", title: "Bağlantı hatası", text: "Sunucuya ulaşılamadı." });
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-magnifying-glass"></i> Karşılaştır';
      }
    });
  }
})();
