# -*- coding: utf-8 -*-
"""innerHTML'e kaçışsız kullanıcı/hata verisi basılmaz (Faz 0.6, G9)."""
import re
from pathlib import Path

JS = Path(__file__).resolve().parent.parent / "ui/static/platform/js"
ESC = re.compile(r"esc\(|escHtml\(|escAttr\(|mcEsc\(|escapeHtml\(")

# Kaçışsız bırakılması riskli ifadeler (hata mesajı, kullanıcı adlı alanlar).
RISKLI = re.compile(r"\$\{\s*(?:String\()?\s*(?:err|e|error)\.message|\$\{\s*py\.name\b")


def test_riskli_ifadeler_kacisli():
    ihlal = []
    for f in JS.glob("*.js"):
        for n, line in enumerate(f.read_text("utf-8", "ignore").splitlines(), 1):
            if "innerHTML" in line and RISKLI.search(line) and not ESC.search(line):
                ihlal.append(f"{f.name}:{n}")
    assert ihlal == []


def test_py_name_launcher_kacisli():
    src = (JS / "launcher_vgs.js").read_text("utf-8")
    assert "esc(py.name)" in src and "${py.name}" not in src
