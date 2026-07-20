"""Yıl bazlı Faz 1.5 — kpi_data'yı yılın PG kopyasına bağla (T12).

DAYANAK: docs/yilbazli/UYGULAMA-PLANI.md §2.5 · SORULAR.md T12
         + kullanıcı kararı K14 (2026-07-20)

T12: "kpi_data yılın PG kopyasına bağlansın" — year=2024 olan satır, o PG'nin
2024 kopyasının id'sine işaret eder. Böylece yıl TEK kaynaktan okunur ve mühür
JOIN process_kpis -> plan_years.status ile tek noktadan işler.

ÖLÇÜM (2026-07-20, Faz 1.2 sonrası) — planın öngördüğünden ÇOK küçük iş:

    kpi_data toplam            366.604
      zaten doğru yılda        365.776   (%99,8)  -> DOKUNULMAZ
      yanlış yılda, PG aktif       555            -> REMAP EDİLİR
      yanlış yılda, PG pasif       273            -> DOKUNULMAZ (K14)

    Plan "366K satırlık geri alınamaz remap" diyordu; gerçekte Faz 1.2'nin
    clone zinciri satırların %99,8'ini zaten doğru kopyaya bağlamış durumda.
    Yapılacak iş 555 satır.

  K14 — PG'si is_active=False olan 273 satır OLDUĞU GİBİ BIRAKILIR.
        Gerekçe: o göstergeler silinmiş, klonlanmadıkları için hedef yıl
        kopyaları yok. Pasif oldukları için hiçbir yıl bazlı ekranda
        görünmüyor, rapor rakamlarını etkilemiyorlar. Doğrulama betiği
        bunları "bilinen istisna" olarak raporlar.
        (Örnekler: "Deneme PG", "Verilen Teklif Sayısı" — tenant 1.)

HEDEF ÇÖZÜMÜ — source_kpi_id zinciri:
    Klonlanan her PG source_kpi_id ile kaynağına bağlı. Zincirin KÖKÜ bulunup,
    aynı kökten türeyen ve yılı kd.year'a eşit olan kopya hedef alınır.
    İsim eşleşmesi YEDEK ölçüt DEĞİL — kullanılmaz (aynı isimli farklı PG'ler
    var: KMF'de "Doğalgaz Tüketim Miktarı" 3 ayrı PG).
    İki yöntem karşılaştırıldı: zincir 555, isim 560 -> %99 örtüşme; zincir
    daha güvenilir olduğu için o seçildi.

GERİ ALINABİLİRLİK: Bu script kpi_data.process_kpi_id'yi değiştirir.
    Eski değer kayıt altına alınır: backups/yilbazli/remap_geri_alma_<tarih>.csv
    Yedek: backups/yilbazli/faz1_2_sonrasi_2026-07-20.dump

KULLANIM:
    python scripts/ops/yilbazli_faz1_5_kpi_data_remap.py            # KONTROL
    python scripts/ops/yilbazli_faz1_5_kpi_data_remap.py --calistir # uygula
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, ".")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402
from sqlalchemy import text  # noqa: E402


# Zincir kökünü bulup hedef yıl kopyasını çözen sorgu.
# kok      : source_kpi_id zincirini yukarı takip ederek her PG'nin kökünü bulur
# pg_yil   : her PG'yi (kök, tenant, yıl) üçlüsüyle etiketler
# son SELECT: kd.year ile PG'nin yılı uyuşmayan satırlar için, AYNI KÖKTEN türeyen
#             ve yılı kd.year'a eşit olan kopyayı hedef seçer
COZUM_SQL = """
WITH RECURSIVE kok AS (
    SELECT id, id AS kok_id
      FROM process_kpis
     WHERE source_kpi_id IS NULL
    UNION ALL
    SELECT pk.id, k.kok_id
      FROM process_kpis pk
      JOIN kok k ON k.id = pk.source_kpi_id
),
pg_yil AS (
    SELECT pk.id AS pg_id, pk.is_active, py.year AS pg_yil,
           p.tenant_id, k.kok_id
      FROM process_kpis pk
      JOIN processes   p  ON p.id  = pk.process_id
      JOIN plan_years  py ON py.id = pk.plan_year_id
      JOIN kok         k  ON k.id  = pk.id
)
SELECT kd.id, kd.process_kpi_id, hedef.pg_id, kd.year,
       kaynak.pg_yil, kaynak.tenant_id
  FROM kpi_data kd
  JOIN pg_yil kaynak ON kaynak.pg_id = kd.process_kpi_id
  JOIN pg_yil hedef  ON hedef.kok_id     = kaynak.kok_id
                    AND hedef.tenant_id  = kaynak.tenant_id
                    AND hedef.pg_yil     = kd.year
 WHERE kd.year <> kaynak.pg_yil
   AND kaynak.is_active = TRUE
