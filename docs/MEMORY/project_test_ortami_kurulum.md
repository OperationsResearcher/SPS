---
name: project-test-ortami-kurulum
description: "Test ortamı (test.kokpitim.com) 2026-05-26'da kuruldu; kullanım ve mevcut quirks"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7e3b87f3-74ac-46ae-ac39-25ec42733a89
---

**Test ortamı 2026-05-26'da kuruldu** — `https://test.kokpitim.com/`

**Konum (Oracle VM 129.159.30.175):**
- Dizin: `/opt/kokpitim-test/app`
- `.env`: `/opt/kokpitim-test/.env` + `app/.env` (kopyası — container içeri okuyor)
- Container: `kokpitim-test-web` (image `kokpitim_test:latest`, host network, port 5050)
- DB: `kokpitim_test_db` (`kokpitim_test_user`), DB şifresi: `/opt/kokpitim-test/.db_password`
- Nginx: `/etc/nginx/sites-enabled/test.kokpitim.com.conf` → 127.0.0.1:5050
- SSL: Let's Encrypt, 2026-08-24'e kadar (otomatik yenilenir)

**Why:** Yerelden direkt yayına çıkmak risk. Test ortamı orta katman — yereldeki değişiklikleri yayın'a almadan önce gerçek prod davranışı altında doğrulamak için.

**How to apply:** Yeni özellik/değişiklik akışı: Yerel → Test → Yayın. Test'e güncelleme için kullanıcının yereldeki kodu tarball ile gönder + container restart (git pull bazı dosyalar commit edilmediği için kırık olabilir). Hızlı script: `scripts/ops/oracle/setup_test_env.sh`.

**Mevcut quirks (yereldeki ile test'in farklı çalışmasına neden olan):**
- Yerelde DEBUG=True → CSP yumuşak. Test'te FLASK_ENV=production → sıkı CSP. Yereldeki `<script src="https://cdn.tailwindcss.com">` test'te bloklanıyordu, app/__init__.py'da fix yapıldı (TASK-134).
- `task_predecessors` tablosu çift tanımlı (`app/models/portfolio_project.py` vs `models/project.py`). Yerelde sessiz, test'in **ilk clone'unda kırılıyor**. Pragmatik: yereldeki tüm app dosyalarını tarball ile aktar.
- `pyyaml` requirements.txt'te eksikti, TASK-134'te eklendi.

İlgili: [[project-uc-ortam]] (terminoloji), `docs/DEVIR.md` (aktif durum özeti).
