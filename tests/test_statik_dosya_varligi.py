"""Şablonların istediği statik dosyalar GERÇEKTEN var mı? (TASK-278)

NEDEN BU TEST VAR:
    Commit ed713231 (URL tek-dil taşıması) şablonlardaki JS yolunu
    `platform/js/raporlar/` → `platform/js/reports/` yaptı ama **klasörü
    taşımadı**. Sonuç: 36 rapor sayfasının JS'i 404 döndü. Sayfa açılıyordu,
    sunucu 200 veriyordu, API çalışıyordu — ama JS yüklenmediği için ekran
    sonsuza kadar "Yükleniyor…" spinner'ında kalıyordu.

    Hiçbir test bunu yakalamadı: 602 test geçiyordu. Çünkü testler HTTP
    yanıtına bakıyor, şablonun referans verdiği statik dosyanın diskte var
    olup olmadığına bakmıyor.

    Bu test o boşluğu kapatır: url_for('app_bp.static', filename=...) ile
    istenen her dosya diskte olmalı.
"""
import pathlib
import re

import pytest

_KOK = pathlib.Path(__file__).resolve().parents[1]
_TEMPLATES = _KOK / "ui" / "templates"
_STATIC = _KOK / "ui" / "static"

# url_for('app_bp.static', filename='platform/js/x.js') → 'platform/js/x.js'
_PAT = re.compile(
    r"""url_for\(\s*['"]app_bp\.static['"]\s*,\s*filename\s*=\s*['"]([^'"]+)['"]"""
)


def _referanslar():
    """(şablon, istenen_dosya) çiftleri — Jinja değişkeni içerenler atlanır."""
    for tpl in sorted(_TEMPLATES.rglob("*.html")):
        icerik = tpl.read_text(encoding="utf-8", errors="ignore")
        for m in _PAT.finditer(icerik):
            hedef = m.group(1)
            if "{" in hedef or "~" in hedef:
                continue  # dinamik yol — statik olarak çözülemez
            yield tpl.relative_to(_KOK).as_posix(), hedef


_REFS = sorted(set(_referanslar()))


def test_referans_bulundu():
    """Tarama çalışıyor mu (regex bozulursa test sessizce boş geçmesin)."""
    assert len(_REFS) > 50, f"Yalnız {len(_REFS)} statik referans bulundu — regex bozuk?"


@pytest.mark.parametrize("tpl,hedef", _REFS)
def test_sablonun_istedigi_statik_dosya_diskte_var(tpl, hedef):
    """Şablon bir statik dosya istiyorsa o dosya diskte olmalı.

    Kırılırsa: ya dosya taşındı/silindi ve şablon güncellenmedi, ya da şablon
    güncellendi ve dosya taşınmadı (ed713231'de bu oldu → 36 sayfa spinner).
    """
    yol = _STATIC / hedef
    assert yol.is_file(), (
        f"{tpl} → '{hedef}' istiyor ama {yol} YOK.\n"
        f"Tarayıcıda 404 → JS/CSS yüklenmez → sayfa sessizce bozulur."
    )
