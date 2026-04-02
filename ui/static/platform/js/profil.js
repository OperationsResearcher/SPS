/**
 * profil.js
 * Kural: alert/confirm/prompt YASAK - SweetAlert2 kullan
 * Kural: Jinja2 {{ }} YASAK - URL data-* ile gelir
 */
(function () {
  "use strict";

  function getCsrf() {
    var m = document.querySelector('meta[name="csrf-token"]');
    return m ? m.content : "";
  }

  function swalSuccess(msg) {
    Swal.fire({
      toast: true, position: "top-end", icon: "success",
      title: msg, showConfirmButton: false, timer: 2500, timerProgressBar: true
    });
  }

  function swalError(msg) {
    Swal.fire({ icon: "error", title: "Hata", text: msg, confirmButtonColor: "#dc2626" });
  }

  function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function validatePhone(phone) {
    return /^(\+90\s?)?(\(?\d{3}\)?\s?)?\d{3}[\s-]?\d{2}[\s-]?\d{2}$/.test(phone.replace(/\s/g, ""));
  }

  var wrap = document.querySelector(".profil-wrap");
  if (!wrap) return;

  var UPDATE_URL = wrap.dataset.updateUrl;
  var UPLOAD_URL = wrap.dataset.uploadUrl;

  /* ---- Fotoğraf yükleme ---- */
  var photoInput = document.getElementById("profilePhotoInput");
  var btnFoto    = document.getElementById("btn-foto-yukle");
  var progressEl = document.getElementById("photoUploadProgress");

  if (btnFoto && photoInput) {
    btnFoto.addEventListener("click", function () { photoInput.click(); });
  }

  if (photoInput && UPLOAD_URL) {
    photoInput.addEventListener("change", function (e) {
      var file = e.target.files[0];
      photoInput.value = "";
      if (!file) return;

      var allowedTypes = ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp"];
      if (allowedTypes.indexOf(file.type) === -1) {
        swalError("Geçersiz dosya tipi. PNG, JPG, GIF veya WEBP seçin.");
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        swalError("Dosya boyutu çok büyük. Maksimum 5MB yükleyebilirsiniz.");
        return;
      }

      if (progressEl) progressEl.style.display = "block";
      if (btnFoto) btnFoto.disabled = true;

      var fd = new FormData();
      fd.append("file", file);
      fd.append("csrf_token", getCsrf());

      fetch(UPLOAD_URL, {
        method: "POST",
        headers: { "X-CSRFToken": getCsrf() },
        body: fd
      })
        .then(function (r) {
          var ct = r.headers.get("content-type") || "";
          if (!ct.includes("application/json")) {
            return r.text().then(function (txt) {
              console.error("Geçersiz yanıt:", txt);
              throw new Error("Sunucudan geçersiz yanıt alındı (HTTP " + r.status + ").");
            });
          }
          return r.json();
        })
        .then(function (d) {
          if (progressEl) progressEl.style.display = "none";
          if (btnFoto) btnFoto.disabled = false;

          if (d.success) {
            var photoUrl = d.photo_url;
            if (!photoUrl.startsWith("http://") && !photoUrl.startsWith("https://")) {
              if (!photoUrl.startsWith("/static/")) {
                photoUrl = "/static/" + photoUrl.replace(/^\/?static\//, "").replace(/^\//, "");
              }
            }
            var container   = document.getElementById("profilePhotoContainer");
            var existingImg = document.getElementById("profilePhotoImg");
            var placeholder = document.getElementById("profilePhotoPlaceholder");

            if (existingImg) {
              existingImg.src = photoUrl + "?t=" + Date.now();
              existingImg.style.display = "";
              if (placeholder) placeholder.style.display = "none";
            } else {
              var newImg = document.createElement("img");
              newImg.id        = "profilePhotoImg";
              newImg.src       = photoUrl + "?t=" + Date.now();
              newImg.alt       = "Profil";
              newImg.className = "profil-avatar-img";
              newImg.onerror   = function () {
                this.style.display = "none";
                if (placeholder) placeholder.style.display = "flex";
              };
              if (placeholder) placeholder.style.display = "none";
              if (container) container.insertBefore(newImg, container.firstChild);
            }
            swalSuccess("Profil fotoğrafı güncellendi.");
          } else {
            swalError(d.message || "Fotoğraf yüklenemedi.");
          }
        })
        .catch(function (err) {
          if (progressEl) progressEl.style.display = "none";
          if (btnFoto) btnFoto.disabled = false;
          swalError(err.message || "Sunucuya bağlanılamadı.");
        });
    });
  }

  /* ---- Form submit ---- */
  var form = document.getElementById("profileForm");
  if (form && UPDATE_URL) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      var email      = (document.getElementById("pf-email").value || "").trim();
      var phone      = (document.getElementById("pf-phone").value || "").trim();
      var curPass    = document.getElementById("pf-cur-pass").value;
      var newPass    = document.getElementById("pf-new-pass").value;
      var confirmPas = document.getElementById("pf-confirm-pass").value;

      if (email && !validateEmail(email)) {
        swalError("Lütfen geçerli bir e-posta adresi girin.");
        return;
      }
      if (phone && !validatePhone(phone)) {
        swalError("Lütfen geçerli bir telefon numarası girin. (Örnek: 0555 123 45 67)");
        return;
      }
      if (newPass && newPass.length < 6) {
        swalError("Yeni şifre en az 6 karakter olmalıdır.");
        return;
      }
      if (newPass && newPass !== confirmPas) {
        swalError("Yeni şifreler eşleşmiyor.");
        return;
      }
      if ((newPass || confirmPas) && !curPass) {
        swalError("Şifre değiştirmek için mevcut şifrenizi girmelisiniz.");
        return;
      }

      var payload = {
        first_name:   document.getElementById("pf-fname").value.trim(),
        last_name:    document.getElementById("pf-lname").value.trim(),
        email:        email,
        phone_number: phone,
        job_title:    document.getElementById("pf-title").value.trim(),
        department:   document.getElementById("pf-dept").value.trim()
      };
      if (curPass || newPass) {
        payload.current_password = curPass;
        payload.new_password     = newPass;
      }

      fetch(UPDATE_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrf()
        },
        body: JSON.stringify(payload)
      })
        .then(function (r) {
          var ct = r.headers.get("content-type") || "";
          if (!ct.includes("application/json")) {
            return r.text().then(function () {
              throw new Error("Sunucudan geçersiz yanıt alındı. Sayfayı yenileyip tekrar deneyin.");
            });
          }
          return r.json();
        })
        .then(function (d) {
          if (d.success) {
            swalSuccess(d.message || "Profil güncellendi.");
            document.getElementById("pf-cur-pass").value     = "";
            document.getElementById("pf-new-pass").value     = "";
            document.getElementById("pf-confirm-pass").value = "";
          } else {
            swalError(d.message || "Güncelleme başarısız.");
          }
        })
        .catch(function (err) {
          swalError(err.message || "Sunucuya bağlanılamadı.");
        });
    });
  }

})();
