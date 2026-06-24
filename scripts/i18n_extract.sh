#!/usr/bin/env bash
# i18n mesaj çıkarma — Jinja `_()` + JS `t()` keyword'leri dahil.
# Kullanım: bash scripts/i18n_extract.sh
# JS tarafı t() helper kullanır (base.html), bu yüzden -k t ZORUNLU.
set -e
cd "$(dirname "$0")/.."
PY=".venv/Scripts/python.exe"
[ -x "$PY" ] || PY="python"

"$PY" -m babel.messages.frontend extract -F babel.cfg \
  -k t -k _ -k gettext -k ngettext \
  -o messages.pot .
# .html içindeki <script> bloklarındaki t() çağrıları babel [javascript] extractor'ı
# tarafından yakalanmaz (yalnız .js dosyaları). Bunları ayrıca topla:
"$PY" scripts/_arsiv/fix_oneshot/extract_inline_t.py
"$PY" -m babel.messages.frontend update -i messages.pot -d translations
echo "[i18n_extract] messages.pot güncellendi + kataloglar update edildi."
echo "Sıradaki: fill script + pybabel compile -d translations"
