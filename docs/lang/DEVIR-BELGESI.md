# i18n Çoklu Dil (TR/EN) — DEVİR BELGESİ

> **Amaç:** Bu belge, i18n çalışmasının tamamını yeni bir sohbete/geliştiriciye devretmek için hazırlandı.
> **Tarih:** 2026-07-01 · **Durum:** ✅ Statik UI katmanı TAM · main'e merge + origin'e push edildi.
> **Kritik kısıt:** Tüm iş git remote'a (GitHub) push edildi ama **Test/Demo/Yayın'a DEPLOY EDİLMEDİ** (kullanıcı kısıtı: "yayına ve teste vermeyelim").

---

## 1. ÖZET — Ne yapıldı?

KOKPİTİM projesi baştan sona **iki dilli (Türkçe/İngilizce)** hale getirildi. Kullanıcı sağ üstteki
dil seçiciden (🇹🇷/🇬🇧) dili değiştirebiliyor; `/set-language/<lang>` route'u session + user tercihine yazıyor.

**Sonuç:** EN katalog **4742 msgid**, **0 boş / 0 fuzzy**. Tüm katmanlar çevrildi:

| Katman | Mekanizma | Nerede |
|--------|-----------|--------|
| Jinja şablon metinleri | `{{ _("...") }}` | `ui/templates/**` |
| Harici JS | `t("...")` + `window._I18N` map | `ui/static/platform/js/*.js` |
| Şablon-içi `<script>` | `t("...")` | inline script blokları |
| Backend flash | `flash(_("..."))` | route dosyaları |
| API JSON message | `"message": _("...")` | route dosyaları |
| Python sabit/label | `_()` veya `lazy_gettext()` | servisler, registry |

---

## 2. MİMARİ — Nasıl çalışıyor?

### 2.1 Backend (Python + Jinja)
- **Flask-Babel** kullanılıyor. `app/i18n.py::get_locale()` locale seçim zinciri:
  `?lang=` → `session['lang']` → `user.locale_preferences` → `Accept-Language` → `BABEL_DEFAULT_LOCALE (tr)`.
- **KRİTİK:** `BABEL_TRANSLATION_DIRECTORIES` MUTLAK yol olmalı — `app/i18n.py`'de
  `os.path.join(os.path.dirname(app.root_path), "translations")`. Göreli yol Flask-Babel'de `app/`'e
  göre çözülür → sessiz başarısızlık (eski bir bug, çözüldü).
- Şablonda: `{{ _("Türkçe metin") }}`. Python'da: `from flask_babel import gettext as _` → `_("...")`.

### 2.2 lazy_gettext — MODÜL-SEVİYESİ SABİTLER İÇİN ZORUNLU
- Modül-seviyesi sabitler (`MODULES=[...]`, `DEMO_ROLES={...}`, `ROLE_LABELS_TR={...}`) **import anında
  bir kez** değerlenir. Düz `gettext` orada Türkçe'ye SABİTLENİR — dil değişse bile çevrilmez (sessiz hata).
- ÇÖZÜM: bu dosyalarda `from flask_babel import lazy_gettext as _` (veya `as _l`). Her erişimde aktif dile göre çözer.
- **Tuzak:** `lazy_gettext` objesi JSON-serileştirilemez. `session[...]`'a veya `tojson`'a yazılıyorsa
  `str(...)` ile düz metne çevir. Örnekler: `micro/modules/demo/routes.py` (session yazımı),
  `app/constants/roles.py::role_labels_json()` (tojson-güvenli helper).
- Bu dosyalar: `micro/core/module_registry.py`, `micro/modules/demo/routes.py`, `app/constants/roles.py`.

