#!/usr/bin/env python
"""
Genesis Plan Year Migration
===========================
Mevcut tüm tenant kayıtlarını (plan_year_id=NULL olan) bir "genesis" PlanYear'a atar.

Çalıştırma (VM veya yerel):
    cd /app  (veya proje kökü)
    PYTHONPATH=. python scripts/migrate_genesis_plan_year.py [--dry-run] [--tenant-id=X]

Seçenekler:
    --dry-run       Değişiklikleri veritabanına yazmaz, sadece raporlar.
    --tenant-id=X   Sadece belirtilen tenant için çalışır (test amaçlı).
"""
import sys
import os
import argparse
from datetime import datetime, timezone

# Proje kökünü PYTHONPATH'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from app.models.core import Tenant, Strategy, SubStrategy
from app.models.process import Process, ProcessKpi, ProcessActivity, IndividualPerformanceIndicator
from app.models.plan_year import PlanYear
from app.models.tenant_year import TenantYearIdentity
from app.models.swot import SwotAnalysis, TowsAnalysis


def log(msg: str):
    print(f"[genesis] {msg}", flush=True)


def get_or_create_genesis_year(tenant: Tenant, dry_run: bool) -> PlanYear:
    """
    Tenant için genesis PlanYear'ı döner veya oluşturur.
    Genesis year = tenant.plan_year_start veya mevcut en eski PlanYear yılı veya 2024.
    """
    # Mevcut en küçük yılı bul
    existing = (
        PlanYear.query
        .filter_by(tenant_id=tenant.id)
        .order_by(PlanYear.year.asc())
        .first()
    )

    if existing:
        # Zaten bir plan year var — onu genesis olarak kullan
        log(f"  Tenant {tenant.id} ({tenant.name}): mevcut genesis year = {existing.year} (id={existing.id})")
        return existing

    # Plan year yok — genesis oluştur
    genesis_year = tenant.plan_year_start or 2024
    log(f"  Tenant {tenant.id} ({tenant.name}): genesis PlanYear oluşturuluyor ({genesis_year})")

    if dry_run:
        log(f"    [dry-run] PlanYear({genesis_year}) oluşturulacak")
        # Fake nesne döndür
        fake = PlanYear()
        fake.id = -1
        fake.year = genesis_year
        fake.tenant_id = tenant.id
        return fake

    py = PlanYear(
        tenant_id=tenant.id,
        year=genesis_year,
        name=f"{genesis_year} Stratejik Planı (Genesis)",
        status="active",
    )
    db.session.add(py)
    db.session.flush()  # id al
    return py


