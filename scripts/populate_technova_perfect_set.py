# -*- coding: utf-8 -*-
"""
Technova kurumu için veritabanındaki TÜM tabloları kapsayan, hiçbir alanı NULL bırakmayan
ve %100 ilişkisel veri seti oluşturur.

Eşleme: Tenant=Kurum, StrategicGoal=AnaStrateji/AltStrateji, Process=Surec,
KPI=SurecPerformansGostergesi, ActualValue=PerformansGostergeVeri (BireyselPerformansGostergesi üzerinden).

Çalıştırma: python scripts/populate_technova_perfect_set.py
"""
import sys
import random
from pathlib import Path
from datetime import datetime, date, timedelta

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Audit log'u devre dışı bırak (request context yok)
try:
    import services.audit_service as audit_svc
    audit_svc._create_log = lambda mapper, connection, target, action, changes: None
    audit_svc._register_model = lambda model_cls: None
except Exception:
    pass

from __init__ import create_app
from extensions import db
from werkzeug.security import generate_password_hash

from models import (
    Kurum, User, AnaStrateji, AltStrateji, Surec, SurecPerformansGostergesi,
    BireyselPerformansGostergesi, PerformansGostergeVeri, AnalysisItem, TowsMatrix,
    Deger, EtikKural, KalitePolitikasi, StrategyMapLink, StrategyProcessMatrix,
)
from models.process import surec_uyeleri, surec_liderleri, surec_alt_stratejiler, process_owners

# Sabitler
TECHNOVA_KISA_AD = "Technova"
PASSWORD = "Tech123!"
KURUM_EMAIL = "info@technova.com.tr"
KURUM_WEB = "https://www.technova.com.tr"
KURUM_TELEFON = "+90 212 555 0000"
KURUM_ADRES = "Maslak Mah. Eski Büyükdere Cad. No:1 Kat:15 Sarıyer / İstanbul"
VERGI_DAIRESI = "Sarıyer Vergi Dairesi"
VERGI_NO = "1234567890"
CALISAN_SAYISI = 85
SEKTOR = "Teknoloji / Yazılım"

USER_DEFS = [
    {"username": "kurumadmin", "sistem_rol": "admin", "first_name": "Teknik", "last_name": "Yönetici", "title": "Kurum Yöneticisi", "department": "Genel Yönetim"},
    {"username": "strateji_muduru", "sistem_rol": "ust_yonetim", "first_name": "Strateji", "last_name": "Müdürü", "title": "Strateji Müdürü", "department": "Strateji"},
    {"username": "ik_uzmani", "sistem_rol": "kurum_kullanici", "first_name": "İnsan", "last_name": "Kaynakları", "title": "İK Uzmanı", "department": "İnsan Kaynakları"},
    {"username": "operasyon_lideri", "sistem_rol": "surec_lideri", "first_name": "Operasyon", "last_name": "Lideri", "title": "Operasyon Lideri", "department": "Operasyon"},
    {"username": "finans_direktoru", "sistem_rol": "kurum_yoneticisi", "first_name": "Finans", "last_name": "Direktörü", "title": "Finans Direktörü", "department": "Finans"},
]

SWOT_STRENGTHS = [
    "Güçlü yazılım geliştirme ekibi ve Agile metodolojisi",
    "Patentli ürün portföyü ve Ar-Ge yetkinliği",
    "Yüksek müşteri memnuniyeti ve tekrarlayan gelir modeli",
    "Bulut ve DevOps altyapısı deneyimi",
    "Uluslararası sertifikasyonlar ve kalite yönetim sistemi",
]
SWOT_WEAKNESSES = [
    "Pazarlama bütçesinin sınırlı olması",
    "Bazı kritik rollerde personel açığı",
    "Legacy sistemlere bağımlılık",
    "Uzun satış döngüsü ve karar verme süreçleri",
    "Coğrafi olarak sınırlı satış ağı",
]
SWOT_OPPORTUNITIES = [
    "SaaS ve bulut hizmetlerinde büyüme talebi",
    "Devlet ve KOSGEB destekleri",
    "Uzaktan çalışma ile yetenek havuzunun genişlemesi",
    "Dijital dönüşüm projelerinde artan bütçeler",
    "Stratejik ortaklık ve M&A fırsatları",
]
SWOT_THREATS = [
    "Küresel rakiplerin pazara girişi",
    "Döviz kuru ve enflasyon baskısı",
    "Siber güvenlik ve veri ihlali riskleri",
    "Yasal düzenlemeler (KVKK, GDPR) uyum maliyeti",
    "Yetenek savaşı ve personel maliyetleri",
]

