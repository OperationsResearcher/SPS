#!/usr/bin/env python3
"""Legacy vs platform route envanteri — docs/LEGACY_ROUTE_INVENTORY.md üretir."""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "LEGACY_ROUTE_INVENTORY.md"

SCAN = [
    ("Legacy main", ROOT / "main", "main_bp"),
    ("Legacy api", ROOT / "api", "api_bp"),
    ("Legacy auth", ROOT / "auth", "auth_bp"),
    ("Legacy admin", ROOT / "main" / "admin.py", "admin_bp"),
    ("Legacy app/routes", ROOT / "app" / "routes", None),
    ("Platform micro", ROOT / "micro", "app_bp"),
]

ROUTE_RE = re.compile(
    r"@(?:\w+\.)?(?:route|get|post|put|patch|delete)\(\s*[\"']([^\"']+)[\"']",
    re.MULTILINE,
)


def count_routes(path: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    files = [path] if path.is_file() else sorted(path.rglob("*.py"))
    for f in files:
        if not f.is_file():
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        for m in ROUTE_RE.finditer(text):
            rows.append((str(f.relative_to(ROOT)).replace("\\", "/"), m.group(1)))
    return rows


def main() -> None:
    # Tarih damgası: "Tarih: otomatik" yazan eski hali dokümanın ne zaman
    # üretildiğini gizliyordu; envanter 16 Haziran'da donup yanlış yön
    # gösterdiği hâlde fark edilmedi (2026-07-15).
    today = date.today().isoformat()
    lines = [
        "# Legacy / Platform Route Envanteri",
        "",
        "> Otomatik üretim: `python scripts/dev/inventory_legacy_routes.py`",
        f"> Üretim tarihi: {today}",
        ">",
        "> ⚠️ Bu dosya ELLE düzenlenmez — sayılar bayatlarsa script'i yeniden çalıştır.",
        "> Çalışan uygulamadaki kanonik dağılım için `docs/SISTEM-HARITASI.md`'ye bak.",
        "",
        "| Katman | Dosya sayısı (py) | Route sayısı | Not |",
        "|--------|-------------------|--------------|-----|",
    ]
    total_legacy = 0
    total_platform = 0
    for label, path, bp in SCAN:
        if not path.exists():
            continue
        rows = count_routes(path)
        n_files = 1 if path.is_file() else len(list(path.rglob("*.py")))
        lines.append(f"| {label} | {n_files} | {len(rows)} | `{bp or 'çeşitli'}` |")
        if label.startswith("Platform"):
            total_platform += len(rows)
        else:
            total_legacy += len(rows)

    toplam = total_legacy + total_platform
    pay = (total_platform / toplam * 100) if toplam else 0
    yon = "modern baskın ✅" if total_platform > total_legacy else "⚠️ legacy baskın"
    lines.extend(
        [
            "",
            f"**Özet:** Legacy ~{total_legacy} route, Platform (micro) ~{total_platform} route "
            f"→ modern pay %{pay:.0f} ({yon}).",
            "",
            "Strangler yönü: `micro/` büyür, legacy erir. Bu oran her ölçümde modern lehine",
            "artmalı; azalıyorsa yeni iş yanlış katmana yazılıyor demektir.",
            "",
            "## Öncelik",
            "",
            "1. Yeni özellikler yalnızca `micro/modules/` + `ui/templates/platform/`.",
            "2. Legacy `main/` / `api/` yalnızca bakım; yeni endpoint eklenmez.",
            "3. `app/routes/process.py` 2026-07-15'te silindi (1806 satır ölü kod) —",
            "   süreç yüzeyi artık tek: `micro/modules/surec/`.",
            "",
        ]
    )

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} ({total_legacy}+{total_platform} routes)")


if __name__ == "__main__":
    main()
