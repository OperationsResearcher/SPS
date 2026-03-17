"""
API Authentication
Sprint 13-15: API ve Entegrasyonlar
OAuth2 ve API Key authentication
"""

from functools import wraps
from flask import request, jsonify
from flask_login import current_user
import jwt
from datetime import datetime, timedelta
from app.models.core import User

# JWT Secret (production'da environment variable'dan alınmalı)
JWT_SECRET = 'your-secret-key-change-in-production'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

class APIAuth:
    """API Authentication helper"""
    
    @staticmethod
    def generate_token(user_id: int, tenant_id: int) -> str:
        """
        JWT token oluştur
        
        Args:
            user_id: Kullanıcı ID
            tenant_id: Tenant ID
        
        Returns:
            JWT token
        """
        payload = {
            'user_id': user_id,
            'tenant_id': tenant_id,
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """
        JWT token doğrula
        
        Args:
            token: JWT token
        
        Returns:
            Payload (user_id, tenant_id)
        
        Raises:
            jwt.ExpiredSignatureError: Token süresi dolmuş
            jwt.InvalidTokenError: Geçersiz token
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception('Token expired')
        except jwt.InvalidTokenError:
            raise Exception('Invalid token')
    
    @staticmethod
    def get_token_from_request() -> str:
        """Request'ten token al"""
        # Authorization header'dan
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        
        # Query parameter'dan
        token = request.args.get('token')
        if token:
            return token
        
        return None


def api_key_required(f):
    """
    API key authentication decorator
    
    Usage:
        @app.route('/api/endpoint')
        @api_key_required
        def endpoint():
            return jsonify({'data': 'protected'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # TODO: API key validation
        # user = User.query.filter_by(api_key=api_key, is_active=True).first()
        # if not user:
        #     return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def jwt_required(f):
    """
    JWT authentication decorator
    
    Usage:
        @app.route('/api/endpoint')
        @jwt_required
        def endpoint():
            return jsonify({'data': 'protected'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = APIAuth.get_token_from_request()
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        try:
            payload = APIAuth.verify_token(token)
            
            # User'ı request context'e ekle
            request.user_id = payload['user_id']
            request.tenant_id = payload['tenant_id']
            
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    
    return decorated_function


def rate_limit_by_key(limit: int = 100, per: int = 3600):
    """
    API key bazlı rate limiting
    
    Args:
        limit: İstek limiti
        per: Süre (saniye)
    
    Usage:
        @app.route('/api/endpoint')
        @rate_limit_by_key(limit=100, per=3600)
        def endpoint():
            return jsonify({'data': 'rate limited'})
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # TODO: Redis ile rate limiting
            # api_key = request.headers.get('X-API-Key')
            # key = f'rate_limit:{api_key}'
            # current = redis.get(key) or 0
            # if int(current) >= limit:
            #     return jsonify({'error': 'Rate limit exceeded'}), 429
            # redis.incr(key)
            # redis.expire(key, per)
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


# OAuth2 Token endpoint
def create_token_endpoint():
    """
    OAuth2 token endpoint
    
    POST /api/v1/oauth/token
    Body:
        {
            "grant_type": "password",
            "username": "user@example.com",
            "password": "password"
        }
    
    Response:
        {
            "access_token": "eyJ...",
            "token_type": "Bearer",
            "expires_in": 86400
        }
    """
    from flask import request, jsonify
    
    grant_type = request.json.get('grant_type')
    
    if grant_type == 'password':
        username = request.json.get('username')
        password = request.json.get('password')
        
        # User authentication
        user = User.query.filter_by(email=username, is_active=True).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate token
        token = APIAuth.generate_token(user.id, user.tenant_id)
        
        return jsonify({
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in': JWT_EXPIRATION_HOURS * 3600
        })
    
    return jsonify({'error': 'Unsupported grant type'}), 400
