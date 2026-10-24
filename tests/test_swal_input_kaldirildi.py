# -*- coding: utf-8 -*-
"""UX-PLANI D / Faz 2.6: Swal `input:` formu kalmadı; yerine openMcTextPrompt (alan altı doğrulama)."""
import re
from pathlib import Path

JS = Path(__file__).resolve().parent.parent / "ui" / "static" / "platform" / "js"
SWAL_INPUT = re.compile(r"""\binput\s*:\s*["'](text|textarea|number|select|date|email|password)["']""")


def test_swal_input_formu_kalmadi():
    kalan = []
    for f in JS.glob("*.js"):
        if f.name.endswith(".min.js"):
            continue
        for n, satir in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if SWAL_INPUT.search(satir):
                kalan.append(f"{f.name}:{n}")
    assert kalan == [], "Swal input: yerine openMcTextPrompt kullan: " + ", ".join(kalan)


def test_ortak_istem_yardimcisi_alan_altinda_hata_gosterir():
    kaynak = (JS / "mc-modal-form.js").read_text(encoding="utf-8")
    assert "window.openMcTextPrompt" in kaynak
    assert 'id="mc-prompt-error"' in kaynak and 'role="alert"' in kaynak
