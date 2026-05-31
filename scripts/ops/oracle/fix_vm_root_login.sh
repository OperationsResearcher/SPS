#!/usr/bin/env bash
# kokpitim-web: / -> login.html (marketing yok); launcher sadece /launcher
set -euo pipefail
docker cp /tmp/launcher.py kokpitim-web:/app/micro/core/launcher.py
docker exec kokpitim-web python3 << 'PY'
from pathlib import Path
p = Path("/app/main/routes.py")
t = p.read_text(encoding="utf-8")
old = '''    return redirect(url_for("marketing_bp.index"))'''
new = '''    return render_template("login.html")'''
if old in t:
    t = t.replace(old, new)
    if "render_template" not in t.split("def index")[1][:400]:
        t = t.replace(
            "from flask import",
            "from flask import render_template,",
            1,
        )
    p.write_text(t, encoding="utf-8")
    print("main/routes.py index OK")
else:
    print("main/routes.py skip (already patched?)")
PY
docker restart kokpitim-web
echo done
