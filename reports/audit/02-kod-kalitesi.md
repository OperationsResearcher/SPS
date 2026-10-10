# 02 — Kod Kalitesi ve Hata Analizi (salt okunur)
Tarih: 2026-10-10 · Dal: claude/duzeltme-faz1-dogruluk (commit edilmemiş değişiklikler dahil)

## Ölçüm sonuçları (aynen)
- **ruff** (`.venv\Scripts\python.exe -m ruff check .`, PATH'te ruff yok): tüm repo → 221 hata, hepsi `F821 undefined-name`; `Kalder/` ve `scripts/_arsiv/` hariç → **"All checks passed!"** (ruff.toml kapsamıyla).
- **pytest**: `--timeout=300` kabul edilmedi (pytest-timeout kurulu değil: `unrecognized arguments: --timeout=300`). Onsuz (`-q -x --ignore=Kalder`) 889 test toplandı; 480 sn sınırında **TIMEOUT ile öldürüldü**. Çıktı %99'a kadar ilerledi (son satır `tests\test_yerel_llm_yolu.py ..`), hiç F/E görülmedi ama **özet satırı ("N passed") üretilmedi → çalıştırma tamamlanmadı, başarılı SAYILMAZ**. Takılma nedeni belirlenemedi (olası: son dosya sonrası ağ/LLM çağrısı veya scheduler/socket teardown).
- Büyük dosyalar (Kalder hariç): migrations baseline 3093; micro/modules/k_rapor/routes.py 2569; micro/modules/admin/routes.py 1883; services/k_radar_service.py 1497; api/routes_projects.py 1390; raporlar/routes_faz0.py 1327; main/routes/pages.py 1166.

## Bulgular
**KQ-001 — Kalder/ tam kopya dizin (1.7 GB, git'te izlenmiyor)** · `Kalder/` · Kanıt: `Kalder/micro/modules/k_rapor/routes.py` (2571 sn) ≈ `micro/...` (2569 sn); `git ls-files Kalder`=0. Açıklama: Kod tabanının yinelenen kopyası; grep/ruff/pytest taramalarını 2x şişirir, yanlış dosya düzenleme riski. Koşul: her araç taramasında. Etki: bakım/yanlış-dosya riski, ruff'ta 221 sahte F821 gürültüsü kaynağı değil ama arşivle birlikte. Önem: orta · Etiket: iyileştirme · Çözüm: repo dışına taşı / .gitignore + araç exclude. Efor: 15 dk · Doğrulama: `ruff`/`grep` süresi ve sonuç sayısı düşer.

**KQ-002 — Test paketi tamamlanmıyor (timeout)** · tests/ · Kanıt: yukarıdaki pytest çıktısı. Açıklama: Tam koşu 8 dk'da bitmiyor, %99'da takılıyor; pytest-timeout yok, CLAUDE/rehberdeki `--timeout` komutu çalışmaz. Koşul: tam koşu. Etki: CI yok (Actions kilitli) → yerel doğrulama güvenilmez. Önem: yüksek · Etiket: olası risk · Çözüm: `pip install pytest-timeout`, `-v` ile takılan testi bul, ağ çağrılarını mock'la. Efor: 2-4 sa · Doğrulama: `pytest -q` özet satırıyla biter.

**KQ-003 — `except Exception: pass` sessiz yutma (kural §3 ihlali)** · ör. app/routes/auth.py:36 (güvenlik denetim fallback'i), app/services/date_sovereign.py:85, app/services/efqm_assessment.py:797, app/services/hata_kontrol_executor.py:101,176,196,252,267,278,323,344,357 · Kanıt: 47 adet "except …: ⏎ pass" deseni (micro/app/main/api/services, Kalder/arşiv hariç). Açıklama: Hata logsuz yutulur; auth.py:36 güvenlik denetimi başarısızlığını bile gizler. Koşul: ilgili try bloğu hata verince. Etki: sessiz veri/tanı kaybı. Önem: orta (auth.py:36 yüksek) · Etiket: kesin hata (kural ihlali) · Çözüm: `app.logger.error(..., exc_info=True)` ekle; gerçekten zararsızlar `contextlib.suppress`+yorum. Efor: 3-4 sa · Doğrulama: `grep -A1 "except.*:$" | grep pass` sıfır; ruff `S110/SIM105` etkinleştir.

**KQ-004 — JS'de native alert() fallback'leri (kural §3)** · ui/static/platform/js/reports/veri_kalitesi.js:98, sp_analiz.js:71, project_form_transfer.js:22 · Kanıt: `alert(title+...)`, `alert(msg)`, `window.alert(msg)` (Swal yoksa dal). Açıklama: SweetAlert2 yüklenmezse devreye giren yedek; kural alert() yasak diyor. Etki: UX/kural tutarsızlığı. Önem: düşük · Etiket: iyileştirme · Çözüm: ortak `mcToast()` yardımcısı, fallback'i kaldır. Efor: 1 sa · Doğrulama: grep `\balert\(` sıfır.

**KQ-005 — Hard delete kullanımı (kural: soft delete)** · micro/modules/sp/routes_analysis.py:854,911; sp/routes_frameworks.py:256; sp/routes_scenario.py:117; surec/helpers.py:136; app/services/k_vektor_config_service.py:116,160,230,255; app/services/notification_service.py:259; main/routes/pages.py:508,904; main/routes/strategy_api.py:86,440 (proje silme); api/routes_pm.py:368,665,681,697 (+ toplu `.delete()` 606); routes_esg.py:227 (bilinçli, yorumlu) · Kanıt: `db.session.delete(...)`; toplam ~31 satır. Açıklama: Bir kısmı bağ/konfig satırı (kabul edilebilir), proje/süreç göstergesi/faaliyet silme veri kaybıdır. Koşul: ilgili DELETE endpoint'i çağrılınca. Etki: geri alınamaz veri kaybı, audit boşluğu. Önem: yüksek (strategy_api.py:440 proje, pages.py:508/904) · Etiket: olası risk · Çözüm: iş varlıkları için `is_active=False`; bağ tablolarını istisna listesine al ve belgele. Efor: 1-2 gün · Doğrulama: ilgili route testleri + DB'de satır kalıyor.

**KQ-006 — Legacy/modern çift yüzey** · main/routes/{pages,projects,strategy_api,kurum_panel}.py, api/routes_*.py (~136 legacy route) vs micro/ · Kanıt: git status'ta hem `main/routes/*` hem `micro/*` değişmiş; KURALLAR S1. Açıklama: Aynı alan iki yerde düzeltilir (Faz1 değişiklikleri ikisine de dokunuyor). Etki: tutarsız düzeltme, regresyon. Önem: orta · Etiket: olası risk · Çözüm: strangler planına göre route envanteriyle eritme; yeni düzeltmeyi tek yüzeye yap. Efor: sürekli · Doğrulama: LEGACY_ROUTE_INVENTORY azalır.

**KQ-007 — Aşırı büyük modüller** · micro/modules/k_rapor/routes.py (2569), admin/routes.py (1883), services/k_radar_service.py (1497), api/routes_projects.py (1390), raporlar/routes_faz0.py (1327) · Açıklama: Tek dosya çok sorumluluk; inceleme/merge çakışması zor. Önem: düşük-orta · Etiket: iyileştirme · Çözüm: alt blueprint/servis katmanına böl. Efor: 1-3 gün/dosya · Doğrulama: smoke route testi (test_smoke_routes) aynı kalır.

**KQ-008 — Yarım kalmış TODO'lar, çalışmayan stub'lar** · app/api/routes.py:413 (webhook), app/services/webhook_service.py:146,170, report_service.py:360, api/routes_ai.py:75 (sahte AI insights), app/api/data_connector.py:44 (O(1) token araması, 2000 kullanıcı sınırı) · Açıklama: Webhook DB'den okumuyor/log yazmıyor; AI insights gerçek değil. Etki: kullanıcıya vaat edilen özellik çalışmaz. Önem: orta · Etiket: olası risk · Çözüm: özelliği tamamla veya endpoint'i kapat. Efor: 1-3 gün · Doğrulama: ilgili endpoint testi.

**KQ-009 — ruff kapsamı arşivi/Kalder'i dışlıyor, ama komut varsayılanı 221 hata basıyor** · scripts/_arsiv/misc/tmp_extracted.py vb. · Açıklama: Kapsamsız `ruff check .` gürültülü; gerçek kod temiz (iyi). Önem: düşük · Etiket: iyileştirme · Çözüm: ruff.toml `extend-exclude` = Kalder, scripts/_arsiv. Efor: 5 dk.

**KQ-010 — Çalışma ağacı büyük ve commit'siz** · ~60 dosya modified, `app/utils/query_optimizer.py` silinmiş (D) · Kanıt: git status; koddan `query_optimizer` referansı bulunmadı (grep boş → silme güvenli görünüyor). Açıklama: Tek seferde büyük commit edilmemiş değişiklik; tests/ tarafında test_login_throttle değişti. Önem: orta · Etiket: olası risk · Çözüm: mantıksal commit'lere böl; tam test koşusu (KQ-002) sonrası. Efor: 1 sa.

Not: console.log (ui/static) = 0; JS'de gerçek `{{ }}` yok (yalnız "yasak" yorumları); `except:` çıplak = 0.

## Düzeltme listesi
- **P0:** KQ-002 (testi bitirilebilir kıl, önce takılan testi bul), KQ-003 auth.py:36.
- **P1:** KQ-005 (proje/süreç/faaliyet hard delete), KQ-010 (commit bölme + testle doğrula).
- **P2:** KQ-003 kalan 46 yer, KQ-006, KQ-008.
- **P3:** KQ-001, KQ-004, KQ-007, KQ-009.
