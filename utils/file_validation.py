# -*- coding: utf-8 -*-
"""
Dosya yükleme validasyonu ve güvenlik kontrolleri
"""
import os
import mimetypes
from typing import Tuple, Optional
from werkzeug.utils import secure_filename
from flask import current_app

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    # current_app context'te olmayabilir, bu yüzden try-except kullan
    try:
        from flask import current_app
        if current_app:
            current_app.logger.warning(
                "python-magic not available. MIME type validation will be limited to extension check."
            )
    except:
        pass  # Context yoksa sessizce geç


# İzin verilen dosya uzantıları ve MIME tipleri
ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp',  # Resimler
    'pdf',  # PDF
    'doc', 'docx',  # Word
    'xls', 'xlsx',  # Excel
    'txt', 'csv'  # Metin
}

ALLOWED_MIME_TYPES = {
    # Resimler
    'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/svg+xml', 'image/webp',
    # PDF
    'application/pdf',
    # Word
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    # Excel
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    # Metin
    'text/plain', 'text/csv',
    # Genel
    'application/octet-stream'  # Bazı dosyalar için fallback
}

# Extension -> MIME type mapping (fallback için)
EXTENSION_MIME_MAP = {
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'gif': 'image/gif',
    'svg': 'image/svg+xml',
    'webp': 'image/webp',
    'pdf': 'application/pdf',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'xls': 'application/vnd.ms-excel',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'txt': 'text/plain',
    'csv': 'text/csv'
}


def validate_file_extension(filename: str) -> bool:
    """
    Dosya uzantısını kontrol et
    
    Args:
        filename: Dosya adı
        
    Returns:
        bool: Uzantı izin verilen listede ise True
    """
    if not filename or '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def get_file_mime_type(file_content: bytes, filename: str) -> Optional[str]:
    """
    Dosyanın gerçek MIME type'ını tespit et
    
    Args:
        file_content: Dosya içeriği (ilk 2048 byte yeterli)
        filename: Dosya adı (fallback için)
        
    Returns:
        str: MIME type veya None
    """
    # python-magic kullanarak gerçek MIME type'ı tespit et
    if MAGIC_AVAILABLE:
        try:
            mime = magic.Magic(mime=True)
            detected_mime = mime.from_buffer(file_content[:2048])
            return detected_mime
        except Exception as e:
            if current_app:
                current_app.logger.warning(f"MIME type tespiti başarısız: {e}")
    
    # Fallback: mimetypes kullan
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type:
        return mime_type
    
    # Son fallback: Extension mapping
    if '.' in filename:
        ext = filename.rsplit('.', 1)[1].lower()
        return EXTENSION_MIME_MAP.get(ext)
    
    return None


def validate_file_mime_type(file_content: bytes, filename: str) -> Tuple[bool, Optional[str]]:
    """
    Dosyanın MIME type'ını kontrol et
    
    Args:
        file_content: Dosya içeriği
        filename: Dosya adı
        
    Returns:
        Tuple[bool, Optional[str]]: (Geçerli mi, MIME type)
    """
    mime_type = get_file_mime_type(file_content, filename)
    
    if not mime_type:
        return False, None
    
    # MIME type izin verilen listede mi?
    if mime_type in ALLOWED_MIME_TYPES:
        return True, mime_type
    
    # Bazı MIME type'lar benzer olabilir (örn: image/jpg vs image/jpeg)
    # Bu durumda extension'a bak
    if validate_file_extension(filename):
        ext = filename.rsplit('.', 1)[1].lower()
        expected_mime = EXTENSION_MIME_MAP.get(ext)
        if expected_mime and mime_type.startswith(expected_mime.split('/')[0]):
            # Aynı ana kategori (image, application, text) ise kabul et
            return True, mime_type
    
    return False, mime_type


def validate_uploaded_file(file, max_size: int = 16 * 1024 * 1024) -> Tuple[bool, str, Optional[str]]:
    """
    Yüklenen dosyayı tam olarak validate et
    
    Args:
        file: Werkzeug FileStorage objesi
        max_size: Maksimum dosya boyutu (bytes)
        
    Returns:
        Tuple[bool, str, Optional[str]]: (Geçerli mi, Hata mesajı, MIME type)
    """
    if not file or not file.filename:
        return False, "Dosya seçilmedi!", None
    
    filename = secure_filename(file.filename)
    
    # 1. Extension kontrolü
    if not validate_file_extension(filename):
        return False, f"Geçersiz dosya tipi! İzin verilen tipler: {', '.join(sorted(ALLOWED_EXTENSIONS))}", None
    
    # 2. Dosya boyutu kontrolü
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > max_size:
        return False, f"Dosya boyutu çok büyük! Maksimum: {max_size / (1024*1024):.0f} MB", None
    
    # 3. MIME type kontrolü (dosya içeriğinden)
    file_content = file.read(2048)  # İlk 2048 byte yeterli
    file.seek(0)  # Dosyayı başa al
    
    is_valid, mime_type = validate_file_mime_type(file_content, filename)
    
    if not is_valid:
        return False, f"Geçersiz dosya içeriği! Beklenen MIME type'lar: {', '.join(sorted(ALLOWED_MIME_TYPES))}. Tespit edilen: {mime_type or 'bilinmiyor'}", mime_type
    
    return True, "", mime_type




















