"""
seed_generic_tenant.py — Generic tenant seed (YAML-driven).

Inputs:
  --data    : tenant_data.yaml  (2026 baseline)
  --deltas  : year_deltas.yaml  (2021-2025 evolution)

Outputs (PostgreSQL kokpitim_db):
  Tenant + PlanYears + Strategies + SubStrategies + Processes + ProcessKpis
  Users (manuel + rule-generated bulk) + KpiData (rule-based trajectory)
  ProcessOwners + ProcessActivities + Projects + Tasks
  SWOT/TOWS/PESTEL/Porter (per year, theme-based)
  OKR (Objectives + KeyResults, per year)
  K-Vektor weights + K-Radar (Maturity, Bottleneck, ValueChain, EVM, Risk,
                              Stakeholder, StakeholderSurvey, A3, Competitor)

Usage:
  python scripts/seed_generic_tenant.py --data docs/tomofil-demo/tenant_data.yaml \
                                        --deltas docs/tomofil-demo/year_deltas.yaml \
                                        --dry-run
  python scripts/seed_generic_tenant.py --data ... --deltas ... --commit
  python scripts/seed_generic_tenant.py --data ... --deltas ... --reset --commit
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import unicodedata
from copy import deepcopy
from datetime import date, datetime, timezone
from pathlib import Path

# UTF-8 stdout
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import yaml
from werkzeug.security import generate_password_hash
from sqlalchemy import text

from app import create_app
from extensions import db
from app.models.core import Tenant, User, Strategy, SubStrategy
from app.models.process import (
    Process, ProcessKpi, KpiData,
    process_owners_table, process_leaders, process_members,
)
from app.models.plan_year import PlanYear
from app.models.swot import SwotAnalysis, TowsAnalysis, PestelAnalysis, PorterFiveForcesAnalysis
from app.models.okr import OkrObjective, OkrKeyResult
from app.models.k_vektor import KVektorStrategyWeight, KVektorSubStrategyWeight
from app.models.k_radar_domain import (
    ProcessMaturity, BottleneckLog, ValueChainItem, EvmSnapshot,
    RiskHeatmapItem, StakeholderMap, StakeholderSurvey, A3Report, CompetitorAnalysis,
)
from app.models.portfolio_project import Project, Task
from app.models.process import ProcessActivity, ProcessActivityAssignee

ROLE_TENANT_ADMIN = 3
ROLE_EXECUTIVE = 4
ROLE_STANDARD = 5
PACKAGE_ID = 1

TR_MAP = str.maketrans("ığüşöçİĞÜŞÖÇıĞ", "igusocIGUSOCiG")
random.seed(42)


def slug(s: str) -> str:
    s = (s or "").strip().lower().translate(TR_MAP)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", ".", s).strip(".")
    return s


# ---------------------------------------------------------------------------
# Year-state computation (forward chaining from 2021 to target year)
# ---------------------------------------------------------------------------
def compute_year_state(year: int, deltas: dict):
    """For a given plan year, return active strategies, sub_strategies, processes, kpi_codes."""
    state = {
        "strategies": set(),
        "sub_strategies": set(),
        "paused_subs": set(),
        "processes": set(),
        "kpi_codes": set(),
        "kpi_target_overrides": {},  # kpi_code -> target_value
        "sub_desc_overrides": {},
    }
    for y in range(2021, year + 1):
        d = deltas["years"].get(y, {})
        # 2021 has explicit active_* (kuruluş yılı)
        if "active_strategies" in d:
            state["strategies"] = set(d["active_strategies"])
            state["sub_strategies"] = set(d["active_sub_strategies"])
            state["processes"] = set(d["active_processes"])
            state["kpi_codes"] = set(d["active_kpi_codes"])
        # Add deltas
        for s in d.get("add_strategies", []) or []:
            state["strategies"].add(s)
        for s in d.get("add_sub_strategies", []) or []:
            state["sub_strategies"].add(s)
        for s in d.get("paused_sub_strategies", []) or []:
            state["paused_subs"].add(s)
        for s in d.get("remove_sub_strategies", []) or []:
            state["sub_strategies"].discard(s)
        for p in d.get("add_processes", []) or []:
            state["processes"].add(p)
        for k in d.get("add_kpi_codes", []) or []:
            state["kpi_codes"].add(k)
        for k, v in (d.get("kpi_targets_override") or {}).items():
            state["kpi_target_overrides"][k] = v.get(f"target_{y}", v)
        for k, v in (d.get("sub_strategy_description_overrides") or {}).items():
            state["sub_desc_overrides"][k] = v
    return state


# ---------------------------------------------------------------------------
# KPI data generation (rule-based trajectory)
# ---------------------------------------------------------------------------
def kpi_trajectory_value(kpi: dict, year: int):
    """Linear interpolation from baseline_2021 -> baseline_2026_actual."""
    start_year = kpi.get("start_year", 2021)
    if year < start_year:
        return None
    b21 = float(kpi.get("baseline_2021", 0) or 0)
    b26 = float(kpi.get("baseline_2026_actual", 0) or 0)
    yspan = max(2026 - start_year, 1)
    progress = (year - start_year) / yspan
    base = b21 + (b26 - b21) * progress
    # Pandemi sapması: 2022 üretim KPI'larında -%10
    if year == 2022 and kpi["process_code"] in ("P2M", "S2P"):
        if kpi.get("direction") == "Increasing":
            base = base * 0.92
        else:  # Decreasing — daha kötüye
            base = base * 1.15
    return base


def generate_kpi_data_rows(kpi: dict, year: int, kpi_id: int, plan_year_id: int, admin_id: int):
    """Generate KpiData records for a KPI in a given year with appropriate frequency."""
    val = kpi_trajectory_value(kpi, year)
    if val is None:
        return []
    rows = []
    target = float(str(kpi["target_value"]).replace(",", "."))
    # Frequency by year
    if year == 2026:
        # Aylık — Ocak-Mayıs (5 ay)
        for month in range(1, 6):
            noise = random.uniform(-0.05, 0.05) * val
            actual = round(val + noise + (month - 3) * 0.02 * val, 2)
            rows.append({
                "process_kpi_id": kpi_id,
                "year": 2026,
                "data_date": date(2026, month, 28),
                "period_type": "Aylık",
                "period_no": month,
                "period_month": month,
                "target_value": target,
                "actual_value": round(actual, 2),
                "user_id": admin_id,
                "is_active": True,
            })
    elif year in (2024, 2025):
        # Çeyreklik
        for q in range(1, 5):
            noise = random.uniform(-0.06, 0.06) * val
            actual = round(val + noise + (q - 2.5) * 0.03 * val, 2)
            rows.append({
                "process_kpi_id": kpi_id,
                "year": year,
                "data_date": date(year, q * 3, 28),
                "period_type": "Çeyreklik",
                "period_no": q,
                "period_month": q * 3,
                "target_value": target,
                "actual_value": round(actual, 2),
                "user_id": admin_id,
                "is_active": True,
            })
    else:
        # Yıllık (2021, 2022, 2023)
        noise = random.uniform(-0.04, 0.04) * val
        rows.append({
            "process_kpi_id": kpi_id,
            "year": year,
            "data_date": date(year, 12, 31),
            "period_type": "Yıllık",
            "period_no": 1,
            "period_month": 12,
            "target_value": target,
            "actual_value": round(val + noise, 2),
            "user_id": admin_id,
            "is_active": True,
        })
    return rows


# ---------------------------------------------------------------------------
# Bulk employee generation
# ---------------------------------------------------------------------------
def generate_bulk_employees(rules: dict, tenant_id: int, used_emails: set, pwd_hash: str):
    """Generate bulk_employees as User insert dicts based on departments + name pools."""
    fnames_m = rules["first_names_male"]
    fnames_f = rules["first_names_female"]
    lnames = rules["last_names"]
    female_ratio = rules.get("female_ratio", 0.22)
    hire_dist = rules["hire_year_distribution"]
    total = rules["total_bulk"]
    pwd = rules.get("password", "Tomofil2026!")

    # hire_year listesi
    hire_years = []
    for y, c in hire_dist.items():
        hire_years.extend([int(y)] * int(c))
    # Boşlukları 2026'dan doldur
    while len(hire_years) < total:
        hire_years.append(2026)
    random.shuffle(hire_years)

    rows = []
    hr_iter = iter(hire_years)
    employee_data_for_processes = []  # (email, process_codes, dept)

    for dept in rules["departments"]:
        for _ in range(dept["count"]):
            is_female = random.random() < female_ratio
            fname = random.choice(fnames_f if is_female else fnames_m)
            lname = random.choice(lnames)
            title = random.choice(dept["titles"])
            email_base = f"{slug(fname)}.{slug(lname)}"
            email = f"{email_base}@tomofil.test"
            n = 1
            while email in used_emails:
                email = f"{email_base}.{n}@tomofil.test"
                n += 1
            used_emails.add(email)
            try:
                hire_year = next(hr_iter)
            except StopIteration:
                hire_year = 2026
            rows.append({
                "email": email,
                "password_hash": pwd_hash,
                "first_name": fname[:64],
                "last_name": lname[:64],
                "is_active": True,
                "tenant_id": tenant_id,
                "role_id": ROLE_EXECUTIVE if dept.get("role") == "executive_manager" else ROLE_STANDARD,
                "job_title": title[:100],
                "department": dept["name"][:100],
                "layout_preference": "classic",
                "show_page_guides": True,
                "guide_character_style": "professional",
                "created_at": datetime(hire_year, random.randint(1, 12), random.randint(1, 28), tzinfo=timezone.utc),
            })
            employee_data_for_processes.append((email, dept["name"]))
    return rows, employee_data_for_processes


# ---------------------------------------------------------------------------
# Reset existing tenant fully
# ---------------------------------------------------------------------------
def reset_tenant(name: str, short_name: str):
    """Mevcut tenant'ı tüm bağlı kayıtlarla birlikte siler.

    Sıra ÖNEMLİ — FK kısıtları nedeniyle alt-katman önce silinmeli.
    try/except kullanılmaz; her hata transaction'ı bozar ve rollback dışta yapılır.
    """
    t = db.session.query(Tenant).filter(
        (Tenant.name == name) | (Tenant.short_name == short_name)
    ).first()
    if not t:
        return False
    tid = t.id
    print(f"  [reset] Mevcut tenant id={tid} ve TÜM bağlı kayıtlar siliniyor...")
    # Sırayla — FK katmanlarına saygıyla
    delete_queries = [
        # 1) Audit + user-bound
        "DELETE FROM audit_logs WHERE user_id IN (SELECT id FROM users WHERE tenant_id=:t)",
        # 2) KPI data (process_kpis'e bağlı)
        "DELETE FROM kpi_data WHERE process_kpi_id IN (SELECT k.id FROM process_kpis k JOIN processes p ON k.process_id=p.id WHERE p.tenant_id=:t)",
        # 3) Process-bound m2m + faaliyetler
        "DELETE FROM process_owners_table WHERE process_id IN (SELECT id FROM processes WHERE tenant_id=:t)",
        "DELETE FROM process_leaders WHERE process_id IN (SELECT id FROM processes WHERE tenant_id=:t)",
        "DELETE FROM process_members WHERE process_id IN (SELECT id FROM processes WHERE tenant_id=:t)",
        "DELETE FROM process_activity_assignees WHERE activity_id IN (SELECT a.id FROM process_activities a JOIN processes p ON a.process_id=p.id WHERE p.tenant_id=:t)",
        "DELETE FROM process_activities WHERE process_id IN (SELECT id FROM processes WHERE tenant_id=:t)",
        # 4) Process'e bağlı K-Radar
        "DELETE FROM bottleneck_log WHERE process_id IN (SELECT id FROM processes WHERE tenant_id=:t) OR tenant_id=:t",
        "DELETE FROM process_maturity WHERE process_id IN (SELECT id FROM processes WHERE tenant_id=:t) OR tenant_id=:t",
        "DELETE FROM value_chain_items WHERE linked_process_id IN (SELECT id FROM processes WHERE tenant_id=:t) OR tenant_id=:t",
        # 5) K-Vektor
        "DELETE FROM k_vektor_strategy_weights WHERE tenant_id=:t",
        "DELETE FROM k_vektor_sub_strategy_weights WHERE tenant_id=:t",
        # 6) Process kpis + processes
        "DELETE FROM process_kpis WHERE process_id IN (SELECT id FROM processes WHERE tenant_id=:t)",
        "DELETE FROM processes WHERE tenant_id=:t",
        # 7) Strateji
        "DELETE FROM sub_strategies WHERE strategy_id IN (SELECT id FROM strategies WHERE tenant_id=:t)",
        "DELETE FROM strategies WHERE tenant_id=:t",
        # 8) K-Radar diğer + analizler
        "DELETE FROM evm_snapshots WHERE tenant_id=:t",
        "DELETE FROM risk_heatmap_items WHERE tenant_id=:t",
        "DELETE FROM stakeholder_maps WHERE tenant_id=:t",
        "DELETE FROM stakeholder_surveys WHERE tenant_id=:t",
        "DELETE FROM a3_reports WHERE tenant_id=:t",
        "DELETE FROM competitor_analyses WHERE tenant_id=:t",
        "DELETE FROM swot_analyses WHERE tenant_id=:t",
        "DELETE FROM tows_analyses WHERE tenant_id=:t",
        "DELETE FROM pestel_analyses WHERE tenant_id=:t",
        "DELETE FROM porter_analyses WHERE tenant_id=:t",
        # 9) OKR (tablo varsa)
        "DELETE FROM okr_key_results WHERE objective_id IN (SELECT id FROM okr_objectives WHERE tenant_id=:t)",
        "DELETE FROM okr_objectives WHERE tenant_id=:t",
        # 10) Proje
        "DELETE FROM task WHERE project_id IN (SELECT id FROM project WHERE tenant_id=:t)",
        "DELETE FROM project WHERE tenant_id=:t",
        # 11) Plan year + user + tenant
        "DELETE FROM plan_years WHERE tenant_id=:t",
        "UPDATE tenants SET package_id=NULL WHERE id=:t",
        "DELETE FROM users WHERE tenant_id=:t",
        "DELETE FROM tenants WHERE id=:t",
    ]
    for q in delete_queries:
        n = db.session.execute(text(q), {"t": tid}).rowcount
        if n:
            print(f"    -{n}: {q[:60]}")
    db.session.flush()
    print(f"  [reset] tenant_id={tid} temizlendi.")
    return True


# ---------------------------------------------------------------------------
# Main seed
# ---------------------------------------------------------------------------
def seed(args):
    data_path = Path(args.data)
    deltas_path = Path(args.deltas)
    if not data_path.exists() or not deltas_path.exists():
        sys.exit(f"HATA: data veya deltas dosyası yok.\n  data:   {data_path}\n  deltas: {deltas_path}")

    data = yaml.safe_load(data_path.read_text(encoding="utf-8"))
    deltas = yaml.safe_load(deltas_path.read_text(encoding="utf-8"))

    print("=" * 76)
    print(f"  GENERIC TENANT SEED — mod: {'DRY-RUN' if args.dry_run else 'COMMIT'}")
    print(f"  Tenant: {data['tenant']['name']}")
    print(f"  Plan years: {[p['year'] for p in data['plan_years']]}")
    print(f"  Strategies (2026): {len(data['strategies'])}")
    print(f"  Processes (2026):  {len(data['processes'])}")
    print(f"  KPIs (2026):       {len(data['process_kpis'])}")
    print(f"  Manuel users:      {len(data['users'])}")
    print(f"  Bulk employees:    {data['employees_generation']['total_bulk']}")
    print("=" * 76)

    # 0) Reset
    if args.reset:
        reset_tenant(data["tenant"]["name"], data["tenant"]["short_name"])
    elif db.session.query(Tenant).filter(
        (Tenant.name == data["tenant"]["name"]) | (Tenant.short_name == data["tenant"]["short_name"])
    ).first():
        sys.exit(f"HATA: Tenant '{data['tenant']['short_name']}' zaten var. --reset ile sil.")

    # 1) Tenant
    t = data["tenant"]
    tenant = Tenant(
        name=t["name"],
        short_name=t.get("short_name"),
        is_active=True,
        package_id=t.get("package_id", PACKAGE_ID),
        sector=t.get("sector"),
        activity_area=t.get("activity_area"),
        employee_count=t.get("employee_count"),
        contact_email=t.get("contact_email"),
        phone_number=t.get("phone_number"),
        website_url=t.get("website_url"),
        tax_office=t.get("tax_office"),
        tax_number=t.get("tax_number"),
        max_user_count=t.get("max_user_count", 500),
        license_end_date=date.fromisoformat(t["license_end_date"]) if t.get("license_end_date") else None,
        vision=t.get("vision"),
        purpose=t.get("purpose"),
        core_values=t.get("core_values"),
        code_of_ethics=t.get("code_of_ethics"),
        quality_policy=t.get("quality_policy"),
        plan_year_enabled=t.get("plan_year_enabled", True),
        plan_year_start=t.get("plan_year_start"),
        k_vektor_enabled=t.get("k_vektor_enabled", False),
        k_radar_enabled=t.get("k_radar_enabled", False),
    )
    db.session.add(tenant)
    db.session.flush()
    print(f"  [OK] Tenant id={tenant.id}")

    # 2) Plan years
    plan_year_by_year = {}
    for py in data["plan_years"]:
        pyr = PlanYear(
            tenant_id=tenant.id,
            year=py["year"],
            name=py.get("name"),
            status=py.get("status", "draft"),
            closed_at=datetime(py["year"], 12, 31, tzinfo=timezone.utc) if py.get("status") == "closed" else None,
        )
        db.session.add(pyr)
        plan_year_by_year[py["year"]] = pyr
    db.session.flush()
    print(f"  [OK] {len(plan_year_by_year)} PlanYear")

    # 3) Admin
    pwd_hash = generate_password_hash(data["admin"]["password"])
    admin = User(
        email=data["admin"]["email"],
        password_hash=pwd_hash,
        first_name=data["admin"]["first_name"],
        last_name=data["admin"]["last_name"],
        is_active=True,
        tenant_id=tenant.id,
        role_id=ROLE_TENANT_ADMIN,
        job_title=data["admin"].get("job_title"),
        department=data["admin"].get("department"),
        phone_number=data["admin"].get("phone_number"),
    )
    db.session.add(admin)
    db.session.flush()
    used_emails = {admin.email}
    print(f"  [OK] Admin {admin.email}")

    # 4) Manual users
    user_pwd_hash = generate_password_hash(data["employees_generation"].get("password", "Tomofil2026!"))
    email_to_uid = {}
    manual_user_process_map = {}  # email -> list[process_code]
    for u in data["users"]:
        used_emails.add(u["email"])
        usr = User(
            email=u["email"],
            password_hash=user_pwd_hash,
            first_name=u["first_name"],
            last_name=u["last_name"],
            is_active=True,
            tenant_id=tenant.id,
            role_id=ROLE_EXECUTIVE if u.get("role") == "executive_manager" else ROLE_STANDARD,
            job_title=u.get("job_title"),
            department=u.get("department"),
            created_at=datetime(u.get("hire_year", 2021), 6, 15, tzinfo=timezone.utc),
        )
        db.session.add(usr)
        manual_user_process_map[u["email"]] = u.get("process_codes", []) or []
    db.session.flush()
    # email -> id
    for r in db.session.execute(text(
        "SELECT id, email FROM users WHERE tenant_id=:t"
    ), {"t": tenant.id}).fetchall():
        email_to_uid[r[1]] = r[0]
    print(f"  [OK] {len(data['users'])} manuel kullanıcı")

    # 5) Bulk users
    bulk_rows, bulk_dept_emails = generate_bulk_employees(
        data["employees_generation"], tenant.id, used_emails, user_pwd_hash
    )
    db.session.bulk_insert_mappings(User, bulk_rows)
    db.session.flush()
    # refresh email map
    for r in db.session.execute(text(
        "SELECT id, email FROM users WHERE tenant_id=:t"
    ), {"t": tenant.id}).fetchall():
        email_to_uid[r[1]] = r[0]
    print(f"  [OK] {len(bulk_rows)} toplu çalışan")

    # 6) Stratejiler + Alt stratejiler — her yıl için ayrı kayıt
    # Yapı: 2026 baseline + year_deltas ile her yıl için aktif set hesapla
    sub_2026_by_code = {}
    for s in data["strategies"]:
        for ss in s.get("sub_strategies", []) or []:
            sub_2026_by_code[ss["code"]] = ss
    strat_2026_by_code = {s["code"]: s for s in data["strategies"]}

    strategy_id_by_year_code = {}    # (year, code) -> Strategy.id
    sub_id_by_year_code = {}         # (year, code) -> SubStrategy.id

    for year, pyr in plan_year_by_year.items():
        if year not in deltas["years"]:
            continue
        state = compute_year_state(year, deltas)
        # Strategies for year
        for h_code in sorted(state["strategies"]):
            base = strat_2026_by_code.get(h_code)
            if not base:
                continue
            prev = strategy_id_by_year_code.get((year - 1, h_code))
            sobj = Strategy(
                tenant_id=tenant.id,
                code=h_code,
                title=base["title"],
                description=base.get("description"),
                is_active=True,
                plan_year_id=pyr.id,
                source_strategy_id=prev,
            )
            db.session.add(sobj)
            db.session.flush()
            strategy_id_by_year_code[(year, h_code)] = sobj.id
        # SubStrategies for year (active + paused)
        all_subs = state["sub_strategies"] | state["paused_subs"]
        for ss_code in sorted(all_subs):
            base = sub_2026_by_code.get(ss_code)
            if not base:
                continue
            # Parent H code = ilk karakter (ör: 1.A.1 -> H1)
            parent_h = "H" + ss_code.split(".")[0]
            strat_id = strategy_id_by_year_code.get((year, parent_h))
            if not strat_id:
                continue
            desc = state["sub_desc_overrides"].get(ss_code, base.get("description"))
            prev = sub_id_by_year_code.get((year - 1, ss_code))
            sobj = SubStrategy(
                strategy_id=strat_id,
                code=ss_code,
                title=base["title"],
                description=desc,
                is_active=(ss_code not in state["paused_subs"]),
                plan_year_id=pyr.id,
                source_sub_strategy_id=prev,
            )
            db.session.add(sobj)
            db.session.flush()
            sub_id_by_year_code[(year, ss_code)] = sobj.id
    print(f"  [OK] Stratejiler + alt stratejiler (yıl bazlı)")

    # 7) Süreçler — her yıl için
    process_by_code_2026 = {p["code"]: p for p in data["processes"]}
    process_id_by_year_code = {}
    for year, pyr in plan_year_by_year.items():
        if year not in deltas["years"]:
            continue
        state = compute_year_state(year, deltas)
        for p_code in sorted(state["processes"]):
            base = process_by_code_2026.get(p_code)
            if not base:
                continue
            prev = process_id_by_year_code.get((year - 1, p_code))
            pobj = Process(
                tenant_id=tenant.id,
                code=p_code,
                name=base["name"],
                english_name=base.get("english_name"),
                weight=base.get("weight"),
                description=base.get("description"),
                status="Aktif",
                is_active=True,
                plan_year_id=pyr.id,
                source_process_id=prev,
            )
            db.session.add(pobj)
            db.session.flush()
            process_id_by_year_code[(year, p_code)] = pobj.id
    print(f"  [OK] Süreçler (yıl bazlı)")

    # 8) ProcessKpis — her yıl için
    kpi_2026_by_code = {k["code"]: k for k in data["process_kpis"]}
    kpi_id_by_year_code = {}
    for year, pyr in plan_year_by_year.items():
        if year not in deltas["years"]:
            continue
        state = compute_year_state(year, deltas)
        for k_code in sorted(state["kpi_codes"]):
            base = kpi_2026_by_code.get(k_code)
            if not base:
                continue
            p_id = process_id_by_year_code.get((year, base["process_code"]))
            if not p_id:
                continue
            ss_id = None
            if base.get("linked_sub_strategy_code"):
                ss_id = sub_id_by_year_code.get((year, base["linked_sub_strategy_code"]))
            target = state["kpi_target_overrides"].get(k_code, base["target_value"])
            prev = kpi_id_by_year_code.get((year - 1, k_code))
            kobj = ProcessKpi(
                process_id=p_id,
                name=base["name"],
                description=base.get("description"),
                code=k_code,
                target_value=str(target),
                unit=base.get("unit"),
                period=base.get("period", "Aylık"),
                direction=base.get("direction", "Increasing"),
                weight=base.get("weight"),
                is_important=base.get("is_important", False),
                gosterge_turu=base.get("gosterge_turu"),
                target_method=base.get("target_method"),
                onceki_yil_ortalamasi=base.get("baseline_2021"),
                is_active=True,
                sub_strategy_id=ss_id,
                plan_year_id=pyr.id,
                source_kpi_id=prev,
            )
            db.session.add(kobj)
            db.session.flush()
            kpi_id_by_year_code[(year, k_code)] = kobj.id
    print(f"  [OK] Process KPI'ları (yıl bazlı)")

    # 9) KPI data — karma sıklık
    kpi_data_rows = []
    for (year, k_code), kpi_id in kpi_id_by_year_code.items():
        base = kpi_2026_by_code[k_code]
        rows = generate_kpi_data_rows({**base, "process_code": base["process_code"]}, year, kpi_id, plan_year_by_year[year].id, admin.id)
        kpi_data_rows.extend(rows)
    if kpi_data_rows:
        db.session.bulk_insert_mappings(KpiData, kpi_data_rows)
        db.session.flush()
    print(f"  [OK] {len(kpi_data_rows)} KpiData satırı")

    # 10) Process owners (sadece 2026)
    for p in data["processes"]:
        p_id = process_id_by_year_code.get((2026, p["code"]))
        owner_email = p.get("owner_email")
        if p_id and owner_email and owner_email in email_to_uid:
            uid = email_to_uid[owner_email]
            db.session.execute(process_owners_table.insert().values(process_id=p_id, user_id=uid))
            db.session.execute(process_leaders.insert().values(process_id=p_id, user_id=uid))
    # Manuel kullanıcıların ek atamaları (members)
    for email, codes in manual_user_process_map.items():
        uid = email_to_uid.get(email)
        if not uid:
            continue
        for c in codes:
            p_id = process_id_by_year_code.get((2026, c))
            if p_id:
                try:
                    db.session.execute(process_members.insert().values(process_id=p_id, user_id=uid))
                except Exception:
                    pass
    db.session.flush()
    print(f"  [OK] Process owners + leaders + members")

    # 11) K-Vektor (2026)
    kv = data.get("k_vektor_weights", {})
    for s in kv.get("strategies", []) or []:
        sid = strategy_id_by_year_code.get((2026, s["code"]))
        if sid:
            db.session.add(KVektorStrategyWeight(tenant_id=tenant.id, strategy_id=sid, weight_raw=s["weight"]))
    for s in kv.get("sub_strategies", []) or []:
        ssid = sub_id_by_year_code.get((2026, s["code"]))
        if ssid:
            db.session.add(KVektorSubStrategyWeight(tenant_id=tenant.id, sub_strategy_id=ssid, weight_raw=s["weight"]))
    db.session.flush()
    print(f"  [OK] K-Vektor ağırlıkları")

    # 12) K-Radar
    for pm in data.get("process_maturity", []) or []:
        pid = process_id_by_year_code.get((2026, pm["process_code"]))
        aid = email_to_uid.get(pm.get("assessor_email"))
        if pid:
            db.session.add(ProcessMaturity(
                tenant_id=tenant.id, process_id=pid,
                maturity_level=pm["maturity_level"], dimension=pm.get("dimension"),
                assessed_by=aid, assessed_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
            ))
    for bl in data.get("bottlenecks", []) or []:
        pid = process_id_by_year_code.get((2026, bl["process_code"]))
        kid = kpi_id_by_year_code.get((2026, bl.get("kpi_code"))) if bl.get("kpi_code") else None
        if pid:
            db.session.add(BottleneckLog(
                tenant_id=tenant.id, process_id=pid, kpi_id=kid,
                severity=bl.get("severity"), note=bl.get("note"),
                triggered_at=datetime.fromisoformat(bl["triggered_at"]) if bl.get("triggered_at") else None,
            ))
    for vc in data.get("value_chain", []) or []:
        pid = process_id_by_year_code.get((2026, vc.get("linked_process_code"))) if vc.get("linked_process_code") else None
        db.session.add(ValueChainItem(
            tenant_id=tenant.id, category=vc["category"], linked_process_id=pid,
            muda_type=vc.get("muda_type"), title=vc["title"], note=vc.get("note"),
        ))
    project_id_by_name = {}  # populated below
    risk_rows = data.get("risks", []) or []
    stakeholder_rows = data.get("stakeholders", []) or []
    survey_rows = data.get("stakeholder_surveys", []) or []
    a3_rows = data.get("a3_reports", []) or []
    competitor_rows = data.get("competitors", []) or []
    print(f"  [OK] K-Radar maturity + bottleneck + value chain")

    # 13) Projects + Tasks — raw SQL (ORM şema sapması var)
    for proj in data.get("projects", []) or []:
        mgr = email_to_uid.get(proj.get("manager_email"))
        result = db.session.execute(text("""
            INSERT INTO project (tenant_id, name, description, manager_id, start_date, end_date,
                                 priority, health_status, is_archived, created_at, updated_at)
            VALUES (:t, :n, :d, :m, :sd, :ed, :p, :hs, false, NOW(), NOW())
            RETURNING id
        """), {
            "t": tenant.id, "n": proj["name"], "d": proj.get("description"),
            "m": mgr,
            "sd": date.fromisoformat(proj["start_date"]) if proj.get("start_date") else None,
            "ed": date.fromisoformat(proj["end_date"]) if proj.get("end_date") else None,
            "p": proj.get("priority"), "hs": proj.get("health_status"),
        })
        pid = result.scalar()
        project_id_by_name[proj["name"]] = pid
        for tk in proj.get("tasks", []) or []:
            asg = email_to_uid.get(tk.get("assignee_email"))
            db.session.execute(text("""
                INSERT INTO task (project_id, title, description, assignee_id, reporter_id, start_date, due_date,
                                  status, priority, is_archived, created_at)
                VALUES (:p, :t, :d, :a, :r, :sd, :dd, :s, :pr, false, NOW())
            """), {
                "p": pid, "t": tk["title"], "d": tk.get("description"),
                "a": asg, "r": mgr or admin.id,
                "sd": date.fromisoformat(tk["start_date"]) if tk.get("start_date") else None,
                "dd": date.fromisoformat(tk["end_date"]) if tk.get("end_date") else None,
                "s": tk.get("status", "Yapılacak"), "pr": tk.get("priority", "Medium"),
            })
    db.session.flush()
    print(f"  [OK] {len(data.get('projects', []))} proje + görevler")

    # 14) EVM (projeye bağlı)
    for ev in data.get("evm_snapshots", []) or []:
        pid = project_id_by_name.get(ev["project_name"])
        if pid:
            db.session.add(EvmSnapshot(
                tenant_id=tenant.id, project_id=pid,
                snapshot_date=date.fromisoformat(ev["snapshot_date"]),
                pv=ev.get("pv"), ev=ev.get("ev"), ac=ev.get("ac"),
                spi=ev.get("spi"), cpi=ev.get("cpi"),
            ))
    # 15) Riskler
    py_2026 = plan_year_by_year[2026]
    for rk in risk_rows:
        owner = email_to_uid.get(rk.get("owner_email"))
        db.session.add(RiskHeatmapItem(
            tenant_id=tenant.id, plan_year_id=py_2026.id,
            title=rk["title"], probability=rk["probability"], impact=rk["impact"],
            rpn=rk["probability"] * rk["impact"],
            owner_id=owner, status=rk.get("status"), source_type=rk.get("source_type"),
        ))
    # 16) Paydaşlar
    for sk in stakeholder_rows:
        db.session.add(StakeholderMap(
            tenant_id=tenant.id, plan_year_id=py_2026.id,
            name=sk["name"], role=sk.get("role"),
            influence=sk.get("influence"), interest=sk.get("interest"),
            strategy=sk.get("strategy"),
        ))
    for sv in survey_rows:
        db.session.add(StakeholderSurvey(
            tenant_id=tenant.id,
            stakeholder_type=sv["stakeholder_type"], period=sv.get("period"),
            score=sv.get("score"), comment=sv.get("comment"), source=sv.get("source"),
        ))
    # 17) A3 + Competitors
    for a3 in a3_rows:
        db.session.add(A3Report(
            tenant_id=tenant.id, source_type=a3.get("source_type"),
            problem=a3.get("problem"), root_cause_json=a3.get("root_cause_json"),
            countermeasures=a3.get("countermeasures"),
        ))
    for cp in competitor_rows:
        db.session.add(CompetitorAnalysis(
            tenant_id=tenant.id, plan_year_id=py_2026.id,
            competitor_name=cp["competitor_name"], dimension=cp.get("dimension"),
            our_score=cp.get("our_score"), their_score=cp.get("their_score"),
        ))
    db.session.flush()
    print(f"  [OK] K-Radar: risks + stakeholders + surveys + a3 + competitors")

    # 18) SWOT/TOWS/PESTEL/Porter — 2026 detaylı, geri yıllar tema-bazlı
    themes = data.get("analyses_year_themes", {}) or {}
    for year, pyr in plan_year_by_year.items():
        if year == 2027:
            continue
        if year == 2026:
            sw = data.get("swot_2026", {})
            db.session.add(SwotAnalysis(
                plan_year_id=pyr.id, tenant_id=tenant.id,
                strengths=sw.get("strengths"), weaknesses=sw.get("weaknesses"),
                opportunities=sw.get("opportunities"), threats=sw.get("threats"),
            ))
        else:
            t_str = themes.get(year, "")
            db.session.add(SwotAnalysis(
                plan_year_id=pyr.id, tenant_id=tenant.id,
                strengths=f"[{year} özet] " + t_str[:500],
                weaknesses=f"[{year} özet] " + t_str[:500],
                opportunities=f"[{year} özet] " + t_str[:500],
                threats=f"[{year} özet] " + t_str[:500],
            ))
        # TOWS / PESTEL / Porter — placeholder per year
        db.session.add(TowsAnalysis(
            plan_year_id=pyr.id, tenant_id=tenant.id,
            so_strategies=f"[{year}] Güçlü+Fırsat",
            st_strategies=f"[{year}] Güçlü+Tehdit",
            wo_strategies=f"[{year}] Zayıf+Fırsat",
            wt_strategies=f"[{year}] Zayıf+Tehdit",
        ))
        db.session.add(PestelAnalysis(
            plan_year_id=pyr.id, tenant_id=tenant.id,
            political=f"[{year}] Siyasi", economic=f"[{year}] Ekonomik",
            social=f"[{year}] Sosyal", technological=f"[{year}] Teknolojik",
            environmental=f"[{year}] Çevresel", legal=f"[{year}] Yasal",
        ))
        db.session.add(PorterFiveForcesAnalysis(
            plan_year_id=pyr.id, tenant_id=tenant.id,
            rivalry_intensity=f"[{year}] Rekabet",
            supplier_power=f"[{year}] Tedarikçi",
            buyer_power=f"[{year}] Alıcı",
            new_entrant_threat=f"[{year}] Yeni giriş",
            substitute_threat=f"[{year}] İkame",
        ))
    db.session.flush()
    print(f"  [OK] SWOT/TOWS/PESTEL/Porter (her yıl için)")

    # 19) OKRs — 2026 detaylı, geri yıllar tema-bazlı
    # OKR tabloları henüz migrate edilmediyse atla
    from sqlalchemy import inspect as _insp
    _tables = set(_insp(db.engine).get_table_names())
    if "okr_objectives" not in _tables:
        print(f"  [skip] OKR tabloları yok — atlandı")
        okr_themes = {}
        skip_okr = True
    else:
        okr_themes = deltas.get("okr_themes", {}) or {}
        skip_okr = False
    _okr_iter = [] if skip_okr else plan_year_by_year.items()
    for year, pyr in _okr_iter:
        if year == 2027:
            continue
        if year == 2026:
            for obj in data.get("okrs_2026", []) or []:
                oo = OkrObjective(
                    tenant_id=tenant.id, plan_year_id=pyr.id,
                    title=obj["title"], owner=obj.get("owner"),
                )
                db.session.add(oo)
                db.session.flush()
                for kr in obj.get("key_results", []) or []:
                    db.session.add(OkrKeyResult(
                        objective_id=oo.id,
                        title=kr["title"], metric=kr.get("metric"),
                        start_value=kr.get("start_value"),
                        target_value=kr.get("target_value"),
                        current_value=kr.get("current_value"),
                    ))
        else:
            for obj in okr_themes.get(year, []) or []:
                oo = OkrObjective(
                    tenant_id=tenant.id, plan_year_id=pyr.id,
                    title=obj["title"], owner=obj.get("owner"),
                )
                db.session.add(oo)
                db.session.flush()
                # Generic 2 KR per theme objective
                for i in range(2):
                    db.session.add(OkrKeyResult(
                        objective_id=oo.id,
                        title=f"KR-{i+1}: {obj['title'][:80]}",
                        metric="%", start_value=0, target_value=100,
                        current_value=80 if year < 2026 else 50,
                    ))
    db.session.flush()
    print(f"  [OK] OKR'lar (her yıl)")

    # 20) Process activities (tüm yıllar için — date'e göre)
    for act in data.get("process_activities", []) or []:
        # Activity'nin başlangıç yılına ait süreç kaydını kullan
        start_dt = date.fromisoformat(act["start_date"]) if act.get("start_date") else date(2026, 1, 1)
        year = start_dt.year
        pid = process_id_by_year_code.get((year, act["process_code"]))
        if not pid:
            # 2026'ya düş
            pid = process_id_by_year_code.get((2026, act["process_code"]))
        if not pid:
            continue
        kpi_id = None
        if act.get("linked_kpi_code"):
            kpi_id = kpi_id_by_year_code.get((year, act["linked_kpi_code"])) or \
                     kpi_id_by_year_code.get((2026, act["linked_kpi_code"]))
        aobj = ProcessActivity(
            process_id=pid, process_kpi_id=kpi_id,
            name=act["name"], description=act.get("description"),
            start_date=start_dt,
            end_date=date.fromisoformat(act["end_date"]) if act.get("end_date") else None,
            status=act.get("status", "Planlandı"),
            progress=act.get("progress", 0),
            plan_year_id=plan_year_by_year.get(year, py_2026).id if year in plan_year_by_year else py_2026.id,
        )
        db.session.add(aobj)
        db.session.flush()
        for em in act.get("assignee_emails", []) or []:
            uid = email_to_uid.get(em)
            if uid:
                db.session.add(ProcessActivityAssignee(activity_id=aobj.id, user_id=uid))
    db.session.flush()
    print(f"  [OK] Process activities")

    print()
    print("=" * 76)
    if args.dry_run:
        db.session.rollback()
        print("  DRY-RUN: tüm INSERT'ler GERİ ALINDI.")
    else:
        db.session.commit()
        print(f"  COMMIT: tenant_id={tenant.id} kaydedildi.")
        print(f"  Login : {data['admin']['email']} / {data['admin']['password']}")
    print("=" * 76)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="tenant_data.yaml yolu")
    ap.add_argument("--deltas", required=True, help="year_deltas.yaml yolu")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--reset", action="store_true")
    args = ap.parse_args()
    if not (args.dry_run or args.commit):
        ap.error("--dry-run veya --commit gerekli")

    app = create_app()
    with app.app_context():
        try:
            seed(args)
        except Exception:
            db.session.rollback()
            raise


if __name__ == "__main__":
    main()
