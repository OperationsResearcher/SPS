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