# 4 ana stratejik eksen (perspective: FINANSAL, MUSTERI, SUREC, OGRENME)
ANA_STRATEJI_DEFS = [
    ("F", "Finansal Mükemmellik", "FINANSAL", "Gelir büyümesi, maliyet kontrolü ve karlılık."),
    ("M", "Müşteri Odaklılık", "MUSTERI", "Müşteri deneyimi, sadakat ve pazar payı."),
    ("S", "Operasyonel Mükemmellik", "SUREC", "Süreç verimliliği, kalite ve teslimat."),
    ("D", "Dijital Dönüşüm", "OGRENME", "Teknoloji, inovasyon ve öğrenen organizasyon."),
]

# Her ana strateji için en az 3 alt hedef (2025-2027)
ALT_STRATEJI_DEFS = [
    ("F", ["Yıllık ciro hedefi %20 artış", "Operasyonel maliyetlerde %10 tasarruf", "Net kar marjı %15"]),
    ("M", ["Müşteri memnuniyet skoru 4.5/5", "Müşteri elde tutma oranı %95", "Yeni müşteri kazanımı yıllık %25"]),
    ("S", ["Proje teslimat zamanında tamamlama %90", "İç süreç verimliliği %15 artış", "Kalite iade oranı %1 altı"]),
    ("D", ["Ar-Ge yatırımı gelirin %8'i", "Dijital ürün portföyü 3 yeni ürün", "Çalışan dijital yetkinlik eğitimleri"]),
]

# 10 ana süreç
SUREc_DEFS = [
    ("SR01", "Yazılım Geliştirme", "Yazılım Geliştirme", "Ürün ve proje geliştirme süreçleri.", 0.15),
    ("SR02", "Müşteri Deneyimi", "Müşteri Deneyimi", "Müşteri ilişkileri ve deneyim yönetimi.", 0.12),
    ("SR03", "İnsan Kaynakları", "İnsan Kaynakları", "İşe alım, eğitim ve performans.", 0.10),
    ("SR04", "Finans Yönetimi", "Finans Yönetimi", "Mali raporlama, bütçe ve nakit akışı.", 0.12),
    ("SR05", "Satış & Pazarlama", "Satış ve Pazarlama", "Satış kanalları ve pazarlama kampanyaları.", 0.12),
    ("SR06", "AR-GE", "AR-GE", "Araştırma ve yenilik projeleri.", 0.10),
    ("SR07", "BT Altyapı", "BT Altyapı", "Altyapı, güvenlik ve operasyon.", 0.09),
    ("SR08", "Kalite Yönetimi", "Kalite Yönetimi", "Kalite standartları ve sürekli iyileştirme.", 0.10),
    ("SR09", "Lojistik", "Lojistik", "Tedarik, depo ve dağıtım.", 0.05),
    ("SR10", "Hukuk & Uyum", "Hukuk ve Uyum", "Yasal uyum ve sözleşme yönetimi.", 0.05),
]

# Süreç başına 10 KPI şablonu: (ad, birim, yön, hedef_metin, veri_kaynagi)
KPI_TEMPLATES = [
    ("Tamamlama Oranı", "%", "Increasing", "90", "Proje yönetim sistemi"),
    ("Ortalama Teslimat Süresi", "Gün", "Decreasing", "15", "Jira/Redmine"),
    ("Hata Oranı", "%", "Decreasing", "2", "Test raporları"),
    ("Müşteri Memnuniyeti", "Puan", "Increasing", "4.5", "Anket"),
    ("Süreç Verimliliği", "%", "Increasing", "85", "İş zekası"),
    ("Maliyet Sapması", "%", "Decreasing", "5", "Muhasebe"),
    ("Gelir Hedefi", "TL", "Increasing", "1000000", "CRM/Satış"),
    ("Eğitim Saati", "Saat", "Increasing", "40", "LMS"),
    ("İşlem Adedi", "Adet", "Increasing", "500", "Operasyon"),
    ("Uyum Skoru", "Puan", "Increasing", "95", "Denetim"),
]


