"""Pagination utility testleri."""
import pytest

from app.utils.pagination import paginate_query


class _Item:
    def __init__(self, id_, name):
        self.id = id_
        self.name = name

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class _FakeQuery:
    """SQLAlchemy Query'yi taklit eden minimal stub."""
    def __init__(self, items):
        self._items = items

    def count(self):
        return len(self._items)

    def limit(self, n):
        self._lim = n
        return self

    def offset(self, n):
        self._off = n
        return self

    def all(self):
        start = getattr(self, "_off", 0)
        end = start + getattr(self, "_lim", len(self._items))
        return self._items[start:end]


def test_paginate_default(app):
    items = [_Item(i, f"Item {i}") for i in range(1, 121)]
    q = _FakeQuery(items)
    with app.test_request_context("/?page=1&page_size=50"):
        result = paginate_query(q)
    assert result["total"] == 120
    assert len(result["data"]) == 50
    assert result["page"] == 1
    assert result["total_pages"] == 3
    assert result["has_next"] is True
    assert result["has_prev"] is False


def test_paginate_last_page(app):
    items = [_Item(i, f"Item {i}") for i in range(1, 121)]
    q = _FakeQuery(items)
    with app.test_request_context("/?page=3&page_size=50"):
        result = paginate_query(q)
    assert result["page"] == 3
    assert len(result["data"]) == 20
    assert result["has_next"] is False
    assert result["has_prev"] is True


def test_paginate_page_exceeds(app):
    items = [_Item(i, f"Item {i}") for i in range(1, 21)]
    q = _FakeQuery(items)
    with app.test_request_context("/?page=99&page_size=10"):
        result = paginate_query(q)
    # Otomatik son sayfaya düşmeli
    assert result["page"] == 2


def test_paginate_clamp_max_page_size(app):
    items = [_Item(i, "x") for i in range(50)]
    q = _FakeQuery(items)
    with app.test_request_context("/?page_size=10000"):
        result = paginate_query(q, max_page_size=100)
    assert result["page_size"] == 100


def test_paginate_empty(app):
    q = _FakeQuery([])
    with app.test_request_context("/"):
        result = paginate_query(q)
    assert result["total"] == 0
    assert result["total_pages"] == 0
    assert result["data"] == []


def test_paginate_invalid_params(app):
    items = [_Item(i, "x") for i in range(10)]
    q = _FakeQuery(items)
    with app.test_request_context("/?page=abc&page_size=xyz"):
        result = paginate_query(q, default_page_size=5)
    assert result["page"] == 1
    assert result["page_size"] == 5
