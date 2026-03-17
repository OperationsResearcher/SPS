# -*- coding: utf-8 -*-
"""Kullanıcıları SQLite'a aktar (V5 - Direct SQL Injection)"""

import sys
import os
import json
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(__file__))

from __init__ import create_app
from extensions import db

basedir = os.path.abspath(os.path.dirname(__file__))
SQLITE_DB_PATH = os.path.join(basedir, 'spsv2.db')
DUMP_FILE = os.path.join(basedir, 'data_dump.json')

app = create_app()
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{SQLITE_DB_PATH}'

def direct_sql_insert(table_name, data_list):
    """Veriyi ORM kullanmadan, doğrudan SQL ile basar."""
    if not data_list:
        print(f"UYARI: {table_name} için veri yok.")
        return

    print(f"\n{table_name} aktarılıyor ({len(data_list)} kayıt)...")
    
    # İlk kayıttan sütun isimlerini al
    columns = list(data_list[0].keys())
    
    # Sütun isimlerini ve değer placeholder'larını hazırla (?, ?, ?)
    cols_str = ', '.join([f'"{c}"' for c in columns]) # "id", "username" ...
    vals_str = ', '.join([':' + c for c in columns]) # :id, :username ...
    
    sql = text(f'INSERT INTO "{table_name}" ({cols_str}) VALUES ({vals_str})')
    
    success_count = 0
    with db.engine.connect() as conn:
        trans = conn.begin()
        try:
            for row in data_list:
                # Boolean değerleri SQLite için 1/0 veya 'true'/'false' yap
                clean_row = {}
                for k, v in row.items():
                    if isinstance(v, bool):
                        clean_row[k] = 1 if v else 0
                    elif v is None:
                         clean_row[k] = None
                    else:
                        clean_row[k] = v
                
                try:
                    conn.execute(sql, clean_row)
                    success_count += 1
                except Exception as e:
                    # Duplicate key hatası ise yoksay, değilse bas
                    if "UNIQUE constraint failed" in str(e):
                        print(f"  - Kayıt zaten var (ID: {row.get('id')})")
                    else:
                        print(f"  X Hata ({table_name}): {str(e)[:100]}")
            
            trans.commit()
            print(f"[OK] {success_count} {table_name} başarıyla işlendi.")
            
        except Exception as e:
            trans.rollback()
            print(f"[!!!] Toplu İşlem Hatası: {e}")

def find_data_in_json(json_data, target_keys):
    # 1. Tables içinde ara
    if 'tables' in json_data:
        for k in target_keys:
            if k in json_data['tables']: return json_data['tables'][k]
            for ak in json_data['tables']:
                if ak.lower() == k.lower(): return json_data['tables'][ak]
    
    # 2. Root içinde ara
    for k in target_keys:
        if k in json_data: return json_data[k]
        for ak in json_data:
            if ak.lower() == k.lower(): return json_data[ak]
            
    return None

with app.app_context():
    # Tabloları oluştur
    db.create_all()
    
    if not os.path.exists(DUMP_FILE):
        print(f"HATA: {DUMP_FILE} bulunamadı!")
        sys.exit(1)

    with open(DUMP_FILE, 'r', encoding='utf-8') as f:
        export_data = json.load(f)

    # Kurum Ara ve Yükle
    # Tablo adı veritabanında genellikle küçüktür (kurum, user)
    kurum_data = find_data_in_json(export_data, ['Kurum', 'institutions', 'Institution'])
    if kurum_data:
        direct_sql_insert("kurum", kurum_data) # Tablo adı: 'kurum'
    else:
        print("UYARI: Kurum verisi bulunamadı.")

    # User Ara ve Yükle
    user_data = find_data_in_json(export_data, ['User', 'users', 'user'])
    if user_data:
        direct_sql_insert("user", user_data) # Tablo adı: 'user'
    else:
        print("UYARI: User verisi bulunamadı.")

    # Sonucu Kontrol Et
    # Basit bir SELECT sorgusu ile say
    with db.engine.connect() as conn:
        try:
            u_count = conn.execute(text("SELECT COUNT(*) FROM user")).scalar()
            k_count = conn.execute(text("SELECT COUNT(*) FROM kurum")).scalar()
            print(f"\nSON DURUM: {u_count} Kullanıcı, {k_count} Kurum.")
        except:
            print("\nTablolar okunamadı (Henüz oluşmamış olabilir).")