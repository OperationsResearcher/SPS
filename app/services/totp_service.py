"""TOTP 2FA Servisi (Sprint 26).

pyotp tabanlı RFC 6238 uyumlu TOTP.
Setup flow:
    1. User TOTP'u etkinleştirmek ister → secret üret + QR göster
    2. User authenticator app'i ile 6 haneli kodu doğrular
    3. Backup codes (recovery) gösterilir, kullanıcı kaydetmelidir
    4. user.totp_enabled = True

Login flow:
    1. Email + password doğrulanır
    2. totp_enabled ise: ek TOTP code istenir
    3. pyotp.verify(secret, code) → login_user

Gereksinim: `pip install pyotp qrcode[pil]`
"""
from __future__ import annotations

import base64
import io
import json
import secrets
import time
from typing import Optional


def generate_totp_secret() -> str:
    """Base32 secret üret (RFC 6238)."""
    try:
        import pyotp
        return pyotp.random_base32()
    except ImportError:
        # Fallback: secrets ile manuel
        return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")


def get_provisioning_uri(secret: str, email: str, issuer: str = "Kokpitim") -> str:
    """authenticator app için otpauth:// URI."""
    try:
        import pyotp
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name=issuer)
    except ImportError:
        return f"otpauth://totp/{issuer}:{email}?secret={secret}&issuer={issuer}"


def get_qr_code_base64(secret: str, email: str, issuer: str = "Kokpitim") -> Optional[str]:
    """QR kodu base64 data URI olarak döner — img src direkt kullanılabilir."""
    uri = get_provisioning_uri(secret, email, issuer)
    try:
        import qrcode
        img = qrcode.make(uri)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/png;base64,{b64}"
    except ImportError:
        return None


def verify_totp_code(secret: str, code: str, valid_window: int = 1) -> bool:
    """TOTP code doğrulama. valid_window=1 → ±30 saniye tolerans."""
    if not secret or not code:
        return False
    try:
        import pyotp
        totp = pyotp.TOTP(secret)
        return totp.verify(code.strip(), valid_window=valid_window)
    except ImportError:
        return False
    except Exception:
        return False


def generate_backup_codes(count: int = 10) -> list[str]:
    """One-time recovery codes (4+4 format, örn. 'AX2K-9PQR')."""
    codes = []
    for _ in range(count):
        a = secrets.token_hex(2).upper()[:4]
        b = secrets.token_hex(2).upper()[:4]
        codes.append(f"{a}-{b}")
    return codes


def consume_backup_code(user, code: str) -> bool:
    """Backup code kullanıldığında listeden çıkar.

    user.totp_backup_codes_json güncellenir; çağıran db.session.commit() yapmalı.
    """
    if not user.totp_backup_codes_json:
        return False
    try:
        codes = json.loads(user.totp_backup_codes_json)
    except (ValueError, TypeError):
        return False
    code_n = code.strip().upper()
    if code_n in codes:
        codes.remove(code_n)
        user.totp_backup_codes_json = json.dumps(codes)
        return True
    return False
