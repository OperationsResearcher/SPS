# -*- coding: utf-8 -*-
"""Diğer legacy modeller — Activity, audit, kurumsal kimlik.

NOT: 29 Faz 2/3/4 mock modeli (ObjectiveComment, StrategicRisk, GembaWalk,
MudaFinding, MetaverseDepartment, DoomsdayScenario... — hepsi `mock_*` tablolu
sadece-id sahte modeldi) KALDIRILDI (2026-07-19). Onları sorgulayan 39 legacy
main.* sayfa silindiği için `models/__init__.py`'deki mock üretici de temizlendi.
"""
from models import (  # noqa: F401
    Activity,
    AuditLog,
    Feedback,
    UserDashboardSettings,
    CorporateIdentity,
)
