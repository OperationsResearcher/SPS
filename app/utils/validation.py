"""
Validation Utilities
Sprint 5-6: Güvenlik ve Stabilite
Marshmallow validation helper'ları
"""

from functools import wraps
from flask import request, jsonify
from marshmallow import ValidationError

def validate_request(schema_class):
    """
    Request validation decorator
    
    Usage:
        @app.route('/api/kpi-data', methods=['POST'])
        @validate_request(KpiDataSchema)
        def create_kpi_data(validated_data):
            # validated_data kullanıma hazır
            return jsonify({'success': True})
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            schema = schema_class()
            
            try:
                # JSON data validation
                if request.is_json:
                    validated_data = schema.load(request.json)
                # Form data validation
                else:
                    validated_data = schema.load(request.form.to_dict())
                
                # Validated data'yı function'a geç
                return f(validated_data, *args, **kwargs)
                
            except ValidationError as err:
                return jsonify({
                    'error': 'Validation failed',
                    'messages': err.messages
                }), 400
        
        return wrapper
    return decorator


def validate_data(schema_class, data):
    """
    Manuel data validation
    
    Usage:
        from app.utils.validation import validate_data
        from app.schemas.kpi_schemas import KpiDataSchema
        
        validated = validate_data(KpiDataSchema, request.json)
        if 'error' in validated:
            return jsonify(validated), 400
    """
    schema = schema_class()
    
    try:
        validated_data = schema.load(data)
        return validated_data
    except ValidationError as err:
        return {
            'error': 'Validation failed',
            'messages': err.messages
        }
