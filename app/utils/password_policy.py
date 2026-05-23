"""Password complexity policy (Sprint 22).

Konfigürasyon (config.py):
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPER = True
    PASSWORD_REQUIRE_LOWER = True
    PASSWORD_REQUIRE_DIGIT = True
    PASSWORD_REQUIRE_SPECIAL = False  # opsiyonel

Kullanım:
    from app.utils.password_policy import validate_password

    ok, errors = validate_password("Test1234!")
    if not ok:
        flash(", ".join(errors), "danger")
        return
"""
from __future__ import annotations

import re
from typing import Optional

from flask import current_app


# Yaygın zayıf şifreler (top 100'den seçilmiş subset)
_COMMON_WEAK = {
    "123456", "password", "12345678", "qwerty", "abc123", "111111",
    "1234567", "iloveyou", "admin", "welcome", "monkey", "login",
    "test1234", "passw0rd", "password1", "password123", "letmein",
    "12345", "1234567890", "qwerty123", "123123", "000000",
    # Türkçe yaygın
    "şifre", "sifre123", "1q2w3e4r", "asd123", "asdasd", "trabzon",
    "fenerbahce", "galatasaray", "besiktas",
}


def validate_password(pwd: str, username: Optional[str] = None) -> tuple[bool, list[str]]:
    """Şifre güvenlik kuralları."""
    cfg = current_app.config if current_app else {}
    errors: list[str] = []

    min_len = int(cfg.get("PASSWORD_MIN_LENGTH", 8))
    req_upper = bool(cfg.get("PASSWORD_REQUIRE_UPPER", True))
    req_lower = bool(cfg.get("PASSWORD_REQUIRE_LOWER", True))
    req_digit = bool(cfg.get("PASSWORD_REQUIRE_DIGIT", True))
    req_special = bool(cfg.get("PASSWORD_REQUIRE_SPECIAL", False))

    if not pwd:
        return False, ["Şifre boş olamaz."]

    if len(pwd) < min_len:
        errors.append(f"Şifre en az {min_len} karakter olmalı.")

    if req_upper and not re.search(r"[A-ZÇĞİÖŞÜ]", pwd):
        errors.append("En az bir BÜYÜK harf gereklidir.")
    if req_lower and not re.search(r"[a-zçğıöşü]", pwd):
        errors.append("En az bir küçük harf gereklidir.")
    if req_digit and not re.search(r"\d", pwd):
        errors.append("En az bir rakam gereklidir.")
    if req_special and not re.search(r"[!@#$%^&*()_+\-=\[\]{};:'\",.<>/?\\|`~]", pwd):
        errors.append("En az bir özel karakter (!@#$%^&* vb.) gereklidir.")

    if pwd.lower() in _COMMON_WEAK:
        errors.append("Bu şifre çok yaygın — daha güçlü bir şifre seçin.")

    if username and pwd.lower() == username.lower():
        errors.append("Şifre kullanıcı adıyla aynı olamaz.")

    return len(errors) == 0, errors


def password_strength(pwd: str) -> int:
    """Şifre kuvveti (0-100). UI'da progress bar için."""
    if not pwd:
        return 0
    score = 0
    # Uzunluk
    score += min(len(pwd) * 4, 40)
    # Karakter çeşidi
    if re.search(r"[a-zçğıöşü]", pwd):
        score += 10
    if re.search(r"[A-ZÇĞİÖŞÜ]", pwd):
        score += 10
    if re.search(r"\d", pwd):
        score += 10
    if re.search(r"[!@#$%^&*()]", pwd):
        score += 15
    # Çeşitlilik bonusu
    if len(set(pwd)) >= len(pwd) * 0.7:
        score += 10
    # Yaygın şifre indirimi
    if pwd.lower() in _COMMON_WEAK:
        score = min(score, 20)
    return min(score, 100)