def _wipe_technova_strategic_data(kurum_id):
    """Technova'nın strateji, analiz, süreç, KPI ve performans verilerini siler (Kurum ve User kalır)."""
    from models import PerformansGostergeVeriAudit, FavoriKPI, SurecFaaliyet
    # BPG ve PGV (kurum kullanıcıları üzerinden)
    user_ids = [u.id for u in User.query.filter_by(kurum_id=kurum_id).all()]
    for uid in user_ids:
        bpg_ids = [r.id for r in BireyselPerformansGostergesi.query.filter_by(user_id=uid).all()]
        if bpg_ids:
            pg_veri_ids = [r.id for r in PerformansGostergeVeri.query.filter(
                PerformansGostergeVeri.bireysel_pg_id.in_(bpg_ids)).all()]
            if pg_veri_ids:
                PerformansGostergeVeriAudit.query.filter(
                    PerformansGostergeVeriAudit.pg_veri_id.in_(pg_veri_ids)).delete(synchronize_session=False)
            PerformansGostergeVeri.query.filter(
                PerformansGostergeVeri.bireysel_pg_id.in_(bpg_ids)).delete(synchronize_session=False)
        BireyselPerformansGostergesi.query.filter_by(user_id=uid).delete(synchronize_session=False)
        FavoriKPI.query.filter_by(user_id=uid).delete(synchronize_session=False)
    surec_ids = [s.id for s in Surec.query.filter_by(kurum_id=kurum_id).all()]
    if surec_ids:
        FavoriKPI.query.filter(FavoriKPI.surec_pg_id.in_(
            db.session.query(SurecPerformansGostergesi.id).filter(SurecPerformansGostergesi.surec_id.in_(surec_ids))
        )).delete(synchronize_session=False)
        SurecPerformansGostergesi.query.filter(SurecPerformansGostergesi.surec_id.in_(surec_ids)).delete(synchronize_session=False)
        SurecFaaliyet.query.filter(SurecFaaliyet.surec_id.in_(surec_ids)).delete(synchronize_session=False)
        StrategyProcessMatrix.query.filter(StrategyProcessMatrix.process_id.in_(surec_ids)).delete(synchronize_session=False)
        db.session.execute(surec_uyeleri.delete().where(surec_uyeleri.c.surec_id.in_(surec_ids)))
        db.session.execute(surec_liderleri.delete().where(surec_liderleri.c.surec_id.in_(surec_ids)))
        db.session.execute(surec_alt_stratejiler.delete().where(surec_alt_stratejiler.c.surec_id.in_(surec_ids)))
        db.session.execute(process_owners.delete().where(process_owners.c.process_id.in_(surec_ids)))
    Surec.query.filter_by(kurum_id=kurum_id).delete(synchronize_session=False)
    ana_ids = [a.id for a in AnaStrateji.query.filter_by(kurum_id=kurum_id).all()]
    if ana_ids:
        StrategyMapLink.query.filter(db.or_(
            StrategyMapLink.source_id.in_(ana_ids), StrategyMapLink.target_id.in_(ana_ids)
        )).delete(synchronize_session=False)
        AltStrateji.query.filter(AltStrateji.ana_strateji_id.in_(ana_ids)).delete(synchronize_session=False)
    AnaStrateji.query.filter_by(kurum_id=kurum_id).delete(synchronize_session=False)
    AnalysisItem.query.filter_by(kurum_id=kurum_id).delete(synchronize_session=False)
    TowsMatrix.query.filter_by(kurum_id=kurum_id).delete(synchronize_session=False)
    Deger.query.filter_by(kurum_id=kurum_id).delete(synchronize_session=False)
    EtikKural.query.filter_by(kurum_id=kurum_id).delete(synchronize_session=False)
    KalitePolitikasi.query.filter_by(kurum_id=kurum_id).delete(synchronize_session=False)
    db.session.commit()


