# -*- coding: utf-8 -*-
from __init__ import create_app
from extensions import db
from sqlalchemy import text


def main():
    app = create_app()
    with app.app_context():
        with db.engine.connect() as conn:
            table_info = conn.execute(text("PRAGMA table_info('ana_strateji')")).fetchall()
            existing_columns = {row[1] for row in table_info}

            if 'perspective' not in existing_columns:
                conn.execute(text("ALTER TABLE ana_strateji ADD COLUMN perspective VARCHAR(20)"))
            if 'bsc_code' not in existing_columns:
                conn.execute(text("ALTER TABLE ana_strateji ADD COLUMN bsc_code VARCHAR(10)"))
            conn.commit()

        with db.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS strategy_map_link (
                    id INTEGER PRIMARY KEY,
                    source_id INTEGER NOT NULL,
                    target_id INTEGER NOT NULL,
                    connection_type VARCHAR(30) NOT NULL DEFAULT 'CAUSE_EFFECT',
                    UNIQUE(source_id, target_id),
                    FOREIGN KEY(source_id) REFERENCES ana_strateji(id),
                    FOREIGN KEY(target_id) REFERENCES ana_strateji(id)
                )
            """))
            conn.commit()

    print("BSC schema ok")


if __name__ == "__main__":
    main()
