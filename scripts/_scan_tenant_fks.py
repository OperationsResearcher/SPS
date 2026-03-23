import sqlite3
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "instance/kokpitim.db"
c = sqlite3.connect(path)
for row in c.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
):
    t = row[0]
    for fk in c.execute(f"PRAGMA foreign_key_list({t!r})"):
        if fk[2] == "tenants" and fk[4] == "id":
            print(f"{t}: {fk[3]} -> tenants.id  ON DELETE {fk[6]}")
