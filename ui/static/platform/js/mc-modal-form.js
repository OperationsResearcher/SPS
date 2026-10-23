/**
 * mc-modal-form.js — Admin "Kullanıcı Düzenle" ile aynı native modal stili
 * openMcFormModal({ title, iconClass, bodyHtml, confirmText, cancelText, onConfirm })
 * onConfirm({ showValidation, clearValidation }) → false | payload
 */
(function () {
  "use strict";

  /**
   * @param {object} opts
   * @param {string} opts.title
   * @param {string} [opts.iconClass] Font Awesome sınıfları, örn. "fas fa-user-edit"
   * @param {string} opts.bodyHtml — mc-form-label / mc-form-input ile işaretlenmiş HTML
   * @param {string} [opts.confirmText]
   * @param {string} [opts.cancelText]
   * @param {function} opts.onConfirm — false dönerse modal açık kalır
   * @returns {Promise<null|*>}
   */
  window.openMcFormModal = function openMcFormModal(opts) {
    const o = opts || {};
    const title = o.title || t("Düzenle");
    const iconClass = o.iconClass || "fas fa-pen-to-square";
    const bodyHtml = o.bodyHtml || "";
    const confirmText = o.confirmText || t("Kaydet");
    const cancelText = o.cancelText || t("İptal");
    const onConfirm = o.onConfirm;

    return new Promise(function (resolve) {
      const overlay = document.getElementById("mc-modal-form-global");
      const bodyEl = document.getElementById("mc-modal-form-body");
      const titleEl = document.getElementById("mc-modal-form-title");
      const iconEl = document.getElementById("mc-modal-form-icon");
      const saveLabel = document.getElementById("mc-modal-form-save-label");
      const cancelBtn = document.getElementById("mc-modal-form-cancel");
      const saveBtn = document.getElementById("mc-modal-form-save");
      const saveIcon = document.getElementById("mc-modal-form-save-icon");
      const closeBtn = document.getElementById("mc-modal-form-close");
      const valEl = document.getElementById("mc-modal-form-validation");

      if (!overlay || !bodyEl || !titleEl || !saveBtn) {
        resolve(null);
        return;
      }

      if (cancelBtn) cancelBtn.style.display = "";
      if (saveIcon) saveIcon.style.display = "";

      function clearValidation() {
        if (valEl) {
          valEl.hidden = true;
          valEl.textContent = "";
        }
      }

      function showValidation(msg) {
        if (!valEl) return;
        valEl.textContent = msg || "";
        valEl.hidden = !msg;
      }

      titleEl.textContent = title;
      if (iconEl) iconEl.className = iconClass;
      if (saveLabel) saveLabel.textContent = confirmText;
      if (cancelBtn) cancelBtn.textContent = cancelText;
      bodyEl.innerHTML = bodyHtml;
      clearValidation();

      function close() {
        overlay.classList.remove("open");
        overlay.setAttribute("aria-hidden", "true");
        document.removeEventListener("keydown", onKey);
      }

      function cancel() {
        close();
        resolve(null);
      }

      function onKey(e) {
        if (e.key === "Escape") cancel();
        // Tek satırlık alanda Enter = Kaydet (textarea'da satır sonu kalır)
        else if (e.key === "Enter" && e.target && e.target.tagName === "INPUT" && overlay.contains(e.target)) {
          e.preventDefault();
          submit();
        }
      }

      function submit() {
        clearValidation();
        if (typeof onConfirm !== "function") {
          close();
          resolve(null);
          return;
        }
        var result = onConfirm({ showValidation: showValidation, clearValidation: clearValidation });
        if (result === false) return;
        close();
        resolve(result);
      }

      overlay.onclick = function (e) {
        if (e.target === overlay) cancel();
      };
      if (closeBtn) closeBtn.onclick = cancel;
      if (cancelBtn) cancelBtn.onclick = cancel;
      saveBtn.onclick = submit;

      overlay.classList.add("open");
      overlay.setAttribute("aria-hidden", "false");
      document.addEventListener("keydown", onKey);

      requestAnimationFrame(function () {
        var first = bodyEl.querySelector("input, textarea, select");
        if (first) first.focus();
      });
    });
  };

  /**
   * Tek alanlı metin istemi (Swal `input:` yerine). Hata mesajı alanın altında görünür.
   * @param {object} opts
   * @param {string} opts.title
   * @param {string} [opts.label] alan etiketi
   * @param {string} [opts.introHtml] alanın üstünde gösterilecek güvenilir HTML
   * @param {string} [opts.value] başlangıç değeri
   * @param {string} [opts.placeholder]
   * @param {boolean} [opts.textarea] çok satırlı alan
   * @param {string} [opts.requiredMessage] verilirse alan boş bırakılamaz, mesaj alanın altında çıkar
   * @param {string} [opts.iconClass] @param {string} [opts.confirmText] @param {string} [opts.cancelText]
   * @returns {Promise<null|string>} iptalde null, aksi halde kırpılmış metin
   */
  window.openMcTextPrompt = function openMcTextPrompt(opts) {
    var o = opts || {};
    function esc(v) {
      return String(v == null ? "" : v).replace(/&/g, "&amp;").replace(/</g, "&lt;")
        .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }
    var field = o.textarea
      ? '<textarea id="mc-prompt-input" class="mc-form-input" rows="3" placeholder="' + esc(o.placeholder) + '">' + esc(o.value) + "</textarea>"
      : '<input id="mc-prompt-input" type="text" class="mc-form-input" value="' + esc(o.value) + '" placeholder="' + esc(o.placeholder) + '">';
    var html =
      (o.introHtml ? '<div class="mc-prompt-intro">' + o.introHtml + "</div>" : "") +
      '<div class="mc-form-field">' +
      (o.label ? '<label class="mc-form-label" for="mc-prompt-input">' + esc(o.label) + "</label>" : "") +
      field +
      '<div class="mc-form-error" id="mc-prompt-error" role="alert" hidden></div></div>';
    return window.openMcFormModal({
      title: o.title,
      iconClass: o.iconClass,
      bodyHtml: html,
      confirmText: o.confirmText,
      cancelText: o.cancelText,
      onConfirm: function () {
        var input = document.getElementById("mc-prompt-input");
        var err = document.getElementById("mc-prompt-error");
        var val = (input ? input.value : "").trim();
        if (o.requiredMessage && !val) {
          if (err) { err.textContent = o.requiredMessage; err.hidden = false; }
          if (input) { input.classList.add("mc-form-input--error"); input.setAttribute("aria-invalid", "true"); input.focus(); }
          return false;
        }
        return { text: val };
      },
    }).then(function (r) { return r ? r.text : null; });
  };

  /**
   * Salt okunur bilgi penceresi (footer’da yalnızca Tamam)
   * @param {object} opts
   * @param {string} opts.title
   * @param {string} opts.bodyHtml — HTML paragraflar
   * @param {string} [opts.iconClass]
   * @param {string} [opts.confirmText] varsayılan "Tamam"
   */
  window.openMcInfoModal = function openMcInfoModal(opts) {
    var o = opts || {};
    var title = o.title || t("Bilgi");
    var bodyHtml = o.bodyHtml || "";
    var iconClass = o.iconClass || "fas fa-circle-info";
    var confirmText = o.confirmText || t("Tamam");

    return new Promise(function (resolve) {
      var overlay = document.getElementById("mc-modal-form-global");
      var bodyEl = document.getElementById("mc-modal-form-body");
      var titleEl = document.getElementById("mc-modal-form-title");
      var iconEl = document.getElementById("mc-modal-form-icon");
      var saveLabel = document.getElementById("mc-modal-form-save-label");
      var cancelBtn = document.getElementById("mc-modal-form-cancel");
      var saveBtn = document.getElementById("mc-modal-form-save");
      var saveIcon = document.getElementById("mc-modal-form-save-icon");
      var closeBtn = document.getElementById("mc-modal-form-close");
      var valEl = document.getElementById("mc-modal-form-validation");

      if (!overlay || !bodyEl || !titleEl || !saveBtn) {
        resolve(false);
        return;
      }

      if (valEl) {
        valEl.hidden = true;
        valEl.textContent = "";
      }

      titleEl.textContent = title;
      if (iconEl) iconEl.className = iconClass;
      if (saveLabel) saveLabel.textContent = confirmText;
      if (cancelBtn) cancelBtn.style.display = "none";
      if (saveIcon) saveIcon.style.display = "none";

      bodyEl.innerHTML =
        '<div class="mc-modal-info-body">' + bodyHtml + "</div>";

      function finish() {
        overlay.classList.remove("open");
        overlay.setAttribute("aria-hidden", "true");
        document.removeEventListener("keydown", onKey);
        if (cancelBtn) cancelBtn.style.display = "";
        if (saveIcon) saveIcon.style.display = "";
        resolve(true);
      }

      function onKey(e) {
        if (e.key === "Escape") finish();
      }

      overlay.onclick = function (e) {
        if (e.target === overlay) finish();
      };
      if (closeBtn) closeBtn.onclick = finish;
      saveBtn.onclick = finish;

      overlay.classList.add("open");
      overlay.setAttribute("aria-hidden", "false");
      document.addEventListener("keydown", onKey);

      requestAnimationFrame(function () {
        if (saveBtn) saveBtn.focus();
      });
    });
  };
})();