def _ensure_technova_and_users(app):
    """Kurum ve 5 kullanıcıyı bul veya oluştur. (Mevcut Technova varsa güncelleme yapılmaz, sadece döndürülür.)"""
    kurum = Kurum.query.filter(Kurum.kisa_ad.ilike(TECHNOVA_KISA_AD)).first()
    if not kurum:
        kurum = Kurum(
            kisa_ad=TECHNOVA_KISA_AD,
            ticari_unvan="Technova Bilişim ve Yazılım Teknolojileri A.Ş.",
            faaliyet_alani="Yazılım Geliştirme, SaaS, Kurumsal Danışmanlık",
            adres=KURUM_ADRES,
            il="İstanbul",
            ilce="Sarıyer",
            email=KURUM_EMAIL,
            web_adresi=KURUM_WEB,
            telefon=KURUM_TELEFON,
            calisan_sayisi=CALISAN_SAYISI,
            sektor=SEKTOR,
            vergi_dairesi=VERGI_DAIRESI,
            vergi_numarasi=VERGI_NO,
            logo_url="https://ui-avatars.com/api/?name=Technova&background=0ea5e9&color=fff&size=128",
            amac="Yenilikçi yazılım çözümleri ile müşteri değeri yaratmak ve sürdürülebilir büyüme sağlamak.",
            vizyon="Türkiye ve bölgede teknoloji ile iş dünyasını dönüştüren lider şirket olmak.",
            stratejik_profil="BSC ile yönetilen, süreç ve müşteri odaklı teknoloji firması.",
            stratejik_durum="tamamlandi",
            stratejik_son_guncelleme=datetime.utcnow(),
            show_guide_system=True,
            silindi=False,
            deleted_at=None,
            deleted_by=None,
        )
        db.session.add(kurum)
        db.session.flush()
    users = {}
    # Mevcut kurum kullanıcılarını yükle (sonradan doldurmak için)
    for u in User.query.filter_by(kurum_id=kurum.id).all():
        users[u.username] = u
    pw_hash = generate_password_hash(PASSWORD)
    for udef in USER_DEFS:
        u = User.query.filter(User.username == udef["username"], User.kurum_id == kurum.id).first()
        if not u:
            email = f"{udef['username']}@technova.com.tr"
            if User.query.filter_by(email=email).first():
                email = f"{udef['username']}_tn@technova.com.tr"
            u = User(
                username=udef["username"],
                email=email,
                password_hash=pw_hash,
                first_name=udef["first_name"],
                last_name=udef["last_name"],
                phone=KURUM_TELEFON,
                title=udef["title"],
                department=udef["department"],
                sistem_rol=udef["sistem_rol"],
                surec_rol="surec_lideri" if udef["sistem_rol"] == "surec_lideri" else None,
                kurum_id=kurum.id,
                profile_photo=f"https://ui-avatars.com/api/?name={udef['first_name'][:1]}+{udef['last_name'][:1]}&background=0ea5e9&color=fff",
                theme_preferences='{"theme":"light","color":"blue"}',
                layout_preference="classic",
                guide_character_style="professional",
                show_page_guides=True,
                completed_walkthroughs="{}",
                silindi=False,
                deleted_at=None,
                deleted_by=None,
            )
            db.session.add(u)
            db.session.flush()
        users[udef["username"]] = u
    db.session.commit()
    db.session.refresh(kurum)
    for uname in users:
        db.session.refresh(users[uname])
    return kurum, users


