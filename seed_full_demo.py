"""
seed_full_demo.py
=================
3 kurum · 3/5/7 kullanıcı · 3 ana strateji × 5 alt strateji
5 süreç / kurum · 1-10 PG / süreç
10-30 KPI verisi / PG / yıl  (2024, 2025, 2026)

Çalıştır:
    python seed_full_demo.py
"""

import sys
import os
import random
import json
from datetime import datetime, date, timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
from app.models.core import Tenant, User, Role, Strategy, SubStrategy
from app.models.process import Process, ProcessKpi, ProcessActivity, KpiData

# ─── Sabit veriler ─────────────────────────────────────────────────────────────

TENANTS = [
    {
        "name": "Anadolu Sağlık Grubu",
        "short_name": "ASG",
        "sector": "Sağlık",
        "activity_area": "Hastane ve Klinik İşletmeciliği",
        "employee_count": 850,
        "user_count": 3,
    },
    {
        "name": "Ege Teknoloji A.Ş.",
        "short_name": "EGE-TECH",
        "sector": "Teknoloji",
        "activity_area": "Yazılım Geliştirme ve Danışmanlık",
        "employee_count": 320,
        "user_count": 5,
    },
    {
        "name": "Marmara Eğitim Vakfı",
        "short_name": "MEV",
        "sector": "Eğitim",
        "activity_area": "Özel Okul ve Kurs İşletmeciliği",
        "employee_count": 560,
        "user_count": 7,
    },
]

# Her tenant için 3 ana strateji şablonu (tenant ismi ile özelleştirilecek)
STRATEGY_TEMPLATES = [
    {
        "code_prefix": "ST1",
        "title_template": "Kurumsal Büyüme ve Sürdürülebilirlik",
        "sub_strategies": [
            "Pazar payını artırma",
            "Yeni ürün/hizmet geliştirme",
            "Stratejik ortaklıklar kurma",
            "Gelir çeşitlendirme",
            "Sürdürülebilirlik raporlaması",
        ],
    },
    {
        "code_prefix": "ST2",
        "title_template": "İnsan Kaynakları Mükemmeliyeti",
        "sub_strategies": [
            "Yetenek kazanımı ve tutundurma",
            "Liderlik geliştirme programları",
            "Kurum kültürünü güçlendirme",
            "Çalışan memnuniyeti artırma",
            "Performans yönetimi sistemi kurma",
        ],
    },
    {
        "code_prefix": "ST3",
        "title_template": "Dijital Dönüşüm ve İnovasyon",
        "sub_strategies": [
            "Süreç otomasyonu",
            "Veri analitiği altyapısı",
            "Siber güvenlik güçlendirme",
            "Bulut geçişi",
            "Ar-Ge yatırımları",
        ],
    },
]

# Sektöre göre süreç şablonları
PROCESS_TEMPLATES = {
    "Sağlık": [
        {"code": "SR-01", "name": "Hasta Kabul ve Kayıt Süreci", "doc_no": "DOK-HK-001"},
        {"code": "SR-02", "name": "Tanı ve Tedavi Planlama", "doc_no": "DOK-TP-001"},
        {"code": "SR-03", "name": "İlaç ve Malzeme Yönetimi", "doc_no": "DOK-MY-001"},
        {"code": "SR-04", "name": "Hasta Güvenliği ve Kalite", "doc_no": "DOK-GK-001"},
        {"code": "SR-05", "name": "Faturalandırma ve Tahsilat", "doc_no": "DOK-FT-001"},
    ],
    "Teknoloji": [
        {"code": "SR-01", "name": "Yazılım Geliştirme Yaşam Döngüsü", "doc_no": "DOK-SG-001"},
        {"code": "SR-02", "name": "Müşteri Destek ve Servis", "doc_no": "DOK-MD-001"},
        {"code": "SR-03", "name": "Altyapı ve Operasyon Yönetimi", "doc_no": "DOK-AO-001"},
        {"code": "SR-04", "name": "Satış ve İş Geliştirme", "doc_no": "DOK-SI-001"},
        {"code": "SR-05", "name": "Proje Yönetimi ve Teslimat", "doc_no": "DOK-PY-001"},
    ],
    "Eğitim": [
        {"code": "SR-01", "name": "Öğrenci Kayıt ve Kabul", "doc_no": "DOK-OK-001"},
        {"code": "SR-02", "name": "Müfredat Planlama ve Uygulama", "doc_no": "DOK-MP-001"},
        {"code": "SR-03", "name": "Öğretmen İşe Alım ve Gelişim", "doc_no": "DOK-OI-001"},
        {"code": "SR-04", "name": "Veli İletişim ve Memnuniyet", "doc_no": "DOK-VM-001"},
        {"code": "SR-05", "name": "Tesis ve Lojistik Yönetimi", "doc_no": "DOK-TL-001"},
    ],
}

