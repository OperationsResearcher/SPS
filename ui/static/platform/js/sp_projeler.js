/* SP Projeler — sp_projeler.js */
"use strict";

(function () {
  const ROOT = document.getElementById("sp-projeler");
  if (!ROOT) return;

  const CAN_MANAGE     = ROOT.dataset.canManage === "true";
  const PROJE_URL      = ROOT.dataset.projeUrl;
  const PROJE_SAVE_URL = ROOT.dataset.projeSaveUrl;
  const PROJE_DEL_BASE = ROOT.dataset.projeDeleteBase;
  // Görev uçları sunucudan gelir — eskiden PROJE_SAVE_URL üzerinde string
  // ikamesiyle türetiliyordu ve Faz 3 taşımasından sonra YANLIŞ URL üretiyordu
  // ("/proje" artık URL'de yok → replace sessizce çalışmadı). TASK-277.
  const GOREV_BASE     = ROOT.dataset.gorevBase;        // …/project/0/task  (0 = yer tutucu)

  let projects = [];
  let tasksCache = {}; // project_id → tasks[]

  // ── Yardımcılar ─────────────────────────────────────────────────────────────
  function apiFetch(url, opts) {
    return fetch(url, {
      headers: { "Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest" },
      ...opts,
    }).then(r => r.json());
  }

  function toast(msg, type) {
    if (window.Swal) {
      Swal.fire({ toast: true, position: "top-end", icon: type || "success",
        title: msg, showConfirmButton: false, timer: 2500, timerProgressBar: true });
    }
  }

  function escHtml(s) {
    return String(s || "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
  }

  function openModal(id)  { document.getElementById(id)?.classList.add("active"); }
  function closeModal(id) { document.getElementById(id)?.classList.remove("active"); }

  document.querySelectorAll(".mc-modal-close, [data-modal]").forEach(el => {
    el.addEventListener("click", () => {
      const id = el.dataset.modal || el.closest(".mc-modal-overlay")?.id;
      if (id) closeModal(id);
    });
  });

  // ── Proje Listesi ────────────────────────────────────────────────────────────
  function loadProjects() {
    apiFetch(PROJE_URL).then(d => {
      if (!d.success) return;
      projects = d.items || [];
      renderProjects();
    });
  }

  const STATUS_COLORS = {
    "Planlandı": "#6366f1",
    "Devam Ediyor": "#f59e0b",
    "Tamamlandı": "#10b981",
    "İptal": "#ef4444",
    "Beklemede": "#9ca3af",
  };

  function renderProjects() {
    const list = document.getElementById("proje-list");
    const empty = document.getElementById("proje-empty");
    if (!list) return;
    list.innerHTML = "";
    if (!projects.length) { empty && (empty.style.display = ""); return; }
    empty && (empty.style.display = "none");

    projects.forEach(p => {
      const color = STATUS_COLORS[p.status] || "#6b7280";
      const progressPct = Math.min(100, Math.max(0, p.progress || 0));
      const card = document.createElement("div");
      card.className = "sp-proje-card";
      card.dataset.id = p.id;
      card.innerHTML = `
        <div class="sp-proje-card-header" style="border-left:4px solid ${color}">
          <div class="sp-proje-card-title">${escHtml(p.name)}</div>
          <div class="sp-proje-card-actions">
            ${CAN_MANAGE ? `<button class="mc-btn mc-btn-ghost mc-btn-xs btn-proje-edit" data-id="${p.id}" title="${t("Düzenle")}">✎</button>
            <button class="mc-btn mc-btn-ghost mc-btn-xs btn-proje-delete" data-id="${p.id}" title="${t("Sil")}">✕</button>` : ""}
          </div>
        </div>
        <div class="sp-proje-card-body">
          ${p.description ? `<p class="sp-proje-desc">${escHtml(p.description)}</p>` : ""}
          <div class="sp-proje-meta">
            <span class="mc-badge" style="background:${color}22;color:${color};border:1px solid ${color}55">${escHtml(p.status)}</span>
            ${p.start_date ? `<span class="mc-text-xs mc-text-muted">${p.start_date}${p.end_date ? " → "+p.end_date : ""}</span>` : ""}
          </div>
          <div class="sp-proje-progress-wrap">
            <div class="sp-proje-progress-bar" style="background:${color};width:${progressPct}%"></div>
          </div>
          <div class="sp-proje-progress-label">${progressPct}% ${t("tamamlandı")}</div>
        </div>
        <div class="sp-proje-card-footer">
          <button class="mc-btn mc-btn-ghost mc-btn-xs btn-gorev-toggle" data-id="${p.id}">
            <i class="fas fa-tasks"></i> ${t("Görevler")} <span class="gorev-count" id="gorev-count-${p.id}"></span>
          </button>
          ${CAN_MANAGE ? `<button class="mc-btn mc-btn-ghost mc-btn-xs btn-gorev-add" data-project-id="${p.id}">+ ${t("Görev Ekle")}</button>` : ""}
        </div>
        <div class="sp-gorev-list" id="gorev-list-${p.id}" style="display:none;"></div>
      `;
      list.appendChild(card);
    });

    bindProjectActions();
  }

  function bindProjectActions() {
    document.querySelectorAll(".btn-proje-edit").forEach(btn => {
      btn.addEventListener("click", () => {
        const p = projects.find(x => x.id == btn.dataset.id);
        if (p) openProjeModal(p);
      });
    });

    document.querySelectorAll(".btn-proje-delete").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = btn.dataset.id;
        if (!window.Swal) { if (!confirm(t("Silinsin mi?"))) return; deleteProject(id); return; }
        Swal.fire({ title: t("Proje silinsin mi?"), text: t("Görevleri de silinecek."), icon: "warning",
          showCancelButton: true, confirmButtonText: t("Evet, Sil"), cancelButtonText: t("İptal"),
          confirmButtonColor: "#ef4444" }).then(r => { if (r.isConfirmed) deleteProject(id); });
      });
    });

    document.querySelectorAll(".btn-gorev-toggle").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = btn.dataset.id;
        const listEl = document.getElementById("gorev-list-" + id);
        if (!listEl) return;
        if (listEl.style.display === "none") {
          listEl.style.display = "";
          loadTasks(id);
        } else {
          listEl.style.display = "none";
        }
      });
    });

    document.querySelectorAll(".btn-gorev-add").forEach(btn => {
      btn.addEventListener("click", () => openGorevModal(btn.dataset.projectId, null));
    });
  }

  function deleteProject(id) {
    fetch(PROJE_DEL_BASE + id, {
      method: "DELETE", headers: { "X-Requested-With": "XMLHttpRequest" }
    }).then(r => r.json()).then(d => {
      if (d.success) { toast(t("Proje silindi.")); loadProjects(); }
      else toast(d.message || t("Hata."), "error");
    });
  }

  // ── Proje Modal ──────────────────────────────────────────────────────────────
  document.getElementById("btn-proje-add")?.addEventListener("click", () => openProjeModal(null));

  function openProjeModal(p) {
    document.getElementById("modal-proje-title").textContent = p ? t("Proje Düzenle") : t("Proje Ekle");
    document.getElementById("proje-edit-id").value     = p?.id || "";
    document.getElementById("proje-edit-name").value   = p?.name || "";
    document.getElementById("proje-edit-desc").value   = p?.description || "";
    document.getElementById("proje-edit-status").value = p?.status || "Planlandı";
    document.getElementById("proje-edit-start").value  = p?.start_date || "";
    document.getElementById("proje-edit-end").value    = p?.end_date || "";
    document.getElementById("proje-edit-progress").value = p?.progress ?? 0;
    openModal("modal-proje-edit");
  }

  document.getElementById("btn-proje-save")?.addEventListener("click", () => {
    const id   = document.getElementById("proje-edit-id").value;
    const name = document.getElementById("proje-edit-name").value.trim();
    if (!name) { toast(t("Proje adı zorunludur."), "warning"); return; }
    const body = {
      name,
      description: document.getElementById("proje-edit-desc").value.trim(),
      status:      document.getElementById("proje-edit-status").value,
      start_date:  document.getElementById("proje-edit-start").value || null,
      end_date:    document.getElementById("proje-edit-end").value || null,
      progress:    parseInt(document.getElementById("proje-edit-progress").value) || 0,
    };
    if (id) body.id = parseInt(id);
    apiFetch(PROJE_SAVE_URL, { method: "POST", body: JSON.stringify(body) }).then(d => {
      closeModal("modal-proje-edit");
      if (d.success) { toast(t("Proje kaydedildi.")); loadProjects(); }
      else toast(d.message || t("Hata."), "error");
    });
  });

  // ── Görevler ─────────────────────────────────────────────────────────────────
  // GOREV_BASE = …/project/0/task — yer tutucu 0'ı gerçek proje id'siyle değiştir.
  function getGorevUrl(projectId) {
    return GOREV_BASE.replace("/0/task", "/" + projectId + "/task");
  }

  function loadTasks(projectId) {
    const url = getGorevUrl(projectId);
    apiFetch(url).then(d => {
      if (!d.success) return;
      tasksCache[projectId] = d.items || [];
      renderTasks(projectId);
      const countEl = document.getElementById("gorev-count-" + projectId);
      if (countEl) countEl.textContent = d.items.length ? `(${d.items.length})` : "";
    });
  }

  function renderTasks(projectId) {
    const listEl = document.getElementById("gorev-list-" + projectId);
    if (!listEl) return;
    const tasks = tasksCache[projectId] || [];
    listEl.innerHTML = "";
    if (!tasks.length) {
      listEl.innerHTML = `<div class="mc-text-muted mc-text-sm mc-p-2">${t("Henüz görev yok.")}</div>`;
      return;
    }
    tasks.forEach(t => {
      const row = document.createElement("div");
      row.className = "sp-gorev-row";
      row.innerHTML = `
        <span class="sp-gorev-status-dot" data-status="${escHtml(t.status)}"></span>
        <span class="sp-gorev-name">${escHtml(t.name)}</span>
        ${t.end_date ? `<span class="mc-text-xs mc-text-muted">${t.end_date}</span>` : ""}
        ${CAN_MANAGE ? `<button class="mc-btn mc-btn-ghost mc-btn-xs btn-gorev-edit" data-id="${t.id}" data-project-id="${projectId}" style="margin-left:auto">✎</button>` : ""}
      `;
      listEl.appendChild(row);
    });

    if (CAN_MANAGE) {
      listEl.querySelectorAll(".btn-gorev-edit").forEach(btn => {
        btn.addEventListener("click", () => {
          const pid = btn.dataset.projectId;
          const task = (tasksCache[pid] || []).find(x => x.id == btn.dataset.id);
          if (task) openGorevModal(pid, task);
        });
      });
    }
  }

  function openGorevModal(projectId, task) {
    document.getElementById("modal-gorev-title").textContent = task ? t("Görevi Düzenle") : t("Görev Ekle");
    document.getElementById("gorev-edit-project-id").value = projectId;
    document.getElementById("gorev-edit-id").value    = task?.id || "";
    document.getElementById("gorev-edit-name").value  = task?.name || "";
    document.getElementById("gorev-edit-desc").value  = task?.description || "";
    document.getElementById("gorev-edit-status").value = task?.status || "Planlandı";
    document.getElementById("gorev-edit-start").value = task?.start_date || "";
    document.getElementById("gorev-edit-end").value   = task?.end_date || "";
    openModal("modal-gorev-edit");
  }

  document.getElementById("btn-gorev-save")?.addEventListener("click", () => {
    const projectId = document.getElementById("gorev-edit-project-id").value;
    const id   = document.getElementById("gorev-edit-id").value;
    const name = document.getElementById("gorev-edit-name").value.trim();
    if (!name) { toast(t("Görev adı zorunludur."), "warning"); return; }
    const saveUrl = getGorevUrl(projectId);
    const body = {
      name,
      description: document.getElementById("gorev-edit-desc").value.trim(),
      status:      document.getElementById("gorev-edit-status").value,
      start_date:  document.getElementById("gorev-edit-start").value || null,
      end_date:    document.getElementById("gorev-edit-end").value || null,
    };
    if (id) body.id = parseInt(id);
    apiFetch(saveUrl, { method: "POST", body: JSON.stringify(body) }).then(d => {
      closeModal("modal-gorev-edit");
      if (d.success) { toast(t("Görev kaydedildi.")); loadTasks(projectId); }
      else toast(d.message || t("Hata."), "error");
    });
  });

  // ── Başlat ───────────────────────────────────────────────────────────────────
  loadProjects();

})();
