"""Fail when legacy schema names still exist in active code."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_DIRS = [
    ROOT / "app" / "models",
    ROOT / "services",
    ROOT / "micro" / "modules" / "admin",
    ROOT / "ui" / "templates" / "platform" / "ayarlar",
]
SKIP_DIRS = {"__pycache__"}
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".sql", ".xlsx", ".pptx"}

TOKENS = [
    r"['\"]surec_performans_gostergesi['\"]",
    r"['\"]performans_gosterge_veri['\"]",
    r"['\"]bireysel_performans_gostergesi['\"]",
    r"['\"]bireysel_faaliyet['\"]",
    r"['\"]surec_faaliyet['\"]",
    r"['\"]surec['\"]",
]
PATTERNS = [re.compile(t) for t in TOKENS]


def should_skip(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return True
    if path.suffix.lower() in SKIP_EXT:
        return True
    return False


def main() -> int:
    hits: list[tuple[str, int, str]] = []
    for base in TARGET_DIRS:
        if not base.exists():
            continue
        iterator = base.rglob("*")
        for p in iterator:
            if not p.is_file() or should_skip(p):
                continue
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for i, line in enumerate(txt.splitlines(), 1):
                if any(rx.search(line) for rx in PATTERNS):
                    hits.append((str(p.relative_to(ROOT)), i, line.strip()))
    if hits:
        print("Legacy schema reference bulundu:")
        for fp, ln, line in hits[:300]:
            print(f"- {fp}:{ln} -> {line}")
        print(f"\nToplam: {len(hits)} satır")
        return 1
    print("OK: legacy schema referansı bulunmadı.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
