#!/usr/bin/env python3
"""CI guard: app katmanında ikinci db instance importu yasak."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN = re.compile(r"from\s+app\.extensions\s+import\s+db\b")

errors: list[str] = []
for path in sorted(ROOT.glob("app/**/*.py")):
    rel = path.relative_to(ROOT).as_posix()
    if rel == "app/extensions.py":
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        continue
    if FORBIDDEN.search(text):
        errors.append(rel)

if errors:
    print("YASAK: 'from app.extensions import db' — extensions.db kullanın:")
    for line in errors:
        print(f"  - {line}")
    sys.exit(1)

print("OK: tek db import politikası")
