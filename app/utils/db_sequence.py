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


def add_and_commit_with_retry(obj, table_name: str, pk_column: str = "id"):
    """Tek nesneyi ekle + commit; PK sequence desync'i (import/restore sonrası)
    UniqueViolation verirse sequence'i hizalayıp bir kez daha dener.

    kpi_data için var olan inline retry döngüsünün tek-noktadan, yeniden
    kullanılabilir hali. Blue Ocean / bildirim gibi insert yollarında
    "duplicate key value violates unique constraint" hatasını önler.
    """
    from sqlalchemy.exc import IntegrityError

    try:
        db.session.add(obj)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        if is_pk_duplicate(e, table_name):
            sync_pg_sequence_if_needed(table_name, pk_column)
            db.session.add(obj)
            db.session.commit()
        else:
            raise
    return obj


def commit_with_retry(table_name: str, restage=None, pk_column: str = "id") -> None:
    """Bekleyen oturumu commit et; PK desync UniqueViolation'ında sequence'i
    hizalayıp tekrar dener. Bulk insert için `restage`, rollback sonrası
    nesneleri yeniden hazırlayan bir callable olmalı (yoksa yalnız commit).
    """
    from sqlalchemy.exc import IntegrityError

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        if is_pk_duplicate(e, table_name):
            sync_pg_sequence_if_needed(table_name, pk_column)
            if restage is not None:
                restage()
            db.session.commit()
        else:
            raise


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


# Sequence'in bir sonraki üreteceği değeri ve tablodaki max id'yi karşılaştıran
# tarama. LİSTE TUTULMAZ (KURALLAR-MASTER §8.6 ile aynı gerekçe): elle tutulan
# liste bakılmadığı gün yalan söyler, yeni tablo sessizce kapsam dışı kalır.
# pg_depend üzerinden her sequence kendi tablosuna/kolonuna bağlanır.
_DRIFT_TARAMA_SQL = """
SELECT s.relname AS seq, t.relname AS tbl, a.attname AS col
FROM pg_class s
JOIN pg_depend d ON d.objid = s.oid AND d.classid = 'pg_class'::regclass
                AND d.refclassid = 'pg_class'::regclass AND d.deptype IN ('a','i')
JOIN pg_class t ON t.oid = d.refobjid
JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = d.refobjsubid
JOIN pg_namespace n ON n.oid = s.relnamespace AND n.nspname = 'public'
WHERE s.relkind = 'S'
ORDER BY t.relname
"""


def scan_sequence_drift() -> list[dict]:
    """Bir sonraki INSERT'te PK çakışması yaratacak sequence'leri bulur.

    S5 (2026-07-21): Yerel DB'de 155 sequence'in 6'sı `last_value=1,
    is_called=false` durumundaydı — yani `nextval` 1 DÖNDÜRÜR (artırmaz) ve
    o tablolarda id=1 zaten doluydu. Sonraki rol/bileşen ekleme denemesi
    `duplicate key value violates unique constraint` ile patlayacaktı.

    Muhtemel kaynak: Yayın→Yerel veri çekiminde `setval` adımının atlanması
    (CLAUDE.md'de bilinen tuzak olarak kayıtlı).

    Returns:
        [{'table','column','sequence','last_value','is_called','max_id','next_id'}]
    """
    bulgular: list[dict] = []
    for r in db.session.execute(text(_DRIFT_TARAMA_SQL)).fetchall():
        tbl = _validate_identifier(r.tbl, "table")
        col = _validate_identifier(r.col, "column")
        seq = _validate_identifier(r.seq, "sequence")
        try:
            max_id = db.session.execute(
                text(f'SELECT COALESCE(MAX("{col}"), 0) FROM "{tbl}"')
            ).scalar() or 0
            last_value, is_called = db.session.execute(
                text(f'SELECT last_value, is_called FROM "{seq}"')
            ).fetchone()
        except Exception:
            db.session.rollback()
            continue
        # is_called=false ise nextval last_value'yi AYNEN döndürür, artırmaz.
        next_id = last_value if not is_called else last_value + 1
        if next_id <= max_id:
            bulgular.append({
                "table": tbl, "column": col, "sequence": seq,
                "last_value": last_value, "is_called": is_called,
                "max_id": max_id, "next_id": next_id,
            })
    return bulgular


def repair_sequence_drift(dry_run: bool = True) -> dict:
    """`scan_sequence_drift` bulgularını setval ile onarır.

    Args:
        dry_run: True (varsayılan) hiçbir şey yazmaz, yalnız raporlar.
    """
    bulgular = scan_sequence_drift()
    onarilan: list[str] = []
    if not dry_run:
        for b in bulgular:
            try:
                db.session.execute(
                    text("SELECT setval(:seq, :val, true)"),
                    {"seq": b["sequence"], "val": b["max_id"]},
                )
                onarilan.append(b["table"])
            except Exception:
                db.session.rollback()
                continue
        if onarilan:
            db.session.commit()
    return {"bulunan": bulgular, "onarilan": onarilan, "dry_run": dry_run}
