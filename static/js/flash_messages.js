/**
 * Renders Flask flash messages via SweetAlert2.
 * Expects #flash-messages container with data-messages attribute (JSON).
 */
(function () {
    "use strict";
    var el = document.getElementById("flash-messages");
    if (!el || !el.dataset.messages) return;
    try {
        var messages = JSON.parse(el.dataset.messages);
        messages.forEach(function (m) {
            var cat = m[0] || "info";
            var text = m[1] || "";
            var icon = cat === "success" ? "success" : cat === "danger" ? "error" : "info";
            if (typeof Swal !== "undefined") {
                Swal.fire({ icon: icon, title: text, toast: true, position: "top-end", showConfirmButton: false, timer: 3000 });
            }
        });
    } catch (e) {}
})();
