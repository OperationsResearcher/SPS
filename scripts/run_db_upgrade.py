#!/usr/bin/env python3
"""Alembic upgrade — Flask CLI yerine (Docker'da FLASK_APP / app.run cakismasini onler).

Kullanim (container icinde, proje kokunden):
    python3 scripts/run_db_upgrade.py
"""
from __future__ import annotations

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(_ROOT)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from flask_migrate import upgrade
from run import app

with app.app_context():
    upgrade()
