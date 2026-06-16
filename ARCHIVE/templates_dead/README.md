# Ölü Eski Template Arşivi

2026-06-16: Eski kök `templates/`'ten **hiçbir yerden referans almayan** (render_template yok,
extends/include yok — kesin teyit) 17 .html buraya taşındı. Modern karşılıkları `ui/templates/platform/`'da.

İçerik: `*_backup_*`, `*_v2`, `*_modern`, `*_old` (eski sürüm artıkları) + `project_list`/`project_form`/
`project_gantt`/`dashboard`/`easy_login`/`kurum_panel_strategic` eski ikizleri + `v2/` (masam/strateji/yonetim).

git mv ile taşındı (geçmiş korundu, geri alınabilir). App smoke OK (891 route).
