# -*- coding: utf-8 -*-
"""Silinen ölü kod geri gelmesin — tek yerde koruma.

Ölü kod silmek kolay, silinmiş kalmasını sağlamak zor: eski bir dal merge
edilir, biri "lazım olur" diye geri koyar, kimse fark etmez. Buradaki testler
o dosyaların geri dönmediğini garanti eder.

Yeni bir ölü kod silindiğinde SILINEN listesine bir satır ekle.
"""
import os

import pytest

# (yol, neden silindi, doğru yer)
SILINEN = [
    (
        "app/routes/process.py",
        "1806 satır legacy süreç route'u — config default false, lazy import, "
        "testi kapalı olmasını şart koşuyordu (TASK-248)",
        "micro/modules/surec/",
    ),
    (
        "app/api/auth.py",
        "221 satır ölü JWT/API-key modülü — hiçbir yerden import edilmiyordu; "
        "api_key_required API key'i DOĞRULAMIYORDU (TODO bırakılmış) (TASK-250)",
        "Gerçek API auth gerekirse: app/api/data_connector.py token deseni",
    ),
]


@pytest.mark.parametrize("yol,neden,dogru_yer", SILINEN)
def test_silinen_dosya_geri_gelmemis(yol, neden, dogru_yer):
    assert not os.path.exists(yol), (
        f"'{yol}' geri gelmiş!\n"
        f"Neden silinmişti: {neden}\n"
        f"Yeni iş buraya yazılır: {dogru_yer}"
    )


def test_jwt_kutuphanesi_artik_kullanilmiyor():
    """PyJWT'nin tek kullanıcısı silinen app/api/auth.py idi.

    Biri JWT'yi geri getirirse requirements'a da eklemesi gerekir — bu test
    'import var ama bağımlılık yok' sessiz kırılmasını erken yakalar.
    """
    import subprocess
    import sys

    sonuc = subprocess.run(
        [sys.executable, "-c", "import jwt"],
        capture_output=True,
    )
    if sonuc.returncode == 0:
        # jwt hâlâ kurulu olabilir (eski venv) — asıl kontrol: kod onu kullanıyor mu?
        kod_kullaniyor = subprocess.run(
            ["git", "grep", "-l", "-E", r"^\s*import jwt|^\s*from jwt import", "--", "*.py"],
            capture_output=True, text=True,
        )
        assert not kod_kullaniyor.stdout.strip(), (
            f"JWT tekrar import edilmiş: {kod_kullaniyor.stdout.strip()}\n"
            f"requirements.txt'e PyJWT eklemeyi unutma."
        )
