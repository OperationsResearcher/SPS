"""Tüm ana sayfalara breadcrumb bloğu ekler. Idempotent (varsa atlar)."""
import re
from pathlib import Path

BASE = Path(r"c:\kokpitim\ui\templates\platform")

# (relative_path, [{label, url_for}])  — son öğenin url'i None bırakılır
PAGES = [
    # Süreç
    ("surec/index.html", [{"l": "Süreç Yönetimi", "u": None}]),
    ("surec/faaliyetler.html", [
        {"l": "Süreç Yönetimi", "u": "url_for('app_bp.surec')"},
        {"l": "Faaliyetler", "u": None},
    ]),
    # Proje
    ("project/list.html", [{"l": "Proje Yönetimi", "u": None}]),
    ("project/portfolio.html", [
        {"l": "Proje Yönetimi", "u": "url_for('app_bp.project_list')"},
        {"l": "Stratejik Portföy", "u": None},
    ]),
    ("project/detail.html", [
        {"l": "Proje Yönetimi", "u": "url_for('app_bp.project_list')"},
        {"l": "project.name if project else 'Proje'", "u": None, "raw": True},
    ]),
    ("project/gantt.html", [
        {"l": "Proje Yönetimi", "u": "url_for('app_bp.project_list')"},
        {"l": "Gantt", "u": None},
    ]),
    ("project/kanban.html", [
        {"l": "Proje Yönetimi", "u": "url_for('app_bp.project_list')"},
        {"l": "Kanban", "u": None},
    ]),
    ("project/calendar.html", [
        {"l": "Proje Yönetimi", "u": "url_for('app_bp.project_list')"},
        {"l": "Takvim", "u": None},
    ]),
    ("project/raid.html", [
        {"l": "Proje Yönetimi", "u": "url_for('app_bp.project_list')"},
        {"l": "RAID Kayıtları", "u": None},
    ]),
    ("project/form.html", [
        {"l": "Proje Yönetimi", "u": "url_for('app_bp.project_list')"},
        {"l": "Yeni / Düzenle", "u": None},
    ]),
    ("project/task_detail.html", [
        {"l": "Proje Yönetimi", "u": "url_for('app_bp.project_list')"},
        {"l": "Görev", "u": None},
    ]),
    ("project/task_form.html", [
        {"l": "Proje Yönetimi", "u": "url_for('app_bp.project_list')"},
        {"l": "Görev / Düzenle", "u": None},
    ]),
    # SP
    ("sp/index.html", [{"l": "Stratejik Planlama", "u": None}]),
    ("sp/menu.html", [{"l": "Stratejik Planlama", "u": None}]),
    ("sp/xmatrix.html", [{"l": "Stratejik Planlama", "u": "url_for('app_bp.sp_menu')"}, {"l": "X-Matrix", "u": None}]),
    ("sp/exec_dashboard.html", [{"l": "Stratejik Planlama", "u": "url_for('app_bp.sp_menu')"}, {"l": "Yönetici Paneli", "u": None}]),
    ("sp/initiatives.html", [{"l": "Stratejik Planlama", "u": "url_for('app_bp.sp_menu')"}, {"l": "Girişimler", "u": None}]),
    ("sp/projeler.html", [{"l": "Stratejik Planlama", "u": "url_for('app_bp.sp_menu')"}, {"l": "Projeler", "u": None}]),
    ("sp/ceyreklik_review.html", [{"l": "Stratejik Planlama", "u": "url_for('app_bp.sp_menu')"}, {"l": "Çeyreklik Review", "u": None}]),
    ("sp/replan_triggers.html", [{"l": "Stratejik Planlama", "u": "url_for('app_bp.sp_menu')"}, {"l": "Replan Tetikleyiciler", "u": None}]),
    ("sp/blue_ocean.html", [{"l": "Stratejik Planlama", "u": "url_for('app_bp.sp_menu')"}, {"l": "Blue Ocean", "u": None}]),
    ("sp/vrio.html", [{"l": "Stratejik Planlama", "u": "url_for('app_bp.sp_menu')"}, {"l": "VRIO", "u": None}]),
    ("sp/scenarios.html", [{"l": "Stratejik Planlama", "u": "url_for('app_bp.sp_menu')"}, {"l": "Senaryolar", "u": None}]),
    ("sp/strateji_haritasi.html", [{"l": "Stratejik Planlama", "u": "url_for('app_bp.sp_menu')"}, {"l": "Strateji Haritası", "u": None}]),
    ("sp/donemler.html", [{"l": "Stratejik Planlama", "u": "url_for('app_bp.sp_menu')"}, {"l": "Dönemler", "u": None}]),
    ("sp/okr.html", [{"l": "Stratejik Planlama", "u": "url_for('app_bp.sp_menu')"}, {"l": "OKR", "u": None}]),
    ("sp/misyon.html", [{"l": "Stratejik Planlama", "u": "url_for('app_bp.sp_menu')"}, {"l": "Misyon", "u": None}]),
    ("sp/vizyon.html", [{"l": "Stratejik Planlama", "u": "url_for('app_bp.sp_menu')"}, {"l": "Vizyon", "u": None}]),
    ("sp/degerler.html", [{"l": "Stratejik Planlama", "u": "url_for('app_bp.sp_menu')"}, {"l": "Değerler", "u": None}]),
    # K-Analiz / K-Radar
    ("k_radar/ks.html", [{"l": "K-Analiz", "u": None}]),
    ("k_radar/kp.html", [{"l": "K-Analiz", "u": "url_for('app_bp.k_radar_ks')"}, {"l": "KP", "u": None}]),
    ("k_radar/kpr.html", [{"l": "K-Analiz", "u": "url_for('app_bp.k_radar_ks')"}, {"l": "KPR", "u": None}]),
    ("k_radar/cross.html", [{"l": "K-Analiz", "u": "url_for('app_bp.k_radar_ks')"}, {"l": "Çapraz", "u": None}]),
    # K-Radar (eski Raporlar)
    ("raporlar/index.html", [{"l": "K-Radar", "u": None}]),
    # Admin
    ("admin/yonetim_paneli.html", [{"l": "Yönetim Paneli", "u": None}]),
    ("admin/users.html", [{"l": "Yönetim Paneli", "u": "url_for('app_bp.yonetim_paneli')"}, {"l": "Kullanıcılar", "u": None}]),
    ("admin/tenants.html", [{"l": "Yönetim Paneli", "u": "url_for('app_bp.yonetim_paneli')"}, {"l": "Kurumlar", "u": None}]),
    ("admin/packages.html", [{"l": "Yönetim Paneli", "u": "url_for('app_bp.yonetim_paneli')"}, {"l": "Paketler", "u": None}]),
    ("admin/sub_tenants.html", [{"l": "Yönetim Paneli", "u": "url_for('app_bp.yonetim_paneli')"}, {"l": "Alt Kurumlar", "u": None}]),
    ("admin/sub_tenants_usage.html", [{"l": "Yönetim Paneli", "u": "url_for('app_bp.yonetim_paneli')"}, {"l": "Alt Kurum Kullanımı", "u": None}]),
    ("admin/notifications.html", [{"l": "Yönetim Paneli", "u": "url_for('app_bp.yonetim_paneli')"}, {"l": "Bildirim Logları", "u": None}]),
    ("admin/holding_dashboard.html", [{"l": "Yönetim Paneli", "u": "url_for('app_bp.yonetim_paneli')"}, {"l": "Holding Panosu", "u": None}]),
    # Diğer
    ("bireysel/karne.html", [{"l": "Bireysel Performans", "u": None}]),
    ("bildirim/index.html", [{"l": "Bildirimler", "u": None}]),
    ("ayarlar/index.html", [{"l": "Ayarlar", "u": None}]),
    ("ayarlar/eposta.html", [{"l": "Ayarlar", "u": "url_for('app_bp.ayarlar_index')"}, {"l": "E-posta", "u": None}]),
    ("ayarlar/yedekleme.html", [{"l": "Ayarlar", "u": "url_for('app_bp.ayarlar_index')"}, {"l": "Yedekleme", "u": None}]),
    ("kurum/index.html", [{"l": "Kurum", "u": None}]),
    ("kurum/ayarlar.html", [{"l": "Kurum", "u": "url_for('app_bp.kurum_index')"}, {"l": "Ayarlar", "u": None}]),
    ("analiz/index.html", [{"l": "Analiz", "u": None}]),
]


