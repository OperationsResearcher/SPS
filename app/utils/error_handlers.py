# -*- coding: utf-8 -*-
"""
Kokpitim Global Error Handlers
Kurumsal hata yakalama (Centralized Exception Handling) mekanizması.
"""
from flask import jsonify, current_app, request, render_template

from app.utils.errors import (
    KokpitimError,
    AuthorizationError,
    ValidationError,
    ResourceNotFoundError,
    BusinessRuleError
)


def register_error_handlers(app):
    """Uygulamaya merkezi hata yakalayıcıları (Interceptor) kaydeder."""

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
        if request.is_json or request.path.startswith('/api/'):
            return jsonify(error.to_dict()), error.status_code
            
        return _render_error_page(error.status_code)

    @app.errorhandler(404)
    def not_found_error(error):
        current_app.logger.info(f"404 Bulunamadı: {request.url}")
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                "success": False,
                "message": "İstenen API veya kaynak bulunamadı.",
                "error_code": "NotFoundError"
            }), 404
        return _render_error_page(404)

    @app.errorhandler(403)
    def forbidden_error(error):
        current_app.logger.warning(f"403 Yetkisiz Erişim: {request.url}")
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                "success": False,
                "message": "Bu işlem için yetkiniz yok.",
                "error_code": "ForbiddenError"
            }), 403
        return _render_error_page(403)

    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        """Yakalanmayan genel hataları (500) sessizce merkezden karşılar."""
        # Gerçek üretim ortamında hata stack trace'ini logla
        import traceback
        current_app.logger.error(f"Beklenmeyen Sistem Hatası: {str(e)}")
        current_app.logger.error(traceback.format_exc())

        error_message = "Sistemde beklenmeyen bir hata oluştu. Lütfen sistem yöneticisi ile iletişime geçin."
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                "success": False,
                "message": error_message,
                "error_code": "InternalServerError"
            }), 500
            
        return _render_error_page(500)
