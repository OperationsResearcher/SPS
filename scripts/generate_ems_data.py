import json
import re
import os
import shutil
from pathlib import Path
import fitz  # PyMuPDF

# Path configuration
ROOT = Path(__file__).resolve().parent.parent
TOMOFIL_DIR = ROOT / "docs" / "tomofil"
EMS_DIR = ROOT / "docs" / "ems"

# Create output dir
EMS_DIR.mkdir(parents=True, exist_ok=True)

# 1. LOGICAL REPLACEMENTS (Automotive OEM -> White Goods Tier-1 Supplier)
REPLACEMENTS = [
    # Company Name
    ("Tomofil Group N.V.", "Eskişehir Makine Sanayii A.Ş. (EMS)"),
    ("Tomofil Group N.V", "Eskişehir Makine Sanayii A.Ş."),
    ("TOMOFİL GROUP N.V.", "ESKİŞEHİR MAKİNE SANAYİİ A.Ş. (EMS)"),
    ("Tomofil Group", "Eskişehir Makine Sanayii"),
    ("TOMOFİL GROUP", "ESKİŞEHİR MAKİNE SANAYİİ"),
    ("Tomofil Otomotiv Sanayi ve Ticaret A.Ş.", "Eskişehir Makine Sanayii A.Ş. (EMS)"),
    ("Tomofil Otomotiv", "Eskişehir Makine Sanayii"),
    ("Tomofil OS", "EMS Connect IoT"),
    ("Tomofil Club", "EMS Club"),
    ("Tomofil Day", "EMS Day"),
    ("Tomofil Academy", "EMS Academy"),
    ("Tomofil Foundation", "EMS Foundation"),
    ("Tomofil Ventures", "EMS Ventures"),
    ("Tomofil", "EMS"),
    ("tomofil", "ems"),
    ("TOMOFİL", "EMS"),
    ("TOMOFIL", "EMS"),

    # Locations Mapping (Specific to Turkish White Goods Corridor)
    ("Münih (Almanya) + Pune (Asya/EMEA) + Monterrey (Amerika)", "Eskişehir OSB (Merkez) + Manisa OSB (Vestel bölgesi) + Çerkezköy OSB (BSH bölgesi)"),
    ("Şangay (Çin) + Pune (Asya/EMEA) + Monterrey (Amerika)", "Eskişehir OSB (Merkez) + Manisa OSB (Vestel bölgesi) + Çerkezköy OSB (BSH bölgesi)"),
    ("Münih", "Eskişehir"),
    ("Munich", "Eskişehir"),
    ("Munih", "Eskişehir"),
    ("Bursa", "Manisa"),      # Manisa is Vestel HQ and major white goods OSB
    ("Pune", "Bolu"),        # Bolu is home to major Arçelik plant
    ("Şangay", "Tekirdağ"),    # Çerkezköy/Tekirdağ has the massive BSH plant
    ("Şanghay", "Tekirdağ"),
    ("Shanghai", "Tekirdağ"),
    ("Budapest", "İzmir"),    # İzmir Serbest Bölge / Hugo Boss / Indesit etc
    ("Budapeşte", "İzmir"),
    ("Stavanger", "Kocaeli"),  # Gebze OSB
    ("Monterrey", "Ankara"),   # Sincan OSB
    ("Ulsan", "Bursa"),
    ("Bangalore", "Gebze"),
    ("Austin", "Eskişehir"),
    ("Amsterdam", "Ankara"),
    ("Almanya", "Türkiye"),
    ("Avrupa", "Manisa"),
    ("Amerika", "Tekirdağ"),
    ("Asya", "Bolu"),
    ("G.Kore", "Türkiye"),
    ("Hindistan", "Türkiye"),
    ("Meksika", "Türkiye"),
    ("Macaristan", "Türkiye"),
    ("Norveç", "Türkiye"),
    ("Çin", "Türkiye"),
    ("Hollanda", "Türkiye"),
    ("ems.test", "ems.test"),  # Guard

    # Budget Scaling (Billion OEM -> Million Tier-1 Supplier)
    ("€12 Mr", "€120M"),
    ("€8.5 Mr", "€85M"),
    ("€2.2 Mr", "€22M"),
    ("€1.3 Mr", "€13M"),
    ("€5.0 Mr", "€50M"),
    ("€1.8 Mr", "€18M"),
    ("€0.7 Mr", "€7M"),
    ("€7 Mr", "€70M"),
    ("€4.5 Mr", "€45M"),
    ("€4 Mr", "€40M"),
    ("€2.5 Mr", "€25M"),
    ("€0.9 Mr", "€9M"),
    ("€0.6 Mr", "€6M"),
    ("€2 Mr", "€20M"),
    ("€0.5 Mr", "€5M"),
    ("€0.3 Mr", "€3M"),
    ("€0.1 Mr", "€1M"),
    ("€34 Mr", "€340M"),

    # Metric / Pricing Scaling
    ("ASP €16.1k → €30.1k", "Birim Fiyat (ASP) €16.1 → €30.1"),
    ("ASP €16.1k → €30.1", "Birim Fiyat (ASP) €16.1 → €30.1"),
    ("€16.1k", "€16.1"),
    ("€30.1k", "€30.1"),
    ("CLV: €18k → €42k → €85k", "CLV (OEM Müşteri Değeri): €18M → €42M → €85M"),
    ("CLV: €18k → €42k", "CLV (OEM Müşteri Değeri): €18M → €42M"),
    ("CLV: €18k", "CLV: €18M"),
    ("€18k", "€18M"),
    ("€42k", "€42M"),
    ("€85k", "€85M"),
    ("Garanti maliyeti/araç: €420 → €220", "Garanti maliyeti/parça: €4.20 → €2.20"),
    ("€420", "€4.20"),
    ("€220", "€2.20"),
    ("Recall oranı", "Müşteri iade oranı"),
    ("Recall", "Müşteri İadesi"),
    ("recall", "müşteri iadesi"),
    ("Geliştirme maliyeti/model: €140M → €95M", "Geliştirme maliyeti/model: €1.40M → €0.95M"),
    ("€140M", "€1.40M"),
    ("€95M", "€0.95M"),

    # White goods domain mappings (Logical equivalents)
    ("Mobiliteyi yeniden tanımlayan, küresel olarak güvenilen, sürdürülebilir liderlik.", "Beyaz eşya teknolojilerini yeniden tanımlayan, küresel olarak güvenilen, sürdürülebilir liderlik."),
    ("sürdürülebilir mobilite", "sürdürülebilir beyaz eşya bileşenleri"),
    ("Sürdürülebilir mobilite", "Sürdürülebilir beyaz eşya bileşenleri"),
    ("mobilite çözümlerini", "beyaz eşya bileşenlerini"),
    ("mobilite", "beyaz eşya bileşenleri"),
    ("Mobilite", "Beyaz Eşya"),
    ("bireysel karayolu taşımacılığı", "beyaz eşya üretimi"),
    ("Bireysel karayolu taşımacılığı", "Beyaz eşya üretimi"),
    
    # Specific EV phrases
    ("küresel EV pazar payı", "küresel beyaz eşya pazar payı"),
    ("EV pazar payı", "beyaz eşya pazar payı"),
    ("EV pivot", "beyaz eşya pivotu"),
    ("EV pivotu", "beyaz eşya pivotu"),
    ("EV parça", "beyaz eşya parça"),
    ("EV cirosu", "beyaz eşya cirosu"),
    ("EV teknolojisi", "beyaz eşya teknolojisi"),
    ("EV ve klasik", "inverter ve klasik"),
    (" EV ", " Beyaz Eşya "),
    (" EV'", " Beyaz Eşya'"),
    (" EV.", " Beyaz Eşya."),
    (" EV,", " Beyaz Eşya,"),
    (" EV/", " Beyaz Eşya/"),
    ("/EV", "/Beyaz Eşya"),
    (" ev ", " beyaz eşya "),
    (" ev'", " beyaz eşya'"),
    (" ev.", " beyaz eşya."),
    (" ev,", " beyaz eşya,"),

    # Technical & Product Replacements
    ("Solid-State Batarya", "Solid-State Akıllı Kompresör"),
    ("Lucid, Rivian", "lokal metal pres rakipleri"),
    ("Tesla'ya alternatif", "küresel rakiplere alternatif"),
    ("T-Prestige, T-Wagon, T-Sedan", "E-Compressor (Kompresör), Drum-X (Tambur), Chassis-S (Şasi)"),
    ("T-Prestige", "E-Compressor"),
    ("T-Wagon", "Drum-X"),
    ("T-Sedan", "Chassis-S"),
    ("T-Mini", "Micro-Pump (Pompa)"),
    ("T-Compact", "Slim-Frame (Kondenser)"),
    ("T-American", "Heavy-Duty-Press (Sac Pres)"),
    ("T-Pickup", "Steel-Chassis (Metal Pres)"),
    ("T-Dragon", "Smart-Tub (Kazan Grubu)"),
    ("T-Horizon", "Lineer-Compressor"),
    ("BaaS — Battery-as-a-Service", "CaaS — Compressor-as-a-Service"),
    ("BaaS", "CaaS"),
    ("Batarya aylık abonelik", "Kompresör gövdesi B2B OEM anlaşması"),
    ("atık batarya", "atık metal/kompresör"),
    ("batarya hücresi", "inverter bobini"),
    ("batarya hücreleri", "inverter bobinleri"),
    ("Batarya Hücre Üretimi", "Bobin ve Motor Üretimi"),
    ("batarya kasası", "kompresör gövdesi"),
    ("Batarya Kasası", "Kompresör Gövdesi"),
    ("batarya geri kazanım", "metal/bakır geri kazanımı"),
    ("batarya test", "kompresör performans test"),
    ("Batarya Test", "Kompresör Test"),
    ("batarya teknolojisi", "kompresör ve motor teknolojisi"),
    ("Batarya Teknolojisi", "Kompresör ve Motor Teknolojisi"),
    ("batarya", "kompresör"),
    ("Batarya", "Kompresör"),
    ("BATARYA", "KOMPRESÖR"),
    ("araç boyama", "sac metal fırın boyama"),
    ("Araç Boyama", "Sac Metal Fırın Boyama"),
    ("araç tescili", "komponent tescili"),
    ("araç geri kazanım", "metal geri kazanımı"),
    ("onarılabilir araç", "onarılabilir beyaz eşya"),
    ("onarılabilir araçlar", "onarılabilir beyaz eşyalar"),
    ("komşu araç", "komşu kompresör"),
    ("2. araç", "mükerrer proje"),
    ("araçlar", "beyaz eşya bileşenleri"),
    ("araç", "beyaz eşya bileşeni"),
    ("Araç", "Beyaz Eşya Bileşeni"),
    ("ARAÇ", "BEYAZ EŞYA BİLEŞENİ"),
    ("araba", "kompresör/tambur"),
    ("Araba", "Kompresör/Tambur"),
    ("otomobil", "beyaz eşya"),
    ("Otomobil", "Beyaz Eşya"),
    ("T-Pilot", "EMS Smart Control"),
    ("otonom sürüş", "akıllı ev entegrasyonu"),
    ("Otonom Sürüş", "Akıllı Ev Entegrasyonu"),
    ("L4 otonom", "A+++ yüksek verimlilik"),
    ("L4 otonom lisans", "A+++ yüksek verimlilik sertifikası"),
    ("L4", "A+++"),
    ("sürüş AI", "motor kontrol sürücü AI"),
    ("Sürüş AI", "Motor Kontrol Sürücü AI"),

    # B2B Customer / Retail context mappings
    ("abone sayısı", "teslim edilen OEM parça siparişi"),
    ("abone sayısı artışı", "OEM sipariş artışı"),
    ("abone artışı", "OEM müşteri sipariş artışı"),
    ("abone sayısı", "OEM sipariş adedi"),
    ("abone", "OEM müşteri"),
    ("Abonelik", "B2B OEM Anlaşması"),
    ("abonelik", "B2B OEM anlaşması"),
    ("Netflix of cars", "Süreklilik Arz Eden OEM Sevkiyatı (Just-In-Time)"),
    ("aylık araç değişimi", "haftalık parça ikmali (Kanban)"),
    ("dealer", "OEM müşteri satın alma"),
    ("bayi", "OEM müşteri satın alma"),
    ("Omnichannel (Dealer + Direct + Online Entegre)", "B2B Entegre Tedarik Zinciri (OEM + JIT + EDI)"),
    ("Omnichannel", "B2B JIT / EDI"),
    ("milyon abone", "milyon adet OEM siparişi"),
    ("8M abone", "8M adet OEM siparişi"),
    ("80k abone", "80k adet OEM siparişi"),
    ("25k abone", "25k adet OEM siparişi"),
    ("250k abone", "250k adet OEM siparişi"),

    # Partners & Sponsors
    ("Lucid, Rivian", "lokal metal pres rakipleri"),
    ("Tesla'ya alternatif", "küresel rakiplere alternatif"),
    ("Uber, Lyft", "Vestel, Arçelik, BSH"),
    ("Hertz, Sixt, Enterprise", "Bosch, Miele, Electrolux"),
    ("Formula E", "Endüstriyel Tasarım Bienali"),
    ("UEFA Sustainability", "Sürdürülebilirlik Zirvesi"),
    ("Girls in STEAM", "Sanayide Kadın Gücü"),
    ("girls in STEAM", "sanayide kadın gücü"),

    # Supply Chain & Raw Materials
    ("HanGang Energy (KR)", "Ereğli Demir Çelik (TR)"),
    ("HanGang Energy", "Ereğli Demir Çelik"),
    ("HanGang", "Erdemir"),
    ("CATL (CN)", "Assan Alüminyum (TR)"),
    ("CATL", "Assan Alüminyum"),
    ("Lityum", "Nitelikli Çelik Saç"),
    ("lityum", "çelik saç"),
    ("Nikel", "Alüminyum Alaşım"),
    ("nikel", "alüminyum"),
    ("Sulawesi Nikel", "İskenderun Pik Demir"),
    ("Sulawesi", "İsdemir"),
    ("Atacama Lityum", "Eskişehir Bor"),
    ("Atacama", "Eskişehir"),
    ("Sulawesi", "Ereğli"),

    ("TMF-", "EMS-"),
]

