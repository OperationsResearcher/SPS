# 10 — Bağımsız Denetim (01–09 raporlarının spot-check'i)
Tarih: 2026-10-10 · Yöntem: salt okunur kod incelemesi (grep/sed), git durumu. Uygulama çalıştırılmadı, sunuculara erişilmedi.

**Kritik bağlam:** Çalışma ağacı commit'siz (~60 değişmiş dosya) ve **izlenmeyen yeni dosyalar** içeriyor: `app/utils/scheduler_leader.py`, `app/utils/outbound_guard.py`, `app/utils/tr_time.py` (`git status: ??`). Raporların bir kısmı bu ara durumu, bir kısmı commit'li kodu anlatıyor. Yayın'da büyük olasılıkla commit'li kod çalışıyor → yerelde "düzeltilmiş" görünen bazı bulgular Yayın'da hâlâ açıktır.

## 1. İddia doğrulama tablosu
| İddia | Kaynak | Sonuç | Kanıt / not |
|---|---|---|---|
| GV-001 listeleme IDOR | 03 | **Düzeltildi (geçersiz)** | `api/routes_files.py:284` `_api_dokuman_merkezi_olu_govde` ölü gövde; ilgili uç 501 döner. |
| GV-001 indirme IDOR | 03 | **Doğrulandı (P0)** | `api/routes_files.py:413-433`: `@api_bp.route('/dokuman-merkezi/<int:file_id>/indir')` + yalnız `@login_required`; `ProjectFile.query.get_or_404(file_id)` → tenant/proje üyeliği kontrolü yok. Blueprint kayıtlı: `app/__init__.py:615-620` (`kokpitim_project_api`). `ProjectFile` modelinde (`app/models/portfolio_project.py:360-369`) tenant/kurum alanı **yok**; yalnız `project_id` (nullable=False), `uploader_id`. Ek bulgu: kod `scope`, `file_name`, `is_active`, `deleted_at` alanlarını kullanıyor ama modelde **bu kolonlar yok** → uç büyük olasılıkla `AttributeError` → 500 döner (istismar pratikte kırık kod nedeniyle engelleniyor olabilir). Aynı durum `DELETE` ucu (`:436`) için de geçerli. Her iki halde de kaldırılmalı veya tenant kontrollü yeniden yazılmalı. |
| GV-002 SSRF (tenant LLM base_url) | 03 | **Doğrulandı** | `micro/modules/sp/routes_tenant_ai.py:67` serbest `base_url`; `app/services/llm_gateway.py:107,411` doğrudan kullanılıyor. Yeni `outbound_guard.validate_outbound_url` var ama llm_gateway'de **çağrılmıyor** (yalnız slack, k_rapor, SMTP); guard dosyası da git'te izlenmiyor. |
| GV-007 demo parolasız giriş | 03 | **Düzeltildi (önem düşürülmeli)** | `config.py:56` varsayılan `"0"` → kapalı; `demo/routes.py:74` bayrak kapalıysa 404. Risk yalnız Yayın `.env`'inde bayrak yanlışlıkla 1 ise; P1→P2. |
| PA-001 scheduler her worker'da | 04 | **Çelişkili / kısmen düzeltildi** | `Dockerfile:44` `--workers ${GUNICORN_WORKERS:-8}` doğru. Ama `app/__init__.py:629-630` artık `run_as_leader` (PG `pg_try_advisory_lock`) kullanıyor — **`scheduler_leader.py` izlenmiyor**. Commit'li/Yayın kodunda bulgu geçerli; yerelde çözülmüş, deploy edilmemiş. |
| PA-003 off-site yedek yok | 04 | **Doğrulandı (kod düzeyinde)** | `scripts/ops` ve `yedekleme_service.py`'de rclone/Object Storage/S3 adımı yok; yalnız eski GCP `scp` scriptleri. Sunucu crontab'ı görülmedi → "kodda yok" kesin, "hiç yok" operatör teyidi ister. |
| KQ-003 auth.py:36 | 02 | **Doğrulandı, önem abartılı** | `app/routes/auth.py:28-37`: audit fallback'teki logger çağrısını saran `except Exception: pass`. Kural ihlali, güvenlik etkisi düşük. P0→P2. |
| KQ-005 hard delete | 02 | **Doğrulandı, genelleme kanıtsız** | `sp/routes_analysis.py:854` atama satırı, `surec/helpers.py:136` strateji-link silme — **join/atama kayıtları**, soft delete'in anlamsız olduğu yerler. "Proje/süreç/faaliyet hard delete" bu örneklerle kanıtlanmamış; ana varlık silmeleri ayrıca taranmalı. |
| "Şifremi unuttum yok" | 05 | **Doğrulandı** | `micro/`, `app/`, `ui/` içinde forgot/reset-token/"şifremi" yok; yalnız admin `reset-password` (`routes_sub_tenants.py:255`). |
| Route sayısı 851 | 01 | **Çelişkili (belge ile)** | 01 runtime `url_map` ile 851; CLAUDE.md/SISTEM-HARITASI 891. Runtime ölçümü daha güvenilir; belge eskimiş. Yeniden ölçülmedi. |
| GV-008 / PA-010 Redis | 03/04 | **Tutarlı, önemler farklı** | Yayın'da Redis'in fiilen bağlı olduğu hiçbir raporda teyit edilmedi. |
| 05 UX bulguları (~254 sayfa, 21 sidebar öğesi, 22 sekme vb.) | 05 | **Kanıtsız** | `[D]` etiketli; kaynak `docs/ekim2026/KOKPITIM-DETAYLI-ANALIZ-EKIM2026.md`, bağımsız doğrulanmamış (05 §11 de kabul ediyor). |
| 07/08/09 pazar büyüklüğü, fiyat, senaryolar | 07-09 | **Kanıtsız (hipotez)** | Kendi etiketleriyle HİPOTEZ; satın alma niyeti/ödeme isteği verisi yok. |
| 05 KVKK "uçlar var" | 05 | **Kanıtsız (yetersiz kapsam)** | `auth.py:192,272` varlığı görülmüş; aydınlatma metni, VERBİS, saklama süresi, LLM'e yurt dışı veri aktarımı incelenmemiş. |

