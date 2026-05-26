"""EMS import için ortak yardımcılar."""
import json
import re
import sys
import unicodedata
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parents[2] / "docs" / "ems"
EMS_TENANT_ID = 28


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("ı", "i").replace("ç", "c").replace("ş", "s").replace("ö", "o").replace("ü", "u").replace("ğ", "g")
    s = re.sub(r"[^a-z0-9]+", ".", s).strip(".")
    return s


def name_to_email(full_name: str, domain: str = "ems.com.tr") -> str:
    """'Mehmet Serdar Güçlü' → 'mehmet.serdar.guclu@ems.com.tr'"""
    return f"{slugify(full_name)}@{domain}"


def load_employees():
    with (DOCS_DIR / "EMS_Calisanlar.json").open(encoding="utf-8") as f:
        return json.load(f)


def load_atomic():
    with (DOCS_DIR / "EMS_Veriler.json").open(encoding="utf-8") as f:
        return json.load(f)


def read_md(filename: str) -> str:
    return (DOCS_DIR / filename).read_text(encoding="utf-8")


def log(msg: str):
    print(f"[ems-import] {msg}", flush=True)


# C-Suite üyeleri (sırasıyla ünvan, ad, açıklama)
C_SUITE = [
    ("CEO", "Mehmet Serdar Güçlü", "22 yıl beyaz eşya imalatı, Arçelik kökenli"),
    ("CFO", "Sibel Karadeniz Alp", "Endüstriyel finansman, Sabancı mezunu"),
    ("CTO", "Hasan Ercan Yıldırım", "BLDC motor Ar-Ge, ODTÜ doktorası"),
    ("COO", "Takeshi Ando", "Toyota Production System, Lean uzmanı"),
    ("CHRO", "Gülden Arslan Demirci", "Sanayi İK, KOSGEB danışmanı kökenli"),
    ("CSO", "Ayşe Nergiz Topçu", "Endüstriyel sürdürülebilirlik, Ankara Üniversitesi"),
    ("CCO", "Volkan Öztürk Sönmez", "B2B OEM satış, Vestel ve BSH kökenli"),
    ("CDO", "Barış Kılıç Vardar", "Endüstriyel veri, Aselsan kökenli"),
    ("CRO", "Nilüfer Çakır Mansur", "Kurumsal risk, Ernst & Young kökenli"),
]

# YK üyeleri
BOARD = [
    ("YK Başkanı", "Ahmet Kaya Çelikbaş", "Anadolu Sanayi Holding"),
    ("YK Üyesi", "Kenji Matsumoto", "Sakura Components"),
    ("YK Üyesi", "Mustafa Erdem Tunç", "Erdemir Grup"),
    ("Bağımsız YK Üyesi", "Ingrid Berglund", "ESG Uzmanı"),
    ("Bağımsız YK Üyesi", "Fatma Yıldız Şahin", "Finans Uzmanı"),
]

# 6 tesis ve hayali müdür isimleri (markdown'da müdür ismi yok, atadığım)
FACILITIES = [
    ("Eskişehir OSB", "Tesis Müdürü — Eskişehir OSB", "Hakan Demir Yıldız"),
    ("Manisa OSB", "Tesis Müdürü — Manisa OSB", "Ferda Karakoç Aslan"),
    ("Çerkezköy OSB", "Tesis Müdürü — Çerkezköy OSB", "Murat Şahin Korkmaz"),
    ("Bolu Fabrikası", "Tesis Müdürü — Bolu", "Selçuk Erdoğmuş Aydın"),
    ("Bursa Fabrikası", "Tesis Müdürü — Bursa", "Berna Çetinkaya Yavuz"),
    ("Gebze Ar-Ge", "Ar-Ge Merkez Müdürü — Gebze", "Dr. Cemil Tuncer Bayrak"),
]