def _add_deger_etik_kalite(kurum_id):
    """Kurum değerleri, etik kurallar ve kalite politikası."""
    # _wipe zaten sildiği için her zaman ekle
    degerler = [
        ("Yenilikçilik", "Sürekli gelişim ve teknolojik yenilikleri takip ederiz."),
        ("Müşteri Odaklılık", "Müşteri başarısı bizim başarımızdır."),
        ("Şeffaflık", "İletişimde açıklık ve hesap verebilirlik."),
        ("Takım Ruhu", "İşbirliği ve ortak hedeflerle çalışırız."),
    ]
    for baslik, aciklama in degerler:
        db.session.add(Deger(kurum_id=kurum_id, baslik=baslik, aciklama=aciklama))
    etik = [
        ("Dürüstlük", "Tüm iş ilişkilerinde dürüstlük ve doğruluk esas alınır."),
        ("Çıkar Çatışması", "Çıkar çatışması yaratacak durumlardan kaçınılır."),
        ("Gizlilik", "Müşteri ve şirket bilgileri gizli tutulur."),
    ]
    for baslik, aciklama in etik:
        db.session.add(EtikKural(kurum_id=kurum_id, baslik=baslik, aciklama=aciklama))
    db.session.add(KalitePolitikasi(
        kurum_id=kurum_id,
        baslik="Kalite Politikası",
        aciklama="ISO 9001 ve müşteri gereksinimlerine uygun, sürekli iyileştirme odaklı kalite politikası uygulanır."
    ))
    db.session.commit()


def _add_swot_and_tows(kurum_id):
    """SWOT: 5 Güçlü, 5 Zayıf, 5 Fırsat, 5 Tehdit. TOWS için strength/opportunity-threat ID'leri döner."""
    categories = [
        ("Strengths", SWOT_STRENGTHS),
        ("Weaknesses", SWOT_WEAKNESSES),
        ("Opportunities", SWOT_OPPORTUNITIES),
        ("Threats", SWOT_THREATS),
    ]
    strength_ids = []
    opportunity_ids = []
    threat_ids = []
    for cat, items in categories:
        for content in items:
            score = random.randint(3, 5) if cat in ("Strengths", "Opportunities") else random.randint(2, 4)
            item = AnalysisItem(
                kurum_id=kurum_id,
                analysis_type="SWOT",
                category=cat,
                content=content,
                score=score,
            )
            db.session.add(item)
            db.session.flush()
            if cat == "Strengths":
                strength_ids.append(item.id)
            elif cat == "Opportunities":
                opportunity_ids.append(item.id)
            elif cat == "Threats":
                threat_ids.append(item.id)
    db.session.commit()
    # TOWS: Strength-Opportunity ve Strength-Threat çiftleri
    all_s = AnalysisItem.query.filter_by(kurum_id=kurum_id, analysis_type="SWOT", category="Strengths").all()
    all_o = AnalysisItem.query.filter_by(kurum_id=kurum_id, analysis_type="SWOT", category="Opportunities").all()
    all_t = AnalysisItem.query.filter_by(kurum_id=kurum_id, analysis_type="SWOT", category="Threats").all()
    for i, s in enumerate(all_s[:3]):
        o = all_o[i % len(all_o)] if all_o else None
        if o:
            db.session.add(TowsMatrix(
                kurum_id=kurum_id,
                strength_id=s.id,
                opportunity_threat_id=o.id,
                strategy_text=f"{s.content} gücünü kullanarak {o.content} fırsatını değerlendir.",
                action_plan="Stratejik proje ve bütçe planlaması yapılacak.",
            ))
    for i, s in enumerate(all_s[:2]):
        t = all_t[i % len(all_t)] if all_t else None
        if t:
            db.session.add(TowsMatrix(
                kurum_id=kurum_id,
                strength_id=s.id,
                opportunity_threat_id=t.id,
                strategy_text=f"{s.content} ile {t.content} tehdidini azalt.",
                action_plan="Risk eylem planı güncellenecek.",
            ))
    db.session.commit()


