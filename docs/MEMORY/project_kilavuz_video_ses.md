---
name: project_kilavuz_video_ses
description: Kılavuz videoları artık mp4 + edge-tts sesli anlatı; ffmpeg/truststore kurulum gerçekleri ve bu makinedeki SSL kesme tuzağı
metadata: 
  node_type: memory
  type: project
  originSessionId: 0265ef0d-566e-4066-930c-3200531599d0
---

Kılavuz & Video Oluşturucu (Senaryo v3, Bölüm 1) videoları artık **sesli mp4** üretir. İlgili: [[project_kilavuz_dokumantasyon]].

**Akış:** Playwright webm kaydeder → her çekim adımına bağlı "beat" anlatısı edge-tts ile mp3'e çevrilir → ffmpeg `adelay`+`amix` ile her ses kendi zaman offset'inde videoya bindirilir → H.264+aac mp4. Ses süresi adımın ekran süresini sürer (senkron). Beat metinleri **senaryoyla tek dosyada**: `docs/kılavuz/yenitomofil_senaryo_taslagi.md` (v4.0 — her alt-bölümde adım + 🎙️ beat yan yana). Ses: `tr-TR-AhmetNeural`. Kod karşılığı: executor `BEATS` sözlüğü (ID'ler birebir).

**Bu makineye özgü kurulum gerçekleri (non-obvious):**
- **ffmpeg:** Playwright'in paket içi ffmpeg'i SADECE libvpx (webm) içerir — mp4/H.264 ÜRETEMEZ. Tam ffmpeg ayrı kuruldu: `%LOCALAPPDATA%\ffmpeg\ffmpeg-8.1.1-essentials_build\bin\ffmpeg.exe` (gyan.dev essentials). `_find_ffmpeg()` glob ile bulur; ffprobe yanında.
- **SSL kesme tuzağı:** Bu makinede kurumsal SSL interception/proxy var. Python certifi MITM kök sertifikasını TANIMAZ → edge-tts `CERTIFICATE_VERIFY_FAILED` verir; **winget de** aynı kökten `0x8a15005e` cert mismatch verir. Çözüm: `truststore` paketi + `truststore.inject_into_ssl()` (Windows sertifika mağazasını kullandırır) — edge-tts importundan ÖNCE çağrılmalı. `_generate_beats()` içinde yapılıyor. (PowerShell `Invoke-WebRequest` ve tarayıcı zaten Windows mağazasını kullandığı için çalışır.)
- **Bağımlılıklar:** `requirements-ai.txt` → playwright, edge-tts, truststore (opsiyonel/yerel-only).

**Çalışma sınırı:** Çekim rotası `_is_local` korumalı — yalnız Yerel'de çalışır; Test/Demo/Yayın'da ffmpeg/edge-tts GEREKMEZ. Ses/edge-tts/internet yoksa sessiz mp4'e güvenli düşüş (akış bozulmaz).

**Yapı kararı:** Bölüm 1 = tek video `1_giris_kurum_kullanici.webm/.mp4` (1.1 Giriş, 1.2 Kurum Yönetimi, 1.3 Kullanıcılar, 1.4 Roller). SP/Süreç/Proje/K-Radar kodu `_INCLUDE_DEFERRED = False` ile korunur ama çalışmaz (silinmez — sırası gelince açılacak).
