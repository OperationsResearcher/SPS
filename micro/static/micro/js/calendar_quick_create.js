/**
 * Kurum / Masaüstü takvimi: boş güne tıklama, aralık seçimi, hızlı oluşturma modalları.
 * KokpitimCalendarQuickCreate.boot({ root, calendarId, loadingId })
 */
(function (global) {
  "use strict";

  function boot(opts) {
    const root =
      typeof opts.root === "string" ? document.getElementById(opts.root) : opts.root;
    if (!root) return;
    const calEl = document.getElementById(opts.calendarId);
    const loadingEl = opts.loadingId ? document.getElementById(opts.loadingId) : null;
    if (!calEl || typeof FullCalendar === "undefined") return;

    const currentUserId = parseInt(root.dataset.currentUserId || "0", 10) || 0;
    const eventsUrl = root.dataset.eventsUrl || root.dataset.calendarEventsUrl;
    const metaUrl = root.dataset.metaUrl;
    const activityAddUrl = root.dataset.activityAddUrl;
    const faaliyetAddUrl = root.dataset.faaliyetAddUrl;
    const taskQuickUrl = root.dataset.taskQuickUrl;
    if (!eventsUrl || !metaUrl || !activityAddUrl || !faaliyetAddUrl || !taskQuickUrl) return;

    function getCsrf() {
      const m = document.querySelector('meta[name="csrf-token"]');
      return m ? m.content : "";
    }

    function escHtml(str) {
      if (!str) return "";
      return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }

    let metaCache = null;
    async function loadMeta() {
      if (metaCache) return metaCache;
      const res = await fetch(metaUrl, { credentials: "same-origin", headers: { Accept: "application/json" } });
      const data = await res.json();
      if (!res.ok || !data.success) throw new Error(data.message || "Meta yüklenemedi");
      metaCache = data;
      return data;
    }

    let activityMetaCache = { processId: null, data: null };

    function activityMetaUrl(pid) {
      return `/api/calendar/process/${pid}/activity-form-meta`;
    }

    const backdrop = document.getElementById("cal-quick-backdrop");
    const modal = document.getElementById("cal-quick-modal");
    if (!backdrop || !modal) return;

    const headIcon = document.getElementById("cal-quick-head-icon");
    const stepType = document.getElementById("cal-quick-step-type");
    const stepForm = document.getElementById("cal-quick-step-form");
    const datesEl = document.getElementById("cal-quick-dates");
    const formDatesRecap = document.getElementById("cal-quick-form-dates-recap");
    const errEl = document.getElementById("cal-quick-err");
    const modalTitle = document.getElementById("cal-quick-title");
    const modalBadge = document.getElementById("cal-quick-badge");
    const optProcess = document.getElementById("cal-opt-process");
    const optProject = document.getElementById("cal-opt-project");
    const optSelf = document.getElementById("cal-opt-self");
    const btnClose = document.getElementById("cal-quick-close");
    const btnBack = document.getElementById("cal-quick-back");
    const btnSubmit = document.getElementById("cal-quick-submit");

    const formProcess = document.getElementById("cal-form-process");
    const formProject = document.getElementById("cal-form-project");
    const formSelf = document.getElementById("cal-form-self");

    const selectProcess = document.getElementById("cal-select-process");
    const actMetaLoading = document.getElementById("cal-act-meta-loading");
    const actMetaHint = document.getElementById("cal-act-meta-hint");
    const actMetaBox = document.getElementById("cal-act-meta-box");

    let rangeStart = null;
    let rangeEndIncl = null;
    let formMode = null;
    let calendar = null;

    const MODAL_CLASSES = ["cal-modal--process", "cal-modal--project", "cal-modal--self"];

    function clearModalVariant() {
      MODAL_CLASSES.forEach((c) => modal.classList.remove(c));
    }

    function fmtTr(d) {
      try {
        return d.toLocaleDateString("tr-TR", { weekday: "short", day: "numeric", month: "long", year: "numeric" });
      } catch (e) {
        return String(d);
      }
    }

    function dateRangeRecap() {
      if (rangeStart === rangeEndIncl) return "Takvim seçimi: " + fmtTr(new Date(rangeStart + "T12:00:00"));
      return "Takvim seçimi: " + fmtTr(new Date(rangeStart + "T12:00:00")) + " → " + fmtTr(new Date(rangeEndIncl + "T12:00:00"));
    }

    function toDatetimeLocal(d, hm) {
      return d + "T" + hm;
    }

    function resetProcessActivityForm() {
      activityMetaCache = { processId: null, data: null };
      selectProcess.innerHTML = "";
      actMetaBox.classList.add("hidden");
      actMetaHint.classList.remove("hidden");
      actMetaLoading.classList.add("hidden");
      document.getElementById("cal-act-name").value = "";
      document.getElementById("cal-act-kpi").innerHTML = "";
      document.getElementById("cal-act-assignee-box").innerHTML = "";
      document.getElementById("cal-act-start").value = "";
      document.getElementById("cal-act-end").value = "";
      ["cal-act-rem-60", "cal-act-rem-1440", "cal-act-rem-4320", "cal-act-rem-7200"].forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.checked = false;
      });
      document.getElementById("cal-act-notify-email").checked = false;
      document.getElementById("cal-act-status").value = "Planlandı";
      document.getElementById("cal-act-desc").value = "";
    }

    function resetProjectForm() {
      document.getElementById("cal-proj-title").value = "";
      document.getElementById("cal-proj-desc").value = "";
      document.getElementById("cal-proj-status").value = "Yapılacak";
      document.getElementById("cal-proj-priority").value = "Medium";
      document.getElementById("cal-proj-assignee").value = "";
      document.getElementById("cal-proj-kpi").value = "";
    }

    function resetSelfForm() {
      document.getElementById("cal-self-title").value = "";
      document.getElementById("cal-self-t-start").value = "";
      document.getElementById("cal-self-t-end").value = "";
      document.getElementById("cal-self-desc").value = "";
    }

    function openModal(isoStart, isoEndExclusive) {
      const s = isoStart.slice(0, 10);
      rangeStart = s;
      if (isoEndExclusive) {
        const endEx = new Date(isoEndExclusive);
        endEx.setDate(endEx.getDate() - 1);
        rangeEndIncl = endEx.toISOString().slice(0, 10);
      } else {
        rangeEndIncl = s;
      }
      if (rangeEndIncl < rangeStart) {
        const t = rangeStart;
        rangeStart = rangeEndIncl;
        rangeEndIncl = t;
      }
      clearModalVariant();
      headIcon.className = "fas fa-calendar-plus text-sky-500";
      modalTitle.textContent = "Takvime ne ekleyelim?";
      modalBadge.classList.add("hidden");
      datesEl.textContent = dateRangeRecap();
      stepType.classList.remove("hidden");
      stepForm.classList.add("hidden");
      errEl.classList.add("hidden");
      resetProcessActivityForm();
      resetProjectForm();
      resetSelfForm();
      formMode = null;
      modal.hidden = false;
      backdrop.hidden = false;
      loadMeta()
        .then((m) => {
          optProcess.disabled = !m.can_process;
          optProject.disabled = !m.can_project;
          optSelf.disabled = !m.can_individual;
        })
        .catch(() => {
          optProcess.disabled = true;
          optProject.disabled = true;
        });
    }

    function closeModal() {
      modal.hidden = true;
      backdrop.hidden = true;
      clearModalVariant();
      if (calendar) calendar.unselect();
    }

    function fillProjectFormFromMeta(m) {
      const tf = (m && m.task_form) || { kpis: [], users: [] };
      const selP = document.getElementById("cal-select-project");
      selP.innerHTML = '<option value="">— Proje seçin —</option>';
      (m.projects || []).forEach((p) => {
        const o = document.createElement("option");
        o.value = String(p.id);
        o.textContent = p.name;
        selP.appendChild(o);
      });
      const selKpi = document.getElementById("cal-proj-kpi");
      selKpi.innerHTML = '<option value="">— PG seçilmedi —</option>';
      (tf.kpis || []).forEach((k) => {
        const o = document.createElement("option");
        o.value = String(k.id);
        o.textContent = k.label;
        selKpi.appendChild(o);
      });
      document.getElementById("cal-proj-kpi-empty").classList.toggle("hidden", (tf.kpis || []).length > 0);
      const selU = document.getElementById("cal-proj-assignee");
      selU.innerHTML = '<option value="">—</option>';
      (tf.users || []).forEach((u) => {
        const o = document.createElement("option");
        o.value = String(u.id);
        o.textContent = u.full_name || u.email || "#" + u.id;
        selU.appendChild(o);
      });
      document.getElementById("cal-proj-start").value = rangeStart;
      document.getElementById("cal-proj-due").value = rangeEndIncl;
    }

    function buildAssigneeCheckboxes(users, selectedIds, canMulti) {
      const box = document.getElementById("cal-act-assignee-box");
      const hint = document.getElementById("cal-act-assignee-hint");
      box.innerHTML = "";
      if (!users || !users.length) {
        box.innerHTML = '<div class="text-xs text-slate-500">Süreçte atanabilir kullanıcı bulunamadı.</div>';
        hint.textContent = "";
        return;
      }
      const sel = new Set((selectedIds || []).map((x) => String(x)));
      hint.textContent = canMulti
        ? "Süreç lideri birden fazla kişi seçebilir."
        : "Yalnızca kendinize atama yapılabilir; sunucu kurallarıyla doğrulanır.";
      users.forEach((u) => {
        const id = String(u.id);
        const checked = sel.has(id) ? " checked" : "";
        const label = u.full_name || u.email || "#" + u.id;
        const lab = document.createElement("label");
        lab.innerHTML = `<input class="cal-act-assignee-chk" type="checkbox" value="${id}"${checked}/><span>${escHtml(label)}</span>`;
        const inp = lab.querySelector("input");
        if (!canMulti) {
          inp.addEventListener("change", () => {
            if (inp.checked) {
              box.querySelectorAll(".cal-act-assignee-chk").forEach((c) => {
                if (c !== inp) c.checked = false;
              });
            }
          });
        }
        box.appendChild(lab);
      });
    }

    async function loadActivityMetaForProcess(pid) {
      const pidInt = parseInt(pid, 10);
      if (!pidInt) return;
      if (activityMetaCache.processId === pidInt && activityMetaCache.data) {
        applyActivityMeta(activityMetaCache.data);
        return;
      }
      actMetaLoading.classList.remove("hidden");
      actMetaHint.classList.add("hidden");
      actMetaBox.classList.add("hidden");
      try {
        const res = await fetch(activityMetaUrl(pidInt), {
          credentials: "same-origin",
          headers: { Accept: "application/json" },
        });
        const data = await res.json();
        if (!res.ok || !data.success) throw new Error(data.message || "Yüklenemedi");
        activityMetaCache = { processId: pidInt, data };
        applyActivityMeta(data);
      } catch (e) {
        actMetaHint.textContent = String(e.message || e);
        actMetaHint.classList.remove("hidden");
      } finally {
        actMetaLoading.classList.add("hidden");
      }
    }

    function applyActivityMeta(data) {
      const kpis = data.kpis || [];
      const users = data.process_users || [];
      const canMulti = !!data.can_multi_assign;
      const sel = document.getElementById("cal-act-kpi");
      sel.innerHTML = '<option value="">Bağımsız</option>';
      kpis.forEach((k) => {
        const o = document.createElement("option");
        o.value = String(k.id);
        o.textContent = k.label;
        sel.appendChild(o);
      });
      const defaultAssignees = canMulti ? [currentUserId] : [currentUserId];
      buildAssigneeCheckboxes(users, defaultAssignees, canMulti);
      document.getElementById("cal-act-start").value = toDatetimeLocal(rangeStart, "09:00");
      document.getElementById("cal-act-end").value = toDatetimeLocal(rangeEndIncl, "17:00");
      actMetaHint.classList.add("hidden");
      actMetaBox.classList.remove("hidden");
    }

    selectProcess.addEventListener("change", () => {
      const v = selectProcess.value;
      if (!v) {
        actMetaBox.classList.add("hidden");
        actMetaHint.textContent = "Önce süreç seçin.";
        actMetaHint.classList.remove("hidden");
        return;
      }
      loadActivityMetaForProcess(v);
    });

    function showForm(mode) {
      formMode = mode;
      clearModalVariant();
      stepType.classList.add("hidden");
      stepForm.classList.remove("hidden");
      errEl.classList.add("hidden");
      formDatesRecap.textContent = dateRangeRecap();

      formProcess.classList.toggle("hidden", mode !== "process");
      formProject.classList.toggle("hidden", mode !== "project");
      formSelf.classList.toggle("hidden", mode !== "self");

      if (mode === "process") {
        modal.classList.add("cal-modal--process");
        headIcon.className = "fas fa-list-check text-emerald-500";
        modalTitle.textContent = "Yeni Faaliyet";
        modalBadge.classList.remove("hidden");
        modalBadge.innerHTML = '<span class="text-emerald-600 dark:text-emerald-400">Süreç karnesi ile aynı form</span>';
        resetProcessActivityForm();
        selectProcess.innerHTML = '<option value="">— Süreç seçin —</option>';
        (metaCache.processes || []).forEach((p) => {
          const o = document.createElement("option");
          o.value = String(p.id);
          o.textContent = p.name;
          selectProcess.appendChild(o);
        });
      } else if (mode === "project") {
        modal.classList.add("cal-modal--project");
        headIcon.className = "fas fa-clipboard-list text-blue-500";
        modalTitle.textContent = "Yeni görev";
        modalBadge.classList.remove("hidden");
        modalBadge.innerHTML = '<span class="text-blue-600 dark:text-blue-400">Proje görevi formu ile aynı</span>';
        resetProjectForm();
        fillProjectFormFromMeta(metaCache);
      } else {
        modal.classList.add("cal-modal--self");
        headIcon.className = "fas fa-user text-amber-500";
        modalTitle.textContent = "Kendime görev";
        modalBadge.classList.remove("hidden");
        modalBadge.innerHTML = '<span class="text-amber-600 dark:text-amber-400">Bireysel faaliyet</span>';
        resetSelfForm();
        document.getElementById("cal-self-start").value = rangeStart;
        document.getElementById("cal-self-end").value = rangeEndIncl;
      }
    }

    function getCheckedReminderOffsets() {
      const ids = ["60", "1440", "4320", "7200"];
      return ids
        .map((v) => document.getElementById("cal-act-rem-" + v))
        .filter((el) => el && el.checked)
        .map((el) => parseInt(el.value, 10));
    }

    async function submitForm() {
      errEl.classList.add("hidden");
      const headers = {
        "Content-Type": "application/json",
        Accept: "application/json",
        "X-CSRFToken": getCsrf(),
      };
      btnSubmit.disabled = true;
      try {
        if (formMode === "self") {
          const title = (document.getElementById("cal-self-title").value || "").trim();
          if (!title) throw new Error("Başlık girin.");
          const sd = document.getElementById("cal-self-start").value || rangeStart;
          const ed = document.getElementById("cal-self-end").value || rangeEndIncl;
          if (ed < sd) throw new Error("Bitiş tarihi başlangıçtan önce olamaz.");
          const ts = (document.getElementById("cal-self-t-start").value || "").trim();
          const te = (document.getElementById("cal-self-t-end").value || "").trim();
          const note = (document.getElementById("cal-self-desc").value || "").trim();
          const parts = [];
          if (ts || te) parts.push("Planlanan saat: " + (ts || "—") + " – " + (te || "—"));
          if (note) parts.push(note);
          const description = parts.length ? parts.join("\n\n") : "";
          const body = { name: title, status: "Planlandı", start_date: sd, end_date: ed };
          if (description) body.description = description;
          const res = await fetch(faaliyetAddUrl, {
            method: "POST",
            credentials: "same-origin",
            headers,
            body: JSON.stringify(body),
          });
          const data = await res.json();
          if (!res.ok || !data.success) throw new Error(data.message || "Kaydedilemedi");
        } else if (formMode === "process") {
          const pid = parseInt(selectProcess.value, 10);
          if (!pid) throw new Error("Süreç seçin.");
          if (actMetaBox.classList.contains("hidden")) throw new Error("Süreç için form yüklenemedi.");
          const name = (document.getElementById("cal-act-name").value || "").trim();
          if (!name) throw new Error("Faaliyet adı zorunludur.");
          const startAt = document.getElementById("cal-act-start").value;
          const endAt = document.getElementById("cal-act-end").value;
          if (!startAt || !endAt) throw new Error("Başlangıç ve bitiş tarih/saat zorunludur.");
          if (endAt < startAt) throw new Error("Bitiş, başlangıçtan sonra olmalıdır.");
          const assigneeIds = Array.from(document.querySelectorAll(".cal-act-assignee-chk:checked"))
            .map((o) => parseInt(o.value, 10))
            .filter((x) => !Number.isNaN(x));
          if (!assigneeIds.length) throw new Error("En az bir atanan seçin.");
          const kpiRaw = document.getElementById("cal-act-kpi").value;
          const body = {
            process_id: pid,
            name,
            process_kpi_id: kpiRaw ? parseInt(kpiRaw, 10) : null,
            start_at: startAt,
            end_at: endAt,
            status: document.getElementById("cal-act-status").value || "Planlandı",
            description: (document.getElementById("cal-act-desc").value || "").trim(),
            assignee_ids: assigneeIds,
            reminder_offsets: getCheckedReminderOffsets(),
            notify_email: !!document.getElementById("cal-act-notify-email").checked,
          };
          const res = await fetch(activityAddUrl, {
            method: "POST",
            credentials: "same-origin",
            headers,
            body: JSON.stringify(body),
          });
          const data = await res.json();
          if (!res.ok || !data.success) throw new Error(data.message || "Kaydedilemedi");
        } else if (formMode === "project") {
          const pid = parseInt(document.getElementById("cal-select-project").value, 10);
          if (!pid) throw new Error("Proje seçin.");
          const title = (document.getElementById("cal-proj-title").value || "").trim();
          if (!title) throw new Error("Başlık zorunludur.");
          const body = {
            project_id: pid,
            title,
            description: (document.getElementById("cal-proj-desc").value || "").trim() || undefined,
            status: document.getElementById("cal-proj-status").value || "Yapılacak",
            priority: document.getElementById("cal-proj-priority").value || "Medium",
            start_date: document.getElementById("cal-proj-start").value || rangeStart,
            due_date: document.getElementById("cal-proj-due").value || rangeEndIncl,
          };
          const aid = document.getElementById("cal-proj-assignee").value;
          if (aid) body.assignee_id = parseInt(aid, 10);
          const kpi = document.getElementById("cal-proj-kpi").value;
          if (kpi) body.process_kpi_id = parseInt(kpi, 10);
          const res = await fetch(taskQuickUrl, {
            method: "POST",
            credentials: "same-origin",
            headers,
            body: JSON.stringify(body),
          });
          const data = await res.json();
          if (!res.ok || !data.success) throw new Error(data.message || "Kaydedilemedi");
        }
        closeModal();
        calendar.refetchEvents();
      } catch (e) {
        errEl.textContent = String(e.message || e);
        errEl.classList.remove("hidden");
      } finally {
        btnSubmit.disabled = false;
      }
    }

    optProcess.addEventListener("click", () => {
      loadMeta().then(() => showForm("process"));
    });
    optProject.addEventListener("click", () => {
      loadMeta().then(() => showForm("project"));
    });
    optSelf.addEventListener("click", () => {
      loadMeta().then(() => showForm("self"));
    });
    btnBack.addEventListener("click", () => {
      stepForm.classList.add("hidden");
      stepType.classList.remove("hidden");
      clearModalVariant();
      headIcon.className = "fas fa-calendar-plus text-sky-500";
      modalTitle.textContent = "Takvime ne ekleyelim?";
      modalBadge.classList.add("hidden");
      errEl.classList.add("hidden");
    });
    btnSubmit.addEventListener("click", submitForm);
    btnClose.addEventListener("click", closeModal);
    backdrop.addEventListener("click", closeModal);

    calendar = new FullCalendar.Calendar(calEl, {
      locale: "tr",
      timeZone: "Europe/Istanbul",
      initialView: "dayGridMonth",
      firstDay: 1,
      height: "auto",
      selectable: true,
      unselectAuto: false,
      headerToolbar: {
        left: "prev,next today",
        center: "title",
        right: "dayGridMonth,timeGridWeek,timeGridDay",
      },
      buttonText: {
        today: "Bugün",
        month: "Ay",
        week: "Hafta",
        day: "Gün",
      },
      events: async function (fetchInfo, successCallback, failureCallback) {
        try {
          const url = `${eventsUrl}?start=${encodeURIComponent(fetchInfo.startStr)}&end=${encodeURIComponent(fetchInfo.endStr)}`;
          const res = await fetch(url, {
            credentials: "same-origin",
            headers: { Accept: "application/json" },
          });
          const contentType = String(res.headers.get("content-type") || "").toLowerCase();
          let data = null;
          if (contentType.includes("application/json")) {
            data = await res.json();
          } else {
            const raw = await res.text();
            throw new Error(
              res.status >= 500
                ? `Sunucu hatası (HTTP ${res.status})`
                : `Beklenmeyen yanıt (HTTP ${res.status}): ${raw.slice(0, 120)}`
            );
          }
          if (!res.ok || !data.success) {
            throw new Error((data && data.message) || `HTTP ${res.status}`);
          }
          if (loadingEl) loadingEl.style.display = "none";
          successCallback(data.events || []);
        } catch (err) {
          if (loadingEl) loadingEl.innerHTML = `<span style="color:#dc2626;">Takvim yüklenemedi: ${String(err.message || err)}</span>`;
          failureCallback(err);
        }
      },
      dateClick: function (info) {
        if (info.jsEvent && info.jsEvent.target && info.jsEvent.target.closest && info.jsEvent.target.closest(".fc-event")) return;
        openModal(info.dateStr, null);
      },
      select: function (info) {
        openModal(info.startStr, info.endStr);
      },
      eventClick: function (info) {
        const u = info.event.url || (info.event.extendedProps && info.event.extendedProps.url);
        if (u) {
          info.jsEvent.preventDefault();
          window.location.href = u;
        }
      },
      eventTimeFormat: {
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
      },
    });
    calendar.render();
  }

  global.KokpitimCalendarQuickCreate = { boot };
})(typeof globalThis !== "undefined" ? globalThis : window);
