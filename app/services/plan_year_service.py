# -*- coding: utf-8 -*-
"""
Plan Year Service — yıllık stratejik planlama dönem yönetimi.

Temel işlevler:
  - get_plan_year(tenant_id, year)          → PlanYear veya None
  - get_or_create_plan_year(tenant_id, year) → PlanYear (yeni oluşturulursa mevcut KPIler kopyalanır)
  - get_kpi_config(kpi, plan_year)           → dict (yıllık config veya ProcessKpi fallback)
  - get_kpi_configs_bulk(kpis, plan_year)    → {kpi_id: dict}
  - close_plan_year(plan_year, actor_id)     → PlanYear
  - clone_plan_year(source, new_year, name)  → PlanYear
  - list_plan_years(tenant_id)              → [PlanYear]
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from flask import current_app

from app.models import db
from app.models.plan_year import (
    PlanYear,
    KpiYearConfig,
    StrategyYearConfig,
    SubStrategyYearConfig,
    ProcessYearConfig,
    IndividualKpiYearConfig,
)
from app.models.process import ProcessKpi, Process, IndividualPerformanceIndicator
from app.models.core import Strategy, SubStrategy


# ── Yardımcı ──────────────────────────────────────────────────────────────────

def _first_or_none(q):
    try:
        return q.first()
    except Exception:
        return None


# ── Plan Year Sorgulama ────────────────────────────────────────────────────────

def get_plan_year(tenant_id: int, year: int) -> Optional[PlanYear]:
    """Tenant + yıl için PlanYear kaydını döner, yoksa None."""
    return PlanYear.query.filter_by(tenant_id=tenant_id, year=year).first()


def list_plan_years(tenant_id: int) -> List[PlanYear]:
    """Tenant'ın tüm plan yıllarını yeni→eski sıralamasıyla döner."""
    return (
        PlanYear.query
        .filter_by(tenant_id=tenant_id)
        .order_by(PlanYear.year.desc())
        .all()
    )


def get_active_plan_year(tenant_id: int) -> Optional[PlanYear]:
    """Status=active olan plan yılını döner; yoksa en son yılı döner."""
    active = PlanYear.query.filter_by(
        tenant_id=tenant_id, status="active"
    ).order_by(PlanYear.year.desc()).first()
    if active:
        return active
    return PlanYear.query.filter_by(
        tenant_id=tenant_id
    ).order_by(PlanYear.year.desc()).first()


def get_or_create_plan_year(tenant_id: int, year: int) -> PlanYear:
    """
    Tenant + yıl için PlanYear döner; yoksa oluşturur.
    Yeni oluşturulursa mevcut tüm KPI, strateji, süreç ve bireysel PGler
    o yılın config tablosuna kopyalanır (başlangıç değerleri = orijinal).
    """
    py = get_plan_year(tenant_id, year)
    if py:
        return py

    py = PlanYear(
        tenant_id=tenant_id,
        year=year,
        name=f"{year} Stratejik Planı",
        status="active",
    )
    db.session.add(py)
    db.session.flush()  # id al

    _seed_kpi_year_configs(py, tenant_id)
    _seed_strategy_year_configs(py, tenant_id)
    _seed_process_year_configs(py, tenant_id)
    _seed_individual_kpi_year_configs(py, tenant_id)

    db.session.commit()
    return py


def _seed_kpi_year_configs(plan_year: PlanYear, tenant_id: int) -> None:
    """Mevcut tüm aktif ProcessKpileri bu yılın kpi_year_configs tablosuna ekler."""
    kpis = (
        ProcessKpi.query
        .join(Process)
        .filter(Process.tenant_id == tenant_id, Process.is_active.is_(True))
        .filter(ProcessKpi.is_active.is_(True))
        .all()
    )
    for kpi in kpis:
        cfg = KpiYearConfig(
            plan_year_id=plan_year.id,
            process_kpi_id=kpi.id,
            target_value=kpi.target_value,
            unit=kpi.unit,
            period=kpi.period,
            direction=kpi.direction,
            target_method=kpi.target_method,
            calculation_method=kpi.data_collection_method,
            basari_puani_araliklari=kpi.basari_puani_araliklari,
            onceki_yil_ortalamasi=kpi.onceki_yil_ortalamasi,
            weight=kpi.weight,
            is_included=True,
        )
        db.session.add(cfg)


