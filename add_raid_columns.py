#!/usr/bin/env python
"""Add missing RAID columns to SQLite database"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'app.db')

# Eklenecek sütunlar
columns_to_add = [
    ('probability', 'INTEGER'),
    ('impact', 'INTEGER'),
    ('mitigation_plan', 'TEXT'),
    ('assumption_validation_date', 'DATE'),
    ('assumption_validated', 'BOOLEAN'),
    ('assumption_notes', 'TEXT'),
    ('issue_urgency', 'VARCHAR(50)'),
    ('issue_affected_work', 'TEXT'),
    ('dependency_type', 'VARCHAR(10)'),
    ('dependency_task_id', 'INTEGER'),
]

def add_columns():
    """Add missing columns to raid_item table"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Var olan sütunları kontrol et
        cursor.execute("PRAGMA table_info(raid_item)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        print(f"Mevcut sütunlar: {existing_columns}")
        
        # Eksik sütunları ekle
        for col_name, col_type in columns_to_add:
            if col_name not in existing_columns:
                sql = f"ALTER TABLE raid_item ADD COLUMN {col_name} {col_type}"
                try:
                    cursor.execute(sql)
                    conn.commit()
                    print(f"✅ Sütun eklendi: {col_name}")
                except Exception as e:
                    print(f"❌ Sütun eklenirken hata ({col_name}): {e}")
            else:
                print(f"⚠️  Sütun zaten var: {col_name}")
        
        conn.close()
        print("\n✅ Migration tamamlandı!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        print(f"❌ Veritabanı bulunamadı: {DB_PATH}")
        exit(1)
    
    add_columns()
