"""Yıl bazlı Faz 1.2b — "karışık yıllı PG" düzeltmesi (süreç yılı <> PG yılı).

SORUN (KMF #16, Yayın kopyasında ölçüldü 2026-10-24): 31 PG, kendi plan yılı (PG yılı) bir süreçte,
ama bağlı olduğu SÜREÇ başka yıla ait (ör. süreç 2020 kopyası, PG yılı 2024). Yeni kodda karne
süreç yılına göre listelenir -> bu PG'lerin ölçümleri (28 adet) ekranda görünmez.

DÜZELTME (soft delete, silme yok), her karışık PG (K) için:
  * Aynı kurumda, aynı adlı, PG yılıyla aynı yıldaki süreç T bulunur (yoksa ATLANIR + raporlanır).
  * T içinde K'nın klonu C varsa (aynı ad ya da source_kpi_id=K): ölçüm ve bağlı kayıtlar K -> C taşınır,
    yıla özgü alanlar (ağırlık, hedef...) K'dan C'ye kopyalanır, K pasife alınır.
  * Klon yoksa: K, T'ye bağlanır (process_id) ve alt stratejisi o yılın klonuna eşlenir.
Geri alma kaydı: instance/yilbazli/karisik_pg_geri_alma_<ts>.csv (konteyner volume'ünde kalıcı).

ÇALIŞTIRMA SIRASI: Faz 1.2 (clone zinciri) SONRASI, Faz 1.5 (kpi_data remap) ÖNCESİ.

KULLANIM:
    python scripts/ops/yilbazli_faz1_2b_karisik_pg_duzelt.py --tenant 16            # KONTROL
    python scripts/ops/yilbazli_faz1_2b_karisik_pg_duzelt.py --tenant 16 --calistir # uygula
"""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, ".")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402
from sqlalchemy import text  # noqa: E402

# K'dan C'ye kopyalanan yıla özgü alanlar
KOPYA_ALAN = ["weight", "target_value", "target_method", "basari_puani_araliklari",
              "onceki_yil_ortalamasi", "direction", "is_important"]

# K'yı gösteren tablo.kolon (taşınacak)
REFERANS = [
    ("kpi_data", "process_kpi_id"),
    ("kpi_year_configs", "process_kpi_id"),
    ("process_activities", "process_kpi_id"),
    ("individual_performance_indicators", "source_process_kpi_id"),
    ("favorite_kpis", "process_kpi_id"),
    ("task", "process_kpi_id"),
    ("bsc_kpi_perspectives", "process_kpi_id"),
]

SORGU_KARISIK = """
SELECT k.id, k.name, k.process_id, k.sub_strategy_id, py.year, p.name, p.plan_year_id
FROM process_kpis k JOIN processes p ON p.id = k.process_id
JOIN plan_years py ON py.id = k.plan_year_id
JOIN plan_years pyp ON pyp.id = p.plan_year_id
WHERE p.tenant_id = :t AND k.is_active AND py.year <> pyp.year
ORDER BY p.name, py.year, k.id
"""


