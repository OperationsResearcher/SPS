# 11 — Düzeltme Eylem Planı (Teknik)

> Tarih: 2026-10-10 · Kaynak: 02, 03, 04 raporları + 10 bağımsız denetimin düzeltmeleri.
> Etiketler: **[D]** doğrulanmış bulgu · **[O]** olası risk · **[İ]** iyileştirme.
> Efor tahminleri tek geliştirici varsayımıyladır, taahhüt değildir.

## Ön koşul — Yayın'da ne çalışıyor? (P0-0)

Yerel çalışma ağacında ~100 commit edilmemiş değişiklik var. Bazı düzeltmeler (`app/utils/scheduler_leader.py`, `outbound_guard.py`) git'te izlenmiyor. Bu yüzden yerelde kapanmış görünen bulgular Yayın'da büyük olasılıkla açık. Aşağıdaki her maddenin "kapandı" sayılması, Yayın'a ulaşmasına bağlıdır.

| Adım | Kabul kriteri |
|---|---|
| Çalışma ağacını gözden geçir, dalda commit et | `git status` temiz; izlenmeyen `app/utils/*.py` dosyaları commit'te |
| Yayın imajının commit'ini tespit et | Yayın'daki commit hash'i yazılı kayıtta |
| Yayın env teyidi: `REDIS_URL`, `GUNICORN_WORKERS`, `KOKPITIM_DEMO_MODE` | Değerler (sır olmadan) kayıtta |

## P0 — Güvenlik, veri kaybı, bütünlük

| ID | Bulgu | Kanıt | Çözüm | Efor | Doğrulama |
|---|---|---|---|---|---|
| P0-1 | **[D]** Kurumsal dosya indirme ve silme uçlarında kiracı kontrolü yok (GV-001, düzeltilmiş) | `api/routes_files.py:413-433`, `:436`; `ProjectFile` modelinde tenant alanı yok | Uçları kaldır (doküman merkezi zaten 501) ya da proje→tenant zinciriyle kontrol ekle | 0,5 gün | Başka kurumun `file_id`'si ile 403/404 dönen test |
| P0-2 | **[O]** Legacy `api/` ve `main/` yüzeyinde sistematik IDOR taraması yapılmadı | 176 `get_or_404`'ün yalnız örneklemi incelendi | Desen taraması: `get_or_404` + tenant filtresi yok; her bulgu için test | 2-3 gün | Tarama listesi + çok kiracılı test paketi |
| P0-3 | **[D]** Off-site yedek kodda yok; restore tatbikatı yok (PA-003) | `oracle_safe_deploy.sh:10,19`; `yedekleme_service.py:39,293` | Şifreli günlük dump'ı ikinci bölgeye/nesne depolamaya kopyala; aylık restore tatbikatı | 1-2 gün | Off-site'tan Test'e restore edilip kayıt sayıları karşılaştırılır |
| P0-4 | **[D]** LLM gateway kurum `base_url` değerini doğrulamıyor, SSRF (GV-002) | `app/services/llm_gateway.py:107, 411`; `outbound_guard` var ama çağrılmıyor | `outbound_guard`'ı gateway'e bağla; iç IP/metadata adreslerini engelle | 0,5 gün | `http://169.254.169.254` base_url ile reddedilen test |
| P0-5 | **[D]** Zamanlayıcı lider kilidi Yayın'da yok (PA-001, düzeltilmiş) | Dockerfile 8 worker; kilit `app/__init__.py:629`'da ama izlenmeyen dosyada | P0-0 ile commit + deploy | P0-0'a dahil | Yayın log'unda gece işinin tek kez çalıştığı görülür |

## P1 — Temel işlevler

