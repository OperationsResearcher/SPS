"""period_type normalize + orphan user_id NULL + FK validate (TASK-253)

TEK KÖK NEDEN, ÜÇ SEMPTOM. 2026-03-26'da tek seferde yüklenen 202 kayıt
("Kayseri Model Fabrika", 10 silinmiş kullanıcıya ait) şunlara yol açtı:

  1. period_type='Aylık' → 'aylik' (365.925) ile ayrı kova; GROUP BY bölünüyor
  2. user_id users'ta yok → kpi_data_user_id_fkey 'validated' işaretli AMA
     veri ihlal ediyor (constraint doğrulanmadan eklenmiş)
  3. (2) yüzünden TASK-252 backfill'i bu 202 satırı ATLADI → *_numeric NULL

Bu migration üçünü birlikte çözer (kullanıcı onayı 2026-07-15: "user_id'yi
NULL'a çek + normalize" — veri KORUNUR, yalnız 'kim girdi' referansı düşer;
o bilgi zaten kayıp, kullanıcılar silinmiş).

Sıra kritik: FK gevşetilmeden UPDATE atılamaz (satır yeniden yazılınca
Postgres FK'yı o anda kontrol eder ve ForeignKeyViolation fırlatır).

Revision ID: e9669efe440c
Revises: f0aa4591b689
Create Date: 2026-07-15 12:37:49.321796

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9669efe440c'
down_revision = 'f0aa4591b689'
branch_labels = None
depends_on = None

# app/constants/periods.py::_ESLEME ile AYNI kural olmalı.
# Buradaki liste değişirse orayı da güncelle (tek kaynak orası; bu, tarihsel
# veriyi bir kereye mahsus hizalayan SQL karşılığı).
_NORMALIZE = """
UPDATE kpi_data SET period_type = CASE lower(btrim(period_type))
    WHEN 'günlük'    THEN 'gunluk'
    WHEN 'haftalık'  THEN 'haftalik'
    WHEN 'aylık'     THEN 'aylik'
    WHEN 'çeyrek'    THEN 'ceyrek'
    WHEN 'çeyreklik' THEN 'ceyrek'
    WHEN 'ceyreklik' THEN 'ceyrek'
    WHEN 'yıllık'    THEN 'yillik'
    ELSE lower(btrim(period_type))
END
WHERE period_type IS NOT NULL
  AND period_type <> CASE lower(btrim(period_type))
    WHEN 'günlük'    THEN 'gunluk'
    WHEN 'haftalık'  THEN 'haftalik'
    WHEN 'aylık'     THEN 'aylik'
    WHEN 'çeyrek'    THEN 'ceyrek'
    WHEN 'çeyreklik' THEN 'ceyrek'
    WHEN 'ceyreklik' THEN 'ceyrek'
    WHEN 'yıllık'    THEN 'yillik'
    ELSE lower(btrim(period_type))
  END
"""

# TASK-252'deki backfill ile AYNI kural — orada orphan'lar atlanmıştı,
# şimdi FK düzeldiği için onlar da doldurulabiliyor.
_BACKFILL = """
UPDATE kpi_data
SET {hedef} = CASE
    WHEN replace(btrim({kaynak}), ',', '.') ~ '^-?[0-9]+(\\.[0-9]+)?$'
    THEN replace(btrim({kaynak}), ',', '.')::numeric
    ELSE NULL
