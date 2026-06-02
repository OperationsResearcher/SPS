# -*- coding: utf-8 -*-
"""Demo ortamı — Tomofil verisini baseline'a sıfırlama (Yol B).

KURALLAR-MASTER §8.4 mutabakatı. Demo DB'nin tüm public tablolarının bir
`demo_baseline` şema kopyası tutulur; sıfırlamada PostgreSQL replica modunda
(FK kapalı) truncate + baseline'dan kopyalama + sequence resync yapılır.

DEMİR GUARD: Tüm yıkıcı işlemler yalnızca `KOKPITIM_DEMO_MODE=1` iken çalışır.
Yerel (flag=0) / Test / Yayın'da ASLA tetiklenmez — yanlış DB'yi sıfırlama riski sıfır.
"""
from __future__ import annotations

import logging

from flask import current_app
from sqlalchemy import text

from app.models import db

logger = logging.getLogger(__name__)

BASELINE_SCHEMA = "demo_baseline"

# Sıfırlamaya DAHİL EDİLMEYEN public tabloları:
#  - alembic_version: migration durumu korunmalı
#  - demo_runtime:    inaktivite izleme (kendi durumunu sıfırlamamalı)
_EXCLUDE_TABLES = frozenset({"alembic_version", "demo_runtime"})


def _assert_demo() -> None:
    """Yıkıcı işlemler yalnızca demo modunda. Aksi halde RuntimeError."""
    if not current_app.config.get("KOKPITIM_DEMO_MODE"):
        raise RuntimeError(
            "demo_reset_service yalnızca KOKPITIM_DEMO_MODE=1 iken çalışır "
            "(yanlış ortamda DB sıfırlama önlemi)."
        )


def _public_tables(conn) -> list[str]:
    rows = conn.execute(text(
        "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
    )).fetchall()
    return [r[0] for r in rows if r[0] not in _EXCLUDE_TABLES]


def _collect_fk_constraints(conn) -> list[tuple[str, str, str]]:
    """public şemasındaki tüm FK constraint'leri: (conname, public-qualified tablo, tanım)."""
    rows = conn.execute(text("""
        SELECT c.conname, t.relname, pg_get_constraintdef(c.oid)
        FROM pg_constraint c
        JOIN pg_class t      ON t.oid = c.conrelid
        JOIN pg_namespace n  ON n.oid = c.connamespace
        WHERE c.contype = 'f' AND n.nspname = 'public'
    """)).fetchall()
    return [(r[0], r[1], r[2]) for r in rows if r[1] not in _EXCLUDE_TABLES]


def _collect_fk_details(conn) -> list[dict]:
    """FK'leri orphan-temizliği için detaylı topla (tek-kolon child/parent kolonları dahil)."""
    rows = conn.execute(text("""
        SELECT c.conname, t.relname, pg_get_constraintdef(c.oid),
               (SELECT attname FROM pg_attribute WHERE attrelid = c.conrelid  AND attnum = c.conkey[1]),
               pt.relname,
               (SELECT attname FROM pg_attribute WHERE attrelid = c.confrelid AND attnum = c.confkey[1]),
               array_length(c.conkey, 1)
        FROM pg_constraint c
        JOIN pg_class t     ON t.oid = c.conrelid
        JOIN pg_namespace n ON n.oid = c.connamespace
        JOIN pg_class pt    ON pt.oid = c.confrelid
        WHERE c.contype = 'f' AND n.nspname = 'public'
    """)).fetchall()
    return [
        {"conname": r[0], "child": r[1], "cdef": r[2], "childcol": r[3],
         "parent": r[4], "parentcol": r[5], "ncols": r[6]}
        for r in rows if r[1] not in _EXCLUDE_TABLES
    ]


def _clean_orphans_iterative(conn, fks: list[dict], max_passes: int = 6) -> int:
    """FK'siz ortamda parent'ı olmayan (orphan) child satırları sabit noktaya kadar siler.

    Bir orphan'ı silmek başka bir FK'de yeni orphan yaratabileceği (cascade) için
    silme 0'a inene kadar tekrarlanır. Yalnızca tek-kolonlu FK'ler için.
    """
    single = [f for f in fks if f["ncols"] == 1]
    total = 0
    for _ in range(max_passes):
        deleted = 0
        for f in single:
            r = conn.execute(text(
                f'DELETE FROM public."{f["child"]}" WHERE "{f["childcol"]}" IS NOT NULL '
                f'AND "{f["childcol"]}" NOT IN (SELECT "{f["parentcol"]}" FROM public."{f["parent"]}")'
            ))
            deleted += (r.rowcount or 0)
        total += deleted
        if deleted == 0:
            break
    logger.info("[demo_reset] orphan temizliği: %d satır silindi", total)
    return total


