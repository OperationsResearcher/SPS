import fitz  # PyMuPDF
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
TOMOFIL_DIR = ROOT / "docs" / "tomofil"
EMS_DIR = ROOT / "docs" / "ems"

# Create output dir if not exist
EMS_DIR.mkdir(parents=True, exist_ok=True)

# Replacements divided into two phases to avoid overlapping and double-redactions
PHASE_1_REPLACEMENTS = [
    # Company Name
    ("Tomofil Group N.V.", "Eskişehir Makine Sanayii A.Ş. (EMS)"),
    ("Tomofil Group N.V", "Eskişehir Makine Sanayii A.Ş."),
    ("TOMOFİL GROUP N.V.", "ESKİŞEHİR MAKİNE SANAYİİ A.Ş. (EMS)"),
    ("Tomofil Group", "Eskişehir Makine Sanayii"),
    ("TOMOFİL GROUP", "ESKİŞEHİR MAKİNE SANAYİİ"),
    ("Tomofil Otomotiv Sanayi ve Ticaret A.Ş.", "Eskişehir Makine Sanayii A.Ş. (EMS)"),
    ("Tomofil Otomotiv", "Eskişehir Makine Sanayii"),
    ("TMF-STRAT-2026-001", "EMS-STRAT-2026-001"),

    # Locations
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

    # Budget Scaling
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

    # Metrics
    ("ASP €16.1k → €30.1k", "Birim Fiyat (ASP) €16.1 → €30.1"),
    ("CLV: €18k → €42k → €85k", "CLV (OEM Müşteri Değeri): €18M → €42M → €85M"),
    ("CLV: €18k → €42k", "CLV (OEM Müşteri Değeri): €18M → €42M"),
    ("Garanti maliyeti/araç: €420 → €220", "Garanti maliyeti/parça: €4.20 → €2.20"),
    ("Recall oranı", "Müşteri iade oranı"),
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

    # Technical & Product Replacements
    ("Solid-State Batarya", "Solid-State Akıllı Kompresör"),
    ("Lucid, Rivian", "lokal metal pres rakipleri"),
    ("Tesla'ya alternatif", "küresel rakiplere alternatif"),
    ("T-Prestige, T-Wagon, T-Sedan", "E-Compressor (Kompresör), Drum-X (Tambur), Chassis-S (Şasi)"),
    ("T-Mini", "Micro-Pump (Pompa)"),
    ("T-Compact", "Slim-Frame (Kondenser)"),
    ("T-American", "Heavy-Duty-Press (Sac Pres)"),
    ("T-Pickup", "Steel-Chassis (Metal Pres)"),
    ("T-Dragon", "Smart-Tub (Kazan Grubu)"),
    ("T-Horizon", "Lineer-Compressor"),
    ("BaaS — Battery-as-a-Service", "CaaS — Compressor-as-a-Service"),
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
    ("sürüş AI", "motor kontrol sürücü AI"),
    ("Sürüş AI", "Motor Kontrol Sürücü AI"),

    # B2B Customer / Retail context mappings
    ("abone sayısı", "teslim edilen OEM parça siparişi"),
    ("abone sayısı artışı", "OEM sipariş artışı"),
    ("abone artışı", "OEM müşteri sipariş artışı"),
    ("abone", "OEM müşteri"),
    ("Abonelik", "B2B OEM Anlaşması"),
    ("abonelik", "B2B OEM anlaşması"),
    ("Netflix of cars", "Süreklilik Arz Eden OEM Sevkiyatı (Just-In-Time)"),
    ("aylık araç değişimi", "haftalık parça ikmali (Kanban)"),
    ("dealer", "OEM müşteri satın alma"),
    ("bayi", "OEM müşteri satın alma"),
    ("Omnichannel (Dealer + Direct + Online Entegre)", "B2B Entegre Tedarik Zinciri (OEM + JIT + EDI)"),
    ("Omnichannel", "B2B JIT / EDI"),
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
    ("CATL (CN)", "Assan Alüminyum (TR)"),
    ("CATL", "Assan Alüminyum"),
    ("Lityum", "Nitelikli Çelik Saç"),
    ("lityum", "çelik saç"),
    ("Nikel", "Alüminyum Alaşım"),
    ("nikel", "alüminyum"),
    ("Sulawesi Nikel", "İskenderun Pik Demir"),
    ("Atacama Lityum", "Eskişehir Bor"),
]

