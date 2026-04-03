# KOKPİTİM — Claude Code Çalışma Dosyası
# Tek gerçek kaynak: docs/KURALLAR-MASTER.md
# Mimari detaylar burada — kurallar MASTER'da

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