# Süreç başına KPI havuzu (sektöre göre)
KPI_POOL = {
    "Sağlık": [
        ("Ortalama Hasta Bekleme Süresi", "Dakika", "5", "Decreasing", "Aylık"),
        ("Hasta Memnuniyet Skoru", "%", "90", "Increasing", "Çeyreklik"),
        ("Yatakta Geceleme Süresi (Ort.)", "Gün", "4", "Decreasing", "Aylık"),
        ("Ameliyathane Doluluk Oranı", "%", "85", "Increasing", "Aylık"),
        ("Taburcu Sonrası Readmisyon Oranı", "%", "3", "Decreasing", "Çeyreklik"),
        ("Enfeksiyon Oranı (1000 Hasta/Gün)", "Oran", "1.5", "Decreasing", "Aylık"),
        ("Randevu İptal Edilme Oranı", "%", "8", "Decreasing", "Aylık"),
        ("Tıbbi Hata Raporu Sayısı", "Adet", "0", "Decreasing", "Aylık"),
        ("Sağlık Personeli Devir Oranı", "%", "5", "Decreasing", "Yıllık"),
        ("Sigorta Tahsilat Süresi", "Gün", "30", "Decreasing", "Aylık"),
    ],
    "Teknoloji": [
        ("Sistem Uptime Oranı", "%", "99.9", "Increasing", "Aylık"),
        ("Sprint Velocity", "Story Point", "60", "Increasing", "Aylık"),
        ("Hata Yoğunluğu (Bug/KLoC)", "Adet", "0.5", "Decreasing", "Çeyreklik"),
        ("Müşteri Destek SLA Tutturma", "%", "95", "Increasing", "Aylık"),
        ("Ortalama Çözüm Süresi", "Saat", "4", "Decreasing", "Aylık"),
        ("Kod Kapsamı (Test Coverage)", "%", "80", "Increasing", "Çeyreklik"),
        ("Dağıtım Sıklığı", "Adet/Ay", "8", "Increasing", "Aylık"),
        ("Müşteri Memnuniyeti (NPS)", "Puan", "45", "Increasing", "Çeyreklik"),
        ("Çalışan Başına Gelir", "TL", "250000", "Increasing", "Yıllık"),
        ("Proje Teslimat Süresi", "Gün", "90", "Decreasing", "Çeyreklik"),
    ],
    "Eğitim": [
        ("Öğrenci Devamsızlık Oranı", "%", "3", "Decreasing", "Aylık"),
        ("Öğretmen Memnuniyeti", "Puan", "4.2", "Increasing", "Çeyreklik"),
        ("Başarı Ortalaması (Sınıf)", "Not", "75", "Increasing", "Çeyreklik"),
        ("Kayıt Yenileme Oranı", "%", "92", "Increasing", "Yıllık"),
        ("Veli Memnuniyet Skoru", "%", "88", "Increasing", "Çeyreklik"),
        ("Sınıf Başına Düşen Öğrenci", "Kişi", "25", "Decreasing", "Yıllık"),
        ("Eğitim Materyali Yenileme Oranı", "%", "30", "Increasing", "Yıllık"),
        ("Öğretmen Devir Oranı", "%", "8", "Decreasing", "Yıllık"),
        ("Burs Alan Öğrenci Oranı", "%", "15", "Increasing", "Yıllık"),
        ("Mezun İstihdam Oranı", "%", "80", "Increasing", "Yıllık"),
    ],
}

UNVAN_POOL = ["Müdür", "Direktör", "Uzman", "Analist", "Koordinatör", "Yönetici", "Danışman"]
DEPARTMAN_POOL = ["İnsan Kaynakları", "Bilgi İşlem", "Finans", "Pazarlama", "Operasyon", "Kalite", "Strateji"]

AD_POOL = ["Ahmet", "Mehmet", "Ayşe", "Fatma", "Ali", "Zeynep", "Mustafa", "Emine", "Hüseyin", "Hatice",
           "İbrahim", "Meryem", "Ömer", "Sümeyye", "Yusuf", "Büşra", "Abdurrahman", "Elif", "Murat", "Seda"]
