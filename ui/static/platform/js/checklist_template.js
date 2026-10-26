/**
 * Kontrol listesi şablonu yönetimi (kurum + yıl bazlı).
 * Sunucu adresleri #ckt-root üzerindeki data-* özniteliklerinden okunur.
 */
(function () {
  "use strict";

  const root = document.getElementById("ckt-root");
  if (!root) return;

  const urls = {
    api: root.dataset.api,
    item: root.dataset.itemUrl,
    itemDelete: root.dataset.itemDeleteUrl,
    reorder: root.dataset.reorderUrl,
    importUrl: root.dataset.importUrl,
    copy: root.dataset.copyUrl,
  };
  let year = parseInt(root.dataset.year, 10) || new Date().getFullYear();
  let years = [year];
  let items = [];

  const $ = (id) => document.getElementById(id);
  const listEl = $("ckt-list");
  const emptyEl = $("ckt-empty");
  const yearSel = $("ckt-year");
  const modal = $("ckt-modal");
  const errEl = $("ckt-err");

  function csrf() {
    const m = document.querySelector('meta[name="csrf-token"]');
    return m ? m.content : "";
  }

  function toast(icon, title) {
    if (typeof Swal === "undefined") return;
    Swal.fire({ toast: true, position: "top-end", icon, title, showConfirmButton: false, timer: 2500 });
  }

  async function call(url, opts) {
    const res = await fetch(url, Object.assign({ credentials: "same-origin", headers: { Accept: "application/json" } }, opts));
    let data = null;
    try { data = await res.json(); } catch (e) { /* JSON olmayan yanıt */ }
    if (!res.ok || !data || !data.success) {
      throw new Error((data && data.message) || t("İşlem tamamlanamadı."));
    }
    return data;
  }

  function post(url, body) {
    return call(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json", "X-CSRFToken": csrf() },
      body: JSON.stringify(body),
    });
  }

  function apply(data) {
    year = data.year;
    years = data.years || [year];
    items = data.items || [];
    render();
  }

  function el(tag, cls, text) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }

  function iconBtn(icon, title, handler, disabled) {
    const b = el("button", "ck-icon-btn");
    b.type = "button";
    b.title = title;
    b.setAttribute("aria-label", title);
    b.innerHTML = `<i class="fas ${icon}"></i>`;
    b.disabled = !!disabled;
    if (!disabled) b.addEventListener("click", handler);
    return b;
  }

  function render() {
    yearSel.innerHTML = "";
    years.forEach((y) => {
      const o = el("option", "", String(y));
      o.value = String(y);
      o.selected = y === year;
      yearSel.appendChild(o);
    });

    listEl.innerHTML = "";
    emptyEl.classList.toggle("ck-hidden", items.length > 0);

    const stageOrder = [];
    const byStage = {};
    items.forEach((it) => {
      if (!byStage[it.stage]) { byStage[it.stage] = []; stageOrder.push(it.stage); }
      byStage[it.stage].push(it);
    });

    stageOrder.forEach((stage) => {
      const box = el("div", "ck-stage");
      const head = el("div", "ck-stage-head");
      head.appendChild(el("span", "", stage));
      head.appendChild(el("span", "ck-stage-count", String(byStage[stage].length) + " " + t("madde")));
      box.appendChild(head);

      let lastGroup = null;
      byStage[stage].forEach((it) => {
        if ((it.item_group || "") !== (lastGroup || "") && it.item_group) {
          box.appendChild(el("div", "ck-group-label", it.item_group));
        }
        lastGroup = it.item_group;
        const idx = items.indexOf(it);
        const row = el("div", "ck-row");
        row.appendChild(el("div", "ck-row-text", it.text));
        const badges = el("div", "ck-badges");
        if (it.period_days) badges.appendChild(el("span", "ck-badge", t("Her") + " " + it.period_days + " " + t("günde bir")));
        if (it.evidence_required) badges.appendChild(el("span", "ck-badge ck-badge-evidence", t("Kanıt zorunlu")));
        row.appendChild(badges);
        const act = el("div", "ck-row-actions");
        act.appendChild(iconBtn("fa-arrow-up", t("Yukarı taşı"), () => move(idx, -1), idx === 0));
        act.appendChild(iconBtn("fa-arrow-down", t("Aşağı taşı"), () => move(idx, 1), idx === items.length - 1));
        act.appendChild(iconBtn("fa-pen", t("Düzenle"), () => openModal(it)));
        act.appendChild(iconBtn("fa-trash", t("Sil"), () => remove(it)));
        row.appendChild(act);
        box.appendChild(row);
      });
      listEl.appendChild(box);
    });

    const stages = $("ckt-stage-list");
    stages.innerHTML = "";
    stageOrder.forEach((s) => { const o = document.createElement("option"); o.value = s; stages.appendChild(o); });
  }

  async function load(y) {
    try {
      apply(await call(urls.api + "?year=" + encodeURIComponent(y)));
    } catch (e) {
      toast("error", e.message);
    }
  }

  async function move(idx, delta) {
    const j = idx + delta;
    if (j < 0 || j >= items.length) return;
    const ids = items.map((i) => i.id);
    [ids[idx], ids[j]] = [ids[j], ids[idx]];
    try {
      apply(await post(urls.reorder, { year, ids }));
    } catch (e) {
      toast("error", e.message);
    }
  }

  async function remove(it) {
    if (typeof Swal !== "undefined") {
      const r = await Swal.fire({
        icon: "warning",
        title: t("Madde silinsin mi?"),
        text: t("Madde şablondan çıkarılır; mevcut projelerdeki kopyaları etkilenmez."),
        showCancelButton: true,
        confirmButtonText: t("Sil"),
        cancelButtonText: t("İptal"),
      });
      if (!r.isConfirmed) return;
    }
    try {
      apply(await post(urls.itemDelete.replace(/0$/, String(it.id)), { year }));
    } catch (e) {
      toast("error", e.message);
    }
  }

  function openModal(it) {
    errEl.classList.add("ck-hidden");
    $("ckt-modal-title").textContent = it ? t("Maddeyi düzenle") : t("Madde ekle");
    $("ckt-f-id").value = it ? String(it.id) : "";
    const lastStage = items.length ? items[items.length - 1].stage : "";
    $("ckt-f-stage").value = it ? it.stage : lastStage;
    $("ckt-f-group").value = it ? it.item_group || "" : "";
    $("ckt-f-text").value = it ? it.text : "";
    $("ckt-f-period").value = it && it.period_days ? String(it.period_days) : "";
    $("ckt-f-evidence").checked = !!(it && it.evidence_required);
    modal.classList.add("open");
    $("ckt-f-text").focus();
  }

  function closeModal() {
    modal.classList.remove("open");
  }

  async function save() {
    errEl.classList.add("ck-hidden");
    const body = {
      year,
      id: $("ckt-f-id").value ? parseInt($("ckt-f-id").value, 10) : null,
      stage: $("ckt-f-stage").value,
      item_group: $("ckt-f-group").value,
      text: $("ckt-f-text").value,
      period_days: $("ckt-f-period").value ? parseInt($("ckt-f-period").value, 10) : null,
      evidence_required: $("ckt-f-evidence").checked,
    };
    try {
      apply(await post(urls.item, body));
      closeModal();
      toast("success", t("Kaydedildi"));
    } catch (e) {
      errEl.textContent = e.message;
      errEl.classList.remove("ck-hidden");
    }
  }

  async function importFile(file) {
    if (!file) return;
    let replace = true;
    if (items.length && typeof Swal !== "undefined") {
      const r = await Swal.fire({
        icon: "question",
        title: t("Mevcut maddeler ne olsun?"),
        text: t("Bu yılın şablonunda zaten madde var."),
        showDenyButton: true,
        showCancelButton: true,
        confirmButtonText: t("Değiştir"),
        denyButtonText: t("Sonuna ekle"),
        cancelButtonText: t("İptal"),
      });
      if (r.isDismissed) { $("ckt-file").value = ""; return; }
      replace = r.isConfirmed;
    }
    const fd = new FormData();
    fd.append("file", file);
    fd.append("year", String(year));
    fd.append("mode", replace ? "replace" : "append");
    try {
      const data = await call(urls.importUrl, { method: "POST", headers: { Accept: "application/json", "X-CSRFToken": csrf() }, body: fd });
      apply(data);
      toast("success", data.imported + " " + t("madde içe aktarıldı"));
    } catch (e) {
      toast("error", e.message);
    } finally {
      $("ckt-file").value = "";
    }
  }

  async function copyFromYear() {
    const others = years.filter((y) => y !== year);
    if (!others.length || typeof openMcFormModal === "undefined") return;
    const options = others.map((y) => `<option value="${y}">${y}</option>`).join("");
    const r = await openMcFormModal({
      title: t("Hangi yıldan kopyalansın?"),
      bodyHtml: `<div class="mc-form-field"><label class="mc-form-label" for="ckt-copy-year">${t("Yıl")}</label>` +
        `<select id="ckt-copy-year" class="mc-form-input">${options}</select></div>`,
      confirmText: t("Kopyala"),
      cancelText: t("İptal"),
      onConfirm: () => ({ year: parseInt(document.getElementById("ckt-copy-year").value, 10) }),
    });
    if (!r) return;
    try {
      const data = await post(urls.copy, { from_year: r.year, to_year: year });
      apply(data);
      toast("success", data.copied + " " + t("madde kopyalandı"));
    } catch (e) {
      toast("error", e.message);
    }
  }

  yearSel.addEventListener("change", () => load(parseInt(yearSel.value, 10)));
  $("ckt-add").addEventListener("click", () => openModal(null));
  $("ckt-save").addEventListener("click", save);
  $("ckt-cancel").addEventListener("click", closeModal);
  $("ckt-modal-close").addEventListener("click", closeModal);
  $("ckt-file").addEventListener("change", (ev) => importFile(ev.target.files[0]));
  $("ckt-copy").addEventListener("click", copyFromYear);

  load(year);
})();
