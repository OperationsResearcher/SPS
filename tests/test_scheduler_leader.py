"""KOD-02 / PERF-01 — zamanlayıcılar yalnız tek (lider) süreçte başlar."""
from types import SimpleNamespace

import pytest

from app.utils import scheduler_leader as sl


@pytest.fixture(autouse=True)
def _reset(monkeypatch):
    monkeypatch.setattr(sl, "_leader_conn", None)
    monkeypatch.delenv("SCHEDULER_ENABLED", raising=False)
    # Arka plan yeniden deneme thread'i testte başlamasın
    monkeypatch.setattr(sl.threading, "Thread",
                        lambda *a, **k: SimpleNamespace(start=lambda: None))


def test_env_false_baslatmaz(app, monkeypatch):
    monkeypatch.setenv("SCHEDULER_ENABLED", "false")
    called = []
    assert sl.run_as_leader(app, lambda: called.append(1)) is False
    assert called == []


def test_pg_disi_veritabaninda_tek_surec_varsayilir(app):
    called = []
    assert sl.run_as_leader(app, lambda: called.append(1)) is True  # test DB = SQLite
    assert called == [1]


class _FakeConn:
    def __init__(self, got):
        self.got, self.closed = got, False

    def execution_options(self, **_):
        return self

    def exec_driver_sql(self, sql):
        assert "pg_try_advisory_lock" in sql
        return SimpleNamespace(scalar=lambda: self.got)

    def close(self):
        self.closed = True


def _fake_pg(monkeypatch, app, got):
    conn = _FakeConn(got)
    from app.models import db
    fake_engine = SimpleNamespace(dialect=SimpleNamespace(name="postgresql"),
                                  connect=lambda: conn)
    monkeypatch.setattr(type(db), "engine", property(lambda self: fake_engine), raising=False)
    return conn


def test_kilit_alinirsa_lider(app, monkeypatch):
    conn = _fake_pg(monkeypatch, app, True)
    called = []
    assert sl.run_as_leader(app, lambda: called.append(1)) is True
    assert called == [1] and conn.closed is False and sl._leader_conn is conn


def test_kilit_alinamazsa_lider_degil_ve_baglanti_kapanir(app, monkeypatch):
    conn = _fake_pg(monkeypatch, app, False)
    called = []
    assert sl.run_as_leader(app, lambda: called.append(1)) is False
    assert called == [] and conn.closed is True and sl._leader_conn is None