def _seed_strategy_year_configs(plan_year: PlanYear, tenant_id: int) -> None:
    """Mevcut tüm aktif stratejileri bu yılın strategy_year_configs tablosuna ekler."""
    strategies = Strategy.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    for s in strategies:
        db.session.add(StrategyYearConfig(
            plan_year_id=plan_year.id,
            strategy_id=s.id,
            title=s.title,
            code=s.code,
            description=s.description,
            is_included=True,
        ))
        for ss in (s.sub_strategies or []):
            if not ss.is_active:
                continue
            db.session.add(SubStrategyYearConfig(
                plan_year_id=plan_year.id,
                sub_strategy_id=ss.id,
                title=ss.title,
                code=ss.code,
                description=ss.description,
                is_included=True,
            ))


def _seed_process_year_configs(plan_year: PlanYear, tenant_id: int) -> None:
    """Mevcut tüm aktif süreçleri bu yılın process_year_configs tablosuna ekler."""
    processes = Process.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    for p in processes:
        db.session.add(ProcessYearConfig(
            plan_year_id=plan_year.id,
            process_id=p.id,
            name=p.name,
            weight=p.weight,
            is_included=True,
        ))


def _seed_individual_kpi_year_configs(plan_year: PlanYear, tenant_id: int) -> None:
    """Mevcut tüm aktif bireysel PGleri bu yılın individual_kpi_year_configs tablosuna ekler."""
    from app.models.core import User as _User
    indivs = (
        IndividualPerformanceIndicator.query
        .join(_User, IndividualPerformanceIndicator.user_id == _User.id)
        .filter(_User.tenant_id == tenant_id, _User.is_active.is_(True))
        .filter(IndividualPerformanceIndicator.is_active.is_(True))
        .all()
    )
    for ind in indivs:
        db.session.add(IndividualKpiYearConfig(
            plan_year_id=plan_year.id,
            individual_performance_id=ind.id,
            target_value=ind.target_value,
            unit=ind.unit,
            period=ind.period,
            direction=ind.direction,
            target_method=getattr(ind, "target_method", None),
            calculation_method=None,
            basari_puani_araliklari=ind.basari_puani_araliklari,
            weight=ind.weight,
            is_included=True,
        ))


# ── KPI Config Fallback ────────────────────────────────────────────────────────

def get_kpi_config(kpi: ProcessKpi, plan_year: Optional[PlanYear]) -> Dict[str, Any]:
    """
    Yıla özgü KPI konfigürasyonunu döner.
    Yıllık config yoksa ProcessKpi'ın orijinal değerleri fallback olarak kullanılır.
    Tüm alanlar None değilse yıllık configden, None ise ProcessKpi'dan alınır.
    """
    if plan_year:
        cfg: Optional[KpiYearConfig] = _first_or_none(
            KpiYearConfig.query.filter_by(
                plan_year_id=plan_year.id,
                process_kpi_id=kpi.id
            )
        )
        if cfg:
            return {
                "target_value": cfg.target_value if cfg.target_value is not None else kpi.target_value,
                "unit": cfg.unit if cfg.unit is not None else kpi.unit,
                "period": cfg.period if cfg.period is not None else kpi.period,
                "direction": cfg.direction if cfg.direction is not None else (kpi.direction or "Increasing"),
                "target_method": cfg.target_method if cfg.target_method is not None else kpi.target_method,
                "data_collection_method": cfg.calculation_method if cfg.calculation_method is not None else (kpi.data_collection_method or "Ortalama"),
                "basari_puani_araliklari": cfg.basari_puani_araliklari if cfg.basari_puani_araliklari is not None else kpi.basari_puani_araliklari,
                "onceki_yil_ortalamasi": cfg.onceki_yil_ortalamasi if cfg.onceki_yil_ortalamasi is not None else kpi.onceki_yil_ortalamasi,
                "weight": cfg.weight if cfg.weight is not None else kpi.weight,
                "is_included": cfg.is_included,
                "_config_source": "year",
                "_year_config_id": cfg.id,
            }

    # Fallback → ProcessKpi orijinal değerleri
    return {
        "target_value": kpi.target_value,
        "unit": kpi.unit,
        "period": kpi.period,
        "direction": kpi.direction or "Increasing",
        "target_method": kpi.target_method,
        "data_collection_method": kpi.data_collection_method or "Ortalama",
        "basari_puani_araliklari": kpi.basari_puani_araliklari,
        "onceki_yil_ortalamasi": kpi.onceki_yil_ortalamasi,
        "weight": kpi.weight,
        "is_included": True,
        "_config_source": "process_kpi",
        "_year_config_id": None,
    }


