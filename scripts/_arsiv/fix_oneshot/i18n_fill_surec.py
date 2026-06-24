# -*- coding: utf-8 -*-
"""Tek-seferlik: en.po'daki surec (+kalan boş/fuzzy) msgstr'larını doldur (i18n FAZ 3b).

polib yoksa düz metin parse. Sadece BOŞ veya #, fuzzy işaretli msgstr'ları doldurur;
zaten dolu (insan onaylı) çevirilere DOKUNMAZ. Sözlük TR msgid -> EN msgstr.
Çalıştır: .venv\Scripts\python.exe scripts\_arsiv\fix_oneshot\i18n_fill_surec.py
"""
import re

PO = "translations/en/LC_MESSAGES/messages.po"

T = {
    # faaliyetler.html
    "Süreç Faaliyetleri": "Process Activities",
    "Faaliyetler": "Activities",
    "Süreç Karnesi": "Process Scorecard",
    "Doküman No": "Document No",
    "Revizyon": "Revision",
    "Yıl": "Year",
    "Süreç": "Process",
    "Toplam": "Total",
    "Tamamlanan": "Completed",
    "Aylık işaretleme": "Monthly marking",
    "Veriler yükleniyor…": "Loading data…",
    "Faaliyet Ekle": "Add Activity",
    "Faaliyet": "Activity",
    "Durum": "Status",
    "İşlem": "Action",
    # ay kısaltmaları
    "Oca": "Jan", "Şub": "Feb", "Mar": "Mar", "Nis": "Apr", "May": "May", "Haz": "Jun",
    "Tem": "Jul", "Ağu": "Aug", "Eyl": "Sep", "Eki": "Oct", "Kas": "Nov", "Ara": "Dec",
    # index.html
    "Ağaç görünümü": "Tree view",
    "Kanban görünümü": "Kanban view",
    "Toplam Süreç": "Total Processes",
    "%(n)s kök süreç": "%(n)s root processes",
    "Toplam PG": "Total PIs",
    "%(n)s PG'siz süreç": "%(n)s processes without PIs",
    "Ortalama Skor": "Average Score",
    "tüm süreçler": "all processes",
    "Yüksek Performans": "High Performance",
    "skor ≥ 80": "score ≥ 80",
    "Kritik Süreç": "Critical Process",
    "skor &lt; 50": "score &lt; 50",
    "K-Vektör": "K-Vector",
    "Aktif": "Active",
    "ağırlıklı skorlama": "weighted scoring",
    "Süreç ara (ad veya kod)…": "Search process (name or code)…",
    "Tüm performanslar": "All performances",
    "Yüksek (≥80)": "High (≥80)",
    "Orta (50-79)": "Medium (50-79)",
    "Kritik (&lt;50)": "Critical (&lt;50)",
    "Hedefte": "On Target",
    "Risk altında": "At Risk",
    "Hedef dışı": "Off Target",
    "Veri yok": "No Data",
    "Görüntülenecek süreç yok": "No processes to display",
    "Süreç haritası, kurumun değer üreten akışlarını (örn. <i>Satış, Üretim, AR-GE, İK</i>) tanımlar. Her sürecin altında <b>Performans Göstergeleri (PG)</b> ile başarısı ölçülür. Tipik bir kurumda 8–15 kök süreç bulunur.":
        "The process map defines the value-producing flows of the organization (e.g. <i>Sales, Production, R&D, HR</i>). Each process is measured by its <b>Performance Indicators (PIs)</b>. A typical organization has 8–15 root processes.",
    "Size lider veya üye olarak atanan bir süreç olduğunda burada listelenir. Yöneticinizden süreç ataması talep edebilirsiniz.":
        "Processes assigned to you as lead or member are listed here. You can request a process assignment from your manager.",
    "İlk Süreci Ekle": "Add First Process",
    "Stratejik Planlama": "Strategic Planning",
    "Yeni Süreç Oluştur": "Create New Process",
    "Süreç en az bir <strong>alt stratejiye</strong> bağlanmalıdır (aşağıda). PG’ler ileride isteğe bağlı alt stratejiye bağlanabilir.":
        "A process must be linked to at least one <strong>sub-strategy</strong> (below). PIs can optionally be linked to a sub-strategy later.",
    "<strong>K-Vektör:</strong> Her seçili alt strateji için katkı %% girin; toplam en fazla 100 olmalıdır.":
        "<strong>K-Vector:</strong> Enter a contribution %% for each selected sub-strategy; the total must not exceed 100.",
    "Süreç Adı": "Process Name",
    "Örn: Satın Alma Süreci": "e.g. Procurement Process",
    "Süreç Kodu": "Process Code",
    "Pasif": "Inactive",
    "Beklemede": "On Hold",
    "Tamamlandı": "Completed",
    "Revizyon No": "Revision No",
    "Revizyon Tarihi": "Revision Date",
    "İlk Yayın Tarihi": "First Publish Date",
    "Üst Süreç (Parent)": "Parent Process",
    "— Bağımsız (Üst Süreç Yok) —": "— Independent (No Parent Process) —",
    "Başlangıç Sınırı": "Start Boundary",
    "Sürecin başlangıç noktası...": "The start point of the process...",
    "Bitiş Sınırı": "End Boundary",
    "Sürecin bitiş noktası...": "The end point of the process...",
    "Açıklama": "Description",
    "İsteğe bağlı açıklama": "Optional description",
    "Alt strateji bağlantısı ve K-Vektör katkı %": "Sub-strategy link and K-Vector contribution %",
    "Alt strateji bağlantısı": "Sub-strategy link",
    "(en az bir)": "(at least one)",
    "Seçili her alt strateji için <strong>katkı %%</strong> girin; toplam en fazla 100 olmalıdır. Ana/alt strateji <strong>ham ağırlıkları</strong> Stratejik Planlama (/sp) sayfasındadır.":
        "Enter a <strong>contribution %%</strong> for each selected sub-strategy; the total must not exceed 100. The <strong>raw weights</strong> of main/sub-strategies are on the Strategic Planning (/sp) page.",
    "Süreç Liderleri": "Process Leaders",
    "Kullanıcılar": "Users",
    "Seçilenleri ekle": "Add selected",
    "Seçilenleri çıkar": "Remove selected",
    "Ekle": "Add",
    "Çıkar": "Remove",
    "Seçilen Liderler": "Selected Leaders",
    "Süreç Üyeleri": "Process Members",
    "Seçilen Üyeler": "Selected Members",
    "Süreci Kaydet": "Save Process",
    # karne.html
    "SÜREÇ KARNESİ": "PROCESS SCORECARD",
    "Rev. tarihi": "Rev. date",
    "Rapor yılı": "Report year",
    "Bu süreçteki PG ağırlıkları ve başarı puanı aralıklarını kontrol eder": "Checks the PI weights and success score ranges in this process",
    "K-Vektör Analizi": "K-Vector Analysis",
    "AI YÖNETİCİ ÖZETİ": "AI EXECUTIVE SUMMARY",
    "Genel bilgiler": "General information",
    "Genel sağlık skoru": "Overall health score",
    "Seçili yıl PG gerçekleşme / hedef ortalamasına göre": "Based on the selected year's PI actual / target average",
    "KPI başarı dağılımı": "KPI success distribution",
    "Faaliyetlerin ilerlemesi": "Activity progress",
    "Genel faaliyet skoru": "Overall activity score",
    "KPI veri doluluk": "KPI data completeness",
    "Yönetici özeti (alt süreçler)": "Executive summary (sub-processes)",
    "Alt süreç": "Sub-process",
    "Süreç lideri (özet)": "Process leader (summary)",
    "İlerleme": "Progress",
    "Gösterge": "Indicator",
    "— PG seçin —": "— Select a PI —",
    "Grafik için bir PG seçin": "Select a PI for the chart",
    "Performans göstergeleri rapor yılı": "Performance indicators report year",
    "Gösterim": "View",
    "Görünüm periyodu": "View period",
    "Yıllık (yıl sonu)": "Annual (year-end)",
    "6 aylık": "Semi-annual",
    "Çeyreklik": "Quarterly",
    "Aylık": "Monthly",
    "Haftalık": "Weekly",
    "Günlük": "Daily",
    "Önceki dönem": "Previous period",
    "Sonraki dönem": "Next period",
    "Önceki": "Previous",
    "Sonraki": "Next",
    "Günlük ay (senkron)": "Daily month (synced)",
    "Veri Giriş Sihirbazı": "Data Entry Wizard",
    "PG ekle": "Add PI",
    "Excel'e aktar": "Export to Excel",
    "Yazdır": "Print",
    "PG tablo modalını aç": "Open PI table modal",
    "Tablo Görünümü": "Table View",
    "Henüz performans göstergesi eklenmemiş.": "No performance indicators added yet.",
    "Özet görünüm": "Summary view",
    "Faaliyet görünümü": "Activity view",
    "Kanban": "Kanban",
    "Aylık takip tablosu": "Monthly tracking table",
    "Faaliyet paneli": "Activity panel",
    "Özet kartlar + detay görünüm": "Summary cards + detail view",
    "Planlananlar": "Planned",
    "Devam Edenler": "In Progress",
    "Tamamlanan / İptal": "Completed / Cancelled",
    "Henüz faaliyet eklenmemiş.": "No activities added yet.",
    "Yeni Performans Göstergesi": "New Performance Indicator",
    "Gösterge Adı": "Indicator Name",
    "Performans göstergesi adı": "Performance indicator name",
    "Kodu": "Code",
    "Hedef Değer": "Target Value",
    "Hedef değer": "Target value",
    "Ölçüm Birimi": "Measurement Unit",
    "Listeden seçin veya kendi biriminizi yazın.": "Select from the list or type your own unit.",
    "Skor Ağırlığı (%)": "Score Weight (%)",
    "Ölçüm Periyodu": "Measurement Period",
    "6 ay": "6 months",
    "Yıllık": "Annual",
    "Hedef Yönü": "Target Direction",
    "Arttıkça İyi ↑": "Higher is Better ↑",
    "Azaldıkça İyi ↓": "Lower is Better ↓",
    "Hesaplama Yöntemi": "Calculation Method",
    "Ortalama": "Average",
    "Toplama": "Sum",
    "Son Değer": "Last Value",
    "Gösterge Türü": "Indicator Type",
    "Seçiniz": "Select",
    "İyileştirme": "Improvement",
    "Koruma": "Maintenance",
    "Bilgi Amaçlı": "Informational",
    "Hedef Belirleme Yöntemi": "Target Setting Method",
    "Rakibe Göre (RG)": "Competitor-Based (CB)",
    "Hedef Katsayısı Yöntemi (HKY)": "Target Coefficient Method (TCM)",
    "Hedef Konulamaz (HK)": "No Target (NT)",
    "Sabit Hedef (SH)": "Fixed Target (FT)",
    "Dalgalı Hedef (DH)": "Variable Target (VT)",
    "Sektöre Göre Hedef (SGH)": "Sector-Based Target (SBT)",
    "Alt Strateji (Opsiyonel)": "Sub-Strategy (Optional)",
    "-- Alt Strateji Seçiniz --": "-- Select Sub-Strategy --",
    "Önceki Yıl Ortalaması": "Previous Year Average",
    "Opsiyonel baz değer": "Optional baseline value",
    "Başarı Puanı Yapılandırması (Opsiyonel)": "Success Score Configuration (Optional)",
    "Aralık": "Range",
    "Aralık hakkında bilgi": "Range info",
    "Aralık açıklaması": "Range description",
    "%(i)s Puan": "%(i)s Points",
    "Beklentinin Çok Altında": "Far Below Expectations",
    "İyileştirmeye Açık": "Needs Improvement",
    "Hedefe Ulaşmış": "Target Achieved",
    "Hedefin Üzerinde": "Above Target",
    "Mükemmel": "Excellent",
    "Veri Girişi Sihirbazı": "Data Entry Wizard",
    "Performans göstergesi": "Performance indicator",
    "Veri tarihi": "Data date",
    "Gerçekleşen değer": "Actual value",
    "Örn: 42": "e.g. 42",
    "Açıklama (opsiyonel)": "Description (optional)",
    "İsteğe bağlı not": "Optional note",
    "Kayıt geçmişi": "Record history",
    "Bu PG için henüz kayıt yok.": "No records for this PI yet.",
    "Kayıt düzenle": "Edit record",
    "Veri tarihi değişmez; yalnızca gerçekleşen değer ve açıklama güncellenir.": "The data date does not change; only the actual value and description are updated.",
    "Kaydı pasifleştir": "Deactivate record",
    "Evet, pasifleştir": "Yes, deactivate",
    "Sütun gösterimi:": "Column display:",
    "Strateji": "Strategy",
    "Ağırlık": "Weight",
    "Birim": "Unit",
    "Periyot": "Period",
    "Yıllık hedef": "Annual target",
    "Önceki yıl": "Previous year",
    "Ağırlıklı başarı": "Weighted success",
    "PG Ekle": "Add PI",
    "PGV Ekle": "Add PIV",
    "Periyot veri detayı": "Period data detail",
    "Veri düzenle": "Edit data",
    "Gerçekleşen": "Actual",
    "Döküman No": "Document No",
    "Süreç seçin": "Select process",
    "Görüntülenecek süreç": "Process to display",
    "Görünüm": "View",
    "Kaydet": "Save",
    # bireysel/karne.html
    "AI PERFORMANS ÖZETİ": "AI PERFORMANCE SUMMARY",
    "Bireysel Performans Karnem": "My Individual Performance Scorecard",
    "Kişisel PG ve faaliyet takibi": "Personal PI and activity tracking",
    "PG VERİ KAPSAMI": "PI DATA COVERAGE",
    "Veri girilen / toplam PG": "Data entered / total PIs",
    "FAALİYET TAMAMLAMA": "ACTIVITY COMPLETION",
    "İşaretlenen aylar / toplam ay": "Marked months / total months",
    "Toplam PG": "Total PIs",
    "Veri Girilen": "Data Entered",
    "Yıl özeti &amp; dikkat": "Year summary &amp; attention",
    "Seçili yılda veri kapsamı ve göstergelerinizin kısa özeti.": "A brief summary of data coverage and your indicators for the selected year.",
    "Sarı uyarı pill’lerindeki “hedefe göre zayıf” ifadesi, son girilen aylık değer ile hedefi karşılaştıran <strong>bilgi amaçlı bir tahmindir</strong>; İK veya resmi ölçüm yerine geçmez.":
        "The “weak against target” label in the yellow warning pills is an <strong>informational estimate</strong> comparing the last entered monthly value with the target; it does not replace HR or official measurement.",
    "Bu yıl ne yaptım?": "What did I do this year?",
    "Henüz kayıtlı bir hareket yok. PG verisi girin veya faaliyet aylarını işaretleyin.": "No recorded activity yet. Enter PI data or mark activity months.",
    "Performans Göstergelerim": "My Performance Indicators",
    "Veri var": "Has data",
    "Geçmiş/geçerli ay, veri yok": "Past/current month, no data",
    "Satıra tıklayınca yıllık detay ve mini grafik açılır.": "Click a row to open annual detail and a mini chart.",
    "Gösterge": "Indicator",
    "Hedef": "Target",
    "Faaliyetlerim": "My Activities",
    "Silme işlemi <strong>sizin adınıza</strong> kayda geçer (kim / ne zaman).": "The deletion is recorded <strong>on your behalf</strong> (who / when).",
}

