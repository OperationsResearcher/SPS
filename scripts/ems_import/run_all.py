"""EMS — Eskişehir Makine Sanayii A.Ş. — tüm verilerin sisteme yüklenmesi.

Kullanım:
    python scripts/ems_import/run_all.py

Sıralı fazlar:
    1. Tenant profili
    2. Kullanıcılar (~30 login-able)
    3. Plan dönemi 2026
    4. Süreç ağacı
    5. Strateji ağacı (6 ana / ~18 alt / ~43 girişim)
    6. KPI + OKR
    7. Risk kaydı (10 ana risk)
    8. Tarihsel veri (25.300 atomik kayıt → aylık aggregate)
    9. Doğrulama
"""
import datetime as dt
import logging
import os
import secrets
import string
import sys
from collections import defaultdict
from pathlib import Path

# Proje root'unu sys.path'e ekle
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Tüm script'e Türkçe yazdırma — Windows konsolu UTF-8
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from scripts.ems_import._common import (
    EMS_TENANT_ID, C_SUITE, BOARD, FACILITIES, PROCESS_MAP, RISKS,
    DOCS_DIR, load_employees, load_atomic, name_to_email, slugify, log,
)


def gen_temp_password() -> str:
    """Geçici güvenli şifre."""
    alphabet = string.ascii_letters + string.digits
    return "Kp_" + "".join(secrets.choice(alphabet) for _ in range(12))


# ─── FAZ 1 — TENANT PROFİLİ ─────────────────────────────────────────────────
def phase_01_tenant(db, models):
    log("FAZ 1 — Tenant profili güncelleniyor")
    Tenant = models["Tenant"]

    t = Tenant.query.get(EMS_TENANT_ID)
    if not t:
        raise SystemExit(f"Tenant id={EMS_TENANT_ID} bulunamadı.")

    t.name = "Eskişehir Makine Sanayii A.Ş."
    t.short_name = "EMS"
    t.tenant_type = "normal"
    t.parent_tenant_id = None
    t.is_active = True
    t.sector = "Beyaz Eşya Bileşeni Üretimi (NACE 27.51)"
    t.activity_area = "Kompresör · Tambur · Şasi · Motor · Kondenser · Bobin"
    t.tax_number = "4820188234"
    t.tax_office = "Eskişehir"
    t.contact_email = "info@ems.com.tr"
    t.phone_number = "+90 222 000 00 00"
    t.website_url = "https://www.ems.com.tr"
    t.employee_count = 4750
    t.max_user_count = 100
    t.purpose = ("Kompresör, tambur, motor ve şasi gibi kritik beyaz eşya bileşenlerini "
                 "dünya standartlarında üreterek küresel OEM müşterilerine güvenilir, "
                 "zamanında ve sürdürülebilir tedarik sağlamak.")
    t.vision = ("Beyaz eşya bileşeni teknolojilerinde Türkiye'nin küresel marka kimliği olmak; "
                "5 kıtada müşteri, Eskişehir'de mükemmellik.")
    t.core_values = ("Kalitede Uzlaşmama · Sözümüzü Tutmak · Sürdürülebilir Büyüme · "
                     "Mühendislik Kültürü · Yerel Güç Küresel Erişim")
    t.k_radar_enabled = True
    t.k_vektor_enabled = True
    t.plan_year_enabled = True
    t.plan_year_start = 2026

    # Logo: placeholder SVG (lacivert kare + EMS yazı)
    logo_dir = Path(__file__).resolve().parents[2] / "instance" / "uploads" / "tenant_logos"
    logo_dir.mkdir(parents=True, exist_ok=True)
    logo_file = logo_dir / f"{EMS_TENANT_ID}.svg"
    if not logo_file.exists():
        logo_file.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 60">'
            '<rect width="200" height="60" rx="6" fill="#1B3F6E"/>'
            '<text x="100" y="40" text-anchor="middle" fill="#fff" '
            'font-family="Arial,Helvetica,sans-serif" font-size="32" font-weight="700" letter-spacing="2">EMS</text>'
            '</svg>',
            encoding="utf-8",
        )
    t.logo_path = f"{EMS_TENANT_ID}.svg"
    t.logo_updated_at = dt.datetime.now(dt.timezone.utc)

    db.session.commit()
    log(f"  ✓ Tenant {t.id} = {t.name} | sektor={t.sector} | type={t.tenant_type}")


