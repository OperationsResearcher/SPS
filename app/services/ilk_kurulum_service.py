# -*- coding: utf-8 -*-
"""Masaüstüm: ilk kurulum kontrol listesi (UX-PLANI E / Faz 2.7).

Beş adım: Plan yılı → Strateji → Süreç → PG → İlk veri. Tamamlanma mevcut kayıtlardan hesaplanır
(yeni tablo yok). "Gizle" tercihi kullanıcının `theme_preferences` JSON'unda `ilk_kurulum_gizle` anahtarı.
Kurum bütün adımları bitirince liste kendiliğinden kaybolur.
"""
from __future__ import annotations

import json

from app.models import db
from app.models.core import Strategy
from app.models.plan_year import PlanYear
from app.models.process import KpiData, Process, ProcessKpi

GIZLE_ANAHTARI = "ilk_kurulum_gizle"
YONETICI_ROLLERI = ("tenant_admin", "executive_manager", "Admin")


def _prefs(user) -> dict:
    raw = getattr(user, "theme_preferences", None)
    if not raw:
        return {}
    try:
        veri = json.loads(raw) if isinstance(raw, str) else raw
    except (TypeError, ValueError):
        return {}
    return veri if isinstance(veri, dict) else {}


def gizli_mi(user) -> bool:
    return bool(_prefs(user).get(GIZLE_ANAHTARI))


def gizle_ayarla(user, gizli: bool = True) -> None:
    """Tercihi yazar (commit çağıranda)."""
    prefs = _prefs(user)
    prefs[GIZLE_ANAHTARI] = bool(gizli)
    user.theme_preferences = json.dumps(prefs)


def adim_durumlari(tenant_id: int) -> list[dict]:
    """[{anahtar, ad, tamam}] — sıra: plan_yili, strateji, surec, pg, veri."""
    plan = db.session.query(PlanYear.id).filter(PlanYear.tenant_id == tenant_id).first() is not None
    strateji = (
        db.session.query(Strategy.id)
        .filter(Strategy.tenant_id == tenant_id, Strategy.is_active.is_(True))
        .first()
        is not None
    )
    surec = (
        db.session.query(Process.id)
        .filter(Process.tenant_id == tenant_id, Process.is_active.is_(True))
        .first()
        is not None
    )
    pg_q = (
        db.session.query(ProcessKpi.id)
        .join(Process, ProcessKpi.process_id == Process.id)
        .filter(Process.tenant_id == tenant_id, Process.is_active.is_(True), ProcessKpi.is_active.is_(True))
    )
    pg = pg_q.first() is not None
    veri = (
        db.session.query(KpiData.id)
        .join(ProcessKpi, KpiData.process_kpi_id == ProcessKpi.id)
        .join(Process, ProcessKpi.process_id == Process.id)
        .filter(Process.tenant_id == tenant_id)
        .first()
        is not None
    )
    return [
        {"anahtar": "plan_yili", "tamam": plan},
        {"anahtar": "strateji", "tamam": strateji},
        {"anahtar": "surec", "tamam": surec},
        {"anahtar": "pg", "tamam": pg},
        {"anahtar": "veri", "tamam": veri},
    ]


def kontrol_listesi(user) -> dict | None:
    """Gösterilecekse {"adimlar": [...], "tamam": n, "toplam": 5}; aksi halde None.

    Gösterilmez: yönetici rolü değil, kurumsuz, gizlenmiş veya tüm adımlar tamam.
    """
    tenant_id = getattr(user, "tenant_id", None)
    rol = user.role.name if getattr(user, "role", None) else ""
    if not tenant_id or rol not in YONETICI_ROLLERI or gizli_mi(user):
        return None
    adimlar = adim_durumlari(tenant_id)
    tamam = sum(1 for a in adimlar if a["tamam"])
    if tamam == len(adimlar):
        return None
    return {"adimlar": adimlar, "tamam": tamam, "toplam": len(adimlar)}
