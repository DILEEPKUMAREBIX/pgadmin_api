# Generated migration to rename table prefix from properties_* to pg_*

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0001_initial'),
    ]

    operations = [
        # Rename Property table
        migrations.RunSQL(
            sql='ALTER TABLE "properties_property" RENAME TO "pg_property"',
            reverse_sql='ALTER TABLE "pg_property" RENAME TO "properties_property"',
        ),
        # Rename Floor table
        migrations.RunSQL(
            sql='ALTER TABLE "properties_floor" RENAME TO "pg_floor"',
            reverse_sql='ALTER TABLE "pg_floor" RENAME TO "properties_floor"',
        ),
        # Rename Room table
        migrations.RunSQL(
            sql='ALTER TABLE "properties_room" RENAME TO "pg_room"',
            reverse_sql='ALTER TABLE "pg_room" RENAME TO "properties_room"',
        ),
        # Rename Bed table
        migrations.RunSQL(
            sql='ALTER TABLE "properties_bed" RENAME TO "pg_bed"',
            reverse_sql='ALTER TABLE "pg_bed" RENAME TO "properties_bed"',
        ),
        # Rename Resident table
        migrations.RunSQL(
            sql='ALTER TABLE "properties_resident" RENAME TO "pg_resident"',
            reverse_sql='ALTER TABLE "pg_resident" RENAME TO "properties_resident"',
        ),
        # Rename Occupancy table
        migrations.RunSQL(
            sql='ALTER TABLE "properties_occupancy" RENAME TO "pg_occupancy"',
            reverse_sql='ALTER TABLE "pg_occupancy" RENAME TO "properties_occupancy"',
        ),
        # Rename OccupancyHistory table
        migrations.RunSQL(
            sql='ALTER TABLE "properties_occupancyhistory" RENAME TO "pg_occupancy_history"',
            reverse_sql='ALTER TABLE "pg_occupancy_history" RENAME TO "properties_occupancyhistory"',
        ),
        # Rename Expense table
        migrations.RunSQL(
            sql='ALTER TABLE "properties_expense" RENAME TO "pg_expense"',
            reverse_sql='ALTER TABLE "pg_expense" RENAME TO "properties_expense"',
        ),
        # Rename Payment table
        migrations.RunSQL(
            sql='ALTER TABLE "properties_payment" RENAME TO "pg_payment"',
            reverse_sql='ALTER TABLE "pg_payment" RENAME TO "properties_payment"',
        ),
        # Rename MaintenanceRequest table
        migrations.RunSQL(
            sql='ALTER TABLE "properties_maintenancerequest" RENAME TO "pg_maintenance_request"',
            reverse_sql='ALTER TABLE "pg_maintenance_request" RENAME TO "properties_maintenancerequest"',
        ),
        # Rename User table
        migrations.RunSQL(
            sql='ALTER TABLE "properties_user" RENAME TO "pg_user"',
            reverse_sql='ALTER TABLE "pg_user" RENAME TO "properties_user"',
        ),
    ]