# ─── FAZ 2 — KULLANICILAR ───────────────────────────────────────────────────
def phase_02_users(db, models):
    log("FAZ 2 — Kullanıcılar oluşturuluyor (~20 kişi: C-Suite + YK + tesis müdürleri)")
    User = models["User"]
    Role = models["Role"]
    from werkzeug.security import generate_password_hash

    # Roller
    role_admin = Role.query.filter_by(name="tenant_admin").first()
    role_exec = Role.query.filter_by(name="executive_manager").first()
    if not role_admin or not role_exec:
        raise SystemExit("Gerekli roller bulunamadı.")

    created = []
    skipped = []

    def upsert_user(full_name, title_text, role_obj, department=""):
        email = name_to_email(full_name)
        u = User.query.filter_by(email=email).first()
        if u:
            # Sadece tenant ve rolünü güncelle
            u.tenant_id = EMS_TENANT_ID
            if u.role_id != role_obj.id:
                u.role_id = role_obj.id
            skipped.append((email, "var olan"))
            return u
        parts = full_name.replace("Dr. ", "").strip().split()
        first = " ".join(parts[:-1]) if len(parts) > 1 else parts[0]
        last = parts[-1] if len(parts) > 1 else ""
        pwd = gen_temp_password()
        u = User(
            email=email,
            first_name=first,
            last_name=last,
            password_hash=generate_password_hash(pwd),
            tenant_id=EMS_TENANT_ID,
            role_id=role_obj.id,
            job_title=title_text,
            department=department or "Üst Yönetim",
            is_active=True,
        )
        db.session.add(u)
        db.session.flush()
        created.append((email, full_name, title_text, pwd))
        return u

    # CEO → tenant_admin
    ceo_full = C_SUITE[0][1]
    upsert_user(ceo_full, "CEO — Genel Müdür", role_admin, "Yönetim")

    # Diğer C-Suite → executive_manager
    for title_code, full_name, _desc in C_SUITE[1:]:
        upsert_user(full_name, f"{title_code} — Üst Yönetim", role_exec, "Yönetim")

    # YK üyeleri → executive_manager (rapor okumak için)
    for title, full_name, _desc in BOARD:
        upsert_user(full_name, title, role_exec, "Yönetim Kurulu")

    # Tesis müdürleri → executive_manager
    for facility, title, full_name in FACILITIES:
        upsert_user(full_name, title, role_exec, facility)

    db.session.commit()

    # Log dosyası
    log_dir = Path(__file__).resolve().parents[2] / "data" / "ems_import_log"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "users_created.csv"
    with log_file.open("w", encoding="utf-8") as f:
        f.write("email,full_name,title,temp_password\n")
        for e, n, t, p in created:
            f.write(f"{e},{n},{t},{p}\n")
    log(f"  ✓ {len(created)} yeni kullanıcı + {len(skipped)} var olan güncellendi")
    log(f"  ✓ Geçici şifreler: {log_file}")


# ─── FAZ 3 — PLAN DÖNEMİ ────────────────────────────────────────────────────
def phase_03_plan_year(db, models):
    log("FAZ 3 — Plan dönemi 2026")
    PlanYear = models["PlanYear"]
    TenantYearIdentity = models["TenantYearIdentity"]
    Tenant = models["Tenant"]

    py = PlanYear.query.filter_by(tenant_id=EMS_TENANT_ID, year=2026).first()
    if not py:
        py = PlanYear(
            tenant_id=EMS_TENANT_ID, year=2026,
            name="2026 Stratejik Planı",
            status="active",
        )
        db.session.add(py)
        db.session.flush()
        log(f"  ✓ PlanYear 2026 oluşturuldu (id={py.id})")
    else:
        py.status = "active"
        py.name = "2026 Stratejik Planı"
        log(f"  ✓ PlanYear 2026 mevcut (id={py.id}) — aktif yapıldı")

    # Diğer plan year'lar varsa pasifleştir (sadece 2026 aktif)
    other = PlanYear.query.filter(
        PlanYear.tenant_id == EMS_TENANT_ID,
        PlanYear.id != py.id,
        PlanYear.status == "active",
    ).all()
    for o in other:
        o.status = "closed"
        log(f"  ✓ PlanYear {o.year} closed yapıldı")

    # Year identity
    t = Tenant.query.get(EMS_TENANT_ID)
    yid = TenantYearIdentity.query.filter_by(plan_year_id=py.id).first()
    if not yid:
        yid = TenantYearIdentity(plan_year_id=py.id, tenant_id=EMS_TENANT_ID)
        db.session.add(yid)
    yid.purpose = t.purpose
    yid.vision = t.vision
    yid.core_values = t.core_values

    db.session.commit()
    log(f"  ✓ TenantYearIdentity 2026 yazıldı")
    return py.id


# ─── FAZ 4 — SÜREÇLER ───────────────────────────────────────────────────────
def phase_04_processes(db, models, plan_year_id):
    log("FAZ 4 — Süreç ağacı (12 ana süreç)")
    Process = models["Process"]
    User = models["User"]

    # C-Suite ünvan → user_id eşlemesi
    csuite_user = {}
    for code, full_name, _ in C_SUITE:
        u = User.query.filter_by(email=name_to_email(full_name)).first()
        if u:
            csuite_user[code] = u

    process_id_by_code = {}
    for code, eng_name, tr_name, desc, owner_csuite in PROCESS_MAP:
        p = Process.query.filter_by(tenant_id=EMS_TENANT_ID, code=code, plan_year_id=plan_year_id).first()
        if not p:
            p = Process(
                tenant_id=EMS_TENANT_ID,
                code=code,
                name=tr_name,
                english_name=eng_name,
                description=desc,
                plan_year_id=plan_year_id,
                status="Aktif",
                is_active=True,
            )
            db.session.add(p)
            db.session.flush()

        # Sahip ata
        owner = csuite_user.get(owner_csuite)
        if owner and owner not in p.owners:
            p.owners.append(owner)
        process_id_by_code[code] = p.id

    db.session.commit()
    log(f"  ✓ {len(process_id_by_code)} süreç oluşturuldu/güncellendi")
    return process_id_by_code


