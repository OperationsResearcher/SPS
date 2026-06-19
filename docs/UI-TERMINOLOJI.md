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
| `Admin` (rol) | **Sistem Yöneticisi** | "Platform Admin", "Admin" | "Sistem Yöneticisi" |
| `tenant_admin` (rol) | **Kurum Yöneticisi** | — | "Kurum Yöneticisi" |
| `executive_manager` (rol) | **Üst Yönetim** | "Kurum Üst Yönetimi" | "Üst Yönetim" |
| `standard_user` (rol) | **Kurum Kullanıcısı** | "Standart Kullanıcı" | "Kurum Kullanıcısı" |

> **Rol etiketleri tek kaynak:** Yukarıdaki rol→Türkçe eşlemesi kodda `app/constants/roles.py::ROLE_LABELS_TR` ve `role_label_tr()` ile tutulur. Template'lerde `{{ role_label_tr(user.role.name) }}`, Python'da `from app.constants.roles import role_label_tr`. **UI'da rol etiketini hardcode etme** — helper'dan oku (L1 Dal 5, 2026-06-19).
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
| `initiative` | **Girişim** |
| `exec dashboard` | **Yönetici Paneli** |
| `quarterly review` | **Çeyreklik Değerlendirme** |
| `replan trigger` | **Yeniden Planlama Tetikleyicileri** |
| `blue ocean` | **Mavi Okyanus** |
| `x-matrix` | **X-Matrisi** (Hoshin X-Matrisi) |
| `AI` / `artificial intelligence` | **Yapay Zeka** |
| `trigger` | **Tetikleyici** |
| `review` (çeyreklik/aylık) | **Değerlendirme** |
| `cadence` | **Ritm / Tempo** |
| `check-in` | **Takip / Kontrol** |
| `what-if` | **Senaryo Varyasyonu** (bağlama göre) |
| `baseline` (senaryo) | **Temel Senaryo** |
| `canvas` (strategy) | **Tuval** (Strateji Tuvali, Değer Tuvali) |
| `value curve` | **Değer Eğrisi** |
| `ERRC grid` | **ERRC Tablosu** |
| Plan yılı durumu: `active/closed/draft/archived` | **aktif / kapalı / taslak / arşiv** |
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

### ✅ Düzeltildi — 2026-05-25

- `/admin/sub-tenants` sayfası: "Alt Tenant" → "Alt Kurum" (tüm metinler)
- `/admin/sub-tenants/usage` sayfası: "Tenant" / "Şirket" → "Kurum"
- Sidebar (Holding): "Alt Şirket Yönetimi" → "Alt Kurum Yönetimi"
- Sidebar (Bayi): "Müşterilerim" → "Müşteri Kurumlarım"
- Holding dashboard: "Şirket" → "Kurum" (tüm metinler, hero etiketleri, başlıklar)
- Holding drill-down: "alt-şirket" → "alt kurum"
- Backend hata mesajları: "tenant" / "alt-tenant" → "kurum" / "alt kurum"

### 🔲 Henüz düzeltilmemiş

- `/admin/tenants` modal'ları içinde JS literal'larda "tenant" geçebilir — kontrol gerekli
- Modal title'larda "Yeni Tenant" benzeri eski kalıntılar varsa
- Audit log mesajları (Türkçe karışık var — politika belirsiz)
- Eski sayfalar (legacy admin/ rotaları)

---

## Bağlantılı Belgeler

- [`docs/KURALLAR-MASTER.md`](KURALLAR-MASTER.md) §2 — Genel dil kuralları
- [`docs/UI-KILAVUZU.md`](UI-KILAVUZU.md) — Tasarım sistemi
- [`CLAUDE.md`](../CLAUDE.md) — Proje genel kuralları