PHASE_2_REPLACEMENTS = [
    # Individual shorter names
    ("Tomofil OS", "EMS Connect IoT"),
    ("Tomofil", "EMS"),
    ("tomofil", "ems"),
    ("TOMOFIL", "EMS"),
    ("TOMOFİL", "EMS"),
    ("Münih", "Eskişehir"),
    ("Munich", "Eskişehir"),
    ("Munih", "Eskişehir"),
    ("Bursa", "Manisa"),
    ("Pune", "Bolu"),
    ("Şangay", "Tekirdağ"),
    ("Shanghai", "Tekirdağ"),
    ("Budapest", "İzmir"),
    ("Stavanger", "Kocaeli"),
    ("Monterrey", "Ankara"),
    ("Ulsan", "Bursa"),
    ("Bangalore", "Gebze"),
    ("Austin", "Eskişehir"),
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
    ("batarya", "kompresör"),
    ("Batarya", "Kompresör"),
    ("BATARYA", "KOMPRESÖR"),
    ("Lityum", "Bor"),
    ("lityum", "bor"),
    ("Nikel", "Alüminyum"),
    ("nikel", "alüminyum"),
    ("Atacama", "Eskişehir"),
    ("Sulawesi", "Ereğli"),
    ("HanGang", "Erdemir"),
    ("CATL", "Assan Alüminyum"),
    ("TMF-", "EMS-"),
    ("TMF", "EMS"),
]

def replace_emails_in_page(page):
    # Regex search for emails and redact them
    text = page.get_text("text")
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@tomofil\.test', text)
    if emails:
        for email in set(emails):
            new_email = email.replace("tomofil.test", "ems.test")
            rects = page.search_for(email)
            for rect in rects:
                page.add_redact_annot(rect, text=new_email, fontname="helv", fill=(1, 1, 1))
        page.apply_redactions()

def adapt_pdf(src_path: Path, dst_path: Path):
    print(f"Adapting PDF: {src_path.name} -> {dst_path.name}")
    doc = fitz.open(src_path)
    
    total_pages = len(doc)
    print(f"  - Total pages: {total_pages}")
    
    for page_num in range(total_pages):
        page = doc[page_num]
        
        # --- EMAIL REPLACEMENT ---
        replace_emails_in_page(page)
        
        # --- PHASE 1: Longer / Multi-word replacements ---
        phase1_applied = False
        for search_text, replace_text in PHASE_1_REPLACEMENTS:
            rects = page.search_for(search_text)
            if rects:
                phase1_applied = True
                for rect in rects:
                    page.add_redact_annot(rect, text=replace_text, fontname="helv", fill=(1, 1, 1))
        
        if phase1_applied:
            page.apply_redactions()
            
        # --- PHASE 2: Shorter / Single-word replacements ---
        phase2_applied = False
        for search_text, replace_text in PHASE_2_REPLACEMENTS:
            rects = page.search_for(search_text)
            if rects:
                phase2_applied = True
                for rect in rects:
                    page.add_redact_annot(rect, text=replace_text, fontname="helv", fill=(1, 1, 1))
                    
        if phase2_applied:
            page.apply_redactions()
            
        if (page_num + 1) % 50 == 0 or page_num + 1 == total_pages:
            print(f"  - Processed {page_num + 1}/{total_pages} pages")
            
    # Save the PDF with optimization
    doc.save(dst_path, garbage=3, deflate=True)
    doc.close()
    print(f"  - Successfully saved to {dst_path}")

def main():
    # 1) Sirket Dosyasi
    src_doc = TOMOFIL_DIR / "Tomofil_Sirket_Dosyasi.pdf"
    dst_doc = EMS_DIR / "EMS_Sirket_Dosyasi.pdf"
    if src_doc.exists():
        adapt_pdf(src_doc, dst_doc)
        
    # 2) Stratejik Plan (270 pages)
    src_plan = TOMOFIL_DIR / "Tomofil_Stratejik_Plan_2026-2035.pdf"
    dst_plan = EMS_DIR / "EMS_Stratejik_Plan_2026-2035.pdf"
    if src_plan.exists():
        adapt_pdf(src_plan, dst_plan)

if __name__ == "__main__":
    main()
