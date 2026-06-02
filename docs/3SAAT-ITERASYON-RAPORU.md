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
