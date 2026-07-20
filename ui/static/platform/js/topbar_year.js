/* Global yıl seçici — üst bar (yıl bazlı program, 2026-07-21)
 *
 * Yıl bazlılık sistemin temel çalışma biçimi (K5), bu yüzden seçici tek bir
 * sayfaya değil ÜST BARA ait: her ekranda aynı yerde, aynı davranışta.
 *
 * Davranış (kullanıcı kararı): seçince ANINDA uygula + sayfayı yenile.
 * Böylece bütün ekran o yıla döner — mevcut plan yılı çubuklarının deseniyle
 * aynı, kullanıcı için tek ve tanıdık bir kural.
 *
 * Uç: POST /api/view-year  (yalnız session'a yazar, veri değiştirmez)
 * NOT: `.../plan-years/set-active` KULLANILMAZ — o uç yönetici rolü istiyor;
 * yıl seçmek ise görüntüleme eylemidir, standart kullanıcı da yapabilmeli.
 */
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    var sec = document.getElementById("topbar-year-select");
    if (!sec) return;

    var oncekiDeger = sec.value;

    sec.addEventListener("change", function () {
      var yil = parseInt(sec.value, 10);
      if (!yil) return;

      sec.disabled = true;

      var meta = document.querySelector('meta[name="csrf-token"]');
      var basliklar = { "Content-Type": "application/json" };
      if (meta && meta.content) basliklar["X-CSRFToken"] = meta.content;

      fetch(sec.dataset.setActiveUrl || "/api/view-year", {
        method: "POST",
        headers: basliklar,
        credentials: "same-origin",
        body: JSON.stringify({ year: yil })
      })
        .then(function (r) { return r.json().catch(function () { return {}; }); })
        .then(function (d) {
          if (d && d.success) {
            // Yıl session'a yazıldı; sayfayı yenile ki tüm ekran o yıla dönsün.
            window.location.reload();
            return;
          }
          geriAl(d && d.message);
        })
        .catch(function () { geriAl(null); });

      function geriAl(mesaj) {
        sec.value = oncekiDeger;
        sec.disabled = false;
        var metin = mesaj || "Yıl değiştirilemedi.";
        if (window.Swal && window.Swal.fire) {
          window.Swal.fire({
            icon: "error", title: metin, toast: true, position: "top-end",
            showConfirmButton: false, timer: 2600
          });
        } else {
          console.error("[topbar-year]", metin);
        }
      }
    });
  });
})();
