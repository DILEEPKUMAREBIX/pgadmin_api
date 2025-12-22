-- Resident schema update for Cloud SQL (Postgres)
-- Date: 2025-12-22
-- Safe to run in pgAdmin against the production database

BEGIN;

-- 1) Add new columns first_name/last_name (add as NULL first)
ALTER TABLE pg_resident
  ADD COLUMN IF NOT EXISTS first_name VARCHAR(150),
  ADD COLUMN IF NOT EXISTS last_name VARCHAR(150);

-- 2) Backfill from existing name column if present
--    first_name: first token; last_name: remainder after first token (NULL if absent)
UPDATE pg_resident
SET
  first_name = COALESCE(
    NULLIF(regexp_replace(name, '^\s*(\S+).*$', '\1'), ''),
    first_name
  ),
  last_name = NULLIF(regexp_replace(name, '^\s*\S+\s+(.*)$', '\1'), '');

-- 3) Enforce NOT NULL on first_name after backfill
ALTER TABLE pg_resident
  ALTER COLUMN first_name SET NOT NULL;

-- 4) Add preferred_billing_day with constraint 1..31
ALTER TABLE pg_resident
  ADD COLUMN IF NOT EXISTS preferred_billing_day SMALLINT;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'pg_resident_preferred_billing_day_check'
  ) THEN
    ALTER TABLE pg_resident
      ADD CONSTRAINT pg_resident_preferred_billing_day_check
      CHECK (preferred_billing_day BETWEEN 1 AND 31);
  END IF;
END $$;

-- 5) Create index to support queries on preferred_billing_day
CREATE INDEX IF NOT EXISTS idx_pg_resident_preferred_billing_day
  ON pg_resident (preferred_billing_day);

-- 6) Drop deprecated columns if they exist
ALTER TABLE pg_resident
  DROP COLUMN IF EXISTS name,
  DROP COLUMN IF EXISTS next_pay_date,
  DROP COLUMN IF EXISTS payment_cycle_start;

COMMIT;

-- Rollback helper (only if you need to undo within same session):
-- ROLLBACK; -- instead of COMMIT above