def migrate_tenant(tenant: Tenant, dry_run: bool) -> dict:
    """Bir tenant için tüm NULL plan_year_id kayıtlarını genesis'e ata."""
    stats = {
        "strategies": 0, "sub_strategies": 0,
        "processes": 0, "process_kpis": 0, "process_activities": 0,
        "individual_kpis": 0, "tenant_year_identity": 0,
        "swot": 0, "tows": 0,
    }

    genesis = get_or_create_genesis_year(tenant, dry_run)
    if genesis.id == -1:
        log(f"  [dry-run] Atama yapılacak ama commit edilmeyecek.")
        return stats

    genesis_id = genesis.id

    # ── Strategies ──────────────────────────────────────────────────────────────
    strats = Strategy.query.filter_by(tenant_id=tenant.id).filter(Strategy.plan_year_id.is_(None)).all()
    for s in strats:
        if not dry_run:
            s.plan_year_id = genesis_id
        stats["strategies"] += 1

    # ── SubStrategies ───────────────────────────────────────────────────────────
    strategy_ids = [s.id for s in Strategy.query.filter_by(tenant_id=tenant.id).all()]
    if strategy_ids:
        sub_strats = (
            SubStrategy.query
            .filter(SubStrategy.strategy_id.in_(strategy_ids))
            .filter(SubStrategy.plan_year_id.is_(None))
            .all()
        )
        for ss in sub_strats:
            if not dry_run:
                ss.plan_year_id = genesis_id
            stats["sub_strategies"] += 1

    # ── Processes ───────────────────────────────────────────────────────────────
    procs = Process.query.filter_by(tenant_id=tenant.id).filter(Process.plan_year_id.is_(None)).all()
    for p in procs:
        if not dry_run:
            p.plan_year_id = genesis_id
        stats["processes"] += 1

    # ── ProcessKpis ─────────────────────────────────────────────────────────────
    proc_ids = [p.id for p in Process.query.filter_by(tenant_id=tenant.id).all()]
    if proc_ids:
        kpis = (
            ProcessKpi.query
            .filter(ProcessKpi.process_id.in_(proc_ids))
            .filter(ProcessKpi.plan_year_id.is_(None))
            .all()
        )
        for k in kpis:
            if not dry_run:
                k.plan_year_id = genesis_id
            stats["process_kpis"] += 1

        # ── ProcessActivities ────────────────────────────────────────────────────
        acts = (
            ProcessActivity.query
            .filter(ProcessActivity.process_id.in_(proc_ids))
            .filter(ProcessActivity.plan_year_id.is_(None))
            .all()
        )
        for a in acts:
            if not dry_run:
                a.plan_year_id = genesis_id
            stats["process_activities"] += 1

    # ── IndividualPerformanceIndicators ─────────────────────────────────────────
    user_ids = [u.id for u in tenant.users]
    if user_ids:
        ind_kpis = (
            IndividualPerformanceIndicator.query
            .filter(IndividualPerformanceIndicator.user_id.in_(user_ids))
            .filter(IndividualPerformanceIndicator.plan_year_id.is_(None))
            .all()
        )
        for ik in ind_kpis:
            if not dry_run:
                ik.plan_year_id = genesis_id
            stats["individual_kpis"] += 1

    # ── TenantYearIdentity ──────────────────────────────────────────────────────
    existing_identity = TenantYearIdentity.query.filter_by(plan_year_id=genesis_id).first()
    if not existing_identity and not dry_run:
        identity = TenantYearIdentity(
            plan_year_id=genesis_id,
            tenant_id=tenant.id,
            purpose=tenant.purpose,
            vision=tenant.vision,
            core_values=tenant.core_values,
            code_of_ethics=tenant.code_of_ethics,
            quality_policy=tenant.quality_policy,
        )
        db.session.add(identity)
        stats["tenant_year_identity"] = 1
    elif not existing_identity:
        stats["tenant_year_identity"] = 1  # would create

    # ── SwotAnalysis (boş) ──────────────────────────────────────────────────────
    existing_swot = SwotAnalysis.query.filter_by(plan_year_id=genesis_id, tenant_id=tenant.id).first()
    if not existing_swot and not dry_run:
        swot = SwotAnalysis(plan_year_id=genesis_id, tenant_id=tenant.id)
        db.session.add(swot)
        stats["swot"] = 1
    elif not existing_swot:
        stats["swot"] = 1

    # ── TowsAnalysis (boş) ──────────────────────────────────────────────────────
    existing_tows = TowsAnalysis.query.filter_by(plan_year_id=genesis_id, tenant_id=tenant.id).first()
    if not existing_tows and not dry_run:
        tows = TowsAnalysis(plan_year_id=genesis_id, tenant_id=tenant.id)
        db.session.add(tows)
        stats["tows"] = 1
    elif not existing_tows:
        stats["tows"] = 1

    return stats


def main():
    parser = argparse.ArgumentParser(description="Genesis PlanYear migration")
    parser.add_argument("--dry-run", action="store_true", help="Veritabanına yazmaz")
    parser.add_argument("--tenant-id", type=int, default=None, help="Sadece bu tenant")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        tenants_q = Tenant.query.filter_by(is_active=True)
        if args.tenant_id:
            tenants_q = tenants_q.filter_by(id=args.tenant_id)
        tenants = tenants_q.all()

        log(f"{'[DRY-RUN] ' if args.dry_run else ''}Toplam {len(tenants)} aktif tenant işlenecek.")

        total = {k: 0 for k in ["strategies", "sub_strategies", "processes",
                                  "process_kpis", "process_activities",
                                  "individual_kpis", "tenant_year_identity", "swot", "tows"]}
        for tenant in tenants:
            log(f"\nTenant: {tenant.id} — {tenant.name}")
            stats = migrate_tenant(tenant, args.dry_run)
            for k, v in stats.items():
                total[k] += v
                if v:
                    log(f"    {k}: {v} kayıt {'güncellenecek' if args.dry_run else 'güncellendi'}")

        if not args.dry_run:
            db.session.commit()
            log("\n✅ Tüm değişiklikler commit edildi.")
        else:
            db.session.rollback()
            log("\n[dry-run] Değişiklikler yazılmadı.")

        log("\n=== ÖZET ===")
        for k, v in total.items():
            log(f"  {k}: {v}")


if __name__ == "__main__":
    main()
