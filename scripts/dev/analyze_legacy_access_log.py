#!/usr/bin/env python3
"""
Nginx/Apache access log'dan legacy URL kullanımını çıkarır.

Örnek:
  python scripts/dev/analyze_legacy_access_log.py /var/log/nginx/access.log
  python scripts/dev/analyze_legacy_access_log.py access.log --top 50
"""
from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

# Platform canonical önekler — bunlar legacy sayılmaz
PLATFORM_PREFIXES = (
    "/launcher", "/masaustu", "/process", "/project", "/proje", "/sp", "/kurum",
    "/bireysel", "/admin/yonetim", "/k-radar", "/k_rapor", "/analiz", "/MfG_hgs",
    "/login", "/logout", "/health", "/m/", "/static", "/api/v1", "/micro/api",
)

LEGACY_HINTS = (
    "/dashboard", "/projeler", "/surec-paneli", "/surec-karnesi", "/kurum-paneli",
    "/performans-kartim", "/admin-panel", "/v2", "/v3", "/hgs", "/main.",
    "/stratejik-planlama", "/gorevlerim", "/redmine",
)

LOG_RE = re.compile(r'"(?:GET|POST|HEAD|PUT|DELETE|PATCH)\s+([^\s?]+)')


def is_legacy_path(path: str) -> bool:
    if not path.startswith("/"):
        return False
    if any(path.startswith(p) for p in PLATFORM_PREFIXES):
        return False
    if any(h in path for h in LEGACY_HINTS):
        return True
    if path == "/":
        return False
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Legacy URL trafik analizi")
    parser.add_argument("logfile", type=Path, help="access.log dosyası")
    parser.add_argument("--top", type=int, default=30)
    args = parser.parse_args()

    if not args.logfile.is_file():
        raise SystemExit(f"Dosya yok: {args.logfile}")

    counter: Counter[str] = Counter()
    for line in args.logfile.read_text(encoding="utf-8", errors="replace").splitlines():
        m = LOG_RE.search(line)
        if not m:
            continue
        path = m.group(1)
        if is_legacy_path(path):
            counter[path] += 1

    print(f"Legacy URL hits (top {args.top}):")
    for path, count in counter.most_common(args.top):
        print(f"  {count:6d}  {path}")
    if not counter:
        print("  (legacy hit bulunamadı veya log formatı eşleşmedi)")


if __name__ == "__main__":
    main()
