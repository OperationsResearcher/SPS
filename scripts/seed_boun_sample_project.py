# -*- coding: utf-8 -*-
"""
Boğaziçi Üniversitesi (BOUN) tenant’ı için örnek proje tohumu:
  • 1 proje lideri (yönetici)
  • 5 proje üyesi
  • 20 görev (12’si Tamamlandı, 8’i açık/devam)

Kullanım (proje kökünden):
  py scripts/seed_boun_sample_project.py
  py scripts/seed_boun_sample_project.py --tenant-id 7
  py scripts/seed_boun_sample_project.py --replace   # aynı isimli demo projeyi silip yeniden oluşturur
  py scripts/seed_boun_sample_project.py --dry-run

Not: `project` / `task` FK’leri legacy `user` tablosuna işaret eder; bu ortamda çoğu kurulumda
`users` (Core) ile aynı tamsayı kimlikler kullanılır. Kurumda en az 6 aktif kullanıcı olmalıdır.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from sqlalchemy import delete, insert, or_
from sqlalchemy.orm import joinedload

from app import create_app
from app.models import db
from app.models.core import Tenant, User as CoreUser
from models.project import Project, Task, project_members, project_leaders, project_observers

# Tekilleştirme için sabit proje adı
PROJECT_NAME = "[BOUN Demo] Kurumsal kalite ve dijital süreç iyileştirme"
PROJECT_DESC = (
    "Boğaziçi Üniversitesi için örnek (demo) proje: süreç iyileştirme, KPI ve dijital dönüşüm "
    "adımlarını kapsar. Üretim verisidir; gerektiğinde --replace ile silinip yeniden oluşturulabilir."
)

# 20 görev başlığı — ilk 12 tamamlanmış sayılır
TASK_TITLES: list[str] = [
    "Paydaş analizi ve ihtiyaç çalıştayı",
    "Proje tüzüğü ve iletişim planı",
    "Mevcut süreç haritalama (AS-IS)",
    "Risk kaydı — ilk sürüm",
    "KPI taslağı ve ölçüm tanımları",
    "Pilot birim seçimi ve onayı",
    "Ekip içi eğitim materyalleri",
    "Veri erişim izinleri ve KVKK kontrol listesi",
    "Ara rapor — 1. faz özeti",
    "Entegrasyon POC ortamı kurulumu",
    "Kullanıcı kabul testi senaryoları",
    "Yürütme kurulu sunumu ve geri bildirim",
    "Hedef süreç modeli (TO-BE) taslağı",
    "Dijital imza / e-imza entegrasyon analizi",
    "Kampüs içi iletişim kampanyası planı",
    "Bütçe ve satın alma kalemleri netleştirme",
    "Veri kalitesi izleme panosu",
    "Yedekleme ve felaket kurtarma planı taslağı",
    "API güvenlik incelemesi (pentest öncesi)",
    "Kapanış dokümanı ve öğrenilen dersler",
]


def find_tenant(name_query: str | None, tenant_id: int | None) -> Tenant | None:
    if tenant_id is not None:
        return Tenant.query.filter_by(id=tenant_id, is_active=True).first()
    q = (name_query or "").strip()
    if q:
        return Tenant.query.filter(Tenant.name.ilike(f"%{q}%")).first()
    return (
        Tenant.query.filter(
            or_(
                Tenant.name.ilike("%boğaziçi%"),
                Tenant.name.ilike("%bogazici%"),
                Tenant.short_name.ilike("%boun%"),
            )
        ).first()
    )


def pick_leader_and_members(users: list[CoreUser]) -> tuple[CoreUser, list[CoreUser]]:
    if len(users) < 6:
        raise RuntimeError(
            f"Bu kurumda en az 6 aktif kullanıcı gerekli (1 lider + 5 üye). Şu an: {len(users)}."
        )
    leader = next(
        (u for u in users if u.role and (u.role.name or "").strip().lower() == "tenant_admin"),
        users[0],
    )
    others = [u for u in users if u.id != leader.id]
    members = others[:5]
    return leader, members


def remove_existing_demo(tenant_id: int) -> None:
    p = Project.query.filter_by(name=PROJECT_NAME, kurum_id=tenant_id).first()
    if not p:
        return
    pid = p.id
    Task.query.filter_by(project_id=pid).delete(synchronize_session=False)
    db.session.execute(delete(project_members).where(project_members.c.project_id == pid))
    db.session.execute(delete(project_observers).where(project_observers.c.project_id == pid))
    db.session.execute(delete(project_leaders).where(project_leaders.c.project_id == pid))
    db.session.delete(p)
    db.session.commit()


def seed(tenant: Tenant, replace: bool, dry_run: bool) -> None:
    tid = tenant.id
    print(f"Kurum: id={tid} | {tenant.name!r}")

    users = (
        CoreUser.query.options(joinedload(CoreUser.role))
        .filter(CoreUser.tenant_id == tid, CoreUser.is_active.is_(True))
        .order_by(CoreUser.id)
        .all()
    )

    try:
        leader, members = pick_leader_and_members(users)
    except RuntimeError as e:
        print(f"Hata: {e}")
        sys.exit(3)

    member_ids = [m.id for m in members]
    print(f"Proje lideri: id={leader.id} email={leader.email!r}")
    print("Proje üyeleri (5): " + ", ".join(f"id={m.id}" for m in members))

    existing = Project.query.filter_by(name=PROJECT_NAME, kurum_id=tid).first()
    if existing and not replace:
        print(
            "Çıkılıyor: Bu isimde demo proje zaten var. Yeniden oluşturmak için --replace kullanın.\n"
            f"  project_id={existing.id}"
        )
        sys.exit(1)

    if dry_run:
        print("[dry-run] Veri yazılmadı.")
        print(f"  Oluşturulacak görev sayısı: {len(TASK_TITLES)} (12 tamamlanmış, 8 açık/devam)")
        return

    if existing and replace:
        remove_existing_demo(tid)
        print(f"Önceki demo proje silindi (kurum_id={tid}).")

    today = date.today()
    project = Project(
        name=PROJECT_NAME,
        description=PROJECT_DESC,
        kurum_id=tid,
        manager_id=leader.id,
        start_date=today - timedelta(days=120),
        end_date=today + timedelta(days=200),
        priority="Yüksek",
        is_archived=False,
    )
    db.session.add(project)
    db.session.flush()

    db.session.execute(insert(project_leaders).values(project_id=project.id, user_id=leader.id))

    for uid in member_ids:
        db.session.execute(insert(project_members).values(project_id=project.id, user_id=uid))

    team_cycle = [leader.id] + member_ids
    base_done = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)

    for i, title in enumerate(TASK_TITLES):
        assignee_id = team_cycle[i % len(team_cycle)]
        if i < 12:
            status = "Tamamlandı"
            completed = base_done - timedelta(days=(20 - i) * 3)
            progress = 100
            due = (today - timedelta(days=(18 - i) * 2)) if i < 12 else None
        elif i < 16:
            status = "Devam Ediyor"
            completed = None
            progress = 20 + (i - 12) * 15
            due = today + timedelta(days=14 + (i - 12) * 7)
        else:
            status = "Yapılacak"
            completed = None
            progress = 0
            due = today + timedelta(days=30 + (i - 16) * 5)

        t = Task(
            project_id=project.id,
            title=title[:200],
            description=None,
            reporter_id=leader.id,
            assignee_id=assignee_id,
            status=status,
            priority="Medium",
            progress=progress,
            completed_at=completed,
            due_date=due,
            start_date=(today - timedelta(days=40 + i)) if i < 12 else (today - timedelta(days=5 + i)),
        )
        db.session.add(t)

    db.session.commit()
    print(f"Tamamlandı: project_id={project.id} | 5 üye | {len(TASK_TITLES)} görev (12 tamamlandı).")


def main() -> None:
    parser = argparse.ArgumentParser(description="BOUN örnek proje + görev tohumu")
    parser.add_argument("--tenant-id", type=int, default=None)
    parser.add_argument("--tenant-name", type=str, default=None, help="Tenant adında arama (içerir)")
    parser.add_argument("--replace", action="store_true", help="Aynı isimli demo projeyi silip yeniden oluştur")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        tenant = find_tenant(args.tenant_name, args.tenant_id)
        if not tenant:
            print(
                "Hata: Kurum bulunamadı. --tenant-id veya --tenant-name ile deneyin.\n"
                "Örnek: py scripts/seed_boun_sample_project.py --tenant-id 7"
            )
            sys.exit(2)
        seed(tenant, replace=args.replace, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
