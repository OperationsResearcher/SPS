"""Import köprüsü ve uygulama fabrikası smoke."""
from app import create_app
from app.models.legacy_bridge import (
    BireyselPerformansGostergesi,
    PerformansGostergeVeri,
    Project,
    Surec,
    User,
)
from config import TestingConfig


def test_create_app():
    app = create_app(TestingConfig)
    assert app is not None
    assert len(app.url_map._rules) > 100


def test_legacy_bridge_exports():
    assert Surec.__tablename__
    assert Project.__tablename__
    assert hasattr(BireyselPerformansGostergesi, "kaynak_surec_pg_id")
    assert hasattr(PerformansGostergeVeri, "bireysel_pg_id")
    assert User.__tablename__ in ("users", "user")


def test_no_direct_process_bp_import_outside_init():
    """Sprint 29-30: app/routes/process.py sadece app/__init__.py'da lazy import edilmeli.

    Başka modülün doğrudan import etmesi yasak (legacy temizlik koruması).
    """
    import os
    import re
    forbidden = re.compile(r"from\s+app\.routes\.process\s+import")
    violators = []
    for root, _, files in os.walk("app"):
        for fn in files:
            if not fn.endswith(".py"):
                continue
            path = os.path.join(root, fn)
            if path.replace("\\", "/").endswith("app/__init__.py"):
                continue  # bilinçli lazy import
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                if forbidden.search(f.read()):
                    violators.append(path)
    assert not violators, (
        f"Legacy process_bp dışarıdan import edilmiş: {violators}. "
        f"Yeni iş micro/surec'e taşı."
    )


def test_no_decorators_py_root_import():
    """Sprint 20'de silinen root decorators.py'a dönüş yapılmamalı."""
    import os
    import re
    forbidden = re.compile(r"^from\s+decorators\s+import|^import\s+decorators\s*$", re.M)
    violators = []
    for root, _, files in os.walk("."):
        if any(skip in root for skip in (".venv", "eski_proje", "Yedekler", "htmlcov", "__pycache__")):
            continue
        for fn in files:
            if not fn.endswith(".py"):
                continue
            # Backup/monolith dosyaları muaf
            if "monolith_backup" in fn or "_backup" in fn:
                continue
            path = os.path.join(root, fn)
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                if forbidden.search(f.read()):
                    violators.append(path)
    assert not violators, (
        f"Root decorators.py (silindi) referansı: {violators}. "
        f"`from app.utils.project_rbac import` kullan."
    )
