# -*- coding: utf-8 -*-
"""Legacy tablolarda kurum_id -> tenant_id (tenants.id FK) gecisi — Faz 1

Revision ID: k9l8m766p001
Revises: f1a2b3c4d5f7
Create Date: 2026-03-26

Varsayim: Kurum satirlariyla tenants satirlari ayni sayisal id ile eslesir
(mevcut app User.kurum_id property yorumuyla uyumlu).

- project: kolon zaten tenants.id ise kurum_id -> tenant_id yeniden adlandirilir.
- Diger tablolar: tenant_id eklenir, doldurulur, kurum_id kaldirilir, FK tenants olur.
- Kurum: tenant_id ile tenants baglanir (kurum.id ile hizali tenant satiri varsayimi).
- Legacy `user` tablosu varsa ayni islem (yoksa atlanir).

Downgrade: gelistirme icin kismi; uretimde downgrade onerilmez.
"""
from alembic import op
import sqlalchemy as sa


revision = "k9l8m766p001"
down_revision = "f1a2b3c4d5f7"
branch_labels = None
depends_on = None


def _table_cols(bind, table: str):
    insp = sa.inspect(bind)
    if not insp.has_table(table):
        return None
    return {c["name"] for c in insp.get_columns(table)}


def _drop_fk_to_kurum(bind, table: str):
    insp = sa.inspect(bind)
    for fk in insp.get_foreign_keys(table):
        if fk.get("referred_table") != "kurum":
            continue
        if "kurum_id" not in fk.get("constrained_columns", []):
            continue
        name = fk.get("name")
        if name:
            op.drop_constraint(name, table, type_="foreignkey")


def _ensure_tenant_column_swap(bind, table: str, with_unique_kurum_code: bool = False):
    cols = _table_cols(bind, table)
    if cols is None or "tenant_id" in cols:
        return
    if "kurum_id" not in cols:
        return

    if with_unique_kurum_code:
        insp = sa.inspect(bind)
        for uk in insp.get_unique_constraints(table):
            ucols = set(uk.get("column_names") or ())
            if ucols == {"kurum_id", "code"}:
                name = uk.get("name")
                if name:
                    op.drop_constraint(name, table, type_="unique")
                break

    _drop_fk_to_kurum(bind, table)
    op.add_column(table, sa.Column("tenant_id", sa.Integer(), nullable=True))
    op.execute(
        sa.text(
            f"""
            UPDATE {table} t
            SET tenant_id = t.kurum_id
            WHERE EXISTS (SELECT 1 FROM tenants tn WHERE tn.id = t.kurum_id)
            """
        )
    )
    orphan = bind.execute(
        sa.text(f"SELECT COUNT(*) FROM {table} WHERE tenant_id IS NULL")
    ).scalar()
    if orphan and int(orphan) > 0:
        raise RuntimeError(
            f"{table}: {orphan} satir icin tenants.id = kurum_id eslemesi yok. "
            "Veriyi duzeltmeden migrasyon durduruldu."
        )

    op.drop_column(table, "kurum_id")
    op.create_foreign_key(
        f"fk_{table}_tenant_id_tenants",
        table,
        "tenants",
        ["tenant_id"],
        ["id"],
    )
    op.alter_column(
        table,
        "tenant_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    idx = f"ix_{table}_tenant_id"
    insp = sa.inspect(bind)
    existing_ix = {i["name"] for i in insp.get_indexes(table)}
    if idx not in existing_ix:
        op.create_index(idx, table, ["tenant_id"], unique=False)

    if with_unique_kurum_code:
        op.create_unique_constraint(
            "uq_ana_strateji_tenant_code",
            table,
            ["tenant_id", "code"],
        )

    old_ix = f"ix_{table}_kurum_id"
    insp2 = sa.inspect(bind)
    if old_ix in {i["name"] for i in insp2.get_indexes(table)}:
        try:
            op.drop_index(old_ix, table_name=table)
        except Exception:
            pass


def _project_rename_kurum_to_tenant(bind):
    cols = _table_cols(bind, "project")
    if cols is None:
        return
    if "tenant_id" in cols:
        return
    if "kurum_id" not in cols:
        return

    insp = sa.inspect(bind)
    points_to_tenants = False
    for fk in insp.get_foreign_keys("project"):
        if "kurum_id" in fk.get("constrained_columns", []):
            points_to_tenants = fk.get("referred_table") == "tenants"
            break
    if not points_to_tenants:
        _ensure_tenant_column_swap(bind, "project", with_unique_kurum_code=False)
        return

    op.execute(sa.text("ALTER TABLE project RENAME COLUMN kurum_id TO tenant_id"))
    try:
        op.execute(sa.text("ALTER INDEX ix_project_kurum_id RENAME TO ix_project_tenant_id"))
    except Exception:
        op.create_index("ix_project_tenant_id", "project", ["tenant_id"], unique=False)


def _kurum_add_tenant_id(bind):
    cols = _table_cols(bind, "kurum")
    if cols is None or "tenant_id" in cols:
        return
    op.add_column("kurum", sa.Column("tenant_id", sa.Integer(), nullable=True))
    op.execute(
        sa.text(
            """
            UPDATE kurum k
            SET tenant_id = k.id
            WHERE EXISTS (SELECT 1 FROM tenants t WHERE t.id = k.id)
            """
        )
    )
    orphan = bind.execute(
        sa.text("SELECT COUNT(*) FROM kurum WHERE tenant_id IS NULL")
    ).scalar()
    if orphan and int(orphan) > 0:
        raise RuntimeError(
            f"kurum: {orphan} satir icin tenants.id = kurum.id bulunamadi."
        )
    op.create_foreign_key(
        "fk_kurum_tenant_id_tenants",
        "kurum",
        "tenants",
        ["tenant_id"],
        ["id"],
    )
    op.alter_column(
        "kurum",
        "tenant_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.create_unique_constraint("uq_kurum_tenant_id", "kurum", ["tenant_id"])


def upgrade():
    bind = op.get_bind()

    _project_rename_kurum_to_tenant(bind)

    for tbl, uk in (
        ("ana_strateji", True),
        ("analysis_item", False),
        ("surec", False),
        ("deger", False),
        ("etik_kural", False),
        ("kalite_politikasi", False),
        ("corporate_identity", False),
    ):
        _ensure_tenant_column_swap(bind, tbl, with_unique_kurum_code=uk)

    if _table_cols(bind, "user") is not None:
        _ensure_tenant_column_swap(bind, "user", with_unique_kurum_code=False)

    _kurum_add_tenant_id(bind)


def downgrade():
    raise NotImplementedError(
        "k9l8m766p001 geri alma desteklenmiyor; yedekten donun veya yeni migration yazin."
    )
