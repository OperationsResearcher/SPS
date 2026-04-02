# -*- coding: utf-8 -*-
"""Micro proje — display yardımcıları (DB gerektirmez)."""

from app_platform.modules.proje.display import user_display


def test_user_display_missing_id():
    assert user_display({}, None, None) == "—"


def test_user_display_map_hit():
    labels = {1: "Ali Veli (a@x.com)"}
    assert user_display(labels, 1, None) == "Ali Veli (a@x.com)"


def test_user_display_fallback_numeric():
    assert user_display({}, 99, None) == "#99"
