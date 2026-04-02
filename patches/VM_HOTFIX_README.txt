VM-only hotfix (origin/main ile uyumlu; yerel büyük değişikliklerden bağımsız)

Patch dosyası: patches/0001-hotfix-vm-Cloudflare-524-guvenlik-basliklari-ProxyFi.patch
(Utf-8 bozulmasın diye `git format-patch` ile üretildi.)

GitHub branch: hotfix/vm-cloudflare-524  (origin’a push edildi)
Baz commit: 9fb14bb

İçerik:
- app/utils/security.py — request.url / Host SecurityError (Cloudflare 524)
- app/__init__.py — ProxyFix (X-Forwarded-Proto)
- config.py — RATELIMIT_STORAGE_URL varsayılan memory://; SQLALCHEMY_ENGINE_OPTIONS
- Dockerfile — FLASK_ENV, TRUST_PROXY, gunicorn timeout

VM'de uygulama:
  cd /home/kokpitim.com/public_html
  git fetch origin
  git checkout hotfix/vm-cloudflare-524
  git pull origin hotfix/vm-cloudflare-524
  (mevcut deploy: docker build + run)

Patch ile (VM kodu 9fb14bb ise):
  git apply --check 0001-hotfix-vm-Cloudflare-524-guvenlik-basliklari-ProxyFi.patch
  git apply 0001-hotfix-vm-Cloudflare-524-guvenlik-basliklari-ProxyFi.patch

Not: VM başka committteyse patch elle uyarlanmalı veya önce origin/main ile hizalanır.

Worktree (Cursor dışı): C:\kokpitim-hotfix-vm — branch hotfix/vm-cloudflare-524
Kaldırmak için: cd C:\kokpitim && git worktree remove C:\kokpitim-hotfix-vm
