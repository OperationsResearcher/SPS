"""KOD-01 / Faz 2.1 — eklenti nesneleri tek kaynak; etkisiz @csrf.exempt kalmamalı."""
import re
from pathlib import Path

import app.extensions as ae
import extensions as root

ROOT = Path(__file__).resolve().parent.parent


def test_tek_nesne(app):
    assert ae.csrf is root.csrf
    assert ae.login_manager is root.login_manager is app.login_manager
    assert ae.migrate is root.migrate
    assert ae.talisman is root.talisman


def test_csrf_exempt_yalniz_baslatilan_nesneye_yazilir(app):
    """`from extensions import csrf` ile exempt edilen uç sayısı init edilen nesneyle aynı olmalı
    (eskiden 75 uç ayrı, hiç init edilmeyen bir nesneye yazılıyordu)."""
    assert root.csrf is ae.csrf
    assert len(root.csrf._exempt_views) > 0


def test_kokten_csrf_importu_regresyonu_yok():
    """Kök `extensions.csrf` ve `app.extensions.csrf` aynı nesne olduğundan her ikisi de güvenli;
    ama yeni `@csrf.exempt` eklenirse GUV-26 envanterine (docs/ekim2026/csrf_exempt_envanteri.txt) not düşülmeli."""
    n = 0
    for d in ("api", "app", "main", "micro"):
        for p in (ROOT / d).rglob("*.py"):
            n += len(re.findall(r"^\s*@csrf\.exempt", p.read_text(encoding="utf-8"), re.M))
    assert n == 53 or n <= 60, f"@csrf.exempt sayısı beklenmedik arttı: {n}"
