# -*- coding: utf-8 -*-
"""Yerel PostgreSQL: kokpitim_user ve kokpitim_db olusturur."""
import sys

def main():
    try:
        import psycopg2
    except ImportError:
        print("HATA: psycopg2 yok. pip install psycopg2-binary")
        sys.exit(1)

    import os
    pg_pass = os.environ.get("POSTGRES_PASSWORD", "")

    try:
        c = psycopg2.connect(
            host="localhost", port=5432, database="postgres",
            user="postgres", password=pg_pass or None
        )
        c.autocommit = True
        cur = c.cursor()
        try:
            cur.execute("CREATE USER kokpitim_user WITH PASSWORD 'kokpitim_dev_123';")
            print("kokpitim_user olusturuldu.")
        except psycopg2.errors.DuplicateObject:
            print("kokpitim_user zaten var.")
        try:
            cur.execute("CREATE DATABASE kokpitim_db OWNER kokpitim_user;")
            print("kokpitim_db olusturuldu.")
        except psycopg2.errors.DuplicateDatabase:
            print("kokpitim_db zaten var.")
        cur.execute("GRANT ALL PRIVILEGES ON DATABASE kokpitim_db TO kokpitim_user;")
        c2 = psycopg2.connect(
            host="localhost", port=5432, database="kokpitim_db",
            user="postgres", password=pg_pass
        )
        c2.autocommit = True
        cur2 = c2.cursor()
        cur2.execute("GRANT ALL ON SCHEMA public TO kokpitim_user;")
        cur2.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO kokpitim_user;")
        print("Yetkiler verildi.")
        c2.close()
        c.close()
    except psycopg2.OperationalError as e:
        print("Baglanti hatasi:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
