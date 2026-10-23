# -*- coding: utf-8 -*-
"""Koşulsuz alert()/confirm()/prompt() yasağı (Faz S.7, KURALLAR §3): SweetAlert2 kullanılır.

SweetAlert2 yüklenemezse devreye giren `else alert(...)` YEDEKLERİ BASELINE'dadır (Swal base.html'de
global yüklü; yedekler fiilen ölü kod). Yeni çağrı testi kırar.
"""
import re
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
ARAMA = [KOK / "ui/static/platform/js", KOK / "ui/templates"]
CAGRI = re.compile(r"(?<![.\w])(alert|confirm|prompt)\s*\(")

# SweetAlert2-yok yedekleri ("if (window.Swal) … else alert(…)") — dosya::çağrı.
BASELINE = {
    "ui/static/platform/js/reports/veri_kalitesi.js::alert",
    "ui/static/platform/js/sp_analiz.js::alert",
    "ui/static/platform/js/totp_setup.js::alert",
    "ui/static/platform/js/twofa.js::alert",
    "ui/templates/platform/surec/index.html::alert",
    "ui/templates/platform/admin/yedekleme.html::confirm",
    "ui/static/platform/js/sp_projeler.js::confirm",
}


def _bulunan():
    out = set()
    for kok in ARAMA:
        for p in kok.rglob("*"):
            if p.suffix not in (".js", ".html"):
                continue
            for satir in p.read_text("utf-8", "ignore").splitlines():
                s = satir.strip()
                if s.startswith(("//", "*", "/*", "{#")):
                    continue
                for m in CAGRI.finditer(satir):
                    out.add(f"{p.relative_to(KOK).as_posix()}::{m.group(1)}")
    return out


def test_yeni_alert_confirm_yok():
    yeni = _bulunan() - BASELINE
    assert not yeni, "alert/confirm/prompt yerine SweetAlert2 kullanın: " + ", ".join(sorted(yeni))