SOYAD_POOL = ["Yılmaz", "Kaya", "Demir", "Şahin", "Çelik", "Doğan", "Erdoğan", "Arslan", "Koç", "Aydın",
              "Özdemir", "Çetin", "Kurt", "Acar", "Bulut", "Güler", "Can", "Yıldız", "Polat", "Güneş"]

PERIODS = ["Aylık", "Çeyreklik", "Yıllık"]
PERIOD_MAP = {
    "Aylık": ("aylik", list(range(1, 13))),
    "Çeyreklik": ("ceyrek", [1, 2, 3, 4]),
    "Yıllık": ("yillik", [1]),
}

# ─── Yardımcı Fonksiyonlar ──────────────────────────────────────────────────────

def rand_float(base, spread_pct=0.3):
    """base değerinin ±spread_pct oranında rastgele değer üretir."""
    base_f = float(base)
    delta = base_f * spread_pct
    val = base_f + random.uniform(-delta, delta)
    # Negatif olmasın
    if val < 0:
        val = abs(val)
    return round(val, 2)


def rand_date_in_year(year, period_type, period_no):
    """Dönem içinde rastgele bir tarih döndürür."""
    if period_type == "aylik":
        month = period_no
        day = random.randint(1, 28)
    elif period_type == "ceyrek":
        month = (period_no - 1) * 3 + random.randint(1, 3)
        day = random.randint(1, 28)
    else:  # yillik
        month = random.randint(1, 12)
        day = random.randint(1, 28)
    try:
        return date(year, month, day)
    except ValueError:
        return date(year, month, 28)


def hash_password(plain):
    from werkzeug.security import generate_password_hash
    return generate_password_hash(plain)


def username_from(first, last, idx):
    return f"{first.lower()[:3]}{last.lower()[:4]}{idx}".replace("ı", "i").replace("ş", "s").replace("ğ", "g").replace("ü", "u").replace("ö", "o").replace("ç", "c")


# ─── Ana Seed Fonksiyonu ───────────────────────────────────────────────────────

