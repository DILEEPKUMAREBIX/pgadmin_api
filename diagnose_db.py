#!/usr/bin/env python
"""
Diagnostic script to check Django database connection and data
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pgadmin_config.settings')
django.setup()

from django.db import connection
from properties.models import Property

print("=" * 70)
print("🔍 DATABASE CONNECTION DIAGNOSTIC")
print("=" * 70)

# Test 1: Database connection
print("\n1️⃣  Testing Database Connection...")
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    print("   ✅ Database connection: SUCCESS")
except Exception as e:
    print(f"   ❌ Database connection: FAILED - {str(e)}")
    exit(1)

# Test 2: Count properties using raw SQL
print("\n2️⃣  Checking Properties Table (Raw SQL)...")
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM properties_property")
        result = cursor.fetchone()
        count = result[0] if result else 0
    print(f"   📊 Total properties in database: {count}")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# Test 3: Check Django ORM
print("\n3️⃣  Checking Properties via Django ORM...")
try:
    all_properties = Property.objects.all()
    count = all_properties.count()
    print(f"   📊 Properties via Django ORM: {count}")
    
    if count > 0:
        print("\n   📋 Properties List:")
        for prop in all_properties:
            print(f"      - ID: {prop.id}, Name: {prop.name}, Active: {prop.is_active}")
    else:
        print("   ⚠️  No properties found!")
        
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# Test 4: Check database settings
print("\n4️⃣  Database Configuration...")
from django.conf import settings
db_config = settings.DATABASES['default']
print(f"   Engine: {db_config.get('ENGINE')}")
print(f"   Database: {db_config.get('NAME')}")
print(f"   Host: {db_config.get('HOST')}")
print(f"   Port: {db_config.get('PORT')}")
print(f"   User: {db_config.get('USER')}")

# Test 5: Check all tables
print("\n5️⃣  Available Tables in Database...")
try:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
    
    if tables:
        print(f"   📊 Total tables: {len(tables)}")
        print("   Tables:")
        for table in tables:
            print(f"      - {table[0]}")
    else:
        print("   ⚠️  No tables found!")
        
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# Test 6: Django migrations status
print("\n6️⃣  Migration Status...")
try:
    from django.core.management import call_command
    from io import StringIO
    
    out = StringIO()
    call_command('showmigrations', stdout=out)
    migrations_output = out.getvalue()
    
    # Count applied migrations
    applied_count = migrations_output.count('[X]')
    print(f"   ✅ Applied migrations: {applied_count}")
    
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

print("\n" + "=" * 70)
print("✨ DIAGNOSTIC COMPLETE")
print("=" * 70)
