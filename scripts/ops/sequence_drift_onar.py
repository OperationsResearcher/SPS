"""Sequence drift taraması ve onarımı (S5).

SORUN: Bir sequence'in `last_value=1, is_called=false` durumunda kalması,
`nextval`in 1 DÖNDÜRMESİ (artırmaması) demektir. O tabloda id=1 zaten doluysa
bir sonraki INSERT `duplicate key value violates unique constraint` ile patlar.
Sömürü değil, operasyonel kaza — ve tam olarak yeni kayıt eklendiği an çıkar.

KAYNAK: Yayın→Yerel veri çekiminde `setval` adımının atlanması
(CLAUDE.md'de "sequence drift" zaten bilinen tuzak olarak kayıtlı).

ÖLÇÜM 2026-07-21 (yerel): 155 sequence'in 6'sı çakışacak durumdaydı —
route_registry(max 81), system_components(35), process_activity_reminders(17),
roles(5), user_tour_progress(4), activity_tracks(1). Hepsi onarıldı.

LİSTE TUTULMAZ (KURALLAR-MASTER §8.6 ile aynı gerekçe): tablo adları ne bu
dosyada ne de db_sequence.py'de yazılı. pg_depend üzerinden her sequence kendi
tablosuna bağlanır → yeni tablo eklendiğinde otomatik kapsanır, bakım gerekmez.

Kullanım:
    python scripts/ops/sequence_drift_onar.py              # KONTROL (yazma yok)
    python scripts/ops/sequence_drift_onar.py --calistir   # onar

Çıkış kodu: 0 = drift yok / onarıldı, 1 = drift var (kontrol modunda).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app import create_app  # noqa: E402
from app.utils.db_sequence import (  # noqa: E402
    repair_sequence_drift,
    scan_sequence_drift,
)


def main() -> int:
    uygula = "--calistir" in sys.argv
    app = create_app()
    with app.app_context():
        sonuc = repair_sequence_drift(dry_run=not uygula)
        bulunan = sonuc["bulunan"]

        print("=" * 62)
        print("SEQUENCE DRIFT " + ("ONARIMI" if uygula else "KONTROLÜ (yazma yok)"))
        print("=" * 62)

        if not bulunan:
            print("\n✅ Çakışacak sequence yok.")
            return 0

        print(f"\nÇakışacak sequence: {len(bulunan)}\n")
        for b in bulunan:
            print(
                f"  {b['table']:<34} sonraki_id={b['next_id']:<7} "
                f"mevcut_max={b['max_id']}"
            )

        if not uygula:
            print("\n⚠ Bu tablolara bir sonraki kayıt eklendiğinde PK çakışması olur.")
            print("  Onarmak için: python scripts/ops/sequence_drift_onar.py --calistir")
            return 1

        print(f"\nOnarılan: {len(sonuc['onarilan'])}")
        kalan = scan_sequence_drift()
        if kalan:
            print(f"\n❌ Onarım sonrası hâlâ {len(kalan)} sequence sorunlu:")
            for b in kalan:
                print(f"  {b['table']} → {b}")
            return 1
        print("✅ Onarım sonrası kalan drift: 0")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
