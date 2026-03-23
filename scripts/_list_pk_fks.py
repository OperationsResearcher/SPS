import sqlite3
from pathlib import Path

c = sqlite3.connect(Path(__file__).resolve().parents[1] / "instance" / "kokpitim.db")
for row in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    t = row[0]
    for fk in c.execute(f'PRAGMA foreign_key_list("{t}")'):
        if fk[2] == "process_kpis" and fk[4] == "id":
            print(t, "->", fk[3])
