# -*- coding: utf-8 -*-
"""i18n çıkarım sarmalayıcısı: .po güncellerken çevirilerin "obsolete"e düşmesini önler.

NEDEN: `pybabel extract -F babel.cfg` iki yerde kör:
  1. Şablon içindeki satır içi JS (`<script>` içinde `t("…")`) — jinja2 çıkarıcı JS görmez (656 çağrı).
  2. `_l(...)` (lazy_gettext takma adı, app/constants/roles.py).
Bu iki kaynağın çevirileri `pybabel update`te "obsolete" (`#~`) bölümüne düşüyordu; arayüz EN'de Türkçe kalıyordu.

Bu betik: (a) `-k t -k _l` ile normal çıkarım, (b) şablonlardaki satır içi `t("…")` çağrılarını regex ile ekler,
(c) POT'u yazar, (d) .po'larda "POT'ta olmayan ama dolu çevirili" girdileri raporlar (obsolete adayı).

Kullanım:
    python scripts/ops/i18n_cikar.py            # KONTROL: yalnız rapor, .po'ya dokunmaz
    python scripts/ops/i18n_cikar.py --yaz      # pybabel update --no-fuzzy-matching + compile

Not: --yaz tüm .po dosyalarını yeniden yazar (büyük diff). Commitlenmemiş .po değişikliğin varsa önce commit et.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from babel.messages.pofile import read_po, write_po

KOK = Path(__file__).resolve().parents[2]
SABLON = KOK / "ui" / "templates"
INLINE_T = re.compile(r"""\bt\(\s*("(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*')""")


def _frontend(*args: str) -> None:
    env = dict(os.environ, PYTHONUTF8="1")
    subprocess.run([sys.executable, "-m", "babel.messages.frontend", *args], cwd=KOK, env=env, check=True)


def main() -> int:
    yaz = "--yaz" in sys.argv
    tmp = Path(tempfile.mkdtemp()) / "messages.pot"
    _frontend("extract", "-F", "babel.cfg", "-k", "t", "-k", "_l", "-o", str(tmp), ".")
    cat = read_po(open(tmp, "rb"))
    ilk = len([m for m in cat if m.id])

    eklenen = 0
    for f in SABLON.rglob("*.html"):
        metin = f.read_text(encoding="utf-8-sig", errors="ignore")
        for m in INLINE_T.finditer(metin):
            try:
                mid = ast.literal_eval(m.group(1))
            except (ValueError, SyntaxError):
                continue
            if not isinstance(mid, str) or not mid.strip():
                continue
            if mid not in cat:
                satir = metin.count("\n", 0, m.start()) + 1
                cat.add(mid, locations=[(f.relative_to(KOK).as_posix(), satir)])
                eklenen += 1
    pot = (KOK / "translations" / "messages.pot") if yaz else tmp
    with open(pot, "wb") as fh:
        write_po(fh, cat, width=120)
    print(f"POT: {ilk} normal + {eklenen} satır içi JS = {ilk + eklenen} msgid -> {pot}")

    po = read_po(open(KOK / "translations" / "en" / "LC_MESSAGES" / "messages.po", "rb"), locale="en")
    ids = {m.id for m in cat if m.id}
    kayip = [m.id for m in po if m.id and m.string and m.id not in ids]
    print(f"EN .po'da dolu çevirili ama POT'ta OLMAYAN (obsolete adayı): {len(kayip)}")
    for k in kayip[:10]:
        print("  -", repr(k)[:90])

    if yaz:
        _frontend("update", "-i", str(pot), "-d", "translations", "--no-fuzzy-matching")
        _frontend("compile", "-d", "translations")
        print("update + compile tamam.")
    else:
        print("KONTROL modu: .po değişmedi. Uygulamak için --yaz")
    return 0


if __name__ == "__main__":
    sys.exit(main())
