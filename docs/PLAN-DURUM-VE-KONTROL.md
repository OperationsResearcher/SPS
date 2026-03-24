# Plan Durumu ve Kontrol Listesi

> **Kaldığımız yer:** VM PostgreSQL geçişi — commit yapıldı, push ve VM adımları bekliyor.

---

## Kaldığımız Yer (2026-03-24)

| Adım | Durum |
|------|--------|
| Yerel PostgreSQL geçiş | ✅ Tamamlandı |
| Veri taşıma, giriş testi | ✅ Tamamlandı |
| Git commit | ✅ Tamamlandı |
| Git push | ⏳ Sizin yapmanız gerekiyor |
| VM'de migration script | ⏳ Push sonrası `git pull` + script çalıştırma |

---

## Plan Kontrolü — Tespit Edilen Noktalar

### 1. Rehber Tutarsızlığı (3.5)

- **Durum:** Bölüm 3.5 "Veri Taşıma" pgloader kullanıyor; `vm_postgres_migration.sh` ise `sqlite_to_postgres.py` kullanıyor.
- **Etki:** 3.0 tek komutla geçiş kullanılıyorsa sorun yok. Elle adım adım gidilirse 3.5 yanıltıcı.
- **Öneri:** 3.5'i "Python script (önerilen)" olarak güncellemek veya 3.0'a referans vermek.

### 2. FLASK_APP (VM Script)

- **Durum:** `flask db upgrade` çalıştırılırken `FLASK_APP` set edilmiyor. Projede `app.py` var; Flask varsayılan olarak bulabilir.
- **Etki:** Çoğu ortamda çalışır, bazı kurulumlarda sorun çıkabilir.
- **Öneri:** Güvenlik için `-e FLASK_APP=app.py` eklenebilir.

### 3. VM Path Varsayımı

- **Durum:** Script `APP_DIR=/home/kokpitim.com/public_html` varsayıyor.
- **Etki:** Farklı path kullanılıyorsa `APP_DIR` ile override edilmeli.
- **Öneri:** Rehberde `APP_DIR` değişkeninin nasıl kullanılacağı belirtilebilir.

### 4. PostgreSQL systemctl Kontrolü

- **Durum:** `systemctl is-active postgresql` root olmadan çalışır; script genelde normal kullanıcı ile çalıştırılıyor.
- **Etki:** Düşük; kontrol amacıyla kullanılıyor.

### 5. Docker Bridge IP (172.17.0.1)

- **Durum:** Bazı Linux/Docker kurulumlarında bridge IP farklı olabilir.
- **Öneri:** `PG_HOST` env ile override edilebilir; rehberde `ip addr show docker0` ile kontrol önerisi mevcut.

---

## Kritik Sorun Yok

Yukarıdaki maddeler iyileştirme niteliğinde; planı engelleyecek kritik bir hata tespit edilmedi. VM migration script, yerelde test edilen `sqlite_to_postgres.py` ile aynı mantığı kullanıyor.

---

## Sonraki Adımlar

1. Uygulama düzeltmelerini yapın.
2. `git push origin main` ile değişiklikleri gönderin.
3. VM'de: `git pull` → `PG_PASSWORD='...' ./scripts/vm_postgres_migration.sh`
