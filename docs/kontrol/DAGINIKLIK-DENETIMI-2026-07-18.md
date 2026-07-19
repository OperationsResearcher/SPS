# Dağınıklık Denetimi — Katman Taşıması Sonrası

> Kullanıcı: "konu çok dağılmış, toparlayamadım. Bileşenleri, URL'leri, sidebar akışını
> her şeyi çok detaylı kontrol et." → 3 paralel ajan + doğrudan ölçüm.
> Tarih: 2026-07-18 · Yöntem: URL/sidebar/kart üç boyut, kod+DB ölçümü (tahmin değil)

---

## ÖNCE İYİ HABER — teknik kırıklık YOK

- **0 kırık endpoint** (BuildError riski yok) — 21 sidebar linki + tüm template `url_for`'ları geçerli.
- **0 hardcoded eski URL** kalıntısı (Faz 6'da temizlenmiş).
- **Kart sistemi tutarlı** — 501 kart, yalnız 12'si (%2.4) açıklamasız; taşımayla ilgisiz.
  Sebep: kart kimliği URL'den değil SAYFA'dan türer (`data-card-code`), taşıma URL'i
  değiştirdi ama dosya ağacına dokunmadı → kart keşfi etkilenmedi.
- Sidebar gating tutarlı — modül `id`'leri taşımada değişmedi (yalnız `url` değişti).

**Yani "dağınıklık" teknik bir bozukluk değil — YAPISAL TUTARSIZLIK.** Sayfalar çalışıyor
ama düzen kullanıcıya dağınık görünüyor. Bu his HAKLI; kaynakları aşağıda.

---

## DAĞINIKLIĞIN 5 ÖLÇÜLMÜŞ KAYNAĞI (önem sırasıyla)

### 1. 🔴 Sidebar katman mimarisini YANSITMIYOR — asıl kök neden
Sidebar 4 bölüme ayrılmış (Ana Modüller / Yönetim / Admin / Sistem) ama bunlar
**işlev/rol bazlı, katman bazlı değil.** "Ana Modüller" 13 girişi katmanları iç içe
karıştırıyor:
```
Masaüstüm → Yönetim Özeti(rapor) → SP(girdi) → Kurum(girdi) → Holding(rapor)
→ Süreç(girdi) → Proje(girdi) → K-Radar(teşhis) → K-Radar Araçları(teşhis)
→ Savaş Odası(girdi) → Bireysel(girdi) → Performans Analitiği(teşhis)
```
Mimarideki girdi/teşhis/rapor katmanlaması **menüye hiç yansımamış.** Kullanıcı
3 katmanı ayırt edemiyor. `base.html:126-307`.

### 2. 🔴 Çift K-Radar girişi — ayırt edilemez
`base.html:208,216` — peş peşe iki giriş:
- **"K-Radar"** → `k_radar_hub` (`/k-radar`)
- **"K-Radar Araçları"** → `k_radar_ks` (`/k-radar/ks`)
Aynı katman, aynı gating, benzer ikon. Kullanıcı farkı menüden anlayamaz.
(Önceki "K-Analiz" ikinci adı temizlenmiş ama yerine bu ikili gelmiş.)

### 3. 🔴 Rapor katmanı sidebar'da YOK — birinci sınıf değil
`/k-report` menüde hiç link almıyor. Tek erişim: K-Radar hub'ındaki kartlar.
Dahası `base.html:209` sidebar `active` koşulu rapor sayfasındayken **"K-Radar"**
highlight ediyor → kullanıcı `/k-report`'tayken menü "K-Radar" gösteriyor. Tutarsız.
Üç katmandan biri (rapor) menüde görünmezse mimari yarım kalır.

### 4. 🟠 `/analysis` modülü TAŞINMAMIŞ — tek yarım-taşıma
7 route hâlâ `/analysis` önekinde, katman mimarisine hiç girmemiş
(`analiz/routes.py:13-207`). Diğer 39 eski-önek route düzgün 307 redirect;
`analiz`'in redirect/legacy dosyası bile YOK. "Performans Analitiği" sidebar'da
ayrı giriş, ama teşhis işi yapıyor — K-Radar Araçları ile örtüşüyor, sınır belirsiz.
**Karar gerekir:** ya `/k-radar/analysis`'e taşı (teşhis katmanı), ya katman-dışı
olduğunu belgele.

### 5. 🟠 `module_registry` yarı-taşınmış + çift `/k-report`
`micro/core/module_registry.py`:
- `k_rapor` (satır 73) ve `raporlar` (satır 81) **iki ayrı modül, ikisi de `url=/k-report`.**
  Faz 4'te URL'de birleştiler ama registry'de ayrı kaldılar → launcher'da iki kutu
  aynı yere gidebilir. `raporlar` erime kalıntısı.
- `kurum` (`/organization`) ve `analiz` (`/analysis`) katman-dışı ve **yorumsuz**
  (sp/surec/k_rapor'da açıklayıcı "Faz" yorumu var, bunlarda yok → bilinçsiz kalıntı işareti).

### (yan) 🟡 Gating iki mekanizma karışık
Rol bazlı (`role_name`) + paket bazlı (`sidebar_module_ids`) iç içe. #2 Yönetim Özeti
sadece rol (paket kontrolü yok), #13 Performans Analitiği çift koşul. Küçük tutarsızlık.

---

## TOPARLAMA PLANI — düşük riskli, hepsi sunum/navigasyon

Not: Hiçbiri kod mantığına dokunmaz; URL taşıması gibi büyük iş DEĞİL. Çoğu sidebar +
registry düzenlemesi. Aşama aşama, her biri Test'te doğrulanır.

| # | İş | Dokunulan | Risk | Etki |
|---|---|---|---|---|
| T1 | **Sidebar'ı katmana göre grupla** — "Girdi / Teşhis / Rapor" bölüm etiketleri | base.html | Düşük | En yüksek — kök neden |
| T2 | **Çift K-Radar'ı tekle** — "K-Radar Araçları"nı hub içine al ya da alt-menü yap | base.html | Düşük | Yüksek |
| T3 | **Rapor katmanını sidebar'a ekle** — "Raporlar" girişi `/k-report`; active koşulunu düzelt | base.html | Düşük | Yüksek |
| T4 | **`/analysis` kararı** — `/k-radar/analysis`'e taşı + legacy redirect, VEYA belgele | analiz modülü | Orta | Orta |
| T5 | **registry temizliği** — `raporlar`+`k_rapor` tek modül; `kurum`/`analiz`'e Faz yorumu | module_registry.py | Düşük | Orta |
| T6 | **Gating'i tektipleştir** — #2/#13'ü diğerleriyle aynı kalıba getir | base.html | Düşük | Düşük |

**Öncelik:** T1+T2+T3 birlikte — üçü de sidebar, "menü katmanı yansıtmıyor" sorununu
tek hamlede çözer, en yüksek "toparlanma" etkisi. T4/T5 ayrı tur.

## Yapılmaması gereken
- **Kart sistemine dokunma** — tutarlı, taşımadan etkilenmemiş.
- **URL'leri yeniden değiştirme** — çalışıyor, redirect'ler yerinde. Sorun URL değil, SUNUM.
- **Büyük refactor** — dağınıklık navigasyon katmanında, mimaride değil.