# ─── FAZ 5 — STRATEJİ AĞACI ─────────────────────────────────────────────────
def parse_strategy_tree():
    """EMS_Strateji_Agaci.md'yi ayrıştır.

    Yapı:
        # H1 — PAZAR LİDERLİĞİ ...
        ## ├── 1.A OEM Müşteri Tabanı Genişletme
        ### │   ├── 1.A.1 Avrupa OEM Derinleşme ...
        - **Açıklama:** ...
        - **Süreçler:** `A2R` · `C2L` · `O2C`
        - **KPI'lar:** OEM pazar payı %4→%11 · ...
    """
    import re
    from scripts.ems_import._common import read_md
    text = read_md("EMS_Strateji_Agaci.md")
    lines = text.splitlines()

    strategies = []  # (code, title)
    sub_strategies = []  # (parent_code, code, title)
    leaves = []  # (sub_code, code, title, aciklama, surec_codes, kpi_text)

    current_main = None
    current_sub = None
    current_leaf = None

    re_main = re.compile(r"^# H(\d)\s+[—–-]\s+(.+?)\s*$")
    re_sub = re.compile(r"^##\s+[├└]──\s+(\d+\.[A-Z])\s+(.+?)\s*$")
    re_leaf = re.compile(r"^###\s+[│\s]*[├└]──\s+(\d+\.[A-Z]\.\d+)\s+(.+?)\s*$")
    re_aciklama = re.compile(r"^-\s+\*\*Açıklama:\*\*\s+(.+)$")
    re_surec = re.compile(r"^-\s+\*\*Süreçler:\*\*\s+(.+)$")
    re_kpi = re.compile(r"^-\s+\*\*KPI'lar:\*\*\s+(.+)$")

    for line in lines:
        m = re_main.match(line)
        if m:
            if current_leaf:
                leaves.append(current_leaf); current_leaf = None
            code = f"H{m.group(1)}"
            current_main = code
            current_sub = None
            strategies.append((code, m.group(2).strip()))
            continue
        m = re_sub.match(line)
        if m:
            if current_leaf:
                leaves.append(current_leaf); current_leaf = None
            current_sub = m.group(1)
            sub_strategies.append((current_main, current_sub, m.group(2).strip()))
            continue
        m = re_leaf.match(line)
        if m:
            if current_leaf:
                leaves.append(current_leaf)
            current_leaf = {
                "code": m.group(1),
                "title": m.group(2).strip(),
                "sub_code": current_sub,
                "aciklama": "",
                "surec_codes": [],
                "kpi_text": "",
            }
            continue
        if current_leaf:
            m = re_aciklama.match(line)
            if m:
                current_leaf["aciklama"] = m.group(1).strip()
                continue
            m = re_surec.match(line)
            if m:
                codes = re.findall(r"`([A-Z0-9]{3,4})`", m.group(1))
                current_leaf["surec_codes"] = codes
                continue
            m = re_kpi.match(line)
            if m:
                current_leaf["kpi_text"] = m.group(1).strip()
                continue
    if current_leaf:
        leaves.append(current_leaf)
    return strategies, sub_strategies, leaves