END
WHERE {kaynak} IS NOT NULL AND btrim({kaynak}) <> '' AND {hedef} IS NULL
"""


def upgrade():
    bind = op.get_bind()
    pg = bind.dialect.name == 'postgresql'

    # 1) user_id: NOT NULL → nullable + ondelete SET NULL
    #    Kullanıcı silinince ÖLÇÜM kaybolmamalı, yalnız "kim girdi" düşmeli.
    #    Okuyan kod None'a hazır: _user_display_name(None) → "—" (doğrulandı).
    with op.batch_alter_table('kpi_data') as batch:
        batch.alter_column('user_id', existing_type=sa.Integer(), nullable=True)

    if pg:
        # SIRA KRİTİK: FK'yi ÖNCE tamamen kaldır. `create_foreign_key` yeni
        # constraint'i anında doğrular; orphan'lar dururken kurmaya çalışmak
        # ForeignKeyViolation verir (ilk denemede bu oldu). Doğru sıra:
        # kaldır → temizle → yeniden kur (artık doğrulama geçer).
        #
        # ADI VARSAYMA: FK adı ortamdan ortama değişir, hatta hiç olmayabilir.
        # Test'te `kpi_data.user_id` üzerinde FK YOKTU → sabit ada yazılmış
        # drop_constraint UndefinedObject ile patladı (2026-07-15, yerelde
        # geçmişti). Adı pg_catalog'dan oku; yoksa bu adımı atla.
        mevcut_fk = bind.execute(sa.text(
            "SELECT conname FROM pg_constraint "
            "WHERE conrelid = 'kpi_data'::regclass AND contype = 'f' "
            "  AND conkey = ARRAY[(SELECT attnum FROM pg_attribute "
            "                      WHERE attrelid = 'kpi_data'::regclass "
            "                        AND attname = 'user_id')]"
        )).scalar()
        if mevcut_fk:
            op.drop_constraint(mevcut_fk, 'kpi_data', type_='foreignkey')
        else:
            print("[TASK-253] kpi_data.user_id uzerinde FK yok — drop atlandi")

        # 2) Orphan temizliği — FK yokken UPDATE serbest
        orphan = bind.execute(sa.text(
            "UPDATE kpi_data kd SET user_id = NULL "
            "WHERE kd.user_id IS NOT NULL "
            "  AND NOT EXISTS (SELECT 1 FROM users u WHERE u.id = kd.user_id)"
        )).rowcount
        print(f"[TASK-253] {orphan} orphan satirin user_id'si NULL'a cekildi "
              f"(silinmis kullanicilar — olcum korundu)")

        # FK'yi yeniden kur — orphan kalmadigi icin dogrulama gecer
        op.create_foreign_key('kpi_data_user_id_fkey', 'kpi_data', 'users',
                              ['user_id'], ['id'], ondelete='SET NULL')
        # Index: yarida kalmis bir kosudan sonra zaten var olabilir (Test'te oldu)
        bind.execute(sa.text(
            "CREATE INDEX IF NOT EXISTS ix_kpi_data_user_id ON kpi_data (user_id)"
        ))

        # 3) period_type normalize
        norm = bind.execute(sa.text(_NORMALIZE)).rowcount
        print(f"[TASK-253] {norm} satirin period_type'i kanonik bicime cevrildi")

        # 4) TASK-252 backfill'inin atladigi satirlari tamamla
        for kaynak, hedef in (('actual_value', 'actual_numeric'),
                              ('target_value', 'target_numeric')):
            n = bind.execute(sa.text(_BACKFILL.format(kaynak=kaynak, hedef=hedef))).rowcount
            print(f"[TASK-253] {kaynak}: {n} satirin sayisal aynasi tamamlandi")

        # 5) FK gerçekten geçerli mi? (Eskisi 'validated' işaretliydi ama veri
        #    ihlal ediyordu — bu kez orphan'lar temizlendikten SONRA kuruldu,
        #    yani doğrulama gerçek. Yine de teyit et, sessiz kabul yok.)
        gecerli = bind.execute(sa.text(
            "SELECT convalidated FROM pg_constraint "
            "WHERE conrelid = 'kpi_data'::regclass AND conname = 'kpi_data_user_id_fkey'"
        )).scalar()
        kalan = bind.execute(sa.text(
            "SELECT count(*) FROM kpi_data kd WHERE kd.user_id IS NOT NULL "
            "AND NOT EXISTS (SELECT 1 FROM users u WHERE u.id = kd.user_id)"
        )).scalar()
        print(f"[TASK-253] FK validated={gecerli} | kalan orphan={kalan} "
              f"(ikisi de dogru olmali: True / 0)")


def downgrade():
    # user_id'yi NOT NULL'a döndürmek MÜMKÜN DEĞİL: NULL'a çekilen 202 satırın
    # eski user_id'si geri getirilemez (kullanıcılar zaten silinmiş). Şema
    # gevşetilmiş kalır — veri kaybı yok, yalnız kısıt esnek.
    if op.get_bind().dialect.name == 'postgresql':
        op.drop_index('ix_kpi_data_user_id', table_name='kpi_data')
    print("[TASK-253] downgrade: user_id nullable BIRAKILDI "
          "(NULL'a cekilen satirlar geri getirilemez)")
