"""
Hizalama Skoru — bireysel hedeflerin stratejik hedeflere katkı oranı.
"""
from __future__ import annotations
from app.models import db
from app.models.process import IndividualPerformanceIndicator, ProcessKpi
from app.models.core import SubStrategy, Strategy


def get_user_alignment_score(user_id: int, tenant_id: int) -> dict:
    """
    Kullanıcının bireysel PG'lerinden kaçının bir süreç PG'sine,
    oradan da bir stratejiye bağlı olduğunu hesaplar.

    Returns:
        {
          "total_pgs": int,
          "aligned_pgs": int,
          "alignment_pct": float,
          "badge": "Yüksek" | "Orta" | "Düşük" | "Yok",
          "details": [{"name": str, "aligned": bool, "strategy": str|None}]
        }
    """
    pgs = IndividualPerformanceIndicator.query.filter_by(
        user_id=user_id, is_active=True
    ).all()

    total = len(pgs)
    if total == 0:
        return {"total_pgs": 0, "aligned_pgs": 0, "alignment_pct": 0.0, "badge": "Yok", "details": []}

    details = []
    aligned = 0

    for pg in pgs:
        strategy_name = None
        is_aligned = False

        if pg.source_process_kpi_id:
            kpi = ProcessKpi.query.get(pg.source_process_kpi_id)
            if kpi and kpi.sub_strategy_id:
                ss = SubStrategy.query.get(kpi.sub_strategy_id)
                if ss and ss.strategy_id:
                    s = Strategy.query.get(ss.strategy_id)
                    if s and s.tenant_id == tenant_id:
                        strategy_name = f"{s.code or ''} {s.title or ''}".strip()
                        is_aligned = True

        if is_aligned:
            aligned += 1

        details.append({
            "name": pg.name,
            "aligned": is_aligned,
            "strategy": strategy_name,
        })

    pct = round((aligned / total) * 100, 1)
    badge = "Yüksek" if pct >= 70 else ("Orta" if pct >= 40 else ("Düşük" if pct > 0 else "Yok"))

    return {
        "total_pgs": total,
        "aligned_pgs": aligned,
        "alignment_pct": pct,
        "badge": badge,
        "details": details,
    }


def get_team_alignment_summary(tenant_id: int) -> list[dict]:
    """
    Tenant'taki tüm aktif kullanıcıların hizalama skorunu döner.
    Yönetici ekip paneli için kullanılır.
    """
    from app.models.core import User
    users = User.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    result = []
    for u in users:
        score = get_user_alignment_score(u.id, tenant_id)
        result.append({
            "user_id": u.id,
            "name": f"{u.first_name or ''} {u.last_name or ''}".strip() or u.email,
            "email": u.email,
            "alignment_pct": score["alignment_pct"],
            "badge": score["badge"],
            "total_pgs": score["total_pgs"],
            "aligned_pgs": score["aligned_pgs"],
        })
    result.sort(key=lambda x: x["alignment_pct"], reverse=True)
    return result
