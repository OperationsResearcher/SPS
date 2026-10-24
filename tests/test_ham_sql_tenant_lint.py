# -*- coding: utf-8 -*-
"""Ham SQL'de tenant_id lint'i (Faz 0.9, G5).

tenant_id kolonu olan tabloya dokunan ham SQL (`text(...)` / `execute("...")`) ifadesinde `tenant_id`
geçmiyorsa izolasyon elle sağlanmamış demektir (merkezi guard ham SQL'i kapsamaz).
Mevcut ihlaller BASELINE'da dondurulmuştur; yeni ihlal testi kırar. Bir ihlali düzeltince
BASELINE'dan çıkarın (liste yalnız küçülmeli).
"""
import ast
import re
from pathlib import Path

from app import create_app
from app.models import db
from config import TestingConfig

KOK = Path(__file__).resolve().parent.parent
TARAMA = ("app", "micro", "api", "services")
ATLA = ("migrations", "_arsiv", "ARCHIVE", "tests", "__pycache__")
SQL_TABLO = re.compile(r"\b(?:FROM|JOIN|UPDATE|INTO)\s+([a-z_][a-z0-9_]*)", re.I)

# "dosya::satır_yaklaşık_değil, dosya::tablo" biçiminde dondurulmuş mevcut ihlaller.
BASELINE: set[str] = set()


def _tenant_tablolari():
    app = create_app(TestingConfig)
    with app.app_context():
        return {t.name for t in db.metadata.sorted_tables if "tenant_id" in t.c}


def _sql_metni(node):
    """Çağrı argümanından SQL metnini (f-string sabit parçaları dahil) çıkarır."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(v.value for v in node.values if isinstance(v, ast.Constant) and isinstance(v.value, str))
    return None


def _ihlaller():
    tablolar = _tenant_tablolari()
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
                if not (isinstance(n, ast.Call) and n.args):
                    continue
                f = n.func
                ad = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")
                if ad not in ("text", "execute"):
                    continue
                sql = _sql_metni(n.args[0])
                if not sql or "tenant_id" in sql.lower():
                    continue
                for t in SQL_TABLO.findall(sql):
                    if t.lower() in tablolar:
                        bulunan.add(f"{p.relative_to(KOK).as_posix()}::{t.lower()}")
    return bulunan


def test_ham_sql_tenant_id_yeni_ihlal_yok():
    yeni = _ihlaller() - BASELINE
    assert not yeni, "tenant_id'siz ham SQL (tenant tablosuna): " + ", ".join(sorted(yeni))
