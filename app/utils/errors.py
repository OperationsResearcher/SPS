# -*- coding: utf-8 -*-
"""
Kokpitim Custom Exceptions
Sıfır Hata (Zero Defect) hedefi doğrultusunda merkezi hata yönetimi için özel hata sınıfları.
"""

class KokpitimError(Exception):
    """Projedeki tüm özel hataların türediği temel (Base) hata sınıfı."""
    def __init__(self, message="Bir hata oluştu.", status_code=500, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['success'] = False
        rv['message'] = self.message
        rv['error_code'] = self.__class__.__name__
        return rv


class AuthorizationError(KokpitimError):
    """Yetki, Kurum (Tenant) uyumsuzluğu ve IDOR ihlallerinde fırlatılacak hata."""
    def __init__(self, message="Bu kaynağa erişim yetkiniz bulunmamaktadır.", payload=None):
        super().__init__(message, status_code=403, payload=payload)


class ValidationError(KokpitimError):
    """Gelen veri doğrulanamadığında (Eksik parametre vb.) fırlatılacak hata."""
    def __init__(self, message="Gönderilen verilerde eksik veya hata var.", payload=None):
        super().__init__(message, status_code=400, payload=payload)


class ResourceNotFoundError(KokpitimError):
    """İstenen kaynak (Proje, Süreç, Kullanıcı) bulunamadığında fırlatılacak hata."""
    def __init__(self, message="İstenen kaynak bulunamadı.", payload=None):
        super().__init__(message, status_code=404, payload=payload)


class BusinessRuleError(KokpitimError):
    """İş kuralları (Business Logic) ihlal edildiğinde fırlatılacak hata."""
    def __init__(self, message="İşleminiz kurum kurallarına aykırıdır.", payload=None):
        super().__init__(message, status_code=422, payload=payload)
