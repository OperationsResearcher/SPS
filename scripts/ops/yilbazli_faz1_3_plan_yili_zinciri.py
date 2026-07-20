"""Yıl bazlı Faz 1.3 — plan yılı zinciri üretimi + boş yıl temizliği.

DAYANAK: docs/yilbazli/UYGULAMA-PLANI.md §2.3 · SORULAR.md K5, K6, T4, T11
         + kullanıcı kararları 2026-07-20 (aşağıda K10-K12)

KULLANICI KARARLARI (2026-07-20, bu script'in yazımı sırasında alındı):

  K10 — Boş geçmiş plan yılları SİLİNİR, gelecek yıl KALIR.
        Tomofil #27 ve klonlarında (58/59/60/61) 2018-2019 boş (kpi_data=0) ->
        silinir. 2027 KALIR: gelecek yıl planlaması meşru ihtiyaç.
        Sonuç: her klon 2020-2027 = 8 plan yılı.

  K11 — Eskişehir #28: 2025 plan yılı ÜRETİLİR.
        Kurumun en eski verisi 2025 ama tek plan yılı 2026 -> T4 gereği 2025
        üretilir, veri ona bağlanır (T12 remap yapacak).

  K12 — Verisi olan kuruma gerçek zincir, boş kuruma 2026.
        Default Corp #1: ilk verisi 2021 -> 2021-2026 zinciri.
        #29, #31, #56, #57 (tamamen boş): yalnız 2026 (K5).

[!] SİLME GÜVENLİĞİ — bu script'in en kritik bölümü

Ölçüm (2026-07-20) 2018/2019 plan yıllarına **6.066 satır bağlı** buldu.
Körlemesine silme veri kaybettirirdi. Kaynak ayrıştırıldı:

  A) 936 satır — Faz 1.1 migration'ının T3 doldurması
     (blue_ocean_* 18 · initiatives 63 · process_maturity 340 · PSSL 515)
     Migration "tenant'ın EN ESKİ plan yılı"nı seçiyordu; Tomofil'de bu 2018'di.
     -> GERÇEK VERİ İŞARET EDİYOR. Silinmez, 2020'ye TAŞINIR.

  B) 5.130 satır — override config tabloları
     (kpi_year_configs 2110 · sub_strategy 930 · individual 1050 ·
      process 680 · strategy 360)
     -> T9 (full-clone) bunları zaten KALDIRIYOR. Ayrıca (plan_year_id, X)
       UNIQUE kısıtı var: 2020'ye taşımak çakışır çünkü aynı kayıtlar orada
       zaten mevcut. Taşınmaz, silinir — Faz 1.4 göçü clone'dan yeniden üretecek.

Bu ayrım yapılmadan silme YAPILMAZ. A grubu taşınmadan B grubu silinirse
Blue Ocean/VRIO/olgunluk verisi kaybolur.

KULLANIM:
    python scripts/ops/yilbazli_faz1_3_plan_yili_zinciri.py            # KONTROL (varsayılan)
    python scripts/ops/yilbazli_faz1_3_plan_yili_zinciri.py --calistir # uygula

Kontrol modu hiçbir şey yazmaz — ne yapacağını satır satır raporlar.
"""
from __future__ import annotations

import io
import os

import argparse
import sys
from collections import defaultdict

sys.path.insert(0, ".")

# Windows konsolu cp1254; Turkce/kutu karakterleri icin UTF-8 zorla
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402
from sqlalchemy import text  # noqa: E402


# Faz 1.1'de plan_year_id eklenen tablolar — bunlar TAŞINIR (A grubu)
TASINACAK = [
    "blue_ocean_canvases",
    "blue_ocean_errc_items",
    "blue_ocean_factors",
    "initiatives",
    "process_maturity",
    "process_sub_strategy_links",
]

# Override config tabloları — T9 kaldıracak, SİLİNİR (B grubu)
SILINECEK_OVERRIDE = [
    "kpi_year_configs",
    "strategy_year_configs",
    "sub_strategy_year_configs",
    "process_year_configs",
    "individual_kpi_year_configs",
]


def _tenant_ilk_veri_yili(conn, tenant_id: int):
    """Kurumun en eski gerçek verisinin yılı (T4). Veri yoksa None."""
    row = conn.execute(text("""
        SELECT MIN(kd.year)
          FROM kpi_data kd
          JOIN process_kpis pk ON pk.id = kd.process_kpi_id
          JOIN processes p ON p.id = pk.process_id
         WHERE p.tenant_id = :t
    """), {"t": tenant_id}).scalar()
    return row


