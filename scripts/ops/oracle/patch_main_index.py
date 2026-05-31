import re
from pathlib import Path

p = Path("/app/main/routes.py")
text = p.read_text(encoding="utf-8")
new_fn = '''@main_bp.route('/')
def index():
    """Kök — giriş ekranı (login.html); oturum varsa launcher."""
    if current_user.is_authenticated:
        return redirect(url_for('app_bp.launcher'))
    return render_template("auth/login.html")
'''
text, n = re.subn(
    r"@main_bp\.route\('/'\)\ndef index\(\):.*?(?=\n@main_bp\.route|\n@main_bp\.route|\Z)",
    new_fn + "\n",
    text,
    count=1,
    flags=re.DOTALL,
)
if n != 1:
    raise SystemExit(f"index block not replaced (n={n})")
p.write_text(text, encoding="utf-8")
print("OK")
