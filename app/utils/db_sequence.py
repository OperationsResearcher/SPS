"""PostgreSQL sequence senkronizasyon yardımcıları."""

from __future__ import annotations

from sqlalchemy import text

from app.models import db


def is_pk_duplicate(err: Exception, table_name: str) -> bool:
    """Hata mesajından PK duplicate olasılığını yakala."""
    msg = str(err).lower()
    table = str(table_name or "").lower().strip()
    if not table:
        return "duplicate key value violates unique constraint" in msg
    return (
        f"{table}_pkey" in msg
        or ("duplicate key value violates unique constraint" in msg and table in msg)
    )


def sync_pg_sequence_if_needed(table_name: str, pk_column: str = "id") -> bool:
    """PostgreSQL tablo sequence değerini MAX(id)+1'e hizala."""
    bind = db.session.get_bind() if hasattr(db.session, "get_bind") else None
    if bind is None:
        try:
            bind = db.engine
        except Exception:
            bind = None
    if bind is None or bind.dialect.name != "postgresql":
        return False

    seq_name = db.session.execute(
        text("SELECT pg_get_serial_sequence(:tbl, :col)"),
        {"tbl": table_name, "col": pk_column},
    ).scalar()
    if not seq_name:
        return False

    db.session.execute(
        text(
            f"SELECT setval(:seq, COALESCE((SELECT MAX({pk_column}) FROM {table_name}), 0) + 1, false)"
        ),
        {"seq": seq_name},
    )
    return True


def sync_many_sequences(pairs: list[tuple[str, str]] | None = None) -> dict[str, bool]:
    """Verilen tablo/kolon çiftleri için sequence hizalaması uygula."""
    items = pairs or []
    result: dict[str, bool] = {}
    for table_name, pk_column in items:
        key = f"{table_name}.{pk_column}"
        try:
            result[key] = bool(sync_pg_sequence_if_needed(table_name, pk_column))
        except Exception:
            db.session.rollback()
            result[key] = False
    return result
