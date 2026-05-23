"""Password complexity policy testleri (Sprint 22)."""
import pytest

from app.utils.password_policy import validate_password, password_strength


def test_too_short(app):
    with app.app_context():
        ok, errs = validate_password("Ab1")
        assert not ok
        assert any("en az" in e.lower() for e in errs)


def test_no_uppercase(app):
    with app.app_context():
        ok, errs = validate_password("alllower1")
        assert not ok
        assert any("büyük" in e.lower() for e in errs)


def test_no_lowercase(app):
    with app.app_context():
        ok, errs = validate_password("ALLUPPER1")
        assert not ok
        assert any("küçük" in e.lower() for e in errs)


def test_no_digit(app):
    with app.app_context():
        ok, errs = validate_password("OnlyLetters")
        assert not ok
        assert any("rakam" in e.lower() for e in errs)


def test_strong_password_passes(app):
    with app.app_context():
        ok, errs = validate_password("Tomofil2026!")
        assert ok
        assert errs == []


def test_common_weak_rejected(app):
    with app.app_context():
        ok, errs = validate_password("Password123")
        # Mevcut kontroller geçse de "common weak" listede
        # Note: "password123" lowercase'de listede
        # "Password123" uppercase ile mevcut kontrol geçer, lowercase _COMMON_WEAK check fails
        assert not ok


def test_same_as_username(app):
    with app.app_context():
        ok, errs = validate_password("Admin123", username="Admin123")
        assert not ok
        assert any("kullanıcı adı" in e.lower() for e in errs)


def test_strength_weak():
    # Zayıf şifre <40 puan
    assert password_strength("abc") < 40
    # Common weak listesinde olan şifre 20 ile cap'lenir
    assert password_strength("password") <= 25


def test_strength_medium():
    assert 40 <= password_strength("Abc12345") <= 80


def test_strength_strong():
    assert password_strength("Tomofil2026!Strong") >= 70


def test_empty_password(app):
    with app.app_context():
        ok, errs = validate_password("")
        assert not ok
