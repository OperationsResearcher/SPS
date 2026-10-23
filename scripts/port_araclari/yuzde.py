# -*- coding: utf-8 -*-
"""_() içinde kaçışsız tek % arar (newstyle gettext % biçimlendirmesi yapar)."""
import re, sys
sys.stdout.reconfigure(encoding="utf-8")
PAT = [re.compile(r'_\("((?:[^"\\]|\\.)*)"\)'), re.compile(r"_\('((?:[^'\\]|\\.)*)'\)")]
for f in sys.argv[1:]:
    t = open(f"ui/templates/platform/{f}.html", encoding="utf-8-sig").read()
    for P in PAT:
        for m in P.finditer(t):
            s = m.group(1)
            if re.search(r"%(?!%|\()", s):
                print(f, m.start(), repr(s[:80]))
