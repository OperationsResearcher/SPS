# -*- coding: utf-8 -*-
"""Legacy kullanıcı/kurum tabloları — geçiş katmanı (models.user shim)."""
from models.user import (  # noqa: F401
    LegacyUser,
    Kurum,
    YetkiMatrisi,
    OzelYetki,
    KullaniciYetki,
    DashboardLayout,
    Deger,
    EtikKural,
    KalitePolitikasi,
    UserActivityLog,
    Note,
    LegacyNotification,
)

# Geriye dönük: legacy kod `User` bekler (`user` tablosu)
User = LegacyUser
Notification = LegacyNotification
