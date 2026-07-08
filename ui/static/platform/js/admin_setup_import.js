/* Kurulum İçe Aktarma sihirbazı (TASK-235)
   URL'ler data-* attribute'lardan okunur (KURALLAR §3: JS'de hardcoded URL yok). */
(function () {
  "use strict";
  var root = document.getElementById("setup-import-root");
  if (!root) return;

  var DRYRUN_URL = root.dataset.dryrunUrl;
  var APPLY_URL = root.dataset.applyUrl;
  var fileInput = document.getElementById("si-file");
  var dryBtn = document.getElementById("si-dryrun-btn");
  var applyBtn = document.getElementById("si-apply-btn");
  var skipCheck = document.getElementById("si-skip-errors");
  var previewCard = document.getElementById("si-preview-card");
  var resultCard = document.getElementById("si-result-card");
  var lastPlanHadErrors = false;

  function esc(s) {
    var d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  fileInput.addEventListener("change", function () {
    dryBtn.disabled = !fileInput.files.length;
    previewCard.style.display = "none";
    resultCard.style.display = "none";
  });

  function post(url, extra) {
    var fd = new FormData();
    fd.append("file", fileInput.files[0]);
    if (extra) Object.keys(extra).forEach(function (k) { fd.append(k, extra[k]); });
    return fetch(url, { method: "POST", body: fd }).then(function (r) { return r.json(); });
  }

  dryBtn.addEventListener("click", function () {
    dryBtn.disabled = true;
    post(DRYRUN_URL).then(function (j) {
      dryBtn.disabled = false;
      if (!j.success) {
        Swal.fire({ icon: "error", title: j.message || "Dosya işlenemedi" });
        return;
      }
      var s = j.summary || {};
      lastPlanHadErrors = (s.error || 0) > 0;
      document.getElementById("si-summary").innerHTML =
        "✅ " + (s.add || 0) + " yeni · 🔄 " + (s.update || 0) + " güncelleme · " +
        "📊 " + (s.strategy_rows || 0) + " strateji satırı · ❌ " + (s.error || 0) + " hatalı";
      var errHtml = "";
      (j.errors || []).forEach(function (e) {
        errHtml += "<div style='font-size:12px;color:#b91c1c;padding:2px 0;'>" +
          esc(e.sheet) + " — Satır " + esc(e.row) + ": " + esc(e.error) + "</div>";
      });
      document.getElementById("si-errors").innerHTML = errHtml;
      applyBtn.disabled = false;
      previewCard.style.display = "block";
      resultCard.style.display = "none";
    }).catch(function () {
      dryBtn.disabled = false;
      Swal.fire({ icon: "error", title: "İstek başarısız" });
    });
  });

  applyBtn.addEventListener("click", function () {
    if (lastPlanHadErrors && !skipCheck.checked) {
      Swal.fire({ icon: "warning",
        title: "Hatalı satırlar var",
        text: "Düzeltin ya da 'hatalıları atla' seçeneğini işaretleyin." });
      return;
    }
    applyBtn.disabled = true;
    post(APPLY_URL, { skip_errors: skipCheck.checked ? "1" : "0" }).then(function (j) {
      applyBtn.disabled = false;
      if (!j.success || !j.applied) {
        Swal.fire({ icon: "error", title: j.message || "Uygulama başarısız — hiçbir değişiklik yazılmadı" });
        return;
      }
      var r = j.result || {};
      var p = r.processes || {}, k = r.kpis || {}, st = r.strategy || {};
      var html =
        "<div>✅ Süreç: " + (p.add || 0) + " eklendi, " + (p.update || 0) + " güncellendi</div>" +
        "<div>✅ PG: " + (k.add || 0) + " eklendi, " + (k.update || 0) + " güncellendi</div>" +
        "<div>✅ Strateji: " + (st.strategy || 0) + " ana, " + (st.sub || 0) + " alt, " +
        (st.link || 0) + " süreç bağı</div>";
      (j.warnings || []).forEach(function (w) {
        html += "<div style='color:#b45309;'>⚠️ " + esc(w) + "</div>";
      });
      document.getElementById("si-result").innerHTML = html;
      resultCard.style.display = "block";
      Swal.fire({ icon: "success", title: "İçe aktarma tamamlandı", timer: 1800, showConfirmButton: false });
    }).catch(function () {
      applyBtn.disabled = false;
      Swal.fire({ icon: "error", title: "İstek başarısız" });
    });
  });
})();
