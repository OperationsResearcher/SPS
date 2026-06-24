# -*- coding: utf-8 -*-
"""Tek-seferlik: en.po'daki surec (+kalan boş/fuzzy) msgstr'larını doldur (i18n FAZ 3b).

polib yoksa düz metin parse. Sadece BOŞ veya #, fuzzy işaretli msgstr'ları doldurur;
zaten dolu (insan onaylı) çevirilere DOKUNMAZ. Sözlük TR msgid -> EN msgstr.
Çalıştır: .venv\Scripts\python.exe scripts\_arsiv\fix_oneshot\i18n_fill_surec.py
"""
import re

PO = "translations/en/LC_MESSAGES/messages.po"

import os, json
_SUPP = os.path.join(os.path.dirname(__file__), "i18n_supplement.json")

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
    # bildirim/index.html
    "Bildirimler": "Notifications",
    "%(n)s bildirim": "%(n)s notifications",
    "Tümünü Okundu İşaretle": "Mark All as Read",
    "Bildirim yok": "No notifications",
    "Şu an okunmamış bildiriminiz bulunmuyor. Sisteme yeni bir aksiyon gerektiğinde (PG sınır aşımı, faaliyet gecikmesi, atanan görev, replan tetikleyici vb.) bildirimler burada görünür.":
        "You have no unread notifications right now. When a new action is required in the system (PI threshold breach, activity delay, assigned task, replan trigger, etc.) notifications will appear here.",
    "Bildirim e-postası ve kanal ayarları": "Notification email and channel settings",
    "Bildirim Ayarları": "Notification Settings",
    "Masaüstü": "Desktop",
    # analiz/index.html
    "Performans Analitiği": "Performance Analytics",
    "Süreç ara…": "Search process…",
    "— Süreç Seçin —": "— Select Process —",
    "Trend frekansı": "Trend frequency",
    "Doğrusal Tahmin": "Linear Forecast",
    "Hareketli Ortalama": "Moving Average",
    "Mevsimsel": "Seasonal",
    "Tahmin yöntemi": "Forecast method",
    "Analiz Et": "Analyze",
    "Seçili sürecin (yoksa tüm) PG'lerinde anomali tara": "Scan anomalies in the selected process (or all) PIs",
    "Anomali Tara": "Scan Anomalies",
    "Sağlık Skoru": "Health Score",
    "Hesaplanıyor…": "Calculating…",
    "Trend": "Trend",
    "Son dönem yönü": "Latest period direction",
    "Tahmin (3 Dönem)": "Forecast (3 Periods)",
    "Sonraki dönem tahmini": "Next period forecast",
    "Anomali": "Anomaly",
    "Tespit edilen": "Detected",
    "Trend Analizi": "Trend Analysis",
    "Excel İndir": "Download Excel",
    "Trend verisi bulunamadı.": "No trend data found.",
    "Tahmin Analizi (3 Dönem)": "Forecast Analysis (3 Periods)",
    "Tahmin verisi bulunamadı.": "No forecast data found.",
    "Anomali Tespiti": "Anomaly Detection",
    "Analiz için süreç seçin": "Select a process for analysis",
    'Yukarıdan bir süreç seçip "Analiz Et" butonuna tıklayın.': 'Select a process above and click the "Analyze" button.',
    # ayarlar/index.html
    "Kurum": "Organization",
    "rol yok": "no role",
    "Tema": "Theme",
    "Aydınlık": "Light",
    "çoklu cihaz senkronlu": "synced across devices",
    "Zamanlanmış Rapor": "Scheduled Report",
    "aktif abonelik": "active subscription",
    "Ayar ara…": "Search settings…",
    "Kişisel": "Personal",
    "Hesap Ayarları": "Account Settings",
    "Bildirim tercihleri, tema, dil ve saat dilimi": "Notification preferences, theme, language and time zone",
    "Profil Bilgileri": "Profile Information",
    "Ad, unvan, departman ve profil fotoğrafı": "Name, title, department and profile photo",
    "E-posta Bildirimleri": "Email Notifications",
    "SMTP yapılandırması ve bildirim tercihleri": "SMTP configuration and notification preferences",
    "Zamanlanmış Raporlar": "Scheduled Reports",
    "Haftalık özet · sabah operasyonel · risk uyarısı · aylık PG": "Weekly summary · morning operational · risk alert · monthly PI",
    "Kurum Ayarları": "Organization Settings",
    "İletişim bilgileri ve logo": "Contact information and logo",
    "Platform Yönetimi": "Platform Management",
    "YALNIZ ADMIN": "ADMIN ONLY",
    "Yönetim Paneli": "Management Panel",
    "Login istatistikleri ve aktivite kayıtları": "Login statistics and activity logs",
    # ayarlar/eposta.html
    "E-posta Ayarları": "Email Settings",
    "E-posta": "Email",
    "Kurumunuza ait e-posta gönderim ayarlarını yapılandırın.": "Configure your organization's email sending settings.",
    "<strong>Özel SMTP kapalıyken</strong> sırayla kullanılır: sunucuda dolu ise <code>MAIL_*</code> ortam değişkenleri; yoksa platform <strong>Admin</strong> hesabının kurumunda kayıtlı özel SMTP (varsayılan çıkış). İsterseniz her zaman bu sayfadan kendi kurum SMTP’nizi açıp kullanabilirsiniz.":
        "<strong>When custom SMTP is off</strong>, used in order: <code>MAIL_*</code> environment variables if set on the server; otherwise the custom SMTP registered in the platform <strong>Admin</strong> account's organization (default outbound). You can always enable and use your own organization SMTP from this page.",
    "«Test Maili Gönder» önce onay penceresi açar; <strong>Gönder</strong> dediğinizde işlem yapılır.":
        "“Send Test Email” first opens a confirmation dialog; the action runs when you click <strong>Send</strong>.",
    "Kurumunuz özel SMTP kullanmıyor; gönderim <code>MAIL_*</code> tanımlıysa onunla, değilse <strong>Admin kurumunun</strong> kayıtlı SMTP’siyle yapılır. Yine de kendi alan adınızdan çıkış için buradan özel SMTP açmanız önerilir.":
        "Your organization does not use custom SMTP; sending is done via <code>MAIL_*</code> if defined, otherwise with the <strong>Admin organization's</strong> registered SMTP. Still, enabling custom SMTP here is recommended for outbound from your own domain.",
    "Özel SMTP Sunucusu": "Custom SMTP Server",
    "Kurumunuzun kendi e-posta sunucusunu kullanın.": "Use your organization's own email server.",
    "Özel SMTP'yi etkinleştir": "Enable custom SMTP",
    "SMTP Sunucu Adresi": "SMTP Server Address",
    "Kullanıcı Adı / E-posta": "Username / Email",
    "Şifre": "Password",
    "Değiştirmek için girin": "Enter to change",
    "Gönderici Adı": "Sender Name",
    "Firma Adı Bildirimleri": "Company Name Notifications",
    "Gönderici E-posta": "Sender Email",
    "STARTTLS kullan (port 587)": "Use STARTTLS (port 587)",
    "SSL/TLS kullan (port 465)": "Use SSL/TLS (port 465)",
    "Bağlantıyı Test Et": "Test Connection",
    "Hangi Olaylar İçin Mail Gitsin?": "Which Events Trigger Email?",
    "Sürece Atama": "Process Assignment",
    "Kullanıcı bir sürece lider veya üye olarak atandığında": "When a user is assigned to a process as leader or member",
    "Performans Göstergesi Değişikliği": "Performance Indicator Change",
    "Süreçte PG eklendiğinde veya güncellendiğinde": "When a PI is added or updated in a process",
    "Faaliyet Ekleme": "Activity Addition",
    "Sürece yeni faaliyet eklendiğinde": "When a new activity is added to a process",
    "Görev Atama": "Task Assignment",
    "Projede kullanıcıya görev atandığında": "When a task is assigned to a user in a project",
    "Test Maili Gönder": "Send Test Email",
    # ayarlar/zamanlanmis_raporlar.html
    "Düzenli aralıklarla otomatik olarak e-posta ile gönderilecek raporları seçin. Tüm raporlar <b>%(email)s</b> adresine gönderilir.":
        "Select reports to be automatically emailed at regular intervals. All reports are sent to <b>%(email)s</b>.",
    "Haftalık Strateji Özeti": "Weekly Strategy Summary",
    "Strateji sağlık skoru · PG performansı · gecikmiş faaliyetler · kritik riskler · girişim durumu. PDF eki ile gönderilir.":
        "Strategy health score · PI performance · overdue activities · critical risks · initiative status. Sent with a PDF attachment.",
    "Açık": "On",
    "Gün": "Day",
    "Pazartesi": "Monday", "Salı": "Tuesday", "Çarşamba": "Wednesday", "Perşembe": "Thursday",
    "Cuma": "Friday", "Cumartesi": "Saturday", "Pazar": "Sunday",
    "Saat": "Hour",
    "Şimdi önizle": "Preview now",
    "Önizleme": "Preview",
    "Sabah Operasyonel Özeti": "Morning Operational Summary",
    "Bugün biten/bekleyen faaliyet, atanan görev, kritik PG'ler. İş gününe başlarken kısa özet.":
        "Activities due/pending today, assigned tasks, critical PIs. A short summary to start the work day.",
    "Saat (her gün)": "Hour (every day)",
    "Risk & Anomali Uyarısı": "Risk & Anomaly Alert",
    "Açık kritik riskler, yüksek öncelikli PG anomalileri, ateşlenmiş replan tetikleyicileri.":
        "Open critical risks, high-priority PI anomalies, fired replan triggers.",
    "Sıklık": "Frequency",
    "Aylık PG Raporu": "Monthly PI Report",
    "Tüm PG'lerin ay sonu durumu: hedef üstü, hedef altı, veri eksikleri. Excel eki ile gönderilir.":
        "Month-end status of all PIs: above target, below target, missing data. Sent with an Excel attachment.",
    "Ayın günü": "Day of month",
    "<b>Not:</b> Tercihler hemen kaydedilir. İlk e-posta seçtiğiniz takvime göre tetiklenir; geçmişe yönelik gönderim yapılmaz. E-posta gönderiminin etkin olabilmesi için sistemin <code>DIGEST_SCHEDULER_ENABLED</code> ayarı aktif olmalıdır.":
        "<b>Note:</b> Preferences are saved immediately. The first email is triggered according to the schedule you selected; no retroactive sending is done. The system's <code>DIGEST_SCHEDULER_ENABLED</code> setting must be active for email sending to work.",
    # kurum/ayarlar.html
    "Kurum Ayarları": "Organization Settings",
    "Kurum bilgilerini ve logosunu güncelle.": "Update organization information and logo.",
    "Yetkili kullanıcılar düzenleyebilir.": "Authorized users can edit.",
    "Kurum Bilgileri": "Organization Information",
    "Kurum Adı": "Organization Name",
    "Sektör": "Sector",
    "Vergi No": "Tax No",
    "İletişim": "Contact",
    "Adres": "Address",
    "Telefon": "Phone",
    "Website": "Website",
    "K-Vektör (vizyon skoru)": "K-Vector (vision score)",
    "Açıldığında vizyon skoru 1000 ölçeğinde hiyerarşik hesaplanır.": "When enabled, the vision score is calculated hierarchically on a 1000 scale.",
    "<strong>Ana ve alt strateji ham ağırlıkları</strong> <a href=\"%(sp_url)s\">Stratejik Planlama</a> (/sp) sayfasından girilir ve düzenlenir.":
        "<strong>Main and sub-strategy raw weights</strong> are entered and edited on the <a href=\"%(sp_url)s\">Strategic Planning</a> (/sp) page.",
    "<strong>Süreç–alt strateji katkı %%</strong> değerleri <a href=\"%(surec_url)s\">Süreç Yönetimi</a> (/process) üzerinden süreç kaydı açılarak girilir.":
        "<strong>Process–sub-strategy contribution %%</strong> values are entered by opening a process record via <a href=\"%(surec_url)s\">Process Management</a> (/process).",
    "K-Vektör kullanımını etkinleştir": "Enable K-Vector usage",
    "Kurum genelinde vizyon skoru ve hiyerarşik ağırlıklar devreye girer.": "Vision score and hierarchical weights are activated across the organization.",
    "Kapalı": "Off",
    "Yıllık Plan Dönemleri": "Annual Plan Periods",
    "Açıldığında Stratejik Planlama sayfasında yıl seçici çubuğu görünür. Her plan yılı için KPI hedefleri, ağırlıklar ve metodlar ayrı ayrı tanımlanabilir. Kapalı olduğunda tüm KPI hesapları mevcut <strong>ProcessKpi</strong> değerlerine göre yapılır.":
        "When enabled, a year selector bar appears on the Strategic Planning page. KPI targets, weights and methods can be defined separately for each plan year. When off, all KPI calculations are based on the current <strong>ProcessKpi</strong> values.",
    "Yıllık dönem planlamasını etkinleştir": "Enable annual period planning",
    "SP sayfasına yıl seçici eklenir; KPI hedefleri yıl bazında ayrı tutulur.": "A year selector is added to the SP page; KPI targets are kept separately per year.",
    "Geçmiş yılları dahil et": "Include past years",
    "Seçilen yıldan bugüne kadar tüm yıllar otomatik oluşturulur. Mevcut SP verisi her yıla kopyalanır; sonradan yıl bazında değiştirilebilir.":
        "All years from the selected year to today are created automatically. Current SP data is copied to each year; it can later be changed per year.",
    "— Seçin —": "— Select —",
    "%(yr)s yılından itibaren": "from %(yr)s onwards",
    "%(yr)s–bugün arası yıllar aktif": "years from %(yr)s to today are active",
    "Kurum Logosu": "Organization Logo",
    "Mevcut Logo": "Current Logo",
    "Kurum logosu": "Organization logo",
    "Logo yok": "No logo",
    "Logo Yükle (max 2MB)": "Upload Logo (max 2MB)",
    "JPG/PNG/GIF/WEBP desteklenir.": "JPG/PNG/GIF/WEBP supported.",
    "Logoyu Yükle": "Upload Logo",
    # kurum/index.html
    "Kurum Paneli": "Organization Panel",
    "Özet Bilgiler": "Summary Info",
    "Henüz madde eklenmedi.": "No items added yet.",
    "Madde ekle": "Add item",
    "Süreç ve proje sayıları, <strong>size atanmış / erişiminiz olan</strong> kayıtlara göredir. Yöneticiler kurum genelini görür.":
        "Process and project counts are based on records <strong>assigned to / accessible by you</strong>. Managers see the organization-wide view.",
    "Stratejik Kimlik": "Strategic Identity",
    "Kurum vizyonu": "Organization vision",
    "Geleceğe yönelik ifade — tüm ekip için ortak pusula": "A forward-looking statement — a shared compass for the whole team",
    "Amaç": "Purpose",
    "Temel değerler": "Core values",
    "Etik kurallar": "Code of ethics",
    "Kalite politikası": "Quality policy",
    "Aktif Kullanıcı": "Active Users",
    "Aktif Süreç": "Active Processes",
    "Ana Strateji": "Main Strategy",
    "Süreç özeti": "Process summary",
    "PG, strateji, operasyon, risk ve performans": "PI, strategy, operations, risk and performance",
    "Erişim kapsamınızdaki süreçlere göre özet rakamlar. Grafikler için aşağıdaki panelleri açın.":
        "Summary figures based on processes within your access scope. Open the panels below for charts.",
    "Aktif süreç": "Active processes",
    "PG tanımlı süreç": "Processes with PI defined",
    "Aktif PG": "Active PIs",
    "Stratejisiz süreç": "Processes without strategy",
    "30g veri giren süreç": "Processes with data in 30d",
    "30g PG veri (satır)": "30d PI data (rows)",
    "Açık faaliyet": "Open activities",
    "Bu ay takip": "Tracked this month",
    "Bayat veri (PG)": "Stale data (PI)",
    "Geciken faaliyet": "Overdue activities",
    "Eksik tanım (PG)": "Incomplete definition (PI)",
    "Ort. PG skoru": "Avg. PI score",
    "Skoru olan PG": "PIs with score",
    "Skor &lt; 50": "Score &lt; 50",
    "Kurum geneli (yönetici)": "Organization-wide (manager)",
    "Tüm aktif süreçler — üyelik filtresi uygulanmaz. Yalnızca <strong>tenant_admin</strong> / <strong>executive_manager</strong> / <strong>Admin</strong>.":
        "All active processes — no membership filter applied. Only <strong>tenant_admin</strong> / <strong>executive_manager</strong> / <strong>Admin</strong>.",
    "30g veri (satır)": "30d data (rows)",
    "Grafikler": "Charts",
    "PG kapsamı &amp; strateji hizalaması": "PI coverage &amp; strategy alignment",
    "PG kapsamı": "PI coverage",
    "Süreçlerde PG tanımı dağılımı": "Distribution of PI definitions across processes",
    "Strateji hizalaması": "Strategy alignment",
    "Alt strateji bağlantısı": "Sub-strategy link",
    "Operasyonel hacim": "Operational volume",
    "Aktif PG, veri giren süreç, açık faaliyet ve bu ay tamamlanan takip": "Active PIs, processes with data, open activities and tracking completed this month",
    "Risk &amp; uyarı": "Risk &amp; alert",
    "PG için son geçerli veri <strong>%(days)s günden</strong> eskiyse “bayat”; geciken faaliyet; hedef/dönem eksik PG.":
        "A PI's last valid data is “stale” if older than <strong>%(days)s days</strong>; overdue activities; PIs missing target/period.",
    "Performans (PG skoru)": "Performance (PI score)",
    "<code class=\"text-[10px] bg-slate-200/50 dark:bg-slate-700/50 px-1 rounded\">calculated_score</code> — düşük (&lt;50), skorlu (≥50), skorsuz.":
        "<code class=\"text-[10px] bg-slate-200/50 dark:bg-slate-700/50 px-1 rounded\">calculated_score</code> — low (&lt;50), scored (≥50), unscored.",
    "Proje özeti": "Project summary",
    "Özet bilgiler, kurum geneli (yönetici) ve akordeon grafikler": "Summary info, organization-wide (manager) and accordion charts",
    "Erişiminiz olan projelere göre özet. Grafikler için aşağıdaki panelleri açın.": "Summary based on projects you can access. Open the panels below for charts.",
    "Aktif proje": "Active projects",
    "Bitişi geciken": "Overdue end",
    "30 gün içinde bitiş": "Ends within 30 days",
    "Açık görev": "Open tasks",
    "Geciken görev": "Overdue tasks",
    "7 gün vadesi": "Due in 7 days",
    "Açık RAID": "Open RAID",
    "Sağlık &lt; 50 proje": "Health &lt; 50 projects",
    "Kurum geneli — projeler (yönetici)": "Organization-wide — projects (manager)",
    "Tüm aktif projeler — üye/lider filtresi uygulanmaz.": "All active projects — no member/lead filter applied.",
    "Bitiş geciken": "End overdue",
    "30 gün bitiş": "30-day end",
    "7 gün vade": "7-day due",
    "Sağlık &lt;50": "Health &lt;50",
    "Proje bitişi &amp; görev dağılımı": "Project completion &amp; task distribution",
    "Proje bitiş durumu": "Project completion status",
    "Geciken, 30 gün içinde, diğer": "Overdue, within 30 days, other",
    "Açık görev dağılımı": "Open task distribution",
    "Vadesi geçen, 7 gün içinde, diğer": "Past due, within 7 days, other",
    "Risk ve yük göstergeleri": "Risk and load indicators",
    "Geciken görev, yaklaşan vade, RAID, düşük sağlık": "Overdue tasks, upcoming due, RAID, low health",
    "Stratejiler": "Strategies",
    "Ana Strateji Ekle": "Add Main Strategy",
    "Alt Ekle": "Add Sub",
    "Alt stratejiler": "Sub-strategies",
    "Bu strateji için henüz alt strateji yok. <span class=\"not-italic font-medium text-violet-600 dark:text-violet-400\">«Alt»</span> ile ekleyebilirsiniz.":
        "No sub-strategy for this strategy yet. You can add one with <span class=\"not-italic font-medium text-violet-600 dark:text-violet-400\">“Sub”</span>.",
    "Henüz strateji eklenmemiş": "No strategy added yet",
    # k_rapor/anomalies.html + index.html
    "KPI Anomali Tespiti": "KPI Anomaly Detection",
    "Z-score tabanlı sapma tespiti — tarihsel ortalamadan ±N standart sapma uzaktaki ölçümler.":
        "Z-score based deviation detection — measurements that are ±N standard deviations away from the historical mean.",
    "Z-Score eşiği": "Z-Score threshold",
    "1.5σ — geniş tespit": "1.5σ — broad detection",
    "2.0σ — standart (%%95 dışı)": "2.0σ — standard (outside %%95)",
    "2.5σ — sıkı": "2.5σ — strict",
    "3.0σ — sadece kritik (%%99.7 dışı)": "3.0σ — critical only (outside %%99.7)",
    "Slack webhook URL (opsiyonel)": "Slack webhook URL (optional)",
    "Önem Eşiği ≥": "Severity Threshold ≥",
    "Düşük (tümü)": "Low (all)",
    "Yüksek (sadece kritik)": "High (critical only)",
    "Tara": "Scan",
    "Slack'e Gönder": "Send to Slack",
    "Anomali bulunamadı": "No anomalies found",
    "Tüm KPI'lar tarihsel ortalamalar civarında.": "All KPIs are around their historical averages.",
    "K-Rapor — Raporlama Merkezi": "K-Report — Reporting Center",
    "K-Rapor": "K-Report",
    "Aktif sekmeyi Excel olarak indir": "Download active tab as Excel",
    "Sekme ara…": "Search tab…",
    "%(n)s sekme": "%(n)s tabs",
    # kr_tabs n/d
    "Kurumsal": "Corporate",
    "Vizyon skoru ve strateji başarı tablosu": "Vision score and strategy success table",
    "Süreç & PG": "Process & PI",
    "Süreç bazlı PG performans tablosu": "Process-based PI performance table",
    "Stratejik Uyum": "Strategic Alignment",
    "Strateji ↔ süreç hizalama analizi": "Strategy ↔ process alignment analysis",
    "Faaliyet": "Activity",
    "Faaliyet durumu ve ilerleme dağılımı": "Activity status and progress distribution",
    "Bireysel": "Individual",
    "Bireysel performans karne özetleri": "Individual performance scorecard summaries",
    "Veri Durumu": "Data Status",
    "PG veri doluluk ve eksik kayıtlar": "PI data completeness and missing records",
    "Risk": "Risk",
    "Risk ısı haritası ve kritik kayıtlar": "Risk heatmap and critical records",
    "Denetim": "Audit",
    "Aktivite ve değişiklik denetim kayıtları": "Activity and change audit logs",
    "Uyarı": "Alert",
    "Aktif sistem uyarıları ve tetikleyiciler": "Active system alerts and triggers",
    "K-Vektör": "K-Vector",
    "K-Vektör ağırlığı ve skor analizi": "K-Vector weight and score analysis",
    "EVM": "EVM",
    "Earned Value · PV/EV/AC, CPI/SPI": "Earned Value · PV/EV/AC, CPI/SPI",
    "Stratejik Analiz": "Strategic Analysis",
    "SWOT · TOWS · PESTEL · Porter 5 güç": "SWOT · TOWS · PESTEL · Porter 5 forces",
    "Paydaş": "Stakeholder",
    "Paydaş haritası ve etkileşim analizi": "Stakeholder map and interaction analysis",
    "Rekabet & A3": "Competition & A3",
    "Rakip kıyaslama ve A3 problem analizi": "Competitor benchmarking and A3 problem analysis",
    "PG Dağılım": "PI Distribution",
    "PG performans bant dağılımı": "PI performance band distribution",
    "Faaliyet Matris": "Activity Matrix",
    "Sorumlu × faaliyet matrisi": "Responsible × activity matrix",
    "Aktivite": "Activity",
    "Aktivite zaman çizelgesi takvimi": "Activity timeline calendar",
    "Kurum Kıyas": "Org Comparison",
    "Kurum içi karşılaştırma raporları": "Intra-organization comparison reports",
    "Str. Kapsama": "Str. Coverage",
    "Strateji kapsama ve boşluk analizi": "Strategy coverage and gap analysis",
    "Sorumlu": "Responsible",
    "Sorumlu kişi yük ve performans dağılımı": "Responsible person load and performance distribution",
    "SWOT Trend": "SWOT Trend",
    "SWOT öğelerinin zaman içinde gelişimi": "Evolution of SWOT items over time",
    "Bildirim": "Notification",
    "Bildirim ve uyarı sıklığı raporu": "Notification and alert frequency report",
    # paneller / kart başlıkları / th / açıklamalar
    "<b>Kurumsal Performans:</b> Vizyon skoru ve strateji bazlı ağırlıklı ortalama performans özeti. Yıl seçici ile dönemler arası kıyas yapılabilir.":
        "<b>Corporate Performance:</b> Vision score and strategy-based weighted average performance summary. Periods can be compared via the year selector.",
    "Vizyon Skoru": "Vision Score",
    "Vizyon Başarı Skoru": "Vision Success Score",
    "Strateji Bazlı Başarı": "Strategy-Based Success",
    "En İyi 5 Süreç": "Top 5 Processes",
    "En Düşük 5 Süreç": "Bottom 5 Processes",
    "Excel İndir": "Download Excel",
    "Kullanıcı Bazlı PG Başarı Tablosu": "User-Based PI Success Table",
    "PG": "PI",
    "Ort. Başarı": "Avg. Success",
    "Başarı %": "Success %",
    "Risk Başlığı": "Risk Title",
    "Olasılık": "Probability",
    "Etki": "Impact",
    "RPN": "RPN",
    "Risk Tablosu (RPN Sıralı)": "Risk Table (RPN Sorted)",
    "<strong>RPN (Risk Öncelik Puanı)</strong> = Olasılık × Etki (1–5 arası).":
        "<strong>RPN (Risk Priority Number)</strong> = Probability × Impact (1–5).",
    "Süreçlerde tetiklenen darboğaz kayıtları": "Bottleneck records triggered in processes",
    "Önem Derecesi": "Severity",
    "Not / Açıklama": "Note / Description",
    "Tetiklenme Tarihi": "Trigger Date",
    "Çözüm Tarihi": "Resolution Date",
    "Başarı oranı %50'nin altında olanlar": "Those with a success rate below %50",
    "Yüksek Riskler": "High Risks",
    "RPN &gt; 10 olan öncelikli riskler": "Priority risks with RPN &gt; 10",
    "<strong>Uyarı Merkezi</strong> — Seçili yılda anlık müdahale gerektiren üç alarm kategorisi:":
        "<strong>Alert Center</strong> — Three alarm categories requiring immediate action in the selected year:",
    "Bitiş tarihi geçmiş ve henüz tamamlanmamış": "Past due date and not yet completed",
    "Bitiş Tarihi": "End Date",
    "Gecikme (gün)": "Delay (days)",
    "Son 7 gün": "Last 7 days", "Son 30 gün": "Last 30 days", "Son 90 gün": "Last 90 days", "Son 180 gün": "Last 180 days",
    "Planlanan Değer": "Planned Value",
    "Bu tarihe kadar <b>tamamlanması planlanan</b> işin parasal karşılığı. Plana göre nerede olmamız gerekirdi?":
        "The monetary value of the work <b>planned to be completed</b> by this date. Where should we be according to the plan?",
    "Kazanılmış Değer": "Earned Value",
    "Bu tarihe kadar <b>gerçekten tamamlanan</b> işin parasal değeri. Gerçekte nerede miyiz?":
        "The monetary value of the work <b>actually completed</b> by this date. Where are we really?",
    "Fiili Maliyet": "Actual Cost",
    "Bu tarihe kadar <b>gerçekten harcanan</b> tutar. Cebimizden ne çıktı?":
        "The amount <b>actually spent</b> by this date. What came out of our pocket?",
    "Zaman Performans Endeksi": "Schedule Performance Index",
    "Maliyet Performans Endeksi": "Cost Performance Index",
    "Anlamı": "Meaning",
    "İyi": "Good",
    "Programın önünde + bütçenin altında — ideal": "Ahead of schedule + under budget — ideal",
    "Pahalı": "Expensive",
    "Hızlı ilerliyor ama bütçeyi aşıyor — kaynak verimliliği zayıf": "Progressing fast but over budget — weak resource efficiency",
    "Yavaş": "Slow",
    "Bütçe iyi ama program gerisinde — hız artırılmalı": "Budget is good but behind schedule — speed must increase",
    "Kritik": "Critical",
    "Hem geç hem pahalı — acil yeniden planlama": "Both late and expensive — urgent replanning",
    "Kazanılmış Değer (EVM) — Proje Snapshot Tablosu": "Earned Value (EVM) — Project Snapshot Table",
    "En güncel ölçüm her proje için bir satır": "One row per project with the latest measurement",
    "PV (Planlanan)": "PV (Planned)",
    "EV (Kazanılmış)": "EV (Earned)",
    "AC (Fiili)": "AC (Actual)",
    "SPI (Zaman)": "SPI (Schedule)",
    "CPI (Maliyet)": "CPI (Cost)",
    "Porter 5 Kuvvet": "Porter 5 Forces",
    "Paydaş Haritası": "Stakeholder Map",
    "Rol": "Role",
    "İlgi": "Interest",
    "Paydaş Anket Özeti": "Stakeholder Survey Summary",
    "Sorun": "Issue",
    "Tedbirler": "Measures",
    "Başarı Yüzdesi Dağılımı (Histogram)": "Success Percentage Distribution (Histogram)",
    "PG Dağılım Grafiği": "PI Distribution Chart",
    "En Çok Geciken Süreçler": "Most Delayed Processes",
    "Toplam": "Total",
    "Tamamlanan": "Completed",
    "Devam": "Ongoing",
    "İptal": "Cancelled",
    "Tamamlanma %": "Completion %",
    "Günlük Veri Giriş Aktivitesi": "Daily Data Entry Activity",
    "Son 30 Gün Trend": "Last 30 Days Trend",
    "Kurum": "Organization",
    "PG Sayısı": "PI Count",
    "Veri Girilen": "Data Entered",
    "Hedefte": "On Target",
    "Riskli": "At Risk",
    "Strateji": "Strategy",
    "Alt Str.": "Sub-Str.",
    "Bağlı Süreç": "Linked Process",
    "Boş Alt Str.": "Empty Sub-Str.",
    "En Çok Geciken Kişiler": "Most Delayed People",
    "Kişi": "Person",
    "Gecikme %": "Delay %",
    "Sorumlu Detay Tablosu": "Responsible Detail Table",
    "SWOT Madde Sayısı Trendi": "SWOT Item Count Trend",
    "Güçlü": "Strengths",
    "Zayıf": "Weaknesses",
    "Fırsat": "Opportunities",
    "Tehdit": "Threats",
    "Yıllık SWOT/TOWS Özet Tablosu": "Annual SWOT/TOWS Summary Table",
    "SWOT Toplam": "SWOT Total",
    "TOWS Toplam": "TOWS Total",
    "Son 30 Gün Bildirim Trendi": "Last 30 Days Notification Trend",
    "Okunmayan Bildirimlerin Yaşlanması": "Aging of Unread Notifications",
    "Kaç gündür okunmadı?": "How many days unread?",
    "En Çok Bildirim Alan Kullanıcılar": "Users Receiving Most Notifications",
    "İlk 10": "Top 10",
    "Faaliyet Durumu": "Activity Status",
    "Son Tarih": "Last Date",
    "Değer": "Value",
    "Giren": "Entered By",
    "Veri Girilmiş PG": "PIs with Data",
    "Toplam Giriş": "Total Entries",
    "Son Giriş": "Last Entry",
    "Performans": "Performance",
    "Aylık Tamamlanan": "Monthly Completed",
    "Geciken Faaliyetler": "Overdue Activities",
    "Proje Portföy Durumu": "Project Portfolio Status",
    "GitHub tarzı ısı haritası": "GitHub-style heatmap",
    "SPI": "SPI", "CPI": "CPI", "SO": "SO", "WO": "WO", "WT": "WT",
    "Z-score tabanlı sapma tespiti — tarihsel ortalamadan ±N standart sapma uzaktaki ölçümler.":
        "Z-score based deviation detection — measurements that are ±N standard deviations away from the historical mean.",
    "<b>Süreç & PG Tablosu:</b> Süreç × dönem ısı haritası — her süreç için PG hedef/gerçekleşme çapraz tablosu ve renk kodlu durum gösterimi.":
        "<b>Process & PI Table:</b> Process × period heatmap — a cross table of PI target/actual for each process with color-coded status indicators.",
    "<b>Stratejik Uyum:</b> Strateji → süreç → PG katkı ağacı. Hangi stratejinin hangi süreçlere ve PG'lere bağlı olduğunu gösterir; bağlantısız alanlar boşluk olarak işaretlenir.":
        "<b>Strategic Alignment:</b> Strategy → process → PI contribution tree. Shows which strategy is linked to which processes and PIs; unlinked areas are marked as gaps.",
    "<b>Faaliyet Durumu:</b> Tüm faaliyetlerin durum ve ilerleme dağılımı — tamamlanan, devam eden, geciken ve planlanan faaliyetlerin süreç bazlı özeti.":
        "<b>Activity Status:</b> Status and progress distribution of all activities — a process-based summary of completed, ongoing, delayed and planned activities.",
    "<b>Bireysel Performans:</b> Kullanıcı bazlı bireysel PG sahipliği ve karne özetleri. Hedef hizalama yüzdesi ve üst yönetim karne görünümü.":
        "<b>Individual Performance:</b> User-based individual PI ownership and scorecard summaries. Target alignment percentage and executive scorecard view.",
    "<b>Veri Durumu:</b> PG ölçüm veri doluluk raporu — hangi PG'lerin son dönemde güncel veri girişi yapıldığını, hangilerin boş kaldığını gösterir.":
        "<b>Data Status:</b> PI measurement data completeness report — shows which PIs have recent data entered in the latest period and which remain empty.",
    "<b>K-Vektör Skoru:</b> Her stratejiye verilen ağırlık (%) ile o stratejinin gerçekleşen skor karşılaştırması. Yüksek ağırlık + düşük skor = en kritik odak noktası.":
        "<b>K-Vector Score:</b> A comparison of the weight (%) given to each strategy against that strategy's achieved score. High weight + low score = the most critical focus point.",
    "Bu tarihe kadar <b>tamamlanması planlanan</b> işin parasal karşılığı. Plana göre nerede olmamız gerekirdi?":
        "The monetary value of the work <b>planned to be completed</b> by this date. Where should we be according to the plan?",
    "Bu tarihe kadar <b>gerçekten tamamlanan</b> işin parasal değeri. Gerçekte nerede miyiz?":
        "The monetary value of the work <b>actually completed</b> by this date. Where are we really?",
    "<b>Stratejik Analiz Paketi:</b> SWOT · TOWS · PESTEL · Porter 5 Güç analizlerinin birleşik görünümü. Stratejik çevre taraması ve yönlendirici aksiyonlar.":
        "<b>Strategic Analysis Package:</b> A combined view of SWOT · TOWS · PESTEL · Porter 5 Forces analyses. Strategic environment scanning and directive actions.",
    "<b>Paydaş Haritası:</b> Kilit paydaşların etki-ilgi matrisinde konumlandırılması. Yüksek etki + yüksek ilgi = aktif yönetim gerektiren paydaşlar.":
        "<b>Stakeholder Map:</b> Positioning of key stakeholders on the power-interest matrix. High power + high interest = stakeholders requiring active management.",
    "<b>Rekabet & A3:</b> Rakip kıyas tablosu ve A3 problem analizi. Rekabetçi konumlandırma ve yapısal iyileştirme alanlarının görsel özeti.":
        "<b>Competition & A3:</b> Competitor benchmarking table and A3 problem analysis. A visual summary of competitive positioning and structural improvement areas.",
    "<b>PG Bant Dağılımı:</b> Tüm performans göstergelerinin hedef bandına göre dağılımı — üstün (≥%110), normal (%90–110), gelişim (%70–90), kritik (&lt;%70).":
        "<b>PI Band Distribution:</b> Distribution of all performance indicators by target band — superior (≥%110), normal (%90–110), developing (%70–90), critical (&lt;%70).",
    "<b>Faaliyet Matrisi:</b> Süreç bazlı faaliyet durum matrisi — her süreçte kaç faaliyet tamamlandı, devam ediyor, gecikti. Gecikme odaklı sıralama.":
        "<b>Activity Matrix:</b> Process-based activity status matrix — how many activities were completed, are ongoing or delayed in each process. Delay-focused ordering.",
    "<b>Aktivite Takvimi:</b> GitHub commit haritası tarzında veri giriş yoğunluğu takvimi — hangi günlerde ne kadar ölçüm ve faaliyet aktivitesi yapıldığı.":
        "<b>Activity Calendar:</b> A data entry intensity calendar in GitHub commit-map style — how much measurement and activity was done on which days.",
    "<b>Kurum Kıyas:</b> Aynı platform üzerindeki diğer kurumlarla anonim performans karşılaştırması — strateji ve süreç skor ortalamaları.":
        "<b>Org Comparison:</b> Anonymous performance comparison with other organizations on the same platform — strategy and process score averages.",
    "<b>Strateji Kapsama:</b> Her stratejinin süreç ve PG ile kapsama oranı — bağlantısız (kapsanmamış) stratejiler boşluk analizi ile işaretlenir.":
        "<b>Strategy Coverage:</b> Coverage ratio of each strategy by process and PI — unlinked (uncovered) strategies are marked via gap analysis.",
    "<b>Sorumlu Analizi:</b> Kişi başına faaliyet yükü — her kullanıcının atandığı faaliyet sayısı, tamamlanma ve gecikme oranı. İş dağılımı dengesizlikleri görünür.":
        "<b>Responsible Analysis:</b> Activity load per person — the number of activities assigned to each user, completion and delay rates. Workload distribution imbalances become visible.",
    "<b>SWOT Trend:</b> SWOT ve TOWS madde sayılarının tüm yıllar boyunca değişimi. Stratejik odak evrimini ve güçlü/zayıf yön dengesini gösterir.":
        "<b>SWOT Trend:</b> The change in SWOT and TOWS item counts across all years. Shows the evolution of strategic focus and the balance of strengths/weaknesses.",
    "<b>Bildirim Analizi:</b> Bildirim gönderim ve okuma istatistikleri — tür dağılımı, okunmayan sayısı, yaşlanma dağılımı ve en aktif bildirim kullanıcıları.":
        "<b>Notification Analysis:</b> Notification send and read statistics — type distribution, unread count, aging distribution and the most active notification users.",
    "Verinin <strong>hangi güne / olaya ilişkin</strong> olduğunu seçin (ör. anketin yapıldığı gün). <strong>Kaydet</strong> ile sisteme işlendiği tarih ve saat <strong>otomatik</strong> kaydedilir; yıl ve dönem bu veri tarihine göre PG ölçüm tipine uygun hesaplanır.":
        "Select <strong>which day / event the data relates to</strong> (e.g. the day the survey was conducted). When you click <strong>Save</strong>, the date and time it was recorded into the system are saved <strong>automatically</strong>; the year and period are calculated according to this data date based on the PI measurement type.",
    "Veri, <strong>kendi adınıza</strong> süreç karnesine ve bireysel karnenize yazılır.":
        "The data is written to the process scorecard and your individual scorecard <strong>under your own name</strong>.",
    "Kayıt <strong>kalıcı olarak silinmez</strong>. Pasif yapılır; skor ve raporlarda kullanılmaz.":
        "The record is <strong>not permanently deleted</strong>. It is deactivated; it is not used in scores or reports.",
    # fuzzy düzeltmeleri (k_rapor th/başlık)
    "Orta": "Medium",
    "Süreç × Dönem Isı Haritası": "Process × Period Heatmap",
    "Strateji → Süreç Katkı Ağacı": "Strategy → Process Contribution Tree",
    "Bitiş": "End",
    "Proje": "Project",
    "Başlangıç": "Start",
    "Bireysel PG Detay Listesi": "Individual PI Detail List",
    "Kod": "Code",
    "PG Adı": "PI Name",
    "Kaynak": "Source",
    "Veri Girilen PG'ler": "PIs with Data Entered",
    "PG Kodu": "PI Code",
    "Veri Girilmeyen PG'ler": "PIs without Data Entered",
    "Süreç Olgunluk Seviyeleri": "Process Maturity Levels",
    "Darboğaz Geçmişi": "Bottleneck History",
    "İşlem Dağılımı": "Transaction Distribution",
    "En Aktif Kullanıcılar": "Most Active Users",
    "Son İşlemler": "Recent Transactions",
    "Tarih": "Date",
    "Kritik Performans Göstergeleri": "Critical Performance Indicators",
    "Ana Strateji Ağırlıkları": "Main Strategy Weights",
    "Ağırlık Tablosu": "Weight Table",
    "Alt Strateji Ağırlıkları": "Sub-Strategy Weights",
    "Alt Strateji": "Sub-Strategy",
    "Ham Ağırlık": "Raw Weight",
    "SWOT Analizi": "SWOT Analysis",
    "TOWS Matrisi": "TOWS Matrix",
    "PESTEL Analizi": "PESTEL Analysis",
    "Rekabetçi Analiz": "Competitive Analysis",
    "A3 Raporları": "A3 Reports",
    "En Düşük Performanslı PG'ler": "Lowest Performing PIs",
    "Süreç Bazlı Faaliyet Durumu": "Process-Based Activity Status",
    "Süreç Faaliyet Detay Tablosu": "Process Activity Detail Table",
    "Geciken": "Delayed",
    "Kurum Performans Karşılaştırması": "Organization Performance Comparison",
    "Kurum Detay Tablosu": "Organization Detail Table",
    "Strateji Kapsama Durumu": "Strategy Coverage Status",
    "Stratejisiz Süreçler": "Processes without Strategy",
    "Strateji Bazlı Kapsama Tablosu": "Strategy-Based Coverage Table",
    "Kişi Başına Faaliyet Yükü": "Activity Load per Person",
    "TOWS Strateji Sayısı Trendi": "TOWS Strategy Count Trend",
    "ST": "ST",
    "Bildirim Türü Dağılımı": "Notification Type Distribution",
}