def _add_strategies_and_links(kurum_id):
    """4 ana strateji, her biri için 3 alt strateji, StrategyMapLink. Ana/Alt strateji listelerini döndürür."""
    ana_map = {}
    for code, ad, perspective, aciklama in ANA_STRATEJI_DEFS:
        a = AnaStrateji(
            kurum_id=kurum_id,
            code=code,
            ad=ad,
            name=ad,
            aciklama=aciklama,
            perspective=perspective,
            bsc_code=code,
        )
        db.session.add(a)
        db.session.flush()
        ana_map[code] = a
    db.session.commit()
    alt_by_ana = {a.id: [] for a in ana_map.values()}
    for ana_code, alt_ads in ALT_STRATEJI_DEFS:
        ana = ana_map.get(ana_code)
        if not ana:
            continue
        for i, ad in enumerate(alt_ads):
            code = f"{ana_code}{i+1}"
            alt = AltStrateji(
                ana_strateji_id=ana.id,
                code=code,
                ad=ad,
                name=ad,
                target_method="HKY",
                aciklama=f"2025-2027 dönemi hedefi: {ad}",
            )
            db.session.add(alt)
            db.session.flush()
            alt_by_ana[ana.id].append(alt)
    db.session.commit()
    # StrategyMapLink: F -> M -> S -> D (neden-sonuç)
    ana_list = list(ana_map.values())
    for i in range(len(ana_list) - 1):
        link = StrategyMapLink(
            source_id=ana_list[i].id,
            target_id=ana_list[i + 1].id,
            connection_type="CAUSE_EFFECT",
        )
        db.session.add(link)
    db.session.commit()
    return ana_list, alt_by_ana


def _add_processes_and_kpis(kurum_id, users):
    """10 süreç, her süreçte 10 KPI. Süreç ve KPI listelerini döndürür."""
    procs = []
    all_kpis = []
    for code, ad, name, aciklama, weight in SUREc_DEFS:
        p = Surec(
            kurum_id=kurum_id,
            code=code,
            ad=ad,
            name=name,
            weight=weight,
            dokuman_no=f"SR-{code}",
            rev_no="01",
            rev_tarihi=date.today(),
            ilk_yayin_tarihi=date(2024, 1, 1),
            durum="Aktif",
            ilerleme=random.randint(60, 95),
            baslangic_siniri="Süreç giriş kriterleri",
            bitis_siniri="Süreç çıkış kriterleri",
            baslangic_tarihi=date(2024, 1, 1),
            bitis_tarihi=date(2027, 12, 31),
            aciklama=aciklama,
            silindi=False,
            deleted_at=None,
            deleted_by=None,
        )
        db.session.add(p)
        db.session.flush()
        procs.append(p)
        for idx, (kpi_ad, birim, yon, hedef_txt, veri_kaynak) in enumerate(KPI_TEMPLATES):
            kodu = f"{code}-PG{idx+1:02d}"
            pg = SurecPerformansGostergesi(
                surec_id=p.id,
                ad=f"{ad} - {kpi_ad}",
                aciklama=f"{kpi_ad} performans göstergesi. Veri kaynağı: {veri_kaynak}.",
                kodu=kodu,
                hedef_deger=hedef_txt,
                olcum_birimi=birim,
                periyot="Aylık",
                veri_alinacak_yer=veri_kaynak,
                hedef_belirleme_yontemi="Geçmiş veri ve hedef belirleme",
                veri_toplama_yontemi="Ortalama",
                calculation_method="AVG",
                agirlik=10,
                onemli=(idx % 3 == 0),
                direction=yon,
                gosterge_turu="Sonuç",
                basari_puani=80,
                agirlikli_basari_puani=8.0,
                target_method="HKY",
                unit=birim,
                baslangic_tarihi=date(2024, 1, 1),
                bitis_tarihi=date(2027, 12, 31),
            )
            db.session.add(pg)
            db.session.flush()
            all_kpis.append((p, pg))
    db.session.commit()
    return procs, all_kpis


