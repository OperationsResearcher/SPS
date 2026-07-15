# -*- coding: utf-8 -*-
"""raporlar/__init__.py haritası gerçeği yansıtıyor mu?

Modülün dosya adları kronolojik (faz0…faz5), alanına göre değil. Hangi
raporun nerede olduğu __init__.py docstring'inde yazılı. Bu tür belge
çürür — LEGACY_ROUTE_INVENTORY tam bunu yaşadı (yanlış sayılarla aylarca
durdu). Aşağıdaki testler haritayı koda bağlar.
"""
import re

import pytest

# DİKKAT: `import micro.modules.raporlar` YAPMA. Modül import edilince route'lar
# app_bp'ye kaydolur; sonra create_app aynı endpoint'i tekrar kaydetmeye çalışır
# → "View function mapping is overwriting an existing endpoint" ve TÜM paket
# çöker (216 hata). Docstring dosyadan metin olarak okunur.

# __init__.py'de ilan edilen route sayıları
ILAN_EDILEN = {
    "routes_faz0.py": 21,
    "routes_faz1.py": 28,
    "routes_faz2.py": 10,
    "routes_faz3.py": 13,
    "routes_faz4.py": 10,
    "routes_faz5.py": 11,
    "routes_esg.py": 7,
}


def _dosya_route_sayisi(dosya: str) -> int:
    with open(f"micro/modules/raporlar/{dosya}", encoding="utf-8") as f:
        return len(re.findall(r'@app_bp\.route\("', f.read()))


@pytest.mark.parametrize("dosya,beklenen", sorted(ILAN_EDILEN.items()))
def test_harita_route_sayisi_dogru(dosya, beklenen):
    """__init__.py'deki sayı gerçekle uyuşmalı — uyuşmuyorsa harita çürümüş."""
    gercek = _dosya_route_sayisi(dosya)
    assert gercek == beklenen, (
        f"{dosya}: haritada {beklenen} route yazıyor ama gerçekte {gercek}. "
        f"micro/modules/raporlar/__init__.py docstring'ini güncelle."
    )


def test_harita_tum_route_dosyalarini_kapsiyor():
    """Yeni bir routes_*.py eklenirse haritaya da girmeli."""
    import glob
    import os

    diskteki = {
        os.path.basename(p)
        for p in glob.glob("micro/modules/raporlar/routes_*.py")
    }
    eksik = diskteki - set(ILAN_EDILEN)
    assert not eksik, (
        f"Bu dosyalar haritada yok: {eksik}. __init__.py docstring'ine ekle "
        f"(ve bu testteki ILAN_EDILEN'e)."
    )


def test_init_docstring_staging_yalanini_tekrarlamiyor():
    """Eski yorum 'staging — sonradan taşınacak' diyordu; taşıma olmadı.
    Yapı kalıcı; belge bunu kabul etmeli, yoksa okuyan yanlış bekler."""
    with open("micro/modules/raporlar/__init__.py", encoding="utf-8") as f:
        ds = f.read()
    assert "KALICI" in ds, "Harita, yapının kalıcı olduğunu söylemeli"
    assert "HANGİ RAPOR NEREDE" in ds, "Yönlendirme haritası docstring'de olmalı"


def test_url_ler_faz_ismi_icermiyor():
    """URL'ler alan-bazlı olmalı — 'faz' URL'e sızarsa kullanıcı linki
    geliştirme kronolojisine bağlanır ve yeniden adlandırma imkânsızlaşır."""
    import glob

    sizinti = []
    for p in glob.glob("micro/modules/raporlar/routes_*.py"):
        with open(p, encoding="utf-8") as f:
            for url in re.findall(r'@app_bp\.route\("([^"]+)"', f.read()):
                if "faz" in url.lower():
                    sizinti.append(f"{p}: {url}")
    assert not sizinti, f"URL'de faz ismi: {sizinti}"
