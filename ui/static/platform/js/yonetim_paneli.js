/**
 * Yönetim Paneli - Login istatistik ve aktiviteler
 */
(function () {
  "use strict";

  function showError(message) {
    Swal.fire({
      icon: "error",
      title: t("Hata"),
      text: message || t("İstatistikler yüklenemedi."),
      confirmButtonColor: "#dc2626",
    });
  }

  function setLoadingState() {
    document.querySelectorAll(".yp-stat-value").forEach((el) => {
      el.textContent = "...";
    });
  }

  function setDataState(data) {
    document.querySelectorAll(".yp-stat-value").forEach((el) => {
      var key = el.dataset.key;
      var val = data && Object.prototype.hasOwnProperty.call(data, key) ? data[key] : 0;
      el.textContent = String(val);
    });
  }

  function formatTimeAgo(isoDate) {
    if (!isoDate) return "-";
    var d = new Date(isoDate);
    if (Number.isNaN(d.getTime())) return "-";
    var diffSec = Math.max(0, Math.floor((Date.now() - d.getTime()) / 1000));
    if (diffSec < 60) return diffSec + " " + t("sn önce");
    var diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return diffMin + " " + t("dk önce");
    var diffHour = Math.floor(diffMin / 60);
    if (diffHour < 24) return diffHour + " " + t("saat önce");
    var diffDay = Math.floor(diffHour / 24);
    return diffDay + " " + t("gün önce");
  }

  function setUserLoadingState() {
    var tbody = document.getElementById("user-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    for (var i = 0; i < 3; i += 1) {
      var tr = document.createElement("tr");
      tr.className = "yp-skeleton-row";
      tr.innerHTML =
        '<td><div class="yp-skeleton-line yp-skeleton-sm"></div></td>' +
        '<td><div class="yp-skeleton-line"></div></td>' +
        '<td><div class="yp-skeleton-line yp-skeleton-sm"></div></td>' +
        '<td><div class="yp-skeleton-line yp-skeleton-sm"></div></td>' +
        '<td><div class="yp-skeleton-line"></div></td>' +
        '<td><div class="yp-skeleton-line yp-skeleton-sm"></div></td>' +
        '<td><div class="yp-skeleton-line yp-skeleton-sm"></div></td>';
      tbody.appendChild(tr);
    }
  }

  function setUserDataState(items) {
    var tbody = document.getElementById("user-tbody");
    if (!tbody) return;
    if (!items || !items.length) {
      tbody.innerHTML = '<tr><td colspan="7">' + t("Kayıt bulunamadı.") + '</td></tr>';
      return;
    }
    tbody.innerHTML = "";
    items.forEach(function (u) {
      var tr = document.createElement("tr");
      var onlineBadge = u.is_online
        ? '<span style="display:inline-flex;align-items:center;gap:4px;color:#16a34a;font-weight:600;font-size:12px;"><span style="width:8px;height:8px;border-radius:50%;background:#16a34a;display:inline-block;"></span>' + t("Çevrimiçi") + '</span>'
        : '<span style="font-size:12px;color:#94a3b8;">—</span>';
      var accountBadge = u.is_active
        ? '<span class="mc-badge mc-badge-success" style="font-size:11px;">' + t("Aktif") + '</span>'
        : '<span class="mc-badge mc-badge-gray" style="font-size:11px;">' + t("Pasif") + '</span>';
      var nameCell = '<strong>' + _esc(u.name) + '</strong><br><span style="font-size:11px;color:#94a3b8;">' + _esc(u.email || '') + '</span>';
      var lastLogin = u.last_login_at ? formatTimeAgo(u.last_login_at) + '<br><span style="font-size:10px;color:#94a3b8;">' + _shortDate(u.last_login_at) + '</span>' : '<span style="color:#94a3b8;">—</span>';
      tr.innerHTML =
        "<td>" + onlineBadge + "</td>" +
        "<td>" + nameCell + "</td>" +
        "<td><span style='font-size:12px;color:#64748b;'>" + _esc(u.role || "—") + "</span></td>" +
        "<td>" + accountBadge + "</td>" +
        "<td style='white-space:nowrap;'>" + lastLogin + "</td>" +
        "<td style='text-align:center;'>" + (u.login_count_30d || 0) + "</td>" +
        "<td style='text-align:center;'>" + (u.actions_30d || 0) + "</td>";
      tbody.appendChild(tr);
    });
  }

  function _esc(str) {
    if (!str) return "";
    return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function _shortDate(isoDate) {
    if (!isoDate) return "";
    try {
      var d = new Date(isoDate);
      return d.toLocaleDateString("tr-TR", { day: "2-digit", month: "2-digit", year: "numeric" });
    } catch (_e) { return ""; }
  }

  async function loadUserTable(root, tenantId) {
    setUserLoadingState();
    var apiUrl = root.dataset.kullaniciUrl;
    if (!apiUrl) return;
    var params = new URLSearchParams();
    if (tenantId !== null && tenantId !== undefined && String(tenantId).trim() !== "") {
      params.append("tenant_id", String(tenantId));
    }
    var url = apiUrl + (params.toString() ? "?" + params.toString() : "");
    try {
      var res = await fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } });
      var body = await res.json();
      if (!res.ok || !body.success) {
        var tbody = document.getElementById("user-tbody");
        if (tbody) tbody.innerHTML = '<tr><td colspan="7">' + t("Kullanıcı verisi alınamadı.") + '</td></tr>';
        return;
      }
      setUserDataState(body.data || []);
    } catch (err) {
      var tbody = document.getElementById("user-tbody");
      if (tbody) tbody.innerHTML = '<tr><td colspan="7">' + t("Sunucuya erişilemedi.") + '</td></tr>';
    }
  }

  function setActivityLoadingState() {
    var tbody = document.getElementById("activity-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    for (var i = 0; i < 3; i += 1) {
      var tr = document.createElement("tr");
      tr.className = "yp-skeleton-row";
      tr.innerHTML =
        '<td><div class="yp-skeleton-line yp-skeleton-sm"></div></td>' +
        '<td><div class="yp-skeleton-line"></div></td>' +
        '<td><div class="yp-skeleton-line"></div></td>' +
        '<td><div class="yp-skeleton-line"></div></td>' +
        '<td><div class="yp-skeleton-line yp-skeleton-sm"></div></td>';
      tbody.appendChild(tr);
    }
  }

  function setActivityEmptyState() {
    var tbody = document.getElementById("activity-tbody");
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="5">' + t("Kayıt bulunamadı.") + '</td></tr>';
  }

  function setActivityDataState(items) {
    var tbody = document.getElementById("activity-tbody");
    if (!tbody) return;
    if (!items || !items.length) {
      setActivityEmptyState();
      return;
    }
    tbody.innerHTML = "";
    items.forEach(function (item) {
      var tr = document.createElement("tr");
      var userName = item.user_name || t("Bilinmiyor");
      tr.innerHTML =
        "<td>" + (item.resource_icon || "📌") + "</td>" +
        "<td>" + (item.resource_type || "-") + "</td>" +
        "<td>" + userName + "</td>" +
        "<td>" + (item.action_label || item.action || "-") + "</td>" +
        "<td>" + formatTimeAgo(item.created_at) + "</td>";
      tbody.appendChild(tr);
    });
  }

  async function loadStats(root, tenantId) {
    setLoadingState();
    var apiUrl = root.dataset.apiUrl;
    var url = apiUrl;
    if (tenantId !== null && tenantId !== undefined && String(tenantId).trim() !== "") {
      url += "?tenant_id=" + encodeURIComponent(String(tenantId));
    }

    try {
      var res = await fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } });
      var body = await res.json();
      if (!res.ok || !body.success) {
        showError((body && body.message) || t("İstatistikler alınamadı."));
        return;
      }
      setDataState(body.data || {});
    } catch (err) {
      showError(t("Sunucuya erişilemedi. Lütfen tekrar deneyin."));
    }
  }

  async function loadActivities(root, tenantId, limit) {
    setActivityLoadingState();
    var apiUrl = root.dataset.aktiviteUrl;
    if (!apiUrl) return;
    var params = new URLSearchParams();
    if (tenantId !== null && tenantId !== undefined && String(tenantId).trim() !== "") {
      params.append("tenant_id", String(tenantId));
    }
    params.append("limit", String(limit || 20));
    var url = apiUrl + "?" + params.toString();
    try {
      var res = await fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } });
      var body = await res.json();
      if (!res.ok || !body.success) {
        showError((body && body.message) || t("Aktivite listesi alınamadı."));
        setActivityEmptyState();
        return;
      }
      setActivityDataState(body.data || []);
    } catch (err) {
      showError(t("Aktivite listesi alınırken sunucuya erişilemedi."));
      setActivityEmptyState();
    }
  }

  function csrfToken() {
    var m = document.querySelector('meta[name="csrf-token"]');
    return m ? m.getAttribute("content") || "" : "";
  }

  var maintCard = document.getElementById("yp-maintenance-card");
  if (maintCard) {
    var bakimUrl = maintCard.dataset.bakimUrl;
    var maintChk = document.getElementById("yp-maintenance-chk");
    var maintLock = document.getElementById("yp-maintenance-lock-hint");
    var maintCanToggle = true;

    async function loadMaintenance() {
      if (!bakimUrl || !maintChk) return;
      try {
        var res = await fetch(bakimUrl, { headers: { "X-Requested-With": "XMLHttpRequest" } });
        var body = await res.json();
        if (!res.ok || !body.success || !body.data) return;
        var d = body.data;
        maintCanToggle = !!d.can_toggle_db;
        maintChk.checked = !!d.active;
        maintChk.disabled = !maintCanToggle;
        if (!maintCanToggle && maintLock) {
          maintLock.style.display = "block";
          if (d.env_force) {
            maintLock.textContent =
              t("Bakım şu an ortam değişkeni MAINTENANCE_MODE ile zorlanıyor; panelden kapatılamaz.");
          } else if (d.override_off) {
            maintLock.textContent =
              t("MAINTENANCE_OVERRIDE_OFF etkin; yalnızca ortam/SSH ile yönetilir.");
          } else {
            maintLock.textContent = t("Bu bayrak şu an panelden değiştirilemiyor.");
          }
        } else if (maintLock) {
          maintLock.style.display = "none";
        }
      } catch (_e) {}
    }

    maintChk.addEventListener("change", async function () {
      if (!maintCanToggle) return;
      var prev = !maintChk.checked;
      try {
        var res = await fetch(bakimUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken(),
            "X-Requested-With": "XMLHttpRequest",
          },
          body: JSON.stringify({ enabled: maintChk.checked }),
        });
        var body = await res.json();
        if (!res.ok || !body.success) {
          maintChk.checked = prev;
          showError((body && body.message) || t("Bakım modu kaydedilemedi."));
          return;
        }
        if (body.data) {
          maintChk.checked = !!body.data.active;
        }
      } catch (err) {
        maintChk.checked = prev;
        showError(t("Sunucuya erişilemedi."));
      }
    });

    loadMaintenance();
  }

  var root = document.getElementById("panel-root");
  if (!root) return;

  var tenantSelect = document.getElementById("tenant-select");
  var moreBtn = document.getElementById("activity-more-btn");
  var activityLimit = 20;
  var initialTenant = root.dataset.tenantId || "";

  var selectedTenant = tenantSelect ? tenantSelect.value : initialTenant;
  loadStats(root, selectedTenant);
  loadActivities(root, selectedTenant, activityLimit);
  loadUserTable(root, selectedTenant);

  if (tenantSelect) {
    tenantSelect.addEventListener("change", function () {
      activityLimit = 20;
      if (moreBtn) moreBtn.disabled = false;
      loadStats(root, tenantSelect.value || "");
      loadActivities(root, tenantSelect.value || "", activityLimit);
      loadUserTable(root, tenantSelect.value || "");
    });
  }

  if (moreBtn) {
    moreBtn.addEventListener("click", function () {
      activityLimit = 50;
      moreBtn.disabled = true;
      var tenantId = tenantSelect ? tenantSelect.value || "" : initialTenant;
      loadActivities(root, tenantId, activityLimit);
    });
  }

  // Accordion
  document.querySelectorAll(".yp-accordion-header").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var expanded = btn.getAttribute("aria-expanded") === "true";
      var bodyId = btn.getAttribute("aria-controls");
      var body = document.getElementById(bodyId);
      if (!body) return;
      if (expanded) {
        btn.setAttribute("aria-expanded", "false");
        body.classList.add("yp-collapsed");
      } else {
        btn.setAttribute("aria-expanded", "true");
        body.classList.remove("yp-collapsed");
      }
    });
  });
})();
