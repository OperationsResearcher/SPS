# -*- coding: utf-8 -*-
import sqlite3
import os

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(base, "instance", "kokpitim.db")
conn = sqlite3.connect(path)
cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
all_tables = [r[0] for r in cur.fetchall()]
target = ['tenants','users','processes','process_kpis','kpi_data','process_activities','project','task','strategies','sub_strategies']
for t in target:
    if t in all_tables:
        n = conn.execute("SELECT COUNT(*) FROM "+t).fetchone()[0]
        print(f"{t}: {n}")
    else:
        print(f"{t}: (yok)")
conn.close()
