"""At-rest şifreleme yardımcıları — Fernet simetrik şifreleme.

Kullanım:
    from app.utils.encryption import encrypt, decrypt

Ortam değişkeni:
    ENCRYPTION_KEY — 32-byte URL-safe base64 Fernet anahtarı.
    Üretmek için: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

    UYARI: Anahtar kaybolursa şifreli veriler çözülemez.
    Yerel/.env'de saklayın, asla kaynak koduna yazmayın.
"""

import logging
import os

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Anahtar yükleme
# ---------------------------------------------------------------------------
# Ortam değişkeninden al; yoksa geçici bir anahtar üret (yalnızca geliştirme).
# Üretimde ENCRYPTION_KEY mutlaka .env'de tanımlı olmalıdır.
_raw_key = os.environ.get("ENCRYPTION_KEY", "").strip()

if _raw_key:
    _fernet = Fernet(_raw_key.encode())
else:
    # Üretimde ENCRYPTION_KEY zorunludur. Tanımsızsa her başlatmada rastgele anahtar
    # üretilirdi → önceki oturumda şifrelenen veri (SMTP/LLM credential vb.) sessizce
    # çözülemez hale gelir. Sessiz veri kaybı yerine açıkça başlatmayı durdururuz.
    if (os.environ.get("FLASK_ENV") or "development").lower() == "production":
        raise RuntimeError(
            "ENCRYPTION_KEY ortam değişkeni üretimde zorunludur. "
            "Üret: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\" "
            "ve .env'e ekle."
        )
    # Geliştirme/test: geçici anahtar üret. Anahtar değeri ASLA loga yazılmaz.
    _generated_key = Fernet.generate_key()
    _fernet = Fernet(_generated_key)
    logger.warning(
        "ENCRYPTION_KEY ortam değişkeni tanımlı değil. Geçici anahtar üretildi — "
        "bu oturum dışında şifreli veriler çözülemez. Üretimde .env'e ENCRYPTION_KEY ekleyin."
    )


# ---------------------------------------------------------------------------
# Genel API
# ---------------------------------------------------------------------------

def encrypt(plaintext: str | None) -> str | None:
    """Düz metni Fernet ile şifreler, base64 token döner.

    Args:
        plaintext: Şifrelenecek metin. None veya boş string geçilirse None döner.

    Returns:
        Şifreli token (str) veya None.
    """
    if not plaintext:
        return None
    try:
        return _fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")
    except Exception:
        logger.exception("encrypt() başarısız oldu")
        raise


def decrypt(ciphertext: str | None) -> str | None:
    """Fernet token'ı çözer, düz metin döner.

    Args:
        ciphertext: Şifreli token. None veya boş string geçilirse None döner.

    Returns:
        Düz metin (str) veya None.

    Raises:
        cryptography.fernet.InvalidToken: Token bozuksa veya anahtar yanlışsa.
    """
    if not ciphertext:
        return None
    try:
        return _fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        logger.error("decrypt() başarısız — geçersiz token veya yanlış anahtar")
        raise
    except Exception:
        logger.exception("decrypt() beklenmedik hata")
        raise
