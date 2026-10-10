"""Faz 1B / Karar 1 — açık uçlu bantlar bandın KONUMUNA göre çözülür.

Kaynak: docs/ekim2026/FAZ1A-ONAY-TABLOSU.md (KMF canlı: 47 PG×yıl karne puanı yanlıştı).
Örnekler KMF'nin gerçek tanımlarından alınmıştır.
"""
import pytest

from app.utils.karne_hesaplamalar import (
    hesapla_basari_puani,
    hesapla_basari_puani_ham,
    parse_aralik_degeri,
)

# PG 330 — "-4" = 4 ve altı (en kötü bant), "20-" = 20 ve üstü (en iyi bant)
PG330 = {1: "-4", 2: "5-9", 3: "10-14", 4: "15-19", 5: "20-"}
# PG 551 — "79-" en kötü bantta = 79 ve altı
PG551 = {1: "79-", 2: "80-89", 3: "90-100"}
# PG 532 — azalan yön: "30-" = 30 ve üstü (en kötü), "20-" = 20 ve altı (en iyi)
PG532 = {1: "30-", 2: "27-29", 3: "24-26", 4: "21-23", 5: "20-"}
# PG 386 — "20+" = 20 ve üstü
PG386 = {1: "20+", 2: "15-19", 3: "10-14", 4: {"aralik": "5-9", "aciklama": "-"}, 5: {"aralik": "4-", "aciklama": "-"}}


@pytest.mark.parametrize("deger,beklenen", [
    (2, 1), (4, 1), (5, 2), (12, 3), (17, 4), (20, 5), (25, 5),
])
def test_artan_eksi_n_en_kotu_bant(deger, beklenen):
    assert hesapla_basari_puani(deger, PG330, "Increasing") == beklenen


@pytest.mark.parametrize("deger,beklenen", [
    (50, 1), (79, 1), (85, 2), (96, 3), (100, 3),
])
def test_artan_n_tire_en_kotu_bant(deger, beklenen):
    assert hesapla_basari_puani(deger, PG551, "Increasing") == beklenen


@pytest.mark.parametrize("deger,beklenen", [
    (35, 1), (30, 1), (29, 2), (24, 3), (23, 4), (21, 4), (20, 5), (10, 5),
])
def test_azalan_yonde_konum_tersine_cozulur(deger, beklenen):
    """Bugünkü hata: 24 için 5 dönüyordu; doğrusu 3."""
    assert hesapla_basari_puani(deger, PG532, "Decreasing") == beklenen


@pytest.mark.parametrize("deger,beklenen", [
    (25, 1), (20, 1), (17, 2), (12, 3), (7, 4), (3, 5),
])
def test_arti_biçimi_n_ve_ustu(deger, beklenen):
    """'20+' bugün hiç parse edilemiyordu (None)."""
    assert hesapla_basari_puani(deger, PG386, "Decreasing") == beklenen


def test_ham_fonksiyon_eski_formatta_ayni_sonucu_verir():
    puan, olcek = hesapla_basari_puani_ham(12, '{"1":"-4","2":"5-9","3":"10-14","4":"15-19","5":"20-"}', "Increasing")
    assert (puan, olcek) == (3.0, "1-5")


def test_yuzde_isareti_korunur():
    assert hesapla_basari_puani(100, {1: "%71-80", 2: "%81-89", 3: "%90-100"}, "Increasing") == 3


def test_hicbir_banda_dusmezse_alt_banda_duser():
    araliklar = {1: "0-40", 5: "91-100"}
    assert hesapla_basari_puani(120, araliklar, "Increasing") == 5
    assert hesapla_basari_puani(-5, araliklar, "Increasing") == 1
    assert hesapla_basari_puani(60, araliklar, "Increasing") == 1   # A-004: bosluk -> alttaki en yakin bant (uydurma 3 kaldirildi)


# ── HATA-07: ondalık nokta ────────────────────────────────────────────────────
@pytest.mark.parametrize("metin,beklenen", [
    ("4.5-9.5", (4.5, 9.5)),
    ("0.95-1", (0.95, 1.0)),
    ("400.000-449.000", (400000.0, 449000.0)),       # binlik ayraç korunur
    ("1.234,56-2.000,00", (1234.56, 2000.0)),
    ("4,5-9,5", (4.5, 9.5)),
])
def test_ondalik_nokta_binlikten_ayrilir(metin, beklenen):
    assert parse_aralik_degeri(metin) == beklenen


def test_ham_parse_geriye_uyumlu():
    assert parse_aralik_degeri("-5") == (-5.0, None)
    assert parse_aralik_degeri("90-") == (90.0, None)
    assert parse_aralik_degeri("20+") == (20.0, None)
    assert parse_aralik_degeri("-50--10") == (-50.0, -10.0)
