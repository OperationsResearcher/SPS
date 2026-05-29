"""Hoshin Kanri X-Matrix servisi.

4 çeyrek (kuzey-doğu-güney-batı):
  North  = Uzun Vadeli Stratejiler   (strategies)
  East   = Yıllık Hedefler           (sub_strategies — aktif plan year)
  South  = İyileştirme Faaliyetleri  (initiatives — aktif yıl içinde)
  West   = Ölçülebilir KPI'lar       (process_kpis)

Korelasyon matrisleri:
  N×E : ProcessSubStrategyLink üzerinden (zaten var) +
        Strategy → SubStrategy parent ilişkisi (direkt link)
  E×S : Initiative.sub_strategy_id veya strategy_id
  S×W : KPI ↔ Initiative — mevcut modelde yok; placeholder (heuristic by process)
  N×W : Strategy → SubStrategy → ProcessSubStrategyLink → Process → KPI zinciri
"""
from __future__ import annotations

from sqlalchemy import text
from extensions import db


def build_xmatrix(tenant_id: int, plan_year_id: int | None = None) -> dict:
    """X-Matrix için 4 ekseni ve korelasyonları döndürür."""
    py_filter = "AND plan_year_id = :py" if plan_year_id else ""
    params = {"t": tenant_id}
    if plan_year_id:
        params["py"] = plan_year_id

    # North — Stratejiler
    strategies = db.session.execute(text(f"""
        SELECT id, code, title
        FROM strategies
        WHERE tenant_id=:t AND is_active=true {py_filter}
        ORDER BY code NULLS LAST, id
    """), params).fetchall()
    north = [{"id": r.id, "code": r.code or "", "title": r.title or f"#{r.id}"} for r in strategies]
    strat_ids = [s["id"] for s in north]

    # East — Alt stratejiler (yıllık hedefler)
    sub_strats = []
    if strat_ids:
        sub_strats = db.session.execute(text("""
            SELECT id, code, title, strategy_id
            FROM sub_strategies
            WHERE strategy_id = ANY(:sids) AND is_active=true
            ORDER BY code NULLS LAST, id
        """), {"sids": strat_ids}).fetchall()
    east = [
        {"id": r.id, "code": r.code or "", "title": r.title or f"#{r.id}", "strategy_id": r.strategy_id}
        for r in sub_strats
    ]

    # South — Initiative'ler
    inits = db.session.execute(text("""
        SELECT id, code, name, strategy_id, sub_strategy_id, status, progress_pct
        FROM initiatives
        WHERE tenant_id=:t AND is_active=true
        ORDER BY priority DESC, id DESC
    """), {"t": tenant_id}).fetchall()
    south = [
        {
            "id": r.id, "code": r.code or "", "name": r.name,
            "strategy_id": r.strategy_id, "sub_strategy_id": r.sub_strategy_id,
            "status": r.status, "progress_pct": float(r.progress_pct or 0),
        }
        for r in inits
    ]

    # West — PG'ler (önemli olanları öncele); plan_year varsa o yıla filtre
    west_py = "AND p.plan_year_id = :py" if plan_year_id else ""
    kpis = db.session.execute(text(f"""
        SELECT k.id, k.code, k.name, p.id as process_id, p.code as proc_code
        FROM process_kpis k
        JOIN processes p ON k.process_id=p.id
        WHERE p.tenant_id=:t AND k.is_active=true AND p.is_active=true {west_py}
        ORDER BY k.is_important DESC NULLS LAST, k.id
        LIMIT 60
    """), params).fetchall()
    west = [
        {"id": r.id, "code": r.code or "", "name": r.name,
         "process_id": r.process_id, "proc_code": r.proc_code or ""}
        for r in kpis
    ]
    kpi_ids = [k["id"] for k in west]

    # ── Korelasyonlar ────────────────────────────────────────────────────────
    correlations = {
        "north_east": [],  # strategy ↔ sub_strategy (parent direct)
        "east_south": [],  # sub_strategy ↔ initiative
        "south_west": [],  # initiative ↔ kpi (heuristic: same process)
        "north_west": [],  # strategy ↔ kpi (via sub_strategy ↔ process link)
    }

    for ss in east:
        correlations["north_east"].append({"n": ss["strategy_id"], "e": ss["id"]})

    # Strateji → tüm alt strateji ID listesi (initiative'ın strategy_id'si ile fallback)
    _subs_by_strat = {}
    for ss in east:
        _subs_by_strat.setdefault(ss["strategy_id"], []).append(ss["id"])

    for ini in south:
        if ini["sub_strategy_id"]:
            correlations["east_south"].append({"e": ini["sub_strategy_id"], "s": ini["id"]})
        elif ini.get("strategy_id"):
            # Fallback: initiative sadece stratejiye bağlıysa, stratejinin tüm alt stratejileriyle eşleştir
            for ss_id in _subs_by_strat.get(ini["strategy_id"], []):
                correlations["east_south"].append({"e": ss_id, "s": ini["id"]})

    # north_west — Strategy → SubStrategy → ProcessSubStrategyLink → Process → KPI
    if strat_ids and kpi_ids:
        rows = db.session.execute(text("""
            SELECT DISTINCT ss.strategy_id as n, k.id as w
            FROM sub_strategies ss
            JOIN process_sub_strategy_links psl ON psl.sub_strategy_id=ss.id
            JOIN process_kpis k ON k.process_id=psl.process_id
            WHERE ss.strategy_id = ANY(:sids)
              AND k.id = ANY(:kids)
              AND ss.is_active=true AND k.is_active=true
        """), {"sids": strat_ids, "kids": kpi_ids}).fetchall()
        correlations["north_west"] = [{"n": r.n, "w": r.w} for r in rows]

    # south_west — heuristic: initiative ile aynı sub_strategy'ye bağlı process'lerin PG'leri
    # Fallback: initiative.sub_strategy_id yoksa initiative.strategy_id'nin tüm alt stratejilerini kullan
    if south and west:
        kpi_by_process = {}
        for k in west:
            kpi_by_process.setdefault(k["process_id"], []).append(k["id"])
        # Tüm sub_strategy_id'leri tek IN sorguda topla (N+1 önlemi)
        _needed_ss_ids = set()
        _ini_sub_ids = {}
        for ini in south:
            ss_ids = []
            if ini["sub_strategy_id"]:
                ss_ids = [ini["sub_strategy_id"]]
            elif ini.get("strategy_id"):
                ss_ids = _subs_by_strat.get(ini["strategy_id"], [])
            _ini_sub_ids[ini["id"]] = ss_ids
            _needed_ss_ids.update(ss_ids)
        _procs_by_ss = {}
        if _needed_ss_ids:
            for r in db.session.execute(text("""
                SELECT DISTINCT sub_strategy_id, process_id FROM process_sub_strategy_links
                WHERE sub_strategy_id = ANY(:sids)
            """), {"sids": list(_needed_ss_ids)}).fetchall():
                _procs_by_ss.setdefault(r.sub_strategy_id, []).append(r.process_id)
        for ini in south:
            for ss_id in _ini_sub_ids.get(ini["id"], []):
                for pid in _procs_by_ss.get(ss_id, []):
                    for kid in kpi_by_process.get(pid, []):
                        correlations["south_west"].append({"s": ini["id"], "w": kid})

    return {
        "tenant_id": tenant_id,
        "plan_year_id": plan_year_id,
        "north": north,
        "east": east,
        "south": south,
        "west": west,
        "correlations": correlations,
        "counts": {
            "north": len(north), "east": len(east),
            "south": len(south), "west": len(west),
        },
    }
