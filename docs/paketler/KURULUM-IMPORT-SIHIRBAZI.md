# Kurulum Verisi Import Sihirbazı — Tasarım (MUTABIK, 2026-07-08)

> **Mutabakat (kullanıcı, 2026-07-08):** (1) Upsert = eşleşen kod GÜNCELLENİR,
> (2) Strateji sayfası v1'e DAHİL, (3) Konum = Admin modülü → Kurulum İçe Aktarma.

> 2026-07-08 (TASK-235 adayı, fablerapor Faz 3). Kapsam onayı alındı; bu belge
> **kodlama öncesi mutabakat** içindir (KURALLAR §1 akışı).
> İlgili mevcut altyapı: `app/services/bulk_import_service.py` (PGV verisi import'u — desen alınacak),
> `admin_users_bulk_import` (kullanıcı import'u).

## 1. Amaç ve konumlandırma

Yeni müşteri onboarding'inde kurulum verilerinin — **süreçler + PG tanımları**
(+ opsiyonel **strateji ağacı**) — tek Excel çalışma kitabından içeri alınması.
Satış argümanı: "Excel'inizi getirin, yarım günde Kokpitim'e geçin."

Mevcut bulk import'lardan farkı: PGV import'u *veri* (ölçüm) alır; bu sihirbaz
*yapı* (tanım) kurar.

## 2. Şablon yapısı — tek .xlsx, 3 sayfa

İndirme: sihirbazın 1. adımında "Şablonu İndir" (mevcut `make_kpi_template_excel` deseni;
başlıklar Türkçe + zorunlu alanlar `(*)` işaretli + örnek 2 satır önceden doldurulmuş).

### Sayfa 1: "Surecler"
| Kolon | Zorunlu | Model alanı | Doğrulama |
|---|---|---|---|
| Süreç Kodu (*) | ✅ | `Process.code` | Tenant içinde benzersiz; mevcutsa GÜNCELLEME (upsert) |
| Süreç Adı (*) | ✅ | `Process.name` | ≤200 karakter |
| Üst Süreç Kodu | ○ | `Process.parent_id` | Aynı dosyada veya DB'de var olmalı; döngü kontrolü |
| Ağırlık | ○ | `Process.weight` | 0-100 sayı |
| Doküman No / Revizyon No | ○ | ilgili alanlar | — |

### Sayfa 2: "PG_Tanimlari"
| Kolon | Zorunlu | Model alanı | Doğrulama |
|---|---|---|---|
| Süreç Kodu (*) | ✅ | `ProcessKpi.process_id` | Sayfa 1'de veya DB'de olmalı |
| PG Kodu (*) | ✅ | `ProcessKpi.code` | Süreç içinde benzersiz; upsert anahtarı |
| PG Adı (*) | ✅ | `ProcessKpi.name` | — |
| Hedef | ○ | `target_value` | — |
| Birim | ○ | `unit` | — |
| Periyot (*) | ✅ | `period` | Liste: Aylık/Çeyreklik/Yıllık (dropdown data-validation şablona gömülür) |
| Toplama Yöntemi | ○ | `data_collection_method` | Toplama/Ortalama/Son Değer (vars. Ortalama) |
| Gösterge Türü | ○ | `gosterge_turu` | İyileştirme/Koruma/Bilgi Amaçlı |
| Ağırlık | ○ | `weight` | 0-100 |

### Sayfa 3: "Strateji" (OPSİYONEL — boş bırakılabilir)
| Kolon | Zorunlu | Model | Doğrulama |
|---|---|---|---|
| Ana Strateji Adı (*) | ✅ | `Strategy.title` | Upsert anahtarı: ad (tenant+plan yılı içinde) |
| Alt Strateji Adı | ○ | `SubStrategy.title` | Ana stratejiye bağlanır |
| Bağlı Süreç Kodları | ○ | `process_sub_strategy_links` | Virgülle ayrık; Sayfa 1/DB'de olmalı |

> K-Vektör ağırlıkları v1 kapsamı DIŞI (config snapshot servisi gerektirir) — UI'dan atanır.

> Strateji sayfası **aktif plan yılına** yazar; plan yılı yoksa sihirbaz uyarır ve
> bu sayfayı atlar (süreç/PG yine kurulur).

## 3. Sihirbaz UX — 3 adım (yeni sayfa: Admin → Kurulum İçe Aktarma)

1. **Şablon + Yükle:** şablon indirme bağlantısı; .xlsx sürükle-bırak (≤5MB).
2. **Önizleme + Doğrulama (dry-run):** dosya sunucuda parse edilir, HİÇBİR yazma yapılmadan
   satır-satır sonuç tablosu döner: ✅ eklenecek / 🔄 güncellenecek / ❌ hatalı (satır no + Türkçe
   hata mesajı: "Satır 12: Periyot 'Haftalık' geçersiz — Aylık/Çeyreklik/Yıllık olmalı").
   Hatalı satır varsa devam butonu kilitli DEĞİL — kullanıcı "hatalıları atla ve devam et"
   seçebilir (checkbox, varsayılan kapalı).
3. **Uygula + Rapor:** tek transaction'da yazım (TASK-228 dersi: yutulan hata yok, hata
   → tam rollback + anlaşılır mesaj). Sonuç özeti: N süreç eklendi, M PG güncellendi,
   K satır atlandı + atlananların indirilebilir hata raporu (.xlsx).

## 4. Teknik tasarım

- **Servis:** `app/services/setup_import_service.py` (yeni) — `parse_workbook() → dry_run() → apply()`
  ayrımı; `bulk_import_service.py` desenleri (openpyxl, kolon başlık eşleme) yeniden kullanılır.
- **Route'lar:** `micro/modules/admin/routes_setup_import.py` (yeni) — 3 endpoint:
  `GET /admin/setup-import` (sayfa), `POST .../dry-run`, `POST .../apply`. `@login_required` +
  tenant_admin/Admin kontrolü; dosya `validate_file_upload` ile doğrulanır.
- **Upsert anahtarları:** Süreç=`(tenant_id, code)`, PG=`(process_id, code)`, Strateji=ad.
  Silme YAPILMAZ (dosyada olmayan mevcut kayıtlar dokunulmaz — güvenli taraf).
- **Transaction:** apply tamamı tek `db.session` transaction; kısmi başarı yok
  ("hatalıları atla" seçiliyse atlanacaklar dry-run'da belirlenir, apply yine tek transaction).
- **Audit:** `SETUP_IMPORT_APPLY` audit kaydı (satır sayıları + dosya adı).
- **Kart standardı:** sayfa kartları `data-card-code="admin_setup_import.*"` ile (KURALLAR §5.1).
- **i18n:** UI metinleri `{{ _() }}`; hata mesajları Türkçe üretilir, msgid'ler .po'ya eklenir.

## 5. Kapsam DIŞI (bilinçli)

- PGV (ölçüm verisi) import'u — zaten var (`bulk-import`)
- Kullanıcı import'u — zaten var (`admin_users_bulk_import`)
- CSV desteği — v1 yalnız .xlsx (CSV'de sayfa/tip kaybı; talep gelirse v2)
- Proje/faaliyet import'u — v2 adayı
- Var olan kayıtların toplu SİLİNMESİ — asla (soft delete politikası)

## 6. Tahmin

Servis + 3 route + sihirbaz sayfası (3 adım) + şablon üretici + testler (dry-run/apply/upsert/
döngü kontrolü) ≈ tek oturumluk iş. Migration GEREKMEZ (yeni tablo yok).

---
**Mutabakat soruları:**
1. Upsert davranışı onay: mevcut kod eşleşirse GÜNCELLE (yoksa yalnız-ekle mi olsun?)
2. Strateji sayfası v1'e dahil mi, yoksa v1 yalnız süreç+PG mi?
3. Sihirbazın yeri: Admin modülü altında mı, Kurum Paneli altında mı?
