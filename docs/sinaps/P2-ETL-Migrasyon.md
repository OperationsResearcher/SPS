# P2 — ETL MİGRASYON (Kokpitim → Sinaps)
> Tarih: 2026-05-16 · Durum: TASLAK · Bağımlılık: D3, D6

---

## 1. Felsefe

- **One-time ETL.** Sürekli replikasyon yok; müşteri "geçmek istediğinde" çalıştırılır
- **Müşteri opt-in.** Kokpitim sahibi kalır; Sinaps'a geçiş ürün kararıdır
- **Veri sadakat ölçümü:** her tabloda satır sayısı + checksum doğrulanır
- **Geri dönüş penceresi:** 30 gün — kaynak Kokpitim dondurulur, salt-okunur kalır

---

## 2. Akış (Yüksek Seviye)

```
Kokpitim PG (snapshot)
   ↓ (1) Dump (pg_dump --schema-only + --data-only)
Staging PG ──→ (2) Transform layer (dbt / Python ETL)
   ↓
Sinaps PG (yeni tenant) ←── (3) Load + RLS doğrulama
   ↓
(4) Reconciliation rapor + müşteri onayı
   ↓
(5) Cut-over (Kokpitim freeze + Sinaps live)
```

---

## 3. Eşleme Tablosu (Ana Varlıklar)

| Kokpitim kaynağı | Sinaps hedefi | Notlar |
|---|---|---|
| `tenant` (legacy) | `core.organizations` + `core.tenants` | 1 tenant → 1 org + 1 root tenant |
| `user` | `core.users` + `core.memberships` | Keycloak'a otomatik sync, password reset zorunlu |
| `paket` | `core.packages.code` mapping | KOBİ-paketi → Sinaps Pro/Enterprise eşlemesi (manuel) |
| `surec` | `process.processes` | RACI/CMMI alanları null bırakılır, müşteri sonradan doldurur |
| `surec_adim` | `process.process_steps` | |
| `kpi` (legacy) | `strategy.kpis` | formula alanı string mapping |
| `kpi_olcum` | `strategy.kpi_measurements` | period normalize edilir |
| `ana_strateji` | `strategy.strategies` (type=main) | pillar boş, müşteri sonradan H1-Hn oluşturur |
| `alt_strateji` | `strategy.strategies` (type=sub, parent set) | |
| `swot_*` | `strategy.analyses` (framework=swot) | jsonb shape dönüşümü |
| `pestle_*` | `strategy.analyses` (framework=pestel) | |
| `bcg_*`, `ansoff_*` | **kaybedilir** | Sinaps'ta yok; PDF export sunulur |
| `bsc_*` | `strategy.bsc_perspectives` | perspective enum mapping |
| `okr` (legacy) | `strategy.okrs` + `strategy.key_results` | tek seviye → org-level olarak yüklenir |
| `bireysel_perf` | `execution.individual_performance` | |
| `proje`, `gorev` | **kaybedilir** | Sinaps'ta initiative yok-MVP'de; PDF arşiv |
| `bildirim` | **atılır** | Geçmiş bildirim taşınmaz |
| `dosya` | `core.documents` + S3 copy | s3_key yeniden üretilir |
| `audit_log` | `audit.events` partition | gözlem amaçlı, 90 gün sonrası S3 |

> Kaybedilen varlıklar için müşteriye **PDF arşiv paketi** üretilir (data export).

---

## 4. Dönüşüm Kuralları

### 4.1 Tenant Yapısı
- Tek Kokpitim tenant → Sinaps'ta `Organization('tomofil')` + tek `Tenant('tomofil.main')` → tenant_path = `tomofil.main`
- Müşteri sub-tenant istemiyorsa burada kalır

### 4.2 Identity
- E-posta primary key — Keycloak'ta varsa link, yoksa yeni user + invite e-postası
- Eski rol enum → yeni role_set mapping tablosu:
  - `admin` → `['tenant_admin']`
  - `editor` → `['strategy_editor','process_editor','kpi_editor']`
  - `viewer` → `['viewer']`

### 4.3 i18n
- Kokpitim sadece TR — Sinaps `translatable_field` JSONB: `{tr: "...", en: null}`
- Migration sonrası **opsiyonel** AI çeviri job'u (kullanıcı onayı) ile en doldurulabilir

### 4.4 ID'ler
- Kokpitim auto-increment int — Sinaps uuid v7
- `legacy_id` int kolonu **geçici migration tablosunda** tutulur; backreference için
- 90 gün sonra `legacy_id` drop

