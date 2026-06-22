# -*- coding: utf-8 -*-
"""Tek-seferlik: /reports altındaki Türkçe iç segmentleri İngilizceye çevir (TASK-204).

KÖK /reports zaten İngilizce (TASK-203). Bu script yalnızca İÇ Türkçe segmentleri çevirir.
Eşleşme: '/reports/<seg>' veya '/reports/api/<seg>' veya '/reports/<x>/<seg>' bağlamında,
segment SONRASI '/' '"' "'" '`' boşluk ')' veya satır sonu olmalı (tam-segment garantisi).

HARİÇ: docs/, htmlcov/, ARCHIVE/, scripts/_arsiv/, .git/, instance/, node_modules + köprü dosyaları.
Fonksiyon adları (raporlar_muda_analizi vb.) DEĞİŞMEZ — yalnızca route string'leri ve frontend URL'leri.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

EXCLUDE_DIRS = {".git", "docs", "htmlcov", "ARCHIVE", "instance", "node_modules", "__pycache__"}
EXCLUDE_PATH_PARTS = (os.path.join("scripts", "_arsiv"),)
EXCLUDE_FILES = {
    os.path.join("app", "legacy_redirect_config.py"),
    os.path.join("app", "middleware", "legacy_sunset.py"),
}
INCLUDE_EXT = {".py", ".html", ".js"}

# Türkçe segment -> İngilizce. Uzun anahtarlar önce gelmeli (bireysel-karne-batch, bireysel-hizalama).
SEG_MAP = {
    "muda-analizi": "muda-analysis",
    "strateji-hikayesi": "strategy-story",
    "stratejik-yillik": "strategic-annual",
    "bireysel-karne-batch": "individual-scorecard-batch",
    "bireysel-hizalama": "individual-alignment",
    "operasyon-istatistik": "operation-statistics",
    "hizalama-sankey": "alignment-sankey",
    "departman-performans": "department-performance",
    "yonetici-liderlik": "executive-leadership",
    "sabah-ozeti": "morning-summary",
    "evrim-filmi": "evolution-film",
    "ai-sunum": "ai-presentation",
    "ai-danisman": "ai-advisor",
    "yatirimci-sunum": "investor-presentation",
    "esg-rapor": "esg-report",
    "esg-yonetim": "esg-management",
    "audit-paketi": "audit-package",
    "veri-kalitesi": "data-quality",
    "k-vektor-carpiklik": "k-vector-skewness",
    "hedef-revizyon": "target-revision",
    "onay-zinciri": "approval-chain",
    "pg-proje-etki": "pg-project-impact",
    "sektorel": "sectoral",
    "iki-fa": "two-fa",
}

# Uzun-anahtar-önce sıralama (çakışma önleme)
_keys = sorted(SEG_MAP.keys(), key=len, reverse=True)
# /reports/ ... <seg> (segment sonrası sınır). Önce kök /reports/ veya /reports/api/ ya da
# /reports/<x>/ olabilir; biz sadece '<seg>' kelimesini /reports bağlamında yakalarız.
_alt = "|".join(re.escape(k) for k in _keys)
PATTERN = re.compile(r"(?P<pre>/reports/(?:api/|[a-z0-9-]+/)?)(?P<seg>" + _alt + r")(?=[/\"'`\s)]|$)")

def _sub(m):
    return m.group("pre") + SEG_MAP[m.group("seg")]

DRY = "--apply" not in sys.argv
changed = []
total = 0

for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
    if any(part in dirpath for part in EXCLUDE_PATH_PARTS):
        continue
    for fn in filenames:
        if os.path.splitext(fn)[1].lower() not in INCLUDE_EXT:
            continue
        fp = os.path.join(dirpath, fn)
        rel = os.path.relpath(fp, ROOT)
        if rel in EXCLUDE_FILES:
            continue
        try:
            with open(fp, encoding="utf-8") as f:
                content = f.read()
        except (UnicodeDecodeError, OSError):
            continue
        hits = len(PATTERN.findall(content))
        if not hits:
            continue
        total += hits
        changed.append((rel, hits))
        if not DRY:
            with open(fp, "w", encoding="utf-8") as f:
                f.write(PATTERN.sub(_sub, content))

mode = "DRY-RUN" if DRY else "APPLIED"
print(f"[{mode}] {total} hit, {len(changed)} dosya")
for rel, hits in sorted(changed, key=lambda x: -x[1]):
    print(f"  {hits:3d}  {rel}")

# Köprü kuralları (PREFIX_REWRITE'a elle eklenecek) — kopyala/yapıştır çıktısı
if DRY:
    print("\n# legacy_redirect_config.py PREFIX_REWRITE için (uzun-önce):")
    for k in _keys:
        print(f'    ("/raporlar/{k}", "/reports/{SEG_MAP[k]}"),  # eski TR kök zaten /reports\'a köprülü; bu iç segment')
