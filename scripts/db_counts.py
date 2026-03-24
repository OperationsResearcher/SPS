# -*- coding: utf-8 -*-
"""PostgreSQL veritabani tablo sayilari."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("SQLALCHEMY_DATABASE_URI",
    "postgresql://kokpitim_user:kokpitim_dev_123@localhost/kokpitim_db")

from app import create_app
from app.models import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    tables = [
        ("tenants", "Kurum"),
        ("users", "Kullanıcı"),
        ("processes", "Süreç"),
        ("process_kpis", "PG (Performans Göstergesi)"),
        ("kpi_data", "PGV (Performans Hedef Değeri / Veri)"),
        ("strategies", "Strateji"),
        ("sub_strategies", "Alt Strateji"),
        ("process_activities", "Süreç Faaliyeti"),
        ("individual_performance_indicators", "Bireysel PG"),
    ]
    print("PostgreSQL Veritabani - Tablo Sayilari")
    print("=" * 50)
    for tbl, label in tables:
        try:
            r = db.session.execute(text(f'SELECT COUNT(*) FROM "{tbl}"')).scalar()
            print(f"  {label:35} ({tbl}): {r}")
        except Exception:
            print(f"  {label:35} ({tbl}): -")
    print("=" * 50)
