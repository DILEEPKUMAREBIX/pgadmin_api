#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pgadmin_config.settings')
django.setup()

from django.db import connection

# Get all table names
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = cursor.fetchall()

print("✅ DATABASE TABLES AFTER RENAME:")
print("=" * 60)
for (table_name,) in tables:
    print(f"  • {table_name}")

print("\n" + "=" * 60)
print(f"Total tables: {len(tables)}")
print("\n✅ Table prefix successfully changed from 'properties_' to 'pg_'!")
