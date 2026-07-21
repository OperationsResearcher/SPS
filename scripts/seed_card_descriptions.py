# -*- coding: utf-8 -*-
"""Kart açıklamalarını (system_cards.description) zenginleştirilmiş metinlerle günceller.

Neden ayrı seed script: kod deploy'u DB'ye dokunmaz (memory: seed script deploy
açığı). Açıklamalar veri olduğu için her ortamda ayrıca koşturulmalı.

İçerik kaynağı: scripts/seed_data/card_descriptions_*.py — kart `code` -> metin.
Metinler DÜZ METİN tutulur (i18n/.po uyumu). Modal onları yapılandırılmış basar
(bkz. base.html::renderInfoBody): "Başlık:" satırı bölüm olur, boş satır paragraf
ayırır, "- " madde olur.

Kullanım:
    python scripts/seed_card_descriptions.py                 # KONTROL (hiçbir şey yazmaz)
    python scripts/seed_card_descriptions.py --calistir      # uygula
    python scripts/seed_card_descriptions.py --calistir --sadece k_radar   # önek filtresi

Güvenlik:
  - Yalnızca `description` alanına yazar; başka sütuna dokunmaz.
  - DB'de olmayan `code` için kart OLUŞTURMAZ — atlar ve raporlar (kart keşfi
    Admin > Kart Yönetimi'nin işi).
  - Mevcut açıklama zaten hedefle aynıysa yazmaz (gürültüsüz idempotency).
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _load_descriptions() -> dict[str, str]:
    """seed_data/card_descriptions_*.py dosyalarındaki DESCRIPTIONS sözlüklerini birleştirir."""
    import importlib.util

    merged: dict[str, str] = {}
    seed_dir = ROOT / "scripts" / "seed_data"
    if not seed_dir.exists():
        return merged
    for path in sorted(seed_dir.glob("card_descriptions_*.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            continue
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        data = getattr(mod, "DESCRIPTIONS", None)
        if isinstance(data, dict):
            overlap = merged.keys() & data.keys()
            if overlap:
                print(f"  [uyari] {path.name}: {len(overlap)} kod baska dosyada da var, sonuncu kazanir")
            merged.update(data)
    return merged


def main() -> int:
    ap = argparse.ArgumentParser(description="Kart aciklamalarini gunceller.")
    ap.add_argument("--calistir", action="store_true", help="Gercekten yaz (varsayilan: kontrol).")
    ap.add_argument("--sadece", default="", help="Yalniz bu onekle baslayan kart kodlari (or. k_radar).")
    args = ap.parse_args()

    from app import create_app
    from extensions import db
    from sqlalchemy import text

    desired = _load_descriptions()
    if args.sadece:
        desired = {k: v for k, v in desired.items() if k.startswith(args.sadece)}
    if not desired:
        print("Uygulanacak aciklama bulunamadi (scripts/seed_data/card_descriptions_*.py bos mu?).")
        return 1

    app = create_app()
    with app.app_context():
        rows = db.session.execute(
            text("SELECT code, coalesce(description,'') FROM system_cards")
        ).fetchall()
        current = {r[0]: r[1] for r in rows}

        yeni, degisen, ayni, eksik = [], [], [], []
        for code, new_desc in desired.items():
            new_desc = new_desc.strip()
            if code not in current:
                eksik.append(code)
            elif not current[code].strip():
                yeni.append(code)
            elif current[code].strip() == new_desc:
                ayni.append(code)
            else:
                degisen.append(code)

        print("=" * 62)
        print(f"  Kart aciklama guncellemesi {'(UYGULA)' if args.calistir else '(KONTROL)'}")
        print("=" * 62)
        print(f"  Hedef metin sayisi : {len(desired)}")
        print(f"  Bos -> dolacak     : {len(yeni)}")
        print(f"  Degisecek          : {len(degisen)}")
        print(f"  Zaten ayni         : {len(ayni)}")
        print(f"  DB'de kart YOK     : {len(eksik)}")
        if eksik:
            print("    (kart kesfi gerekiyor — Admin > Kart Yonetimi)")
            for c in eksik[:10]:
                print(f"      - {c}")
            if len(eksik) > 10:
                print(f"      ... +{len(eksik) - 10} tane daha")

        if not args.calistir:
            print()
            print("  KONTROL modu — hicbir sey yazilmadi. Uygulamak icin: --calistir")
            return 0

        yazilacak = yeni + degisen
        if not yazilacak:
            print("\n  Degisiklik yok — DB zaten guncel.")
            return 0

        for code in yazilacak:
            db.session.execute(
                text("UPDATE system_cards SET description = :d WHERE code = :c"),
                {"d": desired[code].strip(), "c": code},
            )
        db.session.commit()
        # Not: Windows konsolu cp1254 — Unicode simge (✓) UnicodeEncodeError verir.
        print(f"\n  [TAMAM] {len(yazilacak)} kart aciklamasi guncellendi.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
