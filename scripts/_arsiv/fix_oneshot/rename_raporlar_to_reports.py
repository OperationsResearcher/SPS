# -*- coding: utf-8 -*-
"""Tek-seferlik: URL kök segmenti /raporlar -> /reports (tek-dil çalışması, TASK-203).

KAPSAM: yalnızca '/raporlar' literal'i '/reports'a çevrilir. İç Türkçe segmentler
(muda-analizi, strateji-hikayesi vb.) DOKUNULMAZ — ayrı turda.

HARİÇ: docs/, htmlcov/, ARCHIVE/, scripts/_arsiv/, .git/, instance/, node_modules.
Kelime sınırı: '/raporlar' sonrası '/' veya '"' veya "'" veya boşluk veya satır sonu olmalı
(yani /raporlar-x gibi yanlış eşleşme yok — zaten öyle bir şey yok ama garanti).
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

EXCLUDE_DIRS = {".git", "docs", "htmlcov", "ARCHIVE", "instance", "node_modules", "__pycache__"}
EXCLUDE_PATH_PARTS = (os.path.join("scripts", "_arsiv"),)
# Köprü dosyaları: kasıtlı olarak eski /raporlar literal'ini tutar — DOKUNMA.
EXCLUDE_FILES = {
    os.path.join("app", "legacy_redirect_config.py"),
    os.path.join("app", "middleware", "legacy_sunset.py"),
}
INCLUDE_EXT = {".py", ".html", ".js"}

# /raporlar'ı yalnızca URL bağlamında (sonrasında / " ' ` boşluk veya string sonu) çevir
PATTERN = re.compile(r"/raporlar(?=[/\"'`\s)]|$)")

DRY = "--apply" not in sys.argv

changed_files = []
total_hits = 0

for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
    if any(part in dirpath for part in EXCLUDE_PATH_PARTS):
        continue
    for fn in filenames:
        ext = os.path.splitext(fn)[1].lower()
        if ext not in INCLUDE_EXT:
            continue
        fp = os.path.join(dirpath, fn)
        if os.path.relpath(fp, ROOT) in EXCLUDE_FILES:
            continue
        try:
            with open(fp, encoding="utf-8") as f:
                content = f.read()
        except (UnicodeDecodeError, OSError):
            continue
        hits = len(PATTERN.findall(content))
        if not hits:
            continue
        total_hits += hits
        rel = os.path.relpath(fp, ROOT)
        changed_files.append((rel, hits))
        if not DRY:
            new = PATTERN.sub("/reports", content)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(new)

mode = "DRY-RUN" if DRY else "APPLIED"
print(f"[{mode}] {total_hits} hit, {len(changed_files)} dosya")
for rel, hits in sorted(changed_files, key=lambda x: -x[1]):
    print(f"  {hits:3d}  {rel}")
if DRY:
    print("\n--apply ile gerçek değişiklik yapılır.")
