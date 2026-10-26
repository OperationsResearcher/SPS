/**
 * Proje kontrol listesi sekmesi: çift onay, kanıt, rol ataması, kilitli kapanış.
 * Sunucu adresleri #ckp-root üzerindeki data-* özniteliklerinden okunur.
 */
(function () {
  "use strict";

  const root = document.getElementById("ckp-root");
  if (!root) return;

  const api = root.dataset.api;
  const urls = {
    complete: root.dataset.completeUrl,
    reopenProject: root.dataset.reopenProjectUrl,
    assign: root.dataset.assignUrl,
    add: root.dataset.addUrl,
  };
  let state = null;
  const selected = new Set();
  const $ = (id) => document.getElementById(id);

  function csrf() {
    const m = document.querySelector('meta[name="csrf-token"]');
    return m ? m.content : "";
  }

  function toast(icon, title) {
    if (typeof Swal === "undefined") return;
    Swal.fire({ toast: true, position: "top-end", icon, title, showConfirmButton: false, timer: 2500 });
  }

  async function request(url, opts) {
    const res = await fetch(url, Object.assign({ credentials: "same-origin", headers: { Accept: "application/json" } }, opts));
    let data = null;
    try { data = await res.json(); } catch (e) { /* JSON olmayan yanıt */ }
    if (!res.ok || !data || !data.success) throw new Error((data && data.message) || t("İşlem tamamlanamadı."));
    return data;
  }

  function post(url, body, formData) {
    const headers = { Accept: "application/json", "X-CSRFToken": csrf() };
    if (!formData) headers["Content-Type"] = "application/json";
    return request(url, { method: "POST", headers, body: formData || JSON.stringify(body || {}) });
  }

  async function act(url, body, okMsg, formData) {
    try {
      state = await post(url, body, formData);
      render();
      if (okMsg) toast("success", okMsg);
      return true;
    } catch (e) {
      toast("error", e.message);
      return false;
    }
  }

  function el(tag, cls, text) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined && text !== null) n.textContent = text;
    return n;
  }

  function btn(label, icon, cls, handler) {
    const b = el("button", "mc-btn mc-btn-sm " + cls);
    b.type = "button";
    b.innerHTML = `<i class="fas ${icon}"></i> `;
    b.appendChild(document.createTextNode(label));
    b.addEventListener("click", handler);
    return b;
  }

  function confirmDialog(title, text, confirmText) {
    if (typeof Swal === "undefined") return Promise.resolve(true);
    return Swal.fire({
      icon: "warning", title, text, showCancelButton: true,
      confirmButtonText: confirmText, cancelButtonText: t("İptal"),
    }).then((r) => r.isConfirmed);
  }

  // ── Üst bölüm: ilerleme, kilit, rol atamaları ───────────────────────────
  function renderHeader() {
    const p = state.progress;
    $("ckp-bar").style.width = p.pct + "%";
    $("ckp-bar-text").textContent = `%${p.pct} · ${p.approved}/${p.total} ${t("onaylı")} · ${p.done} ${t("onay bekliyor")}`;

    const chips = $("ckp-stage-chips");
    chips.innerHTML = "";
    p.stages.forEach((s) => {
      const c = el("button", "ck-chip", `${s.stage} ${s.approved}/${s.total}`);
      c.type = "button";
      if (s.approved === s.total) c.classList.add("ck-chip-done");
      c.addEventListener("click", () => { $("ckp-f-stage").value = s.stage; renderList(); });
      chips.appendChild(c);
    });

    const done = !!state.project.completed_at;
    const lock = $("ckp-lock");
    lock.classList.toggle("ck-hidden", !done);
    if (done) {
      lock.textContent = `${t("Proje tamamlandı")} (${state.project.completed_at}${state.project.completed_by ? " · " + state.project.completed_by : ""}). ${t("Kontrol listesi kilitli.")}`;
    }
    $("ckp-complete").classList.toggle("ck-hidden", !(state.can_manage && !done));
    $("ckp-complete").disabled = !state.completion.can_complete;
    $("ckp-complete").title = state.completion.can_complete
      ? ""
      : `${state.completion.remaining} ${t("madde onay bekliyor")}`;
    $("ckp-reopen-project").classList.toggle("ck-hidden", !(state.can_manage && done));
    $("ckp-add").classList.toggle("ck-hidden", !(state.can_manage && !done));
  }

  // ── Madde listesi ───────────────────────────────────────────────────────
  function fillStageFilter() {
    const sel = $("ckp-f-stage");
    const cur = sel.value;
    sel.innerHTML = "";
    const o0 = el("option", "", t("Tüm aşamalar"));
    o0.value = "";
    sel.appendChild(o0);
    state.progress.stages.forEach((s) => {
      const o = el("option", "", s.stage);
      o.value = s.stage;
      sel.appendChild(o);
    });
    sel.value = state.progress.stages.some((s) => s.stage === cur) ? cur : "";
  }

  function statusBadge(it) {
    const cls = it.status === "Onaylandı" ? "ck-st-approved" : it.status === "Yapıldı" ? "ck-st-done" : "ck-st-pending";
    const label = it.status === "Yapıldı" ? t("Onay bekliyor") : it.status === "Onaylandı" ? t("Onaylandı") : t("Bekliyor");
    return el("span", "ck-status " + cls, label);
  }

  function renderItem(it, locked) {
    const row = el("div", "ck-item");
    const main = el("div", "ck-item-main");
    main.appendChild(statusBadge(it));
    main.appendChild(el("div", "ck-item-text", it.text));

    const meta = el("div", "ck-item-meta");
    if (it.assignments.length) {
      meta.appendChild(el("span", "", t("Sorumlu") + ":"));
      it.assignments.forEach((a) => {
        const icon = a.type === "process" ? "fa-diagram-project" : a.type === "project" ? "fa-people-group" : "fa-user";
        const chip = el("span", "ck-badge ck-badge-" + a.type);
        chip.innerHTML = `<i class="fas ${icon}"></i> `;
        chip.appendChild(document.createTextNode(a.type === "project" ? t("Proje ekibi") : a.label));
        meta.appendChild(chip);
      });
    } else {
      meta.appendChild(el("span", "ck-unassigned", `${t("Sorumlu")}: ${t("atanmadı")}`));
    }
    if (it.period_days) meta.appendChild(el("span", "ck-badge", `${t("Her")} ${it.period_days} ${t("günde bir")}`));
    if (it.evidence_required) meta.appendChild(el("span", "ck-badge ck-badge-evidence", t("Kanıt zorunlu")));
    if (it.done_by) meta.appendChild(el("span", "", `${t("Yapan")}: ${it.done_by} (${it.done_at})`));
    if (it.approved_by) meta.appendChild(el("span", "", `${t("Onaylayan")}: ${it.approved_by} (${it.approved_at})`));
    main.appendChild(meta);

    if (it.evidences.length) {
      const evs = el("div", "ck-evidences");
      it.evidences.forEach((ev) => {
        const a = el("a", "ck-evidence", ev.title);
        a.href = ev.kind === "link" ? ev.url : ev.download_url;
        a.target = "_blank";
        a.rel = "noopener noreferrer";
        a.title = [ev.uploader, ev.created_at].filter(Boolean).join(" · ");
        const icon = el("i", "fas " + (ev.kind === "link" ? "fa-link" : "fa-paperclip"));
        a.prepend(icon, " ");
        evs.appendChild(a);
        if (it.can_edit_evidence && !locked) {
          const x = el("button", "ck-icon-btn", "✕");
          x.type = "button";
          x.title = t("Kanıtı sil");
          x.setAttribute("aria-label", t("Kanıtı sil"));
          x.addEventListener("click", async () => {
            if (await confirmDialog(t("Kanıt silinsin mi?"), "", t("Sil")))
              act(`${api}/evidence/${ev.id}/delete`, {}, t("Kanıt silindi"));
          });
          evs.appendChild(x);
        }
      });
      main.appendChild(evs);
    }
    if (it.note) main.appendChild(el("div", "ck-note", it.note));
    const left = el("div", "ck-item-left");
    if (state.can_manage && !locked) {
      const cb = el("input", "ck-select");
      cb.type = "checkbox";
      cb.checked = selected.has(it.id);
      cb.setAttribute("aria-label", t("Seç"));
      cb.addEventListener("change", () => {
        if (cb.checked) selected.add(it.id); else selected.delete(it.id);
        updateSelection();
      });
      left.appendChild(cb);
    }
    left.appendChild(main);
    row.appendChild(left);

    const actions = el("div", "ck-item-actions");
    if (!locked) {
      if (it.can_done) actions.appendChild(btn(t("Yapıldı"), "fa-check", "mc-btn-secondary", () =>
        act(`${api}/item/${it.id}/done`, {}, t("İşaretlendi; onay bekliyor"))));
      if (it.can_approve) actions.appendChild(btn(t("Onayla"), "fa-check-double", "mc-btn-primary", () =>
        act(`${api}/item/${it.id}/approve`, {}, t("Onaylandı"))));
      if (it.can_reopen) actions.appendChild(btn(t("Geri al"), "fa-rotate-left", "mc-btn-secondary", async () => {
        if (await confirmDialog(t("Madde geri alınsın mı?"), t("Madde 'Bekliyor' durumuna döner."), t("Geri al")))
          act(`${api}/item/${it.id}/reopen`, {}, t("Geri alındı"));
      }));
      if (it.can_edit_evidence) {
        actions.appendChild(btn(t("Kanıt"), "fa-paperclip", "mc-btn-secondary", () => openEvidence(it)));
        actions.appendChild(btn(t("Not"), "fa-note-sticky", "mc-btn-secondary", () => editNote(it)));
      }
      if (state.can_manage) {
        actions.appendChild(btn(t("Ata"), "fa-user-plus", "mc-btn-secondary", () => openAssign([it.id])));
        actions.appendChild(btn("", "fa-pen", "mc-btn-secondary", () => openModal(it)));
        actions.appendChild(btn("", "fa-trash", "mc-btn-secondary", async () => {
          if (await confirmDialog(t("Madde projeden çıkarılsın mı?"), t("Bu işlem kayıt altına alınır."), t("Çıkar")))
            act(`${api}/item/${it.id}/delete`, {}, t("Madde çıkarıldı"));
        }));
      }
    }
    row.appendChild(actions);
    return row;
  }

  function renderList() {
    const fStatus = $("ckp-f-status").value;
    const fStage = $("ckp-f-stage").value;
    const mine = $("ckp-f-mine").checked;
    const locked = !!state.project.completed_at;
    const listEl = $("ckp-list");
    listEl.innerHTML = "";
    $("ckp-empty").classList.toggle("ck-hidden", state.items.length > 0);
    $("ckp-select-all-wrap").classList.toggle("ck-hidden", !(state.can_manage && !locked && state.items.length));

    const order = [];
    const by = {};
    state.items.forEach((it) => {
      if (fStatus && it.status !== fStatus) return;
      if (fStage && it.stage !== fStage) return;
      if (mine && !it.mine) return;
      if (!by[it.stage]) { by[it.stage] = []; order.push(it.stage); }
      by[it.stage].push(it);
    });
    order.forEach((stage) => {
      const box = el("div", "ck-stage");
      const head = el("div", "ck-stage-head");
      head.appendChild(el("span", "", stage));
      const total = state.items.filter((i) => i.stage === stage);
      head.appendChild(el("span", "ck-stage-count", `${total.filter((i) => i.status === "Onaylandı").length}/${total.length}`));
      box.appendChild(head);
      let lastGroup = null;
      by[stage].forEach((it) => {
        if (it.item_group && it.item_group !== lastGroup) box.appendChild(el("div", "ck-group-label", it.item_group));
        lastGroup = it.item_group;
        box.appendChild(renderItem(it, locked));
      });
      listEl.appendChild(box);
    });
  }

  function render() {
    renderHeader();
    fillStageFilter();
    renderList();
    const stages = $("ckp-stage-list");
    stages.innerHTML = "";
    state.progress.stages.forEach((s) => { const o = document.createElement("option"); o.value = s.stage; stages.appendChild(o); });
  }

  // ── Atama: kişi / süreç (tüm üyeleri) / proje ekibi ─────────────────────
  function escHtml(v) {
    return String(v == null ? "" : v).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function updateSelection() {
    const n = selected.size;
    $("ckp-sel-count").textContent = String(n);
    $("ckp-assign-selected").classList.toggle("ck-hidden", n === 0);
  }

  function checkList(kind, rows, current) {
    return rows.map((r) =>
      `<label class="ck-as-row" data-q="${escHtml(r.name.toLowerCase())}"><input type="checkbox" class="ck-as-${kind}" value="${r.id}"${current.has(r.id) ? " checked" : ""}> <span>${escHtml(r.name)}</span></label>`
    ).join("");
  }

  async function openAssign(ids) {
    if (!ids.length || typeof openMcFormModal === "undefined") return;
    const single = ids.length === 1 ? state.items.find((i) => i.id === ids[0]) : null;
    const cur = { user: new Set(), process: new Set(), project: false };
    if (single) {
      single.assignments.forEach((a) => {
        if (a.type === "project") cur.project = true; else cur[a.type].add(a.id);
      });
    }
    const body =
      `<p class="ck-hint">${escHtml(t("Seçtiğiniz kişi, süreç (tüm üyeleri) veya proje ekibi bu maddelerden sorumlu olur."))}</p>` +
      `<label class="ck-as-team"><input type="checkbox" id="ck-as-project"${cur.project ? " checked" : ""}> <span><b>${escHtml(t("Proje ekibi"))}</b> (${state.project.team_size} ${escHtml(t("kişi"))})</span></label>` +
      `<div class="ck-as-title">${escHtml(t("Süreçler"))} <small>${escHtml(t("(seçilen sürecin tüm üyeleri)"))}</small></div>` +
      `<input type="search" class="mc-form-input ck-as-filter" data-target="ck-as-processes" placeholder="${escHtml(t("Süreç ara…"))}">` +
      `<div class="ck-as-list" id="ck-as-processes">${checkList("process", state.processes, cur.process)}</div>` +
      `<div class="ck-as-title">${escHtml(t("Kullanıcılar"))}</div>` +
      `<input type="search" class="mc-form-input ck-as-filter" data-target="ck-as-users" placeholder="${escHtml(t("Kişi ara…"))}">` +
      `<div class="ck-as-list" id="ck-as-users">${checkList("user", state.users, cur.user)}</div>` +
      (ids.length > 1
        ? `<div class="ck-as-mode"><label><input type="radio" name="ck-as-mode" value="replace" checked> ${escHtml(t("Mevcut atamaların yerine koy"))}</label>` +
          `<label><input type="radio" name="ck-as-mode" value="add"> ${escHtml(t("Mevcutlara ekle"))}</label></div>`
        : "");
    const r = await openMcFormModal({
      title: ids.length > 1 ? `${t("Atama")} (${ids.length} ${t("madde")})` : t("Atama"),
      bodyHtml: body,
      confirmText: t("Ata"),
      cancelText: t("İptal"),
      onConfirm: () => {
        const targets = [];
        if (document.getElementById("ck-as-project").checked) targets.push({ type: "project", id: 0 });
        document.querySelectorAll(".ck-as-process:checked").forEach((c) => targets.push({ type: "process", id: parseInt(c.value, 10) }));
        document.querySelectorAll(".ck-as-user:checked").forEach((c) => targets.push({ type: "user", id: parseInt(c.value, 10) }));
        const mode = document.querySelector('input[name="ck-as-mode"]:checked');
        return { targets, mode: mode ? mode.value : "replace" };
      },
    });
    if (!r) return;
    const ok = await act(urls.assign, { item_ids: ids, targets: r.targets, mode: r.mode }, t("Atama kaydedildi"));
    if (ok) { selected.clear(); updateSelection(); renderList(); }
  }

  document.addEventListener("input", (ev) => {
    const f = ev.target.closest && ev.target.closest(".ck-as-filter");
    if (!f) return;
    const q = f.value.trim().toLowerCase();
    document.querySelectorAll(`#${f.dataset.target} .ck-as-row`).forEach((row) => {
      row.classList.toggle("ck-hidden", !!q && !row.dataset.q.includes(q));
    });
  });

  // ── Madde ekle / düzenle ────────────────────────────────────────────────
  function openModal(it) {
    $("ckp-err").classList.add("ck-hidden");
    $("ckp-modal-title").textContent = it ? t("Maddeyi düzenle") : t("Madde ekle");
    $("ckp-f-id").value = it ? String(it.id) : "";
    $("ckp-m-stage").value = it ? it.stage : "";
    $("ckp-m-group").value = it ? it.item_group || "" : "";
    $("ckp-m-text").value = it ? it.text : "";
    $("ckp-m-period").value = it && it.period_days ? String(it.period_days) : "";
    $("ckp-m-evidence").checked = !!(it && it.evidence_required);
    $("ckp-modal").classList.add("open");
    $("ckp-m-text").focus();
  }

  async function saveItem() {
    const id = $("ckp-f-id").value;
    const body = {
      stage: $("ckp-m-stage").value,
      item_group: $("ckp-m-group").value,
      text: $("ckp-m-text").value,
      period_days: $("ckp-m-period").value ? parseInt($("ckp-m-period").value, 10) : null,
      evidence_required: $("ckp-m-evidence").checked,
    };
    try {
      state = await post(id ? `${api}/item/${id}/update` : urls.add, body);
      $("ckp-modal").classList.remove("open");
      render();
      toast("success", t("Kaydedildi"));
    } catch (e) {
      $("ckp-err").textContent = e.message;
      $("ckp-err").classList.remove("ck-hidden");
    }
  }

  // ── Kanıt ve not ────────────────────────────────────────────────────────
  function openEvidence(it) {
    $("ckp-ev-err").classList.add("ck-hidden");
    $("ckp-ev-item").value = String(it.id);
    $("ckp-ev-title").value = "";
    $("ckp-ev-file").value = "";
    $("ckp-ev-url").value = "";
    $("ckp-ev-modal").classList.add("open");
  }

  async function saveEvidence() {
    const id = $("ckp-ev-item").value;
    const file = $("ckp-ev-file").files[0];
    const url = $("ckp-ev-url").value.trim();
    if (!file && !url) {
      $("ckp-ev-err").textContent = t("Bir dosya seçin veya bağlantı girin.");
      $("ckp-ev-err").classList.remove("ck-hidden");
      return;
    }
    try {
      if (file) {
        const fd = new FormData();
        fd.append("file", file);
        fd.append("title", $("ckp-ev-title").value);
        state = await post(`${api}/item/${id}/evidence`, null, fd);
      } else {
        state = await post(`${api}/item/${id}/evidence`, { url, title: $("ckp-ev-title").value });
      }
      $("ckp-ev-modal").classList.remove("open");
      render();
      toast("success", t("Kanıt eklendi"));
    } catch (e) {
      $("ckp-ev-err").textContent = e.message;
      $("ckp-ev-err").classList.remove("ck-hidden");
    }
  }

  async function editNote(it) {
    const value = await openMcTextPrompt({
      title: t("Not"),
      textarea: true,
      value: it.note || "",
      confirmText: t("Kaydet"),
      cancelText: t("İptal"),
    });
    if (value !== null) act(`${api}/item/${it.id}/note`, { note: value }, t("Kaydedildi"));
  }

  // ── Proje kapanışı ──────────────────────────────────────────────────────
  async function completeProject() {
    if (await confirmDialog(t("Proje tamamlansın mı?"), t("Tüm maddeler onaylı. Proje tamamlandı olarak işaretlenir ve liste kilitlenir."), t("Tamamla")))
      act(urls.complete, {}, t("Proje tamamlandı"));
  }

  async function reopenProject() {
    if (await confirmDialog(t("Proje yeniden açılsın mı?"), t("Kontrol listesi tekrar düzenlenebilir olur."), t("Yeniden aç")))
      act(urls.reopenProject, {}, t("Proje yeniden açıldı"));
  }

  ["ckp-f-status", "ckp-f-stage", "ckp-f-mine"].forEach((id) => $(id).addEventListener("change", () => state && renderList()));
  $("ckp-add").addEventListener("click", () => openModal(null));
  $("ckp-assign-selected").addEventListener("click", () => openAssign(Array.from(selected)));
  $("ckp-select-all").addEventListener("change", (ev) => {
    document.querySelectorAll(".ck-select").forEach((cb) => { cb.checked = ev.target.checked; cb.dispatchEvent(new Event("change")); });
  });
  $("ckp-save").addEventListener("click", saveItem);
  $("ckp-cancel").addEventListener("click", () => $("ckp-modal").classList.remove("open"));
  $("ckp-modal-close").addEventListener("click", () => $("ckp-modal").classList.remove("open"));
  $("ckp-ev-save").addEventListener("click", saveEvidence);
  $("ckp-ev-cancel").addEventListener("click", () => $("ckp-ev-modal").classList.remove("open"));
  $("ckp-ev-close").addEventListener("click", () => $("ckp-ev-modal").classList.remove("open"));
  $("ckp-complete").addEventListener("click", completeProject);
  $("ckp-reopen-project").addEventListener("click", reopenProject);

  request(api).then((d) => { state = d; render(); }).catch((e) => toast("error", e.message));
})();
