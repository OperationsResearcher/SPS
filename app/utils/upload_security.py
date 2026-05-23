"""Upload güvenliği — magic byte ve path sanitization.

Audit (PROJE-AUDIT-2026Q2.md) bulgu: Logo upload sadece extension check yapıyor;
SVG XSS riski, path traversal riski.
"""
from __future__ import annotations

import os
import re
from typing import Optional, Tuple

# Magic byte imzaları (dosya başında ilk N byte)
# Kaynak: https://en.wikipedia.org/wiki/List_of_file_signatures
_MAGIC_SIGNATURES = {
    "png":  [b"\x89PNG\r\n\x1a\n"],
    "jpg":  [b"\xff\xd8\xff"],
    "jpeg": [b"\xff\xd8\xff"],
    "gif":  [b"GIF87a", b"GIF89a"],
    "webp": [b"RIFF"],  # RIFF + 4 byte boyut + "WEBP" — daha derin kontrol aşağıda
    "bmp":  [b"BM"],
    "pdf":  [b"%PDF-"],
}


def detect_image_type(blob: bytes) -> Optional[str]:
    """Bayt içeriğinden gerçek görsel tipini tespit eder. Bilinmiyorsa None.

    SVG tespit edilmez (XML formatı, tehlikeli) — çağıran açıkça SVG kabul etmek isterse
    is_safe_svg() kullanmalı.
    """
    if not blob:
        return None
    for ext, sigs in _MAGIC_SIGNATURES.items():
        for sig in sigs:
            if blob.startswith(sig):
                # WEBP için ekstra kontrol: "WEBP" 8. byte'tan başlamalı
                if ext == "webp":
                    if len(blob) >= 12 and blob[8:12] == b"WEBP":
                        return "webp"
                    continue
                return ext
    return None


# SVG'yi tamamen reddetme veya sıkı sanitize seçeneği
_SVG_DANGEROUS_PATTERN = re.compile(
    rb"(?i)(<script|on\w+\s*=|javascript:|<iframe|<foreignobject|<use[^>]*href)"
)


def is_safe_svg(blob: bytes) -> bool:
    """Basit SVG güvenlik kontrolü. Script, event handler, javascript: yoksa True."""
    if not blob:
        return False
    # XML/SVG ile başlıyor mu?
    head = blob[:200].lstrip()
    if not (head.startswith(b"<?xml") or head.startswith(b"<svg")):
        return False
    # Tehlikeli pattern var mı?
    if _SVG_DANGEROUS_PATTERN.search(blob):
        return False
    return True


def validate_uploaded_image(
    blob: bytes,
    allowed_extensions: set[str],
    accept_svg: bool = False,
) -> Tuple[bool, str, Optional[str]]:
    """Yüklenen byte içeriği güvenli görsel olarak doğrula.

    Returns:
        (ok, message, detected_ext)
        ok=True ise message="" ve detected_ext='png'/'jpg'/...
        ok=False ise message=hata mesajı, detected_ext=None
    """
    if not blob:
        return False, "Boş dosya.", None
    if len(blob) < 8:
        return False, "Dosya çok küçük.", None

    detected = detect_image_type(blob)

    # Normalize allowed extensions (".png" → "png")
    allowed_norm = {e.lower().lstrip(".") for e in allowed_extensions}

    # SVG akışı
    if detected is None and accept_svg and "svg" in allowed_norm:
        if is_safe_svg(blob):
            return True, "", "svg"
        return False, "SVG güvenlik kontrolünden geçemedi (script/event tespit edildi).", None

    if detected is None:
        return False, "Dosya türü tespit edilemedi (geçersiz görsel).", None

    if detected.lower() not in allowed_norm:
        return False, f"Bu dosya türü kabul edilmiyor: {detected}", None

    return True, "", detected


# Path traversal koruma
_SAFE_FILENAME = re.compile(r"^[A-Za-z0-9._-]+$")


def safe_filename(name: str, fallback: str = "file") -> str:
    """Güvenli dosya adı: path separator, .., null byte, kontrol char yok.

    Sadece [A-Za-z0-9._-] karakterlerine izin verir. Diğer her şey '_' ile değiştirilir.
    İçeriği tamamen sıfırlanırsa fallback döner.
    """
    if not name:
        return fallback
    name = os.path.basename(name)  # dizin bileşeni at
    name = name.replace("\x00", "")  # null byte
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    if not name or name in (".", ".."):
        return fallback
    return name[:255]  # filesystem limit
