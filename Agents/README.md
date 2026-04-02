# KOKPİTİM — Sub-Agent Rehberi
> Hangi ajanı ne zaman, nasıl başlatırsınız

---

## Hızlı Karar Tablosu

| Görev | Ajan | Dosya |
|-------|------|-------|
| Route ekle, servis yaz, güvenlik düzelt | Backend | `BACKEND-AGENT.md` |
| Model ekle, migration, DB analizi | DB/Model | `DB-AGENT.md` |
| Sayfa tasarımı, CSS, JS, modal | Tasarım | `TASARIM-AGENT.md` |
| Dead code sil, script temizle, refactor | Temizlik | `TEMIZLIK-AGENT.md` |

---

## Nasıl Başlatılır

### Claude Code (VS Code terminal)
```bash
# Ajanı başlat
cat docs/agents/BACKEND-AGENT.md | pbcopy   # Mac
# veya dosyayı aç, içeriği kopyala, Claude Code chat'e yapıştır
```

### Cursor
```
Cursor chat → + New conversation → İlgili agent dosyasını yapıştır
```

### Bu pencere (claude.ai)
```
/kural snippet → ardından agent dosyasının içeriğini yapıştır
```

---

## Ajan Sınırları — Kısaca

```
Backend Ajanı   → routes.py, services.py, config — template YOK
DB Ajanı        → app/models/, migrations/ — routes YOK
Tasarım Ajanı   → templates/, css/, js/ — model YOK
Temizlik Ajanı  → her yeri tarar — yeni özellik EKLEMEZ
```

---

## Çakışma Durumunda

Bir görev iki ajanı ilgilendiriyorsa (örn. yeni endpoint + yeni model):

```
1. DB Ajanı → modeli oluştur, migration yaz
2. Backend Ajanı → route'u yaz, modeli kullan
3. Tasarım Ajanı → sayfayı bağla
```

Sıra önemli — önce model, sonra route, sonra UI.

---

## Ortak Kural — Hepsi İçin

- `@docs/KURALLAR-MASTER.md` geçerli
- Her görev sonunda `docs/TASKLOG.md` güncellenir
- Push yalnızca kullanıcı istediğinde
- Plan göster → onay al → uygula