def get_kpi_configs_bulk(
    kpis: List[ProcessKpi], plan_year: Optional[PlanYear]
) -> Dict[int, Dict[str, Any]]:
    """
    Birden fazla KPI için yıllık config sözlüğü döner: {kpi_id: config_dict}.
    N+1 sorgusunu önlemek için tek sorguda tüm KpiYearConfig kayıtlarını çeker.
    """
    result: Dict[int, Dict[str, Any]] = {}
    if not kpis:
        return result

    year_cfg_map: Dict[int, KpiYearConfig] = {}
    if plan_year:
        kpi_ids = [k.id for k in kpis]
        cfgs = KpiYearConfig.query.filter(
            KpiYearConfig.plan_year_id == plan_year.id,
            KpiYearConfig.process_kpi_id.in_(kpi_ids)
        ).all()
        year_cfg_map = {c.process_kpi_id: c for c in cfgs}

    for kpi in kpis:
        cfg = year_cfg_map.get(kpi.id)
        if cfg:
            result[kpi.id] = {
                "target_value": cfg.target_value if cfg.target_value is not None else kpi.target_value,
                "unit": cfg.unit if cfg.unit is not None else kpi.unit,
                "period": cfg.period if cfg.period is not None else kpi.period,
                "direction": cfg.direction if cfg.direction is not None else (kpi.direction or "Increasing"),
                "target_method": cfg.target_method if cfg.target_method is not None else kpi.target_method,
                "data_collection_method": cfg.calculation_method if cfg.calculation_method is not None else (kpi.data_collection_method or "Ortalama"),
                "basari_puani_araliklari": cfg.basari_puani_araliklari if cfg.basari_puani_araliklari is not None else kpi.basari_puani_araliklari,
                "onceki_yil_ortalamasi": cfg.onceki_yil_ortalamasi if cfg.onceki_yil_ortalamasi is not None else kpi.onceki_yil_ortalamasi,
                "weight": cfg.weight if cfg.weight is not None else kpi.weight,
                "is_included": cfg.is_included,
                "_config_source": "year",
                "_year_config_id": cfg.id,
            }
        else:
            result[kpi.id] = {
                "target_value": kpi.target_value,
                "unit": kpi.unit,
                "period": kpi.period,
                "direction": kpi.direction or "Increasing",
                "target_method": kpi.target_method,
                "data_collection_method": kpi.data_collection_method or "Ortalama",
                "basari_puani_araliklari": kpi.basari_puani_araliklari,
                "onceki_yil_ortalamasi": kpi.onceki_yil_ortalamasi,
                "weight": kpi.weight,
                "is_included": True,
                "_config_source": "process_kpi",
                "_year_config_id": None,
            }

    return result


# ── Plan Year Yaşam Döngüsü ────────────────────────────────────────────────────

