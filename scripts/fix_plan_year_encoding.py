# -*- coding: utf-8 -*-
"""
plan_years.name alanındaki mojibake (latin-1/utf-8 karışımı) karakterleri düzeltir.
Örnek: "PlanÄ±" → "Planı"
Kullanım: python scripts/fix_plan_year_encoding.py
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def fix_mojibake(s: str) -> str:
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def needs_fix(s: str) -> bool:
    try:
        encoded = s.encode("latin-1")
        decoded = encoded.decode("utf-8")
        return decoded != s
    except (UnicodeEncodeError, UnicodeDecodeError):
        return False


def main() -> int:
    from app import create_app
    from extensions import db
    from sqlalchemy import text

    app = create_app()
    with app.app_context():
        rows = db.session.execute(
            text("SELECT id, name FROM plan_years WHERE name IS NOT NULL")
        ).fetchall()

        fixed = 0
        for row_id, name in rows:
            if not name or not needs_fix(name):
                continue
            new_name = fix_mojibake(name)
            print(f"  ID {row_id}: {name!r} -> {new_name!r}")
            db.session.execute(
                text("UPDATE plan_years SET name = :name WHERE id = :id"),
                {"name": new_name, "id": row_id},
            )
            fixed += 1

        if fixed:
            db.session.commit()
            print(f"\n{fixed} kayıt düzeltildi.")
        else:
            print("Düzeltilecek kayıt yok.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
