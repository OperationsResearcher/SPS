# -*- coding: utf-8 -*-
"""
KalDer PDF Import ve Eşleme Raporu

temp_data içindeki KalDer Stratejik Plan PDF'ini okur:
- Metin ve tabloları çıkarır
- Mümkün olan verileri KalDer kurumuna (AnaStrateji, KPI, PerformansGostergeVeri) aktarır
- Ekrana: PDF'deki hangi başlık/bölüm -> projedeki hangi tablo/alan karşılık gelir raporu basar

Kullanım:
  py scripts/import_kalder_pdf.py
"""
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

TEMP_DATA = PROJECT_ROOT / "temp_data"
PDF_NAME = "KalDer Stratejik Plan 2025-2027_12.12.2025.pdf"


def extract_pdf_content(pdf_path):
    """PDF'den metin ve tabloları çıkarır."""
    try:
        import pdfplumber
    except ImportError:
        print("HATA: pdfplumber kurulu değil. Kurulum: py -m pip install pdfplumber")
        return None, None

    text_by_page = []
    tables_by_page = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            text_by_page.append({"page": i + 1, "text": text or ""})
            tables = page.extract_tables()
            tables_by_page.append({"page": i + 1, "tables": tables or []})
    return text_by_page, tables_by_page


def build_mapping_report(text_by_page, tables_by_page):
    """PDF yapısına göre proje eşleme raporu oluşturur."""
    report = []
    report.append("=" * 70)
    report.append("PDF -> PROJE EŞLEME RAPORU")
    report.append("=" * 70)
    report.append("")

    # Genel eşleme (KalDer stratejik plan yapısına göre)
    report.append("GENEL EŞLEME (KalDer Stratejik Plan PDF):")
    report.append("-" * 50)
    report.append("  PDF'deki bölüm/başlık              -> Projedeki tablo/alan")
    report.append("  ---------------------------------   -> ---------------------------------")
    report.append("  Vizyon / Misyon / Stratejik Hedef   -> AnaStrateji (ana_strateji)")
    report.append("  Alt hedefler / Stratejik amaçlar    -> AltStrateji (alt_strateji)")
    report.append("  BSC Perspektif (Paydaş, Finansal…)  -> AnaStrateji.perspective")
    report.append("  Gösterge / KPI adı                  -> SurecPerformansGostergesi.ad")
    report.append("  Birim / Ölçüm birimi                -> SurecPerformansGostergesi.olcum_birimi")
    report.append("  Hedef değer                        -> PerformansGostergeVeri.hedef_deger")
    report.append("  Gerçekleşen değer                  -> PerformansGostergeVeri.gerceklesen_deger")
    report.append("  Dönem / Ay (Ocak, Şubat…)          -> PerformansGostergeVeri.veri_tarihi (yıl+ay)")
    report.append("")

    # PDF içeriğinden tespit edilen başlıklar
    report.append("PDF İÇERİĞİNDEN TESPİT EDİLEN BAŞLIKLAR:")
    report.append("-" * 50)
    all_text = ""
    for p in text_by_page or []:
        all_text += (p.get("text") or "") + "\n"

    # Yaygın KalDer/stratejik plan başlıkları
    patterns = [
        (r"(?:Vizyon|MİSYON|Misyon)\s*[:.]?\s*(.+)", "Vizyon/Misyon -> Kurum vizyonu / CorporateIdentity veya AnaStrateji açıklaması"),
        (r"(?:STRATEJİK HEDEF|Stratejik Hedef)\s*[:.]?\s*(.+)", "Stratejik Hedef -> AnaStrateji.ad"),
        (r"(?:BSC|Balanced Scorecard|Paydaş|Finansal|Operasyonel|Çalışan)\s*(?:perspektif|boyut)?", "BSC perspektif -> AnaStrateji.perspective (FINANSAL, MUSTERI, SUREC, OGRENME)"),
        (r"Gösterge\s*(?:Adı|adı)?\s*[:.]?", "Gösterge Adı -> SurecPerformansGostergesi.ad"),
        (r"Birim\s*[:.]?", "Birim -> SurecPerformansGostergesi.olcum_birimi"),
        (r"Hedef\s*[:.]?", "Hedef -> PerformansGostergeVeri.hedef_deger"),
        (r"Gerçekleşen\s*[:.]?", "Gerçekleşen -> PerformansGostergeVeri.gerceklesen_deger"),
        (r"Dönem\s*[:.]?", "Dönem -> PerformansGostergeVeri.veri_tarihi (ay)"),
    ]
    for pattern, mapping in patterns:
        if re.search(pattern, all_text, re.IGNORECASE):
            report.append(f"  [Bulundu] {mapping}")
    report.append("")

    # Tablo sayıları
    total_tables = sum(len(p.get("tables") or []) for p in tables_by_page or [])
    report.append("PDF TABLO ÖZETİ:")
    report.append("-" * 50)
    report.append(f"  Toplam sayfa: {len(text_by_page or [])}")
    report.append(f"  Toplam tablo: {total_tables}")
    for p in tables_by_page or []:
        n = len(p.get("tables") or [])
        if n > 0:
            report.append(f"  Sayfa {p['page']}: {n} tablo")
    report.append("")
    report.append("  Tablo satırları -> Stratejik hedef/KPI/veri satırı olarak işlenebilir.")
    report.append("  (İlk satır başlık, sonraki satırlar veri; sütunlar yukarıdaki alanlara eşlenir.)")
    report.append("")
    report.append("=" * 70)
    return "\n".join(report)


