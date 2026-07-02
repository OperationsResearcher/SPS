# -*- coding: utf-8 -*-
"""system_cards.description DB alanındaki Türkçe açıklamaları messages.pot'a ekler.

Bu metinler kaynak dosyada (template/JS) yer almaz — runtime'da DB'den okunup
flask_babel.gettext ile çevrilir (bkz. micro/modules/admin/routes.py::admin_api_card_info).
Babel'in extract/update adımı yalnızca dosya taraması yaptığı için bu msgid'leri
göremez; .pot'ta yoksa `pybabel update` onları "obsolete" (#~) işaretler ve (i)
modalı çevirisi devre dışı kalır.

Bu script, i18n_extract.sh içinde `pybabel update`'ten ÖNCE çalıştırılmalı —
tıpkı extract_inline_t.py gibi .pot'a eksik msgid'leri ekler (mevcut .pot korunur).

Kullanım: .venv/Scripts/python.exe scripts/_arsiv/fix_oneshot/extract_db_card_descriptions.py
"""
import os
import sys

ROOT = r"c:\kokpitim"
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from app import create_app
from extensions import db

app = create_app()
with app.app_context():
    rows = db.session.execute(db.text(
        "SELECT DISTINCT description FROM system_cards "
        "WHERE description IS NOT NULL AND description != ''"
    )).fetchall()
    descriptions = [r[0] for r in rows]

from babel.messages.pofile import read_po, write_po

pot_path = "messages.pot"
with open(pot_path, encoding="utf-8") as fh:
    pot = read_po(fh)

added = 0
for msgid in descriptions:
    if pot.get(msgid) is None:
        pot.add(msgid, locations=[("system_cards.description (DB)", 0)], flags=())
        added += 1

with open(pot_path, "wb") as fh:
    write_po(fh, pot, width=76, omit_header=False, sort_output=False)

print("system_cards.description benzersiz: %d | messages.pot eklenen: %d" % (len(descriptions), added))
