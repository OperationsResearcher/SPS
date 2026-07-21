# -*- coding: utf-8 -*-
"""
Kokpitim Global Error Handlers
Kurumsal hata yakalama (Centralized Exception Handling) mekanizması.
"""
from flask_babel import gettext as _
from flask import jsonify, current_app, request, render_template
from werkzeug.exceptions import HTTPException

from app.utils.errors import (
    KokpitimError,
    AuthorizationError,
    ValidationError,
    ResourceNotFoundError,
    BusinessRuleError
)


def json_error(e, log_prefix: str = "", status: int = 500, message: str = None):
    """İstisnayı LOG'a yazar, istemciye GÜVENLİ mesaj döner.

    S6 (2026-07-21): kapsamda 112 noktada `jsonify({'message': str(e)}), 500`
    kalıbı vardı. SQLAlchemy hatalarında `str(e)` ÇALIŞAN SQL CÜMLESİNİ,
    tablo/kolon adlarını, constraint adlarını ve PARAMETRE DEĞERLERİNİ
    içerir; `pg_restore` hatalarında bağlantı dizesi/host/user taşıyabilir.

    Merkezî `handle_unhandled_exception` (aşağıda) bu işi zaten doğru
    yapıyordu — sorun yerel `except` bloklarının onu ATLAMASIYDI. Bu yardımcı
    aynı güvenliği yerel bloklara getirir.

    Kullanım:
        except Exception as e:
            return json_error(e, "[api_proje_evm]")

    Args:
        e: yakalanan istisna (yalnız log'a gider).
        log_prefix: log satırının başına eklenecek etiket.
        status: HTTP kodu (varsayılan 500).
        message: istemciye gösterilecek Türkçe mesaj; verilmezse genel metin.
    """
    import traceback
    try:
        current_app.logger.error("%s %s", log_prefix or "[hata]", e)
        current_app.logger.error(traceback.format_exc())
    except Exception:
        pass
    return jsonify({
        "success": False,
        "message": message or _("İşlem tamamlanamadı. Lütfen tekrar deneyin."),
    }), status


def register_error_handlers(app):
    """Uygulamaya merkezi hata yakalayıcıları (Interceptor) kaydeder."""

    def _wants_json_response() -> bool:
        if request.is_json:
            return True
        if request.path.startswith("/api/") or request.path.startswith("/process/api/"):
            return True
        accept = request.accept_mimetypes
        return accept.best_match(["application/json", "text/html"]) == "application/json"

    def _render_error_page(status_code: int):
        """Mevcut hata template'lerine güvenli fallback ile render eder."""
        template_map = {
            403: 'errors/403.html',
            404: 'errors/404.html',
            500: 'errors/500.html'
        }
        template_name = template_map.get(status_code, 'errors/500.html')
        return render_template(template_name), status_code
    
    @app.errorhandler(KokpitimError)
    def handle_kokpitim_error(error):
        """Kendi tanımladığımız Kokpitim hatalarını yakalar."""
        current_app.logger.warning(f"{error.__class__.__name__}: {error.message} - Path: {request.path}")
        
        # Eğer istek API/AJAX ise JSON dön, değilse HTML dön
        if _wants_json_response():
            return jsonify(error.to_dict()), error.status_code
            
        return _render_error_page(error.status_code)

    @app.errorhandler(404)
    def not_found_error(error):
        current_app.logger.info(f"404 Bulunamadı: {request.url}")
        if _wants_json_response():
            return jsonify({
                "success": False,
                "message": _("İstenen API veya kaynak bulunamadı."),
                "error_code": "NotFoundError"
            }), 404
        return _render_error_page(404)

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """Werkzeug HTTP hataları (410 Gone dahil) — genel Exception'a düşmesin."""
        code = error.code or 500
        if code >= 500:
            current_app.logger.error(f"HTTP {code}: {error.description} — {request.url}")
        else:
            current_app.logger.info(f"HTTP {code}: {error.description} — {request.url}")
        if request.is_json or request.path.startswith("/api/"):
            return jsonify({
                "success": False,
                "message": error.description or "İstek işlenemedi.",
                "error_code": error.name,
            }), code
        if code in (403, 404, 500):
            return _render_error_page(code)
        return error.description or "İstek işlenemedi.", code

    @app.errorhandler(403)
    def forbidden_error(error):
        current_app.logger.warning(f"403 Yetkisiz Erişim: {request.url}")
        if _wants_json_response():
            return jsonify({
                "success": False,
                "message": _("Bu işlem için yetkiniz yok."),
                "error_code": "ForbiddenError"
            }), 403
        return _render_error_page(403)

    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        """Yakalanmayan genel hataları (500) sessizce merkezden karşılar."""
        # Gerçek üretim ortamında hata stack trace'ini logla
        import traceback
        current_app.logger.error(f"Beklenmeyen Sistem Hatası: {e}")
        current_app.logger.error(traceback.format_exc())

        error_message = "Sistemde beklenmeyen bir hata oluştu. Lütfen sistem yöneticisi ile iletişime geçin."
        
        if _wants_json_response():
            return jsonify({
                "success": False,
                "message": error_message,
                "error_code": "InternalServerError"
            }), 500
            
        return _render_error_page(500)
