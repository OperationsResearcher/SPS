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


# ── Redis yolu (GUV-12) ──────────────────────────────────────────────────────
class _FakeRedis:
    """Yalnız throttle'ın kullandığı komutlar; TTL saati elle ilerletilir."""

    def __init__(self):
        self.now = 1000.0
        self.data, self.exp = {}, {}

    def _alive(self, k):
        if k in self.exp and self.exp[k] <= self.now:
            self.data.pop(k, None)
            self.exp.pop(k, None)
        return k in self.data

    def incr(self, k):
        self._alive(k)
        self.data[k] = int(self.data.get(k, 0)) + 1
        return self.data[k]

    def expire(self, k, sec):
        self.exp[k] = self.now + sec

    def set(self, k, v, ex=None):
        self.data[k] = v
        if ex:
            self.exp[k] = self.now + ex

    def exists(self, k):
        return 1 if self._alive(k) else 0

    def ttl(self, k):
        return int(self.exp[k] - self.now) if self._alive(k) and k in self.exp else -2

    def delete(self, *keys):
        for k in keys:
            self.data.pop(k, None)
            self.exp.pop(k, None)


@pytest.fixture
def redis_backend(monkeypatch):
    from app.utils import login_throttle as lt
    fake = _FakeRedis()
    monkeypatch.setattr(lt, "_redis", fake)
    return fake


def test_redis_lock_ve_sifirlama(redis_backend):
    for _ in range(MAX_ATTEMPTS_PER_EMAIL):
        locked_now, _n = record_failure("r@example.com", "9.9.9.9")
    assert locked_now is True
    locked, remaining = is_locked("r@example.com", "8.8.8.8")  # farklı IP, e-posta kilidi
    assert locked is True and remaining > LOCKOUT_DURATION_SEC - 5
    clear_failures("r@example.com")
    assert is_locked("r@example.com", "8.8.8.8")[0] is False


def test_redis_kilit_suresi_dolunca_acilir(redis_backend):
    for _ in range(MAX_ATTEMPTS_PER_EMAIL):
        record_failure("t@example.com", "7.7.7.7")
    redis_backend.now += LOCKOUT_DURATION_SEC + 1
    assert is_locked("t@example.com", "6.6.6.6")[0] is False


def test_redis_ip_kilidi(redis_backend):
    from app.utils.login_throttle import MAX_ATTEMPTS_PER_IP
    for i in range(MAX_ATTEMPTS_PER_IP):
        record_failure(f"x{i}@example.com", "5.4.3.2")
    assert is_locked("yeni@example.com", "5.4.3.2")[0] is True


def test_redis_dusunce_bellek_yoluna_duser(monkeypatch):
    from app.utils import login_throttle as lt

    class _Dead:
        def __getattr__(self, name):
            def boom(*a, **k):
                raise ConnectionError("redis yok")
            return boom
    monkeypatch.setattr(lt, "_redis", _Dead())
    assert record_failure("d@example.com", "1.1.1.1")[1] == 1  # bellek yolu çalışır
    assert is_locked("d@example.com", "1.1.1.1")[0] is False


def test_bellek_yolu_sinirsiz_buyumez(monkeypatch):
    from app.utils import login_throttle as lt
    monkeypatch.setattr(lt, "_MEM_MAX_KEYS", 50)
    monkeypatch.setattr(lt, "WINDOW_SEC", -1)  # tüm kayıtlar "eski" sayılır
    for i in range(200):
        record_failure(f"bot{i}@example.com", f"10.0.{i // 250}.{i % 250}")
    assert len(lt._attempts_email) <= 60
