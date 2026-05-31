#!/usr/bin/env python3
"""Runtime kodunda doğrudan `from models import` yasak — legacy_bridge kullanın."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

WATCH_DIRS = [
    ROOT / "services",
    ROOT / "app" / "services",
    ROOT / "app" / "utils",
    ROOT / "micro" / "modules",
    ROOT / "tests",
    ROOT / "decorators.py",
    ROOT / "main" / "admin.py",
    ROOT / "api" / "routes.py",
    ROOT / "main" / "routes.py",
    ROOT / "auth" / "routes.py",
]

ALLOWED = {
    ROOT / "app" / "models" / "legacy_bridge.py",
    ROOT / "app" / "models" / "user_legacy.py",
    ROOT / "app" / "models" / "strategy_legacy.py",
    ROOT / "app" / "models" / "legacy_extras.py",
}

FORBIDDEN = re.compile(r"^\s*from\s+models(\.\w+)?\s+import\b")

errors: list[str] = []
for base in WATCH_DIRS:
    paths = [base] if base.is_file() else sorted(base.rglob("*.py"))
    for path in paths:
        if path in ALLOWED or not path.is_file():
            continue
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if FORBIDDEN.match(line):
                errors.append(f"{path.relative_to(ROOT).as_posix()}:{i}")

if errors:
    print("YASAK: doğrudan 'from models' — app.models.legacy_bridge veya canonical import kullanın:")
    for e in errors[:40]:
        print(f"  - {e}")
    if len(errors) > 40:
        print(f"  ... +{len(errors) - 40}")
    sys.exit(1)

print("OK: raw models import yok")