# Ek sözlük (modül modül büyür): i18n_supplement.json
if os.path.exists(_SUPP):
    with open(_SUPP, encoding="utf-8") as _sf:
        _extra = json.load(_sf)
    T.update(_extra)
    print(f"[i18n_fill_surec] supplement: {len(_extra)} ek girdi yüklendi")

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

content2 = "\n".join(out)

# --- 2. geçiş: çok-satır msgid bloklarını doldur ---
# .po blokları boş satırla ayrılır. Her blokta msgid (bir/çok satır) + msgstr.
def join_quoted(seg):
    return "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', seg))

def unesc(s):
    return s.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')

blocks = content2.split("\n\n")
multi = 0
for bi, b in enumerate(blocks):
    if "msgid" not in b or "msgstr" not in b:
        continue
    mm = re.search(r'(^msgid .*?)(^msgstr )', b + "\n", re.S | re.M)
    if not mm:
        continue
    midseg = mm.group(1)
    msseg = b[mm.end(2)-len("msgstr "):]
    mid_u = unesc(join_quoted(midseg))
    ms_val = join_quoted(b[mm.start(2):])
    is_fuzzy = "fuzzy" in b
    if (ms_val == "" or is_fuzzy) and mid_u in T:
        en = T[mid_u]
        new_block = re.sub(r'#, fuzzy\n', '', b)
        # msgstr kısmını tek satıra yaz
        new_block = re.sub(r'(?ms)^msgstr (?:".*?"\s*)+', 'msgstr "%s"' % esc(en).replace('\n','\\n'), new_block)
        blocks[bi] = new_block.rstrip("\n")
        multi += 1

content3 = "\n\n".join(blocks)
with open(PO, "w", encoding="utf-8") as f:
    f.write(content3)

print(f"[i18n_fill_surec] {filled} tek-satır + {multi} çok-satır msgstr dolduruldu")
