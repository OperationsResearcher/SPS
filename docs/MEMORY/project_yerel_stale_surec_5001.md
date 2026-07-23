---
name: project_yerel_stale_surec_5001
description: "Yerelde 5001'de çift/stale python süreci 500'e yol açar; restart öncesi netstat ile kontrol"
metadata: 
  node_type: memory
  type: project
  originSessionId: 0265ef0d-566e-4066-930c-3200531599d0
---

Windows yerelde `py app.py` (Flask debug reloader) **Ctrl+C ile her zaman tam ölmez** — reloader child süreci hayatta kalabilir. Werkzeug `SO_REUSEADDR` kullandığı için aynı 5001 portuna İKİNCİ bir süreç de bağlanabilir; OS bağlantıyı eski (stale, eski kodu yükləmiş) sürece yönlendirir. Sonuç: diskte kod düzeltilmiş olsa bile tarayıcı eski koddan 500 alır ve "düzelmiyor" sanılır.

**Why:** 2026-06-01'de login 500 saatlerce "kod bug'ı" sanıldı; gerçekte diskteki kod sağlamdı (3 yöntemle 302 reprodüce edildi). Sebep 5001'i dinleyen iki süreçti (PID'ler `netstat`'ta görüldü).

**How to apply:** Login/davranış "değişiklikten sonra düzelmiyor" derken önce süreçleri doğrula:
- `netstat -ano | grep ":5001" | grep LISTEN` → birden fazla satır varsa stale süreç var
- `taskkill //F //PID <pid>` ile temizle, sonra TEK temiz sunucu başlat
- Test client (TESTING=True) CSRF'i kapatıp cookie'yi tuttuğu için gerçek tarayıcı davranışını maskeler; gerçek HTTP reprodüksiyonunda Secure session cookie'yi elle gönder (Chromium 127.0.0.1'i secure context sayar, requests saymaz).
