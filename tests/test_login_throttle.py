"""Login throttle / account lock testleri (Sprint 19.2)."""
import time
import pytest

from app.utils.login_throttle import (
    is_locked, record_failure, clear_failures, get_stats,
    MAX_ATTEMPTS_PER_EMAIL, LOCKOUT_DURATION_SEC,
)


@pytest.fixture(autouse=True)
def _reset_state():
    """Her test sonrası state temizliği."""
    from app.utils import login_throttle as lt
    lt._attempts_email.clear()
    lt._attempts_ip.clear()
    lt._locks.clear()
    yield
    lt._attempts_email.clear()
    lt._attempts_ip.clear()
    lt._locks.clear()


def test_no_lock_initially():
    locked, remaining = is_locked("test@example.com", "1.2.3.4")
    assert locked is False
    assert remaining is None


def test_below_threshold_no_lock():
    for _ in range(MAX_ATTEMPTS_PER_EMAIL - 1):
        record_failure("test@example.com", "1.2.3.4")
    locked, _ = is_locked("test@example.com", "1.2.3.4")
    assert locked is False


def test_lock_triggers_at_threshold():
    """N. başarısız denemede lock devreye girer."""
    locked_now = False
    for i in range(MAX_ATTEMPTS_PER_EMAIL):
        locked_now, _ = record_failure("attack@example.com", "1.2.3.4")
    assert locked_now is True

    # is_locked True dönmeli
    locked, remaining = is_locked("attack@example.com", "1.2.3.4")
    assert locked is True
    assert remaining is not None and remaining > LOCKOUT_DURATION_SEC - 5


def test_clear_failures_unlocks():
    """Başarılı login sonrası sayaç sıfırlanır."""
    for _ in range(MAX_ATTEMPTS_PER_EMAIL):
        record_failure("user@example.com", "1.2.3.4")

    locked, _ = is_locked("user@example.com", "5.5.5.5")  # farklı IP
    assert locked is True  # email locked

    clear_failures("user@example.com")
    locked, _ = is_locked("user@example.com", "5.5.5.5")
    assert locked is False


def test_ip_locked_independent_of_email():
    """IP kilidi farklı email'leri de etkiler (DOS koruma)."""
    from app.utils.login_throttle import MAX_ATTEMPTS_PER_IP
    for i in range(MAX_ATTEMPTS_PER_IP):
        record_failure(f"user{i}@example.com", "1.2.3.4")

    # Aynı IP'den yeni email denese de blok
    locked, _ = is_locked("new@example.com", "1.2.3.4")
    assert locked is True


def test_different_ip_different_email_no_lock():
    record_failure("a@example.com", "1.1.1.1")
    locked, _ = is_locked("b@example.com", "2.2.2.2")
    assert locked is False


def test_get_stats_returns_data():
    record_failure("test@example.com", "1.2.3.4")
    record_failure("test@example.com", "1.2.3.4")
    stats = get_stats("test@example.com", "1.2.3.4")
    assert stats["email_attempts"] == 2
    assert stats["ip_attempts"] == 2
