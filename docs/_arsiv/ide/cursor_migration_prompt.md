# Kokpitim — Eski Veritabanından Veri Migration Görevi

## GÖREVIN TANIMI

`docs/kokpitim_yedek.db` dosyasındaki eski verileri mevcut aktif veritabanına (yeni model yapısına göre) taşı. **Veri kaybı kesinlikle yasak.**

---

## ALTIN KURALLAR

1. **Asla hard delete yapma** — sadece `is_active=False` veya `silindi=True`
2. **Önce oku, sonra yaz** — her tablo için önce mevcut veriyle karşılaştır, duplicate oluşturma
3. **Transaction kullan** — her tablo migration'ı ayrı bir transaction içinde olsun, hata varsa rollback yap
4. **Log tut** — her tablo için kaç kayıt taşındı, kaçı atlandı (duplicate), kaç hata oluştu — konsola yazdır
5. **Şifre hash'leri koru** — `password_hash` alanını olduğu gibi taşı, yeniden hashleme
6. **ID çakışması riski** — mevcut DB'deki ID'lerle çakışmamak için ID mapping tablosu tut

---

## YEDEK DB BİLGİLERİ

**Dosya:** `docs/kokpitim_yedek.db`  
**Alembic versiyonu:** `a65f2b9c5a59`

### Taşınacak Tablolar ve Kayıt Sayıları

| Tablo | Kayıt | Öncelik | Not |
|-------|-------|---------|-----|
| `kurum` | 10 | 🔴 KRİTİK | Önce taşı, diğerleri buna bağlı |
| `user` | 36 | 🔴 KRİTİK | kurum_id mapping gerekli |
| `ana_strateji` | 33 | 🔴 KRİTİK | kurum_id mapping gerekli |
| `alt_strateji` | 58 | 🔴 KRİTİK | ana_strateji_id mapping gerekli |
| `surec` | 38 | 🔴 KRİTİK | kurum_id mapping gerekli |
| `surec_performans_gostergesi` | 273 | 🔴 KRİTİK | surec_id mapping gerekli |
| `bireysel_performans_gostergesi` | 204 | 🔴 KRİTİK | user_id mapping gerekli |
| `performans_gosterge_veri` | 1632 | 🔴 KRİTİK | bireysel_pg_id mapping gerekli |
| `swot_analizi` | 8 | 🟡 ORTA | kurum_id mapping |
| `pestle_analizi` | 2 | 🟡 ORTA | kurum_id mapping |
| `analysis_item` | 42 | 🟡 ORTA | kurum_id mapping |
| `tows_matrix` | 7 | 🟡 ORTA | kurum_id mapping |
| `deger` | 15 | 🟡 ORTA | kurum_id mapping |
| `etik_kural` | 4 | 🟡 ORTA | kurum_id mapping |
| `kalite_politikasi` | 1 | 🟡 ORTA | kurum_id mapping |
| `strategic_plan` | 1 | 🟡 ORTA | kurum_id mapping |
| `project` | 15 | 🟡 ORTA | kurum_id + user_id mapping |
| `task` | 72 | 🟡 ORTA | project_id + user_id mapping |
| `activity` | 90 | 🟡 ORTA | user_id mapping |
| `strategy_process_matrix` | 114 | 🟡 ORTA | sub_strategy_id + process_id mapping |
| `surec_alt_stratejiler` | 157 | 🟡 ORTA | surec_id + alt_strateji_id mapping |
| `surec_uyeleri` | 52 | 🟡 ORTA | surec_id + user_id mapping |
| `surec_liderleri` | 44 | 🟡 ORTA | surec_id + user_id mapping |
| `process_owners` | 29 | 🟡 ORTA | process_id + user_id mapping |
| `strategy_map_link` | 23 | 🟡 ORTA | source_id + target_id mapping |
| `raid_item` | 5 | 🟡 ORTA | project_id + user_id mapping |
| `audit_log` | 606 | 🟢 DÜŞÜK | user_id mapping |
| `notification` | 2798 | 🟢 DÜŞÜK | user_id mapping |
| `user_activity_log` | 344 | 🟢 DÜŞÜK | user_id mapping |
| `note` | 1 | 🟢 DÜŞÜK | user_id mapping |
| `feedback` | 2 | 🟢 DÜŞÜK | user_id mapping |
| `user_dashboard_settings` | 2 | 🟢 DÜŞÜK | user_id mapping |

---

## ESKI DB TABLO ŞEMALARI (Önemli Alanlar)

### kurum
`id, kisa_ad, ticari_unvan, faaliyet_alani, adres, il, ilce, email, web_adresi, telefon, calisan_sayisi, sektor, vergi_dairesi, vergi_numarasi, logo_url, amac, vizyon, stratejik_profil, stratejik_durum, created_at, silindi, deleted_at, deleted_by`

### user
`id, username, email, password_hash, first_name, last_name, phone, title, department, sistem_rol, surec_rol, kurum_id, profile_photo, created_at, silindi`

### ana_strateji
`id, kurum_id, code, ad, name, aciklama, created_at, perspective, bsc_code, weight`