def _resync_sequences(conn) -> None:
    """Restore sonrası: her identity/serial sequence'i max(kolon)'a ayarla."""
    seqs = conn.execute(text("""
        SELECT s.relname AS seq, t.relname AS tbl, a.attname AS col
        FROM pg_class s
        JOIN pg_depend d   ON d.objid = s.oid AND d.deptype = 'a'
        JOIN pg_class t    ON t.oid = d.refobjid
        JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = d.refobjsubid
        JOIN pg_namespace n ON n.oid = t.relnamespace
        WHERE s.relkind = 'S' AND n.nspname = 'public'
    """)).fetchall()
    for seq, tbl, col in seqs:
        if tbl in _EXCLUDE_TABLES:
            continue
        conn.execute(text(
            f'SELECT setval(\'public."{seq}"\', '
            f'(SELECT COALESCE(MAX("{col}"), 1) FROM public."{tbl}"))'
        ))


def baseline_exists() -> bool:
    with db.engine.connect() as conn:
        return conn.execute(text(
            "SELECT 1 FROM information_schema.schemata WHERE schema_name = :s"
        ), {"s": BASELINE_SCHEMA}).first() is not None


def snapshot_baseline() -> None:
    """Mevcut public veriyi `demo_baseline` şemasına dondurur (kurulumda 1 kez).

    Yerel Tomofil verisi demo'ya yüklendikten SONRA çalıştırılır; bu an
    'başlangıç noktası' olur.
    """
    _assert_demo()
    conn = db.engine.connect()
    trans = conn.begin()
    try:
        conn.execute(text(f"DROP SCHEMA IF EXISTS {BASELINE_SCHEMA} CASCADE"))
        conn.execute(text(f"CREATE SCHEMA {BASELINE_SCHEMA}"))
        n = 0
        for t in _public_tables(conn):
            conn.execute(text(
                f'CREATE TABLE {BASELINE_SCHEMA}."{t}" '
                f'(LIKE public."{t}" INCLUDING DEFAULTS)'
            ))
            conn.execute(text(
                f'INSERT INTO {BASELINE_SCHEMA}."{t}" SELECT * FROM public."{t}"'
            ))
            n += 1
        trans.commit()
        logger.info("[demo_reset] baseline snapshot alındı (%d tablo)", n)
    except Exception:
        trans.rollback()
        logger.error("[demo_reset] snapshot başarısız", exc_info=True)
        raise
    finally:
        conn.close()


def restore_baseline() -> bool:
    """public veriyi baseline'dan geri yükler — sıfırlama tetiklerinde çağrılır.

    Returns: True = sıfırlandı, False = baseline yok (atlandı).
    """
    _assert_demo()
    if not baseline_exists():
        logger.warning("[demo_reset] baseline şema yok — sıfırlama atlandı (önce snapshot_baseline)")
        return False

    conn = db.engine.connect()
    trans = conn.begin()
    try:
        # Eşzamanlı sıfırlamaları serialize et (sweeper + /demo/end + heartbeat aynı anda tetiklenebilir).
        # Kilit alınamazsa: zaten bir sıfırlama sürüyor → atla (tx sonunda otomatik bırakılır).
        if not conn.execute(text("SELECT pg_try_advisory_xact_lock(918273645)")).scalar():
            logger.info("[demo_reset] başka bir sıfırlama sürüyor — bu çağrı atlandı")
            trans.rollback()
            return False
        tables = _public_tables(conn)
        # Non-superuser uyumlu: session_replication_role kullanılamadığı için
        # FK constraint'leri geçici kaldırılır → truncate+insert sıra-bağımsız → FK geri eklenir.
        fks = _collect_fk_constraints(conn)
        for conname, tbl, _cdef in fks:
            conn.execute(text(f'ALTER TABLE public."{tbl}" DROP CONSTRAINT "{conname}"'))
        for t in tables:
            conn.execute(text(f'TRUNCATE TABLE public."{t}"'))
        for t in tables:
            conn.execute(text(
                f'INSERT INTO public."{t}" SELECT * FROM {BASELINE_SCHEMA}."{t}"'
            ))
        for conname, tbl, cdef in fks:
            conn.execute(text(f'ALTER TABLE public."{tbl}" ADD CONSTRAINT "{conname}" {cdef}'))
        _resync_sequences(conn)
        trans.commit()
        logger.info("[demo_reset] Tomofil baseline'a sıfırlandı (%d tablo, %d FK)", len(tables), len(fks))
        return True
    except Exception:
        trans.rollback()
        logger.error("[demo_reset] sıfırlama başarısız", exc_info=True)
        raise
    finally:
        conn.close()


