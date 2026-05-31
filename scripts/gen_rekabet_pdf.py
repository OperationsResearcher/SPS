"""Kokpitim Rekabet Analizi PDF üreticisi."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# Unicode (Türkçe) için Arial kaydet
pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Italic", r"C:\Windows\Fonts\ariali.ttf"))
pdfmetrics.registerFont(TTFont("Arial-BoldItalic", r"C:\Windows\Fonts\arialbi.ttf"))
registerFontFamily("Arial", normal="Arial", bold="Arial-Bold",
                   italic="Arial-Italic", boldItalic="Arial-BoldItalic")
FONT = "Arial"
FONT_BOLD = "Arial-Bold"

OUT = r"c:\kokpitim\docs\rapor\29mayis_rekabet_analizi.pdf"

styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName=FONT_BOLD, fontSize=18, textColor=colors.HexColor("#0f172a"), spaceAfter=10)
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName=FONT_BOLD, fontSize=14, textColor=colors.HexColor("#1e3a8a"), spaceAfter=6, spaceBefore=10)
H3 = ParagraphStyle("H3", parent=styles["Heading3"], fontName=FONT_BOLD, fontSize=11, textColor=colors.HexColor("#334155"), spaceAfter=4, spaceBefore=6)
BODY = ParagraphStyle("Body", parent=styles["BodyText"], fontName=FONT, fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=4)
SMALL = ParagraphStyle("Small", parent=styles["BodyText"], fontName=FONT, fontSize=9, leading=12, textColor=colors.HexColor("#475569"))
TH = ParagraphStyle("TH", parent=styles["BodyText"], fontName=FONT_BOLD, fontSize=9, leading=12, textColor=colors.white)
META = ParagraphStyle("Meta", parent=styles["BodyText"], fontName=FONT, fontSize=9, textColor=colors.HexColor("#64748b"), spaceAfter=12)

story = []

# Kapak
story.append(Paragraph("KOKPITIM — Tam Set Rekabet Analizi Raporu", H1))
story.append(Paragraph("Tarih: 2026-05-29 &nbsp;·&nbsp; Hazırlayan: Otomatik Analiz &nbsp;·&nbsp; Sürüm: 1.0", META))
story.append(Paragraph(
    "Bu rapor; Kokpitim'in pazar konumunu, doğrudan ve dolaylı rakiplerini, "
    "özellik karşılaştırmasını, fiyatlama, hedef segment, güçlü/zayıf yönler "
    "ve stratejik tavsiyeleri kapsamaktadır. Kokpitim; Stratejik Planlama (Hoshin/X-Matrix), "
    "Süreç & KPI Yönetimi, EFQM 2025 Olgunluk, BSC (Kaplan-Norton), K-Radar/K-Analiz, "
    "Proje & Portföy Yönetimi modüllerini tek platformda birleştiren çok-kiracılı (multi-tenant) "
    "Türkçe arayüzlü bir kurumsal performans yönetimi (CPM/EPM) çözümüdür.", BODY))
story.append(Spacer(1, 0.4*cm))

# 1. Yönetici Özeti
story.append(Paragraph("1. Yönetici Özeti", H2))
story.append(Paragraph(
    "Kokpitim, Türkçe arayüz + EFQM 2025 + Hoshin Kanri + BSC + Süreç KPI + Proje yönetimi entegrasyonu "
    "ile niş bir konumda yer almaktadır. Küresel rakipler (ClearPoint, Cascade, Spider Impact, AchieveIt, "
    "Workboard, Quantive/Gtmhub, Profit.co) güçlü OKR/BSC modülleri sunarken; EFQM olgunluk değerlendirmesi, "
    "K-Vektör ağırlıklandırma ve Türkiye'ye özgü kamu/KOBİ/üniversite süreç şablonları konusunda zayıftır. "
    "Yerli rakipler (Logo CPM, Mikro Stratejik, çeşitli ISO/EFQM danışmanlık ürünleri) ise EFQM tarafında deneyim sahibidir "
    "fakat modern web UX, çapraz-modül entegrasyonu ve AI destekli analitiklerde geridedir.", BODY))
story.append(Paragraph(
    "<b>Fırsat:</b> EFQM Modeli 2025 + Hoshin + Proje + KPI'nın tek çatıda Türkçe sunulması, "
    "kamu kurumları, üniversiteler, sağlık kuruluşları ve EFQM ödül peşindeki KOBİ'ler için yüksek değer önerisidir.", BODY))

# 2. Pazar Tanımı
story.append(Paragraph("2. Pazar Tanımı ve Segmentasyon", H2))
story.append(Paragraph(
    "Hedef pazar: Kurumsal Performans Yönetimi (CPM/EPM) + Stratejik Yürütme Yazılımları (Strategy Execution). "
    "Küresel pazar 2024'te ~6.1 milyar USD, 2030'a kadar yıllık ~%12 büyüme öngörülüyor (Gartner/MarketsAndMarkets). "
    "Türkiye'de KOBİ + kamu + büyük şirket segmenti birlikte ~120-180 milyon TL/yıl yazılım & danışmanlık harcaması "
    "(KalDer, EFQM Türkiye verileri ile tahmin).", BODY))

seg_data = [
    ["Segment", "Boyut (TR)", "Bütçe/Yıl", "Karar Süresi", "Uygunluk"],
    ["Kamu kurumları", "Yüksek", "150K – 1M+ TL", "6-12 ay", "Çok yüksek"],
    ["Üniversiteler", "Orta-Yüksek", "80K – 300K TL", "4-9 ay", "Çok yüksek"],
    ["Sağlık kuruluşları", "Orta", "100K – 400K TL", "3-6 ay", "Yüksek"],
    ["KOBİ (EFQM peşinde)", "Yüksek", "40K – 150K TL", "2-4 ay", "Yüksek"],
    ["Büyük holding", "Orta", "300K – 2M+ TL", "6-18 ay", "Orta"],
    ["Belediyeler", "Yüksek", "120K – 600K TL", "4-9 ay", "Çok yüksek"],
]
t = Table(seg_data, colWidths=[4.2*cm, 2.6*cm, 3*cm, 2.6*cm, 2.6*cm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1e3a8a")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,-1), FONT),
    ("FONTNAME", (0,0), (-1,0), FONT_BOLD),
    ("FONTSIZE", (0,0), (-1,-1), 9),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f1f5f9")]),
    ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#cbd5e1")),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("ALIGN", (1,1), (-1,-1), "CENTER"),
    ("LEFTPADDING", (0,0), (-1,-1), 6),
    ("RIGHTPADDING", (0,0), (-1,-1), 6),
]))
story.append(t)
story.append(Spacer(1, 0.3*cm))

# 3. Rakip Haritası
story.append(PageBreak())
story.append(Paragraph("3. Rakip Haritası", H2))

story.append(Paragraph("3.1 Doğrudan Küresel Rakipler", H3))
direct = [
    ["Rakip", "Köken", "Güçlü Yönler", "Zayıf Yönler", "Yıllık Fiyat (yaklaşık)"],
    ["ClearPoint Strategy", "ABD", "BSC, KPI, raporlama olgun", "EFQM yok, Türkçe yok, pahalı", "$15K–$60K+"],
    ["Cascade Strategy", "Avustralya", "Modern UX, OKR + Strateji", "EFQM yok, süreç modülü zayıf", "$21–$49/kullanıcı/ay"],
    ["Spider Impact", "ABD", "BSC + KPI, dashboard güçlü", "EFQM kısıtlı, lokalizasyon zayıf", "$12K–$50K"],
    ["AchieveIt", "ABD", "Plan yürütme, görev takibi", "BSC/EFQM modülü yok", "$30K–$120K"],
    ["Workboard", "ABD", "OKR + AI, exec dashboard", "Pahalı, EFQM/Süreç yok", "$45K+"],
    ["Quantive (eski Gtmhub)", "Bulgaristan/UK", "OKR lider, AI insights", "EFQM yok, BSC sınırlı", "$8–$18/kullanıcı/ay"],
    ["Profit.co", "ABD/Hindistan", "OKR + KPI uygun fiyat", "EFQM yok, Türkçe sınırlı", "$7–$15/kullanıcı/ay"],
    ["i-nexus", "İngiltere", "Hoshin Kanri lider", "Eski UX, pahalı, dar pazar", "$25K+"],
]
for row in direct[1:]:
    for i, c in enumerate(row):
        row[i] = Paragraph(c, SMALL)
direct[0] = [Paragraph(c, TH) for c in direct[0]]
t = Table(direct, colWidths=[3.4*cm, 2.0*cm, 4.4*cm, 4.4*cm, 3.4*cm], repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1e3a8a")),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f1f5f9")]),
    ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#cbd5e1")),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("FONTNAME", (0,0), (-1,-1), FONT),
    ("LEFTPADDING", (0,0), (-1,-1), 6),
    ("RIGHTPADDING", (0,0), (-1,-1), 6),
    ("TOPPADDING", (0,0), (-1,-1), 7),
    ("BOTTOMPADDING", (0,0), (-1,-1), 7),
]))
story.append(t)
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph("3.2 Yerli ve Dolaylı Rakipler", H3))
local = [
    ["Rakip", "Tip", "Güçlü", "Zayıf"],
    ["Logo CPM / Logo Mind", "Yerli ERP eklenti", "Kurumsal müşteri kitlesi", "Esnek değil, modern UX yok"],
    ["Mikro Stratejik Planlama", "Yerli ERP eklenti", "Mali entegrasyon", "EFQM/Hoshin yok"],
    ["EFQM danışmanlık + Excel", "Manuel", "Düşük yazılım maliyeti", "Manuel hata, izlenebilirlik yok"],
    ["KalDer ödülü hazırlık araçları", "Niş", "EFQM uzmanlığı", "Yazılım değil, danışmanlık"],
    ["Power BI + Excel + SharePoint", "Self-built", "Esnek, ucuz görünür", "TCO yüksek, kurum hafızası kayıp"],
    ["Smartsheet / Asana / Monday", "Görev yönetim", "Modern, kolay benimseme", "Strateji/EFQM yok"],
    ["SAP SuccessFactors", "Büyük IK paketi", "Bireysel performans güçlü", "EFQM/Süreç yok, pahalı, ağır"],
]
for row in local[1:]:
    for i, c in enumerate(row):
        row[i] = Paragraph(c, SMALL)
local[0] = [Paragraph(c, TH) for c in local[0]]
t = Table(local, colWidths=[4*cm, 3*cm, 4.8*cm, 4.8*cm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1e3a8a")),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
    ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#cbd5e1")),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
]))
story.append(t)

# 4. Özellik karşılaştırma
story.append(PageBreak())
story.append(Paragraph("4. Özellik Karşılaştırma Matrisi", H2))
story.append(Paragraph(
    '<font color="#16a34a"><b>VAR</b></font> = Tam destek &nbsp;·&nbsp; '
    '<font color="#ca8a04"><b>KISMİ</b></font> = Kısmi destek &nbsp;·&nbsp; '
    '<font color="#dc2626"><b>YOK</b></font> = Yok', SMALL))
story.append(Spacer(1, 0.2*cm))

feat = [
    ["Özellik", "Kokpitim", "ClearPoint", "Cascade", "Quantive", "Logo CPM", "i-nexus"],
    ["EFQM 2025 Modeli", "✓", "✗", "✗", "✗", "◐", "✗"],
    ["Hoshin / X-Matrix", "✓", "◐", "◐", "✗", "✗", "✓"],
    ["BSC (Kaplan-Norton)", "✓", "✓", "✓", "◐", "◐", "◐"],
    ["OKR", "◐", "◐", "✓", "✓", "✗", "✗"],
    ["Süreç & KPI ağacı", "✓", "◐", "◐", "✗", "◐", "◐"],
    ["Proje & Portföy", "✓", "◐", "◐", "✗", "◐", "◐"],
    ["RAID Log", "✓", "✗", "✗", "✗", "✗", "◐"],
    ["EVM / CPM (Earned Value)", "✓", "✗", "✗", "✗", "✗", "◐"],
    ["VRIO / SWOT / Blue Ocean", "✓", "✗", "◐", "✗", "✗", "◐"],
    ["Bireysel Karne", "✓", "◐", "◐", "◐", "✓", "✗"],
    ["AI Erken Uyarı / Yön. Özeti", "✓", "◐", "◐", "✓", "✗", "✗"],
    ["Çok kiracılı (multi-tenant)", "✓", "✓", "✓", "✓", "◐", "◐"],
    ["Türkçe arayüz", "✓", "✗", "✗", "✗", "✓", "✗"],
    ["EFQM Tanınma seviyeleri", "✓", "✗", "✗", "✗", "✗", "✗"],
    ["Replan Tetikleyici", "✓", "✗", "✗", "✗", "✗", "✗"],
    ["Mobil uygulama", "◐", "✓", "✓", "✓", "◐", "✗"],
    ["API & webhook", "✓", "✓", "✓", "✓", "◐", "◐"],
    ["On-premise / VM kurulum", "✓", "✗", "✗", "✗", "✓", "◐"],
    ["KVKK / Veri yerelliği (TR)", "✓", "✗", "✗", "✗", "✓", "✗"],
]
SYMBOL = ParagraphStyle("SYM", parent=styles["BodyText"], fontName=FONT_BOLD, fontSize=9, alignment=1, leading=12, textColor=colors.white)
def _badge(text, bg):
    p = Paragraph(text, SYMBOL)
    return Table([[p]], colWidths=[1.7*cm], style=TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
GREEN = colors.HexColor("#16a34a")
AMBER = colors.HexColor("#ca8a04")
RED = colors.HexColor("#dc2626")
for row in feat[1:]:
    for i, c in enumerate(row):
        if c == "✓":
            row[i] = _badge("VAR", GREEN)
        elif c == "◐":
            row[i] = _badge("KISMİ", AMBER)
        elif c == "✗":
            row[i] = _badge("YOK", RED)
        else:
            row[i] = Paragraph(c, BODY)
feat[0] = [Paragraph(c, TH) for c in feat[0]]
col_widths = [5.0*cm] + [2.1*cm]*6
t = Table(feat, colWidths=col_widths, repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1e3a8a")),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f1f5f9")]),
    ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#cbd5e1")),
    ("ALIGN", (1,0), (-1,-1), "CENTER"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("BACKGROUND", (1,1), (1,-1), colors.HexColor("#dbeafe")),
    ("FONTNAME", (0,0), (-1,-1), FONT),
    ("LEFTPADDING", (0,0), (-1,-1), 6),
    ("RIGHTPADDING", (0,0), (-1,-1), 6),
    ("TOPPADDING", (0,0), (-1,-1), 6),
    ("BOTTOMPADDING", (0,0), (-1,-1), 6),
]))
story.append(t)

# 5. SWOT
story.append(PageBreak())
story.append(Paragraph("5. Kokpitim SWOT Analizi", H2))
swot = [
    [Paragraph("<b>Güçlü Yönler (S)</b>", BODY), Paragraph("<b>Zayıf Yönler (W)</b>", BODY)],
    [Paragraph(
        "• EFQM Modeli 2025 + Hoshin + BSC + Süreç + Proje tek platformda<br/>"
        "• Türkçe terminoloji ve KVKK uyumu<br/>"
        "• K-Vektör ağırlıklandırma (özgün)<br/>"
        "• AI Erken Uyarı + Yönetici Özeti<br/>"
        "• Replan tetikleyici otomasyonu<br/>"
        "• On-premise / VM kurulum esnekliği<br/>"
        "• Modüler micro-blueprint mimarisi<br/>"
        "• Açık API + webhook", SMALL),
     Paragraph(
        "• Mobil uygulama eksik (responsive var, native yok)<br/>"
        "• Marka bilinirliği düşük<br/>"
        "• Referans müşteri sayısı sınırlı<br/>"
        "• OKR modülü tam değil<br/>"
        "• Global topluluk / pazar yeri yok<br/>"
        "• Onboarding sihirbazı zayıf<br/>"
        "• Görselleştirme zenginliği rakiplere göre az<br/>"
        "• Sertifikasyon (ISO 27001, SOC2) yok", SMALL)],
    [Paragraph("<b>Fırsatlar (O)</b>", BODY), Paragraph("<b>Tehditler (T)</b>", BODY)],
    [Paragraph(
        "• EFQM 2025 geçişi → kurumlar yazılım arıyor<br/>"
        "• Kamu DDO / dijital dönüşüm bütçeleri<br/>"
        "• Üniversite akreditasyon (YÖKAK) entegrasyonu<br/>"
        "• KalDer ödülü hazırlık pazarı<br/>"
        "• Kamu KVKK + veri yerelliği zorunlulukları<br/>"
        "• Ortadoğu / Türki Cumhuriyetler ihracat potansiyeli<br/>"
        "• AI ajan ekosistemi entegrasyonu (Claude, OpenAI)", SMALL),
     Paragraph(
        "• Küresel oyuncuların Türkçe lokalizasyonu (Cascade Türkçe başlatabilir)<br/>"
        "• Logo / Mikro gibi ERP'lerin modül eklemesi<br/>"
        "• Microsoft Viva Goals + Power BI kombinasyonunun yaygınlaşması<br/>"
        "• Açık kaynak alternatifler (Strategic Planner, OpenProject)<br/>"
        "• Müşterinin Excel + danışman ile yetinme alışkanlığı<br/>"
        "• Bütçe baskısı (kriz dönemi)", SMALL)],
]
t = Table(swot, colWidths=[8.3*cm, 8.3*cm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#dbeafe")),
    ("BACKGROUND", (0,2), (-1,2), colors.HexColor("#dcfce7")),
    ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#94a3b8")),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("LEFTPADDING", (0,0), (-1,-1), 8),
    ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ("TOPPADDING", (0,0), (-1,-1), 6),
    ("BOTTOMPADDING", (0,0), (-1,-1), 6),
]))
story.append(t)

# 6. Konumlandırma haritası (text-based)
story.append(PageBreak())
story.append(Paragraph("6. Konumlandırma Haritası", H2))
story.append(Paragraph(
    "İki eksen üzerinde rakip konumlandırması: <b>Y ekseni:</b> Kapsam genişliği (sadece OKR → tam EPM/CPM). "
    "<b>X ekseni:</b> Türkiye uyumu (lokalizasyon + KVKK + EFQM).", BODY))

pos_data = [
    ["", "Düşük TR uyumu ←", "→ Yüksek TR uyumu"],
    ["↑ Geniş kapsam", "ClearPoint, Spider Impact, AchieveIt", "★ KOKPITIM"],
    ["", "Workboard, SAP SuccessFactors", "Logo CPM (sınırlı modül)"],
    ["", "Cascade, Quantive, Profit.co", "Mikro Stratejik"],
    ["↓ Dar kapsam", "i-nexus (Hoshin), Asana, Monday", "EFQM danışman + Excel"],
]
t = Table(pos_data, colWidths=[3.5*cm, 6.5*cm, 6.5*cm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0f172a")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("BACKGROUND", (0,1), (0,-1), colors.HexColor("#0f172a")),
    ("TEXTCOLOR", (0,1), (0,-1), colors.white),
    ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#475569")),
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("BACKGROUND", (2,1), (2,1), colors.HexColor("#fef3c7")),
    ("FONTSIZE", (0,0), (-1,-1), 9),
    ("FONTNAME", (0,0), (-1,-1), FONT),
    ("FONTNAME", (2,1), (2,1), FONT_BOLD),
    ("FONTNAME", (0,0), (-1,0), FONT_BOLD),
    ("FONTNAME", (0,1), (0,-1), FONT_BOLD),
    ("TOPPADDING", (0,0), (-1,-1), 10),
    ("BOTTOMPADDING", (0,0), (-1,-1), 10),
]))
story.append(t)
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph(
    "Kokpitim sağ-üst kadranda neredeyse tek başınadır: geniş EPM kapsamı + yüksek Türkiye uyumu. "
    "Bu boş alan rekabet avantajının kaynağıdır.", BODY))

# 7. Fiyatlama
story.append(Paragraph("7. Fiyatlama Karşılaştırması", H2))
price = [
    ["Ürün", "Model", "Başlangıç", "Orta Ölçek", "Büyük"],
    ["ClearPoint", "Yıllık + kullanıcı", "$15K", "$30K", "$60K+"],
    ["Cascade", "Kullanıcı/ay", "$252/yıl/kul.", "$36K (100 kul.)", "$60K+"],
    ["Quantive", "Kullanıcı/ay", "$96–$216/yıl", "$15K", "$50K+"],
    ["Profit.co", "Kullanıcı/ay", "$84–$180/yıl", "$10K", "$30K"],
    ["Workboard", "Custom", "—", "$45K+", "$150K+"],
    ["i-nexus", "Custom", "—", "$25K+", "$100K+"],
    ["Logo CPM", "Custom + ERP", "₺50K", "₺200K", "₺800K+"],
    ["KOKPITIM (öneri)", "Kurum/yıl + kullanıcı", "₺36K", "₺120K", "₺350K"],
]
for row in price[1:]:
    for i, c in enumerate(row):
        row[i] = Paragraph(c, SMALL)
price[0] = [Paragraph(c, TH) for c in price[0]]
t = Table(price, colWidths=[4*cm, 3.2*cm, 3*cm, 3*cm, 3*cm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1e3a8a")),
    ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#fef3c7")),
    ("ROWBACKGROUNDS", (0,1), (-1,-2), [colors.white, colors.HexColor("#f1f5f9")]),
    ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#cbd5e1")),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("FONTNAME", (0,0), (-1,-1), FONT),
    ("FONTNAME", (0,-1), (-1,-1), FONT_BOLD),
]))
story.append(t)

# 8. Stratejik tavsiyeler
story.append(PageBreak())
story.append(Paragraph("8. Stratejik Tavsiyeler", H2))

recs = [
    ("R1. EFQM Tanınma Hızlı Kazanım Paketi",
     "EFQM ödül sürecindeki kurumlar için 'EFQM Hazırlık' özel paketi (template + danışmanlık + yazılım). "
     "Niş kategoride hızlı pazar payı."),
    ("R2. Üniversite (YÖKAK) Sürümü",
     "YÖKAK kalite süreçleri için hazır şablon. Üniversite başına ₺80K-₺200K'lık özel SKU. "
     "İlk 5 referans ücretsiz pilot ile elde edilebilir."),
    ("R3. Kamu Kurum Modülü",
     "Cumhurbaşkanlığı SBB stratejik plan formatı + 5018 sayılı kanun uyumu + İç kontrol eylem planı. "
     "Bakanlık ve büyükşehir belediyesi pazarı."),
    ("R4. OKR Modülü Tamamlama",
     "Quantive/Profit.co eşdeğer OKR akışı (hedef + key result + check-in + 1:1). "
     "BSC ile entegrasyon doğal avantaj."),
    ("R5. Mobil Uygulama (PWA → Native)",
     "Onay/bildirim/check-in akışları için PWA başlat; React Native ile native paketleme 6 ay içinde."),
    ("R6. Görselleştirme Atılımı",
     "Strateji haritası, ısı haritaları, sankey/alluvial, sparkline'lar — rakiplerin görsel zenginliğine yetiş."),
    ("R7. AI Ajan İşbirliği",
     "Claude Code + MCP ile 'Kokpitim Asistanı': doğal dilde KPI sorgulama, otomatik rapor, "
     "strateji türetme. Yerli yapay zeka entegrasyonu pazarlama mesajı olarak güçlü."),
    ("R8. Sertifikasyon ve Güven",
     "ISO 27001, KVKK uyum sertifikası, penetrasyon test raporu. Kamu ihalelerinde zorunlu."),
    ("R9. Ortaklık Modeli",
     "KalDer + danışmanlık firmaları + ERP entegratörleri ile kanal ortaklığı. Doğrudan satış yerine 70/30 model."),
    ("R10. Açık Kaynak / Topluluk Sürümü",
     "Kısıtlı 'Topluluk Sürümü' GitHub'da → marka bilinirliği, geliştirici akımı, ekosistem."),
]
for title, desc in recs:
    story.append(Paragraph(title, H3))
    story.append(Paragraph(desc, BODY))

# 9. Yol Haritası
story.append(Paragraph("9. 12 Aylık Rekabet Yol Haritası", H2))
roadmap = [
    ["Çeyrek", "Hedef", "Çıktı"],
    ["Q1", "EFQM Hazırlık paketi + 3 üniversite pilotu", "Referans + case study"],
    ["Q2", "OKR modülü + Mobil PWA + ISO 27001 hazırlık", "Özellik paritesi"],
    ["Q3", "Kamu kurum modülü + KalDer ortaklığı + Görselleştirme atılımı", "Pazar genişleme"],
    ["Q4", "AI Asistan + Türki Cumhuriyetler ihracat + 10 referans müşteri", "Ölçek + dış pazar"],
]
for row in roadmap[1:]:
    for i, c in enumerate(row):
        row[i] = Paragraph(c, SMALL)
roadmap[0] = [Paragraph(c, TH) for c in roadmap[0]]
t = Table(roadmap, colWidths=[2*cm, 7*cm, 7.5*cm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1e3a8a")),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f1f5f9")]),
    ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#cbd5e1")),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
]))
story.append(t)

# 10. Sonuç
story.append(Paragraph("10. Sonuç", H2))
story.append(Paragraph(
    "Kokpitim, sağ-üst pazar kadranında (geniş EPM kapsamı × yüksek Türkiye uyumu) "
    "neredeyse tek başına konumlanmıştır. Bu konumu sürdürülebilir kılmak için "
    "<b>EFQM 2025 liderliği</b>, <b>OKR modül paritesi</b>, <b>mobil deneyim</b> ve "
    "<b>sertifikasyon</b> öncelikli yatırım alanlarıdır. Kamu + üniversite + KalDer "
    "ortaklığı ile 12 ay içinde 10+ referans müşteri ve ₺5-8M ARR hedefi makuldür.", BODY))
story.append(Spacer(1, 0.4*cm))
story.append(Paragraph(
    "<i>Bu rapor pazar verisi, rakip web siteleri (Mayıs 2026 itibariyle) ve Kokpitim'in iç özellik envanteri "
    "temel alınarak hazırlanmıştır. Fiyat tahminleri kamuya açık tarifelerden veya analist raporlarından elde edilmiştir; "
    "müzakere ile %20-40 sapabilir.</i>", SMALL))


doc = SimpleDocTemplate(
    OUT, pagesize=A4,
    leftMargin=1.8*cm, rightMargin=1.8*cm,
    topMargin=1.8*cm, bottomMargin=1.8*cm,
    title="Kokpitim Rekabet Analizi", author="Kokpitim"
)

def _footer(canv, doc):
    canv.saveState()
    canv.setFont(FONT, 8)
    canv.setFillColor(colors.HexColor("#64748b"))
    canv.drawString(1.8*cm, 1*cm, "KOKPITIM — Rekabet Analizi · 2026-05-29")
    canv.drawRightString(A4[0]-1.8*cm, 1*cm, f"Sayfa {doc.page}")
    canv.restoreState()

doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
print(f"OK → {OUT}")