## 2. Ajanlar arası çelişkiler ve önerilen çözüm
1. **İlk segment:** 08 vakıf üniversitesi + belediye ↔ 05 danışman destekli KOBİ/kalite kurumu. *Çözüm:* tek kişilik ekip, self-servis kayıt ve şifre sıfırlama eksikliği ile kamu satın alma döngüsünün uzunluğu düşünülünce **danışman/KalDer ortaklığı üzerinden EFQM/ISO'lu orta ölçekli firma** ilk segment; vakıf üniversitesi ikinci deney; belediye (EKAP, referans şartı) en son.
2. **Redis:** 03 (S3 borcu, P2) ve 04 (PA-002 SocketIO, PA-010 sessiz fallback) Redis'i farklı gerekçelerle istiyor; 01 compose'da Redis var diyor, 04 Yayın'ın compose dışında `--network host` ile çalıştığını söylüyor. *Çözüm:* önce `/health`'e Redis kontrolü ekleyip Yayın'da ölç; limiter+cache+(gerekirse) SocketIO tek Redis kararı.
3. **PA-001:** 04 "lider kilidi yok" ↔ yerel ağaçta var ama izlenmiyor. *Çözüm:* "commit + deploy bekliyor" olarak yeniden sınıflandır.
4. **P0 tanımı:** 02 KQ-003'ü P0 yapıyor; etkisi düşük → P2.
5. **Route sayısı:** 01 (851) ↔ CLAUDE.md (891); masaüstü 11 uç ↔ belge "1 route". Belgeler güncellenmeli.
6. **Fiyat ↔ segment:** 09 "Başlangıç 48-96 bin TL (KOBİ)" ↔ 07 "KOBİ fiyata duyarlı, veri girecek personel yok". Başlangıç paketinin destek maliyetiyle kârlılığı hesaplanmamış.

## 3. Gözden kaçan rakip / segment
- **Kamu:** SBB yönlendirmeli SPBİS ve kurum içi strateji sistemleri, YÖKAK/akreditasyon süreç araçları; belediyelerde mevcut e-Belediye yazılım tedarikçileri (satın almada yerleşik tedarikçi engeli).
- **ERP / BI ikameleri:** Logo, Netsis, SAP SuccessFactors, Power BI tabanlı danışman çözümleri — en güçlü ikame.
- **Türk İK performans yazılımları:** bireysel karne/hedef modülüyle doğrudan çakışır (yerli İK yazılımlarının performans modülleri); 06'da incelenmemiş, isimler pazar teyidi ister.
- **Yerli QMS/ISO doküman yazılımları:** Bimser QDMS dışındakiler.

