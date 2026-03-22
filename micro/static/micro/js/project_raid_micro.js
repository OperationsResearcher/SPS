/**
 * RAID sayfası — Micro tema; window.MICRO_RAID_PROJECT_ID set edilmeli.
 */
(function () {
  "use strict";
  function pid() {
    return String(window.MICRO_RAID_PROJECT_ID || "");
  }
  function apiRaid() {
    var base = typeof window.MICRO_API_BASE === "string" ? window.MICRO_API_BASE.replace(/\/$/, "") : "";
    return base + "/api/projeler/" + pid() + "/raid";
  }

  var raidData = { Risk: [], Assumption: [], Issue: [], Dependency: [] };

  window.getRaidModal = function getRaidModal() {
    var el = document.getElementById("raidModal");
    return {
      show: function () {
        if (!el) return;
        el.classList.add("micro-raid-modal--open");
        el.setAttribute("aria-hidden", "false");
      },
      hide: function () {
        if (!el) return;
        el.classList.remove("micro-raid-modal--open");
        el.setAttribute("aria-hidden", "true");
      },
    };
  };

  function _parseJsonRes(res) {
    var ct = (res.headers && res.headers.get("content-type")) || "";
    if (!ct.includes("application/json")) {
      return Promise.reject(
        new Error("API yanıtı JSON değil (oturum veya /api adresi). Sayfayı yenileyin.")
      );
    }
    return res.json();
  }

  window.loadRAID = async function loadRAID() {
    try {
      var res = await fetch(apiRaid(), { credentials: "same-origin" });
      var data = await _parseJsonRes(res);
      if (!data.success) throw new Error(data.message);

      raidData = { Risk: [], Assumption: [], Issue: [], Dependency: [] };
      (data.items || []).forEach(function (item) {
        var itemType = item.type || item.item_type;
        if (raidData[itemType]) raidData[itemType].push(item);
      });

      renderLists();
    } catch (e) {
      console.error(e);
      if (window.showToast) window.showToast("error", e.message, "RAID Yükleme Hatası");
    }
  };

  function renderLists() {
    var types = ["Risk", "Assumption", "Issue", "Dependency"];
    var containers = ["risks-list", "assumptions-list", "issues-list", "dependencies-list"];

    types.forEach(function (type, idx) {
      var container = document.getElementById(containers[idx]);
      if (!container) return;
      var items = raidData[type] || [];

      if (items.length === 0) {
        container.innerHTML = '<p class="micro-raid-muted">Henüz öğe eklenmedi.</p>';
        return;
      }

      container.innerHTML = items
        .map(function (item) {
          var extraInfo = "";

          if (type === "Risk" && item.probability) {
            extraInfo =
              '<div style="margin-top:8px;">' +
              '<span class="micro-raid-badge">Olasılık: ' +
              item.probability +
              "/5</span> " +
              '<span class="micro-raid-badge">Etki: ' +
              item.impact +
              "/5</span></div>";
          } else if (type === "Assumption" && item.assumption_validation_date) {
            extraInfo =
              '<div style="margin-top:8px;"><span class="micro-raid-badge">Doğrulama: ' +
              item.assumption_validation_date +
              "</span></div>";
          } else if (type === "Issue" && item.issue_urgency) {
            extraInfo =
              '<div style="margin-top:8px;"><span class="micro-raid-badge">Aciliyet: ' +
              item.issue_urgency +
              "</span></div>";
          } else if (type === "Dependency" && item.dependency_type) {
            extraInfo =
              '<div style="margin-top:8px;"><span class="micro-raid-badge">Tip: ' +
              item.dependency_type +
              "</span></div>";
          }

          var desc = item.description
            ? '<p class="micro-raid-muted" style="margin:8px 0 0 0;">' +
              String(item.description).replace(/</g, "&lt;") +
              "</p>"
            : "";

          var stBg = item.status === "Closed" ? "#dcfce7" : "#fef3c7";
          var stCol = item.status === "Closed" ? "#166534" : "#92400e";

          return (
            '<div class="micro-raid-item">' +
            '<div style="display:flex; justify-content:space-between; align-items:flex-start; gap:10px;">' +
            "<h6 style=\"margin:0;font-size:14px;font-weight:600;\">" +
            String(item.title || "").replace(/</g, "&lt;") +
            "</h6>" +
            "<div style=\"display:flex; align-items:center; gap:6px; flex-shrink:0;\">" +
            '<span style="font-size:11px;padding:2px 8px;border-radius:6px;background:' +
            stBg +
            ";color:" +
            stCol +
            ';">' +
            item.status +
            "</span>" +
            '<button type="button" class="mc-btn mc-btn-secondary mc-btn-sm" data-raid-edit="' +
            item.id +
            '"><i class="fas fa-edit"></i></button>' +
            '<button type="button" class="mc-btn mc-btn-danger mc-btn-sm" data-raid-del="' +
            item.id +
            '"><i class="fas fa-trash"></i></button>' +
            "</div></div>" +
            desc +
            extraInfo +
            "</div>"
          );
        })
        .join("");

      container.querySelectorAll("[data-raid-edit]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          window.editItem(parseInt(btn.getAttribute("data-raid-edit"), 10));
        });
      });
      container.querySelectorAll("[data-raid-del]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          window.deleteItem(parseInt(btn.getAttribute("data-raid-del"), 10));
        });
      });
    });
  }

  window.openAddModal = function openAddModal(type) {
    document.getElementById("item-id").value = "";
    document.getElementById("item-type").value = type;
    document.getElementById("item-title").value = "";
    document.getElementById("item-description").value = "";
    document.getElementById("item-status").value = "Open";

    document.getElementById("risk-fields").style.display = "none";
    document.getElementById("assumption-fields").style.display = "none";
    document.getElementById("issue-fields").style.display = "none";
    document.getElementById("dependency-fields").style.display = "none";

    if (type === "Risk") {
      document.getElementById("risk-fields").style.display = "block";
      document.getElementById("item-probability").value = "3";
      document.getElementById("item-impact").value = "3";
      document.getElementById("item-mitigation").value = "";
    } else if (type === "Assumption") {
      document.getElementById("assumption-fields").style.display = "block";
      document.getElementById("item-validation-date").value = "";
      document.getElementById("item-assumption-notes").value = "";
    } else if (type === "Issue") {
      document.getElementById("issue-fields").style.display = "block";
      document.getElementById("item-urgency").value = "Orta";
      document.getElementById("item-affected-work").value = "";
    } else if (type === "Dependency") {
      document.getElementById("dependency-fields").style.display = "block";
      document.getElementById("item-dependency-type").value = "SS";
      document.getElementById("item-task-id").value = "";
    }

    document.getElementById("modalTitle").textContent = type + " Ekle";
    window.getRaidModal().show();
  };

  window.editItem = function editItem(id) {
    var flat = []
      .concat(raidData.Risk || [])
      .concat(raidData.Assumption || [])
      .concat(raidData.Issue || [])
      .concat(raidData.Dependency || []);
    var item = flat.find(function (i) {
      return i.id === id;
    });
    if (!item) return;

    document.getElementById("item-id").value = item.id;
    document.getElementById("item-type").value = item.item_type;
    document.getElementById("item-title").value = item.title;
    document.getElementById("item-description").value = item.description || "";
    document.getElementById("item-status").value = item.status;
    document.getElementById("modalTitle").textContent = item.item_type + " Düzenle";

    document.getElementById("risk-fields").style.display = "none";
    document.getElementById("assumption-fields").style.display = "none";
    document.getElementById("issue-fields").style.display = "none";
    document.getElementById("dependency-fields").style.display = "none";

    if (item.item_type === "Risk") {
      document.getElementById("risk-fields").style.display = "block";
      document.getElementById("item-probability").value = item.probability || "3";
      document.getElementById("item-impact").value = item.impact || "3";
      document.getElementById("item-mitigation").value = item.mitigation_plan || "";
    } else if (item.item_type === "Assumption") {
      document.getElementById("assumption-fields").style.display = "block";
      document.getElementById("item-validation-date").value = item.assumption_validation_date || "";
      document.getElementById("item-assumption-notes").value = item.assumption_notes || "";
    } else if (item.item_type === "Issue") {
      document.getElementById("issue-fields").style.display = "block";
      document.getElementById("item-urgency").value = item.issue_urgency || "Orta";
      document.getElementById("item-affected-work").value = item.issue_affected_work || "";
    } else if (item.item_type === "Dependency") {
      document.getElementById("dependency-fields").style.display = "block";
      document.getElementById("item-dependency-type").value = item.dependency_type || "SS";
      document.getElementById("item-task-id").value = item.dependency_task_id || "";
    }

    window.getRaidModal().show();
  };

  window.saveItem = async function saveItem() {
    var id = document.getElementById("item-id").value;
    var type = document.getElementById("item-type").value;
    var title = document.getElementById("item-title").value.trim();
    var description = document.getElementById("item-description").value.trim();
    var status = document.getElementById("item-status").value;

    if (!title) {
      alert("Başlık gerekli");
      return;
    }

    var body = { item_type: type, title: title, description: description, status: status };

    if (type === "Risk") {
      body.probability = parseInt(document.getElementById("item-probability").value, 10) || 3;
      body.impact = parseInt(document.getElementById("item-impact").value, 10) || 3;
      body.mitigation_plan = document.getElementById("item-mitigation").value.trim();
    } else if (type === "Assumption") {
      body.assumption_validation_date = document.getElementById("item-validation-date").value;
      body.assumption_notes = document.getElementById("item-assumption-notes").value.trim();
    } else if (type === "Issue") {
      body.issue_urgency = document.getElementById("item-urgency").value;
      body.issue_affected_work = document.getElementById("item-affected-work").value.trim();
    } else if (type === "Dependency") {
      body.dependency_type = document.getElementById("item-dependency-type").value;
      body.dependency_task_id = parseInt(document.getElementById("item-task-id").value, 10) || null;
    }

    var url = id ? apiRaid() + "/" + id : apiRaid();
    var method = id ? "PUT" : "POST";

    try {
      var res = await fetch(url, {
        method: method,
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      var data = await _parseJsonRes(res);
      if (!data.success) throw new Error(data.message);

      window.getRaidModal().hide();
      await window.loadRAID();
      if (window.showToast) window.showToast("success", "RAID öğesi kaydedildi", "Başarılı");
    } catch (e) {
      console.error(e);
      if (window.showToast) window.showToast("error", e.message, "Kaydetme Hatası");
    }
  };

  window.deleteItem = async function deleteItem(id) {
    if (!confirm("Bu öğeyi silmek istediğinizden emin misiniz?")) return;

    try {
      var res = await fetch(apiRaid() + "/" + id, { method: "DELETE", credentials: "same-origin" });
      var data = await _parseJsonRes(res);
      if (!data.success) throw new Error(data.message);

      await window.loadRAID();
      if (window.showToast) window.showToast("success", "RAID öğesi silindi", "Başarılı");
    } catch (e) {
      console.error(e);
      if (window.showToast) window.showToast("error", e.message, "Silme Hatası");
    }
  };

  document.addEventListener("DOMContentLoaded", function () {
    var tabBar = document.getElementById("raidTabBar");
    if (tabBar) {
      tabBar.querySelectorAll("button[data-raid-pane]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var id = btn.getAttribute("data-raid-pane");
          tabBar.querySelectorAll("button[data-raid-pane]").forEach(function (b) {
            b.classList.remove("is-active");
          });
          btn.classList.add("is-active");
          document.querySelectorAll(".micro-raid-pane").forEach(function (p) {
            p.classList.toggle("is-active", p.id === id);
          });
        });
      });
    }
    document.querySelectorAll("[data-raid-modal-close]").forEach(function (el) {
      el.addEventListener("click", function () {
        window.getRaidModal().hide();
      });
    });
    if (!pid()) return;
    window.loadRAID();
  });
})();