def replace_text(text: str) -> str:
    # First, replace email domains
    text = re.sub(r'([a-zA-Z0-9._%+-]+)@tomofil\.test', r'\1@ems.test', text)
    # Apply replacements
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text

def process_file_content(content: bytes) -> bytes:
    try:
        text = content.decode("utf-8")
        text = replace_text(text)
        return text.encode("utf-8")
    except UnicodeDecodeError:
        return content

def process_strategy_tree():
    src = TOMOFIL_DIR / "Tomofil_Strateji_Agaci.md"
    dst = EMS_DIR / "EMS_Strateji_Agaci.md"
    print(f"Processing Strategy Tree: {src.name} -> {dst.name}")
    content = src.read_bytes()
    processed = process_file_content(content)
    dst.write_bytes(processed)

def process_employees():
    src = TOMOFIL_DIR / "Tomofil_Calisanlar.json"
    dst = EMS_DIR / "EMS_Calisanlar.json"
    print(f"Processing Employees: {src.name} -> {dst.name}")
    with open(src, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    meta = data.get("meta", {})
    if "aciklama" in meta:
        meta["aciklama"] = replace_text(meta["aciklama"])
    if "belge" in meta:
        meta["belge"] = replace_text(meta["belge"])
    
    for emp in data.get("calisanlar", []):
        for field in ["unvan", "departman", "lokasyon", "kpi"]:
            if field in emp and emp[field]:
                emp[field] = replace_text(emp[field])
    
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def process_atomic_data():
    src = TOMOFIL_DIR / "Tomofil_Veriler_v3.json"
    dst = EMS_DIR / "EMS_Veriler_v3.json"
    print(f"Processing Atomic Data: {src.name} -> {dst.name}")
    with open(src, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    meta = data.get("meta", {})
    if "aciklama" in meta:
        meta["aciklama"] = replace_text(meta["aciklama"])
    if "belge" in meta:
        meta["belge"] = replace_text(meta["belge"])
        
    for module_key in data:
        if module_key == "meta":
            continue
        print(f"  - Module: {module_key}")
        for record in data[module_key]:
            for field in record:
                if isinstance(record[field], str):
                    record[field] = replace_text(record[field])
                    
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    print("Starting EMS Deep Logical Data Generation...")
    process_strategy_tree()
    process_employees()
    process_atomic_data()
    print("EMS Deep Logical Data Generation completed successfully!")

if __name__ == "__main__":
    main()
