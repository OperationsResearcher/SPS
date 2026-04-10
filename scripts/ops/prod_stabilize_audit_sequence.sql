-- Purpose: Idempotent production stabilization for audit_logs ID sequence.
-- Safe to run multiple times. Does not alter table schema.
-- Preconditions:
--   - PostgreSQL
--   - Table public.audit_logs exists
-- Rollback:
--   - Restore from pre-change backup/snapshot.

BEGIN;

DO $$
DECLARE
    v_table_exists boolean;
    v_seq_name text;
    v_max_id bigint;
    v_next_id bigint;
BEGIN
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = 'audit_logs'
    ) INTO v_table_exists;

    IF NOT v_table_exists THEN
        RAISE NOTICE 'Table public.audit_logs not found, skipping.';
        RETURN;
    END IF;

    SELECT pg_get_serial_sequence('public.audit_logs', 'id')
      INTO v_seq_name;

    IF v_seq_name IS NULL THEN
        RAISE NOTICE 'No serial/identity sequence bound to public.audit_logs.id, skipping.';
        RETURN;
    END IF;

    EXECUTE 'SELECT COALESCE(MAX(id), 0) FROM public.audit_logs'
      INTO v_max_id;

    v_next_id := v_max_id + 1;

    -- Align sequence to next free ID; false means next nextval() returns v_next_id.
    PERFORM setval(v_seq_name, v_next_id, false);

    RAISE NOTICE 'Aligned sequence % to next id % (max id was %).', v_seq_name, v_next_id, v_max_id;
END$$;

COMMIT;

-- Verification queries (manual):
-- SELECT MAX(id) AS max_id FROM public.audit_logs;
-- SELECT pg_get_serial_sequence('public.audit_logs', 'id') AS seq_name;
-- SELECT last_value, is_called FROM public.audit_logs_id_seq;
