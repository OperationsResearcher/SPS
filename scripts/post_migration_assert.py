# -*- coding: utf-8 -*-
"""Post migration assert report for canonical schema."""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app
from services.admin_backup_service import get_post_migration_assert, get_language_unity_status


def main() -> int:
    app = create_app()
    with app.app_context():
        a = get_post_migration_assert()
        l = get_language_unity_status()
    print("Alembic version:", a["alembic_version"])
    print("Legacy tables present:", a["legacy_tables_present"] or "none")
    print("Canonical tables missing:", a["canonical_tables_missing"] or "none")
    print("Schema clean:", a["is_clean"])
    print("Language unity score:", f'{l["score"]}%')
    print("Scanned files:", l["scanned_files"])
    if l["issues"]:
        print("First issues:")
        for item in l["issues"][:10]:
            print(f"- {item['file']}:{item['line']} -> {item['text']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
