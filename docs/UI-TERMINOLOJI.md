# Kokpitim UI Terminoloji Kılavuzu

> **Sürüm:** 1.0
> **Yürürlük:** 2026-05-25
> **Referans:** `docs/KURALLAR-MASTER.md` §2 (Dil Kuralları)

Bu belge **Kokpitim arayüzünde kullanılacak Türkçe terimleri** sözlük olarak tanımlar. Kod tarafında İngilizce/snake_case kullanımı serbest, ama **kullanıcının gördüğü her metin** bu kılavuza uymalıdır.

---

## Temel Prensip

| Katman | Dil | Örnek |
|---|---|---|
| Kod (model, route, helper, JS değişken) | İngilizce / snake_case | `tenant_id`, `current_user`, `get_kpi_list()` |
| Veritabanı kolonları | İngilizce / snake_case | `users.tenant_id`, `process_kpis.code` |
| API JSON anahtarları | İngilizce / snake_case | `{"tenant_id": 1, "user_email": "..."}` |
| **UI metinleri (label, button, mesaj, başlık)** | **Türkçe — bu kılavuza göre** | "Kurum", "Kullanıcı", "Süreç Performans Göstergesi" |
| Log mesajları | İngilizce | `[admin] tenant_id=27 created sub-tenant 42` |
| Hata mesajları (kullanıcıya görünür) | Türkçe | "Kurum bulunamadı", "Yetkiniz yok" |

**Yasak:**
- UI'da "tenant", "user", "endpoint", "API key" gibi İngilizce/jargon kelimeler doğrudan görünmemeli (parantez içi gloss verilebilir).
- Karışık kullanım: "Tenant Adı" + "Kurum Listesi" gibi aynı kavram için iki terim. **Tek seçim:** Kurum.

---

## Terminoloji Sözlüğü

### Genel Kavramlar

| Kod tarafı | UI tarafı | Yanlış kullanım | Doğru kullanım |
|---|---|---|---|
| `tenant`, `Tenant` | **Kurum** | "Tenant Listesi", "tenant ekle" | "Kurum Listesi", "Kurum Ekle" |
| `user`, `User` | **Kullanıcı** | "User profili", "Add user" | "Kullanıcı Profili", "Kullanıcı Ekle" |
| `dealer` (tenant_type) | **Bayi** | — | "Bayi Yönetim Paneli" |
| `holding` (tenant_type) | **Holding** | — | "Holding Konsolide Görünümü" |
| `parent_tenant` | **Üst Kurum** | "Parent tenant" | "Üst Kurum" |
| `sub_tenant` | **Alt Kurum** | "Sub-tenant" | "Alt Kurum", "Müşteri Kurumu" |
| `role` | **Rol** | — | "Rol: Kurum Yöneticisi" |
| `permission` | **Yetki** | "Permission denied" | "Yetkiniz yok" |
| `notification` | **Bildirim** | — | "Bildirimler" |
| `audit log` | **Denetim Kaydı** | "Audit log" | "Denetim Kaydı" |
| `package` (SubscriptionPackage) | **Paket / Abonelik Paketi** | — | "Abonelik Paketi" |

### Stratejik Planlama

| Kod tarafı | UI tarafı |
|---|---|
| `plan_year` | **Plan Yılı / Dönem** |
| `strategy` | **Strateji / Ana Strateji** |
| `sub_strategy` | **Alt Strateji** |
| `initiative` | **Girişim / Initiative** (her ikisi de kabul, tutarlı kullan) |
| `milestone` | **Kilometre Taşı** |
| `scenario` | **Senaryo** |
| `okr` / `objective` | **Hedef / Objective** (akademik konu — OKR bilinçli kalır) |
| `key_result` | **Anahtar Sonuç** |
| `pivot` | **Pivot / Strateji Değişimi** |
| `vision` | **Vizyon** |
| `mission`, `purpose` | **Misyon** |
| `core_values` | **Değerler** |
| `replan_trigger` | **Yeniden Planlama Tetikleyicisi** |

### Süreç / KPI

| Kod tarafı | UI tarafı |
|---|---|
| `process` | **Süreç** |
| `kpi`, `ProcessKpi` | **KPI / Performans Göstergesi** |
| `kpi_data` | **KPI Verisi / Ölçüm** |
| `activity` (ProcessActivity) | **Faaliyet** |
| `individual_pg` | **Bireysel Performans Göstergesi (PG)** |
| `karne` (zaten Türkçe) | **Karne** |
| `target` | **Hedef** |
| `actual` | **Gerçekleşen** |
| `period` | **Dönem** |

### Risk / K-Radar

| Kod tarafı | UI tarafı |
|---|---|
| `risk_heatmap_item` | **Risk** |
| `risk_score` (probability × impact) | **Risk Skoru** |
| `anomaly` | **Anomali** |
| `bottleneck` | **Darboğaz** |
| `stakeholder` | **Paydaş** |
| `competitor` | **Rakip** |
| `swot` | **GZFT / SWOT** (kısaltma kabul) |
| `pestle` | **PESTEL** |
| `vrio` | **VRIO** |

### Proje Yönetimi

| Kod tarafı | UI tarafı |
|---|---|
| `project` | **Proje** |
| `task` | **Görev** |
| `gantt` | **Gantt / Zaman Çizelgesi** |
| `kanban` | **Kanban Tahtası** |
| `raid` | **RAID (Risk-Varsayım-Sorun-Bağımlılık)** |
| `evm` | **EVM / Kazanılmış Değer Yönetimi** |
| `cpm` | **CPM / Kritik Yol** |
| `milestone` | **Kilometre Taşı** |

### Yapay Zeka

