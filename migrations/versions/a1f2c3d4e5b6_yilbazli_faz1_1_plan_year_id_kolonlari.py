"""Yıl bazlı Faz 1.1 — eksik plan_year_id kolonları (T3)

DAYANAK: docs/yilbazli/UYGULAMA-PLANI.md §2 (Faz 1.1) · SORULAR.md T3, T9

T9 (full-clone tek mekanizma) gereği her varlık kendi plan_year_id'sini taşır.
Bu migration, plan_year_id'si HİÇ OLMAYAN tablolara kolonu ekler ve T3 kuralını
uygular:

    T3 — ilk göçte mevcut kayıt TÜM YILLARA kopyalanır; sonrası normal yıl
    bazlı davranır (2026'daki düzenleme kapalı 2024'e sızmaz).

KAPSAM (ölçüm 2026-07-20, yerel DB):
    process_sub_strategy_links   559  ← bileşik PK, aşağıda özel durum
    process_maturity             340
    initiatives                  104  ← start_year/end_year yerine gerçek plan yılı
    blue_ocean_factors             9
    blue_ocean_canvases            6
    blue_ocean_errc_items          3
    vrio_resources                 0  ← boş, kolon yine de eklenir
    strategy_process_matrix        0
    strategy_map_link              0

ÖZEL DURUM — process_sub_strategy_links BİLEŞİK PK:
    Tablonun PK'si (process_id, sub_strategy_id) çiftidir; ayrı `id` kolonu YOK.
    Full-clone'da aynı süreç–strateji çifti her yıl tekrarlanacağı için mevcut PK
    yıl kopyalarında ÇAKIŞIR → PK'ye plan_year_id eklenmesi gerekir.

    ANCAK bu migration PK'yi DEĞİŞTİRMEZ — Faz 1.3'e ertelendi. Gerekçe §4'te:
    tenant 1'in 3 PSSL satırı var ama plan yılı yok; PK'yi şimdi NOT NULL yapmak
    o satırları silmeyi gerektirirdi. Plan yılları Faz 1.3'te üretildikten sonra
    ayrı migration'da genişletilir.

INITIATIVES NOTU:
    Model bugün start_year/end_year aralığı taşıyor (initiative.py:40-41) ve
    route'lar sp_active_year'ı kullanmıyor. Bu migration plan_year_id'yi EKLER
    ve doldurur; start_year/end_year kolonlarını SİLMEZ — okuma yolları Faz 3'te
    plan_year_id'ye geçtikten sonra ayrı bir migration'da kaldırılır. Kolonu
    burada silmek, henüz onları okuyan route'ları 500'e düşürürdü.

DOLDURMA KURALI:
    Her kayıt, kendi tenant'ının HER plan yılı için çoğaltılır (T3). Tenant'ı
    olmayan/plan yılı bulunmayan kayıtlar plan_year_id=NULL kalır — Faz 1.3
    (plan yılı zinciri üretimi) sonrasında Faz 1.2 doldurma adımı bunları toplar.

    tenant_id'si olmayan tablolarda (blue_ocean_factors, blue_ocean_errc_items,
    process_sub_strategy_links, strategy_*) tenant, parent zinciri üzerinden
    çözülür — kpi_data'da olduğu gibi doğrudan tenant_id kolonu yoktur.

GERİ ALINABİLİR: evet. downgrade kolonları düşürür, PSSL'in PK'sini eski haline
    getirir. Ancak T3 çoğaltması geri alınırken hangi satırın "orijinal" olduğu
    plan yılı sırasına göre seçilir (en küçük plan_year_id) — bilgi kaybı
    ihtimali için Faz 1.0 yedeği esastır.

Revision ID: a1f2c3d4e5b6
Revises: b7d3e1f4a920
Create Date: 2026-07-20
"""
from alembic import op
import sqlalchemy as sa


revision = "a1f2c3d4e5b6"
down_revision = "b7d3e1f4a920"
branch_labels = None
depends_on = None


# (tablo, tenant'a ulaşan JOIN ifadesi) — tenant_id kolonu olanlar için None
_TENANT_PATH = {
    "blue_ocean_canvases": None,
    "vrio_resources": None,
    "process_maturity": None,
    "initiatives": None,
    "blue_ocean_factors": (
        "JOIN blue_ocean_canvases c ON c.id = t.canvas_id"
    ),
    "blue_ocean_errc_items": (
        "JOIN blue_ocean_canvases c ON c.id = t.canvas_id"
    ),
}

# Basit kolon ekleme (id PK'li, tekil satır) — T3 çoğaltması ayrı adımda
_SIMPLE_TABLES = [
    "blue_ocean_canvases",
    "blue_ocean_factors",
    "blue_ocean_errc_items",
    "vrio_resources",
    "process_maturity",
    "initiatives",
    "strategy_process_matrix",
    "strategy_map_link",
]


