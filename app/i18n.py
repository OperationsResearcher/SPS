"""i18n altyapısı (Sprint 28).

Flask-Babel kurulumu. Şu an iskelet — gerçek çeviri Sprint 32+'da yapılacak.

Konfigürasyon (.env):
    BABEL_DEFAULT_LOCALE=tr
    BABEL_DEFAULT_TIMEZONE=Europe/Istanbul
    BABEL_SUPPORTED_LOCALES=tr,en

Kullanım (template):
    {{ _("Hoş geldiniz") }}

Kullanım (Python):
    from flask_babel import gettext as _
    flash(_("Profil güncellendi"), "success")

Locale seçim sırası:
    1. ?lang=en URL parametresi
    2. session['lang']
    3. user.locale_preferences JSON (language alanı)
    4. Accept-Language header
    5. BABEL_DEFAULT_LOCALE
"""
from __future__ import annotations

import json
from typing import Optional


def get_locale() -> str:
    """Aktif locale'i belirle. Babel'in locale_selector'ı."""
    from flask import request, session, current_app
    from flask_login import current_user

    supported = current_app.config.get("BABEL_SUPPORTED_LOCALES", ["tr", "en"])

    # 1. URL parametresi
    lang = request.args.get("lang")
    if lang in supported:
        session["lang"] = lang
        return lang

    # 2. Session
    lang = session.get("lang")
    if lang in supported:
        return lang

    # 3. User locale_preferences
    if current_user.is_authenticated:
        try:
            prefs = current_user.locale_preferences
            if prefs:
                if isinstance(prefs, str):
                    prefs = json.loads(prefs)
                lang = (prefs or {}).get("language")
                if lang in supported:
                    return lang
        except (ValueError, TypeError):
            pass

    # 4. Accept-Language
    try:
        best = request.accept_languages.best_match(supported)
        if best:
            return best
    except Exception as e:
        current_app.logger.warning(f"[get_locale] suppressed: {e}")

    # 5. Default
    return current_app.config.get("BABEL_DEFAULT_LOCALE", "tr")


def js_i18n_map() -> dict:
    """Aktif locale için {kaynak_msgid: çeviri} sözlüğü.

    JS tarafında window.t() helper'ı bu map'i kullanır (FAZ 4). Yalnızca
    aktif dilde gerçek çevirisi olan (msgstr dolu) girdiler döner; default
    dil (tr) için boş sözlük döner çünkü JS literal'leri zaten Türkçe.
    """
    from flask import current_app
    default = current_app.config.get("BABEL_DEFAULT_LOCALE", "tr")
    try:
        # Babel'in aktif locale'i (force_locale dahil doğru değer) — bizim
        # session-tabanlı get_locale() force_locale'i görmez.
        from flask_babel import get_locale as _babel_locale
        locale = str(_babel_locale() or default)
    except Exception:
        locale = default
    if locale == default:
        return {}
    try:
        from flask_babel import get_translations, gettext
        gettext("")  # lazy catalog yüklemesini tetikle
        trans = get_translations()  # aktif locale'in gettext.GNUTranslations'ı
        catalog = getattr(trans, "_catalog", {}) or {}
        out = {}
        for key, val in catalog.items():
            # _catalog: {msgid: msgstr} ve {(msgid, idx): plural}. Sadece düz string id'ler.
            if isinstance(key, str) and key and isinstance(val, str) and val and key != val:
                out[key] = val
        return out
    except Exception:
        return {}


def init_babel(app):
    """Babel'i app'e kaydet."""
    # get_locale her durumda template'lerde kullanılabilir olsun (Babel yoksa da fallback döner).
    @app.context_processor
    def _inject_get_locale():
        def _safe_locale():
            try:
                return get_locale()
            except Exception:
                return app.config.get("BABEL_DEFAULT_LOCALE", "tr")
        return {"get_locale": _safe_locale, "js_i18n_map": js_i18n_map}

    try:
        from flask_babel import Babel
    except ImportError:
        app.logger.warning("[i18n] Flask-Babel kurulu değil — i18n atlandı")
        return None

    # Defaults
    app.config.setdefault("BABEL_DEFAULT_LOCALE", "tr")
    app.config.setdefault("BABEL_DEFAULT_TIMEZONE", "Europe/Istanbul")
    app.config.setdefault("BABEL_SUPPORTED_LOCALES", ["tr", "en"])
    # translations/ proje KÖKÜNDE (app.root_path = .../app, kök bir üst). Mutlak yol şart:
    # göreli "translations" Flask-Babel'de app.root_path'e göre çözülür → app/translations (yanlış).
    import os as _os
    _trans_dir = _os.path.join(_os.path.dirname(app.root_path), "translations")
    app.config.setdefault("BABEL_TRANSLATION_DIRECTORIES", _trans_dir)

    babel = Babel(app, locale_selector=get_locale)
    app.logger.info(f"[i18n] Babel başlatıldı. Default: {app.config['BABEL_DEFAULT_LOCALE']}")
    return babel
