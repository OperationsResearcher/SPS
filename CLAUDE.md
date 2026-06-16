# KOKPİTİM — Claude Code Çalışma Dosyası
# Tek gerçek kaynak: docs/KURALLAR-MASTER.md
# Mimari detaylar burada — kurallar MASTER'da
# Üç ortam (KURALLAR-MASTER §8): Yerel (127.0.0.1) → Test (test.kokpitim.com) → Yayın (www.kokpitim.com)
# "VM", "production", "üretim VM" gibi belirsiz terim KULLANMA — Yerel / Test / Yayın de.

---

## 🚀 OTURUM BAŞLATMA — Otomatik çalıştır

```bash
# 1. Son 3 task'ı oku
head -80 docs/TASKLOG.md

# 2. Git durumu
git log --oneline -5
git status --short
git branch --show-current

# 3. Kritik sağlık kontrolü
grep -n "FakeLimiter" extensions.py
ls -lh instance/kokpitim.db 2>/dev/null || echo "DB YOK"

# 4. Son değişen dosyalar
find micro/ -name "*.py" -newer docs/TASKLOG.md | head -10
```

Hazırlık raporu formatı:
```
✅ KOKPİTİM HAZIR
Son task : TASK-[X] | [tarih] | [özet]
Branch   : [branch]
DB       : [boyut / YOK]
Uyarı    : [varsa]
Ne yapıyoruz?
```

---

## 📋 KURALLAR

@docs/KURALLAR-MASTER.md

---

## 🗺️ SİSTEM HARİTASI — "neyin ne olduğu"

Kod tabanında kaybolduğunda / "bu dosya canlı mı" sorusunda önce buraya bak:
**[`docs/SISTEM-HARITASI.md`](docs/SISTEM-HARITASI.md)** — çekirdek (kökte 9 .py), blueprint dağılımı
(891 route; `app_bp`=556 modern, `main_bp`=136 legacy), modern modüller, model/servis katmanı, legacy yüzey,
onboarding çekirdeği (~12 dosya). Mimari yön: **strangler** — modern `micro/`+`app/` büyür, legacy erir
(sıfırdan yazma reddedildi). Tek-seferlik kök scriptler `scripts/_arsiv/`'de.

---

## 🌿 BRANCH DİSİPLİNİ — ZORUNLU AKIŞ

> Bu kural 2026-05-24'te kullanıcı onayıyla kondu. Baseline: `baseline-2026-05-24`.

### Altın kural
**`main`'e doğrudan commit YOK.** Her yeni iş kendi dalında doğar, test edilir, sonra main'e merge edilir.

### Yeni iş başlangıcında (Claude otomatik yapar)
Kullanıcı "şu işi yapalım" dediğinde, kod yazmaya başlamadan önce:
```bash
git checkout main
git pull origin main 2>/dev/null || true     # bağlantı yoksa atla
git checkout -b claude/<konu-kebab-case>
```
Konu adı: `claude/sp-yeni-modul`, `claude/fix-karne-n1`, `claude/refactor-auth` gibi.

### İş bitince — Claude şunu yapmaz, kullanıcıya sorar:
- `git checkout main && git merge --no-ff claude/<dal>`
- `git tag -a deploy-YYYY-MM-DD -m "..."`
- `git push origin main` veya `git push origin claude/<dal>`
- VM deploy

Bu 4 adım kullanıcı **"merge edelim"** / **"push'la"** / **"deploy"** dediğinde yapılır. Otomatik değil.

### Dal hayatı
- Maksimum 3 gün. Uzarsa `git rebase origin/main` ile main'i yakala.
- İş kabul edildikten sonra dal yerelden silinir: `git branch -d claude/<dal>`

### Tag stratejisi
- `baseline-<tarih>` = stabil dönüm noktası (yılda birkaç kez)
- `deploy-<tarih>` = VM'e gönderilmiş sürüm (her deploy'da)
- Sorun çıkarsa: `git reset --hard <tag>` ile o noktaya dön

### Mevcut tag'ler
- `baseline-2026-05-24` — S59-S63 sonrası stabil

---

## 🏗️ MİMARİ DETAY (Claude Code'a özel)

### Uygulama Başlangıcı
```
app.py → create_app() → config.py → extensions init → blueprints → app.run(5001)
```

### Blueprint Haritası
| Blueprint | Prefix | Durum |
|-----------|--------|-------|
| `micro_bp` | `/micro` | ✅ AKTİF |
| `auth_bp` | `/auth` | Legacy |
| `main_bp` | `/` | Legacy |
| `api_bp`, `admin_bp` | — | Legacy |
| `v2_bp`, `v3_bp` | — | Eski/deney |

### DB Instance Kuralı
```python
# DOĞRU
from extensions import db

# YANLIŞ — asla
from app.models import db
db = SQLAlchemy()
```

### Serbest Tarama Komutları
```bash
# Teknik borç tespiti
find micro/ app/ ui/ -name "*.py" | xargs wc -l | sort -rn | head -15

# N+1 sorgu riski
grep -rn "relationship(" app/models/ | grep -v "lazy=" | head -20

# Jinja2-in-JS kalıntısı (aktif klasör)
grep -rn "{{ " ui/static/platform/js/

# Console.log kalıntısı
grep -rn "console\.log" ui/static/platform/js/
```
