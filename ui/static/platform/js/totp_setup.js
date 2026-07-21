/**
 * 2FA kurulum ekranı — QR okut, kodu doğrula, yedek kodları göster.
 *
 * Sunucu sözleşmesi (app/routes/totp.py:74 totp_verify_setup):
 *   POST form-encoded { code, csrf_token }
 *   200 -> { success: true, message, backup_codes: [...] }
 *   400 -> { success: false, message }
 *
 * URL'ler Jinja'dan data-* ile gelir (KURALLAR §3: JS'de {{ }} yasak).
 */
(function () {
  "use strict";

  var kok = document.getElementById("totp-setup");
  if (!kok) return;

  var form      = document.getElementById("totp-setup-form");
  var kodInput  = document.getElementById("code-input");
  var btnVerify = document.getElementById("btn-verify");
  var sarmal    = document.getElementById("backup-wrap");
  var kodlarEl  = document.getElementById("backup-codes");

  var verifyUrl = kok.dataset.verifyUrl;
  var doneUrl   = kok.dataset.doneUrl;

  function t(s) { return (window.t ? window.t(s) : s); }

  function hata(mesaj) {
    if (typeof Swal !== "undefined") {
      Swal.fire({ icon: "error", title: t("Hata"), text: mesaj, confirmButtonColor: "#dc2626" });
    } else {
      // SweetAlert2 yüklenemediyse sessiz kalmaktansa yedek (KURALLAR §3 istisnası)
      alert(mesaj);
    }
  }

  function panoyaKopyala(metin, btn) {
    var bitti = function () {
      if (!btn) return;
      var eski = btn.innerHTML;
      btn.innerHTML = '<i class="fas fa-check"></i>';
      setTimeout(function () { btn.innerHTML = eski; }, 1400);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(metin).then(bitti).catch(function () {
        hata(t("Panoya kopyalanamadı."));
      });
      return;
    }
    // Eski tarayıcı yedeği
    var ta = document.createElement("textarea");
    ta.value = metin;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); bitti(); }
    catch (e) { hata(t("Panoya kopyalanamadı.")); }
    finally { document.body.removeChild(ta); }
  }

  // Yalnız rakam kabul et
  kodInput.addEventListener("input", function () {
    this.value = this.value.replace(/\D/g, "");
  });

  var secretBtn = document.getElementById("btn-copy-secret");
  if (secretBtn) {
    secretBtn.addEventListener("click", function () {
      var el = document.getElementById("totp-secret");
      panoyaKopyala(el ? el.textContent.trim() : "", secretBtn);
    });
  }

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    var kod = (kodInput.value || "").trim();
    if (kod.length !== 6) {
      hata(t("6 haneli doğrulama kodunu girin."));
      return;
    }

    btnVerify.disabled = true;
    var eskiEtiket = btnVerify.innerHTML;
    btnVerify.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ' + t("Doğrulanıyor…");

    try {
      var govde = new FormData(form);
      var yanit = await fetch(verifyUrl, {
        method: "POST",
        body: govde,
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      var veri = await yanit.json();

      if (!yanit.ok || !veri.success) {
        hata(veri.message || t("Doğrulama kodu hatalı."));
        kodInput.value = "";
        kodInput.focus();
        return;
      }

      // Başarılı: yedek kodları göster, formu kilitle.
      // Bu ekran BİR DAHA GÖSTERİLMEZ — kullanıcı kaydetmeden çıkmamalı.
      form.style.display = "none";
      kodlarEl.textContent = (veri.backup_codes || []).join("\n");
      sarmal.style.display = "block";
      sarmal.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } catch (err) {
      hata(t("Sunucuya erişilemedi."));
    } finally {
      btnVerify.disabled = false;
      btnVerify.innerHTML = eskiEtiket;
    }
  });

  var backupBtn = document.getElementById("btn-copy-backup");
  if (backupBtn) {
    backupBtn.addEventListener("click", function () {
      panoyaKopyala(kodlarEl.textContent, backupBtn);
    });
  }

  var doneBtn = document.getElementById("btn-done");
  if (doneBtn) {
    doneBtn.addEventListener("click", function () {
      window.location.href = doneUrl;
    });
  }
})();
