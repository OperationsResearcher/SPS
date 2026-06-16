# Ertelenen İşler — Kokpitim

> **Amaç:** Şu an aktif geliştirilmeyen ama tamamlanmamış işleri kayıt altında tutmak.
> "Unutulmasın diye yazılmış", "şimdi değil ama dönülecek" listesi.
> En önemli ertelenenler en üstte.

---

## E1 — Kule Yardımcı Sistemi

**Erteleme tarihi:** 2026-05-26
**Branch:** `claude/kule-yardimci-sistemi` (silinmedi, korunuyor)
**Tanım dosyası:** `docs/KULE-TANIM.md` (tek referans)

### Neden ertelendi
Sihirbaz/tur sistemi UI değişikliklerine sıkı bağımlı. UI hala yoğun geliştirme altında olduğu için her UI değişikliğinde Kule'yi de güncellemek ve test etmek zaman alıyor. Önce çekirdek proje sayfaları stabil hale gelsin, sonra Kule yeniden devreye girer.

### Şu an itibarıyla durum
- ✅ Tanım dosyası yazıldı (`docs/KULE-TANIM.md`)
- ✅ DB tablosu + migration uygulandı (`user_tour_progress`)
- ✅ Backend servisi + 5 API endpoint (`/api/kule/tour/...`)
- ✅ Kule SVG karakter (hava trafik kulesi, dönen anten, durum ışığı)
- ✅ CSS + JS runtime (Driver.js + hafif markdown desteği)
- ✅ 17 tur içeriği (`docs/tours/*.yaml`)
- ✅ 13 sayfa template'ine `data-tour` ve meta etiketleri eklendi
- ⏸ **Base template'te yükleme kapatıldı** (geçici) — kullanıcıya görünmüyor

### Devam etmek için
1. `ui/templates/platform/base.html` içindeki Kule yükleme bloğunu yeniden aç (comment çıkar)
2. Yeni eklenen UI sayfalarına `<meta name="kule-tour-key">` ve `data-tour` attribute'larını ekle
3. Yeni tur içerikleri için `docs/tours/<key>.yaml` oluştur
4. Faz 2 — AI köprüsü: kullanıcı sorduğunda sayfa bağlamı + soru → LLM → cevap

### Bilinen eksikler
- Yardımcı modüller (Cross A3, KP Benchmark, KP Darboğaz vs.) için tur YAML'i yok
- Holding/Bayi modülleri (`admin_sub_tenants`, `holding_dashboard`) için tur yok
- Mobil davranış test edilmedi
- Çoklu dil hazırlığı yok (şu an Türkçe-only)

### Verili dosyaların listesi (korunuyor)
```
docs/KULE-TANIM.md
docs/ERTELENEN-ISLER.md  (bu dosya)
docs/tours/*.yaml  (17 dosya)
app/models/tour.py
app/services/kule_service.py
micro/modules/shared/kule/
ui/static/platform/img/kule.svg
ui/static/platform/css/kule.css
ui/static/platform/js/kule.js
migrations/versions/i2j3k4l5m016_user_tour_progress.py
```

Devam ettiğimizde branch'i `git checkout claude/kule-yardimci-sistemi` ile aç, üstüne devam et.

---