# Süreç kod tablosu
PROCESS_MAP = [
    ("P2M", "Plan-to-Make", "Üretim Planlama ve Üretim", "Üretim planlaması, hat yönetimi ve seri imalat süreci.", "COO"),
    ("A2R", "Acquire-to-Retain", "Müşteri Kazanma ve Tutma", "Müşteri kazanma, ilişki yönetimi ve sadakat süreci.", "CCO"),
    ("C2L", "Concept-to-Launch", "Konsept-ten Pazara", "Ar-Ge'den ürün lansmanına kadar geliştirme süreci.", "CTO"),
    ("O2C", "Order-to-Cash", "Sipariş-ten Tahsilata", "Sipariş alımı, sevkiyat, faturalama ve tahsilat.", "CCO"),
    ("S2P", "Source-to-Pay", "Tedarik-ten Ödemeye", "Hammadde tedariki, satın alma ve ödeme süreci.", "COO"),
    ("H2R", "Hire-to-Retire", "İşe Alım-tan Emekliliğe", "İK süreci: işe alım, gelişim, ayrılma.", "CHRO"),
    ("I2R", "Inquiry-to-Resolution", "Talep-ten Çözüme", "Müşteri talep ve şikayet yönetimi.", "CCO"),
    ("F2D", "Forecast-to-Deliver", "Tahmin-den Teslime", "Talep tahmini, üretim planı ve teslim.", "COO"),
    ("R2R", "Record-to-Report", "Kayıt-tan Rapora", "Finansal kayıt, raporlama ve kapanış.", "CFO"),
    ("Q2C", "Quality-to-Compliance", "Kalite ve Uyum", "Kalite muayene, sertifikasyon ve uyum.", "CSO"),
    ("G2N", "Green-to-Net", "ESG ve Net-Sıfır", "Çevre, sürdürülebilirlik ve karbon ayak izi yönetimi.", "CSO"),
    ("K2K", "Knowledge-to-Innovation", "Bilgi-den İnovasyona", "Patent, IP ve açık inovasyon yönetimi.", "CTO"),
]


# 10 ana risk — manuel sahip ataması
RISKS = [
    {"title": "Çelik / Alüminyum fiyat artışı", "kategori": "Finansal", "onem": "Yüksek",
     "olasilik": 4, "etki": 4,
     "azaltma": "Erdemir uzun vadeli kontrat + EUR hedging", "sahip_unvan": "CFO"},
    {"title": "EUR/TRY kur riski", "kategori": "Finansal", "onem": "Yüksek",
     "olasilik": 4, "etki": 4,
     "azaltma": "%65 EUR gelir doğal hedge; opsiyon kullanımı", "sahip_unvan": "CFO"},
    {"title": "OEM müşteri konsantrasyonu (Arçelik %38)", "kategori": "Pazar", "onem": "Yüksek",
     "olasilik": 3, "etki": 5,
     "azaltma": "Avrupa OEM çeşitlendirme hızlandır", "sahip_unvan": "CCO"},
    {"title": "Enerji maliyeti artışı", "kategori": "Operasyonel", "onem": "Yüksek",
     "olasilik": 4, "etki": 3,
     "azaltma": "GES yatırımı + PPA + verimlilik programı", "sahip_unvan": "COO"},
    {"title": "Akıllı kompresör Ar-Ge gecikmesi", "kategori": "Teknoloji", "onem": "Orta",
     "olasilik": 3, "etki": 3,
     "azaltma": "Paralel geliştirme + üniversite ortaklığı", "sahip_unvan": "CTO"},
    {"title": "PCB / Elektronik tedarik kıtlığı", "kategori": "Operasyonel", "onem": "Yüksek",
     "olasilik": 4, "etki": 4,
     "azaltma": "Yerli PCB üreticisi geliştirme + ikinci kaynak", "sahip_unvan": "COO"},
    {"title": "AB CBAM karbon vergisi", "kategori": "Düzenleyici", "onem": "Orta",
     "olasilik": 4, "etki": 3,
     "azaltma": "Net-zero yol haritası + sertifikasyon", "sahip_unvan": "CSO"},
    {"title": "İş güvenliği ihlali", "kategori": "İnsan", "onem": "Kritik",
     "olasilik": 2, "etki": 5,
     "azaltma": "OHSAS 18001, dijital risk takibi", "sahip_unvan": "CHRO"},
    {"title": "Siber saldırı / OT güvenliği", "kategori": "Operasyonel", "onem": "Yüksek",
     "olasilik": 3, "etki": 5,
     "azaltma": "OT/IT ayrımı, SOC kurulum 2026", "sahip_unvan": "CDO"},
    {"title": "Bolu fabrika inşaat gecikmesi", "kategori": "Operasyonel", "onem": "Orta",
     "olasilik": 3, "etki": 3,
     "azaltma": "Eskişehir kapasitesi tampon", "sahip_unvan": "COO"},
]
