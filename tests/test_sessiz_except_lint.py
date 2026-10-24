# -*- coding: utf-8 -*-
"""Sessiz `except ...: pass` yasağı (Faz S.7, A12 / KURALLAR §3): her except iz bırakmalı.

Mevcut ihlaller BASELINE'da dondurulur (yalnız küçülmeli). Yeni `pass` testi kırar.
"""
import ast
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
TARAMA = ("app", "micro", "services", "api")
ATLA = ("migrations", "_arsiv", "ARCHIVE", "__pycache__", "tests")

# Ekim core-denetim port çalışmasında (commitlenmemiş) gelen iki yer; port commitlenince düzeltilip çıkarılacak.
BASELINE = {
    "services/task_activity_service.py",
    "api/routes_files.py",
}


def _ihlal_dosyalari():
    bulunan = set()
    for d in TARAMA:
        for p in (KOK / d).rglob("*.py"):
            if any(a in p.parts for a in ATLA):
                continue
            try:
                tree = ast.parse(p.read_text("utf-8", "ignore"))
            except SyntaxError:
                continue
            for n in ast.walk(tree):
                if isinstance(n, ast.ExceptHandler) and len(n.body) == 1 and isinstance(n.body[0], ast.Pass):
                    bulunan.add(p.relative_to(KOK).as_posix())
    return bulunan


def test_yeni_sessiz_except_yok():
    yeni = _ihlal_dosyalari() - BASELINE
    assert not yeni, "sessiz `except: pass` (logger ekleyin): " + ", ".join(sorted(yeni))
