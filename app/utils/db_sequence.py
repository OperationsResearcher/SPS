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


import re as _re

# Güvenlik: identifier sadece [a-zA-Z0-9_] olabilir (SQL injection koruması)
_IDENTIFIER_RE = _re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def _validate_identifier(name: str, kind: str) -> str:
    """SQL identifier (table_name, column_name) güvenliğini doğrula."""
    if not name or not _IDENTIFIER_RE.match(name):
        raise ValueError(
            f"Geçersiz {kind}: {name!r}. Sadece [a-zA-Z0-9_] karakterleri kabul edilir."
        )
    return name


def sync_pg_sequence_if_needed(table_name: str, pk_column: str = "id") -> bool:
    """PostgreSQL tablo sequence değerini MAX(id)+1'e hizala.

    Güvenlik: table_name ve pk_column SQL injection'a karşı strict regex ile
    doğrulanır — f-string interpolation bu aşamadan sonra güvenlidir.
    """
    # SQL injection koruması
    table_name = _validate_identifier(table_name, "table_name")
    pk_column = _validate_identifier(pk_column, "pk_column")

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

    # Identifier'lar validate edildi — f-string güvenli
    db.session.execute(
        text(
            f"SELECT setval(:seq, COALESCE((SELECT MAX({pk_column}) FROM {table_name}), 0) + 1, false)"
        ),
        {"seq": seq_name},
    )
    return True


def sync_kpi_data_related_sequences() -> None:
    """kpi_data ve kpi_data_audits id sekanslarını tablodaki MAX(id) ile hizalar.

    Import / dump sonrası sekans geride kaldığında INSERT duplicate key hatasını giderir.
    """
    sync_pg_sequence_if_needed("kpi_data", "id")
    sync_pg_sequence_if_needed("kpi_data_audits", "id")


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
