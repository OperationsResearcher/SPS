"""
randomize_tomofil_kpi_data.py — Tomofil tenant icin KpiData satirlarini:
  1. Mevcutleri SIL.
  2. Her ay icin (2021-01'den 2026-05'e), her aktif surece 10-30 arasi random KpiData ekle.
     - user_id: o surecin uyelerinden (process_members + leaders + owners + manuel kullanicilarin process_codes'i + departman eslesmesi)
     - process_kpi: o surecin o yildaki aktif KPI'larindan rastgele
     - actual_value: KPI trajectory + noise

Kullanim:
  python scripts/randomize_tomofil_kpi_data.py --tenant-id 26 --dry-run
  python scripts/randomize_tomofil_kpi_data.py --tenant-id 26 --execute
"""
from __future__ import annotations

import argparse
import random
import sys
from datetime import date, datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sqlalchemy import text
from app import create_app
from extensions import db
from app.models.process import KpiData

random.seed(123)

# Departman → süreç eşleşmesi (bulk kullanıcılar için)
DEPT_TO_PROCESSES = {
    "Üretim — CNC + Montaj":         ["P2M"],
    "Üretim — Kalite Güvence":       ["P2M", "I2R"],
    "Üretim — Bakım":                 ["P2M", "D2I"],
    "Ar-Ge ve Tasarım":               ["C2L"],
    "Tedarik ve Lojistik":            ["S2P"],
    "Satış (OEM + İhracat)":          ["A2R"],
    "İnsan Kaynakları":               ["H2R"],
    "Finans ve Muhasebe":             ["R2R", "R2M"],
    "Bilgi Teknolojileri":            ["D2I"],
    "Sürdürülebilirlik ve ESG":       ["B2R", "R2M"],
    "Müşteri Hizmetleri ve Garanti":  ["I2R"],
    "Strateji ve PMO":                ["S2E"],
    "Sağlık-Güvenlik-Çevre":          ["R2M"],
    "Pazarlama ve İletişim":          ["A2R"],
    "Hukuk ve Uyum":                  ["R2R"],
    "Eğitim ve Akademi":              ["H2R"],
    "Yönetim":                         ["S2E"],
    "Yönetim / IT":                   ["S2E", "D2I"],
}


