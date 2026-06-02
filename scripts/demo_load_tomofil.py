# -*- coding: utf-8 -*-
"""Demo: yerel Tomofil baseline (.json.gz) dosyasını demo DB'ye yükler (KURALLAR §8.4).

YALNIZCA KOKPITIM_DEMO_MODE=1 ortamında çalışır — Test/Yayın'da tenant silip
yüklemeyi önlemek için guard'lı. Mevcut Tomofil tenant verisini temizler ve
dosyadaki veriyi (aynı tenant_id) yükler; global tablolar (rol, paket) korunur.

Kullanım (demo container içinde):
    python -m scripts.demo_load_tomofil backups/tomofil_baseline_local.json.gz

Tipik sıra:
    1. (yerel) Tomofil export → tomofil_baseline_local.json.gz
    2. dosyayı demo'ya kopyala
    3. python -m scripts.demo_load_tomofil <dosya>       ← Tomofil yüklenir
    4. python -m scripts.demo_baseline snapshot           ← başlangıç noktası kaydedilir
"""
import gzip
import json
import sys


def main(argv):
    if len(argv) < 2:
        print("Kullanım: python -m scripts.demo_load_tomofil <dosya.json.gz>")
        return 1
    path = argv[1]

    from dotenv import load_dotenv
    load_dotenv()
    from app import create_app
    app = create_app()

    if not app.config.get("KOKPITIM_DEMO_MODE"):
        print("HATA: KOKPITIM_DEMO_MODE=1 değil. Bu script yalnızca demo ortamında çalışır.")
        return 2

    try:
        with open(path, "rb") as f:
            data = json.loads(gzip.decompress(f.read()).decode("utf-8"))
    except Exception as e:
        print(f"HATA: dosya okunamadı: {e}")
        return 1

    tid = (data.get("meta") or {}).get("tenant_id")
    print(f"→ Tomofil yükleniyor (tenant_id={tid}) — mevcut tenant verisi temizlenip değiştirilecek…")

    with app.app_context():
        from services import tenant_backup_service as tb
        from app.models import db
        result = tb.restore_tenant_data(data)
        db.session.commit()

    total = result.get("total_restored")
    if total is None:
        total = sum((result.get("restored") or {}).values())
    errors = result.get("errors") or []
    print(f"✓ yüklendi: {total} kayıt" + (f" | uyarılar: {errors[:3]}" if errors else ""))
    print("→ Sonraki adım: python -m scripts.demo_baseline snapshot")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
