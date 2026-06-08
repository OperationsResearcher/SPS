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

from flask import render_template, jsonify, current_app, request
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


# ─── İstatistikler ───────────────────────────────────────────────────────────

@app_bp.route("/admin/araclar/istatistikler")
@login_required
def admin_tools_istatistikler():
    """Sistemdeki kurum bazında kullanıcı/strateji/süreç/PG/proje sayıları (salt-okuma)."""
    if not _is_admin():
        return render_template("errors/403.html"), 403
    try:
        from app.services.admin_stats_service import collect_statistics
        stats = collect_statistics()
    except Exception as e:
        current_app.logger.error(f"[admin_tools] istatistikler: {e}", exc_info=True)
        stats = None
    return render_template("platform/admin/istatistikler.html", stats=stats)


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


@app_bp.route("/admin/araclar/hata-kontrolu/gecmis")
@login_required
def admin_tools_hk_gecmis():
    """Kaydedilmiş koşuların özet listesi."""
    if not _is_admin():
        return jsonify({"error": "yetki yok"}), 403
    from app.services.hata_kontrol_executor import list_saved_runs
    return jsonify({"success": True, "kosular": list_saved_runs(current_app._get_current_object())})


@app_bp.route("/admin/araclar/hata-kontrolu/gecmis-yukle")
@login_required
def admin_tools_hk_gecmis_yukle():
    """Tek bir kaydedilmiş koşunun tam içeriği."""
    if not _is_admin():
        return jsonify({"error": "yetki yok"}), 403
    from app.services.hata_kontrol_executor import load_saved_run
    rec = load_saved_run(current_app._get_current_object(), request.args.get("file", ""))
    if not rec:
        return jsonify({"success": False, "message": "Kayıt bulunamadı."}), 404
    return jsonify({"success": True, "kosu": rec})


@app_bp.route("/admin/araclar/hata-kontrolu/tarama-baslat", methods=["POST"])
@csrf.exempt
@login_required
def admin_tools_hk_tarama_baslat():
    """Faz 3b — Playwright tarayıcı taramasını arka planda başlatır. Yalnız Admin + Yerel."""
    if not _is_admin():
        return jsonify({"error": "yetki yok"}), 403
    if not _is_local():
        return jsonify({"success": False, "message": "Tarama yalnız Yerel ortamda çalışır."}), 403
    try:
        from app.services.hata_kontrol_executor import start_run, busy_label
        limit = request.args.get("limit", type=int)
        base_url = request.host_url.rstrip("/")
        run_id = start_run(current_app._get_current_object(), base_url=base_url, limit=limit)
        if run_id is None:
            return jsonify({"success": False, "busy": busy_label(),
                            "message": f"Başka bir Hata Kontrolü işlemi çalışıyor ({busy_label()}). Bitmesini bekleyin."}), 409
        return jsonify({"success": True, "run_id": run_id})
    except Exception as e:
        current_app.logger.error(f"[admin_tools] tarama_baslat: {e}", exc_info=True)
        return jsonify({"success": False, "message": "Tarama başlatılamadı."}), 500


@app_bp.route("/admin/araclar/hata-kontrolu/tarama-durum")
@login_required
def admin_tools_hk_tarama_durum():
    if not _is_admin():
        return jsonify({"error": "yetki yok"}), 403
    from app.services.hata_kontrol_executor import get_progress
    run_id = request.args.get("run", "")
    prog = get_progress(run_id)
    if not prog:
        return jsonify({"success": False, "message": "Koşu bulunamadı."}), 404
    # Sonuç listesi büyük olabilir — özet + son sonuçlar
    return jsonify({"success": True, "durum": {
        "id": prog["id"], "status": prog["status"], "total": prog["total"],
        "done": prog["done"], "current": prog["current"], "counts": prog["counts"],
        "error": prog["error"],
        "results": prog["results"],  # tümü (tek tenant, ~321 satır — yönetilebilir)
        "links": prog.get("links", {}),
    }})


@app_bp.route("/admin/araclar/hata-kontrolu/senaryo-baslat", methods=["POST"])
@csrf.exempt
@login_required
def admin_tools_hk_senaryo_baslat():
    """Faz 3d — aktif CRUD senaryolarını arka planda başlatır. Yalnız Admin + Yerel."""
    if not _is_admin():
        return jsonify({"error": "yetki yok"}), 403
    if not _is_local():
        return jsonify({"success": False, "message": "Senaryolar yalnız Yerel ortamda çalışır."}), 403
    try:
        from app.services.hata_kontrol_executor import start_scenarios, busy_label
        run_id = start_scenarios(current_app._get_current_object(), base_url=request.host_url.rstrip("/"))
        if run_id is None:
            return jsonify({"success": False, "busy": busy_label(),
                            "message": f"Başka bir Hata Kontrolü işlemi çalışıyor ({busy_label()}). Bitmesini bekleyin."}), 409
        return jsonify({"success": True, "run_id": run_id})
    except Exception as e:
        current_app.logger.error(f"[admin_tools] senaryo_baslat: {e}", exc_info=True)
        return jsonify({"success": False, "message": "Senaryolar başlatılamadı."}), 500


@app_bp.route("/admin/araclar/hata-kontrolu/senaryo-durum")
@login_required
def admin_tools_hk_senaryo_durum():
    if not _is_admin():
        return jsonify({"error": "yetki yok"}), 403
    from app.services.hata_kontrol_executor import get_progress
    prog = get_progress(request.args.get("run", ""))
    if not prog:
        return jsonify({"success": False, "message": "Koşu bulunamadı."}), 404
    return jsonify({"success": True, "durum": {
        "id": prog["id"], "status": prog["status"], "total": prog["total"],
        "done": prog["done"], "current": prog["current"],
        "passed": prog.get("passed", 0), "failed": prog.get("failed", 0),
        "scenarios": prog.get("scenarios", []), "reset": prog.get("reset", False),
        "error": prog["error"],
    }})


@app_bp.route("/admin/araclar/hata-kontrolu/tomofiltest-yenile", methods=["POST"])
@csrf.exempt
@login_required
def admin_tools_tomofiltest_yenile():
    """tomofiltest'i Tomofil'den (yeniden) klonlar. Yalnız Admin + Yerel."""
    if not _is_admin():
        return jsonify({"error": "yetki yok"}), 403
    if not _is_local():
        return jsonify({"success": False, "message": "Bu işlem yalnız Yerel ortamda çalışır."}), 403
    # Yenile = tomofiltest'i sıfırlar → çalışan tarama/senaryonun oturumunu öldürür.
    # Bu yüzden o işlem bitmeden yenilemeye izin verme (eşzamanlılık koruması).
    from app.services.hata_kontrol_executor import try_acquire, release, busy_label
    if not try_acquire("yenile"):
        return jsonify({"success": False, "busy": busy_label(),
                        "message": f"Başka bir Hata Kontrolü işlemi çalışıyor ({busy_label()}). Bitmesini bekleyin."}), 409
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
    finally:
        release()
