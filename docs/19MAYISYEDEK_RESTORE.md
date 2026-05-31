# 19mayisyedek — Geri Dönüş Noktası

**Tarih:** 2026-05-19  
**Dal:** `19mayisyedek`  
**Commit:** `0192ee5`  
**Etiket:** `backup-19mayisyedek` (commit `0192ee5` — dal adı `19mayisyedek` ile karışmaması için)

Bu anlık görüntü, mimari iyileştirmelere başlamadan önceki tam kod durumunu saklar.

---

## Hızlı geri dönüş

PowerShell (proje kökünde):

```powershell
.\scripts\ops\restore_19mayisyedek.ps1
```

veya elle:

```powershell
cd C:\kokpitim
git checkout 19mayisyedek
git reset --hard 0192ee5
```

> `.env` ve `instance/` silinmez (`git clean` istisnalı).

---

## Ne içerir?

- Commit edilmiş tüm uygulama kodu (marketing, k_radar birleştirme, plan_year düzeltmeleri öncesi/sonrası WIP dahil)
- **Dahil değil:** `Yedekler/*.zip`, `backups/`, `.claude/` (yerel dosyalar)

---

## main'e geri dönmek

```powershell
git checkout main
```

İyileştirme commit'leri `main` üzerinde devam eder; `19mayisyedek` dalı donmuş referans olarak kalır.
