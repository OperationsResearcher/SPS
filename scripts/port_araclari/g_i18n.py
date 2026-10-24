# -*- coding: utf-8 -*-
"""Şablonlardaki sabit metni {{ _() }} ile sarar. Kullanım: python g_i18n.py <sablon_rel> [...]"""
import re, sys, html
from pathlib import Path

ROOT = Path("ui/templates/platform")
KORUMA = re.compile(r"<script\b.*?</script>|<style\b.*?</style>|\{#.*?#\}|<!--.*?-->|\{%.*?%\}|\{\{.*?\}\}", re.S | re.I)
HARF = re.compile(r"[A-Za-zÇĞİÖŞÜçğıöşüÂâÎîÛû]")
METIN = re.compile(r">([^<>]+)<")
ATTR = re.compile(r'(\s(?:title|placeholder|aria-label|alt))="([^"{}]*)"')
LABEL = re.compile(r"""('label'\s*:\s*)'([^'{}]*)'""")
BLOK = re.compile(r"(\{%\s*block\s+(?:title|page_title)\s*%\})([^{}%]+?)(\{%\s*endblock\s*%\})")


def esc_d(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def esc_s(s):
    return s.replace("\\", "\\\\").replace("'", "\\'")


def norm(raw):
    return " ".join(html.unescape(raw).split()).replace("%", "%%")


def sar_dosya(rel):
    p = ROOT / rel
    raw = p.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    t = raw.decode("utf-8-sig")
    crlf = "\r\n" in t
    t = t.replace("\r\n", "\n")
    n = {"metin": 0, "attr": 0, "label": 0, "blok": 0}

    maske = KORUMA.sub(lambda m: "\x00" * len(m.group(0)), t)
    out, son = [], 0
    # 1) metin düğümleri
    for m in METIN.finditer(maske):
        s, e = m.start(1), m.end(1)
        parca = t[s:e]
        if "\x00" in maske[s:e]:
            continue
        txt = norm(parca)
        if len(txt) < 2 or not HARF.search(txt):
            continue
        if re.fullmatch(r"[\W\d_]*", txt):
            continue
        lead = parca[: len(parca) - len(parca.lstrip())]
        trail = parca[len(parca.rstrip()):]
        out.append(t[son:s]); out.append(f'{lead}{{{{ _("{esc_d(txt)}") }}}}{trail}'); son = e
        n["metin"] += 1
    out.append(t[son:])
    t = "".join(out)

    # 2) öznitelikler (yeniden maskele)
    maske = KORUMA.sub(lambda m: "\x00" * len(m.group(0)), t)
    out, son = [], 0
    for m in ATTR.finditer(maske):
        if "\x00" in maske[m.start():m.end()]:
            continue
        deger = t[m.start(2):m.end(2)]
        txt = norm(deger)
        if not HARF.search(txt) or re.fullmatch(r"[\W\d_]*", txt):
            continue
        out.append(t[son:m.start(2)]); out.append(f"{{{{ _('{esc_s(txt)}') }}}}"); son = m.end(2)
        n["attr"] += 1
    out.append(t[son:])
    t = "".join(out)

    # 3) breadcrumb label ve blok başlıkları
    def lab(m):
        if "_(" in m.group(2):
            return m.group(0)
        n["label"] += 1
        return f"{m.group(1)}_('{esc_s(norm(m.group(2)))}')"
    t = LABEL.sub(lab, t)

    def blok(m):
        txt = norm(m.group(2))
        if not HARF.search(txt):
            return m.group(0)
        n["blok"] += 1
        return f'{m.group(1)}{{{{ _("{esc_d(txt)}") }}}}{m.group(3)}'
    t = BLOK.sub(blok, t)

    if crlf:
        t = t.replace("\n", "\r\n")
    p.write_bytes((b"\xef\xbb\xbf" if bom else b"") + t.encode("utf-8"))
    print(rel, n)


if __name__ == "__main__":
    for r in sys.argv[1:]:
        sar_dosya(r)
