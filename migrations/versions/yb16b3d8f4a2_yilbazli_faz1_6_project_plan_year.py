"""Yıl bazlı Faz 1.6 — portföy Project/Task yıl bazlı (T10 tersine / K16)

DAYANAK: docs/yilbazli/UYGULAMA-PLANI.md §2.6 · SORULAR.md S3, T10
         + kullanıcı kararı K16 (2026-07-20)

T10 "iki proje sistemi birleşsin, PlanProject ana model olsun" diyordu.
Ölçüm (2026-07-20) bu yönün maliyetini plandakinden çok farklı gösterdi:

    portföy Project/Task           SP PlanProject
    ────────────────────────       ──────────────────
    veri : 1 proje, 0 görev        21 proje, 63 görev
    kod  : 2719 satır, 25 route,   6 route
           20 dosya, 10 şablon
           (gantt/kanban/RAID/
            kapasite/takvim)
    alan : Project +9, Task +16 alan PlanProject'te YOK
           (health_score, priority, manager_id, notification_settings,
            process_kpi_id, estimated_time, reminder_date, parent_id...)

    Yani "veri taşıma pratikte yok" doğruydu, ama iş veri değil KOD işiydi:
    2719 satırlık modülü ve 10 ekranı yeniden bağlamak + 25 alanı taşımak.

  K16 — YÖN TERSİNE ÇEVRİLDİ. Portföy `Project` ana model olur; ona
        plan_year_id + source_project_id eklenir ve full-clone'a dahil edilir.
        plan_projects verisi (21 kayıt) oraya taşınır.
        Gerekçe: 2719 satırlık modül ve 10 şablon olduğu gibi çalışmaya devam
        eder; yıl bazlılık hedefi (K5) yine karşılanır. Yazılacak tek yeni şey
        yıl devri bloğu.

TASK YIL BAĞI:
    task -> project_id -> project.plan_year_id zinciriyle çözülür. Task'a ayrı
    plan_year_id EKLENMEZ: proje bir yıla aitse görevleri de o yıla aittir,
    ikinci kolon iki kaynak yaratır (T9'un kaçındığı durum).

NOT — 2026-06-04 hotfix'i (0bb0ad64):
    O commit `Project(...)` constructor'ından plan_year_id'yi kaldırmıştı,
    çünkü model/DB'de kolon YOKTU (TypeError -> 500). Bu migration kolonu
    gerçekten açıyor; hotfix'in gerekçesi ortadan kalkıyor.

Revision ID: yb16b3d8f4a2
Revises: yb14a7c2e9f1
Create Date: 2026-07-20
"""
from alembic import op
import sqlalchemy as sa


revision = "yb16b3d8f4a2"
down_revision = "yb14a7c2e9f1"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "project",
        sa.Column("plan_year_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_project_plan_year_id", "project", "plan_years",
        ["plan_year_id"], ["id"], ondelete="CASCADE",
    )
    op.create_index("ix_project_plan_year_id", "project", ["plan_year_id"])

    # Yıl devri zinciri (clone_full_plan_year bunu kullanacak)
    op.add_column(
        "project",
        sa.Column("source_project_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_project_source_project_id", "project", "project",
        ["source_project_id"], ["id"], ondelete="SET NULL",
    )

    # Mevcut projeleri tenant'ın AKTİF plan yılına bağla; aktif yoksa en yeni.
    # (Ölçüm: portföyde tek kayıt var — tenant 1, "Ar-Ge Stratejileri" 2026-03.)
    op.execute("""
        UPDATE project p
           SET plan_year_id = (
               SELECT py.id FROM plan_years py
                WHERE py.tenant_id = p.tenant_id
                ORDER BY (py.status = 'active') DESC, py.year DESC
                LIMIT 1
           )
         WHERE p.plan_year_id IS NULL
    """)


def downgrade():
    op.drop_constraint("fk_project_source_project_id", "project", type_="foreignkey")
    op.drop_column("project", "source_project_id")
    op.drop_index("ix_project_plan_year_id", table_name="project")
    op.drop_constraint("fk_project_plan_year_id", "project", type_="foreignkey")
    op.drop_column("project", "plan_year_id")
