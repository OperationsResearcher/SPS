"""Yıl bazlı Faz 1.4 — override config -> varlık göçü (T9/K15).

DAYANAK: docs/yilbazli/UYGULAMA-PLANI.md §2.4 · SORULAR.md T9
         + kullanıcı kararı K15 (2026-07-20) · migration yb14a7c2e9f1

T9: override tabloları (*_year_configs) KALDIRILIR, her varlık kendi
plan_year_id'sini ve kendi değerlerini taşır (full-clone tek mekanizma).

ÖLÇÜM (2026-07-20) — planın öngördüğünden çok küçük iş:

    tablo                          toplam   gerçek değer   is_included=False
    kpi_year_configs                 1114        59              18
    sub_strategy_year_configs         475        10               0
    process_year_configs              355        10               0
    strategy_year_configs             190        10               0
    individual_kpi_year_configs       525         0               0
    ──────────────────────────────────────────────────────────────────
                                     2659        89              18

    Plan "7.789 satır taşınacak" diyordu; o sayı Faz 1.3'ten ÖNCEKİ durumdu
    (boş 2018/2019 yıllarının config'leri o adımda silindi). Kalan 2659
    satırın da yalnız 89'u bilgi taşıyor — geri kalanı bağlı olduğu varlıkla
    BİREBİR AYNI, yani artık veri.

  K15 — is_included varlığa taşınır. 18 satır `is_included=FALSE` ve hepsi
        KMF'nin (#16) gerçek verisi; PG'leri is_active=TRUE. Anlamı: "gösterge
        aktif ama bu yıl karneye dahil değil". Varlıkta karşılığı yoktu;
        migration yb14a7c2e9f1 kolonu açtı.

GÖÇ KURALI — hedef PG kopyası nasıl bulunur:
    config.plan_year_id o config'in AİT OLDUĞU yılı söyler. Hedef, aynı
    source_kpi_id zincirinden türeyen ve yılı config'in yılına eşit olan
    varlık kopyasıdır (Faz 1.5'teki remap ile aynı yöntem).
    Hedef bulunamazsa satır ATLANIR ve raporlanır — sessizce kaybolmaz.

BU SCRIPT TABLOLARI DÜŞÜRMEZ. Yalnız veriyi taşır. Tabloların DROP'u,
göç doğrulandıktan sonra ayrı bir migration'da yapılır — böylece taşıma
yanlışsa geri dönülebilir.

KULLANIM:
    python scripts/ops/yilbazli_faz1_4_override_goc.py            # KONTROL
    python scripts/ops/yilbazli_faz1_4_override_goc.py --calistir # uygula
"""
from __future__ import annotations

import argparse
import sys

sys.path.insert(0, ".")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402
from sqlalchemy import text  # noqa: E402


# ⚠ KOLON ADI TUZAĞI — calculation_method (ölçüm 2026-07-20)
#
#   process_kpis'te İKİ AYRI kolon var:
#       calculation_method      = "AVG" / "SUM"          (kod — hesaplama motoru)
#       data_collection_method  = "Ortalama" / "Toplama" (Türkçe — kullanıcı alanı)
#
#   kpi_year_configs.calculation_method AYNI ADI taşır ama karşılığı
#   varlıktaki `data_collection_method`'dur (bkz. plan_year_service.py:118,213 —
#   `calculation_method=kpi.data_collection_method`).
#
#   İlk taslak adı ada eşleştiriyordu; sonuç: 1055 sahte "fark" ve göç
#   çalışsaydı 1050 PG'nin AVG'si "Ortalama" olacak, 24'ünkü NULL'a düşecekti
#   — hesaplama motoru kod beklediği için bozulurdu.
#   Doğru eşlemeyle gerçek fark: 35.
#
# Alan çiftleri: (config_alani, varlik_alani) — adlar aynıysa tek string yazılır.
GOCLER = [
    (
        "kpi_year_configs", "process_kpis", "process_kpi_id", "source_kpi_id",
        ["target_value", "unit", "period", "direction", "target_method",
         ("calculation_method", "data_collection_method"),
         "basari_puani_araliklari", "weight",
         "onceki_yil_ortalamasi", "is_included"],
    ),
    (
        "process_year_configs", "processes", "process_id", "source_process_id",
        ["name", "weight", "is_included"],
    ),
    (
        "strategy_year_configs", "strategies", "strategy_id", "source_strategy_id",
        ["title", "code", "description", "is_included"],
    ),
    (
        "sub_strategy_year_configs", "sub_strategies", "sub_strategy_id",
        "source_sub_strategy_id",
        ["title", "code", "description", "is_included"],
    ),
    (
        "individual_kpi_year_configs", "individual_performance_indicators",
        "individual_performance_id", "source_individual_kpi_id",
        ["target_value", "unit", "period", "direction", "target_method",
         "calculation_method", "basari_puani_araliklari", "weight", "is_included"],
    ),
]


def _varlik_kolonlari(conn, tablo: str) -> set[str]:
    return {r[0] for r in conn.execute(text("""
        SELECT column_name FROM information_schema.columns WHERE table_name = :t
    """), {"t": tablo}).fetchall()}


