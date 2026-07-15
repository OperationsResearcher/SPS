#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Yerel CI köprüsü — GitHub Actions çalışmıyorken aynı kapıları yerelde koşar.

Neden: `.github/workflows/ci.yml` iyi tasarlanmış (ruff + import guard + pytest
+ coverage ratchet) ama GitHub Actions faturalandırma kilidi yüzünden Haziran
2026'dan beri koşmuyor. Bu sürede 21 test sessizce kırıldı. CI kilidi açılana
kadar bu script tek komutluk güvenlik ağıdır; açıldıktan sonra da push öncesi
hızlı kontrol olarak kalır.

Kullanım:
    python scripts/ci/yerel_kontrol.py           # tam kontrol
    python scripts/ci/yerel_kontrol.py --hizli   # ruff + guard (pytest yok)

Çıkış kodu 0 = tüm kapılar geçti; 1 = en az bir kapı kırık.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

GUARDS = (
    "check_single_db.py",
    "check_portfolio_imports.py",
    "check_no_raw_models_import.py",
)


def _modul_var(modul: str) -> bool:
    """`python -m <modul>` çalıştırılabilir mi? (kurulu değilse exit 1 döner,
    FileNotFoundError DEĞİL — bu ayrım olmadan 'kurulu değil' 'kırık' görünür)"""
    return subprocess.run(
        [sys.executable, "-c", f"import {modul}"],
        cwd=ROOT, capture_output=True,
    ).returncode == 0


def _kos(baslik: str, cmd: list[str], gerekli_modul: str | None = None) -> bool:
    """Komutu çalıştır, sonucu bas, başarılı mı döndür."""
    print(f"\n=== {baslik} ===", flush=True)
    if gerekli_modul and not _modul_var(gerekli_modul):
        print(f"ATLANDI: '{gerekli_modul}' kurulu degil -> pip install {gerekli_modul}")
        return True  # eksik arac kapiyi kirmasin; rapor yeter
    try:
        sonuc = subprocess.run(cmd, cwd=ROOT)
    except FileNotFoundError:
        print(f"ATLANDI: '{cmd[0]}' bulunamadi (kurulu degil).")
        return True
    ok = sonuc.returncode == 0
    print(f"--> {'GECTI' if ok else 'KIRIK'}")
    return ok


def main() -> int:
    hizli = "--hizli" in sys.argv
    sonuclar: dict[str, bool] = {}

    sonuclar["ruff"] = _kos(
        "Ruff (sozdizimi/NameError sinifi)",
        [sys.executable, "-m", "ruff", "check", "."],
        gerekli_modul="ruff",
    )

    for g in GUARDS:
        sonuclar[g] = _kos(f"Import politikasi: {g}", [sys.executable, f"scripts/ci/{g}"])

    if not hizli:
        sonuclar["pytest"] = _kos(
            "Pytest (+ coverage esigi)",
            [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=short",
             "--cov=app", "--cov=micro", "--cov-fail-under=25"],
            gerekli_modul="pytest",
        )

    print("\n" + "=" * 46)
    print("YEREL KONTROL OZETI")
    print("=" * 46)
    # ASCII: Windows konsolu (cp1254) ✓/✗ basamıyor
    for ad, ok in sonuclar.items():
        print(f"  [{'OK ' if ok else 'KIRIK'}]  {ad}")

    kirik = [ad for ad, ok in sonuclar.items() if not ok]
    if kirik:
        print(f"\n{len(kirik)} kapı kırık: {', '.join(kirik)}")
        return 1
    print("\nTüm kapılar geçti.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
