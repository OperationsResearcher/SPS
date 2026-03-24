"""Bağlı veritabanında model tablolarının varlığını hızlı kontrol eder.

SQLite ↔ PostgreSQL geçişinde migration atlanmış tablolar için
`ProgrammingError: relation does not exist` riskini önceden görmeye yarar.

Kullanım:
    python scripts/check_pg_schema_gaps.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from sqlalchemy import inspect

from app import create_app
from app.models import db

# ORM'de tanımlı; Alembic/pgloader ile her ortamda garanti olmayan tablolar
OPTIONAL_TABLES: tuple[tuple[str, str], ...] = (
    ("raid_item", "RAID özeti (kurum/proje panelleri)"),
    ("capacity_plan", "Proje kapasite planı"),
    ("working_day", "Çalışma günleri"),
    ("task_baseline", "Görev baz çizgisi"),
    ("project_risk", "Proje riski"),
    ("recurring_task", "Yinelenen görev"),
    ("integration_hook", "Entegrasyon kancası"),
    ("rule_definition", "Kural tanımı"),
    ("sla", "SLA"),
)

# Eski SQLite şeması; saf `processes` / `users` PG kurulumunda olmayabilir
LEGACY_TABLES: tuple[tuple[str, str], ...] = (
    ("surec", "Legacy süreç (micro: processes kullanılır)"),
    ("user", "Legacy kullanıcı (micro: users)"),
)


def main() -> None:
    app = create_app()
    with app.app_context():
        bind = db.engine
        insp = inspect(bind)
        dialect = bind.dialect.name
        print(f"Bağlantı: {dialect}\n")

        def section(title: str, rows: tuple[tuple[str, str], ...]) -> None:
            print(title)
            print("-" * len(title))
            for table, note in rows:
                ok = insp.has_table(table)
                stat = "VAR" if ok else "YOK"
                print(f"  [{stat:3}] {table:24} — {note}")
            print()

        section("İsteğe bağlı / sık atlanan tablolar", OPTIONAL_TABLES)
        section("Legacy (PG-only ortamda eksik olabilir)", LEGACY_TABLES)


if __name__ == "__main__":
    main()
