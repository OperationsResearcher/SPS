#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""instance/kokpitim.db: tum tablolar icin kayit sayisi (yalnizca count > 0)."""

import os
import sqlite3

ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT, "instance", "kokpitim.db")


def main():
    if not os.path.isfile(DB_PATH):
        print("DB not found:", DB_PATH)
        raise SystemExit(1)
    conn = sqlite3.connect(DB_PATH)
    try:
        tables = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            ).fetchall()
        ]
        rows_out = []
        for name in tables:
            try:
                qid = '"' + name.replace('"', '""') + '"'
                n = conn.execute("SELECT COUNT(*) FROM " + qid).fetchone()[0]
            except sqlite3.Error as exc:
                print("[WARN]", name, exc)
                continue
            if n > 0:
                rows_out.append((name, int(n)))
        print("Dosya:", DB_PATH, "\n")
        print("{:<50} {:>10}".format("Tablo", "Kayit"))
        print("-" * 62)
        total = 0
        for name, n in rows_out:
            print("{:<50} {:>10,}".format(name, n))
            total += n
        print("-" * 62)
        print("{:<50} {:>10,}".format("TOPLAM (gosterilen)", total))
        print("\nBos veya atlanan tablo sayisi:", len(tables) - len(rows_out))
    finally:
        conn.close()


if __name__ == "__main__":
    main()