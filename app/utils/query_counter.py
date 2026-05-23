"""SQL query count counter — N+1 regression koruması.

Audit (PROJE-AUDIT-2026Q2.md) bulgu: Process.leaders/members/owners + ProcessMaturity
+ k_rapor genelinde N+1 yaygın. 100 kayıt = 300+ sorgu.

Kullanım:
    from app.utils.query_counter import count_queries

    with count_queries() as counter:
        results = Process.query.all()
        for p in results:
            _ = p.leaders  # lazy load

    assert counter.count < 10, f"N+1 risk: {counter.count} sorgu"
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import event


class QueryCounter:
    def __init__(self):
        self.count = 0
        self.queries: list[str] = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


@contextmanager
def count_queries(engine=None, record_sql: bool = False) -> Iterator[QueryCounter]:
    """Bir bağlam içinde çalıştırılan SQL sorgularını sayar.

    Args:
        engine: SQLAlchemy engine. None ise db.engine kullanılır.
        record_sql: True ise her sorgunun text'i de tutulur (debug için, yavaş).
    """
    if engine is None:
        from extensions import db
        engine = db.engine

    counter = QueryCounter()

    def _on_execute(conn, cursor, statement, parameters, context, executemany):
        counter.count += 1
        if record_sql:
            counter.queries.append(statement[:200])

    event.listen(engine, "before_cursor_execute", _on_execute)
    try:
        yield counter
    finally:
        event.remove(engine, "before_cursor_execute", _on_execute)


def assert_max_queries(max_count: int, counter: QueryCounter):
    """N+1 regression assertion helper."""
    if counter.count > max_count:
        msg = f"N+1 regresyon: beklenen ≤{max_count} sorgu, gerçek {counter.count}"
        if counter.queries:
            msg += "\nSon 5 sorgu:\n" + "\n".join(f"  - {q[:120]}" for q in counter.queries[-5:])
        raise AssertionError(msg)