def phase_05_strategies(db, models, plan_year_id, process_id_by_code):
    log("FAZ 5 — Strateji ağacı (Strategy / SubStrategy / Initiative)")
    Strategy = models["Strategy"]
    SubStrategy = models["SubStrategy"]
    Initiative = models["Initiative"]

    strategies, sub_strategies, leaves = parse_strategy_tree()
    log(f"  Markdown'dan: {len(strategies)} ana, {len(sub_strategies)} alt, {len(leaves)} girişim")

    strategy_id_by_code = {}
    for code, title in strategies:
        s = Strategy.query.filter_by(tenant_id=EMS_TENANT_ID, code=code, plan_year_id=plan_year_id).first()
        if not s:
            s = Strategy(tenant_id=EMS_TENANT_ID, code=code, title=title, plan_year_id=plan_year_id, is_active=True)
            db.session.add(s)
            db.session.flush()
        else:
            s.title = title
        strategy_id_by_code[code] = s.id

    sub_id_by_code = {}
    for parent_code, sub_code, title in sub_strategies:
        parent_id = strategy_id_by_code.get(f"H{sub_code.split('.')[0]}")
        if not parent_id:
            continue
        ss = SubStrategy.query.filter_by(strategy_id=parent_id, code=sub_code, plan_year_id=plan_year_id).first()
        if not ss:
            ss = SubStrategy(strategy_id=parent_id, code=sub_code, title=title, plan_year_id=plan_year_id, is_active=True)
            db.session.add(ss)
            db.session.flush()
        else:
            ss.title = title
        sub_id_by_code[sub_code] = ss.id

    db.session.commit()
    log(f"  ✓ {len(strategy_id_by_code)} ana strateji, {len(sub_id_by_code)} alt strateji yazıldı")

    # Initiatives
    for leaf in leaves:
        code = leaf["code"]
        sub_code = leaf["sub_code"]
        sub_id = sub_id_by_code.get(sub_code) if sub_code else None
        parent_strategy_id = strategy_id_by_code.get(f"H{code.split('.')[0]}")
        i = Initiative.query.filter_by(tenant_id=EMS_TENANT_ID, code=code).first()
        if not i:
            i = Initiative(
                tenant_id=EMS_TENANT_ID,
                code=code,
                name=leaf["title"],
                description=leaf["aciklama"],
                strategy_id=parent_strategy_id,
                sub_strategy_id=sub_id,
                start_year=2026,
                end_year=2030,
                status="planned",
                priority="high",
                progress_pct=0.0,
                is_active=True,
            )
            db.session.add(i)
        else:
            i.name = leaf["title"]
            i.description = leaf["aciklama"]
            i.strategy_id = parent_strategy_id
            i.sub_strategy_id = sub_id
    db.session.commit()
    log(f"  ✓ {len(leaves)} girişim yazıldı")
    return strategy_id_by_code, sub_id_by_code, leaves


# ─── FAZ 6 — KPI + OKR ──────────────────────────────────────────────────────
OKR_DATA = [
    # (code, title, start, target_2030, metric)
    ("OKR1.1", "Beyaz Eşya Bileşeni Pazar Payı %", 0.6, 2.0, "%", "H1"),
    ("OKR1.2", "Toplam Ciro (€M)", 320, 850, "€M", "H1"),
    ("OKR1.3", "OEM Müşteri Sayısı", 12, 35, "adet", "H1"),
    ("OKR1.4", "İhracat / Ciro %", 24, 52, "%", "H1"),
    ("OKR2.1", "Patent Sayısı", 284, 1200, "adet", "H2"),
    ("OKR2.2", "BLDC Lineer Kompresör TRL", 5, 9, "TRL", "H2"),
    ("OKR2.3", "A+++ Sertifikalı Ürün Sayısı", 0, 7, "adet", "H2"),
    ("OKR2.4", "IoT/Yazılım Ciro %", 0.4, 12, "%", "H2"),
    ("OKR3.1", "EBITDA %", 15.2, 20.0, "%", "H3"),
    ("OKR3.2", "Birim Üretim Maliyeti (€)", 13.4, 11.0, "€", "H3"),
    ("OKR3.3", "OEE (tüm tesisler ort.) %", 78, 92, "%", "H3"),
    ("OKR3.4", "ROIC %", 10.5, 15.2, "%", "H3"),
    ("OKR4.1", "Scope 1+2 Emisyon (tCO2e)", 42000, 0, "tCO2e", "H4"),
    ("OKR4.2", "Geri Dön. Hammadde %", 8, 55, "%", "H4"),
    ("OKR4.3", "ESG Sertifika (ISO 50001 tesis)", 2, 6, "tesis", "H4"),
    ("OKR4.4", "EMS Vakfı Mezun/yıl", 0, 1200, "kişi", "H4"),
    ("OKR5.1", "OEM NPS", 48, 65, "skor", "H5"),
    ("OKR5.2", "Preferred Supplier Statüsü (OEM)", 2, 8, "adet", "H5"),
    ("OKR5.3", "EDI Entegre OEM %", 35, 100, "%", "H5"),
    ("OKR5.4", "OEM CLV (€M)", 4.2, 9.8, "€M", "H5"),
    ("OKR6.1", "eNPS", 38, 56, "skor", "H6"),
    ("OKR6.2", "Kadın Mühendis %", 18, 35, "%", "H6"),
    ("OKR6.3", "Eğitim Saati/Kişi", 28, 55, "saat", "H6"),
    ("OKR6.4", "Devir Hızı %", 9.2, 5.5, "%", "H6"),
]


