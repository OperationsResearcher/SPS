"""Admin Araçları — yalnız platform Admin'e açık, genişleyebilir araç bölümü.

İlk araç: Hata Kontrolü (uygulamanın sayfa/özelliklerini otomatik test eder).
Tasarım: docs/HATA-KONTROLU-TASARIM.md

Güvenlik:
  - Yalnız platform `Admin` rolü (tenant_admin dahil kimse giremez).
  - Ortam kilidi: yalnız Yerel (development). Test/Demo/Yayín → 403.
    (Test/Demo/Yayín ProductionConfig kullanır; v1 yalnız Yerel kararı gereği bloklanır.)
"""
from __future__ import annotations

import os

from flask import render_template, jsonify, current_app
from flask_login import login_required, current_user

from platform_core import app_bp
from app.extensions import csrf
from app.constants.roles import PLATFORM_ADMIN_ROLES


def _is_admin() -> bool:
    r = getattr(current_user, "role", None)
    return bool(r and r.name in PLATFORM_ADMIN_ROLES)


def _is_local() -> bool:
    """Yalnız Yerel (development). Test/Demo/Yayín = production → kilitli."""
    return (os.environ.get("FLASK_ENV") or "development").lower() != "production"


# ─── Admin Araçları ana sayfa ────────────────────────────────────────────────

@app_bp.route("/admin/araclar")
@login_required
def admin_tools_home():
    if not _is_admin():
        return render_template("errors/403.html"), 403
    return render_template("platform/admin/araclar.html", is_local=_is_local())


# ─── Hata Kontrolü ───────────────────────────────────────────────────────────

@app_bp.route("/admin/araclar/hata-kontrolu")
@login_required
def admin_tools_hata_kontrolu():
    if not _is_admin():
        return render_template("errors/403.html"), 403
    return render_template("platform/admin/hata_kontrolu.html", is_local=_is_local())


@app_bp.route("/admin/araclar/hata-kontrolu/tomofiltest-durum")
@login_required
def admin_tools_tomofiltest_durum():
    if not _is_admin():
        return jsonify({"error": "yetki yok"}), 403
    try:
        from app.services.tenant_clone_service import tomofiltest_status
        return jsonify({"success": True, "durum": tomofiltest_status(), "is_local": _is_local()})
    except Exception as e:
        current_app.logger.error(f"[admin_tools] tomofiltest_durum: {e}", exc_info=True)
        return jsonify({"success": False, "message": "Durum alınamadı."}), 500


@app_bp.route("/admin/araclar/hata-kontrolu/kesif")
@login_required
def admin_tools_hk_kesif():
    """Faz 2 — taranacak sayfaların keşfi (route haritası, statik)."""
    if not _is_admin():
        return jsonify({"error": "yetki yok"}), 403
    try:
        from app.services.hata_kontrol_service import discover_routes
        return jsonify({"success": True, "kesif": discover_routes()})
    except Exception as e:
        current_app.logger.error(f"[admin_tools] kesif: {e}", exc_info=True)
        return jsonify({"success": False, "message": "Keşif başarısız."}), 500


@app_bp.route("/admin/araclar/hata-kontrolu/tomofiltest-yenile", methods=["POST"])
@csrf.exempt
@login_required
def admin_tools_tomofiltest_yenile():
    """tomofiltest'i Tomofil'den (yeniden) klonlar. Yalnız Admin + Yerel."""
    if not _is_admin():
        return jsonify({"error": "yetki yok"}), 403
    if not _is_local():
        return jsonify({"success": False, "message": "Bu işlem yalnız Yerel ortamda çalışır."}), 403
    try:
        from app.services.tenant_clone_service import clone_tomofiltest
        rep = clone_tomofiltest(dry_run=False)
        if not rep.get("ok"):
            return jsonify({"success": False, "message": rep.get("error") or "Klon başarısız."}), 500
        return jsonify({
            "success": True,
            "tid": rep.get("new_tid"),
            "toplam_satir": rep.get("total_rows"),
            "tablolar": rep.get("tables", {}),
        })
    except Exception as e:
        current_app.logger.error(f"[admin_tools] tomofiltest_yenile: {e}", exc_info=True)
        return jsonify({"success": False, "message": "Klon sırasında hata."}), 500
