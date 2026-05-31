#!/usr/bin/env python3
"""Runtime dosyalarında `from models` → `from app.models.legacy_bridge` toplu geçiş."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

TARGET_DIRS = [
    ROOT / "services",
    ROOT / "app" / "services",
    ROOT / "app" / "utils",
    ROOT / "micro" / "modules",
    ROOT / "tests",
]
TARGET_FILES = [
    ROOT / "decorators.py",
    ROOT / "api" / "routes.py",
    ROOT / "main" / "routes.py",
    ROOT / "auth" / "routes.py",
    ROOT / "v2" / "routes.py",
    ROOT / "v3" / "routes.py",
]

SKIP_PARTS = {
    "models",
    "Yedekler",
    "scripts",
    "ARCHIVE",
    "skills",
    ".venv",
    "app/models/legacy_bridge.py",
}


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if any(s in parts for s in SKIP_PARTS):
        return True
    if path.name == "migrate_models_imports.py":
        return True
    return False


def migrate_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    text = re.sub(
        r"from\s+models\.project\s+import",
        "from app.models.portfolio_project import",
        text,
    )
    text = re.sub(
        r"from\s+models\.user\s+import",
        "from app.models.legacy_bridge import",
        text,
    )
    text = re.sub(
        r"from\s+models\.process\s+import",
        "from app.models.legacy_bridge import",
        text,
    )
    text = re.sub(
        r"from\s+models\.strategy\s+import",
        "from app.models.legacy_bridge import",
        text,
    )
    text = re.sub(
        r"from\s+models\.dashboard\s+import",
        "from app.models.legacy_bridge import",
        text,
    )
    text = re.sub(
        r"from\s+models\s+import",
        "from app.models.legacy_bridge import",
        text,
    )
    text = re.sub(
        r"import\s+models\b",
        "import app.models.legacy_bridge as models",
        text,
    )

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed: list[str] = []
    paths = list(TARGET_FILES)
    for d in TARGET_DIRS:
        if d.exists():
            paths.extend(sorted(d.rglob("*.py")))

    seen = set()
    for path in paths:
        if path in seen or not path.is_file() or should_skip(path):
            continue
        seen.add(path)
        if migrate_file(path):
            changed.append(path.relative_to(ROOT).as_posix())

    print(f"Güncellenen dosya sayısı: {len(changed)}")
    for c in changed[:60]:
        print(f"  {c}")
    if len(changed) > 60:
        print(f"  ... +{len(changed) - 60} daha")


if __name__ == "__main__":
    main()