def phase_06_kpis_okrs(db, models, plan_year_id, strategy_id_by_code, leaves):
    log("FAZ 6 — KPI + OKR")
    OkrObjective = models["OkrObjective"]
    OkrKeyResult = models["OkrKeyResult"]
    ProcessKpi = models["ProcessKpi"]
    Process = models["Process"]

    # 24 OKR — her ana strateji altına bir Objective, KR olarak OKR adı
    # H1 → "Pazar Liderliği" başlığı altında 4 KR
    objectives_by_h = {}
    for code, title, start, target, metric, h_code in OKR_DATA:
        if h_code not in objectives_by_h:
            strat_id = strategy_id_by_code.get(h_code)
            from scripts.ems_import._common import C_SUITE
            obj_title_map = {
                "H1": "Pazar Liderliği ve Büyüme",
                "H2": "Teknoloji ve İnovasyon",
                "H3": "Operasyonel Mükemmellik",
                "H4": "Sürdürülebilirlik",
                "H5": "OEM İlişkileri ve Marka",
                "H6": "Yetenek ve Kültür",
            }
            obj = OkrObjective.query.filter_by(
                tenant_id=EMS_TENANT_ID, plan_year_id=plan_year_id, title=obj_title_map[h_code]
            ).first()
            if not obj:
                obj = OkrObjective(
                    tenant_id=EMS_TENANT_ID,
                    plan_year_id=plan_year_id,
                    title=obj_title_map[h_code],
                    description=f"{h_code} stratejik kapsamı altındaki yıllık hedefler",
                    linked_strategy_id=strat_id,
                    is_active=True,
                )
                db.session.add(obj)
                db.session.flush()
            objectives_by_h[h_code] = obj

        obj = objectives_by_h[h_code]
        kr = OkrKeyResult.query.filter_by(objective_id=obj.id, title=title).first()
        if not kr:
            kr = OkrKeyResult(
                objective_id=obj.id,
                title=title,
                metric=metric,
                start_value=float(start),
                target_value=float(target),
                current_value=float(start),
                is_active=True,
            )
            db.session.add(kr)
    db.session.commit()
    log(f"  ✓ {len(objectives_by_h)} Objective + {len(OKR_DATA)} KeyResult")

    # ProcessKpi'lar — her girişim için KPI metninden 1-2 KPI çıkar, sürece bağla
    process_id_by_code = {p.code: p.id for p in Process.query.filter_by(tenant_id=EMS_TENANT_ID).all()}
    kpi_count = 0
    for leaf in leaves:
        kpi_text = leaf.get("kpi_text") or ""
        if not kpi_text:
            continue
        sub_code = leaf.get("sub_code")
        proc_codes = leaf.get("surec_codes") or []
        # İlk süreç kodunu primary olarak al
        primary_proc_id = None
        for pc in proc_codes:
            if pc in process_id_by_code:
                primary_proc_id = process_id_by_code[pc]
                break
        if not primary_proc_id:
            continue

        # KPI metinleri ' · ' ile ayrılı: "OEM pazar payı %4→%11 · OTD %89→%98"
        items = [s.strip() for s in kpi_text.split("·") if s.strip()]
        for item in items[:3]:  # max 3 KPI per leaf
            kpi_name = item[:200]
            code = f"PG-{leaf['code']}-{kpi_count+1}"
            # Mevcut?
            existing = ProcessKpi.query.filter_by(
                process_id=primary_proc_id, name=kpi_name, plan_year_id=plan_year_id
            ).first()
            if existing:
                continue
            # Sub strategy bağı
            sub_id = None
            if sub_code:
                from app.models.core import SubStrategy as _SS
                ss = _SS.query.filter_by(code=sub_code, plan_year_id=plan_year_id).first()
                if ss:
                    sub_id = ss.id
            pk = ProcessKpi(
                process_id=primary_proc_id,
                name=kpi_name,
                description=leaf.get("aciklama"),
                code=code,
                plan_year_id=plan_year_id,
                sub_strategy_id=sub_id,
                period="Aylık",
                direction="Increasing",
                gosterge_turu="İyileştirme",
                is_active=True,
            )
            db.session.add(pk)
            kpi_count += 1
    db.session.commit()
    log(f"  ✓ {kpi_count} süreç KPI'sı oluşturuldu")


# ─── FAZ 7 — RİSK KAYDI ─────────────────────────────────────────────────────
def phase_07_risks(db, models, plan_year_id):
    log("FAZ 7 — Risk kaydı (10 ana risk)")
    RiskHeatmapItem = models["RiskHeatmapItem"]
    User = models["User"]

    # C-Suite kullanıcı ID'lerini topla
    csuite_user_id = {}
    for code, full_name, _ in C_SUITE:
        u = User.query.filter_by(email=name_to_email(full_name)).first()
        if u:
            csuite_user_id[code] = u.id

    count = 0
    for r in RISKS:
        existing = RiskHeatmapItem.query.filter_by(
            tenant_id=EMS_TENANT_ID, title=r["title"], plan_year_id=plan_year_id
        ).first()
        owner_id = csuite_user_id.get(r["sahip_unvan"])
        if not existing:
            item = RiskHeatmapItem(
                tenant_id=EMS_TENANT_ID,
                plan_year_id=plan_year_id,
                title=r["title"],
                probability=r["olasilik"],
                impact=r["etki"],
                rpn=r["olasilik"] * r["etki"],
                owner_id=owner_id,
                status="Açık",
                source_type=r["kategori"],
                is_active=True,
            )
            db.session.add(item)
            count += 1
        else:
            existing.probability = r["olasilik"]
            existing.impact = r["etki"]
            existing.rpn = r["olasilik"] * r["etki"]
            existing.owner_id = owner_id or existing.owner_id
            existing.source_type = r["kategori"]
    db.session.commit()
    log(f"  ✓ {count} yeni risk + güncelleme")