def calis(tenant: int, calistir: bool) -> int:
    app = create_app()
    with app.app_context():
        c = db.session.connection()
        satirlar = c.execute(text(SORGU_KARISIK), {"t": tenant}).fetchall()
        print(f"\n{'=' * 72}\n  FAZ 1.2b — KARIŞIK YILLI PG  [{'UYGULAMA' if calistir else 'KONTROL'}]  tenant={tenant}\n{'=' * 72}")
        print(f"Karışık PG: {len(satirlar)}")
        kayit, atlanan, tasi, bagla, olcum = [], [], 0, 0, 0
        baglananlar = set()  # bu çalışmada T'ye bağlanan K'lar klon sayılmaz (aynı adlı kardeş PG'ler birleşmesin)
        for kid, kad, pid, ssid, yil, sad, _ in satirlar:
            t = c.execute(text("""
                SELECT p2.id FROM processes p2 JOIN plan_years y2 ON y2.id = p2.plan_year_id
                WHERE p2.tenant_id = :t AND p2.is_active AND y2.year = :y AND y2.tenant_id = :t
                  AND p2.name = :n ORDER BY p2.id LIMIT 1"""), {"t": tenant, "y": yil, "n": sad}).scalar()
            if not t:
                atlanan.append((kid, kad, sad, yil, "yıl süreci yok"))
                continue
            n_olcum = c.execute(text("SELECT count(*) FROM kpi_data WHERE process_kpi_id=:k"), {"k": kid}).scalar()
            cid = c.execute(text("""
                SELECT id FROM process_kpis WHERE process_id=:t AND is_active
                  AND (source_kpi_id=:k OR name=:n) AND id <> ALL(:bag) ORDER BY (source_kpi_id=:k) DESC, id LIMIT 1"""),
                {"t": t, "k": kid, "n": kad, "bag": list(baglananlar) or [0]}).scalar()
            # alt strateji eşlemesi (yılın klonu)
            yss = None
            if ssid:
                yss = c.execute(text("""
                    SELECT s2.id FROM sub_strategies s2 JOIN strategies st ON st.id = s2.strategy_id
                    JOIN plan_years y2 ON y2.id = st.plan_year_id
                    WHERE y2.year=:y AND y2.tenant_id=:t AND s2.is_active
                      AND (s2.source_sub_strategy_id=:s OR s2.id=:s
                           OR s2.title=(SELECT title FROM sub_strategies WHERE id=:s))
                    ORDER BY (s2.source_sub_strategy_id=:s) DESC, s2.id LIMIT 1"""),
                    {"y": yil, "t": tenant, "s": ssid}).scalar()
            if cid:
                print(f"  TAŞI  K={kid} -> C={cid}  {sad[:6]} {yil} '{kad[:34]}' ölçüm={n_olcum}")
                tasi += 1
                olcum += n_olcum
                if calistir:
                    for tab, col in REFERANS:
                        ek = ""
                        if tab == "individual_performance_indicators":
                            ek = f" AND NOT EXISTS (SELECT 1 FROM {tab} x WHERE x.{col}=:c AND x.user_id={tab}.user_id AND x.is_active)"
                        ids = [r[0] for r in c.execute(text(f"SELECT id FROM {tab} WHERE {col}=:k{ek}"), {"k": kid, "c": cid})]
                        if ids:
                            c.execute(text(f"UPDATE {tab} SET {col}=:c WHERE {col}=:k{ek}"), {"k": kid, "c": cid})
                            kayit += [(tab, i, col, kid, cid) for i in ids]
                    eski = c.execute(text(f"SELECT {','.join(KOPYA_ALAN)} FROM process_kpis WHERE id=:c"), {"c": cid}).fetchone()
                    kayit.append(("process_kpis", cid, "KOPYA_ALAN", repr(tuple(eski)), kid))
                    c.execute(text("UPDATE process_kpis SET " + ",".join(f"{a}=k.{a}" for a in KOPYA_ALAN) +
                                   " FROM process_kpis k WHERE k.id=:k AND process_kpis.id=:c"), {"k": kid, "c": cid})
                    c.execute(text("UPDATE process_kpis SET is_active=false WHERE id=:k"), {"k": kid})
                    kayit.append(("process_kpis", kid, "is_active", True, False))
            else:
                print(f"  BAĞLA K={kid} -> süreç {t}  {sad[:6]} {yil} '{kad[:34]}' ölçüm={n_olcum} alt_str {ssid}->{yss}")
                bagla += 1
                baglananlar.add(kid)
                olcum += n_olcum
                if calistir:
                    kayit.append(("process_kpis", kid, "process_id|sub_strategy_id", f"{pid}|{ssid}", f"{t}|{yss or ssid}"))
                    c.execute(text("UPDATE process_kpis SET process_id=:t, sub_strategy_id=:s WHERE id=:k"),
                              {"t": t, "s": yss or ssid, "k": kid})
        for a in atlanan:
            print(f"  ATLANDI {a}")
        print(f"\nÖzet: taşı={tasi} bağla={bagla} atlanan={len(atlanan)} etkilenen ölçüm={olcum}")
        if calistir:
            yol = Path("instance/yilbazli")
            yol.mkdir(parents=True, exist_ok=True)
            dosya = yol / f"karisik_pg_geri_alma_{datetime.now():%Y%m%d_%H%M%S}.csv"
            with dosya.open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["tablo", "id", "kolon", "eski", "yeni"])
                w.writerows(kayit)
            db.session.commit()
            kalan = db.session.connection().execute(text(SORGU_KARISIK), {"t": tenant}).fetchall()
            print(f"UYGULANDI. Geri alma: {dosya}  | kalan karışık PG: {len(kalan)}")
        else:
            print("KONTROL: yazılmadı. Uygulamak için --calistir")
        return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Faz 1.2b — karışık yıllı PG düzelt")
    ap.add_argument("--tenant", type=int, required=True)
    ap.add_argument("--calistir", action="store_true")
    a = ap.parse_args()
    sys.exit(calis(a.tenant, a.calistir))
