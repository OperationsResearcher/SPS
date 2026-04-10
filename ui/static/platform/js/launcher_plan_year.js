/**
 * launcher_plan_year.js — Ana sayfa SP Dönem Yönetimi
 * Bağımlılık: SweetAlert2
 */
(function () {
  "use strict";

  const root = document.getElementById("launcher-plan-year-root");
  if (!root) return;

  const CREATE_URL     = root.dataset.planYearsCreateUrl     || "";
  const SET_ACTIVE_URL = root.dataset.planYearsSetActiveUrl  || "";
  const CAN_MANAGE     = root.dataset.canManage === "true";

  const yearSelect = document.getElementById("lpy-year-select");
  const btnNew     = document.getElementById("lpy-btn-new");
  const btnClose   = document.getElementById("lpy-btn-close");
  const modalNew   = document.getElementById("lpy-modal-new");
  const btnSave    = document.getElementById("lpy-btn-save");

  function getCsrf() {
    const el = document.querySelector('meta[name="csrf-token"]');
    return el ? el.getAttribute("content") : "";
  }

  async function postJson(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrf() },
      body: JSON.stringify(body),
    });
    return res.json();
  }

  function toastOk(msg) {
    Swal.fire({ icon: "success", title: msg, timer: 2000, showConfirmButton: false, toast: true, position: "top-end" });
  }
  function toastErr(msg) {
    Swal.fire({ icon: "error", title: "Hata", text: msg });
  }

  // ── Dönem Değiştir ────────────────────────────────────────────────────────
  if (yearSelect) {
    yearSelect.addEventListener("change", async function () {
      const year = parseInt(this.value, 10);
      if (!year) return;
      try {
        const data = await postJson(SET_ACTIVE_URL, { year });
        if (data.success) {
          window.location.reload();
        } else {
          toastErr(data.message || "Dönem değiştirilemedi.");
        }
      } catch (e) {
        toastErr("Bağlantı hatası.");
      }
    });
  }

  // ── Dönemi Kapat ─────────────────────────────────────────────────────────
  if (btnClose && CAN_MANAGE) {
    btnClose.addEventListener("click", async function () {
      const closeUrl = this.dataset.closeUrl;
      const year     = parseInt(this.dataset.year, 10);
      if (!closeUrl || !year) return;

      const result = await Swal.fire({
        icon: "warning",
        title: `${year} Dönemini Kapat`,
        html: `<p>${year} stratejik plan dönemi kapatılacak. Kapalı dönemler artık düzenlenemez.</p>
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
          toastOk(data.message || `${year} dönemi kapatıldı.`);
          setTimeout(() => window.location.reload(), 1200);
        } else {
          toastErr(data.message || "Dönem kapatılamadı.");
        }
      } catch (e) {
        toastErr("Bağlantı hatası.");
      }
    });
  }

  // ── Modal Aç/Kapat ────────────────────────────────────────────────────────
  function openModal()  { if (modalNew) modalNew.classList.add("open"); }
  function closeModal() { if (modalNew) modalNew.classList.remove("open"); }

  if (btnNew && CAN_MANAGE) btnNew.addEventListener("click", openModal);

  document.querySelectorAll("[data-modal-close='lpy-modal-new']").forEach(function (el) {
    el.addEventListener("click", closeModal);
  });
  if (modalNew) {
    modalNew.addEventListener("click", function (e) {
      if (e.target === modalNew) closeModal();
    });
  }

  // ── Yeni Dönem Kaydet ────────────────────────────────────────────────────
  if (btnSave && CAN_MANAGE) {
    btnSave.addEventListener("click", async function () {
      const yearInput     = document.getElementById("lpy-year");
      const nameInput     = document.getElementById("lpy-name");
      const fromYearInput = document.getElementById("lpy-from-year");

      const newYear  = parseInt((yearInput  ? yearInput.value  : ""), 10);
      const name     = nameInput     ? nameInput.value.trim()            : "";
      const fromYear = fromYearInput ? parseInt(fromYearInput.value, 10) || null : null;

      if (!newYear || newYear < 2000 || newYear > 2100) {
        toastErr("Geçerli bir yıl girin (2000-2100).");
        return;
      }

      btnSave.disabled = true;
      try {
        const payload = { year: newYear };
        if (name)     payload.name      = name;
        if (fromYear) payload.from_year = fromYear;

        const data = await postJson(CREATE_URL, payload);
        if (data.success) {
          toastOk(data.message || `${newYear} dönemi oluşturuldu.`);
          closeModal();
          setTimeout(() => window.location.reload(), 1200);
        } else {
          toastErr(data.message || "Dönem oluşturulamadı.");
        }
      } catch (e) {
        toastErr("Bağlantı hatası.");
      } finally {
        btnSave.disabled = false;
      }
    });
  }
})();