def _link_processes_strategy_and_users(kurum_id, procs, alt_by_ana, users):
    """surec_alt_stratejiler, surec_liderleri, surec_uyeleri, process_owners ve StrategyProcessMatrix."""
    ana_list = AnaStrateji.query.filter_by(kurum_id=kurum_id).order_by(AnaStrateji.id).all()
    alt_list = []
    for a in ana_list:
        alt_list.extend(AltStrateji.query.filter_by(ana_strateji_id=a.id).all())
    user_list = list(users.values())
    for i, p in enumerate(procs):
        # Süreç sahibi ve lider
        u_owner = user_list[i % len(user_list)]
        u_lider = user_list[(i + 1) % len(user_list)]
        db.session.execute(process_owners.insert().values(process_id=p.id, user_id=u_owner.id))
        db.session.execute(surec_liderleri.insert().values(surec_id=p.id, user_id=u_lider.id))
        db.session.execute(surec_uyeleri.insert().values(surec_id=p.id, user_id=u_owner.id))
        if u_lider.id != u_owner.id:
            db.session.execute(surec_uyeleri.insert().values(surec_id=p.id, user_id=u_lider.id))
        # Alt strateji ilişkisi (her sürece 1-2 alt strateji)
        for j, alt in enumerate(alt_list):
            if (i + j) % 4 == 0 or (i + j) % 4 == 1:
                try:
                    db.session.execute(surec_alt_stratejiler.insert().values(surec_id=p.id, alt_strateji_id=alt.id))
                except Exception:
                    pass
        # StrategyProcessMatrix: alt strateji - süreç (skor 3 veya 9)
        for alt in alt_list[:6]:
            try:
                db.session.add(StrategyProcessMatrix(
                    sub_strategy_id=alt.id,
                    process_id=p.id,
                    relationship_strength=9 if (i + alt.id) % 3 == 0 else 3,
                    relationship_score=9 if (i + alt.id) % 3 == 0 else 3,
                ))
            except Exception:
                pass
    db.session.commit()


def _add_bpg_and_actual_values(kurum_id, process_kpis, admin_user):
    """Her süreç KPI'sı için bir BireyselPerformansGostergesi (kurumadmin'e) ve 2024 12 ay PerformansGostergeVeri."""
    for p, pg in process_kpis:
        bpg = BireyselPerformansGostergesi(
            user_id=admin_user.id,
            ad=pg.ad,
            aciklama=pg.aciklama or "",
            kodu=pg.kodu,
            hedef_deger=pg.hedef_deger,
            gerceklesen_deger=pg.hedef_deger,
            olcum_birimi=pg.olcum_birimi,
            periyot=pg.periyot,
            agirlik=pg.agirlik or 0,
            onemli=pg.onemli or False,
            baslangic_tarihi=pg.baslangic_tarihi or date(2024, 1, 1),
            bitis_tarihi=pg.bitis_tarihi or date(2027, 12, 31),
            durum="Devam Ediyor",
            kaynak="Süreç",
            kaynak_surec_id=p.id,
            kaynak_surec_pg_id=pg.id,
        )
        db.session.add(bpg)
        db.session.flush()
        # 2024 12 ay veri
        is_increasing = (pg.direction or "Increasing") == "Increasing"
        hedef_val = pg.hedef_deger or "0"
        try:
            hedef_float = float(hedef_val.replace(",", "."))
        except ValueError:
            hedef_float = 80.0
        for ay in range(1, 13):
            veri_tarihi = date(2024, ay, 15)
            # Hedef civarında korelasyonlu gerçekleşen
            r = random.uniform(0.85, 1.08) if is_increasing else random.uniform(0.92, 1.02)
            gercek = hedef_float * r
            if pg.olcum_birimi == "%":
                gercek = min(100, max(0, round(gercek, 1)))
            elif "Gün" in (pg.olcum_birimi or ""):
                gercek = max(1, round(gercek, 0))
            else:
                gercek = round(gercek, 2)
            gercek_str = str(int(gercek)) if isinstance(gercek, (int, float)) and gercek == int(gercek) else str(gercek)
            durum_pct = min(100, (gercek / hedef_float * 100) if hedef_float else 0) if is_increasing else min(100, (hedef_float / gercek * 100) if gercek else 0)
            pv = PerformansGostergeVeri(
                bireysel_pg_id=bpg.id,
                user_id=admin_user.id,
                yil=2024,
                veri_tarihi=veri_tarihi,
                giris_periyot_tipi="aylik",
                giris_periyot_no=(ay - 1) // 3 + 1,
                giris_periyot_ay=ay,
                ceyrek=(ay - 1) // 3 + 1,
                ay=ay,
                hafta=0,
                gun=15,
                hedef_deger=hedef_val,
                gerceklesen_deger=gercek_str,
                durum="Hedefde" if 95 <= durum_pct <= 105 else ("Üstünde" if durum_pct > 105 else "Altında"),
                durum_yuzdesi=round(durum_pct, 2),
                aciklama=f"2024/{ay} aylık veri.",
                created_by=admin_user.id,
                updated_by=admin_user.id,
            )
            db.session.add(pv)
    db.session.commit()