def rapor_ve_uygula(calistir: bool) -> int:
    app = create_app()
    with app.app_context():
        conn = db.session.connection()
        mod = "UYGULAMA" if calistir else "KONTROL"
        print(f"\n{'='*74}\n  FAZ 1.4 — OVERRIDE -> VARLIK GÖÇÜ (T9/K15)  [{mod} MODU]\n{'='*74}\n")

        toplam_tasinan = 0
        toplam_atlanan = 0

        for cfg_tab, var_tab, fk, zincir, alanlar in GOCLER:
            var_kolon = _varlik_kolonlari(conn, var_tab)
            # alanlar: "ad" ya da ("config_alani", "varlik_alani")
            ciftler = [(a, a) if isinstance(a, str) else a for a in alanlar]
            tasinabilir = [(c, v) for c, v in ciftler if v in var_kolon]
            atlanan_alan = [c for c, v in ciftler if v not in var_kolon]

            n = conn.execute(text(f"SELECT COUNT(*) FROM {cfg_tab}")).scalar()
            if not n:
                print(f"── {cfg_tab}: boş, atlandı\n")
                continue

            # Gerçekten farklı olan config'ler (artık veriyi taşımaya gerek yok)
            # Gerçek override = config DOLU ve varlıktakinden farklı.
            # NULL config "değer yok" demektir, varlıktaki değeri EZMEMELİ
            # (ölçüm: 24 satırda cfg NULL iken varlıkta geçerli AVG vardı).
            fark_kosul = " OR ".join(
                f"(cfg.{cf} IS NOT NULL AND cfg.{cf} IS DISTINCT FROM v.{vf})"
                for cf, vf in tasinabilir
            )
            farkli = conn.execute(text(f"""
                SELECT COUNT(*) FROM {cfg_tab} cfg
                  JOIN {var_tab} v ON v.id = cfg.{fk}
                 WHERE {fark_kosul}
            """)).scalar()

            print(f"── {cfg_tab}")
            print(f"   toplam config          {n:>5}")
            print(f"   varlıktan FARKLI       {farkli:>5}  -> taşınacak aday")
            if atlanan_alan:
                print(f"   varlıkta olmayan alan: {', '.join(atlanan_alan)}")

            # Hedef varlık kopyasını zincirden çöz
            # Taşırken de NULL config varlığı ezmesin: COALESCE ile koru
            set_ifade = ", ".join(
                f"{vf} = COALESCE(k.{cf}, t.{vf})" for cf, vf in tasinabilir
            )
            hedef_sql = f"""
                WITH RECURSIVE kok AS (
                    SELECT id, id AS kok_id FROM {var_tab} WHERE {zincir} IS NULL
                    UNION ALL
                    SELECT v.id, k.kok_id FROM {var_tab} v
                      JOIN kok k ON k.id = v.{zincir}
                ),
                var_yil AS (
                    SELECT v.id AS var_id, v.plan_year_id, k.kok_id
                      FROM {var_tab} v JOIN kok k ON k.id = v.id
                     WHERE v.plan_year_id IS NOT NULL
                ),
                esles AS (
                    SELECT cfg.id AS cfg_id, hedef.var_id,
                           {', '.join('cfg.' + cf + ' AS ' + cf for cf, _ in tasinabilir)}
                      FROM {cfg_tab} cfg
                      JOIN var_yil kaynak ON kaynak.var_id = cfg.{fk}
                      JOIN var_yil hedef  ON hedef.kok_id = kaynak.kok_id
                                         AND hedef.plan_year_id = cfg.plan_year_id
                      JOIN {var_tab} v ON v.id = cfg.{fk}
                     WHERE {fark_kosul}
                )
            """

            eslesen = conn.execute(text(
                hedef_sql + " SELECT COUNT(*) FROM esles")).scalar()
            atlanan = farkli - eslesen
            print(f"   hedef kopyası çözülen  {eslesen:>5}")
            if atlanan:
                print(f"   ⚠ hedefi bulunamayan   {atlanan:>5}  -> ATLANIR (raporlandı)")

            toplam_tasinan += eslesen
            toplam_atlanan += atlanan

            if calistir and eslesen:
                conn.execute(text(f"""
                    {hedef_sql}
                    UPDATE {var_tab} t SET {set_ifade}
                      FROM esles k WHERE t.id = k.var_id
                """))
                print(f"   [OK] {eslesen} satır varlığa taşındı")
            print()

        print(f"{'─'*74}")
        print(f"   TOPLAM taşınan: {toplam_tasinan}   atlanan: {toplam_atlanan}")

        if calistir:
            db.session.commit()
            # Doğrulama: is_included korundu mu?
            conn2 = db.session.connection()
            print(f"\n── DOĞRULAMA — is_included=FALSE dağılımı (varlıkta)")
            for _, var_tab, *_ in GOCLER:
                n = conn2.execute(text(
                    f"SELECT COUNT(*) FROM {var_tab} WHERE is_included = FALSE")).scalar()
                print(f"   {var_tab:36} {n:>4}")
            print(f"\n{'='*74}\n  [OK] FAZ 1.4 UYGULANDI"
                  f"\n  NOT: override tabloları HENÜZ DÜŞÜRÜLMEDİ (ayrı migration)"
                  f"\n{'='*74}\n")
        else:
            db.session.rollback()
            print(f"\n{'='*74}\n  KONTROL MODU — hiçbir şey yazılmadı."
                  f"\n  Uygulamak için: --calistir\n{'='*74}\n")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Faz 1.4 — override göçü")
    ap.add_argument("--calistir", action="store_true")
    args = ap.parse_args()
    sys.exit(rapor_ve_uygula(args.calistir))
