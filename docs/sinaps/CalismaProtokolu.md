# SİNAPS × KOKPİTİM — PARALEL ÇALIŞMA PROTOKOLÜ
> İki ürün, iki repo, sıfır karışma
> Tarih: 2026-05-16
> Geçerlilik: Kalıcı (her oturumun başında referans alınmalı)

---

## 1. Temel İlke

**Kokpitim YAŞIYOR. Sinaps DOĞUYOR.** İki ürün aynı anda gelişir, hiçbir değişiklik diğerine sızmaz.

- Kokpitim'e zarar gelmesi = kabul edilemez
- Sinaps'tan Kokpitim'e kod sızması = kabul edilemez (stack ayrı)
- Kokpitim öğrenmeleri Sinaps'a (insan kararı ile) taşınır — kod olarak değil, **ders olarak**

---

## 2. Fiziksel Ayrım

| Boyut | Kokpitim | Sinaps |
|--|--|--|
| Working dir | `c:\kokpitim` | `c:\sinaps` |
| Repo | mevcut | `kokpit/sinaps` (yeni) |
| Default branch | `main` | `main` |
| DB | mevcut PG + SQLite | Docker compose PG (yerel) |
| Port (yerel) | 5001 | 3000 (web) + 8000 (api) |
| Stack | Flask + Jinja + SQLAlchemy | FastAPI + Next.js + SQLAlchemy |
| Kural dosyası | `c:\kokpitim\CLAUDE.md` + `docs/KURALLAR-MASTER.md` | `c:\sinaps\CLAUDE.md` + `docs/KURALLAR-SINAPS.md` |
| Görev günlüğü | `docs/TASKLOG.md` | `CHANGELOG.md` + `docs/sinaps/DecisionLog.md` |

---

## 3. Sözlü Protokol — Kullanıcı Komut Verirken

Her görev `Kokpitim:` veya `Sinaps:` prefix ile başlar.

✅ İyi: "Kokpitim: extensions.py'de FakeLimiter'ı gerçek Limiter'a çevir"
✅ İyi: "Sinaps: apps/api'ye health endpoint ekle"
❌ Belirsiz: "Şu fonksiyonu düzelt" → Claude **sorar**, varsayım yapmaz

Karışık görev → ikiye böl:
- "Kokpitim'deki şu logic'i Sinaps'a port et" → İki ayrı görev:
  1. Kokpitim: kaynak kodu oku/anla
  2. Sinaps: yeni stack'le yeniden yaz (kopyala-yapıştır YASAK)

---

## 4. Claude'un Görsel İşaretlemesi

Her tool call öncesi Claude tek satır söyler:

- `🔧 KOKPİTİM: <ne yapıyorum>`
- `🆕 SİNAPS:   <ne yapıyorum>`

Bu satır görünmeyince kullanıcı uyarır: "hangi repo?"

---

## 5. Kokpitim Çalışma Kuralları (mevcut + bu protokol)

**Geçerli kural seti:** `c:\kokpitim\CLAUDE.md` + `docs/KURALLAR-MASTER.md`

Ek protokol:
- Her dosya değişikliği öncesi **tam okuma** zorunlu (memory kuralı)
- Yedek/snapshot olmadan migration yok
- Push **mutlaka** kullanıcı onayıyla
- VM/prod deploy yalnız `scripts/vm_safe_deploy.sh` ile
- Riskli görünen her aksiyon → DUR + sor

---

## 6. Sinaps Çalışma Kuralları (özet — detay c:\sinaps\CLAUDE.md'de)

**Stack:** FastAPI · Next.js 15 · PostgreSQL + ltree + RLS · Keycloak · OPA · NATS · Vault · LiteLLM · Turborepo + pnpm + uv

**Zorunlu (Sinaps):**
- RLS policy her tenant tablosunda
- Soft delete (`deleted_at`)
- OTEL trace + structured log (JSON)
- Idempotency-Key POST için
- ETag/`If-Match` PATCH için
- OpenAPI auto-export her PR'da
- Tenant Isolation Suite yeşil olmadan merge yok

**Yasak (Sinaps):**
- Hard delete
- Hardcoded secret
- Raw SQL (SQLAlchemy bound params zorunlu)
- `print()` (log kullan)
- Flask/Jinja/jQuery (eski stack)
- Tenant_id query parametresi (path veya JWT)

**Ortak (Kokpitim + Sinaps):**
- Backend EN / Frontend TR
- Push kullanıcı onayıyla
- `Oku → Plan → Onay → Uygula → Test → Log → Dur`
- "Deneme yanılma" yasak — kök neden bulmadan kod yazma

---

## 7. Geçiş Anı — `c:\kokpitim` → `c:\sinaps`

**Tetik:** Kullanıcı "Sinaps S0 başla" dediğinde.

