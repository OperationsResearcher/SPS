/**
 * SWOT Analysis - AJAX add/delete
 */
(function () {
    "use strict";

    var el = document.querySelector("[data-swot-url]");
    var swotUrl = el ? el.getAttribute("data-swot-url") : null;
    if (!swotUrl) swotUrl = "/strategy/swot";

    function getCookie(name) {
        var v = document.cookie.match("(^|;) ?" + name + "=([^;]*)(;|$)");
        return v ? v[2] : null;
    }

    function csrfHeader() {
        var token = document.querySelector('meta[name="csrf-token"]') && document.querySelector('meta[name="csrf-token"]').getAttribute("content");
        return token ? { "X-CSRFToken": token } : {};
    }

    document.querySelectorAll(".swot-add-form").forEach(function (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault();
            var input = form.querySelector(".swot-input");
            var content = (input && input.value || "").trim();
            if (!content) return;
            var category = form.dataset.category;
            var fd = new FormData();
            fd.append("action", "add");
            fd.append("category", category);
            fd.append("content", content);
            var xhr = new XMLHttpRequest();
            xhr.open("POST", swotUrl);
            xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            xhr.onload = function () {
                if (xhr.status === 200) {
                    var res = JSON.parse(xhr.responseText || "{}");
                    if (res.success && res.id) {
                        var ul = form.previousElementSibling;
                        if (ul && ul.classList.contains("swot-list")) {
                            var li = document.createElement("li");
                            li.dataset.id = res.id;
                            li.innerHTML = "<span>" + escapeHtml(res.content) + "</span><button type=\"button\" class=\"btn btn-sm btn-outline-danger swot-delete\">Sil</button>";
                            ul.appendChild(li);
                            bindDelete(li.querySelector(".swot-delete"));
                        }
                        input.value = "";
                    }
                } else if (typeof Swal !== "undefined") {
                    Swal.fire({ icon: "error", title: "Hata", text: "Eklenemedi." });
                }
            };
            xhr.send(fd);
        });
    });

    function escapeHtml(s) {
        var div = document.createElement("div");
        div.textContent = s;
        return div.innerHTML;
    }

    function bindDelete(btn) {
        if (!btn) return;
        btn.addEventListener("click", function () {
            var li = btn.closest("li");
            var id = li && li.dataset.id;
            if (!id) return;
            Swal.fire({ title: "Emin misiniz?", text: "Silmek istediğinize emin misiniz?", icon: "warning", showCancelButton: true, confirmButtonText: "Sil", cancelButtonText: "İptal" }).then(function (r) {
                if (r.isConfirmed) doDelete(id, li);
            });
        });
    }

    function doDelete(id, li) {
        var fd = new FormData();
        fd.append("action", "delete");
        fd.append("id", id);
        var xhr = new XMLHttpRequest();
        xhr.open("POST", swotUrl);
        xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
        xhr.onload = function () {
            if (xhr.status === 200) {
                var res = JSON.parse(xhr.responseText || "{}");
                if (res.success && li && li.parentNode) li.remove();
            }
        };
        xhr.send(fd);
    }

    document.querySelectorAll(".swot-delete").forEach(bindDelete);
})();
