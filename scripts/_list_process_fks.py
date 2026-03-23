import sqlite3
from pathlib import Path

c = sqlite3.connect(Path(__file__).resolve().parents[1] / "instance" / "kokpitim.db")
for row in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    t = row[0]
    for fk in c.execute(f'PRAGMA foreign_key_list("{t}")'):
        ref_table, col_from, col_to = fk[2], fk[3], fk[4]
        if ref_table == "processes" and col_to == "id":
            print(t, "->", col_from)
