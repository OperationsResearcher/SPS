"""Tenant LLM yapılandırması — BYOK (Bring Your Own Key) modeli.

Anahtar Fernet ile şifreli saklanır. Fernet key = SECRET_KEY türevidir.
"""
from __future__ import annotations

import base64
import hashlib
import os
from typing import Optional

from extensions import db


def _fernet_key() -> bytes:
    """SECRET_KEY'den deterministik 32-byte Fernet anahtarı türet."""
    secret = (
        os.environ.get("LLM_ENCRYPTION_KEY")
        or os.environ.get("SECRET_KEY")
        or "kokpitim-default-do-not-use-in-prod"
    )
    digest = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_key(plaintext: str) -> str:
    if not plaintext:
        return ""
    try:
        from cryptography.fernet import Fernet
        f = Fernet(_fernet_key())
        return f.encrypt(plaintext.encode()).decode()
    except ImportError:
        # cryptography yoksa base64 (zayıf — sadece dev fallback)
        return "b64:" + base64.b64encode(plaintext.encode()).decode()


def decrypt_key(ciphertext: str) -> Optional[str]:
    if not ciphertext:
        return None
    try:
        if ciphertext.startswith("b64:"):
            return base64.b64decode(ciphertext[4:]).decode()
        from cryptography.fernet import Fernet
        f = Fernet(_fernet_key())
        return f.decrypt(ciphertext.encode()).decode()
    except Exception:
        return None


def mask_key(plaintext: str) -> str:
    """UI'da gösterim için maskeleme: AIza••••••••••••xyz"""
    if not plaintext or len(plaintext) < 8:
        return "•" * 8
    return plaintext[:4] + "•" * 12 + plaintext[-4:]


class TenantLLMConfig(db.Model):
    """Tenant'a özel LLM yapılandırması (BYOK)."""

    __tablename__ = "tenant_llm_configs"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(
        db.Integer, db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False, unique=True,
    )

    # Hangi provider — gemini / openai / anthropic / groq / openrouter
    provider = db.Column(db.String(40), nullable=False, default="gemini")
    model = db.Column(db.String(120), nullable=True)  # ör: "gemini-2.0-flash", "gpt-4o-mini"
    api_key_encrypted = db.Column(db.Text, nullable=True)
    base_url = db.Column(db.String(300), nullable=True)  # OpenRouter, self-hosted için

    # Davranış
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    # True → bu tenant kendi key'ini kullanır
    # False → sistem key'i kullanılır
    pii_mask_enabled = db.Column(db.Boolean, nullable=False, default=True)

    # Test bilgisi (son test ne zaman, sonuç ne)
    last_test_at = db.Column(db.DateTime, nullable=True)
    last_test_status = db.Column(db.String(40), nullable=True)  # ok / error
    last_test_message = db.Column(db.String(500), nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, nullable=False,
        server_default=db.func.now(), onupdate=db.func.now(),
    )

    @property
    def api_key_plain(self) -> Optional[str]:
        return decrypt_key(self.api_key_encrypted) if self.api_key_encrypted else None

    def set_api_key(self, plaintext: str):
        self.api_key_encrypted = encrypt_key(plaintext) if plaintext else None

    def to_dict(self, reveal_key: bool = False) -> dict:
        plain = self.api_key_plain
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "provider": self.provider,
            "model": self.model,
            "api_key_masked": mask_key(plain) if plain else None,
            "api_key": plain if reveal_key else None,
            "base_url": self.base_url,
            "is_active": self.is_active,
            "pii_mask_enabled": self.pii_mask_enabled,
            "last_test_at": self.last_test_at.isoformat() if self.last_test_at else None,
            "last_test_status": self.last_test_status,
            "last_test_message": self.last_test_message,
        }
