# -*- coding: utf-8 -*-
"""Yerel DB: alembic sürümü ve tenant_id kolon kontrolü (tek seferlik doğrulama)."""
from __future__ import annotations

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from sqlalchemy import text

from app import create_app
from app.models import db

TABLES = ("project", "ana_strateji", "surec", "kurum", "user")


def main():
    app = create_app()
    with app.app_context():
        ver = db.session.execute(text("SELECT version_num FROM alembic_version")).scalar()
        print("alembic_version:", ver)
        in_list = ", ".join(f"'{t}'" for t in TABLES)
        existing = {
            r[0]
            for r in db.session.execute(
                text(
                    f"SELECT tablename FROM pg_tables WHERE schemaname = 'public' "
                    f"AND tablename IN ({in_list})"
                )
            ).fetchall()
        }
        print("mevcut tablolar:", sorted(existing))
        for t in TABLES:
            if t not in existing:
                print(f"  {t}: (tablo yok)")
                continue
            rows = db.session.execute(
                text(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = :t
                      AND column_name IN ('tenant_id', 'kurum_id')
                    ORDER BY column_name
                    """
                ),
                {"t": t},
            ).fetchall()
            cols = [r[0] for r in rows]
            print(f"  {t}: {cols}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
