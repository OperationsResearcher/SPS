import os
import sqlite3
from typing import Dict, List, Tuple

import pandas as pd
from sqlalchemy import create_engine, text, inspect


SOURCE_PRIMARY = "spsv2_yedek.db"
SOURCE_FALLBACK = "spsv2.db"


def _log(msg: str) -> None:
    print(msg)


def _pick_source() -> str:
    if os.path.exists(SOURCE_PRIMARY):
        return SOURCE_PRIMARY
    if os.path.exists(SOURCE_FALLBACK):
        return SOURCE_FALLBACK
    raise FileNotFoundError(
        f"Kaynak dosya bulunamadı: '{SOURCE_PRIMARY}' veya '{SOURCE_FALLBACK}'"
    )


def _get_target_url() -> str:
    url = (os.getenv("SUPABASE_DATABASE_URL") or os.getenv("DATABASE_URL") or "").strip()
    if not url:
        raise EnvironmentError(
            "SUPABASE_DATABASE_URL veya DATABASE_URL tanımlı değil."
        )
    return url


def _list_sqlite_tables(conn: sqlite3.Connection) -> List[str]:
    df = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';",
        conn,
    )
    return df["name"].tolist()


def _count_sqlite_rows(conn: sqlite3.Connection, tables: List[str]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for table in tables:
        try:
            df = pd.read_sql(f'SELECT COUNT(*) AS cnt FROM "{table}";', conn)
            counts[table] = int(df.iloc[0]["cnt"])
        except Exception as exc:
            _log(f"[WARN] SQLite sayım hatası ({table}): {exc}")
            counts[table] = -1
    return counts


def _count_pg_rows(engine, tables: List[str]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for table in tables:
        try:
            with engine.connect() as conn:
                df = pd.read_sql(
                    f'SELECT COUNT(*) AS cnt FROM "{table}";',
                    conn,
                )
                counts[table] = int(df.iloc[0]["cnt"])
        except Exception as exc:
            _log(f"[WARN] Postgres sayım hatası ({table}): {exc}")
            counts[table] = -1
    return counts


def _coerce_bool_columns(df: pd.DataFrame, bool_cols: List[str]) -> pd.DataFrame:
    if not bool_cols:
        return df
    for col in bool_cols:
        if col not in df.columns:
            continue
        def to_bool(val):
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return None
            if isinstance(val, bool):
                return val
            try:
                return bool(int(val))
            except Exception:
                return bool(val)
        df[col] = df[col].apply(to_bool)
    return df


def _coerce_int_columns(df: pd.DataFrame, int_cols: List[str]) -> pd.DataFrame:
    if not int_cols:
        return df
    for col in int_cols:
        if col not in df.columns:
            continue
        df[col] = df[col].replace("", None)
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    return df


def _truncate_target_tables(pg_engine, tables: List[str]) -> None:
    _log("[STEP] Hedef tablolar temizleniyor (TRUNCATE CASCADE)...")
    with pg_engine.connect() as conn:
        for table in tables:
            try:
                with conn.begin():
                    conn.execute(text(f'TRUNCATE TABLE "{table}" CASCADE;'))
                _log(f"[OK] {table}: temizlendi")
            except Exception as exc:
                _log(f"[WARN] {table}: temizlenemedi -> {exc}")


def _transfer_tables(sqlite_conn, pg_engine, table_map: Dict[str, str]) -> None:
    inspector = inspect(pg_engine)
    for src_table, dst_table in table_map.items():
        if not dst_table:
            continue
        try:
            df = pd.read_sql(f'SELECT * FROM "{src_table}";', sqlite_conn)
            if df.empty:
                _log(f"[SKIP] {src_table}: veri yok")
                continue

            columns = inspector.get_columns(dst_table)
            bool_cols = [
                c["name"] for c in columns
                if str(c["type"]).lower() in ("boolean", "bool")
            ]
            int_cols = [
                c["name"] for c in columns
                if str(c["type"]).lower() in ("integer", "smallint", "bigint")
            ]
            df = _coerce_bool_columns(df, bool_cols)
            df = _coerce_int_columns(df, int_cols)

            with pg_engine.connect() as conn:
                with conn.begin():
                    conn.execute(text("SET session_replication_role = 'replica';"))
                    df.to_sql(
                        dst_table,
                        conn,
                        if_exists="append",
                        index=False,
                        method="multi",
                        chunksize=1000,
                    )
                    conn.execute(text("SET session_replication_role = 'origin';"))
            _log(f"[OK] {src_table} -> {dst_table}: {len(df)} kayıt aktarıldı")
        except Exception as exc:
            _log(f"[ERROR] {src_table}: aktarım hatası -> {exc}")


def _fix_sequences(pg_engine, tables: List[str]) -> None:
    with pg_engine.connect() as conn:
        for table in tables:
            try:
                with conn.begin():
                    sql = (
                        "SELECT setval(pg_get_serial_sequence(:t, 'id'), "
                        "COALESCE(MAX(id), 1)) FROM " + f'"{table}";'
                    )
                    conn.execute(text(sql), {"t": table})
                _log(f"[OK] {table}: sequence reset")
            except Exception as exc:
                _log(f"[WARN] {table}: sequence reset yok sayıldı -> {exc}")


def _print_comparison(src_counts: Dict[str, int], dst_counts: Dict[str, int]) -> None:
    headers = ["TABLO", "KAYNAK", "HEDEF", "DURUM"]
    rows: List[Tuple[str, str, str, str]] = []
    for table in sorted(src_counts.keys()):
        src = src_counts.get(table, -1)
        dst = dst_counts.get(table, -1)
        status = "OK" if src == dst and src != -1 else "MISMATCH"
        rows.append((table, str(src), str(dst), status))

    widths = [
        max(len(headers[0]), max(len(r[0]) for r in rows)),
        max(len(headers[1]), max(len(r[1]) for r in rows)),
        max(len(headers[2]), max(len(r[2]) for r in rows)),
        max(len(headers[3]), max(len(r[3]) for r in rows)),
    ]
    line = "+".join("-" * (w + 2) for w in widths)

    def fmt(row: Tuple[str, str, str, str]) -> str:
        return "|".join(f" {col:<{w}} " for col, w in zip(row, widths))

    _log("\nKARSILASTIRMA TABLOSU")
    _log(line)
    _log(fmt(tuple(headers)))  # type: ignore[arg-type]
    _log(line)
    for row in rows:
        _log(fmt(row))
    _log(line)


def main() -> None:
    source_path = _pick_source()
    target_url = _get_target_url()

    _log(f"[INFO] Kaynak: {source_path}")
    _log("[INFO] Hedef: Supabase/PostgreSQL (env ile)")

    sqlite_conn = sqlite3.connect(source_path)
    pg_engine = create_engine(target_url)

    tables = _list_sqlite_tables(sqlite_conn)
    src_counts = _count_sqlite_rows(sqlite_conn, tables)

    target_tables = set(inspect(pg_engine).get_table_names())
    table_map: Dict[str, str] = {}
    for table in tables:
        if table in target_tables:
            table_map[table] = table
        elif f"mock_{table}" in target_tables:
            table_map[table] = f"mock_{table}"
        else:
            table_map[table] = ""

    _log("[STEP] Transfer başlıyor...")
    mapped_targets = sorted({t for t in table_map.values() if t})
    _truncate_target_tables(pg_engine, mapped_targets)
    _transfer_tables(sqlite_conn, pg_engine, table_map)

    _log("[STEP] Sequence reset başlıyor...")
    _fix_sequences(pg_engine, mapped_targets)

    _log("[STEP] Doğrulama başlıyor...")
    dst_counts: Dict[str, int] = {}
    for table in tables:
        dst_table = table_map.get(table) or ""
        if not dst_table:
            dst_counts[table] = 0 if src_counts.get(table, 0) == 0 else -1
            continue
        dst_counts[table] = _count_pg_rows(pg_engine, [dst_table]).get(dst_table, -1)

    _print_comparison(src_counts, dst_counts)

    sqlite_conn.close()


if __name__ == "__main__":
    main()