# ─── FAZ 8 — TARİHSEL VERİ ──────────────────────────────────────────────────
# KPI eşleme tablosu — her modül için (modül adı, KPI tanımları)
# Yapı: list of (kpi_name, agg_fn, value_extract_fn) — atomik kayıtlardan değer üret
KPI_DEFS = {
    "uretim_hat_kayitlari": [
        ("OEE Genel %", "AVG", lambda r: r.get("oee_pct")),
        ("Üretim Adedi (toplam)", "SUM", lambda r: r.get("uretilen_adet")),
        ("Hata Oranı %", "AVG", lambda r: r.get("hata_orani_pct")),
    ],
    "kalite_muayene": [
        ("Sigma Seviye Ort.", "AVG", lambda r: r.get("sigma_seviye")),
        ("Geçme Oranı %", "AVG", lambda r: r.get("gecme_pct")),
        ("PPM Hatalı", "AVG", lambda r: r.get("ppm")),
    ],
    "oem_musteri_temas": [
        ("OEM NPS Ortalaması", "AVG", lambda r: r.get("nps")),
        ("OEM CSAT", "AVG", lambda r: r.get("csat")),
        ("Sözleşme Geliri (EUR)", "SUM", lambda r: r.get("sozlesme_geliri_eur")),
    ],
    "tedarik_satin_alma": [
        ("Tedarik Tutarı (EUR)", "SUM", lambda r: r.get("tutar_eur")),
        ("Teslimat Gecikmesi (gün)", "AVG", lambda r: r.get("teslimat_gecikme_gun")),
    ],
    "ik_islemleri": [
        ("İK İşlem Süresi (dk)", "AVG", lambda r: r.get("sure_dakika")),
        ("eNPS Referans", "AVG", lambda r: r.get("enps_referans")),
    ],
    "esg_cevre_olcumleri": [
        ("ESG Ölçüm Değeri", "AVG", lambda r: r.get("deger")),
        ("ESG Hedef Sapması", "AVG", lambda r: r.get("sapma")),
    ],
    "finansal_islemler": [
        ("Finansal İşlem Tutarı", "SUM", lambda r: r.get("tutar")),
        ("Finansal İşlem Adedi", "SUM", lambda r: r.get("adet")),
    ],
}

# KPI'nın hangi sürece ait olduğu
MODULE_PROCESS = {
    "uretim_hat_kayitlari": "P2M",
    "kalite_muayene": "Q2C",
    "oem_musteri_temas": "A2R",
    "tedarik_satin_alma": "S2P",
    "ik_islemleri": "H2R",
    "esg_cevre_olcumleri": "G2N",
    "finansal_islemler": "R2R",
}