def rapor_ve_uygula(calistir: bool) -> int:
    app = create_app()
    with app.app_context():
        conn = db.session.connection()
        mod = "UYGULAMA" if calistir else "KONTROL"
        print(f"\n{'='*70}\n  FAZ 1.3 — PLAN YILI ZİNCİRİ  [{mod} MODU]\n{'='*70}\n")

        # -- 1) Boş geçmiş plan yılları (K10) ----------------------------
        bos = conn.execute(text("""
            SELECT py.id, py.tenant_id, py.year
              FROM plan_years py
             WHERE py.year < 2020
             ORDER BY py.tenant_id, py.year
        """)).fetchall()

        print(f"-- 1) K10: 2020 öncesi plan yılları ({len(bos)} adet)\n")
        if bos:
            bos_ids = [r[0] for r in bos]
            # Güvenlik: gerçekten veri yok mu?
            veri = conn.execute(text("""
                SELECT COUNT(*) FROM kpi_data kd
                  JOIN process_kpis pk ON pk.id = kd.process_kpi_id
                  JOIN processes p ON p.id = pk.process_id
                  JOIN plan_years py ON py.tenant_id = p.tenant_id AND py.year = kd.year
                 WHERE py.id = ANY(:ids)
            """), {"ids": bos_ids}).scalar()
            print(f"   Bu yıllara ait gerçek kpi_data: {veri}")
            if veri:
                print("   [DUR] DUR — gerçek veri var, silme iptal. İnceleme gerekir.")
                return 1

            for tid, grup in _grupla(bos):
                yillar = ", ".join(str(r[2]) for r in grup)
                print(f"   tenant {tid:>3} -> silinecek: {yillar}")

            # A grubu: taşı
            print(f"\n   A) Faz 1.1 verisi 2020'ye TAŞINIYOR:")
            for tab in TASINACAK:
                n = conn.execute(text(f"""
                    SELECT COUNT(*) FROM {tab} WHERE plan_year_id = ANY(:ids)
                """), {"ids": bos_ids}).scalar()
                if not n:
                    continue
                print(f"      {tab:32} {n:>5} satır")
                if calistir:
                    conn.execute(text(f"""
                        UPDATE {tab} t
                           SET plan_year_id = hedef.id
                          FROM plan_years eski
                          JOIN plan_years hedef
                            ON hedef.tenant_id = eski.tenant_id AND hedef.year = 2020
                         WHERE t.plan_year_id = eski.id
                           AND eski.id = ANY(:ids)
                    """), {"ids": bos_ids})

            # B grubu: sil (T9 zaten kaldıracak + UNIQUE çakışması)
            print(f"\n   B) Override config SİLİNİYOR (T9 yeniden üretecek):")
            for tab in SILINECEK_OVERRIDE:
                n = conn.execute(text(f"""
                    SELECT COUNT(*) FROM {tab} WHERE plan_year_id = ANY(:ids)
                """), {"ids": bos_ids}).scalar()
                if not n:
                    continue
                print(f"      {tab:32} {n:>5} satır")
                if calistir:
                    conn.execute(text(f"DELETE FROM {tab} WHERE plan_year_id = ANY(:ids)"),
                                 {"ids": bos_ids})

            if calistir:
                conn.execute(text("DELETE FROM plan_years WHERE id = ANY(:ids)"), {"ids": bos_ids})
                print(f"\n   [OK] {len(bos)} boş plan yılı silindi.")
        else:
            print("   (yok)")

        # -- 2) Eksik plan yılı üretimi (K11 + K12 + T4) ----------------─
        print(f"\n-- 2) K11/K12: eksik plan yılı üretimi\n")
        tenants = conn.execute(text("""
            SELECT id, name FROM tenants WHERE is_active ORDER BY id
        """)).fetchall()

        uretilecek: list[tuple[int, int]] = []
        for tid, tname in tenants:
            ilk_veri = _tenant_ilk_veri_yili(conn, tid)
            mevcut = {r[0] for r in conn.execute(text(
                "SELECT year FROM plan_years WHERE tenant_id = :t"), {"t": tid}).fetchall()}

            # T4/K12: verisi olan kurum ilk verisinden başlar; boş kurum 2026'dan (K5)
            baslangic = ilk_veri if ilk_veri else 2026
            # K6: sistem ekseni 2020'den önce başlamaz
            baslangic = max(baslangic, 2020)
            hedef = set(range(baslangic, 2027))  # 2026 dahil

            eksik = sorted(hedef - mevcut)
            if eksik:
                ad = (tname or "")[:24]
                kaynak = f"ilk veri {ilk_veri}" if ilk_veri else "veri yok -> 2026 (K5)"
                print(f"   tenant {tid:>3} {ad:24} {kaynak:22} -> üretilecek: "
                      f"{', '.join(map(str, eksik))}")
                uretilecek += [(tid, y) for y in eksik]

        if not uretilecek:
            print("   (eksik yok)")
        elif calistir:
            for tid, yil in uretilecek:
                # T11: kapalı yıl üretilmez — kurum kendisi mühürler
                conn.execute(text("""
                    INSERT INTO plan_years (tenant_id, year, name, status, created_at)
                    VALUES (:t, :y, :n, 'draft', NOW())
                """), {"t": tid, "y": yil, "n": f"{yil} Stratejik Planı"})
            print(f"\n   [OK] {len(uretilecek)} plan yılı üretildi (status=draft — T11).")

        # -- 3) T11: mevcut closed -> draft ------------------------------─
        print(f"\n-- 3) T11: kapalı yıllar taslağa çevriliyor\n")
        kapali = conn.execute(text(
            "SELECT COUNT(*) FROM plan_years WHERE status = 'closed'")).scalar()
        print(f"   status='closed' plan yılı: {kapali}")
        if kapali and calistir:
            conn.execute(text("""
                UPDATE plan_years SET status = 'draft', closed_at = NULL
                 WHERE status = 'closed'
            """))
            print(f"   [OK] {kapali} yıl draft yapıldı (kurum kendisi mühürleyecek).")
        elif kapali:
            print("   -> draft yapılacak; closed_at temizlenecek")

        if calistir:
            db.session.commit()
            print(f"\n{'='*70}\n  [OK] FAZ 1.3 UYGULANDI\n{'='*70}\n")
        else:
            db.session.rollback()
            print(f"\n{'='*70}\n  KONTROL MODU — hiçbir şey yazılmadı."
                  f"\n  Uygulamak için: --calistir\n{'='*70}\n")
    return 0


def _grupla(rows):
    d = defaultdict(list)
    for r in rows:
        d[r[1]].append(r)
    return sorted(d.items())


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Faz 1.3 — plan yılı zinciri")
    ap.add_argument("--calistir", action="store_true",
                    help="Değişiklikleri uygula (varsayılan: kontrol modu)")
    args = ap.parse_args()
    sys.exit(rapor_ve_uygula(args.calistir))
