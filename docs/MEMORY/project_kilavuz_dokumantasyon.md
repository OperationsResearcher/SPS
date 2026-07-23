---
name: project_kilavuz_dokumantasyon
description: Kılavuz & video çekme işi dokümantasyonu docs/kılavuz/ altında toplanır (sabit yönerge)
metadata: 
  node_type: memory
  type: project
  originSessionId: 0265ef0d-566e-4066-930c-3200531599d0
---

**Sabit yönerge (KURALLAR-MASTER §9):** Kullanım kılavuzu & video çekme (Kılavuz & Video Oluşturucu) işiyle ilgili **her türlü dokümantasyon `docs/kılavuz/` klasöründe** toplanır. Yeni senaryo/plan/metin oraya `.md` eklenir.

**Why:** Uzun soluklu bir iş; dağınık olmasın, tek yerde tutulsun (kullanıcı isteği, 2026-06-09).

**How to apply:**
- Klasör indeksi: `docs/kılavuz/README.md`. Ana senaryo: `docs/kılavuz/yenitomofil_senaryo_taslagi.md`.
- Senaryo değişikliği **önce burada yazılır, mutabakat sağlanınca koda yansıtılır** — yani önce taslakta mutabık kal, sonra kodla.
- İlgili KOD yerinde durur (path bağımlılığı): `app/services/kilavuz_olusturucu_executor.py`, `ui/templates/platform/admin/kilavuz_olusturucu.html`, `docs/compile_guide.py`, `docs/user_guide_master.html`.
- Üretilen binary (PDF/video/img) commit edilmez (.gitignore'da).

İlgili kod incelemesi/düzeltmeleri: Kılavuz executor'un seçicileri hata-kontrol senaryolarındaki doğrulanmış id'lerle hizalandı (sp-modal-vision, btn-surec-add, /k-radar vb.).
