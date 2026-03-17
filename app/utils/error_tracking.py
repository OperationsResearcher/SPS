# -*- coding: utf-8 -*-
"""
Error tracking and logging utilities
"""
import logging
import traceback
from datetime import datetime
from flask import request, has_request_context
from functools import wraps


def setup_logging(app):
    """Setup application logging"""
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # File handler for errors
    error_handler = logging.FileHandler('error.log')
    error_handler.setLevel(logging.ERROR)
    
    # Formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    console_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)
    
    # Add handlers
    app.logger.addHandler(console_handler)
    app.logger.addHandler(error_handler)
    app.logger.setLevel(logging.INFO)
    
    return app.logger


def log_error(error, context=None):
    """
    Log error with context information
    
    Args:
        error: Exception object
        context: Additional context dict
    """
    error_info = {
        'timestamp': datetime.now().isoformat(),
        'error_type': type(error).__name__,
        'error_message': str(error),
        'traceback': traceback.format_exc(),
    }
    
    # Add request context if available
    if has_request_context():
        error_info.update({
            'url': request.url,
            'method': request.method,
            'ip': request.remote_addr,
            'user_agent': request.user_agent.string,
        })
    
    # Add custom context
    if context:
        error_info['context'] = context
    
    # Log to file
    logging.error(f"Error occurred: {error_info}")
    
    return error_info


def handle_api_error(f):
    """Decorator to handle API errors gracefully"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            log_error(e, {'function': f.__name__})
            return {'success': False, 'error': str(e)}, 400
        except PermissionError as e:
            log_error(e, {'function': f.__name__})
            return {'success': False, 'error': 'Yetkisiz işlem'}, 403
        except Exception as e:
            log_error(e, {'function': f.__name__})
            return {'success': False, 'error': 'Bir hata oluştu'}, 500
    
    return decorated_function


# Sentry integration placeholder (optional)
def init_sentry(app):
    """
    Initialize Sentry for error tracking (optional)
    
    To use: pip install sentry-sdk[flask]
    Set SENTRY_DSN in environment variables
    """
    sentry_dsn = app.config.get('SENTRY_DSN')
    
    if sentry_dsn:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            
            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[FlaskIntegration()],
                traces_sample_rate=0.1,
                environment=app.config.get('ENV', 'development')
            )
            app.logger.info("Sentry initialized successfully")
        except ImportError:
            app.logger.warning("Sentry SDK not installed. Install with: pip install sentry-sdk[flask]")
    
    return app
