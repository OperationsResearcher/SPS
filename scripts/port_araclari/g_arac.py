# -*- coding: utf-8 -*-
"""Statik inline style= -> sinif. Kullanim: python g_arac.py <sablon_rel> <on_ek> <css_adi>"""
import re, sys
from pathlib import Path

ROOT = Path("ui/templates/platform")
CSSDIR = Path("ui/static/platform/css")
KORUMA = re.compile(r"<script\b.*?</script>|<style\b.*?</style>|\{#.*?#\}|<!--.*?-->|\{%.*?%\}|\{\{.*?\}\}", re.S | re.I)
ETIKET = re.compile(r"<([a-zA-Z][\w-]*)((?:[^<>\"']|\"[^\"]*\"|'[^']*')*)>", re.S)
STIL = re.compile(r'\sstyle="([^"]*)"')
GIZLI = re.compile(r"display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0\b", re.I)
SINIF = re.compile(r'\sclass="([^"]*)"')


def norm(v):
    v = " ".join(v.split()).strip()
    if v and not v.endswith(";"):
        v += ";"
    return v


def calis(rel, onek, cssad):
    p = ROOT / rel
    raw = p.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    crlf = "\r\n" in text
    text = text.replace("\r\n", "\n")
    # koruma: Jinja/script/style/yorum alanlarini ayni uzunlukta maskele
    maske = KORUMA.sub(lambda m: "\x00" * len(m.group(0)), text)
    haritasi, sayac = {}, [0]

    def sinif_adi(v):
        if v not in haritasi:
            sayac[0] += 1
            haritasi[v] = f"{onek}-{sayac[0]:03d}"
        return haritasi[v]

    out, son, dizi_eski = [], 0, []
    for m in ETIKET.finditer(maske):
        s, e = m.span()
        if "\x00" in text[s:e] and False:
            pass
        tag = text[s:e]
        mm = maske[s:e]
        if "\x00" in mm and len(re.findall(r"\sclass\s*=", tag)) > 1:
            continue
        sm = STIL.search(tag)
        if not sm:
            continue
        v = sm.group(1)
        if "{{" in v or "{%" in v or GIZLI.search(v) or "url(" in v or "!important" in v or not v.strip():
            continue
        if len(STIL.findall(tag)) != 1:
            continue
        ad = sinif_adi(norm(v))
        yeni = tag[: sm.start()] + tag[sm.end():]
        cm = SINIF.search(yeni)
        if cm:
            yeni = yeni[: cm.end() - 1] + " " + ad + yeni[cm.end() - 1:]
        else:
            ta = re.match(r"<[a-zA-Z][\w-]*", yeni).end()
            yeni = yeni[:ta] + f' class="{ad}"' + yeni[ta:]
        out.append(text[son:s]); out.append(yeni); son = e
    out.append(text[son:])
    yeni_text = "".join(out)
    if not haritasi:
        print(rel, "degisiklik yok"); return
    # css
    css = ["/* Üretildi: inline style= → sınıf (UX-PLANI G devam). Görünüm değişmez; .x.x = inline stilin özgüllüğünü taklit eder. */"]
    for v, ad in haritasi.items():
        css.append(f".{ad}.{ad} {{ {v} }}")
    (CSSDIR / cssad).write_text("\n".join(css) + "\n", encoding="utf-8")
    # link
    link = "<link rel=\"stylesheet\" href=\"{{ url_for('app_bp.static', filename='platform/css/" + cssad + "') }}?v={{ config['VERSION'] }}\">"
    if "{% block extra_css %}" in yeni_text:
        yeni_text = yeni_text.replace("{% block extra_css %}", "{% block extra_css %}\n" + link, 1) if False else re.sub(r"(\{% block extra_css %\}.*?)(\{% endblock %\})", lambda mo: mo.group(1) + link + "\n" + mo.group(2), yeni_text, count=1, flags=re.S)
    else:
        i = yeni_text.index("{% block content %}")
        yeni_text = yeni_text[:i] + "{% block extra_css %}\n" + link + "\n{% endblock %}\n\n" + yeni_text[i:]
    if crlf:
        yeni_text = yeni_text.replace("\n", "\r\n")
    p.write_bytes((b"\xef\xbb\xbf" if bom else b"") + yeni_text.encode("utf-8"))
    print(rel, len(haritasi), "sinif")


if __name__ == "__main__":
    calis(*sys.argv[1:4])
