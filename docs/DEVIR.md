# DEVİR — Aktif durum özeti

> **Bu dosya kısadır.** Sonraki Claude ilk girişte buraya bakar, gerçek detay için `docs/TASKLOG.md` + `docs/KURALLAR-MASTER.md` + `docs/ERTELENEN-ISLER.md`.
> Son güncelleme: 2026-05-26

---

## 1. Bilmen gereken kavramlar (ezber)

- **Üç ortam:** Yerel (127.0.0.1:5001) → Test (test.kokpitim.com) → Yayın (www.kokpitim.com). "VM"/"production VM" gibi belirsiz terim kullanma — bkz. `KURALLAR-MASTER §8`.
- **Branch disiplini:** main'e doğrudan commit yok. Her iş `claude/<konu>` dalında. Merge/push/deploy kullanıcı isteyince.
- **Push/deploy:** Otomatik değil. Kullanıcı "push" / "yayına çıkalım" demeden yapılmaz.
- **`Yerel / Test / Yayın`** üçlüsü dışında "VM" deme.

---

## 2. Son git durumu

- **Branch:** `main` (yerel + origin senkronize)
- **Son commit:** `d0f628d feat(env): Test ortamı kurulumu + üç-ortam terminolojisi + CSP fix`
- **Açık dallar:**
  - `claude/kule-yardimci-sistemi` — askıda (bkz. `ERTELENEN-ISLER.md` E1)
  - `claude/ems-data-import` — main'e merge edildi, ama branch silinmedi

---

## 3. Ortamların durumu

### Yerel (127.0.0.1:5001)
- DB: PG `kokpitim_db` (Tomofil reconcile dahil son hal)
- Çalışıyor, dev server.

### Test (https://test.kokpitim.com)
- ✅ Aktif, SSL ile
- Oracle VM `/opt/kokpitim-test/` · port 5050 · DB `kokpitim_test_db`
- Container: `kokpitim-test-web` (host network)
- Yereldeki tüm veri + .env yüklü
- Kurulum scripti: `scripts/ops/oracle/setup_test_env.sh`

### Yayın (https://www.kokpitim.com)
- ✅ Aktif (eskiden beri çalışıyor)
- Oracle VM `/opt/kokpitim/` · port 5000 · DB `kokpitim_db`
- ⚠️ Kod yereldekine göre **geride**. Son değişiklikler henüz yayına gitmedi.

---

## 4. Bekleyen önemli işler

1. **Yayın'a deploy** — Yereldeki son hal (EMS import, Tomofil reconcile, K-Vektör 100 ölçeği, CSP fix, üç ortam terminolojisi) test'te doğrulandı; yayın'a alınmak için kullanıcı kararı bekliyor.
2. **Kule yardımcı sistemi** — askıda, `ERTELENEN-ISLER.md E1`. UI stabilleşince devam.
3. **Teknik borç:**
   - `task_predecessors` çift tanımı (`app/models/portfolio_project.py` vs `models/project.py`) — yerelde sessiz, VM clone'da kırılıyor
   - Yayın VM'inin kodu yereldekine göre eski (örn. `micro/core/launcher.py` marketing redirect içeriyor)
4. **Tomofil eksik kodları** — `1.B, 1.C, 4.B, 4.C, 5.C, 6.C` alt strateji kodları markdown'da var ama DB'de yok (reconcile sırasında script de yakaladı)

---

## 5. Aktif veri / önemli kişiler

- **EMS** (id=28) — Eskişehir Makine Sanayii A.Ş., 21 kullanıcı (C-Suite + YK + tesis müdürü), 12 süreç, 6 strateji, 24 OKR
- **Tomofil** (id=27) — Tomofil Otomotiv Sanayi, 97 kullanıcı (96'sı @kokpitim.com gerçek mail), 14 süreç, 6 strateji, 18 alt, 55 girişim, 48.283 KpiData
- **Kayseri Model Fabrika** (id=16) — Salih Yalçın kurum yöneticisi
- **Default Corp** (id=1) — Talat Konuk (platform yöneticisi, kokpitim ekibi)

---

## 6. Açık secret/credential dosyaları (yerel diskte)

- `.env` — GEMINI, cPanel token, vs. (gitignore'da)
- `data/cpanel_email_log.csv` — Tomofil cPanel mail hesapları (gitignore yok ama hassas)
- `data/tomofil_photo_rename_log.csv` — foto-kullanıcı eşleşmesi
- `data/ems_import_log/users_created.csv` — EMS geçici şifreleri (artık `EmS_2626`'ya değişti)

---

## 7. Bir sonraki oturuma "ne yapsak?" sorusu için aday liste

- Yayın'a deploy (test → yayın geçişi)
- Kule sistemini geri açmak (UI stabilleştiyse)
- `task_predecessors` çift tanımını temizlemek
- EMS için kullanıcı fotoğrafları (henüz yapılmadı)
- Yeni özellik talepleri

---

**Sonraki Claude:** `head -80 docs/TASKLOG.md` çalıştır, son 3 task'ı oku, `git status`'a bak. Bu dosya zaten kısa özet — ayrıntı için TASKLOG.