def import_pdf_to_kalder(pdf_path, text_by_page, tables_by_page):
    """PDF tablolarından çıkarılan veriyi KalDer kurumuna yazar."""
    from __init__ import create_app
    from extensions import db
    from models import (
        Kurum,
        User,
        AnaStrateji,
        AltStrateji,
        Surec,
        SurecPerformansGostergesi,
        BireyselPerformansGostergesi,
        PerformansGostergeVeri,
    )
    from datetime import date

    app = create_app()
    KALDER_KURUM = "KalDer"
    BSC_SUREÇ_ADI = "KalDer BSC Göstergeleri"
    AY_ADLARI = {
        "ocak": 1, "şubat": 2, "subat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "mayis": 5,
        "haziran": 6, "temmuz": 7, "ağustos": 8, "agustos": 8, "eylül": 9, "eylul": 9,
        "ekim": 10, "kasım": 11, "kasim": 11, "aralık": 12, "aralik": 12,
    }

    def norm(s):
        if s is None or (isinstance(s, float) and str(s) == "nan"):
            return ""
        return str(s).strip()

    def donem_to_ay(val):
        if not val:
            return None
        s = norm(val).lower().replace("ı", "i").replace("ş", "s").replace("ğ", "g").replace("ü", "u").replace("ö", "o")
        for ay_ad, no in AY_ADLARI.items():
            if ay_ad in s:
                return no
        return None

    with app.app_context():
        kurum = Kurum.query.filter(Kurum.kisa_ad.ilike(KALDER_KURUM)).first()
        if not kurum:
            print("  [UYARI] KalDer kurumu yok. Önce scripts/setup_kalder_and_import_bsc.py çalıştırın.")
            return 0
        kalder_admin = User.query.filter(User.username == "KalDerAdmin").first()
        if not kalder_admin:
            print("  [UYARI] KalDerAdmin kullanıcısı yok. Önce setup scriptini çalıştırın.")
            return 0
        surec = Surec.query.filter(Surec.kurum_id == kurum.id, Surec.ad.ilike(BSC_SUREÇ_ADI)).first()
        if not surec:
            surec = Surec(kurum_id=kurum.id, ad=BSC_SUREÇ_ADI, code="BSC", durum="Aktif")
            db.session.add(surec)
            db.session.commit()

        imported = 0
        yil = 2025
        for page_data in tables_by_page or []:
            for table in page_data.get("tables") or []:
                if len(table) < 2:
                    continue
                header = [norm(c) for c in (table[0] or [])]
                # Stratejik Hedef, Gösterge Adı, Birim, Dönem, Hedef, Gerçekleşen benzeri sütun ara
                idx_hedef = idx_gosterge = idx_birim = idx_donem = idx_hedef_val = idx_gercek = -1
                for i, h in enumerate(header):
                    h = h.lower()
                    if "stratejik" in h and "hedef" in h:
                        idx_hedef = i
                    elif "gösterge" in h or "gosterge" in h:
                        idx_gosterge = i
                    elif "birim" in h:
                        idx_birim = i
                    elif "dönem" in h or "donem" in h or h == "ay":
                        idx_donem = i
                    elif "hedef" in h and "gerçek" not in h and "gercek" not in h:
                        if idx_hedef_val < 0:
                            idx_hedef_val = i
                    elif "gerçekleşen" in h or "gerceklesen" in h:
                        idx_gercek = i
                if idx_gosterge < 0:
                    idx_gosterge = 1 if len(header) > 1 else 0
                if idx_hedef < 0:
                    idx_hedef = 0

                hedef_ff = ""
                gosterge_ff = ""
                for row in table[1:]:
                    if not row:
                        continue
                    row = list(row) + [""] * (max(len(header), idx_hedef_val, idx_gercek, idx_donem) + 1 - len(row))
                    hedef_metni = norm(row[idx_hedef]) if idx_hedef >= 0 else ""
                    gosterge_adi = norm(row[idx_gosterge]) if idx_gosterge >= 0 else ""
                    if hedef_metni:
                        hedef_ff = hedef_metni
                    if gosterge_adi:
                        gosterge_ff = gosterge_adi
                    if not gosterge_ff and not hedef_ff:
                        continue
                    gosterge_adi = gosterge_ff or "Gösterge"
                    hedef_metni = hedef_ff or "Genel Hedef"
                    birim = norm(row[idx_birim]) if idx_birim >= 0 else ""
                    donem = norm(row[idx_donem]) if idx_donem >= 0 else ""
                    hedef_val = norm(row[idx_hedef_val]) if idx_hedef_val >= 0 else ""
                    gercek_val = norm(row[idx_gercek]) if idx_gercek >= 0 else ""
                    ay_no = donem_to_ay(donem)
                    if not ay_no and not hedef_val and not gercek_val:
                        continue
                    if not ay_no:
                        ay_no = 1

                    ana = AnaStrateji.query.filter(AnaStrateji.kurum_id == kurum.id, AnaStrateji.ad == hedef_metni).first()
                    if not ana:
                        ana = AnaStrateji(kurum_id=kurum.id, ad=hedef_metni)
                        db.session.add(ana)
                        db.session.commit()
                    alt = AltStrateji.query.filter(AltStrateji.ana_strateji_id == ana.id, AltStrateji.ad == hedef_metni).first()
                    if not alt:
                        alt = AltStrateji(ana_strateji_id=ana.id, ad=hedef_metni)
                        db.session.add(alt)
                        db.session.commit()
                    surec_pg = SurecPerformansGostergesi.query.filter(
                        SurecPerformansGostergesi.surec_id == surec.id,
                        SurecPerformansGostergesi.ad == gosterge_adi,
                    ).first()
                    if not surec_pg:
                        surec_pg = SurecPerformansGostergesi(
                            surec_id=surec.id,
                            ad=gosterge_adi,
                            olcum_birimi=birim,
                            alt_strateji_id=alt.id,
                        )
                        db.session.add(surec_pg)
                        db.session.commit()
                    bireysel_pg = BireyselPerformansGostergesi.query.filter(
                        BireyselPerformansGostergesi.user_id == kalder_admin.id,
                        BireyselPerformansGostergesi.kaynak_surec_pg_id == surec_pg.id,
                    ).first()
                    if not bireysel_pg:
                        bireysel_pg = BireyselPerformansGostergesi(
                            user_id=kalder_admin.id,
                            ad=gosterge_adi,
                            olcum_birimi=surec_pg.olcum_birimi or "",
                            kaynak="Süreç",
                            kaynak_surec_id=surec.id,
                            kaynak_surec_pg_id=surec_pg.id,
                        )
                        db.session.add(bireysel_pg)
                        db.session.commit()
                    veri_tarihi = date(yil, ay_no, 1)
                    existing = PerformansGostergeVeri.query.filter(
                        PerformansGostergeVeri.bireysel_pg_id == bireysel_pg.id,
                        PerformansGostergeVeri.veri_tarihi == veri_tarihi,
                    ).first()
                    if existing:
                        if hedef_val:
                            existing.hedef_deger = hedef_val
                        if gercek_val:
                            existing.gerceklesen_deger = gercek_val
                    else:
                        pv = PerformansGostergeVeri(
                            bireysel_pg_id=bireysel_pg.id,
                            yil=yil,
                            veri_tarihi=veri_tarihi,
                            giris_periyot_tipi="aylik",
                            giris_periyot_ay=ay_no,
                            ay=ay_no,
                            user_id=kalder_admin.id,
                            hedef_deger=hedef_val,
                            gerceklesen_deger=gercek_val or "",
                        )
                        db.session.add(pv)
                    imported += 1
                db.session.commit()
    return imported


def main():
    pdf_path = TEMP_DATA / PDF_NAME
    if not pdf_path.exists():
        print(f"PDF bulunamadı: {pdf_path}")
        return 1

    print("PDF okunuyor:", pdf_path.name)
    text_by_page, tables_by_page = extract_pdf_content(pdf_path)
    if text_by_page is None:
        return 1

    # Eşleme raporu
    report = build_mapping_report(text_by_page, tables_by_page)
    print(report)

    # Import
    print("\nPDF verisi KalDer kurumuna aktarılıyor...")
    n = import_pdf_to_kalder(pdf_path, text_by_page, tables_by_page)
    print(f"  [OK] {n} satır/kayıt PDF'den aktarıldı.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
