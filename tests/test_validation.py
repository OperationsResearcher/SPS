"""
Validation Tests
Sprint 5-6: Güvenlik ve Stabilite
"""

import pytest
from marshmallow import ValidationError
from app.schemas.kpi_schemas import KpiDataSchema, ProcessKpiSchema
from app.schemas.user_schemas import UserSchema, PasswordChangeSchema
from datetime import datetime, timedelta

class TestKpiDataSchema:
    """KPI data validation testleri"""
    
    def test_valid_kpi_data(self):
        """Geçerli KPI data testi"""
        schema = KpiDataSchema()
        data = {
            'process_kpi_id': 1,
            'data_date': datetime.now().date().isoformat(),
            'actual_value': 85.5,
            'target_value': 90.0,
            'notes': 'Test note'
        }
        
        result = schema.load(data)
        assert result['actual_value'] == 85.5
        assert result['target_value'] == 90.0
    
    def test_negative_value(self):
        """Negatif değer testi"""
        schema = KpiDataSchema()
        data = {
            'process_kpi_id': 1,
            'data_date': datetime.now().date().isoformat(),
            'actual_value': -10,
            'target_value': 90.0
        }
        
        with pytest.raises(ValidationError) as exc:
            schema.load(data)
        assert 'actual_value' in exc.value.messages
    
    def test_future_date(self):
        """Gelecek tarih testi"""
        schema = KpiDataSchema()
        future_date = (datetime.now() + timedelta(days=1)).date()
        data = {
            'process_kpi_id': 1,
            'data_date': future_date.isoformat(),
            'actual_value': 85.5,
            'target_value': 90.0
        }
        
        with pytest.raises(ValidationError) as exc:
            schema.load(data)
        assert 'data_date' in exc.value.messages
    
    def test_missing_required_field(self):
        """Eksik zorunlu alan testi"""
        schema = KpiDataSchema()
        data = {
            'process_kpi_id': 1,
            'actual_value': 85.5
            # data_date ve target_value eksik
        }
        
        with pytest.raises(ValidationError) as exc:
            schema.load(data)
        assert 'data_date' in exc.value.messages
        assert 'target_value' in exc.value.messages


class TestPasswordChangeSchema:
    """Şifre değiştirme validation testleri"""
    
    def test_valid_password(self):
        """Geçerli şifre testi"""
        schema = PasswordChangeSchema()
        data = {
            'old_password': 'OldPass123',
            'new_password': 'NewPass123',
            'confirm_password': 'NewPass123'
        }
        
        result = schema.load(data)
        assert result['new_password'] == 'NewPass123'
    
    def test_weak_password(self):
        """Zayıf şifre testi"""
        schema = PasswordChangeSchema()
        data = {
            'old_password': 'OldPass123',
            'new_password': 'weak',  # Çok kısa, büyük harf yok, rakam yok
            'confirm_password': 'weak'
        }
        
        with pytest.raises(ValidationError) as exc:
            schema.load(data)
        assert 'new_password' in exc.value.messages
    
    def test_no_uppercase(self):
        """Büyük harf olmayan şifre testi"""
        schema = PasswordChangeSchema()
        data = {
            'old_password': 'OldPass123',
            'new_password': 'newpass123',  # Büyük harf yok
            'confirm_password': 'newpass123'
        }
        
        with pytest.raises(ValidationError) as exc:
            schema.load(data)
        assert 'büyük harf' in str(exc.value.messages['new_password'][0]).lower()


class TestUserSchema:
    """User validation testleri"""
    
    def test_valid_user(self):
        """Geçerli kullanıcı testi"""
        schema = UserSchema()
        data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'role_id': 1
        }
        
        result = schema.load(data)
        assert result['email'] == 'test@example.com'
    
    def test_invalid_email(self):
        """Geçersiz email testi"""
        schema = UserSchema()
        data = {
            'email': 'invalid-email',
            'first_name': 'Test',
            'last_name': 'User',
            'role_id': 1
        }
        
        with pytest.raises(ValidationError) as exc:
            schema.load(data)
        assert 'email' in exc.value.messages
