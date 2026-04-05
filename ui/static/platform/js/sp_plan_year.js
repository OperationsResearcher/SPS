/**
 * sp_plan_year.js — Stratejik Plan Yılı Seçici ve Yönetimi
 * Bağımlılık: SweetAlert2
 */
(function () {
  "use strict";

  const wrap = document.getElementById("sp-index");
  if (!wrap) return;

  const PLAN_YEARS_URL = wrap.dataset.planYearsUrl || "";
  const CREATE_URL = wrap.dataset.planYearsCreateUrl || "";
  const SET_ACTIVE_URL = wrap.dataset.planYearsSetActiveUrl || "";
  const CAN_MANAGE = wrap.dataset.canManage === "true";

  const yearSelect = document.getElementById("sp-plan-year-select");
  const statusBadge = document.getElementById("plan-year-status-badge");
  const btnNew = document.getElementById("btn-plan-year-new");
  const btnClose = document.getElementById("btn-plan-year-close");
  const modalNew = document.getElementById("modal-plan-year-new");
  const btnNewSave = document.getElementById("btn-plan-year-new-save");

  // ── CSRF ──────────────────────────────────────────────────────────────────
  function getCsrf() {
    const el = document.querySelector('meta[name="csrf-token"]');
    return el ? el.getAttribute("content") : "";
  }

  async function postJson(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrf(),
      },
      body: JSON.stringify(body),
    });
    return res.json();
  }

  function toastOk(msg) {
    if (window.Swal) {
      Swal.fire({ icon: "success", title: msg, timer: 2000, showConfirmButton: false, toast: true, position: "top-end" });
    }
  }
  function toastErr(msg) {
    if (window.Swal) {
      Swal.fire({ icon: "error", title: "Hata", text: msg });
    }
  }

  // ── Yıl Değişimi ──────────────────────────────────────────────────────────
  if (yearSelect) {
    yearSelect.addEventListener("change", async function () {
      const year = parseInt(this.value, 10);
      if (!year) return;
      try {
        const data = await postJson(SET_ACTIVE_URL, { year });
        if (data.success) {
          // Sayfayı yenile — strateji ağacı vb. yıla göre sunucu tarafında render ediliyor
          window.location.reload();
        } else {
          toastErr(data.message || "Yıl değiştirilemedi.");
        }
      } catch (e) {
        toastErr("Bağlantı hatası.");
      }
    });
  }

  // ── Yılı Kapat ────────────────────────────────────────────────────────────
  if (btnClose && CAN_MANAGE) {
    btnClose.addEventListener("click", async function () {
      const closeUrl = this.dataset.closeUrl;
      const year = parseInt(this.dataset.year, 10);
      if (!closeUrl || !year) return;

      const result = await Swal.fire({
        icon: "warning",
        title: `${year} Yılını Kapat`,
        html: `<p>${year} stratejik plan yılı kapatılacak. Kapalı yıllar artık düzenlenemez.</p>
               <p><strong>Bu işlem geri alınamaz.</strong></p>`,
        showCancelButton: true,
        confirmButtonText: "Evet, Kapat",
        cancelButtonText: "Vazgeç",
        confirmButtonColor: "#dc2626",
      });
      if (!result.isConfirmed) return;

      try {
        const data = await postJson(closeUrl, {});
        if (data.success) {
          toastOk(data.message || `${year} kapatıldı.`);
          setTimeout(() => window.location.reload(), 1200);
        } else {
          toastErr(data.message || "Yıl kapatılamadı.");
        }
      } catch (e) {
        toastErr("Bağlantı hatası.");
      }
    });
  }

  // ── Yeni Yıl Modalı Aç ────────────────────────────────────────────────────
  if (btnNew && modalNew) {
    btnNew.addEventListener("click", function () {
      modalNew.style.display = "flex";
    });
  }

  // Modal kapat (overlay ve ✕ butonu)
  document.querySelectorAll("[data-modal-close='modal-plan-year-new']").forEach(function (el) {
    el.addEventListener("click", function () {
      if (modalNew) modalNew.style.display = "none";
    });
  });
  if (modalNew) {
    modalNew.addEventListener("click", function (e) {
      if (e.target === modalNew) modalNew.style.display = "none";
    });
  }

  // ── Yeni Yıl Kaydet ───────────────────────────────────────────────────────
  if (btnNewSave) {
    btnNewSave.addEventListener("click", async function () {
      const yearInput = document.getElementById("pyn-year");
      const nameInput = document.getElementById("pyn-name");
      const fromYearInput = document.getElementById("pyn-from-year");

      const newYear = parseInt((yearInput ? yearInput.value : ""), 10);
      const name = nameInput ? nameInput.value.trim() : "";
      const fromYear = fromYearInput ? parseInt(fromYearInput.value, 10) || null : null;

      if (!newYear || newYear < 2000 || newYear > 2100) {
        toastErr("Geçerli bir yıl girin (2000-2100).");
        return;
      }

      btnNewSave.disabled = true;
      try {
        const payload = { year: newYear };
        if (name) payload.name = name;
        if (fromYear) payload.from_year = fromYear;

        const data = await postJson(CREATE_URL, payload);
        if (data.success) {
          toastOk(data.message || `${newYear} yılı planı oluşturuldu.`);
          if (modalNew) modalNew.style.display = "none";
          setTimeout(() => window.location.reload(), 1200);
        } else {
          toastErr(data.message || "Plan yılı oluşturulamadı.");
        }
      } catch (e) {
        toastErr("Bağlantı hatası.");
      } finally {
        btnNewSave.disabled = false;
      }
    });
  }
})();