with open(PO, encoding="utf-8") as f:
    content = f.read()

# msgid bloklarını işle: msgid (tek veya çok satır) + opsiyonel #, fuzzy + msgstr
# Basit yaklaşım: her "msgid \"X\"\nmsgstr \"\"" veya fuzzy olanı sözlükten doldur.
filled = 0
skipped_dup = 0

def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')

# Tek-satır msgid'ler için satır-bazlı geçiş
lines = content.split("\n")
out = []
i = 0
while i < len(lines):
    line = lines[i]
    m = re.match(r'^msgid "(.*)"$', line)
    if m:
        mid = m.group(1)
        # unescape
        mid_u = mid.replace('\\"', '"').replace("\\\\", "\\")
        # sonraki satır(lar): boş çok-satır msgid değilse msgstr'a bak
        j = i + 1
        if j < len(lines) and re.match(r'^msgstr "(.*)"$', lines[j]):
            ms = re.match(r'^msgstr "(.*)"$', lines[j]).group(1)
            # fuzzy önceki satırlarda mı
            is_fuzzy = any("fuzzy" in lines[k] for k in range(max(0, i-3), i))
            if (ms == "" or is_fuzzy) and mid_u in T:
                # fuzzy yorumunu kaldır (önceki #, fuzzy satırı)
                if is_fuzzy:
                    # out'tan son fuzzy satırını temizle
                    for k in range(len(out)-1, max(0, len(out)-4), -1):
                        if "#, fuzzy" in out[k]:
                            del out[k]; break
                out.append(line)
                out.append('msgstr "%s"' % esc(T[mid_u]))
                filled += 1
                i = j + 1
                continue
    out.append(line)
    i += 1

with open(PO, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print(f"[i18n_fill_surec] {filled} msgstr dolduruldu")