### 2.3 JS i18n — window.t() mekanizması (FAZ 4'te sıfırdan kuruldu)
- `app/i18n.py::js_i18n_map()` aktif locale'in TÜM çeviri katalogunu `{tr_msgid: en_translation}`
  dict döndürür (default dilde boş → fallback Türkçe).
  **KRİTİK:** `flask_babel.get_locale()` kullanır (bizim session-tabanlı `get_locale()` `force_locale`'i görmez).
- `ui/templates/platform/base.html` (satır ~27) bunu enjekte eder:
  ```js
  window._I18N = {{ js_i18n_map() | tojson }};
  window.t = function(s, params) { /* _I18N[s] || s, + %(x)s interpolation */ };
  ```
- JS'de: `t("Türkçe metin")` → EN'de çeviri, TR'de Türkçe. Named arg: `t("%(n)s öğe", {n: 5})`.

### 2.4 Çeviri katalog akışı (message extraction pipeline)
```
bash scripts/i18n_extract.sh          # extract (pybabel + inline t()) → messages.pot → update .po
.venv/Scripts/python.exe scripts/_arsiv/fix_oneshot/i18n_fill_surec.py   # sözlükten doldur
.venv/Scripts/python.exe -m babel.messages.frontend compile -d translations   # .po → .mo
```

---

## 3. ÖNEMLİ ARAÇLAR (scripts)

| Dosya | İşlev |
|-------|-------|
| `scripts/i18n_extract.sh` | extract + update. Keyword'ler: `-k t -k _ -k _l -k gettext -k lazy_gettext -k ngettext`. **`extract_inline_t.py`'yi otomatik çağırır.** |
| `scripts/_arsiv/fix_oneshot/extract_inline_t.py` | **KRİTİK:** babel'in kaçırdığı `t()` çağrılarını toplar: (1) `.html` içi `<script>` blokları, (2) `.js` dosyalarındaki **`${t(...)}` template-literal** çağrıları. Bunlar olmadan JS dinamik metinleri katalога girmez. |
| `scripts/_arsiv/fix_oneshot/i18n_fill_surec.py` | `.po`'daki boş/fuzzy msgstr'ları TR→EN sözlükten doldurur. `i18n_supplement.json`'u yükler (`_SUPP`). Tek-satır + çok-satır msgid destekler (`po_escape`). |
| `scripts/_arsiv/fix_oneshot/i18n_supplement.json` | **~3992 girdilik ana TR→EN sözlük.** Modül modül büyüdü. Yeni çeviri buraya eklenir. |
| `scripts/_arsiv/fix_oneshot/*_tr_en.json` | Modül bazlı çeviri parçaları (admin/raporlar/sp/js/message/pylabel/faz3b/jsdyn) — hepsi supplement'e merge edildi. |

---

## 4. KRİTİK KURALLAR / TUZAKLAR (tekrar düşmemek için)

1. **`%` escape (Jinja `_()`):** Flask-Babel `_()` çıktısına DAİMA `%`-format uygular. Argümansız tek `%`
   → **ValueError runtime crash**. Şablon `_()` içinde literal `%` MUTLAKA `%%` yazılır. Named arg: `%(x)s`.
   - **AMA JS `t()` için değil:** JS `t()` %-format uygulamaz; JS'de tek `%` AYNEN kalır, çiftlenmez.
   - supplement değerlerinde de `%%` sayısı KEY ile eşit olmalı (KEY `%%` → VALUE `%%`).

2. **JS `t` shadow:** `.map((t,..)=>)`, `function(t)` gibi bir yerel `t` binding'i, İÇİNDE `t("...")` çeviri
   çağrısı varsa onu gölgeler → runtime crash ("t is not a function"). Çözüm: parametreyi `it`/`task` yap.

3. **babel `${t(...)}` boşluğu:** babel `[javascript]` extractor template-literal içindeki `t()` çağrılarını
   KAÇIRIR. `extract_inline_t.py` bunu telafi eder. **Yeni JS yazınca extract'ı bu script ile çalıştır.**

4. **Python import sırası:** `from flask_babel import gettext as _` eklerken — `from __future__ import`
   satırından SONRA ve çok-satır import parantezi DIŞINA koy (yoksa SyntaxError).

5. **DB-key / enum / karşılaştırma DOKUNULMAZ:** `if x == "Tamamlandı"`, sözlük anahtarları, durum kodları,
   DB'ye seed edilen değerler, dosya adları, log mesajları, LLM prompt'ları → ÇEVRİLMEZ (mantık bozulur).

6. **fuzzy auto-match riski:** babel benzer string'leri yanlış eşler (örn "Hoş geldiniz"→"Holding").
   `unfuzzy` adımı bunu onaylayabilir. Kısa msgid'lerde gözle kontrol şart. (Bir vaka bulunup düzeltildi.)

7. **PowerShell/konsol UTF-8 bozuk:** Türkçe karakterler konsola bozuk basılır. Doğrulama için UTF-8
   dosyaya yazıp Read et, VEYA `force_locale` render + dosya çıktısı kullan. Konsol çıktısına güvenme.

8. **Doğrulama komutları:**
   - Katalog: `babel.messages.pofile.read_po` → empty/fuzzy/%%-mismatch say
   - Şablon: Jinja `Environment.parse`
   - JS: `node --check`
   - Python: `py_compile` + `create_app()` (import-time lazy patlamasını yakalar)
   - Gerçek doğrulama: Flask `test_client` + `force_locale('en')` + TR-kelime oranı ölç

---

## 5. TERMİNOLOJİ (tutarlı — UI-TERMINOLOJI.md'ye bağlı)

- PG → **PI** (Performance Indicator). Ama URL'de `pi`, kod/DB'de `pg` kalır. KPI → KPI.
- Kurum → **Organization**, Alt Kurum → **Sub-Organization**, Kullanıcı → **User**, Bayi → **Reseller**, Holding → Holding.
- Strateji → Strategy, Alt Strateji → Sub-Strategy, Süreç → Process, Faaliyet → Activity,
  Girişim → Initiative, Proje → Project, Karne → Scorecard, Dönem → Period.
- K-Vektör → **K-Vector**. KS/KP/KPR, SWOT/TOWS/PESTEL/VRIO/BSC/OKR/EVM/RPN/CMMI/ESG → AYNEN korunur.
- Marka: Kokpitim, Tomofil, YeniTomofil, tomofiltest → AYNEN.
- Ortam: Yerel → Local, Yayın → Production.
- Dil adları kendi dilinde: "Türkçe" her dilde "Türkçe" (çevrilmez — dil seçicide doğru).

---

## 6. YAPILAN FAZLAR (git commit karşılığı)

- **URL tek-dil (TASK-199..213):** Tüm Türkçe URL'ler İngilizce'ye (301 köprülü). PG→PI (URL'de).
- **FAZ 0 (TASK-214):** i18n altyapısı canlıya bağlandı — Flask-Babel paketi, dil seçici, /set-language.
- **FAZ 1:** base.html ortak iskelet + translations yolu bugfix.
- **FAZ 3 (a-j):** Şablon çevirisi modül modül — masaustu, surec, bireysel, bildirim, analiz, ayarlar,
  kurum, k_rapor, k_radar, admin, raporlar, sp. (~2500+ metin, 6'ya kadar paralel ajan.)
- **FAZ 4 (TASK-224):** JS stringleri — 86 dosya + `window.t()` mekanizması kuruldu.
- **FAZ 4b (TASK-225):** Şablon-içi `<script>` Swal/toast (43 şablon).
- **FAZ 5:** flash() mesajları (11 dosya, 97 çağrı).
- **FAZ 5b:** API JSON `"message"` yanıtları (60 dosya, 537 mesaj).
- **FAZ 5c (TASK-226):** Python UI label/sabit + rapor içerikleri + **lazy_gettext** düzeltmeleri.
- **FAZ 3-tamamlama (TASK-227):** Gözle-doğrulama 27 atlanan şablonu ortaya çıkardı (project/auth/
  calendar/demo/errors/launcher) → çevrildi.
- **JS FIX (87c59dd):** babel `${t(...)}` boşluğu — 447 JS dinamik string katalога eklendi
  (dashboard "Kritik KPI"/"Geciken Proje" tarayıcıda Türkçe kalıyordu).

**Tümü main'e merge (`d42f58e`) + origin'e push edildi. Dal silindi.**

---

## 7. AÇIK / KALAN İŞLER

### 7.1 Deploy (kullanıcı kararı bekliyor)
- Kod **origin/main**'de ama **Test/Demo/Yayın VM'lerine deploy EDİLMEDİ**. Kullanıcı "yayına ve teste
  vermeyelim" dedi. Deploy akışı: `docs/KURALLAR-MASTER.md §8.3`. **Kullanıcı "yayına çıkalım" demeden deploy YOK.**
- Deploy olunca VM'de `.mo` dosyalarının derlenmesi gerekir (`pybabel compile -d translations`) veya
  derlenmiş `.mo`'lar commit'te (şu an commit'teler).

### 7.2 Bilinçli kapsam-dışı (çevrilmemeli — bunlar İŞ DEĞİL)
- Kullanıcı/tenant VERİSİ: girilen strateji adları, kişi adları, tenant adı (örn "Sürdürülebilirlik",
  "Ayşe Yılmaz"). Bunlar EN'de de Türkçe görünür — DOĞRU, çevrilemez.
- DB-seed JSON (`app/templates_data/*.json` — sektörel plan şablonları), `.pyc`, enum/durum kodları.

### 7.3 Olası kalan kaçaklar (yeni sohbette kontrol edilebilir)
- Gözle-doğrulama her turda birkaç kaçak buldu. TAM emin olmak için: uygulamayı `?lang=en` ile gez,
  Türkçe gördüğün yeri not al. Kaçak tipleri: (a) FAZ kapsamına girmemiş yeni şablon, (b) `${t()}` yeni
  JS, (c) modül-seviyesi statik gettext (lazy olmalı). Yöntem §4.8'deki test_client + TR-kelime oranı.
- **Yeni UI eklenirse:** şablonda `{{ _() }}`, JS'de `t()` kullan; sonra `bash scripts/i18n_extract.sh`
  → `i18n_fill_surec.py` (çeviriyi supplement.json'a ekle) → `compile`.

### 7.4 TR katalog
- `translations/tr/` de var ama TR default dil olduğu için msgstr'lar çoğunlukla boş (fallback msgid = Türkçe).
  Bu normal; TR için ayrı çeviri gerekmez.

---

## 8. HIZLI BAŞLANGIÇ (yeni sohbet için)

```bash
# Durum kontrolü
git branch --show-current                    # main olmalı
git log --oneline -3                          # 87c59dd i18n FIX... en üstte

# Katalog sağlığı
.venv/Scripts/python.exe -c "from babel.messages.pofile import read_po; c=read_po(open('translations/en/LC_MESSAGES/messages.po',encoding='utf-8')); print('empty',len([m for m in c if m.id and not m.string]),'fuzzy',len([m for m in c if m.id and m.fuzzy]))"
# → empty 0 fuzzy 0 olmalı

# EN render testi (herhangi bir string)
.venv/Scripts/python.exe -c "import sys;sys.path.insert(0,'.');from app import create_app;from flask_babel import force_locale,gettext;app=create_app()
with app.test_request_context('/'):
    with force_locale('en'): print(gettext('Kurum Yönetimi'))"   # → Organization Management

# Yerel çalıştırma (stale süreç tuzağına dikkat — memory'de kayıtlı)
python pybasla.py    # 5001'de temiz başlatır; sonra 127.0.0.1:5001/desktop?lang=en
```

**Not:** `.js`/`.mo`/base.html değişince uygulamayı yeniden başlat + tarayıcı hard-refresh (Ctrl+F5).
Bu makinede auto-reload güvenilmez (memory'de kayıtlı).
