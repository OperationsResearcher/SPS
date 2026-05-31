# -*- coding: utf-8 -*-
"""
Geriye dönük uyumluluk: scriptler `from __init__ import create_app` kullanabilir.

Canlı uygulama girişi: `app.py` / `run.py` → `from app import create_app`
Eski kök fabrika: dal `19mayisyedek` commit 0192ee5 (geri dönüş için bkz. docs/19MAYISYEDEK_RESTORE.md)
"""
from app import create_app
from extensions import db, migrate, login_manager, csrf, limiter, talisman, cache

__all__ = [
    "create_app",
    "db",
    "migrate",
    "login_manager",
    "csrf",
    "limiter",
    "talisman",
    "cache",
]
