"""
Service Tests
Sprint 5-6: Güvenlik ve Stabilite
"""

import pytest
from unittest.mock import MagicMock, patch

from app.utils.audit_logger import AuditLogger
from app.utils.cache_utils import CACHE_KEYS


class TestCacheKeys:
    """cache_utils CACHE_KEYS fabrikaları"""

    def test_process_list_key(self):
        assert CACHE_KEYS["process_list"](7) == "process_list_7"

    def test_vision_score_key(self):
        assert CACHE_KEYS["vision_score"](3, 2025) == "vision_score_3_2025"


class TestAuditLogger:
    """Audit logger testleri"""

    def test_log_create(self, app, test_user):
        with app.test_request_context("/api/test", method="POST"):
            with patch("app.utils.audit_logger.db.session") as mock_session:
                AuditLogger.log_create(
                    resource_type="Process",
                    resource_id=1,
                    new_values={"name": "Test Process"},
                )
                assert mock_session.add.called
                assert mock_session.commit.called

    def test_log_update(self, app, test_user):
        with app.test_request_context("/api/test/1", method="PUT"):
            with patch("app.utils.audit_logger.db.session") as mock_session:
                AuditLogger.log_update(
                    resource_type="Process",
                    resource_id=1,
                    old_values={"name": "Old Name"},
                    new_values={"name": "New Name"},
                )
                assert mock_session.add.called
                assert mock_session.commit.called
