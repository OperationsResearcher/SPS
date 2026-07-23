---
name: project-i18n-devir
description: "i18n (TR/EN) çoklu dil çalışması durumu — statik UI katmanı tamamlandı, deploy bekliyor"
metadata: 
  node_type: memory
  type: project
  originSessionId: b1750688-0b9c-41fa-a334-6391622230bb
---

KOKPİTİM statik UI katmanı TR/EN çoklu dile TAM çevrildi (2026-07-01). EN katalog 4742 msgid, 0 boş/0 fuzzy.
Mekanizma: Flask-Babel (backend+Jinja `_()`/`lazy_gettext`) + `window.t()` (JS, `app/i18n.py::js_i18n_map()` ile enjekte).
Tüm iş main'e merge edilip origin'e push edildi (commit `d42f58e` merge, `87c59dd` son fix).

**Why:** Kullanıcı "yayına ve teste vermeyelim" dedi — kod origin/main'de duruyor ama Test/Demo/Yayın VM'lerine
deploy EDİLMEDİ. Deploy yalnızca kullanıcı "yayına çıkalım" dediğinde yapılacak ([[project_l_paketleri_deploy_kurali]] ile aynı disiplin).

**How to apply:**
- Yeni sohbette "i18n nerede kaldı" sorulursa: statik katman bitti, deploy bekliyor — deploy ÖNERME.
- Yeni UI eklenirse: şablonda `{{ _() }}`, JS'de `t()` kullan → `bash scripts/i18n_extract.sh` →
  `scripts/_arsiv/fix_oneshot/i18n_fill_surec.py` (supplement.json'dan doldur) → `pybabel compile -d translations`.
- Kritik tuzaklar: modül-seviyesi sabitlerde `lazy_gettext` şart (düz `gettext` import anında Türkçe'ye kilitlenir);
  babel `${t(...)}` template-literal çağrılarını kaçırır → `extract_inline_t.py` telafi eder; Jinja `_()` çıktısında
  literal `%` → `%%` yazılmalı (JS `t()` için bu kural GEÇERLİ DEĞİL); DB-key/enum/log/prompt çevrilmez.
- Tam detay: `docs/lang/DEVIR-BELGESI.md`.