def close_plan_year(plan_year: PlanYear, actor_id: Optional[int] = None) -> PlanYear:
    """
    Plan yılını kapatır (status=closed).
    Kapalı bir yıl artık düzenlenemez; arşivlenmiş geçmiş olarak korunur.
    """
    plan_year.status = "closed"
    plan_year.closed_at = datetime.now(timezone.utc)
    try:
        db.session.commit()
        current_app.logger.info(
            f"[plan_year_service] PlanYear {plan_year.year} kapatıldı (actor={actor_id})"
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[plan_year_service] close_plan_year hata: {e}")
        raise
    return plan_year


def clone_plan_year(
    source: PlanYear,
    new_year: int,
    name: Optional[str] = None,
    compute_prev_year_averages: bool = True,
) -> PlanYear:
    """
    Kaynak plan yılından yeni yıl oluşturur.
    - KpiYearConfig, StrategyYearConfig, SubStrategyYearConfig, ProcessYearConfig,
      IndividualKpiYearConfig kayıtları kopyalanır.
    - onceki_yil_ortalamasi: kaynak yılın KpiData gerçekleşen ortalamasından hesaplanır.
    - Hedef değerler kopyalanır; kullanıcı üzerine yazabilir.
    """
    tenant_id = source.tenant_id

    # Var mı kontrolü
    existing = get_plan_year(tenant_id, new_year)
    if existing:
        raise ValueError(f"{new_year} yılı için bu tenant'ta zaten bir plan mevcut (id={existing.id})")

    new_py = PlanYear(
        tenant_id=tenant_id,
        year=new_year,
        name=name or f"{new_year} Stratejik Planı",
        status="draft",
        template_source_id=source.id,
    )
    db.session.add(new_py)
    db.session.flush()

    # Önceki yıl gerçekleşen ortalamaları (onceki_yil_ortalamasi alanı)
    prev_actuals: Dict[int, Optional[float]] = {}
    if compute_prev_year_averages:
        prev_actuals = _compute_prev_year_actuals(source)

    # KpiYearConfig kopyala
    src_kpi_cfgs = source.kpi_year_configs.all()
    for src_cfg in src_kpi_cfgs:
        prev_avg = prev_actuals.get(src_cfg.process_kpi_id)
        db.session.add(KpiYearConfig(
            plan_year_id=new_py.id,
            process_kpi_id=src_cfg.process_kpi_id,
            target_value=src_cfg.target_value,
            unit=src_cfg.unit,
            period=src_cfg.period,
            direction=src_cfg.direction,
            target_method=src_cfg.target_method,
            calculation_method=src_cfg.calculation_method,
            basari_puani_araliklari=src_cfg.basari_puani_araliklari,
            onceki_yil_ortalamasi=prev_avg if prev_avg is not None else src_cfg.onceki_yil_ortalamasi,
            weight=src_cfg.weight,
            is_included=src_cfg.is_included,
        ))

    # StrategyYearConfig kopyala
    for src_cfg in source.strategy_year_configs.all():
        db.session.add(StrategyYearConfig(
            plan_year_id=new_py.id,
            strategy_id=src_cfg.strategy_id,
            title=src_cfg.title,
            code=src_cfg.code,
            description=src_cfg.description,
            is_included=src_cfg.is_included,
            weight=src_cfg.weight,
        ))

    # SubStrategyYearConfig kopyala
    for src_cfg in source.sub_strategy_year_configs.all():
        db.session.add(SubStrategyYearConfig(
            plan_year_id=new_py.id,
            sub_strategy_id=src_cfg.sub_strategy_id,
            title=src_cfg.title,
            code=src_cfg.code,
            description=src_cfg.description,
            is_included=src_cfg.is_included,
        ))

    # ProcessYearConfig kopyala
    for src_cfg in source.process_year_configs.all():
        db.session.add(ProcessYearConfig(
            plan_year_id=new_py.id,
            process_id=src_cfg.process_id,
            name=src_cfg.name,
            weight=src_cfg.weight,
            is_included=src_cfg.is_included,
        ))

    # IndividualKpiYearConfig kopyala
    for src_cfg in source.individual_kpi_year_configs.all():
        db.session.add(IndividualKpiYearConfig(
            plan_year_id=new_py.id,
            individual_performance_id=src_cfg.individual_performance_id,
            target_value=src_cfg.target_value,
            unit=src_cfg.unit,
            period=src_cfg.period,
            direction=src_cfg.direction,
            target_method=src_cfg.target_method,
            calculation_method=src_cfg.calculation_method,
            basari_puani_araliklari=src_cfg.basari_puani_araliklari,
            weight=src_cfg.weight,
            is_included=src_cfg.is_included,
        ))

    # Kaynak yılda olup yeni yılda henüz config olmayan KPIler için ekle
    _backfill_missing_kpi_configs(new_py, tenant_id, prev_actuals)

    db.session.commit()
    current_app.logger.info(
        f"[plan_year_service] PlanYear klonlandı: {source.year} → {new_year} (id={new_py.id})"
    )
    return new_py


def _compute_prev_year_actuals(plan_year: PlanYear) -> Dict[int, Optional[float]]:
    """
    Verilen plan yılının KpiData gerçekleşen verilerinden her KPI için
    yıllık ortalama hesaplar. onceki_yil_ortalamasi alanını doldurmak için kullanılır.
    """
    from app.models.process import KpiData

    entries = (
        KpiData.query
        .filter_by(year=plan_year.year, is_active=True)
        .all()
    )
    by_kpi: Dict[int, list] = {}
    for e in entries:
        by_kpi.setdefault(e.process_kpi_id, []).append(e.actual_value)

    result: Dict[int, Optional[float]] = {}
    for kpi_id, vals in by_kpi.items():
        nums = []
        for v in vals:
            try:
                nums.append(float(v))
            except (TypeError, ValueError):
                pass
        result[kpi_id] = round(sum(nums) / len(nums), 6) if nums else None
    return result


def _backfill_missing_kpi_configs(plan_year: PlanYear, tenant_id: int, prev_actuals: Dict) -> None:
    """
    Klonlama sonrası kaynak yılda olmayıp şu an aktif olan KPIler için
    kpi_year_configs ekler (yeni KPI eklendiyse).
    """
    existing_ids = {
        c.process_kpi_id for c in plan_year.kpi_year_configs.all()
    }
    all_kpis = (
        ProcessKpi.query
        .join(Process)
        .filter(Process.tenant_id == tenant_id, Process.is_active.is_(True))
        .filter(ProcessKpi.is_active.is_(True))
        .all()
    )
    for kpi in all_kpis:
        if kpi.id not in existing_ids:
            db.session.add(KpiYearConfig(
                plan_year_id=plan_year.id,
                process_kpi_id=kpi.id,
                target_value=kpi.target_value,
                unit=kpi.unit,
                period=kpi.period,
                direction=kpi.direction,
                target_method=kpi.target_method,
                calculation_method=kpi.data_collection_method,
                basari_puani_araliklari=kpi.basari_puani_araliklari,
                onceki_yil_ortalamasi=prev_actuals.get(kpi.id),
                weight=kpi.weight,
                is_included=True,
            ))


# ── KpiYearConfig Güncelleme ────────────────────────────────────────────────────

def upsert_kpi_year_config(
    plan_year: PlanYear,
    kpi_id: int,
    data: Dict[str, Any],
) -> KpiYearConfig:
    """
    KpiYearConfig kaydını günceller; yoksa oluşturur.
    data: {target_value, unit, period, direction, target_method,
           calculation_method, basari_puani_araliklari, onceki_yil_ortalamasi,
           weight, is_included}
    """
    cfg = KpiYearConfig.query.filter_by(
        plan_year_id=plan_year.id, process_kpi_id=kpi_id
    ).first()

    if cfg is None:
        kpi = ProcessKpi.query.get(kpi_id)
        if not kpi:
            raise ValueError(f"ProcessKpi id={kpi_id} bulunamadı")
        cfg = KpiYearConfig(plan_year_id=plan_year.id, process_kpi_id=kpi_id)
        db.session.add(cfg)

    updatable = [
        "target_value", "unit", "period", "direction", "target_method",
        "calculation_method", "basari_puani_araliklari", "onceki_yil_ortalamasi",
        "weight", "is_included",
    ]
    for field in updatable:
        if field in data:
            setattr(cfg, field, data[field])

    db.session.commit()
    return cfg
