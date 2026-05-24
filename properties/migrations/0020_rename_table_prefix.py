# Generated migration to rename table prefix from properties_* to pg_*

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0001_initial'),
    ]

    operations = [
        # Rename Property table
        migrations.RunSQL(
            sql='''
DO $$
BEGIN
    IF to_regclass('public.properties_property') IS NOT NULL AND to_regclass('public.pg_property') IS NULL THEN
        EXECUTE 'ALTER TABLE "properties_property" RENAME TO "pg_property"';
    END IF;
END $$;
''',
            reverse_sql='''
DO $$
BEGIN
    IF to_regclass('public.pg_property') IS NOT NULL AND to_regclass('public.properties_property') IS NULL THEN
        EXECUTE 'ALTER TABLE "pg_property" RENAME TO "properties_property"';
    END IF;
END $$;
''',
        ),
        # Rename Floor table
        migrations.RunSQL(
            sql='''
DO $$
BEGIN
    IF to_regclass('public.properties_floor') IS NOT NULL AND to_regclass('public.pg_floor') IS NULL THEN
        EXECUTE 'ALTER TABLE "properties_floor" RENAME TO "pg_floor"';
    END IF;
END $$;
''',
            reverse_sql='''
DO $$
BEGIN
    IF to_regclass('public.pg_floor') IS NOT NULL AND to_regclass('public.properties_floor') IS NULL THEN
        EXECUTE 'ALTER TABLE "pg_floor" RENAME TO "properties_floor"';
    END IF;
END $$;
''',
        ),
        # Rename Room table
        migrations.RunSQL(
            sql='''
DO $$
BEGIN
    IF to_regclass('public.properties_room') IS NOT NULL AND to_regclass('public.pg_room') IS NULL THEN
        EXECUTE 'ALTER TABLE "properties_room" RENAME TO "pg_room"';
    END IF;
END $$;
''',
            reverse_sql='''
DO $$
BEGIN
    IF to_regclass('public.pg_room') IS NOT NULL AND to_regclass('public.properties_room') IS NULL THEN
        EXECUTE 'ALTER TABLE "pg_room" RENAME TO "properties_room"';
    END IF;
END $$;
''',
        ),
        # Rename Bed table
        migrations.RunSQL(
            sql='''
DO $$
BEGIN
    IF to_regclass('public.properties_bed') IS NOT NULL AND to_regclass('public.pg_bed') IS NULL THEN
        EXECUTE 'ALTER TABLE "properties_bed" RENAME TO "pg_bed"';
    END IF;
END $$;
''',
            reverse_sql='''
DO $$
BEGIN
    IF to_regclass('public.pg_bed') IS NOT NULL AND to_regclass('public.properties_bed') IS NULL THEN
        EXECUTE 'ALTER TABLE "pg_bed" RENAME TO "properties_bed"';
    END IF;
END $$;
''',
        ),
        # Rename Resident table
        migrations.RunSQL(
            sql='''
DO $$
BEGIN
    IF to_regclass('public.properties_resident') IS NOT NULL AND to_regclass('public.pg_resident') IS NULL THEN
        EXECUTE 'ALTER TABLE "properties_resident" RENAME TO "pg_resident"';
    END IF;
END $$;
''',
            reverse_sql='''
DO $$
BEGIN
    IF to_regclass('public.pg_resident') IS NOT NULL AND to_regclass('public.properties_resident') IS NULL THEN
        EXECUTE 'ALTER TABLE "pg_resident" RENAME TO "properties_resident"';
    END IF;
END $$;
''',
        ),
        # Rename Occupancy table
        migrations.RunSQL(
            sql='''
DO $$
BEGIN
    IF to_regclass('public.properties_occupancy') IS NOT NULL AND to_regclass('public.pg_occupancy') IS NULL THEN
        EXECUTE 'ALTER TABLE "properties_occupancy" RENAME TO "pg_occupancy"';
    END IF;
END $$;
''',
            reverse_sql='''
DO $$
BEGIN
    IF to_regclass('public.pg_occupancy') IS NOT NULL AND to_regclass('public.properties_occupancy') IS NULL THEN
        EXECUTE 'ALTER TABLE "pg_occupancy" RENAME TO "properties_occupancy"';
    END IF;
END $$;
''',
        ),
        # Rename OccupancyHistory table
        migrations.RunSQL(
            sql='''
DO $$
BEGIN
    IF to_regclass('public.properties_occupancyhistory') IS NOT NULL AND to_regclass('public.pg_occupancy_history') IS NULL THEN
        EXECUTE 'ALTER TABLE "properties_occupancyhistory" RENAME TO "pg_occupancy_history"';
    END IF;
END $$;
''',
            reverse_sql='''
DO $$
BEGIN
    IF to_regclass('public.pg_occupancy_history') IS NOT NULL AND to_regclass('public.properties_occupancyhistory') IS NULL THEN
        EXECUTE 'ALTER TABLE "pg_occupancy_history" RENAME TO "properties_occupancyhistory"';
    END IF;
END $$;
''',
        ),
        # Rename Expense table
        migrations.RunSQL(
            sql='''
DO $$
BEGIN
    IF to_regclass('public.properties_expense') IS NOT NULL AND to_regclass('public.pg_expense') IS NULL THEN
        EXECUTE 'ALTER TABLE "properties_expense" RENAME TO "pg_expense"';
    END IF;
END $$;
''',
            reverse_sql='''
DO $$
BEGIN
    IF to_regclass('public.pg_expense') IS NOT NULL AND to_regclass('public.properties_expense') IS NULL THEN
        EXECUTE 'ALTER TABLE "pg_expense" RENAME TO "properties_expense"';
    END IF;
END $$;
''',
        ),
        # Rename Payment table
        migrations.RunSQL(
            sql='''
DO $$
BEGIN
    IF to_regclass('public.properties_payment') IS NOT NULL AND to_regclass('public.pg_payment') IS NULL THEN
        EXECUTE 'ALTER TABLE "properties_payment" RENAME TO "pg_payment"';
    END IF;
END $$;
''',
            reverse_sql='''
DO $$
BEGIN
    IF to_regclass('public.pg_payment') IS NOT NULL AND to_regclass('public.properties_payment') IS NULL THEN
        EXECUTE 'ALTER TABLE "pg_payment" RENAME TO "properties_payment"';
    END IF;
END $$;
''',
        ),
        # Rename MaintenanceRequest table
        migrations.RunSQL(
            sql='''
DO $$
BEGIN
    IF to_regclass('public.properties_maintenancerequest') IS NOT NULL AND to_regclass('public.pg_maintenance_request') IS NULL THEN
        EXECUTE 'ALTER TABLE "properties_maintenancerequest" RENAME TO "pg_maintenance_request"';
    END IF;
END $$;
''',
            reverse_sql='''
DO $$
BEGIN
    IF to_regclass('public.pg_maintenance_request') IS NOT NULL AND to_regclass('public.properties_maintenancerequest') IS NULL THEN
        EXECUTE 'ALTER TABLE "pg_maintenance_request" RENAME TO "properties_maintenancerequest"';
    END IF;
END $$;
''',
        ),
        # Rename User table
        migrations.RunSQL(
            sql='''
DO $$
BEGIN
    IF to_regclass('public.properties_user') IS NOT NULL AND to_regclass('public.pg_user') IS NULL THEN
        EXECUTE 'ALTER TABLE "properties_user" RENAME TO "pg_user"';
    END IF;
END $$;
''',
            reverse_sql='''
DO $$
BEGIN
    IF to_regclass('public.pg_user') IS NOT NULL AND to_regclass('public.properties_user') IS NULL THEN
        EXECUTE 'ALTER TABLE "pg_user" RENAME TO "properties_user"';
    END IF;
END $$;
''',
        ),
    ]
