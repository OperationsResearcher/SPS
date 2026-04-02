"""Hard unify legacy process tables into canonical names.

Revision ID: r7s8t9u0v001
Revises: q1w2e3r4t005
Create Date: 2026-03-26
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "r7s8t9u0v001"
down_revision = "q1w2e3r4t005"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        # Hard unify migration PostgreSQL için tasarlanmıştır.
        # SQLite/test ortamlarda no-op bırakılır.
        return

    # PostgreSQL odaklı: legacy süreç tablolarındaki veriyi canonical tablolara taşır.
    op.execute(
        """
DO $$
BEGIN
  -- surec -> processes (minimum güvenli kolon seti)
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='surec')
     AND EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='processes')
     AND (SELECT COUNT(*) FROM processes) = 0
  THEN
    INSERT INTO processes (
      id, tenant_id, parent_id, code, name, english_name, weight,
      status, progress, start_date, end_date, description,
      is_active, deleted_at, created_at, updated_at
    )
    SELECT
      s.id,
      s.tenant_id,
      s.parent_id,
      s.code,
      COALESCE(NULLIF(TRIM(s.name), ''), s.ad),
      NULLIF(TRIM(s.name), ''),
      s.weight,
      s.durum,
      s.ilerleme,
      s.baslangic_tarihi,
      s.bitis_tarihi,
      s.aciklama,
      NOT COALESCE(s.silindi, FALSE),
      s.deleted_at,
      s.created_at,
      s.created_at
    FROM surec s
    ON CONFLICT (id) DO NOTHING;
  END IF;

  -- surec_performans_gostergesi -> process_kpis (minimum güvenli kolon seti)
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='surec_performans_gostergesi')
     AND EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='process_kpis')
     AND (SELECT COUNT(*) FROM process_kpis) = 0
  THEN
    INSERT INTO process_kpis (
      id, process_id, name, description, code, target_value, unit, period,
      data_source, target_setting_method, data_collection_method, calculation_method,
      weight, is_important, direction, calculated_score,
      sub_strategy_id, start_date, end_date, created_at, updated_at
    )
    SELECT
      spg.id,
      spg.surec_id,
      spg.ad,
      spg.aciklama,
      spg.kodu,
      spg.hedef_deger,
      COALESCE(spg.unit, spg.olcum_birimi),
      spg.periyot,
      spg.veri_alinacak_yer,
      spg.hedef_belirleme_yontemi,
      spg.veri_toplama_yontemi,
      spg.calculation_method,
      COALESCE(spg.weight, spg.agirlik),
      spg.onemli,
      spg.direction,
      spg.calculated_score,
      spg.alt_strateji_id,
      spg.baslangic_tarihi,
      spg.bitis_tarihi,
      spg.created_at,
      spg.created_at
    FROM surec_performans_gostergesi spg
    ON CONFLICT (id) DO NOTHING;
  END IF;

  -- bireysel_performans_gostergesi -> individual_performance_indicators (minimum güvenli kolon seti)
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='bireysel_performans_gostergesi')
     AND EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='individual_performance_indicators')
     AND (SELECT COUNT(*) FROM individual_performance_indicators) = 0
  THEN
    INSERT INTO individual_performance_indicators (
      id, user_id, name, description, code, target_value, actual_value, unit,
      period, weight, is_important, start_date, end_date, status, source,
      process_kpi_id, created_at, updated_at
    )
    SELECT
      bpg.id, bpg.user_id, bpg.ad, bpg.aciklama, bpg.kodu,
      bpg.hedef_deger, bpg.gerceklesen_deger, bpg.olcum_birimi,
      bpg.periyot, bpg.agirlik, bpg.onemli,
      bpg.baslangic_tarihi, bpg.bitis_tarihi, bpg.durum, bpg.kaynak,
      bpg.surec_pg_id, bpg.created_at, bpg.created_at
    FROM bireysel_performans_gostergesi bpg
    ON CONFLICT (id) DO NOTHING;
  END IF;

  -- bireysel_faaliyet -> individual_activities (minimum güvenli kolon seti)
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='bireysel_faaliyet')
     AND EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='individual_activities')
     AND (SELECT COUNT(*) FROM individual_activities) = 0
  THEN
    INSERT INTO individual_activities (
      id, user_id, name, description, start_date, end_date, status, progress,
      source, source_process_activity_id, created_at, updated_at
    )
    SELECT
      bf.id, bf.user_id, bf.ad, bf.aciklama, bf.baslangic_tarihi, bf.bitis_tarihi,
      bf.durum, bf.ilerleme, 'Bireysel', NULL,
      bf.created_at, bf.created_at
    FROM bireysel_faaliyet bf
    ON CONFLICT (id) DO NOTHING;
  END IF;

  -- performans_gosterge_veri -> kpi_data / individual_kpi_data
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='performans_gosterge_veri')
  THEN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='kpi_data')
       AND (SELECT COUNT(*) FROM kpi_data) = 0
    THEN
      INSERT INTO kpi_data (
        id, process_kpi_id, year, data_date, period_type, period_no, period_month,
        target_value, actual_value, status, status_percentage, description, user_id,
        created_at, updated_at, is_active, deleted_at, deleted_by_id
      )
      SELECT
        pgv.id,
        COALESCE(pgv.surec_pg_id, pgv.pg_id),
        pgv.yil,
        COALESCE(pgv.veri_tarihi, CURRENT_DATE),
        pgv.periyot_tipi,
        pgv.periyot,
        pgv.ay,
        pgv.hedef_deger,
        pgv.gerceklesen_deger,
        pgv.durum,
        pgv.durum_yuzdesi,
        pgv.aciklama,
        COALESCE(pgv.user_id, 1),
        pgv.created_at,
        pgv.created_at,
        NOT COALESCE(pgv.is_deleted, FALSE),
        pgv.deleted_at,
        NULL
      FROM performans_gosterge_veri pgv
      WHERE COALESCE(pgv.bireysel_pg_id, 0) = 0
      ON CONFLICT (id) DO NOTHING;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='individual_kpi_data')
       AND (SELECT COUNT(*) FROM individual_kpi_data) = 0
    THEN
      INSERT INTO individual_kpi_data (
        id, individual_indicator_id, year, data_date, period_type, period_no, period_month,
        target_value, actual_value, status, status_percentage, description, user_id,
        created_at, updated_at
      )
      SELECT
        pgv.id,
        pgv.bireysel_pg_id,
        pgv.yil,
        COALESCE(pgv.veri_tarihi, CURRENT_DATE),
        pgv.periyot_tipi,
        pgv.periyot,
        pgv.ay,
        pgv.hedef_deger,
        pgv.gerceklesen_deger,
        pgv.durum,
        pgv.durum_yuzdesi,
        pgv.aciklama,
        COALESCE(pgv.user_id, 1),
        pgv.created_at,
        pgv.created_at
      FROM performans_gosterge_veri pgv
      WHERE COALESCE(pgv.bireysel_pg_id, 0) <> 0
      ON CONFLICT (id) DO NOTHING;
    END IF;
  END IF;

  -- Legacy süreç tablolarını kaldır (hard migration)
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='performans_gosterge_veri_audit') THEN
    DROP TABLE performans_gosterge_veri_audit CASCADE;
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='faaliyet_takip') THEN
    DROP TABLE faaliyet_takip CASCADE;
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='favori_kpi') THEN
    DROP TABLE favori_kpi CASCADE;
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='surec_faaliyet') THEN
    DROP TABLE surec_faaliyet CASCADE;
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='performans_gosterge_veri') THEN
    DROP TABLE performans_gosterge_veri CASCADE;
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='bireysel_faaliyet') THEN
    DROP TABLE bireysel_faaliyet CASCADE;
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='bireysel_performans_gostergesi') THEN
    DROP TABLE bireysel_performans_gostergesi CASCADE;
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='surec_performans_gostergesi') THEN
    DROP TABLE surec_performans_gostergesi CASCADE;
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='surec') THEN
    DROP TABLE surec CASCADE;
  END IF;
END $$;
"""
    )


def downgrade():
    # Hard migration: downgrade yalnızca no-op olarak bırakıldı.
    # İhtiyaç halinde full backup üzerinden geri dönüş yapılmalıdır.
    pass
