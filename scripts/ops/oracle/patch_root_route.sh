#!/usr/bin/env bash
# Container icinde kokpitim-web: / kokusu login_required launcher -> marketing
set -euo pipefail
FILE=/app/micro/core/launcher.py
if grep -q 'platform_root' "$FILE" 2>/dev/null; then
  echo "launcher.py zaten platform_root icin guncel"
  exit 0
fi
python3 << 'PY'
from pathlib import Path
p = Path("/app/micro/core/launcher.py")
text = p.read_text(encoding="utf-8")
old = '''@app_bp.route("/")
@login_required
def launcher():
    """Modül launcher ekranı."""
    modules = get_accessible_modules(current_user)
    ctx = _get_plan_year_context()
    return render_template("platform/launcher.html", modules=modules, **ctx)'''
new = '''@app_bp.route("/launcher")
@login_required
def launcher():
    """Modül launcher ekranı."""
    modules = get_accessible_modules(current_user)
    ctx = _get_plan_year_context()
    return render_template("platform/launcher.html", modules=modules, **ctx)


@app_bp.route("/")
def platform_root():
    """Kök — oturum varsa launcher, yoksa tanıtım."""
    from flask import redirect
    from flask_login import current_user as _cu
    if _cu.is_authenticated:
        return redirect(url_for("app_bp.launcher"))
    return redirect(url_for("marketing_bp.index"))'''
if old not in text:
    raise SystemExit("launcher pattern not found")
if "from flask import redirect" not in text:
    text = text.replace(
        "from flask import render_template",
        "from flask import redirect, render_template",
        1,
    )
p.write_text(text.replace(old, new), encoding="utf-8")
print("launcher.py patched")
PY
