# -*- coding: utf-8 -*-
"""UX-PLANI F / WCAG AA: metin token'ları ve başlıca buton/rozet çiftleri >= 4.5:1."""
import re
from pathlib import Path

CSS = (Path(__file__).resolve().parent.parent / "ui/static/platform/css/components.css").read_text(encoding="utf-8")


def _lum(h):
    h = h.lstrip("#")
    r = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r[0]) + 0.7152 * f(r[1]) + 0.0722 * f(r[2])


def _oran(a, b):
    x, y = sorted((_lum(a), _lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


def _tok(ad, blok):
    return re.search(r"--%s:\s*(#[0-9a-fA-F]{6})" % ad, blok).group(1)


def _acik():
    return CSS[: CSS.index("html.dark {")]


def _koyu():
    s = CSS.index("html.dark {")
    return CSS[s: CSS.index("}", s)]


def _kural(sel):
    m = re.search(re.escape(sel) + r"\s*\{([^}]*)\}", CSS)
    return dict(re.findall(r"([\w-]+):\s*([^;]+);", m.group(1)))


def test_acik_tema_metin_tokenlari():
    a = _acik()
    for yuzey in ("#ffffff", _tok("surface-page", a), _tok("surface-hover", a)):
        for t in ("text-default", "text-muted", "text-subtle"):
            assert _oran(_tok(t, a), yuzey) >= 4.5, (t, yuzey)


def test_koyu_tema_metin_tokenlari():
    k = _koyu()
    for yuzey in (_tok("surface-card", k), _tok("surface-hover", k)):
        for t in ("text-default", "text-muted", "text-subtle"):
            assert _oran(_tok(t, k), yuzey) >= 4.5, (t, yuzey)


def test_buton_ve_rozet_ciftleri():
    for sel in (".mc-btn-danger", ".mc-btn-success", ".mc-badge-success", ".mc-badge-warning",
                ".mc-badge-danger", ".mc-badge-info", ".mc-badge-gray"):
        d = _kural(sel)
        bg = re.search(r"#[0-9a-fA-F]{6}", d["background"]).group(0)
        assert _oran(d["color"].strip(), bg) >= 4.5, sel
    h = _kural(".mc-btn-success:hover")
    assert _oran("#ffffff", h["background"].strip()) >= 4.5
    assert _oran(re.search(r"\.dark \.mc-badge-gray\s*\{[^}]*color:\s*(#\w+)", CSS).group(1), "#334155") >= 4.5