def phase_08_historical(db, models, plan_year_id, process_id_by_code):
    log("FAZ 8 — Tarihsel veri (25.300 atomik kayıt → aylık aggregate)")
    ProcessKpi = models["ProcessKpi"]
    KpiData = models["KpiData"]
    User = models["User"]
    OkrKeyResult = models["OkrKeyResult"]
    RiskHeatmapItem = models["RiskHeatmapItem"]

    data = load_atomic()

    # Veri girici default kullanıcı (CEO)
    ceo = User.query.filter_by(email=name_to_email(C_SUITE[0][1])).first()
    if not ceo:
        raise SystemExit("Veri girici kullanıcı (CEO) bulunamadı.")

    # 8 modülün KPI'larını oluştur (mevcut süreç altında)
    kpi_by_module_name = {}
    for module, defs in KPI_DEFS.items():
        proc_code = MODULE_PROCESS[module]
        proc_id = process_id_by_code.get(proc_code)
        if not proc_id:
            log(f"  ! Süreç bulunamadı: {proc_code} — atlanıyor")
            continue
        for kpi_name, agg, _fn in defs:
            existing = ProcessKpi.query.filter_by(
                process_id=proc_id, name=kpi_name, plan_year_id=plan_year_id
            ).first()
            if not existing:
                existing = ProcessKpi(
                    process_id=proc_id, name=kpi_name,
                    plan_year_id=plan_year_id,
                    period="Aylık",
                    calculation_method=agg,
                    data_collection_method="Toplama" if agg == "SUM" else "Ortalama",
                    gosterge_turu="İyileştirme",
                    is_active=True,
                )
                db.session.add(existing)
                db.session.flush()
            kpi_by_module_name[(module, kpi_name)] = existing.id
    db.session.commit()
    log(f"  ✓ {len(kpi_by_module_name)} aggregate KPI hazır")

    # Her modül için (year, month, kpi_name) → list of values topla
    # Sonra aggregate edip KpiData'ya yaz
    aggregates = defaultdict(list)  # (module, kpi_name, year, month) → values

    total_records = 0
    for module, defs in KPI_DEFS.items():
        records = data.get(module, [])
        for rec in records:
            vt = rec.get("veri_tarihi")
            if not vt:
                continue
            year = int(vt[:4])
            month = int(vt[5:7])
            for kpi_name, _agg, fn in defs:
                val = fn(rec)
                if val is None:
                    continue
                try:
                    aggregates[(module, kpi_name, year, month)].append(float(val))
                except (TypeError, ValueError):
                    continue
            total_records += 1
    log(f"  ✓ {total_records} atomik kayıt işlendi, {len(aggregates)} aylık aggregate üretildi")

    # KpiData yaz
    written = 0
    for (module, kpi_name, year, month), values in aggregates.items():
        kpi_id = kpi_by_module_name.get((module, kpi_name))
        if not kpi_id:
            continue
        agg_fn = next(d[1] for d in KPI_DEFS[module] if d[0] == kpi_name)
        if agg_fn == "SUM":
            value = sum(values)
        else:
            value = sum(values) / len(values)
        # KpiData mevcut mu?
        existing = KpiData.query.filter_by(
            process_kpi_id=kpi_id, year=year, period_month=month
        ).first()
        data_date = dt.date(year, month, 1)
        if existing:
            existing.actual_value = f"{value:.2f}"
        else:
            kd = KpiData(
                process_kpi_id=kpi_id,
                year=year,
                data_date=data_date,
                period_type="aylik",
                period_month=month,
                period_no=month,
                actual_value=f"{value:.2f}",
                user_id=ceo.id,
                is_active=True,
            )
            db.session.add(kd)
            written += 1
        if written % 200 == 0:
            db.session.commit()
    db.session.commit()
    log(f"  ✓ {written} KpiData satırı yazıldı")

    # OKR snapshots — son skor güncellemesini KR'a yansıt
    okr_updates = data.get("okr_risk_guncelleme", [])
    okr_latest = {}  # okr_kodu → (date, skor, baseline, hedef)
    risk_latest = {}  # risk_adi → (date, olasilik, etki)
    for rec in okr_updates:
        vt = rec.get("veri_tarihi", "")
        # OKR
        okr_code = rec.get("okr_kodu")
        skor = rec.get("okr_skor")
        if okr_code and skor is not None:
            prev = okr_latest.get(okr_code)
            if not prev or vt > prev[0]:
                okr_latest[okr_code] = (vt, skor, rec.get("okr_baseline"), rec.get("okr_hedef"))
        # Risk
        risk_name = rec.get("risk_adi")
        olas = rec.get("olasilik")
        etk = rec.get("etki")
        if risk_name and olas is not None and etk is not None:
            prev = risk_latest.get(risk_name)
            if not prev or vt > prev[0]:
                risk_latest[risk_name] = (vt, olas, etk)

    # OKR snapshot → KR.current_value güncelle
    from app.models.okr import OkrKeyResult as _KR, OkrObjective as _OBJ
    for okr_code, (_, skor, baseline, hedef) in okr_latest.items():
        # OKR_DATA'da OKR adıyla eşleştir
        match = next((row for row in OKR_DATA if row[0] == okr_code), None)
        if not match:
            continue
        kr_title = match[1]
        kr = _KR.query.join(_OBJ).filter(
            _OBJ.tenant_id == EMS_TENANT_ID,
            _OBJ.plan_year_id == plan_year_id,
            _KR.title == kr_title,
        ).first()
        if kr:
            # current_value = baseline + skor * (hedef - baseline)
            if baseline is not None and hedef is not None and skor is not None:
                kr.current_value = float(baseline) + float(skor) * (float(hedef) - float(baseline))
    log(f"  ✓ {len(okr_latest)} OKR snapshot uygulandı")

    # Risk snapshot — yeni risk verileri varsa olasılık/etkiyi güncelle
    updated_risks = 0
    for risk_name, (_, olas, etk) in risk_latest.items():
        # 1-5 skalasına çevir (olasilik 0-1, etki 0-1 olabilir)
        olas_int = int(round(olas * 5)) if olas <= 1.0 else int(round(olas))
        etk_int = int(round(etk * 5)) if etk <= 1.0 else int(round(etk))
        olas_int = max(1, min(5, olas_int))
        etk_int = max(1, min(5, etk_int))
        item = RiskHeatmapItem.query.filter_by(
            tenant_id=EMS_TENANT_ID, plan_year_id=plan_year_id, title=risk_name
        ).first()
        if item:
            item.probability = olas_int
            item.impact = etk_int
            item.rpn = olas_int * etk_int
            updated_risks += 1
    db.session.commit()
    log(f"  ✓ {updated_risks} risk OKR/risk modülünden güncellendi")


