#!/usr/bin/env python3
"""main/routes.py dosyasını main/routes/ paketine böler (bir kerelik)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "main" / "routes.py"
PKG = ROOT / "main" / "routes"

SPLITS = [
    ("_common.py", 1, 204),
    ("pages.py", 205, 2033),
    ("kurum_panel.py", 2034, 3974),
    ("strategy_api.py", 3975, 5234),
    ("projects.py", 5235, None),
]

HEADER = '''# -*- coding: utf-8 -*-
# Otomatik bölüm — `python scripts/dev/split_main_routes.py`
from main.routes._common import *  # noqa: F401,F403
from main.routes import main_bp
'''

INIT = '''# -*- coding: utf-8 -*-
"""Main blueprint — modüler route paketi (Dalga C)."""
from flask import Blueprint

main_bp = Blueprint("main", __name__)

from main.routes import _common  # noqa: F401
from main.routes import pages  # noqa: F401
from main.routes import kurum_panel  # noqa: F401
from main.routes import strategy_api  # noqa: F401
from main.routes import projects  # noqa: F401
'''

COMMON_HEADER = '''# -*- coding: utf-8 -*-
"""Paylaşılan import ve yardımcılar — main route paketi."""
'''


def main() -> None:
    lines = SRC.read_text(encoding="utf-8").splitlines(keepends=True)
    PKG.mkdir(parents=True, exist_ok=True)

    common_body = "".join(lines[0:204])
    # main_bp tanımı paket __init__'te; monolit satırını kaldır
    common_body = common_body.replace(
        "main_bp = Blueprint('main', __name__)\n\n",
        "",
    )
    (PKG / "_common.py").write_text(COMMON_HEADER + common_body, encoding="utf-8")

    for name, start, end in SPLITS[1:]:
        chunk = lines[start - 1 : end]
        (PKG / name).write_text(HEADER + "".join(chunk), encoding="utf-8")

    (PKG / "__init__.py").write_text(INIT, encoding="utf-8")
    backup = ROOT / "main" / "routes_monolith_backup.py"
    if not backup.exists():
        backup.write_text(SRC.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"OK: {PKG} oluşturuldu. Yedek: {backup.name}")
    print("Sonraki adım: main/routes.py dosyasını silin veya yeniden adlandırın.")


if __name__ == "__main__":
    main()
