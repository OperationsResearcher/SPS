"""Rapor katmanı — eski URL yönlendirmeleri (katman mimarisi Faz 4).

Rapor katmanı `/k-report/` önekinde birleşti (2026-07-17). Önceden iki önek vardı:
`/k-rapor` (35 route) ve `/reports` (106 route). Yayın çalışıyor; bookmark'lar,
e-posta içindeki rapor linkleri ve dış paylaşımlar kırılmasın diye ikisi de
kalıcı olarak yeni adrese yönlendirilir.

Neden **307** (301 değil):
    301 tarayıcıya POST'u GET'e çevirme izni verir — rapor üretme/export uçları
    (PDF/Excel/sunum generate) POST ile çağrılıyor, gövdeleri korunmalı.
    Faz 3'te aynı kalıp kullanıldı.

⚠️ `/reports/daily`, `/reports/weekly`, `/reports/monthly`, `/reports/dashboard`,
`/reports/performance/<id>` — bunlar `ai_bp`/`api_bp` (dış REST API) route'ları,
`app_bp` DEĞİL. Katman mimarisi UI katmanıdır; dış API sözleşmesi bozulmaz.
Flask daha spesifik statik kuralı dinamik `<path:subpath>` kuralına tercih eder,
bu yüzden o adresler buraya düşmez ve çalışmaya devam eder.

Kalıcıdır — Faz 6 temizliğinde SİLİNMEZ.
Bkz. docs/kontrol/ENDPOINT-SOZLESMESI.md
"""

from __future__ import annotations

from flask import redirect, request

from platform_core import app_bp

_YENI_TABAN = "/k-report"


def _yonlendir(subpath: str = ""):
    target = f"{_YENI_TABAN}/{subpath}" if subpath else _YENI_TABAN
    qs = request.query_string.decode() if request.query_string else ""
    if qs:
        target = f"{target}?{qs}"
    return redirect(target, code=307)


# ── /k-rapor → /k-report ──────────────────────────────────────────────────────


@app_bp.route("/k-rapor")
@app_bp.route("/k-rapor/")
def k_rapor_katman_legacy_index():
    return _yonlendir()


@app_bp.route("/k-rapor/<path:subpath>")
def k_rapor_katman_legacy_path(subpath):
    return _yonlendir(subpath)


# ── /reports → /k-report ──────────────────────────────────────────────────────


@app_bp.route("/reports")
@app_bp.route("/reports/")
def reports_katman_legacy_index():
    return _yonlendir()


@app_bp.route("/reports/<path:subpath>")
def reports_katman_legacy_path(subpath):
    return _yonlendir(subpath)
