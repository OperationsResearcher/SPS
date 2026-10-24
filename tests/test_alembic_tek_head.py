# -*- coding: utf-8 -*-
"""Alembic grafiği TEK head olmalı: aksi halde `alembic upgrade head` deploy'da "Multiple head revisions" ile durur.

Paralel dallarda iki migration aynı atadan ayrılırsa `alembic merge` ile birleştir (örn. mg01a2b3c4d5).
Ayrıca deploy (git archive) için migration dosyalarının hepsi commitli olmalı (KeyError: <revision> tuzağı).
"""
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

KOK = Path(__file__).resolve().parent.parent


def _sd():
    c = Config()
    c.set_main_option("script_location", str(KOK / "migrations"))
    return ScriptDirectory.from_config(c)


def test_tek_head():
    heads = _sd().get_heads()
    assert len(heads) == 1, f"Birden çok alembic head: {heads} → `alembic merge` ile birleştir"


def test_tum_revizyonlar_zincire_bagli():
    sd = _sd()
    # walk_revisions tüm bağlı revizyonları gezer; dosya sayısı ile eşit olmalı (yetim migration yok)
    zincir = {r.revision for r in sd.walk_revisions()}
    dosyalar = len([p for p in (KOK / "migrations" / "versions").glob("*.py") if p.name != "__init__.py"])
    assert len(zincir) == dosyalar, f"zincirde {len(zincir)} revizyon, dosya {dosyalar}"
