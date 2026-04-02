# -*- coding: utf-8 -*-
"""
Security utilities - Headers, rate limiting, validation
"""
from functools import wraps
from flask import request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import bleach

# Rate limiter instance (will be initialized in app factory)
limiter = None


def init_limiter(app):
    """Initialize rate limiter with app"""
    global limiter
    limits = app.config.get("RATELIMIT_DEFAULT", "50000 per hour; 1000000 per day")
    limit_list = [s.strip() for s in str(limits).split(";") if s.strip()]
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=limit_list if limit_list else ["50000 per hour", "1000000 per day"],
        storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://'),
        strategy="fixed-window"
    )
    return limiter


def set_security_headers(response):
    """Add security headers to response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    # HSTS yalnızca gerçek HTTPS isteklerde. request.url kullanılmaz: Werkzeug boş/şüpheli
    # Host başlığında SecurityError üretebilir; after_request içinde bu yanıtı keser (CF 524).
    forwarded = (request.environ.get("HTTP_X_FORWARDED_PROTO") or "").split(",")[0].strip().lower()
    if forwarded == "https" or request.is_secure:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    return response


def sanitize_html(html_content):
    """Sanitize HTML content to prevent XSS"""
    if not html_content:
        return html_content
    
    ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'span', 'div']
    ALLOWED_ATTRS = {
        'a': ['href', 'title', 'target'],
        'span': ['class'],
        'div': ['class']
    }
    
    return bleach.clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        strip=True
    )


def validate_file_upload(file, allowed_extensions=None, max_size_mb=5):
    """
    Validate uploaded file
    
    Args:
        file: FileStorage object
        allowed_extensions: Set of allowed extensions (default: images)
        max_size_mb: Maximum file size in MB
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    if not file or file.filename == '':
        return False, "Dosya seçilmedi"
    
    # Check extension
    if '.' not in file.filename:
        return False, "Geçersiz dosya adı"
    
    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in allowed_extensions:
        return False, f"Geçersiz dosya tipi. İzin verilenler: {', '.join(allowed_extensions)}"
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset to beginning
    
    max_size_bytes = max_size_mb * 1024 * 1024
    if size > max_size_bytes:
        return False, f"Dosya çok büyük (maksimum {max_size_mb}MB)"
    
    return True, None
