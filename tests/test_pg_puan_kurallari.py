"""Faz 1B / Karar 4-6 — tek PG puan kuralları (motor, k_rapor, sağlık, dönem raporu ortak)."""
import pytest

from app.services.score_engine_service import aggregate_actuals, compute_pg_score


# ── Karar 4: hedef 0 ─────────────────────────────────────────────────────────
@pytest.mark.parametrize("gercek,beklenen", [(0, 100.0), (1, 0.0), (498, 0.0)])
def test_azalan_hedef_sifir(gercek, beklenen):
    """İş Kazası Sayısı gibi: hedef 0, azalması iyi."""
    assert compute_pg_score(0, gercek, "Decreasing") == beklenen


def test_artan_hedef_sifir_puanlanmaz():
    assert compute_pg_score(0, 5, "Increasing") is None
    assert compute_pg_score(0, 0, "Increasing") is None


# ── Karar 5: azalması iyi + gerçekleşen 0 ────────────────────────────────────
@pytest.mark.parametrize("hedef", [12, 1, 0.5])
def test_azalan_gerceklesen_sifir_tam_puan(hedef):
    """KMF PG 386: k_rapor %0, motor 100 gösteriyordu."""
    assert compute_pg_score(hedef, 0, "Decreasing") == 100.0


def test_azalan_normal_oran_degismedi():
    assert compute_pg_score(100, 200, "Decreasing") == 50.0
    assert compute_pg_score(100, 50, "Decreasing") == 100.0


# ── Karar 6: tek toplulaştırma, 100 kayıt sınırı yok ─────────────────────────
def test_aggregate_toplama_ortalama_son():
    v = [5.0, 3.0, 4.0]                      # en yeni → en eski
    assert aggregate_actuals(v, "Toplama") == 12.0
    assert aggregate_actuals(v, "SUM") == 12.0
    assert aggregate_actuals(v, "Ortalama") == 4.0
    assert aggregate_actuals(v, "Son Değer") == 5.0
    assert aggregate_actuals([], "Toplama") is None


def test_aggregate_100den_fazla_kayit_kesilmez():
    v = [1.0] * 365
    assert aggregate_actuals(v, "Toplama") == 365.0   # eskiden en fazla 100
