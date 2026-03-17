"""
KPI Validation Schemas
Sprint 5-6: Güvenlik ve Stabilite
"""

from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime

class KpiDataSchema(Schema):
    """KPI veri girişi validation"""
    
    process_kpi_id = fields.Int(required=True, validate=validate.Range(min=1))
    data_date = fields.Date(required=True)
    actual_value = fields.Float(required=True, validate=validate.Range(min=0))
    target_value = fields.Float(required=True, validate=validate.Range(min=0))
    notes = fields.Str(validate=validate.Length(max=500), allow_none=True)
    
    @validates('data_date')
    def validate_date(self, value):
        """Gelecek tarih kontrolü"""
        if value > datetime.now().date():
            raise ValidationError('Gelecek tarih girilemez')
    
    @validates('actual_value')
    def validate_actual_value(self, value):
        """Gerçekleşen değer kontrolü"""
        if value < 0:
            raise ValidationError('Gerçekleşen değer negatif olamaz')
        if value > 1000000:
            raise ValidationError('Gerçekleşen değer çok büyük')


class ProcessKpiSchema(Schema):
    """KPI tanımlama validation"""
    
    code = fields.Str(required=True, validate=validate.Length(min=2, max=20))
    name = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    unit = fields.Str(required=True, validate=validate.Length(max=20))
    frequency = fields.Str(
        required=True,
        validate=validate.OneOf(['daily', 'weekly', 'monthly', 'quarterly', 'yearly'])
    )
    target_value = fields.Float(required=True, validate=validate.Range(min=0))
    weight = fields.Float(validate=validate.Range(min=0, max=100), allow_none=True)
    description = fields.Str(validate=validate.Length(max=1000), allow_none=True)
    
    @validates('code')
    def validate_code(self, value):
        """KPI kodu format kontrolü"""
        if not value.replace('-', '').replace('_', '').isalnum():
            raise ValidationError('KPI kodu sadece harf, rakam, tire ve alt çizgi içerebilir')