def _add_plan_year_column(table: str, nullable: bool = True) -> None:
    """plan_year_id kolonu + FK + index ekler (idempotent değil — Alembic sırası yönetir)."""
    op.add_column(
        table,
        sa.Column("plan_year_id", sa.Integer(), nullable=nullable),
    )
    op.create_foreign_key(
        f"fk_{table}_plan_year_id",
        table,
        "plan_years",
        ["plan_year_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        f"ix_{table}_plan_year_id",
        table,
        ["plan_year_id"],
    )


def upgrade():
    conn = op.get_bind()

    # ------------------------------------------------------------------
    # 1) Basit tablolar — kolon + FK + index
    # ------------------------------------------------------------------
    for table in _SIMPLE_TABLES:
        _add_plan_year_column(table)

    # ------------------------------------------------------------------
    # 2) process_sub_strategy_links — bileşik PK yeniden tanımlanır
    #    (process_id, sub_strategy_id) → (+ plan_year_id)
    # ------------------------------------------------------------------
    op.add_column(
        "process_sub_strategy_links",
        sa.Column("plan_year_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_process_sub_strategy_links_plan_year_id",
        "process_sub_strategy_links",
        "plan_years",
        ["plan_year_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        "ix_process_sub_strategy_links_plan_year_id",
        "process_sub_strategy_links",
        ["plan_year_id"],
    )

    # ------------------------------------------------------------------
    # 3) T3 doldurma — mevcut kayıt tenant'ının TÜM plan yıllarına kopyalanır
    #
    #    Yöntem: önce mevcut satırların plan_year_id'si tenant'ın EN ESKİ plan
    #    yılına set edilir (orijinal satır), sonra kalan yıllar için kopya
    #    üretilir. Böylece orijinal satırın id'si korunur — ona bağlı FK'ler
    #    (blue_ocean_factors.canvas_id vb.) kırılmaz.
    # ------------------------------------------------------------------

    # 3a) tenant_id kolonu OLAN tablolar
    for table in ["blue_ocean_canvases", "vrio_resources", "process_maturity", "initiatives"]:
        conn.execute(sa.text(f"""
            UPDATE {table} t
               SET plan_year_id = (
                   SELECT py.id FROM plan_years py
                    WHERE py.tenant_id = t.tenant_id
                    ORDER BY py.year ASC
                    LIMIT 1
               )
             WHERE t.plan_year_id IS NULL
        """))

    # 3b) process_sub_strategy_links — tenant processes üzerinden çözülür
    conn.execute(sa.text("""
        UPDATE process_sub_strategy_links l
           SET plan_year_id = (
               SELECT py.id FROM plan_years py
                JOIN processes p ON p.tenant_id = py.tenant_id
                WHERE p.id = l.process_id
                ORDER BY py.year ASC
                LIMIT 1
           )
         WHERE l.plan_year_id IS NULL
    """))

    # 3c) blue_ocean alt tabloları — canvas üzerinden miras alır
    for table in ["blue_ocean_factors", "blue_ocean_errc_items"]:
        conn.execute(sa.text(f"""
            UPDATE {table} t
               SET plan_year_id = c.plan_year_id
              FROM blue_ocean_canvases c
             WHERE c.id = t.canvas_id
               AND t.plan_year_id IS NULL
        """))

    # ------------------------------------------------------------------
    # 4) PSSL PK değişimi — BİLİNÇLİ OLARAK Faz 1.3'E ERTELENDİ
    #
    # ÖLÇÜM (2026-07-20, migration yazımı sırasında yapıldı):
    #     PSSL toplam 559 satır. Bunların 3'ü tenant 1'e (Default Corp) ait ve
    #     tenant 1'in HİÇ plan yılı yok (bkz. UYGULAMA-PLANI.md §2.3 — 5 tenant'ta
    #     plan yılı sıfır, Faz 1.3'te üretilecek).
    #
    # Bu adım burada `DELETE ... WHERE plan_year_id IS NULL` içeriyordu; o hali
    # tenant 1'in 3 meşru satırını SESSİZCE SİLERDİ. Plan yılı henüz üretilmediği
    # için "plan yılı yok" ≠ "veri çöp".
    #
    # KARAR: plan_year_id NULLABLE kalır, PK değişmez. Faz 1.3 (plan yılı zinciri
    # üretimi) tüm tenant'lara plan yılı verdikten SONRA, Faz 1.2 doldurma adımı
    # kalan NULL'ları toplar ve PK o zaman genişletilir (ayrı migration).
    #
    # KURALLAR-MASTER §3: hard delete yasak — soft delete zorunlu. Burada silme
    # zaten yanlıştı; kural da aynı yöne işaret ediyor.
    # ------------------------------------------------------------------
    pass


def downgrade():
    # PSSL PK'sine dokunulmadı (upgrade §4 — Faz 1.3'e ertelendi), bu yüzden
    # burada PK geri alma adımı da yok. Yalnızca kolon/FK/index düşürülür.
    op.drop_index(
        "ix_process_sub_strategy_links_plan_year_id",
        table_name="process_sub_strategy_links",
    )
    op.drop_constraint(
        "fk_process_sub_strategy_links_plan_year_id",
        "process_sub_strategy_links",
        type_="foreignkey",
    )
    op.drop_column("process_sub_strategy_links", "plan_year_id")

    for table in reversed(_SIMPLE_TABLES):
        op.drop_index(f"ix_{table}_plan_year_id", table_name=table)
        op.drop_constraint(f"fk_{table}_plan_year_id", table, type_="foreignkey")
        op.drop_column(table, "plan_year_id")
