-- Drop redundant Resident location columns now derived from Occupancy
-- Date: 2025-12-22

BEGIN;

ALTER TABLE pg_resident
  DROP COLUMN IF EXISTS current_bed,
  DROP COLUMN IF EXISTS current_room,
  DROP COLUMN IF EXISTS current_floor;

COMMIT;
