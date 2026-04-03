/**
 * Yönetim Paneli - Login istatistik ve aktiviteler
 */
(function () {
  "use strict";

  function showError(message) {
    Swal.fire({
      icon: "error",
      title: "Hata",
      text: message || "İstatistikler yüklenemedi.",
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
    if (diffSec < 60) return diffSec + " sn önce";
    var diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return diffMin + " dk önce";
    var diffHour = Math.floor(diffMin / 60);
    if (diffHour < 24) return diffHour + " saat önce";
    var diffDay = Math.floor(diffHour / 24);
    return diffDay + " gün önce";
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
    tbody.innerHTML = '<tr><td colspan="5">Kayıt bulunamadı.</td></tr>';
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
      var userName = item.user_name || "Bilinmiyor";
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
        showError((body && body.message) || "İstatistikler alınamadı.");
        return;
      }
      setDataState(body.data || {});
    } catch (err) {
      showError("Sunucuya erişilemedi. Lütfen tekrar deneyin.");
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
        showError((body && body.message) || "Aktivite listesi alınamadı.");
        setActivityEmptyState();
        return;
      }
      setActivityDataState(body.data || []);
    } catch (err) {
      showError("Aktivite listesi alınırken sunucuya erişilemedi.");
      setActivityEmptyState();
    }
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

  if (tenantSelect) {
    tenantSelect.addEventListener("change", function () {
      activityLimit = 20;
      if (moreBtn) moreBtn.disabled = false;
      loadStats(root, tenantSelect.value || "");
      loadActivities(root, tenantSelect.value || "", activityLimit);
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
})();
