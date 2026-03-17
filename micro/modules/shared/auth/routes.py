"""Auth sayfaları — micro platform için profil ve ayarlar.

Login/logout işlemleri mevcut auth_bp'ye yönlendirilir.
Micro'ya özel login sayfası da burada tanımlanır.
"""

import json

from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user

from micro import micro_bp


@micro_bp.route("/login")
def micro_login():
    """Micro platform login sayfası — zaten giriş yapıldıysa launcher'a yönlendir."""
    if current_user.is_authenticated:
        return redirect(url_for("micro_bp.launcher"))
    return render_template("micro/auth/login.html")


@micro_bp.route("/profil", methods=["GET", "POST"])
@login_required
def profil():
    """Profil sayfası — mevcut auth_bp.profile ile aynı mantık, micro UI."""
    if request.method == "POST":
        # POST işlemini mevcut auth_bp.profile'a yönlendir
        return redirect(url_for("auth_bp.profile"), code=307)
    return render_template("micro/auth/profil.html")


@micro_bp.route("/ayarlar")
@login_required
def ayarlar():
    """Ayarlar hub sayfası."""
    return render_template("micro/ayarlar/index.html")


@micro_bp.route("/ayarlar/hesap", methods=["GET", "POST"])
@login_required
def ayarlar_hesap():
    """Kişisel hesap ayarları — mevcut auth_bp.settings ile aynı mantık, micro UI."""
    if request.method == "POST":
        return redirect(url_for("auth_bp.settings"), code=307)

    # GET — mevcut ayarları yükle
    def _parse_json(val, default=None):
        if default is None:
            default = {}
        if not val:
            return default
        try:
            return json.loads(val) if isinstance(val, str) else (val or default)
        except (ValueError, TypeError):
            return default

    notif_prefs = _parse_json(getattr(current_user, "notification_preferences", None), {
        "email": True, "process": True, "task": True, "deadline": True
    })
    locale_prefs = _parse_json(getattr(current_user, "locale_preferences", None), {
        "language": "tr", "timezone": "Europe/Istanbul", "date_format": "dd.mm.yyyy"
    })
    theme_prefs = _parse_json(getattr(current_user, "theme_preferences", None), {
        "theme": "light", "color": "primary"
    })

    return render_template(
        "micro/auth/ayarlar.html",
        notif_prefs=notif_prefs,
        locale_prefs=locale_prefs,
        theme_prefs=theme_prefs,
        show_page_guides=getattr(current_user, "show_page_guides", True),
        guide_character_style=getattr(current_user, "guide_character_style", "professional"),
    )
