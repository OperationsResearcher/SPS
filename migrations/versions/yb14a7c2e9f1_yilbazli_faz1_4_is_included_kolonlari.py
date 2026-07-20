"""Yıl bazlı Faz 1.4 — varlıklara is_included kolonu (T9/K15)

DAYANAK: docs/yilbazli/UYGULAMA-PLANI.md §2.4 · SORULAR.md T9
         + kullanıcı kararı K15 (2026-07-20)

T9 override tablolarını (*_year_configs) kaldırıyor. Ölçüm (2026-07-20) o
tabloların neredeyse tamamen artık veri olduğunu gösterdi:

    tablo                          toplam   gerçek değer taşıyan
    kpi_year_configs                 1114        59
    sub_strategy_year_configs         475        10
    process_year_configs              355        10
    strategy_year_configs             190        10
    individual_kpi_year_configs       525         0
    ─────────────────────────────────────────────────
                                     2659        89

"Gerçek değer" = config'in alanı, bağlı olduğu varlığınkinden FARKLI.
Kalan 2570 satır varlığıyla birebir aynı — hiçbir bilgi taşımıyor.

ANCAK — is_included KAYBOLURSA GERİ GELMEZ:
    18 config `is_included = FALSE` taşıyor ve hepsi KMF'nin (#16) gerçek
    verisi; PG'leri `is_active = TRUE`. Anlamı: "bu gösterge aktif ama şu yıl
    karneye dahil değil."

    Varlıkta bunun karşılığı YOK. `is_active` farklı bir şey ifade ediyor
    (kayıt silinmiş mi?). Dolayısıyla override tablosu kaldırılmadan önce bu
    bilgiye varlıkta bir yer açılmalı.

  K15 — Varlıklara `is_included` kolonu eklenir (varsayılan TRUE).
        Böylece 89 gerçek değer + 18 dahil-etme bilgisi varlık kopyalarına
        taşınabilir ve override tabloları bilgi kaybı olmadan kaldırılabilir.

KAPSAM:
    process_kpis     <- kpi_year_configs.is_included
    processes        <- process_year_configs.is_included
    strategies       <- strategy_year_configs.is_included
    sub_strategies   <- sub_strategy_year_configs.is_included
    individual_performance_indicators <- individual_kpi_year_configs.is_included

    Full-clone (T9) sayesinde her varlık zaten yıl başına ayrı satır; bu yüzden
    kolon doğrudan "o yıl karneye dahil mi" sorusunu cevaplar — ayrı override
    tablosuna gerek kalmaz.

NOT: Bu migration yalnızca KOLONU açar. Veri taşıma ve override tablolarının
    düşürülmesi ayrı adımda (scripts/ops/yilbazli_faz1_4_override_goc.py) —
    böylece taşıma doğrulanmadan tablolar silinmez.

Revision ID: yb14a7c2e9f1
Revises: a1f2c3d4e5b6
Create Date: 2026-07-20
"""
from alembic import op
import sqlalchemy as sa


revision = "yb14a7c2e9f1"
down_revision = "a1f2c3d4e5b6"
branch_labels = None
depends_on = None


_TABLOLAR = [
    "process_kpis",
    "processes",
    "strategies",
    "sub_strategies",
    "individual_performance_indicators",
]


def upgrade():
    for tablo in _TABLOLAR:
        op.add_column(
            tablo,
            sa.Column(
                "is_included",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
        )


def downgrade():
    for tablo in reversed(_TABLOLAR):
        op.drop_column(tablo, "is_included")
