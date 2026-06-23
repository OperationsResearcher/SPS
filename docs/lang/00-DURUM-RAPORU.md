# KOKPİTİM — Çoklu Dil (i18n) Durum Raporu

> Tarih: 2026-06-23 · Hazırlayan: Claude (keşif + analiz)
> Bu belge **mevcut durumun envanteri**. Plan ve fazlar: [`02-FAZ-PLANI.md`](02-FAZ-PLANI.md).

---

## TL;DR

Çoklu dil **altyapısı tasarlanmış ama hiçbir zaman canlıya bağlanmamış.** İskelet Mayıs 2026'da
(Sprint 28/31) kondu, sonra terk edildi. Bugün:

- ✅ Locale-seçim mantığı yazılı ve sağlam (`app/i18n.py`)
- ✅ Çeviri kataloğu iskeleti var (`translations/{tr,en}/` — **sadece 33 string**)
- ✅ DB'de `User.locale_preferences` alanı hazır
- ❌ **Flask-Babel paketi KURULU DEĞİL** → `init_babel()` her başlangıçta `ImportError` yiyip sessizce atlıyor (restart loglarındaki `[i18n] Flask-Babel kurulu değil — i18n atlandı` uyarısı bu)
- ❌ **`requirements`'ta Babel yok**
- ❌ **Template'lerde `{{ _() }}` kullanımı = 0 dosya** (hiçbir metin çeviriye işaretlenmemiş)
- ❌ **Dil seçici UI yok**, `/set-language` route yok
- ❌ JS'lerde ~850 hardcoded Türkçe string
- ❌ flash() mesajları (~74+) ham Türkçe

**Tek cümleyle:** Çatı kurulu, elektrik bağlı değil, duvarlar boş. Asıl iş = **~2.500 string'i işaretleyip çevirmek** + paketi kurup kabloyu bağlamak + dil seçici eklemek.

---

## 1. Ne VAR (kullanılabilir miras)

| Bileşen | Dosya | Durum |
|---------|-------|-------|
| Locale seçim zinciri | `app/i18n.py` (`get_locale`) | ✅ Sağlam: ?lang → session → user prefs → Accept-Language → default(tr) |
| Babel init iskeleti | `app/i18n.py` (`init_babel`) | ⚠️ Yazılı ama ImportError'da atlıyor |
| create_app bağlantısı | `app/__init__.py:435-436` | ✅ `init_babel(app)` çağrılıyor |
| Babel ekstraksiyon config | `babel.cfg` | ✅ `**/templates/**.html` + `**.py` tarar (NOT: `ui/templates` kapsıyor mu, kontrol edilmeli) |
| Çeviri kataloğu | `translations/{tr,en}/LC_MESSAGES/messages.{po,mo}` | ⚠️ Sadece 33 temel string (Hoş geldiniz, Giriş, Kaydet...) |
| User dil tercihi | `app/models/core.py:136` `locale_preferences` (Text/JSON) | ✅ Şema hazır, doldurulmuyor |

## 2. Ne YOK (yapılacak iş)

| Eksik | Etki | Büyüklük |
|-------|------|----------|
| **Flask-Babel paketi** | i18n hiç çalışmıyor | 1 satır requirements + pip install |
| **Template metin işaretleme** `{{ _() }}` | 164 modern template hiç çeviriye hazır değil | ~1.680 string — EN BÜYÜK İŞ |
| **JS metin işaretleme** | 84 JS dosyası, SweetAlert/toast/buton | ~850 string |
| **flash() sarmalama** `_()` | Python route mesajları | ~74+ çağrı |
| **Dil seçici UI** | Kullanıcı dili değiştiremiyor | base.html topbar + 1 route |
| **`/set-language` route** | session/user prefs yazımı | ~15 satır |
| **`babel.cfg` ui/ kapsamı** | `ui/templates/` taranıyor mu? | config doğrulaması |
| **`<html lang="tr">` dinamikleştirme** | hardcoded | 1 satır/template |

## 3. KRİTİK MİMARİ AYRIM — UI dili vs İçerik dili

Bu sistemin en önemli i18n kararı. İki ayrı katman var, KARIŞTIRILMAMALI:

### A. UI metinleri (ÇEVRİLİR — i18n kapsamı)
Sistem/uygulama metinleri: buton etiketleri, menü, başlıklar, flash mesajları, sabit açıklamalar,
SweetAlert metinleri. **Bunlar `_()` ile işaretlenir, .po'ya çevrilir.**

### B. Kullanıcı içeriği (ÇEVRİLMEZ — kullanıcı ne girdiyse o)
Strateji adları, süreç adları, KPI adları, proje adları, kullanıcı açıklamaları. Kullanıcı hangi dilde
girdiyse öyle kalır. `/set-language` **UI dilini** değiştirir, içeriği DEĞİL. ✅ Doğru yaklaşım budur.

### C. Sistem-üretimi sabit veri (GRİ ALAN — karar gerekli)
DB'de seed ile gelen Türkçe sabitler:
- **Modül/paket adları** (`system_modules.name="Kurum Paneli"`, `seed_l2_paketler.py`)
- **Rol görünen adları** (`Kurum Yöneticisi` — kod İngilizce `tenant_admin` ama label TR)
- **Status enum'ları** (`status="Planlandı"`, `"Aktif"` — `app/models/project.py:26`, `process.py:77`)
- **Tomofil demo verisi** (tamamen Türkçe — bu DEMO örneği, sorun değil)

**Öneri:** Modül/paket/rol/status gibi **sınırlı, sabit kümeler** için `_()` + sabit-anahtar yaklaşımı
(kod sabit, görünen ad çevrilir). Tomofil demo içeriği Türkçe kalır. Detay: `01-ANALIZ.md §3`.

## 4. Geçmiş deneme (neden yarım kaldı)

- **Sprint 28** (~2026 başı): `app/i18n.py` Babel iskeleti yazıldı, create_app'e bağlandı.
- **Sprint 31** (2026-05-23): `translations/{tr,en}` + 33 temel string + `messages.mo` derlendi.
- Sonra **terk edildi** — muhtemelen şu yüzden: (a) flask-babel kurulmadı/kaldırıldı, (b) ~2.500 string'i
  elle işaretlemek büyük iş, (c) öncelik başka yöne (kart sistemi, URL tek-dil) kaydı.
- TASKLOG'da i18n için **özel TASK kaydı yok** — yani hiç "bitirildi" denmedi, askıda.

## 5. Şu anki davranış

Uygulama **tek dil (Türkçe)** çalışıyor. `init_babel` ImportError'da sessizce dönüyor, `_()` çağrısı
olmadığı için hiçbir şey kırılmıyor. Yani **i18n'i açmak mevcut işleyişi bozmaz** — sıfırdan, güvenli
inşa edilebilir. Bu iyi haber: yarım iş bir engel değil, sağlam bir temel.
