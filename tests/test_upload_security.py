"""Upload security testleri."""
import pytest

from app.utils.upload_security import (
    detect_image_type, is_safe_svg, validate_uploaded_image, safe_filename
)


def test_detect_png():
    blob = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    assert detect_image_type(blob) == "png"


def test_detect_jpg():
    assert detect_image_type(b"\xff\xd8\xff\xe0" + b"\x00" * 100) == "jpg"


def test_detect_gif():
    assert detect_image_type(b"GIF89a" + b"\x00" * 100) == "gif"
    assert detect_image_type(b"GIF87a" + b"\x00" * 100) == "gif"


def test_detect_webp():
    blob = b"RIFF" + b"\x00\x00\x00\x00" + b"WEBP" + b"\x00" * 100
    assert detect_image_type(blob) == "webp"


def test_detect_webp_rejects_other_riff():
    """RIFF ile başlayan ama WEBP olmayan dosya kabul edilmez."""
    blob = b"RIFF" + b"\x00\x00\x00\x00" + b"WAVE" + b"\x00" * 100  # WAV
    assert detect_image_type(blob) is None


def test_detect_unknown_returns_none():
    assert detect_image_type(b"random text content here" * 10) is None


def test_safe_svg_clean():
    svg = b'<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg"><rect /></svg>'
    assert is_safe_svg(svg) is True


def test_safe_svg_rejects_script():
    svg = b'<?xml version="1.0"?><svg><script>alert(1)</script></svg>'
    assert is_safe_svg(svg) is False


def test_safe_svg_rejects_onclick():
    svg = b'<svg xmlns="http://www.w3.org/2000/svg"><rect onclick="alert(1)" /></svg>'
    assert is_safe_svg(svg) is False


def test_safe_svg_rejects_javascript_url():
    svg = b'<svg xmlns="http://www.w3.org/2000/svg"><a href="javascript:alert(1)" /></svg>'
    assert is_safe_svg(svg) is False


def test_safe_svg_rejects_foreignobject():
    svg = b'<svg xmlns="http://www.w3.org/2000/svg"><foreignObject></foreignObject></svg>'
    assert is_safe_svg(svg) is False


def test_safe_svg_rejects_non_svg():
    assert is_safe_svg(b"not svg content") is False


def test_validate_uploaded_image_png_ok():
    blob = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    ok, msg, ext = validate_uploaded_image(blob, {".png", ".jpg"})
    assert ok is True
    assert ext == "png"


def test_validate_uploaded_image_rejects_unknown():
    ok, msg, ext = validate_uploaded_image(b"random content" * 10, {".png", ".jpg"})
    assert ok is False
    assert "tespit edilemedi" in msg.lower()


def test_validate_uploaded_image_rejects_wrong_type():
    """PNG yüklenir ama sadece JPG kabul ediliyor."""
    blob = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    ok, msg, ext = validate_uploaded_image(blob, {".jpg"})
    assert ok is False


def test_validate_uploaded_image_accepts_safe_svg():
    svg = b'<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg"><rect /></svg>'
    ok, msg, ext = validate_uploaded_image(svg, {".svg", ".png"}, accept_svg=True)
    assert ok is True
    assert ext == "svg"


def test_validate_uploaded_image_rejects_unsafe_svg():
    svg = b'<svg><script>alert(1)</script></svg>'
    ok, msg, ext = validate_uploaded_image(svg, {".svg"}, accept_svg=True)
    assert ok is False


def test_safe_filename_strips_path():
    # os.path.basename Unix path separator'ını işliyor, "../etc/passwd" → "passwd"
    assert safe_filename("../etc/passwd") == "passwd"
    assert safe_filename("/etc/passwd") == "passwd"
    # Windows path separator backslash karakter olarak sanitize edilir
    out = safe_filename("..\\..\\Windows\\system.dll")
    assert ".." not in out  # path traversal yok
    assert "/" not in out and "\\" not in out


def test_safe_filename_strips_null():
    assert safe_filename("file\x00.txt") == "file.txt"


def test_safe_filename_keeps_safe_chars():
    assert safe_filename("logo_5.png") == "logo_5.png"
    assert safe_filename("My-Image.WEBP") == "My-Image.WEBP"


def test_safe_filename_fallback_on_empty():
    assert safe_filename("") == "file"
    assert safe_filename("..") == "file"
    assert safe_filename(".") == "file"


def test_safe_filename_length_limit():
    long = "a" * 500 + ".png"
    result = safe_filename(long)
    assert len(result) == 255