**Adımlar (Claude tarafından sırayla):**
1. `c:\sinaps\` dizinini oluştur
2. `c:\kokpitim\docs\sinaps\*.md` (19 dosya) → `c:\sinaps\docs\` altına **kopyala** (taşıma değil — kaynak Kokpitim'de canlı kalır referans için)
3. `c:\sinaps\CLAUDE.md` yaz (Sinaps stack kuralları)
4. `c:\sinaps\docs\KURALLAR-SINAPS.md` yaz (detaylı kural seti)
5. `git init` + `gh repo create kokpit/sinaps --private`
6. S0 bootstrap checklist (F1 §2 — 10 madde)
7. İlk commit + push

**Geçiş sonrası:**
- Kokpitim oturumlarında `cwd = c:\kokpitim`
- Sinaps oturumlarında `cwd = c:\sinaps`
- Aynı oturumda hem Kokpitim hem Sinaps yapılacaksa Claude `cd` yerine **tam yolla** dosya açar (kafa karışması en aza insin)

---

## 8. Değişiklik Sonrası Onay Akışı

### Kokpitim için
Claude her değişiklik bitiminde:
1. `git status --short` (değişen dosyalar)
2. `git diff --stat` (özet)
3. Test komutu önerir (manuel doğrulama)
4. **Push yok** kullanıcı "push" demedikçe
5. TASKLOG.md'ye satır eklenmesini önerir (kullanıcı onayıyla)

### Sinaps için
Claude her değişiklik bitiminde:
1. `git status --short`
2. CI lokal koşumu (`turbo lint && turbo test` veya equivalent)
3. RLS testi geçti mi (tenant tablosu eklendiyse zorunlu)
4. **Push yok** kullanıcı "push" demedikçe
5. CHANGELOG.md / DecisionLog.md güncellemesi önerir

---

## 9. Yanılma Önleyici Kontroller (Claude için)

Her görev başında Claude şunlara dikkat eder:
- **Working directory check:** path başlangıcı `c:\kokpitim` mi `c:\sinaps` mi?
- **Stack imzası:** `from flask` görüyorsam Kokpitim; `from fastapi` görüyorsam Sinaps
- **Dosya türü ipucu:** `templates/*.html` (Jinja) → Kokpitim; `apps/web/src/app/*.tsx` → Sinaps
- **Şüphe varsa**: değişiklik yapmadan SOR

---

## 10. Acil Geri Alma (Kokpitim için)

```bash
# Lokal değişiklik geri al
git restore <dosya>                  # stage edilmemiş
git restore --staged <dosya>         # stage edilmiş
git reset --hard HEAD                # tüm lokali at

# Commit yapıldı, push yok
git reset --soft HEAD~1              # son commit geri al, değişiklik kalır
git reset --hard HEAD~1              # son commit + değişiklik at

# Push yapıldı (dikkat — kişisel branch'te)
git revert <sha>                     # anti-commit (önerilen)

# DB yanlışı (production-vari)
# scripts/vm_safe_deploy.sh PG yedek alıyor → restore yordamı:
# docs/YERELDEN_VM_YAYIN.md §"Geri alma"
```

---

## 11. Bilgi Akışı (Kokpitim → Sinaps)

Kokpitim'de öğrenilen ders Sinaps'a **kod olarak değil, karar olarak** taşınır:

| Öğrenme tipi | Aktarım yolu |
|--|--|
| Kullanıcı UX şikayeti | Sinaps PRD / UX revize |
| Performans darboğazı | Sinaps capacity model / index stratejisi |
| Güvenlik açığı | Sinaps threat model güncellemesi |
| İş kuralı (domain logic) | Sinaps domain model + test |
| Çalışan/yanlış kod | Sinaps **asla kopyalanmaz**; ders not edilir, yeniden yazılır |

---

## 12. Çakışma Önleyici Genel İlke

> **"Hangi repo?" sorusu daima sorulabilir.**
> Sen şüphelendiğinde sor.
> Ben şüphelendiğimde değişiklik yapmadan sorarım.
> Hiçbir tool call hangi repoyu hedeflediği belirsizken çalışmaz.

---

## 13. Geçiş Checklist'i (kullanıcı işaretleyecek)

Sinaps S0'a geçmeden önce:
- [ ] Tüm açık sorular kapatıldı (DecisionLog.md ✓)
- [ ] F0-F4 planlama tamam (18+1 doküman ✓)
- [ ] `c:\sinaps\` çalışma dizini hazır
- [ ] GitHub `kokpit` org oluşturuldu (kullanıcı yapacak)
- [ ] Kokpitim'de askıdaki kritik görev kalmadı (yoksa önce o)
- [ ] Yedek alındı (Kokpitim son commit + DB snapshot)
