# KOKPİTİM Dokümantasyon İndeksi

> **Kod tabanında kaybolduysan önce:** [`SISTEM-HARITASI.md`](SISTEM-HARITASI.md) — "neyin ne olduğu".
> **Kurallar:** [`KURALLAR-MASTER.md`](KURALLAR-MASTER.md) — tek gerçek kaynak.
> Son düzen: 2026-06-16 (docs/ kök 115 → 49 aktif; arşiv `_arsiv/`'e taşındı).

---

## 🎯 Başla buradan
- [`KURALLAR-MASTER.md`](KURALLAR-MASTER.md) — çalışma kuralları, ortamlar, güvenlik borcu (TEK kaynak)
- [`SISTEM-HARITASI.md`](SISTEM-HARITASI.md) — sistem haritası: çekirdek, blueprint'ler, modüller, legacy yüzey
- [`PROJE-MASTER.md`](PROJE-MASTER.md) — proje bağlamı / master özet
- [`TASKLOG.md`](TASKLOG.md) — görev defteri (her değişiklik buraya)

## 🖥️ Ortam & Deploy
- [`SUNUCU-GUNCELLEME-REHBERI.md`](SUNUCU-GUNCELLEME-REHBERI.md) — **canonical** deploy (Yerel→Test/Demo/Yayın)
- [`ORACLE-PROD-VM.md`](ORACLE-PROD-VM.md) · [`ORACLE_DEPLOY_ADIMLAR.md`](ORACLE_DEPLOY_ADIMLAR.md) — Oracle VM
- [`DEMO-ORTAMI-PLAN.md`](DEMO-ORTAMI-PLAN.md) — demo ortamı
- [`VM-YEREL-SENKRON-REHBERI.md`](VM-YEREL-SENKRON-REHBERI.md) · [`VM_DEN_YERELE.md`](VM_DEN_YERELE.md) · [`YERELDEN_VM_YAYIN.md`](YERELDEN_VM_YAYIN.md)
- [`PostgreSQL-Geçiş-Rehberi.md`](PostgreSQL-Geçiş-Rehberi.md) · [`19MAYISYEDEK_RESTORE.md`](19MAYISYEDEK_RESTORE.md) — geri dönüş noktası

## 🔒 Güvenlik & Politika
- [`GUVENLIK_REHBERI.md`](GUVENLIK_REHBERI.md) · [`AI-POLITIKASI.md`](AI-POLITIKASI.md)
- [`SOC2_ISO27001_HAZIRLIK.md`](SOC2_ISO27001_HAZIRLIK.md) · [`YEDEKLER_POLICY.md`](YEDEKLER_POLICY.md) · [`LOCAL_ONLY_DEPLOY_POLICY.md`](LOCAL_ONLY_DEPLOY_POLICY.md)

## 🏗️ Teknik referans (canonical)
- [`CANONICAL_SCHEMA_DICTIONARY.md`](CANONICAL_SCHEMA_DICTIONARY.md) — isim/şema standardı
- [`PROCESS_API_CANONICAL.md`](PROCESS_API_CANONICAL.md) · [`SKOR_MOTORU_KULLANIM.md`](SKOR_MOTORU_KULLANIM.md) · [`K_VEKTOR.md`](K_VEKTOR.md)
- [`UI-TERMINOLOJI.md`](UI-TERMINOLOJI.md) · [`UI-KILAVUZU.md`](UI-KILAVUZU.md) · [`STATIC_ASSETS_PLATFORM.md`](STATIC_ASSETS_PLATFORM.md)
- [`KULE-TANIM.md`](KULE-TANIM.md) · [`TENANT-VERI-ENVANTERI.md`](TENANT-VERI-ENVANTERI.md)

## ♻️ Legacy / Strangler (eritilecek yüzey)
- [`LEGACY_ROUTE_INVENTORY.md`](LEGACY_ROUTE_INVENTORY.md) · [`LEGACY_ROUTE_DEPRECATION.md`](LEGACY_ROUTE_DEPRECATION.md)
- [`LEGACY_REDIRECT_MAP.md`](LEGACY_REDIRECT_MAP.md) · [`LEGACY_SUNSET_MAP.md`](LEGACY_SUNSET_MAP.md)
- [`CIFT-MODEL-BORCU-KURUMSAL-KIMLIK.md`](CIFT-MODEL-BORCU-KURUMSAL-KIMLIK.md) · [`HARD_MIGRATION_INVENTORY.md`](HARD_MIGRATION_INVENTORY.md)
- [`KOK_MICRO_BIRLESTIRME_CHECKLIST.md`](KOK_MICRO_BIRLESTIRME_CHECKLIST.md)

## 🧩 Micro platform
- [`micro-kullanim-kilavuzu.md`](micro-kullanim-kilavuzu.md) · [`micro-kok-url-migration.md`](micro-kok-url-migration.md)
- [`micro-proje-modulu-gereksinimler.md`](micro-proje-modulu-gereksinimler.md) · [`micro-karne-kontrol-listesi.md`](micro-karne-kontrol-listesi.md)
- [`proje-legacy-ve-tenant.md`](proje-legacy-ve-tenant.md)

## ✅ Checklist & Test
- [`DEPLOY_SMOKE_CHECKLIST.md`](DEPLOY_SMOKE_CHECKLIST.md) · [`QUICK_WINS_CHECKLIST.md`](QUICK_WINS_CHECKLIST.md)
- [`yetki-smoke-test-checklist.md`](yetki-smoke-test-checklist.md) · [`TEST_YONERGESI_SKOR_MOTORU.md`](TEST_YONERGESI_SKOR_MOTORU.md)

## 🗺️ Aktif planlama
- [`ROADMAP-2026H2.md`](ROADMAP-2026H2.md) — yol haritası
- [`paketler/`](paketler/) — paketleme/L1 stratejisi + teknik borç envanteri

## 📂 Konu klasörleri
`paketler/` · `kılavuz/` (kullanım kılavuzu & video) · `runbooks/` · `ops/` · `sinaps/` · `analizhaziran/` · `ems/` · `rapor/` · `test/` · `tomofil/`

## 🗄️ Arşiv — `_arsiv/`
Tamamlanmış/eski belgeler (2026-06-16'da taşındı, `git mv`, geçmiş korundu):
- `_arsiv/rapor/` — sprint raporları, Q2 analizleri, tamamlanmış iş özetleri (33)
- `_arsiv/ide/` — başka IDE/AI çıktıları (cursor/kiro/Gemini/Antigravity) (13)
- `_arsiv/plan/` — tamamlanmış/geçersiz eski planlar (10)
- `_arsiv/gunluk/` — tarihli iş notları / günlük raporlar (11)
