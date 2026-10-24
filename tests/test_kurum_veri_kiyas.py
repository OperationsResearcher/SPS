# -*- coding: utf-8 -*-
"""scripts/ops/kurum_veri_kiyas.py kıyas mantığı (DB'siz): kayıp / değişen / beklenen / eklenen ayrımı.

Bu araç Yayın→yerel yedek kıyasının güvencesidir; "kayıp yok" derken yanılmamalı (negatif kontrol).
"""
import sys
from pathlib import Path

import pytest

pytest.importorskip("psycopg2")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "ops"))
import kurum_veri_kiyas as k  # noqa: E402


def _s(veri, kolonlar=None, alembic="x"):
    return {"db": "t", "ad": "K", "tenant_id": 1, "kisa": "K", "alembic": [alembic], "sayilar": {t: len(v) for t, v in veri.items()},
            "kolonlar": kolonlar or {t: ["id", "ad"] for t in veri}, "pk": {t: ["id"] for t in veri}, "uyarilar": [], "veri": veri,
            "toplam_tablo": len(veri)}


def test_kayip_yakalanir_ve_cikis_kodu_icin_sayilir():
    once = _s({"process": {"1": {"id": "1", "ad": "a"}, "2": {"id": "2", "ad": "b"}}})
    sonra = _s({"process": {"1": {"id": "1", "ad": "a"}}})
    r = k.kiyasla(once, sonra)
    assert r["kayip"] == {"process": ["2"]}
    md, kayip = k.md_kiyas(once, sonra, r)
    assert kayip == 1 and "KAYIP" in md


def test_degisen_deger_yakalanir_beklenen_ayrilir():
    once = _s({"kpi_data": {"1": {"id": "1", "process_kpi_id": "5", "ad": "x"}}}, {"kpi_data": ["id", "process_kpi_id", "ad"]})
    sonra = _s({"kpi_data": {"1": {"id": "1", "process_kpi_id": "9", "ad": "y"}}}, {"kpi_data": ["id", "process_kpi_id", "ad"]})
    r = k.kiyasla(once, sonra)
    assert "ad" in r["degisen"]["kpi_data"], "beklenmeyen değişim (ad) alarm vermeli"
    assert "process_kpi_id" in r["beklenen"]["kpi_data"], "Faz 1.5 remap beklenen sayılmalı"
    assert not r["kayip"]


def test_eklenen_ve_yeni_kolon_kayip_degildir():
    once = _s({"process": {"1": {"id": "1", "ad": "a"}}})
    sonra = _s({"process": {"1": {"id": "1", "ad": "a", "yeni": "z"}, "2": {"id": "2", "ad": "b", "yeni": "z"}}},
               {"process": ["id", "ad", "yeni"]})
    r = k.kiyasla(once, sonra)
    assert r["eklenen"] == {"process": ["2"]} and r["yeni_kolon"] == {"process": ["yeni"]} and not r["kayip"] and not r["degisen"]


def test_yayin_kopya_al_ana_db_adini_reddeder():
    import subprocess
    p = subprocess.run([sys.executable, str(Path(k.__file__).parent / "yayin_kopya_al.py"), "--db", "kokpitim_db"],
                       capture_output=True, text=True)
    assert p.returncode != 0 and "kokpitim_yayin_" in (p.stdout + p.stderr)
