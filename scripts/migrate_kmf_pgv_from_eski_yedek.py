#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kayseri Model Fabrika (eski kurum_id=9) performans_gosterge_veri kayitlarini
docs/kokpitim_yedek_eski.db -> aktif DB (tenants.id=16) kpi_data olarak aktarir.

Eslestirme:
- Kurum: sabit eski kurum 9 -> yeni tenant 16 (KMF / Kayseri Model Fabrika)
- Surec: surec.ad == processes.name (tenant 16)
- PG: surec_performans_gostergesi.ad == process_kpis.name (ayni surec altinda)
- Kullanici: user.email (kucuk harf) eslesmesi

Kullanim:
  python scripts/migrate_kmf_pgv_from_eski_yedek.py
  python scripts/migrate_kmf_pgv_from_eski_yedek.py --dry-run
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OLD_DB = ROOT / "docs" / "kokpitim_yedek_eski.db"
OLD_KURUM_ID = 9
NEW_TENANT_ID = 16


def _parse_date(val) -> date | None:
    if val is None:
        return None
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    s = str(val).strip()[:10]
    if len(s) >= 10:
        try:
            return date(int(s[0:4]), int(s[5:7]), int(s[8:10]))
        except ValueError:
            return None
    return None


def _parse_dt(val) -> datetime | None:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val if val.tzinfo else val.replace(tzinfo=timezone.utc)
    s = str(val).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(s[:26], fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not OLD_DB.is_file():
        raise SystemExit(f"Eski DB yok: {OLD_DB}")

    old = sqlite3.connect(OLD_DB)
    old.row_factory = sqlite3.Row

    from app import create_app
    from app.models import db
    from app.models.core import User
    from app.models.process import KpiData, Process, ProcessKpi

    app = create_app()

    with app.app_context():
        surec_map: dict[int, int] = {}
        for row in old.execute(
            "SELECT id, ad FROM surec WHERE kurum_id = ? AND silindi = 0",
            (OLD_KURUM_ID,),
        ):
            oid, oad = row["id"], row["ad"]
            if not oad:
                print(f"[UYARI] Eski surec id={oid} ad bos, atlandi")
                continue
            p = Process.query.filter_by(
                tenant_id=NEW_TENANT_ID, name=oad, is_active=True
            ).first()
            if not p:
                print(f"[HATA] Yeni DB'de surec bulunamadi (ad eslesmedi): eski id={oid}")
                raise SystemExit(1)
            surec_map[oid] = p.id

        # SPG -> process_kpi: (eski_surec_id, eski_spg_ad) -> yeni pk id
        def resolve_pk_id(old_surec_id: int, spg_ad: str) -> int | None:
            npid = surec_map.get(old_surec_id)
            if not npid or not spg_ad:
                return None
            pk = ProcessKpi.query.filter_by(
                process_id=npid, name=spg_ad, is_active=True
            ).first()
            return pk.id if pk else None

        # Kullanici email haritasi
        user_map: dict[int, int] = {}
        old_users = old.execute(
            "SELECT id, email FROM user WHERE kurum_id = ?", (OLD_KURUM_ID,)
        ).fetchall()
        for r in old_users:
            oid = r["id"]
            em = (r["email"] or "").strip().lower()
            if not em:
                continue
            u = User.query.filter_by(email=em).first()
            if not u:
                print(f"[HATA] Aktif DB'de kullanici yok: email={em} (eski user id={oid})")
                raise SystemExit(1)
            if u.tenant_id != NEW_TENANT_ID:
                print(
                    f"[UYARI] {em} tenant_id={u.tenant_id} != {NEW_TENANT_ID}; yine de eslestirildi."
                )
            user_map[oid] = u.id

        sql = """
        SELECT pgv.*, b.kaynak_surec_id, b.kaynak_surec_pg_id, spg.ad AS spg_ad
        FROM performans_gosterge_veri pgv
        JOIN user u ON u.id = pgv.user_id
        JOIN bireysel_performans_gostergesi b ON b.id = pgv.bireysel_pg_id
        JOIN surec_performans_gostergesi spg ON spg.id = b.kaynak_surec_pg_id
        WHERE u.kurum_id = ?
        ORDER BY pgv.created_at ASC, pgv.id ASC
        """
        rows = old.execute(sql, (OLD_KURUM_ID,)).fetchall()
        migrated = skipped = errors = 0

        for pgv in rows:
            uid_old = pgv["user_id"]
            uid_new = user_map.get(uid_old)
            if not uid_new:
                print(f"[HATA] user_id={uid_old} haritada yok")
                errors += 1
                continue

            pk_id = resolve_pk_id(pgv["kaynak_surec_id"], pgv["spg_ad"])
            if not pk_id:
                print(
                    f"[HATA] process_kpi bulunamadi: surec_id={pgv['kaynak_surec_id']} spg_ad={pgv['spg_ad']!r}"
                )
                errors += 1
                continue

            d = _parse_date(pgv["veri_tarihi"])
            if not d:
                print(f"[HATA] veri_tarihi cozulemedi: pgv id={pgv['id']}")
                errors += 1
                continue

            yil = int(pgv["yil"])
            pt = pgv["giris_periyot_tipi"] or (
                "ceyrek" if pgv["ceyrek"] else ("aylik" if pgv["ay"] else None)
            )
            pn = pgv["giris_periyot_no"]
            if pn is None and pgv["ceyrek"]:
                pn = int(pgv["ceyrek"])
            pm = pgv["giris_periyot_ay"] if pgv["giris_periyot_ay"] is not None else pgv["ay"]

            actual = pgv["gerceklesen_deger"]
            if actual is None or str(actual).strip() == "":
                actual = "0"

            dup = KpiData.query.filter_by(
                process_kpi_id=pk_id,
                year=yil,
                data_date=d,
                user_id=uid_new,
                is_active=True,
            ).first()
            if dup:
                print(f"[ATLANDI] Duplicate: pk={pk_id} yil={yil} tarih={d} user={uid_new}")
                skipped += 1
                continue

            entry = KpiData(
                process_kpi_id=pk_id,
                year=yil,
                data_date=d,
                period_type=pt,
                period_no=pn,
                period_month=pm,
                target_value=pgv["hedef_deger"],
                actual_value=str(actual),
                status=pgv["durum"],
                status_percentage=pgv["durum_yuzdesi"],
                description=pgv["aciklama"],
                user_id=uid_new,
                created_at=_parse_dt(pgv["created_at"]) or datetime.now(timezone.utc),
                updated_at=_parse_dt(pgv["updated_at"]) or datetime.now(timezone.utc),
                is_active=True,
                deleted_at=None,
                deleted_by_id=None,
            )
            db.session.add(entry)
            migrated += 1
            print(f"  + pgv eski id={pgv['id']} -> kpi_data pk={pk_id} user={uid_new} {d}")

        if args.dry_run:
            db.session.rollback()
            print(f"\n[DRY-RUN] migrated={migrated} skipped={skipped} errors={errors}")
        else:
            db.session.commit()
            print(f"\n[TAMAM] migrated={migrated} skipped={skipped} errors={errors}")

    old.close()


if __name__ == "__main__":
    main()
