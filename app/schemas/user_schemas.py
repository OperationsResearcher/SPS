"""
User Validation Schemas
Sprint 5-6: Güvenlik ve Stabilite
"""

from marshmallow import Schema, fields, validate, validates, ValidationError
import re

class UserSchema(Schema):
    """Kullanıcı validation"""
    
    email = fields.Email(required=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    phone = fields.Str(validate=validate.Length(max=20), allow_none=True)
    role_id = fields.Int(required=True, validate=validate.Range(min=1))
    
    @validates('phone')
    def validate_phone(self, value):
        """Telefon numarası format kontrolü"""
        if value and not re.match(r'^\+?[\d\s\-\(\)]+$', value):
            raise ValidationError('Geçersiz telefon numarası formatı')


class UserUpdateSchema(Schema):
    """Kullanıcı güncelleme validation"""
    
    first_name = fields.Str(validate=validate.Length(min=2, max=50), allow_none=True)
    last_name = fields.Str(validate=validate.Length(min=2, max=50), allow_none=True)
    phone = fields.Str(validate=validate.Length(max=20), allow_none=True)
    
    @validates('phone')
    def validate_phone(self, value):
        if value and not re.match(r'^\+?[\d\s\-\(\)]+$', value):
            raise ValidationError('Geçersiz telefon numarası formatı')


class PasswordChangeSchema(Schema):
    """Şifre değiştirme validation"""
    
    old_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8, max=128))
    confirm_password = fields.Str(required=True)
    
    @validates('new_password')
    def validate_password(self, value):
        """Şifre güvenlik kontrolü"""
        if len(value) < 8:
            raise ValidationError('Şifre en az 8 karakter olmalıdır')
        if not re.search(r'[A-Z]', value):
            raise ValidationError('Şifre en az bir büyük harf içermelidir')
        if not re.search(r'[a-z]', value):
            raise ValidationError('Şifre en az bir küçük harf içermelidir')
        if not re.search(r'\d', value):
            raise ValidationError('Şifre en az bir rakam içermelidir')
