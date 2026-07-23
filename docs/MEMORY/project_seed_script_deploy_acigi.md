---
name: project-seed-script-deploy-acigi
description: "Kod deploy'u DB seed çalıştırmaz — Test'te 2026-07-05'te paket/modül eksikliği bu yüzden yaşandı, kalıcı çözüm docs'a işlendi"
metadata: 
  node_type: memory
  type: project
  originSessionId: 1c201b8f-7e54-4158-89cc-c16526a01fc7
---

Kod deploy'u (git pull / tarball + restart) yalnızca dosyaları günceller; `scripts/seed_*.py` script'lerini
OTOMATİK çalıştırmaz. 2026-07-05'te Test ortamında `/admin/packages` sadece 1 paket gösterdi (yerelde 4) —
kök neden `seed_l2_module_gating.py` ve `seed_l2_paketler.py`'nin Test DB'sinde hiç çalıştırılmamış olmasıydı.
Aynı gün Demo'da da aynı eksiklik teyit edilip aynı 2 seed çalıştırıldı (Demo'da da sequence drift vardı).

**Why:** Seed script'leri idempotent ve tek-seferlik "DB'ye veri ekle" işlemleri; git commit'e girmeleri
onları otomatik "uygulanmış" yapmıyor — her ortam için ayrı elle tetiklenmesi gerekiyor. Bu görünmez bir
boşluk: kod aynı görünür ama DB verisi farklı kalır.

**How to apply:** Artık kalıcı süreç var:
- `docs/kontrol/seed_calistirma_kaydi.md` — hangi seed script'i hangi ortamda (Yerel/Test/Demo/Yayın)
  çalıştırıldığının kaydı. Yeni seed yazılınca satır eklenir; bir ortamda çalıştırılınca işaretlenir.
- `docs/SUNUCU-GUNCELLEME-REHBERI.md` §8 madde 4 — deploy sonrası doğrulama listesine "seed senkron
  kontrolü" eklendi: kayıtta `?`/boş olan script'leri hedef ortamda `--dry-run` ile kontrol et.
- Yan tuzak: seed çalıştırırken "duplicate key / sequence" hatası çıkabilir (PG sequence drift) —
  önce `sync_pg_sequence_if_needed(tablo, 'id')` çağır, sonra seed'i tekrar dene.

İlgili: [[project_l_paketleri_deploy_kurali]], [[project_kart_sistemi_mimari]]