| Kod tarafı | UI tarafı |
|---|---|
| `llm`, `ai` | **AI / Yapay Zeka** |
| `prompt` | **Prompt / Soru** (teknik bağlamda Prompt kalabilir) |
| `token` | **Token** (teknik terim — bırak) |
| `byok` (Bring Your Own Key) | **Kendi Anahtarım** |
| `api key` | **API Anahtarı** |
| `quota` | **Kota / Kullanım Limiti** |

### Kimlik / Güvenlik

| Kod tarafı | UI tarafı |
|---|---|
| `login` | **Giriş** |
| `logout` | **Çıkış** |
| `password` | **Şifre / Parola** (Şifre öncelikli) |
| `2fa`, `totp` | **İki Faktörlü Doğrulama (2FA)** |
| `backup codes` | **Yedek Kodlar** |
| `csrf` | (UI'da görünmez) |
| `session` | **Oturum** |

### Eylem Fiilleri (Buton Metni)

| Kod / İngilizce | UI Türkçe |
|---|---|
| `create` / `add` | **Ekle / Oluştur / Yeni** |
| `edit` / `update` | **Düzenle / Güncelle / Kaydet** |
| `delete` | **Sil** |
| `archive` | **Arşivle** |
| `activate` / `deactivate` | **Aktifleştir / Pasifleştir** |
| `enable` / `disable` | **Etkinleştir / Devre Dışı Bırak** |
| `submit` | **Gönder / Tamam** |
| `cancel` | **İptal** |
| `confirm` | **Onayla** |
| `reset` | **Sıfırla** |
| `export` | **Dışa Aktar / İndir** |
| `import` | **İçe Aktar / Yükle** |
| `upload` | **Yükle** |
| `download` | **İndir** |
| `view` / `show` | **Görüntüle / Aç** |
| `close` | **Kapat** |
| `refresh` / `reload` | **Yenile** |
| `search` | **Ara** |
| `filter` | **Filtrele** |
| `sort` | **Sırala** |

---

## Tutarlılık Kuralları

1. **Tek seçim**: Bir kavramın TR karşılığı tek olmalı. "Kurum" seçtikse her yerde "Kurum" — "şirket" veya "tenant" yok.

2. **Cümlede ilk harf büyük**, başlıklarda **Title Case (Türkçe)**:
   - ✓ "Yeni kurum eklendi."
   - ✓ "Kurum Yönetimi"
   - ✗ "yeni kurum eklendi"
   - ✗ "Yeni Kurum Eklendi" (cümle başlığı değilse)

3. **İngilizce kısaltmalar büyük kalır**: API, KPI, EVM, CPM, SWOT, OKR, 2FA, BYOK

4. **Tooltip/title attribute**: Aynı dil kurallarına tabidir.

5. **Hata/uyarı mesajları**: Net ve aksiyon yönlü:
   - ✓ "Bu e-posta zaten kullanılıyor. Farklı bir e-posta deneyin."
   - ✗ "Email already exists"
   - ✗ "Hata: validation_error"

6. **Boş durum (empty state)** mesajları teşvik edici:
   - ✓ "Henüz görev yok. Yeni Görev Ekle ile başlayabilirsiniz."
   - ✗ "No tasks"

7. **Modal başlıkları fiil + nesne**:
   - ✓ "Yeni Kullanıcı Ekle"
   - ✓ "Kurumu Düzenle"
   - ✗ "User Add"

---

## Bu Belgenin Güncellenmesi

Yeni terim eklerken:

1. Bu dosyayı düzenle, ilgili kategoriye satır ekle (alfabetik sıra korumaya gerek yok, anlamsal grup öncelikli).
2. Tabloyu **Kod tarafı | UI tarafı | Yanlış | Doğru** sırasıyla doldur.
3. Tutarlılık kurallarına ihlal eden yerler varsa "Tutarsızlık" bölümüne kayıt at.
4. Commit mesajı: `docs(ui-terminoloji): "X" → "Y" eklendi`.

---

## Tutarsızlık Listesi (Henüz Düzeltilmemiş)

Bu liste mevcut UI'da kılavuza aykırı olan yerleri listeler. **Sırayla düzeltilecek** — yeni özellik eklerken o ekrana dokunulduğunda buradan da kontrol et:

### Düzeltilmesi gereken — "tenant" / "user" tabanlı

| Konum | Mevcut | Olması gereken |
|---|---|---|
| `/admin/tenants` sayfa başlığı, button'lar | "Kurum Yönetimi" / "Yeni Kurum" ✓ (bu zaten doğru) | — |
| `/admin/users` sayfa başlığı, button'lar | "Kullanıcı Yönetimi" / "Yeni Kullanıcı" ✓ (zaten doğru) | — |
| `/admin/sub-tenants` modalda "Alt Tenant" | "Alt Tenant Aç" → "Alt Kurum Aç" | "Yeni Alt Kurum" |
| Sidebar: "Alt Şirket Yönetimi" (Holding) | OK ama "şirket" yerine "kurum" tutarlılığı | "Alt Kurum Yönetimi" |
| Sidebar: "Müşterilerim" (Bayi) | OK — bayi bağlamında "müşteri" mantıklı | — |
| `/holding/tenant/<id>/view` üst banner | "Holding görünümü: ..." OK | — |
| Hata mesajları | "tenant_id" görünür — değiştir | "Kurum ID" / kullanıcıya gizle |

---

## Bağlantılı Belgeler

- [`docs/KURALLAR-MASTER.md`](KURALLAR-MASTER.md) §2 — Genel dil kuralları
- [`docs/UI-KILAVUZU.md`](UI-KILAVUZU.md) — Tasarım sistemi
- [`CLAUDE.md`](../CLAUDE.md) — Proje genel kuralları