"""


def rapor_ve_uygula(calistir: bool) -> int:
    app = create_app()
    with app.app_context():
        mod = "UYGULAMA" if calistir else "KONTROL"
        print(f"\n{'='*72}\n  FAZ 1.5 — kpi_data REMAP (T12)  [{mod} MODU]\n{'='*72}\n")

        conn = db.session.connection()

        toplam = conn.execute(text("SELECT COUNT(*) FROM kpi_data")).scalar()

        yanlis = conn.execute(text("""
            SELECT COUNT(*) FROM kpi_data kd
              JOIN process_kpis pk ON pk.id = kd.process_kpi_id
              JOIN plan_years  py ON py.id = pk.plan_year_id
             WHERE kd.year <> py.year
        """)).scalar()

        pasif = conn.execute(text("""
            SELECT COUNT(*) FROM kpi_data kd
              JOIN process_kpis pk ON pk.id = kd.process_kpi_id
              JOIN plan_years  py ON py.id = pk.plan_year_id
             WHERE kd.year <> py.year AND pk.is_active = FALSE
        """)).scalar()

        print(f"   kpi_data toplam        {toplam:>8}")
        print(f"   zaten doğru yılda      {toplam - yanlis:>8}  -> dokunulmaz")
        print(f"   yanlış yılda           {yanlis:>8}")
        print(f"     PG pasif (K14)       {pasif:>8}  -> dokunulmaz")
        print(f"     PG aktif             {yanlis - pasif:>8}  -> remap adayı\n")

        satirlar = conn.execute(text(COZUM_SQL)).fetchall()
        print(f"── Zincirden hedefi çözülen: {len(satirlar)} satır\n")

        if not satirlar:
            print("   (remap edilecek satır yok)")
        else:
            ozet: dict[tuple, int] = {}
            for _, _, _, veri_yili, eski_yil, tid in satirlar:
                ozet[(tid, eski_yil, veri_yili)] = ozet.get((tid, eski_yil, veri_yili), 0) + 1
            print(f"   {'tenant':>7}{'PG yılı':>9}{'->':>4}{'veri yılı':>11}{'satır':>7}")
            for (tid, eski, yeni), n in sorted(ozet.items()):
                print(f"   {tid:>7}{eski:>9}{'->':>4}{yeni:>11}{n:>7}")

            if calistir:
                # Geri alma kaydı
                yedek = Path("backups/yilbazli")
                yedek.mkdir(parents=True, exist_ok=True)
                csv_yol = yedek / "remap_geri_alma_2026-07-20.csv"
                with csv_yol.open("w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    w.writerow(["kpi_data_id", "eski_process_kpi_id", "yeni_process_kpi_id"])
                    for kd_id, eski_pg, yeni_pg, *_ in satirlar:
                        w.writerow([kd_id, eski_pg, yeni_pg])
                print(f"\n   Geri alma kaydı: {csv_yol}")

                for kd_id, _eski, yeni_pg, *_ in satirlar:
                    conn.execute(text(
                        "UPDATE kpi_data SET process_kpi_id = :y WHERE id = :i"
                    ), {"y": yeni_pg, "i": kd_id})
                db.session.commit()
                print(f"   [OK] {len(satirlar)} satır remap edildi.")

        if calistir:
            # Doğrulama
            conn2 = db.session.connection()
            son_toplam = conn2.execute(text("SELECT COUNT(*) FROM kpi_data")).scalar()
            son_yanlis = conn2.execute(text("""
                SELECT COUNT(*) FROM kpi_data kd
                  JOIN process_kpis pk ON pk.id = kd.process_kpi_id
                  JOIN plan_years  py ON py.id = pk.plan_year_id
                 WHERE kd.year <> py.year
            """)).scalar()
            print(f"\n── DOĞRULAMA")
            print(f"   kpi_data toplam: {son_toplam} "
                  f"({'DEĞİŞMEDİ' if son_toplam == toplam else '!!! DEĞİŞTİ'})")
            print(f"   kalan yanlış yıl: {son_yanlis} "
                  f"({'= K14 istisnası, beklenen' if son_yanlis == pasif else '!!! beklenmedik'})")
            print(f"\n{'='*72}\n  [OK] FAZ 1.5 UYGULANDI\n{'='*72}\n")
        else:
            db.session.rollback()
            print(f"\n{'='*72}\n  KONTROL MODU — hiçbir şey yazılmadı."
                  f"\n  Uygulamak için: --calistir\n{'='*72}\n")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Faz 1.5 — kpi_data remap (T12)")
    ap.add_argument("--calistir", action="store_true")
    args = ap.parse_args()
    sys.exit(rapor_ve_uygula(args.calistir))
