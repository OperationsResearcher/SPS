# -*- coding: utf-8 -*-
"""Inline <script> bloklarındaki t("...") / t('...') çağrılarını toplayıp
messages.pot'a ekler. Babel'in [javascript] extractor'ı yalnızca .js dosyalarını
tarar; .html içindeki <script> blokları kapsanmaz (FAZ 4b boşluğu).

Çıktı: messages.pot'a eksik msgid'leri ekler (mevcut .pot'u korur).
Kullanım: .venv/Scripts/python.exe scripts/_arsiv/fix_oneshot/extract_inline_t.py
"""
import re, glob, os
os.chdir(os.path.join(os.path.dirname(__file__), '..', '..', '..')) if False else None
# proje köküne çık
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
# ROOT yanlış olabilir; c:\kokpitim sabit
ROOT = r'c:\kokpitim'
os.chdir(ROOT)

def _scan_body(body, base_off, txt, f):
    # t("...") / t('...') — template-literal ${t(...)} dahil (babel JS extractor bunu kaçırır)
    for m in re.finditer(r'\bt\(\s*(["\'])((?:\\.|(?!\1).)*?)\1', body):
        raw = m.group(2)
        if not raw.strip():
            continue
        s = raw.replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\').replace('\\n', '\n').replace('\\t', '\t')
        line = txt[:base_off + m.start()].count('\n') + 1
        ids.setdefault(s, (f.replace('\\', '/'), line))

ids = {}  # msgid -> (file, line)
# 1) .html içindeki <script> blokları
for f in glob.glob('ui/templates/**/*.html', recursive=True):
    txt = open(f, encoding='utf-8').read()
    for sm in re.finditer(r'<script[^>]*>(.*?)</script>', txt, re.S):
        _scan_body(sm.group(1), sm.start(1), txt, f)
# 2) harici .js dosyaları (babel ${t(...)} interpolation'ını kaçırır)
for f in glob.glob('ui/static/platform/js/**/*.js', recursive=True):
    txt = open(f, encoding='utf-8').read()
    _scan_body(txt, 0, txt, f)

from babel.messages.pofile import read_po, write_po
from babel.messages.catalog import Catalog

pot_path = 'messages.pot'
with open(pot_path, encoding='utf-8') as fh:
    pot = read_po(fh)

added = 0
for msgid, (f, line) in ids.items():
    if pot.get(msgid) is None:
        pot.add(msgid, locations=[(f, line)], flags=())
        added += 1

with open(pot_path, 'wb') as fh:
    write_po(fh, pot, width=76, omit_header=False, sort_output=False)

print('inline t() benzersiz: %d | messages.pot eklenen: %d' % (len(ids), added))
