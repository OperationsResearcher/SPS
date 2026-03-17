"""
Model Tests
Sprint 5-6: Güvenlik ve Stabilite
"""

import pytest
from werkzeug.security import generate_password_hash, check_password_hash

from app.models.core import User, Tenant, Role
from app.models.process import Process
from app.models.audit import AuditLog


class TestUserModel:
    """User model testleri"""

    def test_user_creation(self, db_session, test_tenant, test_role):
        """Kullanıcı oluşturma testi"""
        user = User(
            email='newuser@example.com',
            first_name='New',
            last_name='User',
            tenant_id=test_tenant.id,
            role_id=test_role.id,
            password_hash=generate_password_hash('Password123'),
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.email == 'newuser@example.com'
        assert check_password_hash(user.password_hash, 'Password123')
    
    def test_password_hashing(self, test_user):
        """Şifre hashleme testi"""
        assert test_user.password_hash is not None
        assert test_user.password_hash != 'TestPassword123'
        assert check_password_hash(test_user.password_hash, 'TestPassword123')
        assert not check_password_hash(test_user.password_hash, 'WrongPassword')
    
    def test_user_repr(self, test_user):
        """User __repr__ testi"""
        assert 'User' in repr(test_user)
        assert test_user.email == 'test@example.com'


class TestTenantModel:
    """Tenant model testleri"""
    
    def test_tenant_creation(self, db_session):
        """Tenant oluşturma testi"""
        tenant = Tenant(
            name='New Tenant',
            short_name='newtenant',
            is_active=True
        )
        db_session.add(tenant)
        db_session.commit()

        assert tenant.id is not None
        assert tenant.name == 'New Tenant'
        assert tenant.short_name == 'newtenant'


class TestAuditLogModel:
    """AuditLog model testleri"""
    
    def test_audit_log_creation(self, db_session, test_user):
        """Audit log oluşturma testi"""
        audit_log = AuditLog(
            user_id=test_user.id,
            username=test_user.email,
            tenant_id=test_user.tenant_id,
            action='CREATE',
            resource_type='Process',
            resource_id=1,
            description='Test process created',
            ip_address='127.0.0.1'
        )
        
        db_session.add(audit_log)
        db_session.commit()
        
        assert audit_log.id is not None
        assert audit_log.action == 'CREATE'
        assert audit_log.resource_type == 'Process'