def build_process_members(tenant_id: int):
    """{process_code: [user_ids]} eşleşmesini oluştur."""
    process_to_members: dict[str, set[int]] = {}

    # Tum proseslerin id->code mapping
    rows = db.session.execute(text(
        "SELECT id, code, plan_year_id FROM processes WHERE tenant_id=:t"
    ), {"t": tenant_id}).fetchall()
    proc_id_to_code = {r[0]: r[1] for r in rows}

    # Manuel kullanicilar zaten owners/leaders/members tablolarinda
    for tbl in ("process_owners_table", "process_leaders", "process_members"):
        rows = db.session.execute(text(
            f"SELECT process_id, user_id FROM {tbl} WHERE process_id IN "
            f"(SELECT id FROM processes WHERE tenant_id=:t)"
        ), {"t": tenant_id}).fetchall()
        for pid, uid in rows:
            code = proc_id_to_code.get(pid)
            if code:
                process_to_members.setdefault(code, set()).add(uid)

    # Departman eşleştirmesinden bulk kullanıcılar
    users = db.session.execute(text(
        "SELECT id, department FROM users WHERE tenant_id=:t AND is_active=true"
    ), {"t": tenant_id}).fetchall()
    for uid, dept in users:
        for code in DEPT_TO_PROCESSES.get(dept or "", []):
            process_to_members.setdefault(code, set()).add(uid)

    # En azindan owner her zaman var; emniyet için admin de fallback olur
    return {k: list(v) for k, v in process_to_members.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tenant-id", type=int, required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--min-per-month", type=int, default=10)
    ap.add_argument("--max-per-month", type=int, default=30)
    args = ap.parse_args()

    if not (args.dry_run or args.execute):
        ap.error("--dry-run veya --execute gerekli")

    app = create_app()
    with app.app_context():
        tid = args.tenant_id
        print(f"Tenant id = {tid}")

        # 1) Mevcut kpi_data say
        existing = db.session.execute(text("""
            SELECT count(*) FROM kpi_data WHERE process_kpi_id IN (
              SELECT k.id FROM process_kpis k
              JOIN processes p ON k.process_id=p.id
              WHERE p.tenant_id=:t
            )
        """), {"t": tid}).scalar()
        print(f"Mevcut kpi_data : {existing}")

        # 2) Süreç → üye eşleştirmesi
        members = build_process_members(tid)
        for code, ids in sorted(members.items()):
            print(f"  members[{code:4s}] = {len(ids)} kullanıcı")

        # 3) Yıl → plan_year_id; süreç_code+plan_year → process_id; KPI listesi
        plan_year_rows = db.session.execute(text(
            "SELECT id, year FROM plan_years WHERE tenant_id=:t ORDER BY year"
        ), {"t": tid}).fetchall()
        year_to_pyid = {y: pid for pid, y in plan_year_rows}

        process_rows = db.session.execute(text(
            "SELECT id, code, plan_year_id FROM processes WHERE tenant_id=:t"
        ), {"t": tid}).fetchall()
        # (year, code) -> process_id
        proc_by_year_code = {}
        # plan_year_id -> year
        pyid_to_year = {pid: y for pid, y in plan_year_rows}
        for pid, code, plan_year_id in process_rows:
            y = pyid_to_year.get(plan_year_id)
            if y:
                proc_by_year_code[(y, code)] = pid

        kpi_rows = db.session.execute(text("""
            SELECT k.id, k.process_id, k.target_value, k.direction, k.onceki_yil_ortalamasi, k.code, p.plan_year_id
            FROM process_kpis k JOIN processes p ON k.process_id=p.id
            WHERE p.tenant_id=:t AND k.is_active=true
        """), {"t": tid}).fetchall()
        # (year, process_code) -> [(kpi_id, target, direction, baseline, code)]
        kpis_by_year_process = {}
        for kid, pid, tv, direction, base, kcode, plan_year_id in kpi_rows:
            y = pyid_to_year.get(plan_year_id)
            # process code'u bul
            code = None
            for r_pid, r_code, r_pyid in process_rows:
                if r_pid == pid:
                    code = r_code
                    break
            if not (y and code):
                continue
            try:
                tv_num = float(str(tv).replace(",", "."))
            except (ValueError, TypeError):
                tv_num = 0.0
            kpis_by_year_process.setdefault((y, code), []).append(
                (kid, tv_num, direction or "Increasing", float(base or 0), kcode)
            )

        # 4) Yeni kayit planini olustur
        # Yıl-ay listesi: 2021-01 → 2026-05
        months = []
        for y in range(2021, 2026):
            for m in range(1, 13):
                months.append((y, m))
        for m in range(1, 6):  # 2026-01 ... 2026-05
            months.append((2026, m))

        # Aktif süreçler her yıl için
        active_procs_per_year: dict[int, list[str]] = {}
        for (y, code) in proc_by_year_code.keys():
            active_procs_per_year.setdefault(y, []).append(code)

        total_planned = 0
        new_rows = []
        for (y, m) in months:
            procs = active_procs_per_year.get(y, [])
            for code in procs:
                kpis = kpis_by_year_process.get((y, code), [])
                if not kpis:
                    continue
                members_list = members.get(code, [])
                if not members_list:
                    continue
                count = random.randint(args.min_per_month, args.max_per_month)
                for _ in range(count):
                    kid, tv, direction, base, kcode = random.choice(kpis)
                    uid = random.choice(members_list)
                    # Actual value = baseline → target arasında lineer + noise
                    # Yıllar arası progress: (y - 2021) / 5
                    progress = max(0.0, min(1.0, (y - 2021) / 5.0))
                    span = tv - base
                    value = base + span * progress * random.uniform(0.6, 1.0)
                    # Pandemi sapması
                    if y == 2022 and code in ("P2M", "S2P"):
                        value *= 0.92 if direction == "Increasing" else 1.15
                    # Aylık noise
                    value *= random.uniform(0.93, 1.07)
                    new_rows.append({
                        "process_kpi_id": kid,
                        "year": y,
                        "data_date": date(y, m, 28),
                        "period_type": "Aylık",
                        "period_no": m,
                        "period_month": m,
                        "target_value": tv,
                        "actual_value": round(value, 2),
                        "user_id": uid,
                        "is_active": True,
                        "created_at": datetime(y, m, 28, tzinfo=timezone.utc),
                    })
                    total_planned += 1

        print()
        print(f"Plan: {len(months)} ay × ~{len(set([c for cs in active_procs_per_year.values() for c in cs]))} süreç")
        print(f"Yeni satır sayısı: {total_planned}")

        if args.dry_run:
            print("\nDRY-RUN — değişiklik yok.")
            return

        # 5) Mevcut kpi_data sil
        deleted = db.session.execute(text("""
            DELETE FROM kpi_data WHERE process_kpi_id IN (
              SELECT k.id FROM process_kpis k JOIN processes p ON k.process_id=p.id
              WHERE p.tenant_id=:t
            )
        """), {"t": tid}).rowcount
        print(f"Mevcut kpi_data silindi: {deleted}")

        # 6) Yeni satirlari bulk insert
        BATCH = 1000
        inserted = 0
        for i in range(0, len(new_rows), BATCH):
            db.session.bulk_insert_mappings(KpiData, new_rows[i:i + BATCH])
            inserted += len(new_rows[i:i + BATCH])
            if inserted % 2000 == 0 or inserted == len(new_rows):
                print(f"  insert: {inserted}/{len(new_rows)}")
        db.session.commit()
        print(f"\nTAMAM. Toplam yeni kpi_data: {inserted}")


if __name__ == "__main__":
    main()
