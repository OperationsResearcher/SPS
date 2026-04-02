/**
 * Kokpitim ortak toast — SweetAlert2; showToast yoksa tanımlar.
 */
(function (global) {
  "use strict";

  function showAppToast(type, message, title) {
    var msg = message != null ? String(message) : "";
    if (!msg && title) msg = String(title);
    if (typeof Swal !== "undefined") {
      var icon =
        type === "success"
          ? "success"
          : type === "error"
            ? "error"
            : type === "warning"
              ? "warning"
              : "info";
      Swal.fire({
        toast: true,
        position: "top-end",
        icon: icon,
        title: msg || title || "",
        showConfirmButton: false,
        timer: 2800,
      });
    } else {
      global.alert(msg || title || "");
    }
  }

  global.showAppToast = showAppToast;
  if (typeof global.showToast !== "function") {
    global.showToast = showAppToast;
  }
})(typeof window !== "undefined" ? window : this);