# ─── FAZ 9 — DOĞRULAMA ──────────────────────────────────────────────────────
def phase_09_verify(db, models, plan_year_id):
    log("FAZ 9 — Doğrulama")
    Tenant = models["Tenant"]
    User = models["User"]
    PlanYear = models["PlanYear"]
    Strategy = models["Strategy"]
    SubStrategy = models["SubStrategy"]
    Initiative = models["Initiative"]
    Process = models["Process"]
    ProcessKpi = models["ProcessKpi"]
    KpiData = models["KpiData"]
    OkrObjective = models["OkrObjective"]
    OkrKeyResult = models["OkrKeyResult"]
    RiskHeatmapItem = models["RiskHeatmapItem"]

    t = Tenant.query.get(EMS_TENANT_ID)
    uc = User.query.filter_by(tenant_id=EMS_TENANT_ID).count()
    py = PlanYear.query.filter_by(tenant_id=EMS_TENANT_ID, year=2026).first()
    sc = Strategy.query.filter_by(tenant_id=EMS_TENANT_ID, plan_year_id=plan_year_id).count()
    ssc = SubStrategy.query.join(Strategy).filter(
        Strategy.tenant_id == EMS_TENANT_ID, SubStrategy.plan_year_id == plan_year_id
    ).count()
    ic = Initiative.query.filter_by(tenant_id=EMS_TENANT_ID).count()
    pc = Process.query.filter_by(tenant_id=EMS_TENANT_ID, plan_year_id=plan_year_id).count()
    pkc = ProcessKpi.query.join(Process).filter(
        Process.tenant_id == EMS_TENANT_ID, ProcessKpi.plan_year_id == plan_year_id
    ).count()
    kdc = KpiData.query.join(ProcessKpi).join(Process).filter(
        Process.tenant_id == EMS_TENANT_ID
    ).count()
    obj_c = OkrObjective.query.filter_by(tenant_id=EMS_TENANT_ID, plan_year_id=plan_year_id).count()
    kr_c = OkrKeyResult.query.join(OkrObjective).filter(
        OkrObjective.tenant_id == EMS_TENANT_ID, OkrObjective.plan_year_id == plan_year_id
    ).count()
    rc = RiskHeatmapItem.query.filter_by(tenant_id=EMS_TENANT_ID, plan_year_id=plan_year_id).count()

    log("─" * 60)
    log(f"Tenant     : {t.name} (id={t.id}, type={t.tenant_type}, sektor={t.sector})")
    log(f"Kullanıcı  : {uc}")
    log(f"Plan Yılı  : {py.year} ({py.status})")
    log(f"Süreç      : {pc}")
    log(f"Strateji   : {sc} ana / {ssc} alt")
    log(f"Girişim    : {ic}")
    log(f"OKR        : {obj_c} obj / {kr_c} KR")
    log(f"ProcessKpi : {pkc}")
    log(f"KpiData    : {kdc} satır")
    log(f"Risk       : {rc}")
    log("─" * 60)


# ─── MAIN ───────────────────────────────────────────────────────────────────
def main():
    from app import create_app
    from app.extensions import db as _db
    from app.models.core import Tenant, User, Role, Strategy, SubStrategy
    from app.models.process import Process, ProcessKpi, KpiData
    from app.models.plan_year import PlanYear
    from app.models.tenant_year import TenantYearIdentity
    from app.models.initiative import Initiative
    from app.models.okr import OkrObjective, OkrKeyResult
    from app.models.k_radar_domain import RiskHeatmapItem

    app = create_app()
    with app.app_context():
        models = {
            "Tenant": Tenant, "User": User, "Role": Role,
            "Strategy": Strategy, "SubStrategy": SubStrategy,
            "Process": Process, "ProcessKpi": ProcessKpi, "KpiData": KpiData,
            "PlanYear": PlanYear, "TenantYearIdentity": TenantYearIdentity,
            "Initiative": Initiative,
            "OkrObjective": OkrObjective, "OkrKeyResult": OkrKeyResult,
            "RiskHeatmapItem": RiskHeatmapItem,
        }
        log("=" * 60)
        log(f"EMS DATA IMPORT — başlıyor (tenant_id={EMS_TENANT_ID})")
        log("=" * 60)

        phase_01_tenant(_db, models)
        phase_02_users(_db, models)
        plan_year_id = phase_03_plan_year(_db, models)
        process_id_by_code = phase_04_processes(_db, models, plan_year_id)
        strat_ids, sub_ids, leaves = phase_05_strategies(_db, models, plan_year_id, process_id_by_code)
        phase_06_kpis_okrs(_db, models, plan_year_id, strat_ids, leaves)
        phase_07_risks(_db, models, plan_year_id)
        phase_08_historical(_db, models, plan_year_id, process_id_by_code)
        phase_09_verify(_db, models, plan_year_id)

        log("✓ TÜM FAZLAR TAMAMLANDI")


if __name__ == "__main__":
    main()
