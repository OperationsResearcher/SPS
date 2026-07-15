"""kpi_data actual_numeric + target_numeric (TASK-252)

366.716 sayısal ölçüm String(100) olarak duruyordu → DB tarafında AVG/percentile
yapılamıyor, her analitik tüm satırı Python'a çekip safe_float'tan geçiriyordu.

Bu migration ham metin kolonları KORUYARAK sayısal ayna ekler:
  - actual_value / target_value    → değişmez (kullanıcı girdisi, serbest format)
  - actual_numeric / target_numeric → safe_float türevi; indirgenemeyende NULL

Backfill SQL'de yapılır (366k satırı Python'a çekmek gereksiz). SQL kuralı
app/utils/numeric.py::safe_float ile birebir aynı olmalı:
    strip() → virgülü noktaya çevir → float() dene → olmuyorsa None

Bilinçli NULL kalanlar (hata DEĞİL, iş kuralı — yerelde ölçüldü):
  '-'            → veri girilmedi (108 satır)
  '90-100'       → aralık hedefi; DH/HKY yöntemleri metinden okur (~168 satır)
  '%100'         → yüzde işaretli (23 satır)
  '₺100.070.853' → para birimi + binlik ayraç

Ölçek Numeric(20,6): ilk denemede (20,4) idi ve doğrulama testi 1 sapma
yakaladı — '0.4444444444444444' → 0.4444'e yuvarlanıp safe_float'tan
sapıyordu. Veri ölçüldü: max değer 381.806.691 (9 tam basamak), 4'ten fazla
ondalık yalnız 1 satırda. (20,6) ile o satırda 4.4e-7 fark kalır — KPI
ölçümünde anlamsız, diğer 366.513 satır birebir.

Revision ID: f0aa4591b689
Revises: da9b27f1a650
Create Date: 2026-07-15 12:15:19.835265

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0aa4591b689'
down_revision = 'da9b27f1a650'
branch_labels = None
depends_on = None

# safe_float'ın SQL karşılığı: virgülü noktaya çevir, salt sayısalsa cast et.
# Regex, float()'ın kabul ettiği kümeyi kapsar. Bilimsel gösterim (1e5) float()
# tarafından kabul edilir ama veride yok (ölçüldü) — kapsam dışı bırakmak
# backfill'i güvenli tarafta tutar (yanlış cast yerine NULL).
# DİKKAT — `AND EXISTS (users)` neden var?
# Bu migration yazılırken keşfedildi: kpi_data'da user_id'si users'ta OLMAYAN
# 202 satır var (hepsi "Kayseri Model Fabrika"; silinmiş kullanıcıların verisi).
# kpi_data_user_id_fkey `validated=True` işaretli ama veri onu ihlal ediyor —
# yani constraint doğrulanmadan eklenmiş. UPDATE satırı yeniden yazdığı için
# Postgres FK'yı O ANDA kontrol ediyor ve ForeignKeyViolation fırlatıyor.
#
# Bu migration'ın işi veri onarımı DEĞİL. Orphan satırlar atlanır, sayıları
# raporlanır (aşağıda) ve ayrı bir task'a bırakılır. Aksi halde backfill
# ilgisiz bir veri sorunu yüzünden hiç çalışamazdı.
_BACKFILL = """
UPDATE kpi_data kd
SET {hedef} = CASE
    WHEN replace(btrim(kd.{kaynak}), ',', '.') ~ '^-?[0-9]+(\\.[0-9]+)?$'
    THEN replace(btrim(kd.{kaynak}), ',', '.')::numeric
    ELSE NULL
END
WHERE kd.{kaynak} IS NOT NULL AND btrim(kd.{kaynak}) <> ''
  AND EXISTS (SELECT 1 FROM users u WHERE u.id = kd.user_id)
"""

_KOLONLAR = (('actual_value', 'actual_numeric'), ('target_value', 'target_numeric'))


def upgrade():
    op.add_column('kpi_data', sa.Column('target_numeric', sa.Numeric(20, 6), nullable=True))
    op.add_column('kpi_data', sa.Column('actual_numeric', sa.Numeric(20, 6), nullable=True))

    bind = op.get_bind()
    if bind.dialect.name != 'postgresql':
        return  # SQLite/test: kolon yeter; veri ORM listener'ı ile türetilir

    for kaynak, hedef in _KOLONLAR:
        bind.execute(sa.text(_BACKFILL.format(kaynak=kaynak, hedef=hedef)))

    # Doğrulama raporu — sessizce geçmek YASAK. Operatör ne olduğunu görmeli.
    orphan = bind.execute(sa.text(
        "SELECT count(*) FROM kpi_data kd "
        "WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id = kd.user_id)"
    )).scalar()

    for kaynak, hedef in _KOLONLAR:
        toplam = bind.execute(sa.text(
            f"SELECT count(*) FROM kpi_data "
            f"WHERE {kaynak} IS NOT NULL AND btrim({kaynak}) <> ''"
        )).scalar()
        # indirgenemeyen = dolu ama numeric NULL, orphan'lar HARİÇ
        indirgenemeyen = bind.execute(sa.text(
            f"SELECT count(*) FROM kpi_data kd "
            f"WHERE kd.{kaynak} IS NOT NULL AND btrim(kd.{kaynak}) <> '' "
            f"  AND kd.{hedef} IS NULL "
            f"  AND EXISTS (SELECT 1 FROM users u WHERE u.id = kd.user_id)"
        )).scalar()
        print(f"[TASK-252] {kaynak}: {toplam} dolu | {indirgenemeyen} sayiya "
              f"indirgenemedi (aralik hedefi / '-' / yuzde / para birimi — beklenen)")

    if orphan:
        print(f"[TASK-252] UYARI: {orphan} satirin user_id'si users'ta YOK "
              f"(FK 'validated' isaretli ama veri ihlal ediyor). Bu satirlar "
              f"backfill DISI birakildi — ayri veri onarim isi gerekiyor.")

    # Analitik index: "tenant X, yil Y ortalamasi" sorgulari bunu kullanir
    op.create_index('ix_kpi_data_actual_numeric', 'kpi_data', ['actual_numeric'])


def downgrade():
    op.drop_index('ix_kpi_data_actual_numeric', table_name='kpi_data')
    op.drop_column('kpi_data', 'actual_numeric')
    op.drop_column('kpi_data', 'target_numeric')