| ID | Bulgu | Çözüm | Efor | Doğrulama |
|---|---|---|---|---|
| P1-1 | **[D]** Tam test paketi bitmiyor, CI kilitli (KQ-002) | `pytest-timeout` ekle, takılan testi bul; CI faturasını aç veya yerel ön-commit koşusu | 1 gün | 889 testin özet satırı |
| P1-2 | **[O]** TestingConfig'te `TENANT_GUARD_MODE=off`; izolasyon testleri guard'ı doğrulamıyor olabilir | İzolasyon testlerini guard açık koştur | 0,5 gün | Guard kapatılınca kırmızıya dönen test |
| P1-3 | **[D]** Deploy'da sağlık kapısı ve otomatik geri alma yok (PA-004) | Health başarısızsa önceki imaja dön | 1 gün | Bozuk imajla Test'te tatbikat |
| P1-4 | **[D]** 185 pip-audit bulgusu, kilitsiz requirements (GV-004) | Lock dosyası; socketio/engineio/werkzeug/urllib3/pypdf güncelle | 1-2 gün | `pip-audit` temiz veya istisnalar gerekçeli |
| P1-5 | **[O]** Rate limit ve cache `memory://`'ye düşebiliyor (GV-008, PA-010) | Önce Yayın'da Redis bağlı mı ölç; değilse bağla | 0,5 gün | `/health` Redis durumunu raporlar |
| P1-6 | **[O]** 8 sync worker, ağır rapor istekleri tıkayabilir (PA-006) | gthread worker + rapor uçlarına timeout/önbellek | 1 gün | Yük testi |
| P1-7 | **[D]** Şifremi unuttum akışı yok | E-posta tokenlı sıfırlama | 1 gün | Uçtan uca test |
| P1-8 | **[D]** ENCRYPTION_KEY rotasyon/yedek prosedürü yok (GV-012) | Anahtar yedeği ayrı kasada; rotasyon belgesi | 0,5 gün | Belge + tatbikat |

## P2 — Kalite ve sürdürülebilirlik

- **[D] Açık yönlendirme** `app/routes/auth.py:95-106` (GV-006). `/\evil.com` biçimini reddet. 0,5 gün.
- **[D] 63 `@csrf.exempt`** (GV-003). API anahtarı yazan POST'ları korumaya al. 1 gün.
- **[D] Demo bayrağı** varsayılanı kapalı, `config.py:56` (GV-007, P1'den indirildi). Yayın env teyidi yeterli.
- **[D] 47 `except Exception: pass`** (KQ-003). Hepsine `app.logger.error` ekle. `auth.py:36` düşük etkili. 1 gün.
- **[D] N+1** `process_performance_service.py:61-93, 317-333` (PA-007). `score_engine_service`'teki toplu yükleme desenini uygula. 1 gün.
- **[İ] /health derinleştirme** (PA-011). Redis, disk, son yedek yaşı. Dış uptime izleme. 0,5 gün.
- **[İ] Migration disiplini** (PA-012). `alembic heads/check` CI'a. `_disabled` revizyonları arşivle. 0,5 gün.
- **[İ] CSP `unsafe-inline`** (GV-005). Nonce'a geçiş, kademeli. 3+ gün.
- **[O] Hard delete** (KQ-005). Denetçiye göre genelleme kanıtsız. Yalnız `strategy_api.py:440` ve `pages.py:508,904` tek tek incelenmeli.
- **[İ] Dosya yüklemede antivirüs ve `static/uploads` doğrudan servis** (GV-010). nginx ayarı incelenmeli.

## P3 — İsteğe bağlı

- `Kalder/` SİLİNMEZ/TAŞINMAZ (kullanıcı kararı); yalnız `.dockerignore` ve tarama hariç tutma (KQ-001, denetçi notu).
- `ruff.toml` exclude (KQ-009). Büyük dosyaları böl (KQ-007). Native `alert()` kalıntıları (KQ-004).
- Skor motorunda O(n²) `next()` (PA-008). Bileşik indeks EXPLAIN ile (PA-009). Root olmayan Docker kullanıcısı (PA-013).
- Belgelerin güncellenmesi: route sayısı 851, DB PostgreSQL, HGS kaldırıldı.