### alt_strateji
`id, ana_strateji_id, code, ad, name, target_method, aciklama, created_at, weight`

### surec
`id, kurum_id, code, ad, name, weight, dokuman_no, rev_no, durum, ilerleme, baslangic_tarihi, bitis_tarihi, aciklama, created_at, silindi, parent_id`

### surec_performans_gostergesi
`id, surec_id, ad, aciklama, kodu, hedef_deger, olcum_birimi, periyot, agirlik, direction, gosterge_turu, basari_puani, created_at`

### bireysel_performans_gostergesi
`id, user_id, ad, aciklama, kodu, hedef_deger, gerceklesen_deger, olcum_birimi, periyot, agirlik, baslangic_tarihi, bitis_tarihi, durum, kaynak, kaynak_surec_id, kaynak_surec_pg_id, created_at`

### performans_gosterge_veri
`id, bireysel_pg_id, yil, veri_tarihi, ceyrek, ay, hafta, hedef_deger, gerceklesen_deger, durum, durum_yuzdesi, aciklama, user_id, created_at`

---

## MIGRATION SCRIPT YAPISI

```python
# migrate_old_data.py
# Çalıştırma: flask shell < migrate_old_data.py
# VEYA: python migrate_old_data.py

import sqlite3
from datetime import datetime
from app import create_app, db

OLD_DB_PATH = 'docs/kokpitim_yedek.db'

app = create_app()

def migrate():
    old_conn = sqlite3.connect(OLD_DB_PATH)
    old_conn.row_factory = sqlite3.Row
    
    # ID mapping sözlükleri — eski ID → yeni ID
    kurum_map = {}
    user_map = {}
    ana_strateji_map = {}
    alt_strateji_map = {}
    surec_map = {}
    surec_pg_map = {}
    bireysel_pg_map = {}
    project_map = {}
    task_map = {}
    
    stats = {}  # Her tablo için {tablo: {migrated:0, skipped:0, error:0}}
    
    with app.app_context():
        # ADIM 1: kurum
        # ADIM 2: user (kurum_map kullan)
        # ADIM 3: ana_strateji (kurum_map)
        # ADIM 4: alt_strateji (ana_strateji_map)
        # ADIM 5: surec (kurum_map)
        # ADIM 6: surec_performans_gostergesi (surec_map)
        # ADIM 7: bireysel_performans_gostergesi (user_map, surec_map, surec_pg_map)
        # ADIM 8: performans_gosterge_veri (bireysel_pg_map, user_map)
        # ... diğer tablolar
        
        # Her adımda:
        # - Duplicate kontrolü: email, kisa_ad, code gibi unique alanlara göre
        # - Hata varsa o kaydı atla, logla, devam et
        # - Transaction: her tablo için db.session.commit() veya rollback()
        
        print("\n=== MİGRASYON RAPORU ===")
        for tablo, s in stats.items():
            print(f"{tablo}: {s['migrated']} taşındı, {s['skipped']} atlandı, {s['error']} hata")

if __name__ == '__main__':
    migrate()
```

---

## ÖNEMLİ NOTLAR

### Mevcut DB Model Yapısı
- Yeni modeller `app/models/` altında (Tenant, Role, User, Process, ProcessKpi vb.)
- Eski DB modelleri farklı alan adları kullanıyor — mapping gerekli
- Örnek: eski `sistem_rol` → yeni `role_id` (Role tablosundan bul)
- Örnek: eski `silindi` → yeni `is_active` (tersine çevir)

### Duplicate Kontrolü Kuralları
- `kurum`: `kisa_ad` unique kontrol
- `user`: `email` unique kontrol
- `ana_strateji`: `kurum_id + code` unique kontrol
- `alt_strateji`: `ana_strateji_id + code` unique kontrol
- `surec`: `kurum_id + code` unique kontrol
- `surec_performans_gostergesi`: `surec_id + kodu` unique kontrol

### Kritik Uyarılar
1. Migration'ı önce **test ortamında** çalıştır
2. Migration öncesi mevcut DB'nin yedeğini al
3. `performans_gosterge_veri` (1632 kayıt) en büyük tablo — batch işle (100'er kayıt)
4. `notification` (2798 kayıt) — isteğe bağlı, önceliği düşük
5. Şifre hash'lerini (`password_hash`) aynen koru, değiştirme

---

## BAŞARILI MİGRASYON KONTROLÜ

Migration sonrası şu sorguları çalıştır:

```python
# Kontrol scripti
print("Kurum sayısı:", Kurum.query.count())
print("User sayısı:", User.query.count())  
print("Ana Strateji:", AnaStrateji.query.count())
print("Süreç:", Surec.query.count())
print("Süreç PG:", SurecPerformansGostergesi.query.count())
print("Bireysel PG:", BireyselPerformansGostergesi.query.count())
print("PG Veri:", PerformansGostergeVeri.query.count())
```

Beklenen minimum değerler:
- Kurum: ≥ 10
- User: ≥ 36
- Ana Strateji: ≥ 33
- Süreç PG: ≥ 273
- Bireysel PG: ≥ 204
- PG Veri: ≥ 1632