## 4. Teknik eksik alanlar
- **KVKK:** LLM sağlayıcılarına (Gemini/OpenRouter/Groq) kurum verisi gönderimi = yurt dışı aktarım; DPA/açık rıza, saklama-imha politikası, VERBİS, log'larda kişisel veri.
- **Çok kiracılı test:** izolasyon testleri var (`tests/test_tenant_isolation.py`, `test_tenant_guard.py`, `test_proje_tenant_izolasyonu.py`), ama paket tamamlanmıyor (KQ-002) ve TestingConfig'te `TENANT_GUARD_MODE=off` → testlerin guard'ı gerçekten doğrulayıp doğrulamadığı belirsiz.
- **Yedek geri yükleme tatbikatı:** otomasyon/kanıt yok; PA-005 restore tek-transaction değil.
- **Legacy `api/` ve `main/` IDOR taraması:** 03 "176 get_or_404 doğrulanamadı" diyor. GV-001 tam bu yüzeyden çıktı → aynı desen (`get_or_404` + yalnız `@login_required`) `api/routes_projects.py`, `api/routes_pm.py`, `main/routes/*` genelinde sistematik taranmalı. En yüksek beklenen getirili güvenlik işi.
- **`Kalder/` kopyası (1.7 GB, izlenmiyor):** `COPY . .` (PA-013) ile imaja girip girmediği doğrulanmalı; girerse eski `csrf.exempt`'li kod ve scheduler'lar imajda olur.
- **Commit'siz ağaç:** güvenlik düzeltmeleri izlenmeyen dosyalarda; disk kaybında kaybolur, deploy'a girmez.

## 5. Maliyet / kapasite gerçekçiliği
Tek kişilik ekip (+ AI ajanları) varsayımında 08'in 12 kanalı ve 30/60/90 planı, eşzamanlı fuar+webinar+Ads+EKAP **gerçekçi değil**; 05'in B1–B7 yeni modül listesi teknik borçla (test paketi, legacy erime, güvenlik) aynı anda yürütülemez. Önerilen: en fazla 2 kanal (K4 danışman ortaklığı + K1 kişisel doğrudan erişim) ve 1 yeni modül (B1 şablon kütüphanesi, mevcut klon altyapısı üzerine).

**Yüksek maliyet / düşük etki:** K3 fuar, K7 Google Ads (niş B2B), K12 EKAP (referans yokken), B7 holding konsolidasyonu, B4 EFQM RADAR+DÖF+YGG (L efor), kullanıcı hacmi yokken SocketIO'yu Redis queue ile ölçeklemek, PA-008/PA-009 mikro optimizasyonlar, KQ-007 büyük dosya bölme.

## 6. Karar engelleyen belirsizlikler
1. Yayın'da hangi kod çalışıyor? (commit'siz ağaç; PA-001/GV-002 durumu buna bağlı)
2. Yayın'da Redis bağlı mı; `GUNICORN_WORKERS` ve `KOKPITIM_DEMO_MODE` gerçek değerleri ne?
3. Sunucuda off-site yedek / cron var mı (kodda yok)?
4. İlk segment: danışman kanalı orta ölçekli firma mı, vakıf üniversitesi/belediye mi? (fiyat, satış döngüsü, gereken özellikler — SSO, şifre sıfırlama, kamu ihale belgeleri — buna bağlı)
5. Ekip kapasitesi ve 90 günlük bütçe nedir? (08/09 planları buna göre küçültülmeli)

## 7. Düzeltilmiş P0 listesi
1. **GV-001 indirme/silme uçları:** `api/routes_files.py:413-470` kaldır veya tenant + proje üyeliği kontrolüyle yeniden yaz (model alan uyuşmazlığını da çöz). Efor: S.
2. **Legacy `api/` + `main/` IDOR taraması** (`get_or_404` + yalnız `@login_required` deseni). Efor: M.
3. **PA-003:** off-site şifreli yedek + bir kez restore tatbikatı. Efor: S-M.
4. **Commit'siz ağacı güvenceye al** (scheduler_leader, outbound_guard izlenmiyor), test edip deploy et → PA-001 kapanır. Efor: S.
5. **GV-002:** `llm_gateway`'de tenant `base_url` için `validate_outbound_url` veya izin listesi. Efor: S.
6. **KQ-002:** test paketinin tamamlanması; izolasyon testleri guard açıkken koşmalı. Efor: S-M.

**Önemi indirilenler:** KQ-003 auth.py:36 (P0→P2), GV-007 (P1→P2, yalnız Yayın env teyidi).
