"""Skorsuz `kpi_data` satırlarını geriye dönük doldurur (K1).

SORUN: `KpiData.status_percentage` 8 yerde okunuyordu ama HİÇBİR YERDE
yazılmıyordu. Kod tarafı düzeltildi (app/services/kpi_data_score_service.py,
5 yazma noktasından çağrılıyor) — ama BUGÜNE KADAR girilmiş satırlar skorsuz
kalır. Bu script onları doldurur.

ÖLÇÜM 2026-07-21 (yerel):
    Kayseri Model Fabrika    334 / 334 skorsuz  (%100)
    Eskişehir Makine         289 / 289 skorsuz  (%100)
    Default Corp               2 /   2 skorsuz  (%100)
    Tomofil (seed verisi)      0 / 91.408       (%0)
    ─────────────────────────────────────────────────
    TOPLAM                   972 skorsuz satır

SEMANTİK — neden hepsi dolmayacak (İ4 kararıyla uyumlu):
    Hedefi ya da gerçekleşeni olmayan satır SKORSUZ KALIR. "Ölçülmedi" ile
    "başarısız" farklı şeylerdir; boş satıra 0 yazmak kurumu veri girmediği
    için cezalandırır ve skoru yorumlanamaz kılar. KMF örneğinde 385 satırın
    217'si skorlanabiliyor, 168'i gerçekten ölçülmemiş (hedef = '-').

GÜVENLİK: Yalnız `status_percentage IS NULL` olan satırlara dokunur. Zaten
skorlu satır (365.632 adet) ASLA yeniden hesaplanmaz — bu script mevcut veriyi
değiştirmez, yalnız boşluğu doldurur.

Kullanım:
    python scripts/ops/kpi_data_skor_doldur.py              # KONTROL (yazma yok)
    python scripts/ops/kpi_data_skor_doldur.py --calistir   # doldur
    python scripts/ops/kpi_data_skor_doldur.py --calistir --tenant 16
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import logging  # noqa: E402

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.services.kpi_data_score_service import hesapla_kpi_data_skoru  # noqa: E402

TOPLU_BOYUT = 500


class _SahtePG:
    """hesapla_kpi_data_skoru yalnız `direction`, `target_value` ve `id` okur.

    ORM nesnesi yüklemek 972 satır için gereksiz N+1 üretirdi; ham sorgudan
    gelen alanları taşıyan hafif bir kabuk yeterli.
    """

    __slots__ = ("direction", "target_value", "id")

    def __init__(self, direction, target_value, pg_id):
        self.direction = direction or "Increasing"
        self.target_value = target_value
        self.id = pg_id


def _skorsuz_satirlar(tenant_id: int | None):
    kosul = "AND p.tenant_id = :tid" if tenant_id else ""
    return db.session.execute(
        text(f"""
            SELECT kd.id, kd.target_value, kd.actual_value,
                   pk.id AS pg_id, pk.direction, pk.target_value AS pg_target,
                   p.tenant_id, t.name AS tenant_adi
            FROM kpi_data kd
            JOIN process_kpis pk ON pk.id = kd.process_kpi_id
            JOIN processes p ON p.id = pk.process_id
            JOIN tenants t ON t.id = p.tenant_id
            WHERE kd.status_percentage IS NULL {kosul}
            ORDER BY p.tenant_id, kd.id
        """),
        {"tid": tenant_id} if tenant_id else {},
    ).fetchall()


def main() -> int:
    uygula = "--calistir" in sys.argv
    tenant_id = None
    if "--tenant" in sys.argv:
        tenant_id = int(sys.argv[sys.argv.index("--tenant") + 1])

    app = create_app()
    with app.app_context():
        # Satır satır uyarı basmak 972 satırda log'u boğar; özet zaten aşağıda.
        logging.getLogger(
            "app.services.kpi_data_score_service"
        ).setLevel(logging.ERROR)

        rows = _skorsuz_satirlar(tenant_id)
        print("=" * 66)
        print("KPI VERİ SKOR DOLDURMA " + ("(UYGULANIYOR)" if uygula else "(KONTROL — yazma yok)"))
        print("=" * 66)
        print(f"\nSkorsuz satır: {len(rows)}\n")
        if not rows:
            print("✅ Doldurulacak satır yok.")
            return 0

        kurum_ozet: dict = {}
        guncellemeler: list[dict] = []

        for r in rows:
            pg = _SahtePG(r.direction, r.pg_target, r.pg_id)
            durum, yuzde = hesapla_kpi_data_skoru(pg, r.target_value, r.actual_value)
            oz = kurum_ozet.setdefault(
                (r.tenant_id, r.tenant_adi), {"toplam": 0, "skorlandi": 0, "olculmedi": 0}
            )
            oz["toplam"] += 1
            if yuzde is None:
                oz["olculmedi"] += 1
            else:
                oz["skorlandi"] += 1
                guncellemeler.append({"i": r.id, "s": durum, "y": yuzde})

        print(f"{'Kurum':<34} {'Toplam':>7} {'Skorlandı':>10} {'Ölçülmedi':>10}")
        print("-" * 66)
        for (tid, ad), oz in sorted(kurum_ozet.items()):
            print(f"  t{tid:<4} {(ad or '')[:26]:<26} {oz['toplam']:>7} "
                  f"{oz['skorlandi']:>10} {oz['olculmedi']:>10}")
        print("-" * 66)
        top_s = sum(o["skorlandi"] for o in kurum_ozet.values())
        top_o = sum(o["olculmedi"] for o in kurum_ozet.values())
        print(f"  {'TOPLAM':<32} {len(rows):>7} {top_s:>10} {top_o:>10}")

        print("\n'Ölçülmedi' = hedef veya gerçekleşen yok/sayısal değil.")
        print("Bunlara bilinçli olarak 0 YAZILMAZ — ölçülmemiş ≠ başarısız.")

        if not uygula:
            print(f"\n{top_s} satır doldurulacak. Uygulamak için: --calistir")
            return 0

        yazilan = 0
        for i in range(0, len(guncellemeler), TOPLU_BOYUT):
            parca = guncellemeler[i:i + TOPLU_BOYUT]
            db.session.execute(
                text("UPDATE kpi_data SET status = :s, status_percentage = :y "
                     "WHERE id = :i"),
                parca,
            )
            yazilan += len(parca)
        db.session.commit()
        print(f"\n✅ {yazilan} satır güncellendi.")

        kalan = len(_skorsuz_satirlar(tenant_id))
        print(f"Kalan skorsuz satır: {kalan} (beklenen: {top_o} — ölçülmemişler)")
        return 0 if kalan == top_o else 1


if __name__ == "__main__":
    raise SystemExit(main())
