"""SP — eski /sp URL yönlendirmeleri (katman mimarisi Faz 3).

Girdi katmanı `/k-plan/` önekine taşındı (2026-07-17). Yayın çalışıyor; kullanıcı
bookmark'ları, dış linkler ve e-posta içindeki adresler kırılmasın diye eski
`/sp/...` adresleri yeni `/k-plan/strategy/...` adresine yönlendirilir.

Neden **307** (301 değil):
    301 tarayıcıya POST'u GET'e çevirme izni verir — form gönderimleri ve API
    çağrıları sessizce bozulur. 307 metodu ve gövdeyi korur. Süreç modülünün
    mevcut `/surec` redirect'i de 307 kullanıyor (routes_legacy.py); aynı kalıp.

Kalıcıdır — Faz 6 temizliğinde SİLİNMEZ (yol haritası: "eski redirect'leri koru,
bookmark'lar için kalıcı"). İç `url_for` çağrıları zaten yeni path'i üretir;
buraya yalnızca dışarıdan gelen eski adresler düşer.

Bkz. docs/kontrol/ENDPOINT-SOZLESMESI.md
"""

from __future__ import annotations

from flask import redirect, request

from platform_core import app_bp

_YENI_TABAN = "/k-plan/strategy"


def _yonlendir(subpath: str = ""):
    target = f"{_YENI_TABAN}/{subpath}" if subpath else _YENI_TABAN
    qs = request.query_string.decode() if request.query_string else ""
    if qs:
        target = f"{target}?{qs}"
    return redirect(target, code=307)


@app_bp.route("/sp")
@app_bp.route("/sp/")
def sp_katman_legacy_index():
    return _yonlendir()


# NOT: /sp/tv bu kuralın kapsamına girmez — Faz 2'de /k-radar/savas-odasi'na
# taşındı ve kendi redirect'i var (sp_tv_mode_legacy, routes_exec_advisor.py).
# Flask statik kuralı (/sp/tv) dinamik kurala (/sp/<path:subpath>) tercih eder.
@app_bp.route("/sp/<path:subpath>")
def sp_katman_legacy_path(subpath):
    return _yonlendir(subpath)