def seed():
    app = create_app()
    with app.app_context():

        # ── Admin rolünü bul ──────────────────────────────
        role_user = Role.query.filter(Role.name.in_(["Kullanıcı", "User", "user"])).first()
        role_admin = Role.query.filter(Role.name.in_(["Admin", "admin", "Yönetici"])).first()
        if not role_user:
            role_user = Role(name="Kullanıcı", description="Standart kullanıcı")
            db.session.add(role_user)
            db.session.flush()
        if not role_admin:
            role_admin = Role(name="Admin", description="Yönetici")
            db.session.add(role_admin)
            db.session.flush()

        total_kpi_data = 0
        total_kpis = 0
        total_processes = 0

        for t_idx, t_def in enumerate(TENANTS):
            print(f"\n{'='*60}")
            print(f"🏢  Kurum: {t_def['name']}")
            print(f"{'='*60}")

            # ── Tenant ──────────────────────────────────────────────
            tenant = Tenant.query.filter_by(short_name=t_def["short_name"]).first()
            if not tenant:
                tenant = Tenant(
                    name=t_def["name"],
                    short_name=t_def["short_name"],
                    sector=t_def["sector"],
                    activity_area=t_def["activity_area"],
                    employee_count=t_def["employee_count"],
                    max_user_count=50,
                    is_active=True,
                )
                db.session.add(tenant)
                db.session.flush()
                print(f"  ✅ Tenant oluşturuldu: {tenant.name} (ID={tenant.id})")
            else:
                print(f"  ⚠️  Tenant zaten mevcut: {tenant.name} (ID={tenant.id})")

            # ── Kullanıcılar ─────────────────────────────────────────
            user_count = t_def["user_count"]
            existing_users = User.query.filter_by(tenant_id=tenant.id).all()
            seed_users = []

            if len(existing_users) >= user_count:
                seed_users = existing_users[:user_count]
                print(f"  ⚠️  {len(seed_users)} kullanıcı zaten mevcut, mevcut kullanıcılar kullanılıyor.")
            else:
                # Mevcut kullanıcıları da kullan
                seed_users.extend(existing_users)
                to_create = user_count - len(existing_users)
                used_names = set()

                for u_idx in range(to_create):
                    while True:
                        first = random.choice(AD_POOL)
                        last = random.choice(SOYAD_POOL)
                        uname = username_from(first, last, u_idx)
                        if uname not in used_names:
                            used_names.add(uname)
                            break

                    email = f"{uname}@{t_def['short_name'].lower().replace('-', '')}.demo.tr"
                    # Email çakışmasını önle
                    if User.query.filter_by(email=email).first():
                        email = f"{uname}{random.randint(10,99)}@{t_def['short_name'].lower()}.demo.tr"

                    new_user = User(
                        email=email,
                        password_hash=hash_password("Demo2024!"),
                        first_name=first,
                        last_name=last,
                        tenant_id=tenant.id,
                        role_id=role_user.id,
                        job_title=random.choice(UNVAN_POOL),
                        department=random.choice(DEPARTMAN_POOL),
                        is_active=True,
                    )
                    db.session.add(new_user)
                    db.session.flush()
                    seed_users.append(new_user)
                    print(f"  👤 Kullanıcı: {first} {last} <{email}>")

            # ── Stratejiler ──────────────────────────────────────────
            all_sub_strategies = []
            for s_idx, s_tmpl in enumerate(STRATEGY_TEMPLATES):
                code = f"{s_tmpl['code_prefix']}"
                # Mevcut strategy kontrolü
                strat = Strategy.query.filter_by(tenant_id=tenant.id, code=code).first()
                if not strat:
                    strat = Strategy(
                        tenant_id=tenant.id,
                        code=code,
                        title=s_tmpl["title_template"],
                        description=f"{t_def['name']} için {s_tmpl['title_template'].lower()} kapsamındaki stratejik hedefler.",
                        is_active=True,
                    )
                    db.session.add(strat)
                    db.session.flush()
                    print(f"  📌 Strateji: [{code}] {strat.title}")

                # Alt stratejiler
                for ss_idx, ss_title in enumerate(s_tmpl["sub_strategies"]):
                    ss_code = f"{code}.{ss_idx + 1}"
                    ss = SubStrategy.query.filter_by(strategy_id=strat.id, code=ss_code).first()
                    if not ss:
                        ss = SubStrategy(
                            strategy_id=strat.id,
                            code=ss_code,
                            title=ss_title,
                            description=f"{ss_title} kapsamında yürütülecek faaliyetler.",
                            is_active=True,
                        )
                        db.session.add(ss)
                        db.session.flush()
                    all_sub_strategies.append(ss)

            print(f"  📊 Toplam {len(all_sub_strategies)} alt strateji hazır.")

            # ── Süreçler ─────────────────────────────────────────────
            process_templates = PROCESS_TEMPLATES.get(t_def["sector"], PROCESS_TEMPLATES["Teknoloji"])
            kpi_pool = KPI_POOL.get(t_def["sector"], KPI_POOL["Teknoloji"])

            for p_templ in process_templates:
                # Mevcut süreç kontrolü
                proc = Process.query.filter_by(tenant_id=tenant.id, code=p_templ["code"]).first()
                if not proc:
                    proc = Process(
                        tenant_id=tenant.id,
                        code=p_templ["code"],
                        name=p_templ["name"],
                        document_no=p_templ["doc_no"],
                        revision_no=f"V{random.randint(1,3)}",
                        description=f"{p_templ['name']} kapsamındaki tüm adımları, sorumlulukları ve kontrol noktalarını tanımlar.",
                        status="Aktif",
                        progress=random.randint(20, 90),
                        is_active=True,
                        start_date=date(2024, 1, 1),
                    )
                    db.session.add(proc)
                    db.session.flush()
                total_processes += 1

                print(f"\n  🔄 Süreç: [{p_templ['code']}] {p_templ['name']}")

                # ── KPI'lar ─────────────────────────────────────────
                # Bu süreç için mevcut KPI sayısını kontrol et
                existing_kpi_count = ProcessKpi.query.filter_by(process_id=proc.id, is_active=True).count()
                if existing_kpi_count > 0:
                    print(f"     ⚠️  {existing_kpi_count} KPI zaten mevcut, SEED atlanıyor.")
                    continue

                kpi_count = random.randint(1, min(10, len(kpi_pool)))
                selected_kpis = random.sample(kpi_pool, kpi_count)

                # Süreç sahibi (random user)
                owner_user = random.choice(seed_users)

                for k_idx, (kpi_name, unit, target, direction, period) in enumerate(selected_kpis):
                    code_prefix = p_templ["code"].replace("SR-", "PG-")
                    kpi_code = f"{code_prefix}{k_idx+1:02d}"

                    # Alt strateji ata (rastgele)
                    sub_strat = random.choice(all_sub_strategies)

                    # Başarı puanı aralıkları (bazen boş, bazen dolu)
                    basari_araliklari = None
                    if random.random() > 0.5:
                        basari_araliklari = json.dumps({
                            "1": "0-40",
                            "2": "40-60",
                            "3": "60-80",
                            "4": "80-95",
                            "5": "95-",
                        })

                    kpi = ProcessKpi(
                        process_id=proc.id,
                        name=kpi_name,
                        code=kpi_code,
                        target_value=target,
                        unit=unit,
                        period=period,
                        direction=direction,
                        weight=round(random.uniform(5, 30), 1),
                        data_collection_method=random.choice(["Ortalama", "Toplama", "Son Değer"]),
                        gosterge_turu=random.choice(["İyileştirme", "Koruma", "Bilgi Amaçlı"]),
                        target_method=random.choice(["SH", "DH", "HKY", "RG"]),
                        basari_puani_araliklari=basari_araliklari,
                        onceki_yil_ortalamasi=rand_float(target),
                        sub_strategy_id=sub_strat.id,
                        is_active=True,
                    )
                    db.session.add(kpi)
                    db.session.flush()
                    total_kpis += 1

                    # ── KPI Verisi ─────────────────────────────────
                    period_type_key, period_nos = PERIOD_MAP[period]
                    kpi_data_count = 0

                    for year in [2024, 2025, 2026]:
                        # Bu yıl için kaç veri girilecek
                        n_entries = random.randint(10, 30)
                        # Veriyi dönem bazlı dağıt
                        # Toplam dönem sayısı
                        all_period_slots = [(pno,) for pno in period_nos]
                        # n_entries dönemlere rastgele dağıtılır (tekrarlı olabilir)
                        for _ in range(n_entries):
                            period_no = random.choice(all_period_slots)[0]
                            actual_val = rand_float(target)
                            entry_date = rand_date_in_year(year, period_type_key, period_no)

                            # 2026 için gelecek tarih kontrolü — bugün 2026-02-22
                            if year == 2026 and entry_date > date(2026, 2, 22):
                                entry_date = date(2026, random.randint(1, 2), random.randint(1, 22))

                            data_entry = KpiData(
                                process_kpi_id=kpi.id,
                                year=year,
                                data_date=entry_date,
                                period_type=period_type_key,
                                period_no=period_no,
                                target_value=target,
                                actual_value=str(actual_val),
                                description=f"{year} yılı {period} {period_no}. dönem veri girişi.",
                                user_id=owner_user.id,
                            )
                            db.session.add(data_entry)
                            kpi_data_count += 1
                            total_kpi_data += 1

                    print(f"     📈 PG: [{kpi_code}] {kpi_name[:35]:<35} | {period:<10} | Hedef: {target:<8} | {kpi_data_count} veri")

                # ── Faaliyetler (süreç başına 2-4 adet) ────────────
                act_count = random.randint(2, 4)
                act_names_pool = [
                    f"{p_templ['name']} süreç iyileştirme projesi",
                    "Personel eğitim programı hazırlama",
                    "Prosedür dokümantasyonu güncelleme",
                    "Paydaş analizi ve geri bildirim toplama",
                    "Teknoloji altyapısı yenileme",
                    "Sistem entegrasyon çalışması",
                    "İç denetim ve uyumluluk kontrolü",
                ]
                for a_idx in range(act_count):
                    act_name = random.choice(act_names_pool)
                    start_m = random.randint(1, 6)
                    end_m = random.randint(start_m + 1, 12)
                    status = random.choice(["Planlandı", "Devam Ediyor", "Tamamlandı", "Planlandı"])
                    act = ProcessActivity(
                        process_id=proc.id,
                        name=act_name,
                        description=f"{p_templ['name']} kapsamında yürütülen faaliyet.",
                        start_date=date(2025, start_m, 1),
                        end_date=date(2025, end_m, 28),
                        status=status,
                        progress=100 if status == "Tamamlandı" else random.randint(0, 80),
                        is_active=True,
                    )
                    db.session.add(act)

            db.session.commit()
            print(f"\n  ✅ {t_def['name']} için commit tamamlandı!")

        print("\n" + "="*60)
        print("🎉  SEED TAMAMLANDI!")
        print(f"   Kurumlar  : {len(TENANTS)}")
        print(f"   Süreçler  : {total_processes}")
        print(f"   KPI'lar   : {total_kpis}")
        print(f"   KPI Veri  : {total_kpi_data:,}")
        print("="*60)


if __name__ == "__main__":
    seed()
