# KOKPİTİM — Çoklu Dil (i18n) Faz Planı

> Durum: [`00-DURUM-RAPORU.md`](00-DURUM-RAPORU.md) · Analiz: [`01-ANALIZ.md`](01-ANALIZ.md)
> İlke: **küçük dilimler, her dilim test edilir ve çalışır halde biter** (yarım kalmasın). URL tek-dil
> çalışmasındaki gibi: oku → işaretle → derle → test → commit.

---

## Strateji: neden fazlı + dikey dilim

Geçen sefer yarım kaldı çünkü "tüm projeyi birden" hedeflendi. Bu sefer **dikey dilimler**: her faz
SONUNDA dil değiştirme **gerçekten çalışır** (o ana kadar işaretlenmiş yüzeyde). Kullanıcı erken değer görür,
iş hiç "hep ya da hiç" olmaz. base.html + dil seçici ilk fazda → ilk günden dil değişimi gözle görülür.

---

## FAZ 0 — Altyapıyı canlıya bağla (yarım günlük, RİSKSİZ)
**Hedef:** Babel gerçekten çalışsın, dil değişimi mekanik olarak mümkün olsun (henüz metin çevrilmemiş olsa da).

- [ ] `Flask-Babel` → `requirements-ai.txt` veya ana requirements'a ekle, kur
- [ ] `babel.cfg`'yi doğrula: `ui/templates/**.html` ve `ui/static/**/*.js` kapsıyor mu? (şu an `**/templates/**.html`)
- [ ] `init_babel` çalıştığını doğrula (restart'ta artık "kurulu değil" uyarısı OLMAMALI, "Babel başlatıldı" gelmeli)
- [ ] `/set-language/<lang>` route ekle (session['lang'] + user.locale_preferences yaz, referer'a dön)
- [ ] base.html topbar'a dil seçici (TR/EN) — `url_for('...set_language', lang='en')`
- [ ] `<html lang="{{ get_locale() }}">` dinamikleştir (tüm base'ler: `ui/.../base.html` + `templates/base.html`)
- **Test:** `?lang=en` ve dil seçici → session değişiyor, sayfa kırılmıyor, `get_locale()` doğru dönüyor.
- **Çıktı:** Dil altyapısı CANLI. Henüz çeviri yok ama anahtar dönüyor. **Commit.**

## FAZ 1 — base.html + ortak iskelet (yüksek değer, görünür)
**Hedef:** Her sayfada görünen ortak metinler çevrili. İlk gözle görülür çok-dillilik.

- [ ] base.html: sidebar menü, topbar, breadcrumb, user dropdown, dark-mode, demo banner → `{{ _() }}`
- [ ] Ortak makrolar / `_banner.html` / hata sayfaları (403/404/500)
- [ ] `pybabel extract -F babel.cfg -o messages.pot .` → `pybabel update -d translations`
- [ ] EN çevirileri doldur (UI-TERMINOLOJI.md EN kolonu referans)
- [ ] `pybabel compile -d translations`
- **Test:** Dil EN → menü/topbar İngilizce, sayfa içeriği TR (henüz). Geçiş akıcı.
- **Çıktı:** İskelet iki dilli. **Commit.**

## FAZ 2 — UI-TERMINOLOJI.md'ye EN kolonu + domain sözlüğü
**Hedef:** Çeviri tutarlılığının tek kaynağı. (Faz 1 ile paralel yürüyebilir.)

- [ ] `docs/UI-TERMINOLOJI.md`'ye İngilizce kolonu ekle (Kurum→Organization, Süreç→Process, PG→PI...)
- [ ] Domain terimleri sabitle: K-Vektör, EVM, OKR, SWOT, CMMI (çevrilmez/kısaltma)
- **Çıktı:** Çevirmen (insan/AI) için referans. **Commit.**

## FAZ 3 — Modül modül template çevirisi (ASIL İŞ, dikey dilimler)
**Hedef:** Her modül kendi içinde tam çevrili. Sırayla, her biri ayrı commit + test.
Öncelik = görünürlük × yoğunluk:

- [ ] 3a. `masaustu/` (desktop — ana sayfa, herkes görür)
- [ ] 3b. `surec/` + `surec.js` (en yoğun JS)
- [ ] 3c. `bireysel/` (her kullanıcının karnesi)
- [ ] 3d. `sp/` (en yoğun template — parçalara böl: pages, analysis, frameworks, plan-year)
- [ ] 3e. `raporlar/` (45 dosya — fazlara böl)
- [ ] 3f. `k_radar/` + `k_rapor/`
- [ ] 3g. `kurum/` (organization), `ayarlar/`, `bildirim/`, `analiz/`
- [ ] 3h. `admin/` (yönetici — düşük öncelik, son)
- **Her dilim:** `_()` işaretle → extract/update → EN doldur → compile → restart → o sayfayı EN'de gör → commit.

## FAZ 4 — JS metinleri
**Hedef:** SweetAlert/toast/buton metinleri çevrili.
- [ ] Backend-mesaj yaklaşımı (A): fetch yanıtlarındaki `message` zaten sunucudan → `flash`/`jsonify(_())`
- [ ] İstemci-saf metinler (C): base.html'de `window.I18N = {...}` aktif dil sözlüğü, JS `t("key")`
- [ ] En yoğun JS önce: surec.js, k_radar_ks.js, k_rapor.js, tool_info_modal.js, admin.js
- **Test:** EN dilde modal/toast İngilizce. **Commit (dilim dilim).**

## FAZ 5 — flash() mesajları + sistem sabit veri
- [ ] Python route'larında `flash("...")` → `flash(_("..."))` (~74 çağrı)
- [ ] Modül/paket/rol/status gösterimini `_()` ile çevir (DB değeri sabit kalır)
- **Commit.**

## FAZ 6 — Tarih/sayı/para formatı (cilalama)
- [ ] Template'lerde tarih → `{{ x | format_date(locale=get_locale()) }}`
- [ ] Para/sayı → `format_currency`/`format_number`
- **Commit.**

## FAZ 7 — Tamamlama + kalite
- [ ] Çeviri doluluk kontrolü (boş msgstr taraması — CI/script)
- [ ] Eksik kalanları tara (`pybabel extract` + diff)
- [ ] KURALLAR-MASTER'a i18n bölümü (yeni metin yazarken `_()` zorunlu)
- [ ] Legacy `templates/` kararı: çevir mi, eritilsin mi (strangler)
- **Commit + TASKLOG.**

---

## Tahmini boyut (kaba)

| Faz | İş | Büyüklük |
|-----|----|----------|
| 0 | Altyapı + dil seçici | ½ gün |
| 1 | base.html iskelet | ½ gün |
| 2 | Terminoloji sözlüğü | ¼ gün |
| 3 | Modül template (asıl iş) | 3–5 gün (dilimlere yayılır) |
| 4 | JS metinleri | 1–2 gün |
| 5 | flash + sabit veri | ½ gün |
| 6 | Format | ¼ gün |
| 7 | Kalite | ¼ gün |
| **Toplam** | | **~6–9 iş günü** (dilimlere yayılı, her dilim commit'li) |

## Çalışma disiplini (her dilimde)
1. Oku (hangi metinler görünür, hangileri içerik/sabit)
2. `_()` işaretle (yalnız UI metni; içerik değişkenlerine DOKUNMA)
3. `pybabel extract → update → EN doldur → compile`
4. `python pybasla.py` restart → o sayfayı TR ve EN'de aç, gör
5. Smoke test (sayfa 200/302 dönüyor mu, kırılma yok)
6. Commit (tek dilim) + gerekirse push
7. TASKLOG'a kısa kayıt

## İlk somut adım
**FAZ 0** — riskli değil, yarım günde dil altyapısı canlı olur ve dil değişimi mekanik çalışır.
Kullanıcı onayıyla başlanır. Mevcut işleyişi bozmaz (i18n şu an zaten kapalı, açmak ek özellik).