def build_block(crumbs):
    parts = []
    for c in crumbs:
        if c.get("raw"):
            label_expr = c["l"]
        else:
            label_expr = "'" + c["l"].replace("'", "\\'") + "'"
        url_expr = c["u"] if c["u"] else "None"
        parts.append("{'label': " + label_expr + ", 'url': " + url_expr + "}")
    items = "[" + ", ".join(parts) + "]"
    return (
        "{% block breadcrumb %}\n"
        "    {{ mc_breadcrumb(" + items + ") }}\n"
        "{% endblock %}\n\n"
    )


def patch(path: Path, crumbs):
    text = path.read_text(encoding="utf-8")
    if "{% block breadcrumb %}" in text:
        return "skip (var)"
    if "{% block content %}" not in text:
        return "skip (content yok)"
    block = build_block(crumbs)
    new_text = text.replace("{% block content %}", block + "{% block content %}", 1)
    path.write_text(new_text, encoding="utf-8")
    return "OK"


added = skipped = missing = 0
for rel, crumbs in PAGES:
    p = BASE / rel
    if not p.exists():
        print(f"  - {rel}: dosya yok")
        missing += 1
        continue
    r = patch(p, crumbs)
    print(f"  - {rel}: {r}")
    if r == "OK":
        added += 1
    else:
        skipped += 1

print(f"\nÖzet: eklendi={added}, atlandı={skipped}, eksik={missing}")
