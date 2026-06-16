#!/usr/bin/env python
"""Flask context'inde db tabloları oluştur"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from __init__ import create_app, db

app = create_app()
with app.app_context():
    db.create_all()
    print("DB tabloları oluşturuldu!")
