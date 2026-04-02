# Kokpitim Tek Yapı Birleştirme Checklist

Bu dokuman, `/kok` (legacy) ve `micro` ayrimini tamamen kaldirip tek bir Kokpitim yapisina gecis icin uygulanacak adimlari ve kontrol noktalarini tanimlar.

## Hedef

- Sistemde `/kok` URL on eki kalmamasi
- Kod tabaninda `micro` adlandirmasinin (blueprint/module/template/static yol adi olarak) kalmamasi
- Tek route hatti, tek template/static organizasyonu ve tek giris akisi

## Yedek Politikasi (Tamamlandi)

- Git gecmisi yedegi: `Yedekler/Kokpitim_git_20260325_213031.bundle`
- Calisma agaci snapshot: `Yedekler/Kokpitim_Tam_Set_Snapshot_20260325_213519/`

Not: Canliya gecis bu checklist tamamlanmadan yapilmaz.

## Faz 0 - Envanter ve Donma

- [ ] `/kok` referanslarini dosya bazinda cikar
- [ ] `micro` import/route/template/static referanslarini cikar
- [ ] Eski davranis gerektiren URL'ler icin gecis matrisi hazirla
- [ ] Dokumantasyonlarda "legacy/micro" dilini "tek yapi" diline tasima listesi cikar

## Faz 1 - URL ve Auth Birlesimi

- [ ] `LEGACY_URL_PREFIX` bagimliligini kaldir
- [ ] `app/__init__.py` icindeki legacy blueprint kayitlarini kok path'e tasi
- [ ] `/isr` ve `/micro` uyumluluk yonlendirmelerini kaldir
- [ ] `login_view` ve auth endpointlerini tek hattan calistir
- [ ] Swagger/API pathlerini tek URL semasina cek

## Faz 2 - Blueprint / Namespace Birlesimi

- [ ] `micro_bp` ismini platform-nötr bir blueprint ismine tasi
- [ ] `from micro...` importlarini yeni kok package yapisina guncelle
- [ ] `url_for('micro_bp....')` cagrilarini yeni endpoint isimlerine cek
- [ ] Moduller arasi import dongulerini test et

## Faz 3 - Dosya Yapisini Birlestirme

- [ ] `ui/templates/platform/...` icerigini hedef template yapisina tasi
- [ ] `ui/static/platform/...` icerigini hedef static yapisina tasi
- [ ] Template include/extents pathlerini yeni yapida duzelt
- [ ] `static_url_path="m"` bagimliligini kaldir
- [ ] Cakisan dosya adlarini konsolide et

## Faz 4 - Kod Temizligi

- [ ] Artik kullanilmayan `micro` klasorlerini kaldir
- [ ] Legacy `/kok` yorumlari, config alanlari, fallback kodlari temizle
- [ ] Eski redirect/alias endpointlerini sil
- [ ] Gecis sirasinda eklenen gecici notlari temizle

## Faz 5 - Test ve Dogrulama

- [ ] Temel auth akisi: `/login`, `/logout`
- [ ] Ana sayfa ve launcher akisi
- [ ] Surec/KPI/faaliyet ekranlari
- [ ] Proje/gorev ekranlari
- [ ] Bildirim merkezi + unread API
- [ ] Analiz merkezi + ilgili API'ler
- [ ] Ayarlar/eposta ve SMTP test akisi
- [ ] Lint/diagnostic temizligi

## Faz 6 - Canliya Gecis Oncesi Kriterler

- [ ] `rg "/kok|legacy_url_prefix"` sonucu kod dosyalarinda 0
- [ ] `rg "from micro|import micro|micro_bp|url_for\\('micro_bp"` sonucu kod dosyalarinda 0
- [ ] Smoke test senaryolari tam gecti
- [ ] Rollback adimlari yazili ve test edildi

## Faz 7 - VM Gecis Protokolu (Son Asama)

- [ ] Yerel son yedek
- [ ] VM tam yedek
- [ ] Guvenli deploy scripti ile gecis
- [ ] Health + kritik URL testleri
- [ ] Gerekirse rollback

---

## Notlar

- Bu gecis buyuk bir mimari refactor oldugu icin fazli ilerlenir.
- Her faz sonu commit alinip test raporu cikarilir.
- Fazlar tamamlanmadan canliya alinmaz.
