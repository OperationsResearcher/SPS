/* Same-origin değiştirici isteklere (POST/PUT/PATCH/DELETE) X-CSRFToken ekler.
 * Token <meta name="csrf-token"> içinden okunur; çağıran kendi başlığını verdiyse dokunulmaz. */
(function () {
    "use strict";
    var orig = window.fetch;
    if (!orig) return;
    var SAFE = { GET: 1, HEAD: 1, OPTIONS: 1 };

    window.fetch = function (input, init) {
        try {
            init = init || {};
            var method = String(init.method || (input && input.method) || "GET").toUpperCase();
            if (!SAFE[method]) {
                var url = typeof input === "string" ? input : (input && input.url) || "";
                if (new URL(url, window.location.href).origin === window.location.origin) {
                    var headers = new Headers(init.headers || (input && input.headers) || {});
                    if (!headers.has("X-CSRFToken")) {
                        var meta = document.querySelector('meta[name="csrf-token"]');
                        if (meta && meta.content) headers.set("X-CSRFToken", meta.content);
                    }
                    init.headers = headers;
                }
            }
        } catch (e) {
            /* sarmalayıcı isteği asla bozmaz */
        }
        return orig.call(this, input, init);
    };
})();