### 4.5 Timestamps
- TZ-naive (TR varsayım) → UTC `timestamptz`
- created_by null kayıtlar → `system_user` UUID'sine bağlanır

### 4.6 Soft Delete
- Kokpitim `is_active=false` → Sinaps `deleted_at = updated_at` (en iyi tahmin)

---

## 5. ETL Aracı Seçimi

| Seçenek | Karar |
|--|--|
| **dbt + Postgres staging** | ✅ Yapı/snapshot/test'i en olgun |
| Custom Python script | tek-seferlik için overkill değil ama dbt'nin test/lineage'i yok |
| Airbyte/Fivetran | ücretli + sürekli sync için tasarlanmış, tek seferlik için over |

**Karar:** dbt + Python wrapper. Repo: `ops/migration-from-kokpitim/`.

---

## 6. Reconciliation (Veri Sadakat Doğrulaması)

Her tablo için **3 katman test:**

1. **Row count parity** — Kokpitim N satır → Sinaps N satır (kaybedilen tablolar hariç)
2. **Checksum** — Kritik metin alanları (KPI adı, OKR objective) SHA256 → eşleşmeli
3. **Spot check** — Rastgele 50 satır UI'da görsel kontrol (müşteri katılımıyla)

Rapor formatı: `migration_report.html` — yeşil/sarı/kırmızı tablo özet.

---

## 7. Cut-over Prosedürü (D-Day)

| T | Aksiyon |
|--|--|
| T-7 gün | Müşteri bilgilendirme, freeze tarihi duyuru |
| T-1 gün | Dry-run (production snapshot → staging Sinaps) |
| T 09:00 | Kokpitim salt-okunur moda alınır (banner: "Sinaps geçişi devam ediyor") |
| T 09:15 | Production dump başlar |
| T 10:00 | ETL çalıştırılır (Postgres-to-Postgres) |
| T 12:00 | Reconciliation rapor + müşteri sign-off |
| T 13:00 | Keycloak user provisioning + invite e-posta |
| T 14:00 | Sinaps tenant live; smoke test 5 kullanıcı |
| T 15:00 | Müşteri GO/NO-GO kararı |
| T 16:00 | GO → Kokpitim DNS redirect / NO-GO → Kokpitim live'a geri |

**Rollback penceresi:** 30 gün — Kokpitim salt-okunur ama erişilebilir; Sinaps'ta sorun olursa müşteri Kokpitim'e dönebilir.

---

## 8. Müşteri Tarafı Hazırlık Checklist'i

Migration başlamadan **müşteri** şunları yapar:
- [ ] Kullanıcı listesi temizliği (pasif hesaplar arşivlendi)
- [ ] Belgeler için S3 erişim onayı
- [ ] DPA imza yenilemesi (Sinaps farklı veri controller)
- [ ] İletişim sahipleri: teknik kontak + iş kontak
- [ ] Yedek alma onayı

---

## 9. Maliyet ve Süre

- Standart Kokpitim tenant (< 100 kullanıcı, < 1000 KPI): **2 iş günü** ETL + 1 gün cut-over
- Büyük tenant (> 500 kullanıcı): **5-7 iş günü** ETL + 2 gün cut-over
- Müşteri fiyatı: Implementation pack'e dahil veya €5K eklenti
- Dahili maliyet: ~20 saat ETL eng. + 8 saat CSM + 4 saat SRE

---

## 10. Kayıp Veri Politikası

Tomofil'ten örnek: BCG, Ansoff, Proje/Görev gibi Sinaps'ta olmayan modüller.

**Müşteri seçimi:**
- (a) PDF arşiv (default, ücretsiz)
- (b) Custom Sinaps modülü geliştirme (€25K+ kustom iş)
- (c) Kokpitim'de tutmaya devam (paralel kullanım — yıllık)

---

## 11. Açık Sorular
- OS-1: Migration paid mi (Implementation Pack içinde) yoksa first-year promo ücretsiz mi?
- OS-2: Birden çok Kokpitim tenant aynı müşterinin → tek org çatısı altında birleştirilir mi?
- OS-3: Keycloak user import sırasında MFA reset zorunlu mu? — Önerim: evet, güvenlik için
- OS-4: 30 gün sonrası Kokpitim verisi otomatik silinsin mi yoksa müşteri onayıyla mı?
