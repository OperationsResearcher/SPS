"""
seed_tomofil_full.py — Tomofil Group N.V. tenant seed (Phase 1).

Kaynak dosyalar:
  docs/tomofil/Tomofil_Strateji_Agaci.md
  docs/tomofil/Tomofil_Calisanlar.json

Phase 1 kapsam (tek transaction):
  - Tenant + tenant_admin user
  - PlanYear 2026-2035 (2026 active)
  - 14 Process (A2R, C2L, P2M, ...)
  - 6 Strategy (H1-H6)
  - 73 SubStrategy (18 L1 + 55 L2, kod prefix ile hiyerarsi)
  - ~3800 User (JSON'daki tum calisanlar)
  - Process owners (her surece o sureci yoneten ilk "Yonetici")
  - Strateji agacindan parse edilen ProcessKpi'lar

Kullanim:
  python scripts/seed_tomofil_full.py --dry-run   # rapor, INSERT yok
  python scripts/seed_tomofil_full.py --commit    # gercek seed
  python scripts/seed_tomofil_full.py --reset --commit  # tenant varsa once sil
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

# UTF-8 stdout (Windows console cp1254 sorunu icin)
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Proje koku
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from werkzeug.security import generate_password_hash
from sqlalchemy import text

from app import create_app
from extensions import db
from app.models.core import Tenant, User, Role, Strategy, SubStrategy
from app.models.process import Process, ProcessKpi, process_owners_table, process_leaders
from app.models.plan_year import PlanYear

DOCS_DIR = ROOT / "docs" / "tomofil"
MD_PATH = DOCS_DIR / "Tomofil_Strateji_Agaci.md"
EMP_PATH = DOCS_DIR / "Tomofil_Calisanlar.json"

TENANT_NAME = "Tomofil Group N.V."
TENANT_SHORT = "Tomofil"
ADMIN_EMAIL = "admin@tomofil.test"
DEFAULT_PASSWORD = "Tomofil2026!"
PACKAGE_ID = 1  # Master Package
ROLE_TENANT_ADMIN = 3
ROLE_EXECUTIVE = 4
ROLE_STANDARD = 5

PLAN_YEARS = list(range(2026, 2036))  # 2026-2035

# 14 surec — kod, TR ad, EN ad
PROCESS_DEFS = [
    ("A2R", "Musteri Edinme ve Tutma",     "Acquire-to-Retain"),
    ("C2L", "Konsept'ten Lansmana",        "Concept-to-Launch"),
    ("P2M", "Planlama'dan Uretime",        "Plan-to-Manufacture"),
    ("S2P", "Tedarik'ten Odemeye",         "Source-to-Pay"),
    ("O2C", "Siparis'ten Nakite",          "Order-to-Cash"),
    ("I2R", "Sorun'dan Cozume",            "Issue-to-Resolution"),
    ("F2D", "Tahmin'den Teslime",          "Forecast-to-Deliver"),
    ("B2R", "Bataryadan Geri Donusume",    "Battery-to-Recycle"),
    ("R2M", "Risk'ten Azaltmaya",          "Risk-to-Mitigation"),
    ("H2R", "Ise Alim'dan Emekligine",     "Hire-to-Retire"),
    ("S2E", "Strateji'den Icraya",         "Strategy-to-Execution"),
    ("D2I", "Veri'den Icgoruye",           "Data-to-Insight"),
    ("R2R", "Kayit'tan Raporlamaya",       "Record-to-Report"),
    ("W2R", "Garanti'den Onarima",         "Warranty-to-Repair"),
]

# Turkce karakter -> ASCII (slug icin)
TR_MAP = str.maketrans("ığüşöçİĞÜŞÖÇıĞ", "igusocIGUSOCiG")


def slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = s.translate(TR_MAP)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", ".", s).strip(".")
    return s


# ---------------------------------------------------------------------------
# Strateji agaci parser
# ---------------------------------------------------------------------------
H_RE = re.compile(r"^# H(\d)\s+.\s+(.+)$", re.M)
L1_RE = re.compile(r"^## .*?(\d\.[A-Z])\s+(.+)$", re.M)
L2_RE = re.compile(r"^### .*?(\d\.[A-Z]\.\d)\s+(.+)$", re.M)
ACIK_RE = re.compile(r"\*\*Aciklama:?\*\*|\*\*A[çc]?[ıi]?klama:?\*\*\s*(.*)")
SUREC_RE = re.compile(r"\*\*S[üu]?re[çc]?ler:?\*\*\s*(.*)")
KPI_LINE_RE = re.compile(r"^\s*-\s+([A-Z0-9]{3,5}):\s+(.+?):\s+(.+)$")
OKR_LINE_RE = re.compile(r"^\s*-\s+(OKR\d+\.\d+)\s+—\s+(.+?):\s+(.+)$")


def parse_strategy_tree(md_text: str):
    """
    md -> {
        H: [(num, title)],
        L1: [(code, title, parent_h)],
        L2: [(code, title, parent_l1, body_text)],
        kpis_per_l2: { 'X.Y.Z': [(surec_code, kpi_name, target_text)] }
    }
    """
    h_list = [(n, t.strip()) for n, t in H_RE.findall(md_text)]
    l1_list = [(c, t.strip(), c[0]) for c, t in L1_RE.findall(md_text)]
    l2_raw = list(L2_RE.finditer(md_text))
    l2_list = []
    kpis_per_l2 = {}

    # Her L2'nin govdesi = bir sonraki ### / ## / # baslangicina kadar
    for i, m in enumerate(l2_raw):
        code = m.group(1)
        title = m.group(2).strip()
        start = m.end()
        end = l2_raw[i + 1].start() if i + 1 < len(l2_raw) else len(md_text)
        # Bir sonraki ## veya # daha onceyse onu kullan
        next_section = re.search(r"\n##? [^#]", md_text[start:end])
        if next_section:
            end = start + next_section.start()
        body = md_text[start:end]

        parent_l1 = ".".join(code.split(".")[:2])
        l2_list.append((code, title, parent_l1, body.strip()))

        # KPI satirlari (hem OKR hem surec KPI)
        kpis = []
        for line in body.splitlines():
            m_okr = OKR_LINE_RE.match(line)
            if m_okr:
                kpis.append(("OKR", m_okr.group(1), m_okr.group(2).strip(), m_okr.group(3).strip()))
                continue
            m_pg = KPI_LINE_RE.match(line)
            if m_pg:
                surec_code = m_pg.group(1).strip()
                if surec_code in {p[0] for p in PROCESS_DEFS}:
                    kpis.append((surec_code, m_pg.group(2).strip(), m_pg.group(2).strip(), m_pg.group(3).strip()))
        kpis_per_l2[code] = kpis

    return {"H": h_list, "L1": l1_list, "L2": l2_list, "kpis": kpis_per_l2}


# ---------------------------------------------------------------------------
# Seed
# ---------------------------------------------------------------------------
def find_existing_tenant():
    return db.session.query(Tenant).filter(
        (Tenant.name == TENANT_NAME) | (Tenant.short_name == TENANT_SHORT)
    ).first()


def reset_tenant(t: Tenant):
    """Tomofil tenant ve bagli tum verileri sil."""
    print(f"  [RESET] tenant_id={t.id} ve bagli kayitlar siliniyor...")
    tid = t.id
    # FK ondelete=CASCADE/SET NULL set up; ama ozellikle yardimci tablolari temizle
    # Siralama: KpiData -> ProcessKpi -> Process -> SubStrategy -> Strategy -> PlanYear -> User -> Tenant
    db.session.execute(text("""
        DELETE FROM kpi_data WHERE process_kpi_id IN (
            SELECT k.id FROM process_kpis k
            JOIN processes p ON k.process_id = p.id
            WHERE p.tenant_id = :tid
        )
    """), {"tid": tid})
    db.session.execute(text("DELETE FROM process_owners_table WHERE process_id IN (SELECT id FROM processes WHERE tenant_id=:tid)"), {"tid": tid})
    db.session.execute(text("DELETE FROM process_leaders WHERE process_id IN (SELECT id FROM processes WHERE tenant_id=:tid)"), {"tid": tid})
    db.session.execute(text("DELETE FROM process_members WHERE process_id IN (SELECT id FROM processes WHERE tenant_id=:tid)"), {"tid": tid})
    db.session.execute(text("DELETE FROM process_kpis WHERE process_id IN (SELECT id FROM processes WHERE tenant_id=:tid)"), {"tid": tid})
    db.session.execute(text("DELETE FROM processes WHERE tenant_id=:tid"), {"tid": tid})
    db.session.execute(text("DELETE FROM sub_strategies WHERE strategy_id IN (SELECT id FROM strategies WHERE tenant_id=:tid)"), {"tid": tid})
    db.session.execute(text("DELETE FROM strategies WHERE tenant_id=:tid"), {"tid": tid})
    db.session.execute(text("DELETE FROM plan_years WHERE tenant_id=:tid"), {"tid": tid})
    db.session.execute(text("DELETE FROM users WHERE tenant_id=:tid"), {"tid": tid})
    db.session.execute(text("DELETE FROM tenants WHERE id=:tid"), {"tid": tid})
    db.session.flush()


def seed(args):
    if not MD_PATH.exists():
        sys.exit(f"HATA: {MD_PATH} bulunamadi")
    if not EMP_PATH.exists():
        sys.exit(f"HATA: {EMP_PATH} bulunamadi")

    md_text = MD_PATH.read_text(encoding="utf-8")
    emp_data = json.loads(EMP_PATH.read_text(encoding="utf-8"))
    employees = emp_data["calisanlar"]
    tree = parse_strategy_tree(md_text)

    print("=" * 70)
    print(f"  TOMOFIL SEED — mod: {'DRY-RUN' if args.dry_run else 'COMMIT'}")
    print("=" * 70)
    print(f"  Strateji agaci: H={len(tree['H'])} L1={len(tree['L1'])} L2={len(tree['L2'])}")
    print(f"  Calisan kaydi : {len(employees)}")
    print(f"  Surec sayisi  : {len(PROCESS_DEFS)}")
    print(f"  Plan yili     : {PLAN_YEARS[0]}-{PLAN_YEARS[-1]} ({len(PLAN_YEARS)} yil)")
    print()

    existing = find_existing_tenant()
    if existing:
        if args.reset:
            reset_tenant(existing)
            print(f"  [OK] Mevcut tenant silindi (id={existing.id})")
        else:
            sys.exit(f"HATA: '{TENANT_NAME}' zaten var (id={existing.id}). --reset ile sil.")

    # 1) Tenant
    tenant = Tenant(
        name=TENANT_NAME,
        short_name=TENANT_SHORT,
        is_active=True,
        package_id=PACKAGE_ID,
        sector="Otomotiv / Mobilite",
        activity_area="Surdurulebilir Elektrikli Arac Uretimi",
        employee_count=len(employees),
        contact_email="info@tomofil.test",
        max_user_count=5000,
        vision='Mobiliteyi yeniden tanimlayan, kuresel olarak guvenilen, surdurulebilir liderlik.',
        purpose="Surdurulebilir mobilite cozumlerini erisilebilir kilmak.",
        core_values="Inovasyon, Surdurulebilirlik, Cesitlilik, Musteri Odaklilik, Etik",
        plan_year_enabled=True,
        plan_year_start=2026,
        k_vektor_enabled=True,
        k_radar_enabled=True,
    )
    db.session.add(tenant)
    db.session.flush()
    print(f"  [OK] Tenant olusturuldu: id={tenant.id} '{tenant.name}'")

    # 2) PlanYear
    plan_years_by_year = {}
    for y in PLAN_YEARS:
        py = PlanYear(
            tenant_id=tenant.id,
            year=y,
            name=f"{y} Stratejik Plani",
            status="active" if y == 2026 else "draft",
        )
        db.session.add(py)
        plan_years_by_year[y] = py
    db.session.flush()
    active_py = plan_years_by_year[2026]
    print(f"  [OK] PlanYear: {len(PLAN_YEARS)} yil (2026 active)")

    # 3) Admin user
    pwd_hash = generate_password_hash(DEFAULT_PASSWORD)
    admin = User(
        email=ADMIN_EMAIL,
        password_hash=pwd_hash,
        first_name="Tomofil",
        last_name="Admin",
        is_active=True,
        tenant_id=tenant.id,
        role_id=ROLE_TENANT_ADMIN,
        job_title="Tenant Yoneticisi",
        department="Yonetim",
    )
    db.session.add(admin)
    db.session.flush()
    print(f"  [OK] Admin: {ADMIN_EMAIL} / {DEFAULT_PASSWORD}")

    # 4) Calisanlar (3800 user)
    print(f"  [..] {len(employees)} kullanici insert ediliyor...")
    used_emails = {ADMIN_EMAIL}
    users_by_emp_id = {}
    user_rows = []
    for emp in employees:
        ad_soyad = emp["ad_soyad"].strip()
        parts = ad_soyad.split()
        first = " ".join(parts[:-1]) if len(parts) > 1 else ad_soyad
        last = parts[-1] if len(parts) > 1 else ""
        email_base = f"{slug(first)}.{slug(last)}" if last else slug(first)
        email = f"{email_base}@tomofil.test"
        if email in used_emails:
            email = f"{email_base}.{emp['id']}@tomofil.test"
        used_emails.add(email)

        role_id = ROLE_EXECUTIVE if emp.get("kademe") == "Yonetici" or emp.get("kademe") == "Yönetici" else ROLE_STANDARD
        user_rows.append({
            "email": email,
            "password_hash": pwd_hash,
            "first_name": first[:64],
            "last_name": last[:64],
            "is_active": True,
            "tenant_id": tenant.id,
            "role_id": role_id,
            "job_title": (emp.get("unvan") or "")[:100],
            "department": (emp.get("departman") or "")[:100],
            "layout_preference": "classic",
            "show_page_guides": True,
            "guide_character_style": "professional",
            "created_at": datetime.now(timezone.utc),
        })

    # Bulk insert + emp_id -> user_id mapping icin email araciligiyla geri oku
    db.session.bulk_insert_mappings(User, user_rows)
    db.session.flush()

    email_to_uid = {
        u.email: u.id for u in db.session.query(User.id, User.email).filter(User.tenant_id == tenant.id).all()
    }
    # emp_id -> user_id eslestir
    for emp in employees:
        ad_soyad = emp["ad_soyad"].strip()
        parts = ad_soyad.split()
        first = " ".join(parts[:-1]) if len(parts) > 1 else ad_soyad
        last = parts[-1] if len(parts) > 1 else ""
        eb = f"{slug(first)}.{slug(last)}" if last else slug(first)
        em = f"{eb}@tomofil.test"
        if em not in email_to_uid:
            em = f"{eb}.{emp['id']}@tomofil.test"
        users_by_emp_id[emp["id"]] = email_to_uid.get(em)

    print(f"  [OK] {len(user_rows)} kullanici insert edildi (executive={sum(1 for r in user_rows if r['role_id']==ROLE_EXECUTIVE)})")

    # 5) Process (14)
    process_by_code = {}
    for code, name_tr, name_en in PROCESS_DEFS:
        p = Process(
            tenant_id=tenant.id,
            code=code,
            name=name_tr,
            english_name=name_en,
            status="Aktif",
            is_active=True,
            plan_year_id=active_py.id,
            weight=round(100.0 / len(PROCESS_DEFS), 2),
        )
        db.session.add(p)
        process_by_code[code] = p
    db.session.flush()
    print(f"  [OK] {len(PROCESS_DEFS)} surec olusturuldu")

    # 6) Process owners — her surec icin o sureci yoneten ilk "Yonetici" kademe
    # Calisan listesinde olmayan surecler (O2C) icin fallback: admin
    owner_count = 0
    fallback_count = 0
    seen_pairs = set()
    for code, p in process_by_code.items():
        assigned = False
        for emp in employees:
            if emp.get("surec_kodu") == code and emp.get("kademe") in ("Yonetici", "Yönetici"):
                uid = users_by_emp_id.get(emp["id"])
                if uid and (p.id, uid) not in seen_pairs:
                    db.session.execute(process_owners_table.insert().values(process_id=p.id, user_id=uid))
                    db.session.execute(process_leaders.insert().values(process_id=p.id, user_id=uid))
                    seen_pairs.add((p.id, uid))
                    owner_count += 1
                    assigned = True
                    break
        if not assigned:
            db.session.execute(process_owners_table.insert().values(process_id=p.id, user_id=admin.id))
            db.session.execute(process_leaders.insert().values(process_id=p.id, user_id=admin.id))
            fallback_count += 1
            print(f"     [warn] {code}: calisanlar JSON'da yonetici yok -> admin atandi")
    print(f"  [OK] {owner_count} surec sahibi + {fallback_count} fallback (admin) atandi")

    # 7) Strategies (H1-H6)
    strategy_by_h = {}
    for h_num, title in tree["H"]:
        s = Strategy(
            tenant_id=tenant.id,
            code=f"H{h_num}",
            title=title.strip(),
            description=f"Ana Stratejik Hedef H{h_num}",
            is_active=True,
            plan_year_id=active_py.id,
        )
        db.session.add(s)
        strategy_by_h[h_num] = s
    db.session.flush()
    print(f"  [OK] {len(strategy_by_h)} ana strateji")

    # 8) SubStrategies (L1 + L2) — hepsi sub_strategies tablosunda
    substrat_by_code = {}
    for code, title, parent_h in tree["L1"]:
        parent = strategy_by_h.get(parent_h)
        if not parent:
            continue
        ss = SubStrategy(
            strategy_id=parent.id,
            code=code,
            title=title,
            description=f"L1 Alt Strateji {code}",
            is_active=True,
            plan_year_id=active_py.id,
        )
        db.session.add(ss)
        substrat_by_code[code] = ss
    db.session.flush()

    for code, title, parent_l1, body in tree["L2"]:
        parent_h = code[0]
        parent_strategy = strategy_by_h.get(parent_h)
        if not parent_strategy:
            continue
        # L2 govdesinde aciklama-benzeri ilk satiri al
        m = re.search(r"\*\*A[çc]?[ıi]?klama:?\*\*\s*(.+)", body)
        desc = m.group(1).strip() if m else None
        ss = SubStrategy(
            strategy_id=parent_strategy.id,
            code=code,
            title=title,
            description=desc,
            is_active=True,
            plan_year_id=active_py.id,
        )
        db.session.add(ss)
        substrat_by_code[code] = ss
    db.session.flush()
    print(f"  [OK] {len(substrat_by_code)} alt strateji (L1+L2)")

    # 9) ProcessKpi — strateji agacindaki KPI satirlari
    kpi_count = 0
    seen_kpis = set()
    for l2_code, kpis in tree["kpis"].items():
        ss = substrat_by_code.get(l2_code)
        for kpi_tuple in kpis:
            tag = kpi_tuple[0]
            if tag == "OKR":
                # OKR'lar S2E surecine bagli
                surec_code = "S2E"
                code_val, name, target = kpi_tuple[1], kpi_tuple[2], kpi_tuple[3]
            else:
                surec_code = tag
                code_val, name, target = "", kpi_tuple[2], kpi_tuple[3]
            proc = process_by_code.get(surec_code)
            if not proc:
                continue
            dedupe_key = (proc.id, name[:120], l2_code)
            if dedupe_key in seen_kpis:
                continue
            seen_kpis.add(dedupe_key)
            kpi = ProcessKpi(
                process_id=proc.id,
                name=name[:200],
                description=f"{l2_code}: {target}"[:500],
                code=code_val[:50] if code_val else None,
                target_value=target[:100],
                period="Yillik",
                direction="Increasing",
                is_active=True,
                sub_strategy_id=ss.id if ss else None,
                plan_year_id=active_py.id,
                weight=1.0,
            )
            db.session.add(kpi)
            kpi_count += 1
    db.session.flush()
    print(f"  [OK] {kpi_count} ProcessKpi olusturuldu")

    print()
    print("=" * 70)
    if args.dry_run:
        db.session.rollback()
        print("  DRY-RUN: tum degisiklikler GERI ALINDI. INSERT yok.")
    else:
        db.session.commit()
        print(f"  COMMIT: tenant_id={tenant.id} kalici olarak kaydedildi.")
        print(f"  Login : {ADMIN_EMAIL} / {DEFAULT_PASSWORD}")
    print("=" * 70)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Insert sonrasi rollback")
    ap.add_argument("--commit", action="store_true", help="Gercek commit")
    ap.add_argument("--reset", action="store_true", help="Mevcut Tomofil tenant'i sil ve yeniden seed et")
    args = ap.parse_args()
    if not (args.dry_run or args.commit):
        ap.error("--dry-run veya --commit secmelisin")

    app = create_app()
    with app.app_context():
        try:
            seed(args)
        except Exception:
            db.session.rollback()
            raise


if __name__ == "__main__":
    main()
