
# -*- coding: utf-8 -*-
from app import app
from extensions import db
from models.audit import AuditLog

def create_table():
    with app.app_context():
        print("Creating audit_log table...")
        try:
            db.create_all()
            print("Done. Tables created (if they didn't exist).")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    create_table()
