---
name: project-encryption-key-deploy-riski
description: ENCRYPTION_KEY eksikliği 3 ortamda da (yerel/Test/Yayın) sırayla patladı — her yeni ortama kod deploy ederken bu env değişkeni MUTLAKA önceden kontrol edilmeli
metadata: 
  node_type: memory
  type: project
  originSessionId: 1c201b8f-7e54-4158-89cc-c16526a01fc7
---

`app/utils/encryption.py` — production'da (`FLASK_ENV=production`) `ENCRYPTION_KEY`
ortam değişkeni yoksa `RuntimeError` fırlatıp uygulamanın başlamasını engelliyor
(bilinçli tasarım, sessiz veri bozulmasını önlemek için). Bu üç kez farklı ortamda
sorun oldu:

1. **Yerel** (2026-07-06): `.env`'de hiç yoktu, her process restart'ında rastgele
   geçici anahtar üretiliyordu → SMTP şifresi kaydedilip okunamıyordu.
2. **Test** (aynı gün, dolaylı): benzer risk teşhis edildi.
3. **Yayın** (2026-07-07): 155 commit'lik büyük bir kod deploy'u sonrası container
   `RuntimeError: ENCRYPTION_KEY ortam değişkeni üretimde zorunludur` ile crash-loop'a
   girdi, `/health` 404 döndü, ~15-20 dakika prod-down yaşandı. Kök neden: eski kod
   bu değişkeni gerektirmiyordu, yeni kod (email_config.py şifreleme) gerektiriyor,
   ama Yayın'ın `.env`'i deploy öncesi hiç güncellenmemişti.

**Why:** Bu değişken kodun DAVRANIŞ gereksinimidir ama `.env` dosyaları deploy
sürecinin bir parçası olarak otomatik senkronize edilmiyor — kod ilerledikçe yeni
zorunlu env değişkenleri ortaya çıkabiliyor, deploy script'i bunu kontrol etmiyor.

**How to apply:** Yayın'a (veya Test/Demo'ya) büyük bir kod deploy'u yapmadan önce:
- Deploy edilecek commit aralığında `app/utils/encryption.py`, `config.py` gibi
  "ortam değişkeni zorunlu" mantığı olan dosyalarda değişiklik var mı kontrol et.
- Deploy sonrası container'ın gerçekten ayakta kaldığını (sadece `docker ps` ile
  "Up" değil, birkaç dakika sonra tekrar kontrol ederek "Restarting" döngüsüne
  girmediğini) doğrula — `oracle_safe_deploy.sh` şu an bunu otomatik yakalamıyor.
- `docker restart` env dosyası değişikliğini YENİDEN OKUMAZ (bilinen Docker
  davranışı) — env/`.env` değiştiyse container'ı silip yeniden oluşturmak şart.

İlgili: [[project_test_demo_image_baked_gercegi]] (benzer "restart yetmez" tuzağı)
