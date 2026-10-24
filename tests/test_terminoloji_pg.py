# -*- coding: utf-8 -*-
"""Türkçe arayüzde "KPI" yazılmaz, "PG" kullanılır (Faz 2.5, dil birliği; UI-TERMINOLOJI.md).

Kapsam: çeviri çağrılarındaki (`_()`, `t()`, `gettext`) literaller ve şablonlardaki düz etiket metni.
Veri kodları (`KPI-327`) kimliktir, kapsam dışı. İngilizce çeviri (msgstr) "KPI" kalabilir.
"""
import re
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
BS, DQ, SQ = chr(92), chr(34), chr(39)


def _lit(q):
    return q + "(?:[^" + q + BS + BS + "]|" + BS + BS + ".)*" + q


CEVIRI = re.compile("(?:" + BS + "b_|" + BS + "bt|" + BS + "bgettext)" + BS + "(" + BS + "s*(" + _lit(DQ) + "|" + _lit(SQ) + ")")
ETIKET = re.compile("(>|</i>)" + BS + "s*KPI" + BS + "s*(<|" + BS + "n)")
KPI = re.compile(BS + "bKPI" + BS + "b(?!-" + BS + "d)")

DOSYALAR = [p for d, uz in (("ui/templates", ".html"), ("ui/static/platform/js", ".js"), ("app", ".py"),
                            ("micro", ".py"), ("services", ".py"), ("api", ".py"))
            for p in (KOK / d).rglob("*" + uz) if "_arsiv" not in p.parts and "__pycache__" not in p.parts]


def test_turkce_arayuzde_kpi_yok():
    ihlal = []
    for p in DOSYALAR:
        txt = p.read_text("utf-8", "ignore")
        for m in CEVIRI.finditer(txt):
            if KPI.search(m.group(1)[1:-1]):
                ihlal.append(f"{p.relative_to(KOK).as_posix()}: {m.group(1)[:60]}")
        if p.suffix == ".html" and ETIKET.search(txt):
            ihlal.append(f"{p.relative_to(KOK).as_posix()}: >KPI< etiketi")
    assert not ihlal, "Türkçe arayüzde 'KPI' yerine 'PG' yazın:\n" + "\n".join(ihlal[:20])


def test_tr_katalogunda_kpi_msgid_yok():
    from babel.messages.pofile import read_po

    cat = read_po((KOK / "translations/tr/LC_MESSAGES/messages.po").open("rb"), locale="tr")
    kalan = [m.id for m in cat if isinstance(m.id, str) and KPI.search(m.id)]
    assert not kalan, kalan[:10]
