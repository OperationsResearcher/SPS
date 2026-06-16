# 🎯 KOKPİTİM — RİSK MATRİSİ (2026 Q2)

> Audit kaynak: [PROJE-AUDIT-2026Q2.md](PROJE-AUDIT-2026Q2.md)
> Risk skoru = Olasılık × Etki (1-5 skala, max 25)
> Tarih: 2026-05-23

---

## 🔥 KRİTİK BÖLGE (Risk ≥ 16) — Sprint 1'de çözülmeli

| Risk | Olasılık | Etki | Skor | Açıklama | Etkilenen |
|---|:-:|:-:|:-:|---|---|
| Plan year NULL handling tutarsızlığı → multi-year data corruption | 5 | 4 | **20** | Tomofil testinde dropdown bug'ı olarak ortaya çıktı. Aktif yıl + NULL pattern'i 3 modülde farklı. KpiData, Activity'de filtre eksik. | sp, surec, k_rapor, bireysel |
| `app/routes/process.py` 1.805 satır legacy monolith | 4 | 4 | **16** | Sunset bekliyor ama dosya canlı. Yeni özellik geliştirme bu dosyadan etkilenebilir. | core |
| Tenant scope validation eksikliği (K-Radar) | 3 | 5 | **15** | Client başka tenant'ın process_id'sini request edebilir → cross-tenant veri sızıntısı. | k_radar |
| Audit log silent fail (admin operations) | 4 | 4 | **16** | Tenant/User edit/delete try/except içinde audit kaydı atlanıyor. KVKK/uyum riski. | admin |
| Logo upload — file magic byte check yok | 3 | 5 | **15** | SVG XSS riski. Üretimde public tenant logo URL'leri var. | admin, tüm tenant'lar |

---

## 🟠 YÜKSEK BÖLGE (Risk 10-15) — Sprint 2-3'te çözülmeli

| Risk | Olasılık | Etki | Skor | Açıklama | Etkilenen |
|---|:-:|:-:|:-:|---|---|
| N+1 sorgu yaygınlığı (Process.leaders/members/owners, ProcessMaturity, k_rapor) | 5 | 3 | **15** | 100+ kayıt liste sayfalarında 300+ sorgu. Ölçekleme problemi. | sp, surec, k_radar, k_rapor, proje |
| KpiData + KpiDataAudit transaction atomicity zayıf | 3 | 4 | **12** | Hata durumunda orphan audit log. Forensic eksikliği. | surec |
| Activity cross-tenant assignment riski | 3 | 4 | **12** | Assigned user'ın same tenant'ı validate edilmiyor. | surec |
| Test kapsamı zayıflığı (sp %5, k_radar %0, bireysel %0, k_rapor %0, admin %0) | 5 | 3 | **15** | Refactor riski, regression riski. | core ve genel |
| `clone_full_plan_year()` rollback'te FK orphan | 3 | 4 | **12** | Yeni plan yılı klonu hata verirse veri tutarsızlığı. | sp |
| K-Vektor strateji + alt strateji weight update atomic değil | 3 | 4 | **12** | Partial state kalabilir. | sp |
| `/sp/api/graph` limit yok | 3 | 4 | **12** | Büyük tenant'ta OOM/timeout. | sp |
| Process parent-child circular reference (A→B→C→A) | 2 | 5 | **10** | Hierarchy walk'ta infinite loop. | surec |
| Schedule persistence dosya sisteminde (K-Radar) | 3 | 4 | **12** | Multi-server deployment'ta sync sorunu. | k_radar |
| Recommendation state race condition | 3 | 3 | 9 | Concurrent user'lar same recommendation. | k_radar |
| KPI period mismatch validation zayıf (Aylık vs Çeyreklik) | 3 | 3 | 9 | Yanlış periyota veri girişi. | surec |

---

## 🟡 ORTA BÖLGE (Risk 5-9) — Sprint 4-6'da

| Risk | Skor | Açıklama |
|---|:-:|---|
| Gantt performans riski (500+ task render) | 9 | proje/routes_views.py |
| Task `due_date` vs `due_at` karmaşası | 6 | proje/routes_tasks.py |
| PDF export hiçbir yerde yok | 8 | k_rapor, bireysel, proje |
| Process parent-child circular yok | 8 | surec |
| Legacy `Surec.query` fallback (proje modülünde) | 6 | proje |
| `accessible_processes_filter` performans (3× .any() query) | 8 | surec |
| `hesapla_basari_puani()` unit test yok — formula değişirse tarihsel tutarsızlık | 9 | surec |
| Strategy.source_strategy_id cascade unclear | 6 | sp |
| ProcessMaturity index yok | 8 | k_radar |
| Bulk import encoding tutarsızlığı | 4 | admin |
| Login stats query kompleks string matching | 6 | admin |
| i18n eksik (hardcoded TR) | 6 | tüm modüller |

---

## 🟢 DÜŞÜK BÖLGE (Risk < 5) — Backlog

- `_safe_json()` HTTP status differentiation yok
- PK sequence sync workaround (bireysel)
- Tenant name unique check eksik (model-level)
- `decorators.py` (root) ölü kod — **15 dk'da silinir**

---

## 📊 ÖZET DAĞILIMI

| Bölge | Risk sayısı | Toplam efor tahmini |
|---|:-:|---|
| 🔴 KRİTİK (≥16) | 5 | ~3-4 hafta |
| 🟠 YÜKSEK (10-15) | 11 | ~6-8 hafta |
| 🟡 ORTA (5-9) | 12 | ~4-5 hafta |
| 🟢 DÜŞÜK (<5) | 4+ | ~1 hafta |

**Toplam:** 32+ tespit edilmiş risk · tahmini efor **14-18 hafta** = 7-9 sprint

Bu, kullanıcının "3-6 aylık yapısal dönüşüm" hedefiyle uyumlu.

---

## 🎯 SPRINT 1 ÖNERİSİ (KRİTİK + QUICK WIN)

İlk sprint için **risk skoru ≥16** olanların hepsi + quick win'ler:

1. ✅ OKR migration — **TAMAMLANDI** (bu oturum)
2. ✅ Project soft-delete migration — **TAMAMLANDI** (bu oturum)
3. ✅ /kurum dropdown plan_year filtresi — **TAMAMLANDI** (bu oturum)
4. 🔥 Plan year filter helper (`app/utils/plan_year_filter.py`) yarat
5. 🔥 `surec/routes_kpi_data.py` ve `routes_activity.py`'a plan_year filter
6. 🔥 K-Radar tenant scope validation decorator
7. 🔥 Audit log silent fail kaldır (admin operations)
8. 🔥 Logo upload magic byte check
9. ⚡ `decorators.py` (root) sil (0 reference)
10. ⚡ Login audit log

→ Detaylı dağılım: [ROADMAP-2026H2.md](ROADMAP-2026H2.md)
