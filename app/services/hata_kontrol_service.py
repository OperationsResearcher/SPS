"""Hata Kontrolü — Keşif (Faz 2).

Test edilecek sayfaların listesini üretir. Bu adım STATİK: Flask route haritasından
güvenli (GET, parametresiz, kara-liste dışı) URL'leri çıkarır. Sayfa yüklemez.

BFS (bağlantı gezme) sonraki fazda tarayıcı motoruyla birlikte gelir.

Tasarım: docs/HATA-KONTROLU-TASARIM.md (K4 keşif, K5 parametreliler atlanır, kara liste).
"""
from __future__ import annotations

import re

from flask import current_app

# Asla taranmayacak yıkıcı / oturum-bozan / ikili-çıktı uçlar (kara liste).
_BLACKLIST = re.compile(
    r"(logout|/sil\b|/delete|/remove|/kaldir|/wipe|/reset|/purge|/truncate|"
    r"export|/indir|/download|\.pdf|\.xlsx|\.csv|excel|/sample|/template|attachment|/send|e-?posta|/email|"
    r"demo/end|/deploy|impersonate|switch[-_]tenant|/become|/hgs|"
    r"tenant-logo|profile-picture|/admin/araclar)",  # kendini tarama
    re.IGNORECASE,
)

# Modül etiketleri (URL önekine göre)
_MODULE_MAP = [
    ("/sp", "Stratejik Planlama"),
    ("/k-radar", "K-Analiz"),
    ("/k-analiz", "K-Analiz"),
    ("/k-rapor", "Raporlar"),
    ("/surec", "Süreç"),
    ("/process", "Süreç"),
    ("/bireysel", "Bireysel"),
    ("/kurum", "Kurum"),
    ("/proje", "Proje"),
    ("/project", "Proje"),
    ("/rapor", "Raporlar"),
    ("/admin", "Admin"),
    ("/api", "API"),
    ("/auth", "Hesap"),
    ("/profile", "Hesap"),
    ("/settings", "Hesap"),
    ("/ayarlar", "Ayarlar"),
    ("/bildirim", "Bildirim"),
    ("/desktop", "Masaüstü"),
    ("/analiz", "Analiz"),
]


def _module_of(rule: str) -> str:
    for prefix, label in _MODULE_MAP:
        if rule == prefix or rule.startswith(prefix + "/") or rule.startswith(prefix):
            return label
    seg = rule.strip("/").split("/", 1)[0]
    return seg or "Kök"


# Aktif platform blueprint'i — Hata Kontrolü canlı uygulamayı (micro UI) tarar.
_ACTIVE_BLUEPRINT = "app_bp"


def discover_routes(active_only: bool = True) -> dict:
    """Route haritasından test edilebilir sayfa URL'lerini çıkarır.

    active_only=True (varsayılan): yalnız aktif platform (app_bp) sayfaları — legacy/
    pazarlama/diğer blueprint'ler hariç (yanlış-alarm ve gürültüyü önler).

    Döner: {
      "urls": [{"url","module","endpoint"}...],   # taranacaklar (GET, parametresiz, güvenli)
      "by_module": {modul: adet}, "count": int,
      "skipped": {"param","blacklist","non_get","static","legacy"},
    }
    """
    app = current_app._get_current_object()
    urls = []
    seen = set()
    skipped = {"param": 0, "blacklist": 0, "non_get": 0, "static": 0, "legacy": 0}

    for rule in app.url_map.iter_rules():
        endpoint = rule.endpoint
        path = str(rule.rule)
        if endpoint == "static" or path.startswith("/static"):
            skipped["static"] += 1
            continue
        methods = rule.methods or set()
        if "GET" not in methods:
            skipped["non_get"] += 1
            continue
        if active_only and not endpoint.startswith(_ACTIVE_BLUEPRINT + "."):
            skipped["legacy"] += 1
            continue
        if "<" in path:  # parametreli — v1'de atla
            skipped["param"] += 1
            continue
        if _BLACKLIST.search(path):
            skipped["blacklist"] += 1
            continue
        if path in seen:
            continue
        seen.add(path)
        urls.append({"url": path, "module": _module_of(path), "endpoint": endpoint})

    urls.sort(key=lambda x: (x["module"], x["url"]))
    by_module: dict[str, int] = {}
    for u in urls:
        by_module[u["module"]] = by_module.get(u["module"], 0) + 1

    return {
        "urls": urls,
        "by_module": dict(sorted(by_module.items(), key=lambda kv: -kv[1])),
        "count": len(urls),
        "skipped": skipped,
    }