def _print_summary(kurum_id):
    """Eklenen kayıt sayılarını yazdır."""
    counts = {
        "Kurum (Tenant)": Kurum.query.filter_by(id=kurum_id).count(),
        "User": User.query.filter_by(kurum_id=kurum_id).count(),
        "AnalysisItem (SWOT)": AnalysisItem.query.filter_by(kurum_id=kurum_id).count(),
        "TowsMatrix": TowsMatrix.query.filter_by(kurum_id=kurum_id).count(),
        "Deger": Deger.query.filter_by(kurum_id=kurum_id).count(),
        "EtikKural": EtikKural.query.filter_by(kurum_id=kurum_id).count(),
        "KalitePolitikasi": KalitePolitikasi.query.filter_by(kurum_id=kurum_id).count(),
        "AnaStrateji (StrategicGoal)": AnaStrateji.query.filter_by(kurum_id=kurum_id).count(),
        "AltStrateji": AltStrateji.query.join(AnaStrateji).filter(AnaStrateji.kurum_id == kurum_id).count(),
        "StrategyMapLink": StrategyMapLink.query.filter(
            db.or_(StrategyMapLink.source.has(kurum_id=kurum_id), StrategyMapLink.target.has(kurum_id=kurum_id))
        ).count(),
        "Surec (Process)": Surec.query.filter_by(kurum_id=kurum_id).count(),
        "SurecPerformansGostergesi (KPI)": SurecPerformansGostergesi.query.filter(
            SurecPerformansGostergesi.surec.has(kurum_id=kurum_id)
        ).count(),
        "BireyselPerformansGostergesi": BireyselPerformansGostergesi.query.join(User).filter(User.kurum_id == kurum_id).count(),
        "PerformansGostergeVeri (ActualValue)": PerformansGostergeVeri.query.join(BireyselPerformansGostergesi).join(User).filter(User.kurum_id == kurum_id).count(),
        "StrategyProcessMatrix": StrategyProcessMatrix.query.filter(
            StrategyProcessMatrix.process.has(kurum_id=kurum_id)
        ).count(),
    }
    print("\n" + "=" * 60)
    print("TECHNOVA VERİ SETİ ÖZETİ")
    print("=" * 60)
    for label, c in counts.items():
        print(f"  {label}: {c}")
    print("=" * 60)
    total = sum(counts.values())
    print(f"  TOPLAM KAYIT: {total}")
    print("=" * 60)


def main():
    app = create_app()
    with app.app_context():
        try:
            kurum, users = _ensure_technova_and_users(app)
            # Technova zaten varsa strateji/süreç/KPI verilerini sil, tam set oluştur
            if Kurum.query.filter(Kurum.kisa_ad.ilike(TECHNOVA_KISA_AD)).first():
                _wipe_technova_strategic_data(kurum.id)
            _add_deger_etik_kalite(kurum.id)
            _add_swot_and_tows(kurum.id)
            ana_list, alt_by_ana = _add_strategies_and_links(kurum.id)
            procs, process_kpis = _add_processes_and_kpis(kurum.id, users)
            _link_processes_strategy_and_users(kurum.id, procs, alt_by_ana, users)
            admin_user = users.get("kurumadmin")
            if admin_user:
                _add_bpg_and_actual_values(kurum.id, process_kpis, admin_user)
            _print_summary(kurum.id)
            print("\nTechnova veri seti tamamlandı. Giriş: kurumadmin / %s" % PASSWORD)
        except Exception as e:
            db.session.rollback()
            print("HATA:", str(e))
            import traceback
            traceback.print_exc()
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