def fk_safe_tenant_load(data: dict) -> dict:
    """tenant_backup_service.restore_tenant_data'yı FK-drop sarmalı içinde çalıştırır.

    Dolu bir tenant'ı değiştirirken silme FK-sırası sorununu (process_maturity →
    processes vb.) aşar: tüm FK'ler geçici kaldırılır → sıra-bağımsız delete+insert →
    FK'ler geri eklenir → sequence resync. Yalnızca demo modunda.
    """
    _assert_demo()
    from services.tenant_backup_service import restore_tenant_data

    # 1) FK detaylarını topla + tüm FK'leri kaldır
    with db.engine.begin() as conn:
        fks = _collect_fk_details(conn)
        for f in fks:
            conn.execute(text(f'ALTER TABLE public."{f["child"]}" DROP CONSTRAINT "{f["conname"]}"'))
    logger.info("[demo_reset] tenant load: %d FK kaldırıldı", len(fks))

    try:
        # 2) FK'siz ortamda tenant restore (delete + insert, sıra-bağımsız)
        result = restore_tenant_data(data)
        db.session.commit()
        # 3) Kapsam-dışı orphan'ları iteratif temizle (notifications vb. — TABLE_PLAN dışı tablolar)
        with db.engine.begin() as conn:
            _clean_orphans_iterative(conn, fks)
        # 4) FK'leri geri ekle + sequence resync (orphan temizlendiği için başarılı olmalı)
        failed = []
        for f in fks:
            try:
                with db.engine.begin() as conn:
                    conn.execute(text(f'ALTER TABLE public."{f["child"]}" ADD CONSTRAINT "{f["conname"]}" {f["cdef"]}'))
            except Exception as e:
                failed.append((f["conname"], str(e)[:120]))
        with db.engine.begin() as conn:
            _resync_sequences(conn)
        if failed:
            logger.error("[demo_reset] %d FK geri eklenemedi: %s", len(failed), failed[:5])
            raise RuntimeError(f"{len(failed)} FK geri eklenemedi (ilk: {failed[0]})")
        logger.info("[demo_reset] tenant load: %d FK geri eklendi + sequence resync", len(fks))
        return result
    except Exception:
        logger.error("[demo_reset] fk_safe_tenant_load HATA — FK'ler kaldırılmış olabilir, yedekten kurtar", exc_info=True)
        raise


def safe_restore_baseline() -> bool:
    """Tetiklerden çağrılan best-effort sarmalayıcı — istisna yutar, isteği bozmaz."""
    try:
        return restore_baseline()
    except Exception as e:
        logger.error("[demo_reset] safe_restore hata: %s", e, exc_info=True)
        return False


def trigger_async_reset() -> None:
    """Sıfırlamayı ARKA PLAN thread'inde başlatır → HTTP isteğini bloke etmez.

    Sebep: restore_baseline ~1-2 dk (156 tablo truncate + ~92k satır + 236 FK drop/readd).
    Senkron çağrıda gunicorn worker timeout → SIGKILL → 502. Thread'de çalışınca
    /demo/end anında yanıt verir; restore_baseline atomik (tek transaction) + advisory
    lock'lu olduğundan thread kesilse bile rollback olur ve çift-çalışma engellenir.
    """
    if not current_app.config.get("KOKPITIM_DEMO_MODE"):
        return
    import threading
    app = current_app._get_current_object()

    def _run():
        with app.app_context():
            safe_restore_baseline()

    threading.Thread(target=_run, daemon=True, name="demo-reset").start()


# ── İnaktivite izleme (demo_runtime tablosu — Alembic'siz, snapshot/restore'dan hariç) ──

def _ensure_runtime_table(conn) -> None:
    conn.execute(text(
        "CREATE TABLE IF NOT EXISTS public.demo_runtime (k text PRIMARY KEY, v text)"
    ))


def mark_activity() -> None:
    """Demo aktivitesini damgalar (demo_start + heartbeat çağırır). Best-effort.

    last_activity = now(); dirty = '1' (veri değişmiş olabilir → sweep sıfırlayabilir).
    """
    if not current_app.config.get("KOKPITIM_DEMO_MODE"):
        return
    try:
        with db.engine.begin() as conn:
            _ensure_runtime_table(conn)
            conn.execute(text(
                "INSERT INTO public.demo_runtime(k, v) "
                "VALUES ('last_activity', now()::text), ('dirty', '1') "
                "ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v"
            ))
    except Exception:
        logger.error("[demo_reset] mark_activity hata", exc_info=True)


def inactivity_sweep(inactivity_minutes: int = 15) -> bool:
    """İnaktivite eşiği aşıldıysa ve veri 'dirty' ise Tomofil'i baseline'a sıfırla.

    Scheduler tarafından periyodik çağrılır. KOKPITIM_DEMO_MODE dışında no-op.
    """
    if not current_app.config.get("KOKPITIM_DEMO_MODE"):
        return False
    try:
        with db.engine.begin() as conn:
            _ensure_runtime_table(conn)
            row = conn.execute(text(
                "SELECT (SELECT v FROM public.demo_runtime WHERE k = 'dirty'), "
                "(SELECT v::timestamptz < now() - (:m || ' minutes')::interval "
                " FROM public.demo_runtime WHERE k = 'last_activity')"
            ), {"m": str(int(inactivity_minutes))}).first()
        dirty = bool(row and row[0] == "1")
        idle = bool(row and row[1] is True)
        if not (dirty and idle):
            return False
    except Exception:
        logger.error("[demo_reset] inactivity_sweep kontrol hata", exc_info=True)
        return False

    ok = safe_restore_baseline()
    try:
        with db.engine.begin() as conn:
            conn.execute(text("UPDATE public.demo_runtime SET v = '0' WHERE k = 'dirty'"))
        logger.info("[demo_reset] inaktivite sıfırlaması yapıldı (eşik=%d dk)", inactivity_minutes)
    except Exception:
        logger.error("[demo_reset] dirty bayrak temizleme hata", exc_info=True)
    return ok
