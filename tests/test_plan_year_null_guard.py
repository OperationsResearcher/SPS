"""HATA-10 — rapor uçlarında plan_year_id NULL (legacy) kayıtlar dışarıda kalmamalı."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOSYALAR = [
    "micro/modules/raporlar/routes_faz0.py",
    "micro/modules/raporlar/routes_faz1.py",
    "micro/modules/raporlar/routes_faz3.py",
    "micro/modules/raporlar/routes_faz5.py",
    "micro/modules/k_rapor/routes.py",
]
# Sıkı eşitlik kalıpları: NULL'u dışarıda bırakır.
YASAK = [
    re.compile(r"filter_by\([^)]*plan_year_id\s*=\s*(?:py|active_py|py_id)"),
    re.compile(r"(?<![\w\[(])(?:Process|IPI|IndividualPerformanceIndicator)\.plan_year_id\s*==\s*(?:py|active_py|py_id)"),
    re.compile(r"\.filter_by\(plan_year_id=py_id\)"),
]


def test_rapor_uclarinda_siki_plan_yili_filtresi_yok():
    ihlal = []
    for d in DOSYALAR:
        for no, satir in enumerate((ROOT / d).read_text(encoding="utf-8").splitlines(), 1):
            if "or_(" in satir or "HATA-10" in satir:
                continue
            if any(p.search(satir) for p in YASAK):
                ihlal.append(f"{d}:{no}: {satir.strip()}")
    assert not ihlal, "NULL plan_year_id dışarıda kalır:\n" + "\n".join(ihlal)
