"""
Process Validation Schemas
Sprint 5-6: Güvenlik ve Stabilite
"""

from marshmallow import Schema, fields, validate, validates, ValidationError

class ProcessSchema(Schema):
    """Süreç validation"""
    
    code = fields.Str(required=True, validate=validate.Length(min=2, max=20))
    name = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    description = fields.Str(validate=validate.Length(max=1000), allow_none=True)
    parent_id = fields.Int(validate=validate.Range(min=1), allow_none=True)
    owner_id = fields.Int(validate=validate.Range(min=1), allow_none=True)
    
    @validates('code')
    def validate_code(self, value):
        """Süreç kodu format kontrolü"""
        if not value.replace('-', '').replace('_', '').isalnum():
            raise ValidationError('Süreç kodu sadece harf, rakam, tire ve alt çizgi içerebilir')


class ActivitySchema(Schema):
    """Faaliyet validation"""
    
    code = fields.Str(required=True, validate=validate.Length(min=2, max=20))
    name = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    description = fields.Str(validate=validate.Length(max=1000), allow_none=True)
    process_id = fields.Int(required=True, validate=validate.Range(min=1))
    responsible_id = fields.Int(validate=validate.Range(min=1), allow_none=True)
