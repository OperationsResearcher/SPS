# KOKPİTİM — Çoklu Dil (i18n) Analiz

> Durum envanteri: [`00-DURUM-RAPORU.md`](00-DURUM-RAPORU.md) · Plan: [`02-FAZ-PLANI.md`](02-FAZ-PLANI.md)

Bu belge **iş hacmini, teknik kararları ve riskleri** analiz eder.

---

## 1. İş hacmi (ölçülmüş)

| Katman | Birim | Tahmini string |
|--------|-------|----------------|
| Modern template `ui/templates/platform/` | 164 dosya | ~1.530 görünür metin + ~150 attribute |
| JS `ui/static/platform/js/` | 84 dosya | ~850 hardcoded string |
| Python `flash()` mesajları | ~74+ çağrı | ~74 |
| Legacy template `templates/` | 97 dosya | ~2.800 (büyük ölçüde ÖLÜ/fallback) |
| **Birincil hedef (modern + JS + flash)** | — | **~2.500–2.600** |

**En yoğun modüller (öncelik sırası):** `sp/` (~800), `admin/` (~540), `raporlar/` (~520),
`k_radar/` (~280), `surec/`, `k_rapor/`. **base.html** (~92 string) tüm sayfalarda görünür → en yüksek öncelik.

**En yoğun JS:** `surec.js` (290 satır), `k_radar_ks.js`, `k_rapor.js`, `tool_info_modal.js`, `admin.js`.

> Not: Legacy `templates/` (97 dosya) büyük ölçüde fallback/ölü. Modern `ui/templates/platform/` canlı yüzey.
> i18n YALNIZCA canlı yüzeye yapılmalı — ölü legacy'ye emek = strangler'a ters (bkz proje teknik borç notu).

## 2. Teknik kararlar

### 2.1 Çeviri yöntemi: gettext (`_()`) — STANDART
Flask-Babel + Jinja2 `{{ _("metin") }}` + Python `gettext as _`. Kaynak metin = Türkçe (msgid),
çeviri = İngilizce (msgstr). Avantaj: kaynak okunabilir kalır, eksik çeviri Türkçe'ye düşer (graceful).

### 2.2 JS metinleri: en zor kısım
JS gettext'i doğrudan göremez. Üç yaklaşım:
- **(A) Backend JSON'da çeviri:** API yanıtı `{"message": _("Başarılı")}` döndürür, JS sadece gösterir.
  → Sunucu-üretimi mesajlar için İDEAL (zaten çoğu fetch yanıtı `message` taşıyor).
- **(B) `data-i18n` attribute + JS sözlüğü:** Sayfa yüklenince `{{ _() }}` ile basılan gizli sözlükten oku.
- **(C) `window.I18N = {{ catalog|tojson }}`:** base.html'de aktif dilin JS sözlüğünü göm, JS `t("key")` kullanır.
- **Öneri:** Sunucu mesajları (A) ile; saf-istemci metinleri (toast başlıkları, "Emin misiniz?") (C) ile.

### 2.3 Tarih/sayı/para formatı
Babel `format_date`, `format_currency`, `format_number` filtreleri locale-aware. Şu an hiç kullanılmıyor.
TR `gg.aa.yyyy` / `1.234,56 ₺` vs EN `MM/dd/yyyy` / `1,234.56`. İkinci faz — kritik değil ama profesyonel.

### 2.4 `<html lang>` dinamik
`<html lang="{{ get_locale() }}">` — SEO/erişilebilirlik. base.html tek satır.

## 3. Sistem-üretimi sabit veri stratejisi (gri alan kararı)

| Veri | Şu an | Öneri |
|------|-------|-------|
| Modül adları (`system_modules.name`) | DB'de TR | `_()` sarmalı çeviri (sabit küme ~13 modül) VEYA `name_en` sütunu |
| Paket adları (Başlangıç/Yönetim/Strateji) | seed TR | `_()` — sadece 3 paket |
| Rol görünen adları | `ROLE_LABELS` map (JS) | TR/EN map'i genişlet; zaten merkezi (`app/constants/roles.py`?) |
| Status enum (`Planlandı`, `Aktif`) | model default TR | `_()` gösterimde; DB değeri sabit kalır (anahtar olarak) |
| Tomofil demo içeriği | tamamen TR | **DOKUNMA** — demo örneği, kullanıcı içeriği gibi |

**İlke:** Sabit kümeler (modül/paket/rol/status) için **DB değeri = değişmez anahtar**, **gösterim = `_()` çevirisi**.
`name_en` sütunu eklemek yerine gettext tercih → tek kaynak, migration yok, tutarlı. Status için dikkat:
`status="Planlandı"` hem DB değeri hem gösterim olamaz; gösterimde `_(p.status)` ile çevrilir.

## 4. Riskler ve tuzaklar

| Risk | Açıklama | Azaltma |
|------|----------|---------|
| **Hacim** | ~2.500 string elle işaretleme yorucu/hataya açık | Modül modül, faz faz; base.html önce; her faz test |
| **JS senkronu** | data-i18n anahtarı ile sözlük eşleşmezse metin kaybolur | (A) backend-mesaj yaklaşımını tercih et |
| **Çeviri kalitesi** | Otomatik/makine çeviri domain terimlerini bozar (PG, K-Vektör, EVM) | Domain sözlüğü sabit; UI-TERMINOLOJI.md'ye EN kolonu |
| **msgid kayması** | Kaynak Türkçe metin değişince çeviri kopar | msgid'i sabit tut; metin değişiminde `pybabel update` |
| **Eksik çeviri** | İngilizce'de boş msgstr → Türkçe görünür | Kabul edilebilir (graceful); CI'da %doluluk kontrolü |
| **Tomofil/içerik karışması** | Kullanıcı içeriğini yanlışlıkla `_()`'a almak | Yalnız sabit UI metni işaretle; içerik değişkenlerine dokunma |
| **Performans** | Her istekte locale + katalog | Babel cache'li; ihmal edilebilir |
| **base.html lang** | Demo/login sayfaları farklı base | Tüm base'leri kontrol et (`templates/base.html` + `ui/.../base.html`) |

## 5. Çevrilmeyecekler (netlik için)
- Kullanıcı içeriği (strateji/süreç/KPI/proje adları, açıklamalar)
- Tomofil demo seed verisi
- Kod sabitleri (route adları — zaten İngilizce yapıldı, URL tek-dil işi)
- Log mesajları (KURALLAR: log İngilizce zaten)
- `data-card-code`, endpoint adları, teknik anahtarlar

## 6. UI-TERMINOLOJI.md ile ilişki
Proje zaten bir terminoloji sözlüğüne sahip (`docs/UI-TERMINOLOJI.md`: tenant→Kurum, user→Kullanıcı...).
i18n bunu **tersine** kullanmalı: TR görünen terim → EN karşılığı. Bu sözlük İngilizce kolonu ile
genişletilirse çeviri tutarlılığının tek kaynağı olur. **Öneri: önce sözlüğe EN kolonu ekle, sonra çevir.**
