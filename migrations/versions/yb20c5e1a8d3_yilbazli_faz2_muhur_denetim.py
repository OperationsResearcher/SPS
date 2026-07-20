"""Yıl bazlı Faz 2 — mühür denetim tablosu (K9/S13/T1)

DAYANAK: docs/yilbazli/UYGULAMA-PLANI.md §3 · SORULAR.md K7-K9, S13, T1

DENETİM SONUCU (HASAR-TESPITI-2.md §13):
    K7 — Yıl kapatma        : ⚠ var ama sadece status string'i yazıyor
    K8 — Kapalı yıl korumalı: ❌ YOK — 12 yazma yolunda hiç kontrol yok
    K9 — Üst yönetim açabilir: ❌ YOK — `status="active"` atayan tek route yok;
                                geri dönüş SADECE DB müdahalesiyle mümkündü

    En kötü kombinasyon: sistem mührü hem uygulamıyor, hem de yanlışlıkla
    kapatılan yılı kurtarma yolu bırakmıyordu.

BU MIGRATION: plan_year_seal_audits tablosu.

  S13 — "Açma işlemi loglanacak mı — kim, ne zaman, NEDEN?"
        Karar: gerekçe alanı ZORUNLU + denetim tablosu.
  T1  — Gecikmeli veri için tolerans yok; tek yol mührü açmak. Bu yüzden
        açma işlemi izlenebilir olmalı, yoksa mühür anlamını yitirir.

TASARIM NOTLARI:
  - `action` = 'close' | 'reopen'. İkisi de kaydedilir; yalnız açmayı kaydetmek
    "ne zaman kapandı" sorusunu cevapsız bırakırdı.
  - `reason` NOT NULL: gerekçesiz açma yok (S13). Kapatmada da istenir —
    boş string yerine anlamlı metin beklenir, doğrulama route katmanında.
  - `actor_id` ondelete=SET NULL: kullanıcı silinse bile denetim izi kalır.
    Kim olduğu kaybolur ama olayın kendisi kaybolmaz.
  - `plan_year_id` ondelete=CASCADE: plan yılı silinirse izi de gider —
    tutarlılık için (yetim denetim kaydı anlamsız).

Revision ID: yb20c5e1a8d3
Revises: yb16b3d8f4a2
Create Date: 2026-07-20
"""
from alembic import op
import sqlalchemy as sa


revision = "yb20c5e1a8d3"
down_revision = "yb16b3d8f4a2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "plan_year_seal_audits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "plan_year_id", sa.Integer(),
            sa.ForeignKey("plan_years.id", ondelete="CASCADE"),
            nullable=False, index=True,
        ),
        sa.Column("tenant_id", sa.Integer(), nullable=False, index=True),
        # 'close' | 'reopen'
        sa.Column("action", sa.String(20), nullable=False),
        # S13: gerekçe zorunlu
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column(
            "actor_id", sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True, index=True,
        ),
        sa.Column("actor_label", sa.String(200), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(),
            nullable=False, server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_plan_year_seal_audits_py_created",
        "plan_year_seal_audits",
        ["plan_year_id", "created_at"],
    )


def downgrade():
    op.drop_index(
        "ix_plan_year_seal_audits_py_created",
        table_name="plan_year_seal_audits",
    )
    op.drop_table("plan_year_seal_audits")
