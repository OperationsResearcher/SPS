// 2FA Profil Yönetimi
(function () {
  "use strict";
  const card = document.getElementById("twofa-card");
  if (!card) return;

  const URLS = {
    status:  card.dataset.statusUrl,
    init:    card.dataset.initUrl,
    verify:  card.dataset.verifyUrl,
    disable: card.dataset.disableUrl,
  };

  function show(id) { document.getElementById(id).style.display = "block"; }
  function hide(id) { document.getElementById(id).style.display = "none"; }

  function getCsrfToken() {
    const m = document.querySelector('meta[name="csrf-token"]');
    return m ? m.content : "";
  }

  function postForm(url, data) {
    const fd = new FormData();
    for (const k in data) fd.append(k, data[k]);
    return fetch(url, {
      method: "POST",
      body: fd,
      headers: { "X-CSRFToken": getCsrfToken() },
      credentials: "same-origin",
    }).then(r => r.json());
  }

  function postJson(url) {
    return fetch(url, {
      method: "POST",
      headers: { "X-CSRFToken": getCsrfToken(), "Content-Type": "application/json" },
      credentials: "same-origin",
      body: "{}",
    }).then(r => r.json());
  }

  // ─── Durum yükle ────────────────────────────────────────────────────────
  function loadStatus() {
    hide("twofa-off"); hide("twofa-on"); show("twofa-loading");
    fetch(URLS.status, { credentials: "same-origin" })
      .then(r => r.json())
      .then(j => {
        hide("twofa-loading");
        if (j.enabled) {
          document.getElementById("twofa-backup-count").textContent = j.backup_codes_remaining;
          show("twofa-on");
        } else {
          show("twofa-off");
        }
      })
      .catch(() => {
        hide("twofa-loading");
        show("twofa-off");
      });
  }
  loadStatus();

  // ─── 2FA AÇIK: Etkinleştir ──────────────────────────────────────────────
  document.getElementById("twofa-enable-btn").addEventListener("click", function () {
    document.getElementById("twofa-setup-error").style.display = "none";
    document.getElementById("twofa-code-input").value = "";
    postJson(URLS.init).then(j => {
      if (!j.success) {
        if (window.Swal) Swal.fire({ toast: true, position: "top-end", icon: "error", title: j.message, showConfirmButton: false, timer: 3000 });
        else alert(j.message || "Hata");
        return;
      }
      document.getElementById("twofa-qr").src = j.qr_code;
      document.getElementById("twofa-secret").textContent = j.secret;
      document.getElementById("twofa-setup-modal").style.display = "flex";
    });
  });

  // ─── Modal: Kurulum kapatma ─────────────────────────────────────────────
  function closeSetupModal() {
    document.getElementById("twofa-setup-modal").style.display = "none";
  }
  document.getElementById("twofa-setup-close").addEventListener("click", closeSetupModal);
  document.getElementById("twofa-setup-cancel").addEventListener("click", closeSetupModal);

  // ─── Modal: Doğrula ─────────────────────────────────────────────────────
  document.getElementById("twofa-setup-verify").addEventListener("click", function () {
    const code = document.getElementById("twofa-code-input").value.trim();
    const errEl = document.getElementById("twofa-setup-error");
    errEl.style.display = "none";
    if (!/^\d{6}$/.test(code)) {
      errEl.textContent = "Lütfen 6 haneli doğrulama kodunu girin.";
      errEl.style.display = "block";
      return;
    }
    const btn = this;
    btn.disabled = true;
    const orig = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Doğrulanıyor…';
    postForm(URLS.verify, { code: code })
      .then(j => {
        btn.disabled = false;
        btn.innerHTML = orig;
        if (!j.success) {
          errEl.textContent = j.message || "Doğrulama hatalı.";
          errEl.style.display = "block";
          return;
        }
        // Başarılı — backup kodlarını göster
        closeSetupModal();
        const list = document.getElementById("twofa-backup-list");
        list.innerHTML = "";
        (j.backup_codes || []).forEach(c => {
          const div = document.createElement("div");
          div.style.cssText = "padding:6px 10px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:4px;text-align:center;";
          div.textContent = c;
          list.appendChild(div);
        });
        document.getElementById("twofa-backup-modal").style.display = "flex";
      });
  });

  // ─── Modal: Backup kodlar kopyala / kapat ───────────────────────────────
  document.getElementById("twofa-backup-copy").addEventListener("click", function () {
    const codes = Array.from(document.querySelectorAll("#twofa-backup-list div")).map(d => d.textContent).join("\n");
    navigator.clipboard.writeText(codes).then(() => {
      const btn = this;
      const orig = btn.innerHTML;
      btn.innerHTML = '<i class="fas fa-check"></i> Kopyalandı';
      setTimeout(() => btn.innerHTML = orig, 1500);
    });
  });
  document.getElementById("twofa-backup-done").addEventListener("click", function () {
    document.getElementById("twofa-backup-modal").style.display = "none";
    loadStatus();
  });

  // ─── 2FA KAPALI: Devre Dışı Bırak ───────────────────────────────────────
  document.getElementById("twofa-disable-btn").addEventListener("click", function () {
    document.getElementById("twofa-disable-password").value = "";
    document.getElementById("twofa-disable-error").style.display = "none";
    document.getElementById("twofa-disable-modal").style.display = "flex";
  });
  document.getElementById("twofa-disable-cancel").addEventListener("click", function () {
    document.getElementById("twofa-disable-modal").style.display = "none";
  });
  document.getElementById("twofa-disable-confirm").addEventListener("click", function () {
    const pw = document.getElementById("twofa-disable-password").value;
    const errEl = document.getElementById("twofa-disable-error");
    errEl.style.display = "none";
    if (!pw) {
      errEl.textContent = "Şifrenizi girin.";
      errEl.style.display = "block";
      return;
    }
    const btn = this;
    btn.disabled = true;
    postForm(URLS.disable, { password: pw })
      .then(j => {
        btn.disabled = false;
        if (!j.success) {
          errEl.textContent = j.message || "Hata";
          errEl.style.display = "block";
          return;
        }
        document.getElementById("twofa-disable-modal").style.display = "none";
        if (window.Swal) Swal.fire({ toast: true, position: "top-end", icon: "info", title: "2FA devre dışı bırakıldı", showConfirmButton: false, timer: 2500 });
        loadStatus();
      });
  });
})();
