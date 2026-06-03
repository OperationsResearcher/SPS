# 3 Saatlik Otonom İyileştirme Koşusu — 2026-06-03

> Dal: `claude/3saat-iyilestirme` · Deadline epoch: **1780449948**
> Yalnızca yerel. Her iyileştirme ayrı commit. Geri almak için: `git revert <hash>`.

## Tur Günlüğü

### Tur 1 — Correctness: karne aralık parser ondalık bug
- **Commit:** karne aralık parser Türkçe ondalık/binlik biçimi
- **Sorun:** `parse_aralik_degeri` ',' ve '.' ikisini de siliyordu → "4,5" → "45" (yanlış başarı puanı).
- **Fix:** Türkçe biçim ('.' binlik kaldır, ',' ondalık→'.'). 8 regresyon testi eklendi (`tests/test_karne_parse.py`).
- **Risk:** Düşük; veri İngilizce-ondalık ("4.5") kullanıyorsa revert edilebilir.

### Tur 2 — Performans: admin kullanıcı listesi N+1
- **Commit:** admin kullanıcı listelerinde rol eager-load
- 4 sorgu noktasına `selectinload(User.role)`. 50 user: 5→2 sorgu. Sonuç değişmez.
- **Risk:** Çok düşük (sadece eager-load).

### Tur 3 — Performans: vision-score N+1
- **Commit:** vision-score alt-strateji süreçleri eager-load
- `compute_vision_score` ss.processes lazy → selectinload+joinedload. Sonuç aynı, her raporda çalıştığı için yüksek etki.
- **Risk:** Çok düşük.

### Tur 4 — Kalite: skor motoru birim testleri
- **Commit:** skor motoru saf fonksiyonlarına 17 birim testi
- compute_pg_score / _default_weight / _resolve_target_for_calculation. Sıfır risk, regresyon koruması.

### Tur 5 — Performans: admin kullanıcı sayfası tenant N+1
- **Commit:** kullanıcı sayfasında tenant eager-load
- users.html `u.tenant.name` kullanıyor → selectinload(User.tenant). 50 user: 8→3 sorgu.

### Tur 6 — Kalite: karne başarı puanı testleri
- **Commit:** karne başarı puanı + aralık kontrolü 13 birim testi
- deger_aralikta_mi + hesapla_basari_puani (artan/azalan, sınır aşımı, açık üst-sınır). Çekirdek skorlama, sıfır risk.

### Tur 7 — Kalite: karne ağırlıklı puan testleri
- **Commit:** ağırlıklı başarı puanı 6 birim testi. Karne test kapsamı tamamlandı.

### Tur 8 — Kalite: cache anahtar format testleri
- **Commit:** cache anahtarı format 7 birim testi (cache_key_for_model + CACHE_KEYS). Invalidation tutarlılığı koruması.

### Tur 9 — Kod: sessiz audit hatalarına logging
- **Commit:** sessiz audit except'lerine logging (3 yer: 2FA reset, holding drill-down, KpiData delete)
- `except Exception: pass` → `current_app.logger.error`. CLAUDE.md "her except loglamalı" uyumu + gözlemlenebilirlik. Control flow aynı.

### Tur 10 — Kalite: date-sovereign doktrin testleri
- **Commit:** entity_exists_in_year 6 birim testi (çok-yıllı varlık-mevcudiyet doktrini).

### Tur 11 — Kod: 2 sessiz dashboard hatasına logging
- **Commit:** k_radar olgunluk + k_rapor proje-adı sessiz hatalarına logging. Inline parse-default'lara dokunulmadı.

### Tur 12 — A11y: kurum ayarları label-for
- **Commit:** kurum ayarları formunda 7 label'a for= (input id'leri mevcuttu). Parse OK.

### Tur 13 — Correctness: karne negatif aralık parse (deep-scan C4)
- **Commit:** negatif sınırlı aralıkları parse et (regex) + 4 test. Mevcut davranış korundu.

### Tur 14 — Performans: process_health KPI verisi N+1
- **Commit:** calculate_process_health_score KPI verisi bulk-load. 4 KPI: 6→3 sorgu, sonuç aynı.

### Tur 15 — A11y: SMTP ayarları label-for
- **Commit:** eposta.html 6 label'a for= (input id'leri mevcuttu). Parse OK.

### Tur 16 — Kalite: forecast regresyon matematiği testleri
- **Commit:** _linear_regression + _standard_error 7 birim testi. Saf matematik.

### Tur 17 — Kalite: karne JSON aralık parser testleri
- **Commit:** parse_basari_puani_araliklari 6 birim testi (liste/dict/obje/geçersiz). NOT: process_performance_service:518 N+1 tespit edildi ama çeyrek-tipine göre değişen sorgu → riskli refactor, ertelendi.

### Tur 18 — Kod: exec-dashboard/quarterly sessiz hatalara logging
- **Commit:** 4 best-effort except'e logger.error (risk + anomali, exec_dashboard + quarterly). Modül logger eklendi.

### Tur 19 — Kalite + Bulgu: _resolve_target testleri
- **Commit:** _resolve_target_for_calculation 8 test. **BULGU:** score-engine ('400.000'→400.0) vs karne parser ('400.000'→400000) binlik-ayraç tutarsızlığı (1000x). Riskli/domain kararı → değiştirilmedi, kullanıcı kararına bırakıldı.

### Tur 20 — A11y: süreç formu label-for
- **Commit:** surec/index.html süreç ekle/düzenle formunda 10 label'a for=. Parse OK.

### Tur 21 — Performans: strateji haritası N+1 (yüksek etki)
- **Commit:** routes_flow links eager-load + KPI bulk-load. 68 süreç: 137→3 sorgu.

### Tur 22 — Kod: efqm KPI-327 sessiz hatasına logging
- **Commit:** efqm outer except'e logger.error (iç parse-default korundu).

### Tur 23 — Kalite/Güvenlik: db_sequence testleri
- **Commit:** is_pk_duplicate + _validate_identifier (SQL injection guard) 9 test.

### Tur 24 — Perf: bireysel zaman çizelgesi N+1
- **Commit:** contains_eager(individual_activity) — döngü içi lazy-load (≤30 track) elendi.

### Tur 25 — Hijyen: proje sessiz except:pass loglama
- **Commit:** project_create — plan yılı + notification_settings exception'ları artık logger.warning (MASTER §3).

### Tur 26 — Test: numeric.safe_float (12 test)
- **Commit:** safe_float davranış sözleşmesi (TR virgül-ondalık, binlik ayraç sınırı, bool→1.0).

### Tur 27 — A11y: profil formu label-for (9)
- **Commit:** auth/profil.html — profil + şifre değiştir formu 9 label-for bağı. Toplam a11y label-for: 42.
