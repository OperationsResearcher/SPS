# -*- coding: utf-8 -*-
"""Legacy main route handler'ları için GET yedek yönlendirme (middleware kapalıysa)."""
from __future__ import annotations

from functools import wraps

from flask import redirect, request, url_for

from app.legacy_redirect_config import EXACT_ENDPOINT


def legacy_html_to_platform(f):
    """GET/HEAD isteklerini platform endpoint'ine yönlendir; POST/PUT/DELETE olduğu gibi."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.method in ("GET", "HEAD"):
            endpoint = EXACT_ENDPOINT.get(request.path)
            if endpoint:
                return redirect(url_for(endpoint, **request.args), code=301)
        return f(*args, **kwargs)

    return wrapper
