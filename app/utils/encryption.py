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
    _generated_key = Fernet.generate_key()
    _fernet = Fernet(_generated_key)
    # Güvenlik: üretilen anahtar değeri ASLA loga yazılmaz (log erişimi olan biri
    # şifreli veriyi çözebilirdi). Yerel geliştirmede anahtarı kalıcı yapmak için
    # .env'e ekleyin: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
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
