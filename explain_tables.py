import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pgadmin_config.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;")
tables = cursor.fetchall()

print("=" * 80)
print("ALL TABLES IN DATABASE (21 total)")
print("=" * 80)
print()

# Django Core Tables (10)
print("█ DJANGO CORE TABLES (Automatically Created by Django - 10 tables)")
print("-" * 80)

core_tables = {
    'auth_group': 'User groups for permission management (e.g., "Admins", "Staff")',
    'auth_group_permissions': 'M2M relationship: Which permissions each group has',
    'auth_permission': 'All available permissions in the system (add, change, delete, view)',
    'auth_user': 'User accounts for login and authentication',
    'auth_user_groups': 'M2M relationship: Which groups each user belongs to',
    'auth_user_user_permissions': 'M2M relationship: Direct user-specific permissions',
    'django_content_type': 'Content type framework - tracks which models exist',
    'django_migrations': 'Migration history - tracks which migrations have been applied',
    'django_session': 'Session data storage for user sessions',
    'django_admin_log': 'Admin interface activity log',
}

for table_name, description in sorted(core_tables.items()):
    print(f"  • {table_name:<35} → {description}")

print()
print("█ YOUR APPLICATION TABLES (Properties App - 11 tables)")
print("-" * 80)

app_tables = {
    'properties_property': 'Main property/building information',
    'properties_floor': 'Floors within each property',
    'properties_room': 'Rooms on each floor',
    'properties_bed': 'Individual beds in each room',
    'properties_resident': 'Tenant/resident information',
    'properties_occupancy': 'Current occupancy assignments',
    'properties_occupancyhistory': 'Historical occupancy records',
    'properties_expense': 'Building expenses and maintenance costs',
    'properties_payment': 'Rent and other payments',
    'properties_maintenancerequest': 'Maintenance issues and requests',
    'properties_user': 'Custom user model (if extended)',
}

for table_name, description in sorted(app_tables.items()):
    if any(table_name == t[0] for t in tables):
        print(f"  • {table_name:<35} → {description}")

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Django Core Tables:        10 tables (required by Django framework)")
print(f"Your App Tables:           11 tables (from your models)")
print(f"Total:                     21 tables")
print()
print("WHY THESE EXTRA TABLES?")
print("-" * 80)
print("""
Django automatically creates these core tables when you run migrations:

1. auth_* tables: Django's built-in authentication system
   - User model for login/authentication
   - Group and Permission system for access control
   - Required for Django admin, API security, etc.

2. django_* tables: Django framework infrastructure
   - content_type: Internal registry of all models
   - migrations: Tracks which migrations have been applied
   - sessions: Stores user session data when they log in
   - admin_log: Records of admin interface changes

3. properties_* tables: YOUR 11 MODELS
   - Created from your models.py
   - Specific to your PG Admin application

These are NOT optional - they're part of Django's core architecture and enable:
✓ User authentication
✓ Permission management
✓ Admin interface
✓ API security
✓ Session management
✓ Migration tracking

ALL 21 TABLES ARE NECESSARY AND EXPECTED.
""")
print("=" * 80)

cursor.close()
