# Kök Dizin Script Arşivi

> **2026-06-16:** Kök dizinde (`c:\kokpitim` doğrudan altında) biriken **102 tek-seferlik script**
> buraya taşındı. Amaç: kök dizini görünür/yönetilebilir tutmak (111 .py → 9 çekirdek).

Bu scriptler **bir kez çalışıp işi bitmiş** araçlardır — uygulamanın çalışması için GEREKLİ DEĞİL.
Hiçbiri aktif kod (`app/`, `micro/`, `main/`, `platform_core/`) tarafından import edilmiyor (taşımadan önce teyit edildi).
`git mv` ile taşındı → geçmiş korundu, geri alınabilir.

## Kökte KALAN çekirdek (9 dosya — buraya taşınMAdı)
`__init__.py` (geriye-uyum fabrika), `app.py` (entry), `config.py`, `extensions.py` (aktif kod import ediyor),
`run.py`/`server.py`/`production_server.py` (sunucu çalıştırıcı), `maintenance.py`, `github_sync.py` (ops).

## Kategoriler
| Klasör | İçerik | Adet |
|--------|--------|------|
| `find_debug/` | `find_*`, `check_*`, `scan_*`, `read_log`, `get_users`, `list_data` — kod arama/inceleme araçları | 16 |
| `fix_oneshot/` | `fix_*` — tek seferlik hotfix scriptleri (encoding, template, schema…) | 10 |
| `seed/` | `seed_*` — demo/örnek veri yükleyiciler | 10 |
| `create/` | `create_*` — tablo/kullanıcı/örnek-veri/sunum üreticiler | 8 |
| `migrate_import/` | `migration_*`, `migrate_*`, `import_*`, `setup_*` — eski şema/veri göçü + içe aktarma | 18 |
| `test_deneme/` | `test_*`, `*_check`, `load_test`, `init_db`, `validate_*` — ad-hoc test/doğrulama | 14 |
| `rewrite_delete/` | `rewrite_*`, `replace_*`, `kod_stratejiler` — silme fonksiyonu yeniden yazma denemeleri | 5 |
| `misc/` | `tmp_*`, `update_*`, `add_*`, `apply_*`, `optimize_*`, `remove_*`, `models_backup`, `git_kur` vb. | 21 |

## Not
- Bazı scriptler birbirini import edebilir (ör. `seed_final` → `seed`); arşivde çalıştırılmaları beklenmiyor.
- Gerçekten gerekirse: ilgili dosyayı köke geri taşı (`git mv scripts/_arsiv/.../X.py .`) ve bağımlılıklarını çöz.
- Resmi/tekrarlı operasyonel scriptler `scripts/ops/` altındadır — burası değil.
