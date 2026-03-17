"""
Service Tests
Sprint 5-6: Güvenlik ve Stabilite
"""

import pytest
from app.services.cache_service import CacheService
from app.utils.audit_logger import AuditLogger
from unittest.mock import Mock, patch

class TestCacheService:
    """Cache service testleri"""
    
    def test_cache_key_generation(self):
        """Cache key oluşturma testi"""
        key = CacheService._make_key('test', 1, 'data')
        assert key == 'test:1:data'
    
    def test_tenant_cache_key(self):
        """Tenant-specific cache key testi"""
        key = CacheService._make_tenant_key(1, 'processes')
        assert key == 'tenant:1:processes'


class TestAuditLogger:
    """Audit logger testleri"""
    
    @patch('app.utils.audit_logger.db.session')
    @patch('app.utils.audit_logger.current_user')
    @patch('app.utils.audit_logger.request')
    def test_log_create(self, mock_request, mock_user, mock_session):
        """CREATE log testi"""
        # Mock setup
        mock_user.is_authenticated = True
        mock_user.id = 1
        mock_user.email = 'test@example.com'
        mock_user.tenant_id = 1
        mock_request.remote_addr = '127.0.0.1'
        mock_request.user_agent.string = 'Test Agent'
        mock_request.method = 'POST'
        mock_request.path = '/api/test'
        
        # Test
        AuditLogger.log_create(
            resource_type='Process',
            resource_id=1,
            new_values={'name': 'Test Process'}
        )
        
        # Verify
        assert mock_session.add.called
        assert mock_session.commit.called
    
    @patch('app.utils.audit_logger.db.session')
    @patch('app.utils.audit_logger.current_user')
    @patch('app.utils.audit_logger.request')
    def test_log_update(self, mock_request, mock_user, mock_session):
        """UPDATE log testi"""
        mock_user.is_authenticated = True
        mock_user.id = 1
        mock_user.email = 'test@example.com'
        mock_user.tenant_id = 1
        mock_request.remote_addr = '127.0.0.1'
        mock_request.user_agent.string = 'Test Agent'
        mock_request.method = 'PUT'
        mock_request.path = '/api/test/1'
        
        AuditLogger.log_update(
            resource_type='Process',
            resource_id=1,
            old_values={'name': 'Old Name'},
            new_values={'name': 'New Name'}
        )
        
        assert mock_session.add.called
        assert mock_session.commit.called
