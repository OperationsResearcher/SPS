# DEVİR BELGESİ — SaaS Paket Hiyerarşisi + Gating (2026-06-21)

> Yeni sohbete devam için. Önceki oturum session limitine takıldı.
> **Bağlayıcı kurallar:** CLAUDE.md + docs/KURALLAR-MASTER.md. Yerel→Test→Yayın.
> **Tüm L paketleri bitmeden Yayın'a ÇIKMA YOK** (memory: project_l_paketleri_deploy_kurali).
> Hiçbir şey push/deploy edilmedi — her şey YEREL (127.0.0.1:5001, PostgreSQL).

---

## NEREDEYİZ — Tek cümle
L1/L2/L3 paketleri inşa edildi ve main'de. Şu an **4-katman SaaS hiyerarşisi + paket gating** üzerinde çalışıyoruz. Aktif iş: **KART katmanı** (`claude/kart-katmani` dalı, main'e MERGE EDİLMEDİ, 5 commit).

## AKTİF DAL DURUMU
- **Branch:** `claude/kart-katmani` (main'den 5 commit ileride, merge bekliyor)
- **Migration head:** `c3d4e5f6a7b8` (kart_katmani — system_cards + card_data_sources)
- Dal commit'leri:
  1. `0acf8e6` KART model temeli (SystemCard + CardDataSource + migration)
  2. `5ba333b` card_data_visible helper + kart-içi veri gating kanıtı
  3. `17a9cd0` Otomatik kart keşfi + 4-katman admin hiyerarşi UI
  4. `ce0ccd9` KART/veri düzenleme (gör/taşı/düzenle tamam)
  5. `8368b45` modül-bileşen eşlemesi onarımı

---

## 4-KATMAN MİMARİSİ (kullanıcının kurduğu, çekirdek)
```
PAKET     subscription_packages   (baslangic/yonetim/strateji + master)  [4]
  └ MODÜL   system_modules         (surec, kurum, sp, k_radar...)         [13]
      └ BİLEŞEN system_components   (performans_gostergesi, swot...)       [35]
          └ KART  system_cards     (kurum_ozet_kartlar...)                [YENİ — kademeli]
              └ VERİ card_data_sources (data_key + required_component_code)
```
Bağ tabloları: `package_modules`, `module_component_slugs`.

### ASIL ZOR KISIM (kullanıcının en çok vurguladığı — ÇÖZÜLDÜ ve KANITLANDI)
Bir kart farklı paketlerden veri çeker. Kullanıcının paketinde **olmayan** veri parçası
karttan **DÜŞER** (kart kalır, kısmi gösterilir). Komple gizleme YOK.
- **Kanıt (runtime):** `/kurum` özet kartında user_count(kısıtsız)/process_count(L2-süreç)/
  strategy_count(L1) — **tom1'de SADECE process_count düştü**, kullanıcı+strateji kaldı.
- Admin'den `required_component_code` değişince son kullanıcının görünümü ANINDA değişiyor
  (koddan değil DB'den). Tam istenen.

### Kullanıcı kararları (bağlayıcı)
1. Yetkisiz veri → **satır/alan düşer** (kart kalır).
2. Yönetim **DB-tabanlı + admin UI** (4 katman gör/taşı/düzenle).
3. Kart keşfi **otomatik** (template data-card-* tarar) + **tekrar tetiklenebilir**.
4. Veri-kaynak eşlemesi **DB'de** (CardDataSource), admin UI'dan yönetilir.
5. Düzenleme kapsamı: **kart + veri katmanı** (paket/modül üst katmanlar mevcut UI'larda).
6. Kimlik kartları (Misyon/Amaç/Değerler/Etik/Kalite) → **kurum modülü** bileşeni.

---

## ENFORCEMENT KATMANLARI (hepsi çalışıyor, runtime doğrulandı)
1. **Route gating** (`platform_core/__init__.py::_enforce_package_module_gating`):
   blueprint before_request, /process,/bireysel,/project,/analiz,/k-radar,/k-rapor
   prefix'leri pakete göre kapatır. tom1'de 6 modül 302→masaüstü.
2. **Sidebar gating** (`app/__init__.py::_inject_sidebar_modules` + base.html):
   sidebar modül linkleri paket'e göre gizlenir.
3. **Bileşen görünürlük** (`component_visible(slug)` Jinja helper, app/__init__.py):
   modül açık ama içindeki bileşen kapalı. /kurum PG bloğu sarıldı.
4. **Kart-içi veri** (`card_data_visible(card_code, data_key)` helper):
   kartın her veri parçası ayrı gate. /kurum özet kartı 3 stat işaretli.
- Tümünde: yalnız platform **Admin** bypass; kurum rolleri (tenant_admin/executive_manager)
  pakete TABİ (require_component bypass'ı daraltıldı). Fail-open.

---

## TEST ORTAMI — tom1/tom2/tom3 (Tomofil'den kademeli klon)
| Tenant | id | Paket | Veri | Kullanıcı |
|--------|----|----|----|----|
| tom1 | — | baslangic(L1) | kimlik+strateji+süreç(PGV YOK) | 97× `1<email>` |
| tom2 | — | yonetim(L2) | +PGV+bireysel | 97× `2<email>` |
| tom3 | — | strateji(L3) | +ileri analiz | 97× `3<email>` |
- **Ortak şifre: `Test1234!`**. Giriş örn: `1deniz.tunc@kokpitim.com` (executive_manager).
- Platform Admin: `admin@kokpitim.com` (şifre kullanıcıda) — /admin sayfaları için.
- KOE tom1'de çalışıyor (PGV'siz, süreç VARLIĞINDAN) — kullanıcı haklıydı.

## KONTROL LİNKLERİ (admin@kokpitim.com ile)
- `/admin/hierarchy` — 4-katman ağaç + "Kartları Keşfet" + required_component dropdown
- `/admin/packages` — paket↔modül atama (pakete tıkla→Modüller)
- `1deniz` ile `/kurum` — sonucu son kullanıcıda gör

## YEREL BAŞLATMA
`python pybasla.py` — 5001'deki stale süreçleri öldürüp tek temiz app.py başlatır
(memory: yerel 5001 stale süreç tuzağı çözümü). DB değişikliği öncesi pg_dump şart
(C:/pgdata/bin, PGPASSWORD env — şifreyi ekrana basma).

---

## SON YAPILAN (bu oturumun finali)
**Sorun (kullanıcı):** "modüllerin altında bileşen katmanı yok, direkt karta iniyor."
**Kök neden:** `module_component_slugs` eski/karışıktı — 35 bileşen sadece sp+surec'e
(mantıksız), kurum/k_radar/bireysel/proje/analiz/k_rapor → 0 bileşen.
**Çözüm:** `scripts/remap_modul_bilesen.py` — 122 karışık satır silindi, 35 temiz bağ
(kimlik→kurum, ileri analiz→ileri_sp, PG→surec). Ağaç doldu: baslangic 18 bileşen.

## SIRADAKİ ADIMLAR (kullanıcıya soruldu, henüz seçilmedi)
- **(a)** Eksik modüllerin (k_radar/bireysel/proje/analiz/k_rapor) bileşenlerini tanımla
  — bunlar system_components'ta HİÇ yok (35 bileşen hep sp/surec/kurum dünyasından).
- **(b)** Daha çok kartı `data-card-*` ile işaretle → keşfet (kademeli kapsam).
  Şu an SADECE /kurum özet kartı işaretli (kanıt örneği).
- **(c)** `claude/kart-katmani` dalını main'e merge et.

## AÇIK SINIRLAR (dürüstçe)
- Bu **template-düzeyi** gizleme (kart render edilmez → veri gösterilmez). Servis/route
  hâlâ veriyi HESAPLIYOR (boşa). Derin güvenlik (doğrudan API çağrısı) ayrı.
- Admin UI: kart+veri düzenleme var; sira alanı var ama template'ler sira'ya göre render
  ETMİYOR (sürükle-bırak görsel taşıma yok, sayısal sıra girişi var).
- Kart işaretleme kademeli — çoğu kart henüz işaretsiz.

## İLGİLİ BELGELER
- `docs/paketler/KART-KATMANI-TASARIM.md` — 4-katman + veri-farkındalık tasarımı (mutabakat)
- `docs/paketler/BILESEN-GORUNURLUK-KALIBI.md` — component_visible kalıbı
- `docs/paketler/PAKETLEME-STRATEJISI.md` — §4.A/B/C: L1/L2/L3 inşa kararları
- `docs/L1-L2-L3-UX-TEST.md` — UX test yönergesi
- `docs/TASKLOG.md` — TASK-184…198 (L1'den kart katmanına tüm geçmiş)

## ÇALIŞMA TARZI (memory'den — bağlayıcı)
- Ajan/keşif raporlarına GÜVENME → DB query / runtime test_client ile teyit et.
  (Bu oturumda defalarca kanıtlandı: "yok" denenler aslında vardı.)
- Tek seferde doğru çözüm; deneme-yanılma yasak; dosyayı okumadan kod yazma.
- Canlı veri üstünde upsert testi YAPMA → sentetik veri + temizlik (Porter dersi).
- main'e doğrudan commit YOK; her iş kendi dalında → kullanıcı onayıyla merge.
