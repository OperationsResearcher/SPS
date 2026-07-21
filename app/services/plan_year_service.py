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

from flask import current_app, session

from app.models import db
from app.models.plan_year import (
    PlanYear,
    KpiYearConfig,
    StrategyYearConfig,
    SubStrategyYearConfig,
    ProcessYearConfig,
    IndividualKpiYearConfig,
    PlanYearSealAudit,
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

    Yıl bazlı Faz 1.8 (T9/T2, 2026-07-20) — DAVRANIŞ DEĞİŞTİ:
      ESKİ: yeni yıl açılınca *_year_configs (override) tabloları seed edilirdi;
            varlık kopyası ÜRETİLMEZDİ. Yani yeni yılda süreç/PG yoktu, yalnız
            config satırları vardı.
      YENİ: T9 full-clone tek mekanizma. Yeni yıl, bir önceki DOLU yıldan
            clone_full_plan_year ile klonlanır — süreçler, PG'ler, stratejiler
            ve hedefleriyle birlikte (T2: "yıl devrinde her şey kopyalanır").
            Klonlanacak önceki yıl yoksa boş plan yılı açılır.

    S9 (seed açığı) bu değişiklikle kökten kapanır: seed ayrı bir adım değil,
    yıl oluşturmanın kendisidir. Ham INSERT ile açılan yıllarda seed'in
    atlanması sorunu (KMF #16 ve Eskişehir #28'de hedefli config = 0) artık
    doğmaz.
    """
    py = get_plan_year(tenant_id, year)
    if py:
        return py

    # Klonlanacak kaynak: bu yıldan önceki EN YAKIN dolu yıl; yoksa sonraki
    # en yakın dolu yıl (Faz 1.2'deki geriye klonlama ile aynı mantık —
    # kurumun yapısı ileri bir yılda olabilir).
    kaynak = (
        PlanYear.query
        .filter(PlanYear.tenant_id == tenant_id, PlanYear.year < year)
        .filter(Process.query.filter(
            Process.plan_year_id == PlanYear.id).exists())
        .order_by(PlanYear.year.desc())
        .first()
    )
    if kaynak is None:
        kaynak = (
            PlanYear.query
            .filter(PlanYear.tenant_id == tenant_id, PlanYear.year > year)
            .filter(Process.query.filter(
                Process.plan_year_id == PlanYear.id).exists())
            .order_by(PlanYear.year.asc())
            .first()
        )

    if kaynak is not None:
        return clone_full_plan_year(kaynak, year)

    # Klonlanacak yapı yok — boş plan yılı aç (yeni kurumun ilk yılı)
    py = PlanYear(
        tenant_id=tenant_id,
        year=year,
        name=f"{year} Stratejik Planı",
        status="active",
    )
    db.session.add(py)
    db.session.commit()
    return py


# ── ÖLÜ KOD (yıl bazlı Faz 1.8, 2026-07-20) ──────────────────────────────────
# Aşağıdaki dört _seed_* fonksiyonu ARTIK ÇAĞRILMIYOR.
#
# T9 (full-clone tek mekanizma) override tablolarını kaldırıyor; yeni yıl
# artık clone_full_plan_year ile gerçek varlık kopyaları üreterek doğuyor.
# Bu fonksiyonlar ise *_year_configs satırı yazıyordu — Faz 1.4'te "artık veri"
# olarak temizlediğimiz 2570 satırın kaynağı tam olarak buydu.
#
# SİLİNMEDİLER çünkü override tabloları henüz DROP edilmedi (bilinçli: göç
# doğrulanana kadar geri dönüş yolu açık). Tablolar düşürüldüğünde bu blok da
# silinecek. Yeni kod bunları ÇAĞIRMASIN.
# ─────────────────────────────────────────────────────────────────────────────

def _seed_kpi_year_configs(plan_year: PlanYear, tenant_id: int) -> None:
    """[ÖLÜ KOD — bkz. yukarıdaki not] Aktif ProcessKpi'leri kpi_year_configs'e ekler."""
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

def close_plan_year(
    plan_year: PlanYear,
    actor_id: Optional[int] = None,
    reason: Optional[str] = None,
    actor_label: Optional[str] = None,
) -> PlanYear:
    """Plan yılını MÜHÜRLER (status=closed).

    Yıl bazlı Faz 2 (K7/K8/S13, 2026-07-20) — DAVRANIŞ DEĞİŞTİ:

      ESKİ: yalnız `status` + `closed_at` yazıyordu. Docstring "kapalı bir yıl
            artık düzenlenemez" diyordu ama KODDA KARŞILIĞI YOKTU — kapalı yıla
            serbestçe veri girilip silinebiliyordu (HASAR-TESPITI-2.md §13).
      YENİ: mühür gerçekten uygulanır (yazma yollarındaki `plan_year_writable`
            kontrolü) ve olay denetim tablosuna işlenir (S13).

    K8 gereği mühür mutlaktır: kapalı yıla veri girişi/düzenlemesi/silmesi
    yapılamaz. Geri dönüş yalnızca `reopen_plan_year` ile, kurum üst yönetimi
    tarafından ve gerekçeyle mümkündür (K9).
    """
    # K9 (2026-07-21): mühürlenen yıl kurumun AKTİF yılı mıydı? Bu bilgi
    # `reopen` sırasında statüyü doğru geri yüklemek için gerekli — aksi
    # halde aktif yılın kendisi mühürlenip açıldığında kurum aktif yılsız
    # kalıyordu. Ayrı kolon eklemek yerine denetim kaydının `action`
    # alanında taşınıyor (migration gerektirmez, geçmiş kayıtlar bozulmaz).
    aktif_miydi = (plan_year.status or "").strip().lower() == "active"

    plan_year.status = "closed"
    plan_year.closed_at = datetime.now(timezone.utc)
    try:
        db.session.add(PlanYearSealAudit(
            plan_year_id=plan_year.id,
            tenant_id=plan_year.tenant_id,
            action="close_active" if aktif_miydi else "close",
            reason=(reason or "").strip() or "(gerekçe belirtilmedi)",
            actor_id=actor_id,
            actor_label=actor_label,
        ))
        db.session.commit()
        current_app.logger.info(
            f"[plan_year_service] PlanYear {plan_year.year} MÜHÜRLENDİ "
            f"(tenant={plan_year.tenant_id} actor={actor_id})"
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[plan_year_service] close_plan_year hata: {e}")
        raise
    return plan_year


def reopen_plan_year(
    plan_year: PlanYear,
    reason: str,
    actor_id: Optional[int] = None,
    actor_label: Optional[str] = None,
) -> PlanYear:
    """Mührü AÇAR — plan yılını yeniden yazılabilir yapar (K9).

    Bu fonksiyon yıl bazlı Faz 2'de YENİ eklendi. Öncesinde sistemde
    `status="active"` atayan hiçbir route/servis yoktu: yanlışlıkla kapatılan
    bir yılı kurtarmanın tek yolu doğrudan DB müdahalesiydi
    (HASAR-TESPITI-2.md §13.1).

    K9: yetki kurum üst yönetimindedir — kontrol route katmanında.
    S13: `reason` ZORUNLU. Gerekçesiz açma kabul edilmez; mühür açma geri
         alınamaz bir güvenlik kapısıdır, izlenebilir olmalıdır.
    T1:  gecikmeli veri için tolerans yoktur; unutulan veriyi girmenin tek
         yolu budur — mühür aç, veriyi gir, yılı tekrar mühürle.

    STATÜ GERİ YÜKLEME (K9 düzeltmesi, 2026-07-21):
        İlk sürüm koşulsuz `draft` yazıyordu; gerekçe "kurumun aktif çalışma
        yılı genellikle başkasıdır" idi. "Genellikle" yeterli değilmiş:
        AKTİF YILIN KENDİSİ mühürlenip açıldığında kurum aktif yılsız
        kalıyordu (Tomofil 2026 `active` → mühürle → aç → `draft`).

        Artık mühürleme anındaki statü denetim kaydından okunur
        (`action="close_active"`) ve geri yüklenir. Kurumda o sırada başka
        bir `active` yıl varsa çakışmayı önlemek için `draft` verilir —
        `get_active_plan_year` tek aktif yıl varsayıyor.
    """
    temiz = (reason or "").strip()
    if not temiz:
        raise ValueError("Mühür açma gerekçesi zorunludur (S13).")

    hedef_statu = "draft"
    try:
        son_kapatma = (
            PlanYearSealAudit.query
            .filter(
                PlanYearSealAudit.plan_year_id == plan_year.id,
                PlanYearSealAudit.action.in_(("close", "close_active")),
            )
            .order_by(PlanYearSealAudit.created_at.desc())
            .first()
        )
        if son_kapatma is not None and son_kapatma.action == "close_active":
            baska_aktif = PlanYear.query.filter(
                PlanYear.tenant_id == plan_year.tenant_id,
                PlanYear.status == "active",
                PlanYear.id != plan_year.id,
            ).first()
            if baska_aktif is None:
                hedef_statu = "active"
            else:
                current_app.logger.info(
                    "[plan_year_service] PlanYear %s mühürlenirken aktifti ama "
                    "kurumda artık %s aktif — draft olarak açılıyor.",
                    plan_year.year, baska_aktif.year,
                )
    except Exception as e:
        # Denetim kaydı okunamazsa güvenli tarafta kal: draft.
        current_app.logger.error(
            "[plan_year_service] reopen statü çözümlenemedi (draft'a düşüldü): %s", e
        )

    plan_year.status = hedef_statu
    plan_year.closed_at = None
    try:
        db.session.add(PlanYearSealAudit(
            plan_year_id=plan_year.id,
            tenant_id=plan_year.tenant_id,
            action="reopen",
            reason=temiz,
            actor_id=actor_id,
            actor_label=actor_label,
        ))
        db.session.commit()
        current_app.logger.info(
            f"[plan_year_service] PlanYear {plan_year.year} MÜHRÜ AÇILDI "
            f"(tenant={plan_year.tenant_id} actor={actor_id}) gerekçe={temiz[:80]!r}"
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[plan_year_service] reopen_plan_year hata: {e}")
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


# ── Geçmiş Yıl Başlatma ────────────────────────────────────────────────────────

def initialize_plan_years(tenant_id: int, start_year: int) -> List[PlanYear]:
    """
    start_year'dan bugüne kadar olan tüm yıllar için plan_year kayıtları oluşturur.
    - Zaten var olan yıllar atlanır.
    - Zaten aktif bir plan_year varsa onun status'u değiştirilmez.
    Döner: oluşturulan veya mevcut PlanYear listesi (start_year→bugün).

    Yıl bazlı Faz 1.8 (2026-07-20) — İKİ DAVRANIŞ DEĞİŞTİ:

    1) T11 — geçmiş yıllar artık `closed` DEĞİL, `draft` açılır.
       Mühür (kilit) gerçek olduğu için "kapalı" bilinçli bir kurum kararıdır;
       sistem kendiliğinden yıl mühürlemez. Eskiden geçmiş yıllar otomatik
       closed açılıyordu ve o etiket hiçbir koruma sağlamıyordu.

    2) T9/S9 — override seed'i yerine full-clone.
       Yıllar get_or_create_plan_year üzerinden üretilir; o da bir önceki dolu
       yıldan clone_full_plan_year ile klonlar (T2). Böylece yeni yılda gerçek
       süreç/PG kopyaları doğar. Eski davranış yalnız *_year_configs satırı
       yazıyordu — yapı üretmiyordu, S9'daki seed açığının kaynağı buydu.
    """
    from datetime import date
    current_year = date.today().year
    if start_year > current_year:
        raise ValueError(f"Başlangıç yılı ({start_year}) mevcut yıldan ({current_year}) büyük olamaz.")

    years = list(range(start_year, current_year + 1))
    result: List[PlanYear] = []

    for yr in years:
        existing = get_plan_year(tenant_id, yr)
        if existing:
            result.append(existing)
            continue

        # T9/S9: yapıyı da üreten tek giriş noktası. get_or_create_plan_year
        # bir önceki dolu yıldan klonlar; yoksa boş yıl açar.
        py = get_or_create_plan_year(tenant_id, yr)

        # T11: sistem kendiliğinden yıl mühürlemez. Yalnız içinde bulunulan
        # yıl 'active', geçmiş yıllar 'draft' kalır — kapatma kurum kararıdır.
        py.status = "active" if yr == current_year else "draft"

        result.append(py)

    db.session.commit()
    current_app.logger.info(
        f"[plan_year_service] initialize_plan_years tenant={tenant_id} "
        f"start={start_year} created={sum(1 for py in result if not db.session.is_modified(py) is False)}"
    )
    return result


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


# ── Tam Klon (Full Clone) ─────────────────────────────────────────────────────

def clone_full_plan_year(
    source: PlanYear,
    new_year: int,
    name: Optional[str] = None,
    as_scenario_label: Optional[str] = None,
    into_existing: Optional[PlanYear] = None,
) -> PlanYear:
    """
    Kaynak SP döneminin TÜM yapısını yeni yıla klonlar (Full Clone sistemi).

    Klonlanan yapılar (sırasıyla):
      1. Strategy          → source_strategy_id zinciri
      2. SubStrategy       → source_sub_strategy_id zinciri
      3. Process           → source_process_id zinciri (parent hiyerarşisi korunur)
      4. ProcessSubStrategyLink → yeni process/sub_strategy ID'leriyle yeniden kurulur
      5. ProcessKpi        → source_kpi_id zinciri; onceki_yil_ortalamasi hesaplanır
      6. ProcessActivity   → şablon olarak aktarılır (tarih/status sıfırlanır)
      7. IndividualPerformanceIndicator → source_individual_kpi_id zinciri
      8. TenantYearIdentity → misyon/vizyon/değerler kopyalanır
      9. SwotAnalysis + TowsAnalysis → boş kayıtlar oluşturulur

    into_existing (yıl bazlı Faz 1.2, 2026-07-20):
        Hedef yılın PlanYear kaydı ZATEN VARSA ve içi boşsa, yeni kayıt açmak
        yerine o kayda klonlar. Neden gerekli: göç sırasında boş yıllar mevcut
        (Faz 1.3'te üretildi) ve onlara `individual_performance_indicators` gibi
        tablolar bağlanmış durumda. Kaydı silip yeniden yaratmak o satırları
        YETİM bırakırdı (ölçüm: KMF'de 13 bireysel PG).
        Kullanan: scripts/ops/yilbazli_faz1_2_clone_zinciri.py

    Dönüş: hedef PlanYear nesnesi (yeni açıldıysa status="draft")
    """
    from app.models.process import (
        ProcessActivity, ProcessActivityAssignee, ProcessSubStrategyLink, KpiData,
    )
    from app.models.tenant_year import TenantYearIdentity
    from app.models.swot import SwotAnalysis, TowsAnalysis

    tenant_id = source.tenant_id

    if into_existing is not None:
        if into_existing.tenant_id != tenant_id:
            raise ValueError(
                f"into_existing tenant uyuşmuyor: {into_existing.tenant_id} != {tenant_id}"
            )
        new_py = into_existing
        new_py.template_source_id = source.id
        db.session.flush()
    else:
        # Sprint 56: scenario mode aynı yıla ikinci kayıt açabilir (partial unique index)
        if not as_scenario_label:
            existing = get_plan_year(tenant_id, new_year)
            if existing:
                raise ValueError(f"{new_year} yılı için tenant {tenant_id}'de zaten plan mevcut (id={existing.id})")

        new_py = PlanYear(
            tenant_id=tenant_id,
            year=new_year,
            name=name or (
                f"{new_year} — {as_scenario_label.title()} Senaryosu"
                if as_scenario_label else f"{new_year} Stratejik Planı"
            ),
            status="draft",
            template_source_id=source.id,
            scenario_of_id=source.id if as_scenario_label else None,
            scenario_label=as_scenario_label,
        )
        db.session.add(new_py)
        db.session.flush()  # new_py.id için

    # ── 1. Strategy klonlama ──────────────────────────────────────────────────
    strategy_id_map: Dict[int, int] = {}   # old_id → new_id
    src_strategies = Strategy.query.filter_by(
        tenant_id=tenant_id, plan_year_id=source.id, is_active=True
    ).all()
    for s in src_strategies:
        new_s = Strategy(
            tenant_id=tenant_id,
            plan_year_id=new_py.id,
            source_strategy_id=s.id,
            code=s.code,
            title=s.title,
            description=s.description,
            is_active=True,
        )
        db.session.add(new_s)
        db.session.flush()
        strategy_id_map[s.id] = new_s.id

    # ── 2. SubStrategy klonlama ───────────────────────────────────────────────
    sub_strategy_id_map: Dict[int, int] = {}
    if strategy_id_map:
        src_sub_strategies = SubStrategy.query.filter(
            SubStrategy.strategy_id.in_(strategy_id_map.keys()),
            SubStrategy.plan_year_id == source.id,
            SubStrategy.is_active.is_(True),
        ).all()
        for ss in src_sub_strategies:
            new_ss = SubStrategy(
                strategy_id=strategy_id_map[ss.strategy_id],
                plan_year_id=new_py.id,
                source_sub_strategy_id=ss.id,
                code=ss.code,
                title=ss.title,
                description=ss.description,
                is_active=True,
            )
            db.session.add(new_ss)
            db.session.flush()
            sub_strategy_id_map[ss.id] = new_ss.id

    # ── 3. Process klonlama (hiyerarşi: parent önce) ──────────────────────────
    process_id_map: Dict[int, int] = {}
    src_processes = (
        Process.query
        .filter_by(tenant_id=tenant_id, plan_year_id=source.id, is_active=True)
        .order_by(Process.parent_id.asc().nullsfirst(), Process.id.asc())
        .all()
    )
    for p in src_processes:
        new_parent_id = process_id_map.get(p.parent_id) if p.parent_id else None
        new_p = Process(
            tenant_id=tenant_id,
            plan_year_id=new_py.id,
            source_process_id=p.id,
            parent_id=new_parent_id,
            code=p.code,
            name=p.name,
            english_name=p.english_name,
            weight=p.weight,
            document_no=p.document_no,
            revision_no=p.revision_no,
            revision_date=p.revision_date,
            first_publish_date=p.first_publish_date,
            status=p.status,
            start_boundary=p.start_boundary,
            end_boundary=p.end_boundary,
            description=p.description,
            is_active=True,
        )
        db.session.add(new_p)
        db.session.flush()
        process_id_map[p.id] = new_p.id

    # ── 4. ProcessSubStrategyLink yeniden kurulumu ────────────────────────────
    for old_proc_id, new_proc_id in process_id_map.items():
        old_links = ProcessSubStrategyLink.query.filter_by(process_id=old_proc_id).all()
        for link in old_links:
            new_ss_id = sub_strategy_id_map.get(link.sub_strategy_id)
            if new_ss_id:
                db.session.add(ProcessSubStrategyLink(
                    process_id=new_proc_id,
                    sub_strategy_id=new_ss_id,
                    contribution_pct=link.contribution_pct,
                ))

    # ── 5. ProcessKpi klonlama ────────────────────────────────────────────────
    kpi_id_map: Dict[int, int] = {}
    prev_actuals = _compute_prev_year_actuals(source)  # KpiData ortalamaları

    src_kpis = (
        ProcessKpi.query
        .filter(
            ProcessKpi.process_id.in_(process_id_map.keys()),
            ProcessKpi.plan_year_id == source.id,
            ProcessKpi.is_active.is_(True),
        )
        .all()
    )
    for k in src_kpis:
        new_sub_strategy_id = sub_strategy_id_map.get(k.sub_strategy_id) if k.sub_strategy_id else None
        avg = prev_actuals.get(k.id)
        new_k = ProcessKpi(
            process_id=process_id_map[k.process_id],
            plan_year_id=new_py.id,
            source_kpi_id=k.id,
            name=k.name,
            description=k.description,
            code=k.code,
            target_value=k.target_value,
            unit=k.unit,
            period=k.period,
            data_source=k.data_source,
            target_setting_method=k.target_setting_method,
            data_collection_method=k.data_collection_method,
            calculation_method=k.calculation_method,
            gosterge_turu=k.gosterge_turu,
            target_method=k.target_method,
            basari_puani_araliklari=k.basari_puani_araliklari,
            onceki_yil_ortalamasi=avg if avg is not None else k.onceki_yil_ortalamasi,
            weight=k.weight,
            is_important=k.is_important,
            direction=k.direction,
            sub_strategy_id=new_sub_strategy_id,
            is_active=True,
        )
        db.session.add(new_k)
        db.session.flush()
        kpi_id_map[k.id] = new_k.id

    # ── 6. ProcessActivity klonlama (şablon: tarih/status sıfırla) ────────────
    src_activities = (
        ProcessActivity.query
        .filter(
            ProcessActivity.process_id.in_(process_id_map.keys()),
            ProcessActivity.plan_year_id == source.id,
            ProcessActivity.is_active.is_(True),
        )
        .all()
    )
    # N+1 önlemi: assignee'leri loop öncesi toplu çek ve activity_id'ye göre indexle
    src_act_ids = [a.id for a in src_activities]
    if src_act_ids:
        all_assignees = ProcessActivityAssignee.query.filter(
            ProcessActivityAssignee.activity_id.in_(src_act_ids)
        ).all()
    else:
        all_assignees = []
    _assignees_by_activity = {}
    for _asgn in all_assignees:
        _assignees_by_activity.setdefault(_asgn.activity_id, []).append(_asgn)

    for a in src_activities:
        new_kpi_id = kpi_id_map.get(a.process_kpi_id) if a.process_kpi_id else None
        new_a = ProcessActivity(
            process_id=process_id_map[a.process_id],
            plan_year_id=new_py.id,
            source_activity_id=a.id,
            process_kpi_id=new_kpi_id,
            name=a.name,
            description=a.description,
            # Şablon aktarım: tarih ve durum sıfırlanır
            status="Planlandı",
            progress=0,
            start_at=None,
            end_at=None,
            start_date=None,
            end_date=None,
            notify_email=a.notify_email,
            auto_complete_enabled=a.auto_complete_enabled,
            is_active=True,
        )
        db.session.add(new_a)
        db.session.flush()

        # Atananları kopyala (toplu çekilen dict'ten — N+1 önlendi)
        for assignee_link in _assignees_by_activity.get(a.id, []):
            db.session.add(ProcessActivityAssignee(
                activity_id=new_a.id,
                user_id=assignee_link.user_id,
                order_no=getattr(assignee_link, "order_no", getattr(assignee_link, "sort_order", getattr(assignee_link, "order", 1))),
                assigned_at=assignee_link.assigned_at,
            ))

    # ── 7. IndividualPerformanceIndicator klonlama ────────────────────────────
    from app.models.core import Tenant as TenantModel
    user_ids = [u.id for u in TenantModel.query.get(tenant_id).users]
    if user_ids:
        src_ind_kpis = (
            IndividualPerformanceIndicator.query
            .filter(
                IndividualPerformanceIndicator.user_id.in_(user_ids),
                IndividualPerformanceIndicator.plan_year_id == source.id,
                IndividualPerformanceIndicator.is_active.is_(True),
            )
            .all()
        )
        for ik in src_ind_kpis:
            new_proc_id = process_id_map.get(ik.source_process_id) if ik.source_process_id else None
            new_kpi_id = kpi_id_map.get(ik.source_process_kpi_id) if ik.source_process_kpi_id else None
            new_ik = IndividualPerformanceIndicator(
                user_id=ik.user_id,
                plan_year_id=new_py.id,
                source_individual_kpi_id=ik.id,
                name=ik.name,
                description=ik.description,
                code=ik.code,
                target_value=ik.target_value,
                unit=ik.unit,
                period=ik.period,
                weight=ik.weight,
                is_important=ik.is_important,
                direction=ik.direction,
                basari_puani_araliklari=ik.basari_puani_araliklari,
                source=ik.source,
                source_process_id=new_proc_id,
                source_process_kpi_id=new_kpi_id,
                is_active=True,
            )
            db.session.add(new_ik)

    # ── 8. TenantYearIdentity klonlama ────────────────────────────────────────
    src_identity = TenantYearIdentity.query.filter_by(plan_year_id=source.id).first()
    if src_identity:
        db.session.add(TenantYearIdentity(
            plan_year_id=new_py.id,
            tenant_id=tenant_id,
            purpose=src_identity.purpose,
            vision=src_identity.vision,
            core_values=src_identity.core_values,
            code_of_ethics=src_identity.code_of_ethics,
            quality_policy=src_identity.quality_policy,
        ))

    # ── 9. SwotAnalysis + TowsAnalysis (boş) ─────────────────────────────────
    db.session.add(SwotAnalysis(plan_year_id=new_py.id, tenant_id=tenant_id))
    db.session.add(TowsAnalysis(plan_year_id=new_py.id, tenant_id=tenant_id))

    db.session.commit()
    current_app.logger.info(
        f"[plan_year_service] clone_full_plan_year: {source.year} → {new_year} "
        f"(strategies={len(strategy_id_map)}, processes={len(process_id_map)}, "
        f"kpis={len(kpi_id_map)}, activities={len(src_activities)})"
    )
    return new_py


# ── Aktif Dönem Yardımcısı ─────────────────────────────────────────────────────

def get_active_plan_year_for_user(user) -> Optional[PlanYear]:
    """
    Kullanıcının aktif SPDönemini döner.

    Tarih egemen doktrin (Faz 1):
    - Session'da sp_active_year varsa o yılın PlanYear'ı (kullanıcı seçimi).
    - Yoksa **bugünün takvim yılı** için PlanYear (UI default'ları ile tutarlı).
    - O da yoksa tenant'ın status='active' PlanYear'ı (legacy fallback).
    - Hiç PlanYear yoksa None.

    Not: Bu fonksiyon "GÖRÜNTÜ" bağlamıdır. Veri yazımı için
    `app.services.date_sovereign.resolve_plan_year_for_date()` kullanın.
    """
    from datetime import date as _date
    from app.models.core import Tenant
    tenant = Tenant.query.get(user.tenant_id)
    if tenant is None:
        return None
    # Yıl bazlı Faz 1.7 (K5): plan_year_enabled kontrolü KALDIRILDI.
    # Yıl bazlılık artık zorunlu; flag'e bakmak, kapalı kurumlarda tüm yıl
    # filtrelerini sessizce devre dışı bırakıyordu (HASAR-TESPITI.md §1).

    year = session.get("sp_active_year")
    if year:
        py = get_plan_year(user.tenant_id, int(year))
        if py:
            return py

    # Bugünün takvim yılı için PlanYear varsa öncelikli (UI default'larıyla tutarlı)
    today_py = get_plan_year(user.tenant_id, _date.today().year)
    if today_py:
        return today_py

    return get_active_plan_year(user.tenant_id)
