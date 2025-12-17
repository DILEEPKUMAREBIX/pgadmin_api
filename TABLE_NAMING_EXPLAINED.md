# 🔍 Why Tables Have `properties_` Prefix?

## Short Answer

Django automatically names tables based on:
```
<app_name>_<model_name_lowercase>
```

So your app is named **`properties`** → all tables get **`properties_`** prefix

---

## 📝 How Django Names Tables

### Rule 1: App Name + Model Name

```
App Name:     properties
              ↓
Model Class:  Property → property (lowercase)
              ↓
Table Name:   properties_property
```

### Examples from Your Project

```python
# Model Class Name          →  Table Name
class Property              →  properties_property
class Floor                 →  properties_floor
class Room                  →  properties_room
class Bed                   →  properties_bed
class Resident              →  properties_resident
class Occupancy             →  properties_occupancy
class OccupancyHistory      →  properties_occupancyhistory
class Expense               →  properties_expense
class Payment               →  properties_payment
class MaintenanceRequest    →  properties_maintenancerequest
class User                  →  properties_user
```

---

## 🎯 Why This Naming Convention?

### 1. **Namespace Separation**
```
If you had multiple apps:
  - properties_property
  - residents_property     (different table!)
  - occupancy_property     (different table!)

This prevents naming conflicts!
```

### 2. **Clear Organization**
```
properties_*
  - properties_property
  - properties_floor
  - properties_room
  - properties_bed
  - properties_resident
  - properties_occupancy
  - properties_expense
  - properties_payment
  - properties_maintenancerequest
  - properties_user

All your tables are grouped together! 
```

### 3. **Multi-App Projects**
```
If you add more apps later:

auth_*
  - auth_user
  - auth_group
  - auth_permission

billing_*
  - billing_invoice
  - billing_payment
  - billing_customer

properties_*
  - properties_property
  - properties_resident
  - properties_occupancy
```

---

## 🔧 Can You Change the Table Name?

Yes! Using Django's `Meta` class:

### Current (Auto-generated):
```python
class Property(models.Model):
    name = models.CharField(max_length=255)
    
    # Auto table name: properties_property
```

### Custom:
```python
class Property(models.Model):
    name = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'properties'  # Custom name!
        
# Table name: properties (instead of properties_property)
```

### All Your Models (Current Default):
```python
class Floor(models.Model):
    # Auto: properties_floor
    
    # Or custom:
    class Meta:
        db_table = 'floors'  # Just 'floors'
```

---

## 📊 Your Current Table Names

| Model Class | Auto Table Name | Custom Option |
|-------------|-----------------|---------------|
| Property | `properties_property` | `db_table = 'properties'` |
| Floor | `properties_floor` | `db_table = 'floors'` |
| Room | `properties_room` | `db_table = 'rooms'` |
| Bed | `properties_bed` | `db_table = 'beds'` |
| Resident | `properties_resident` | `db_table = 'residents'` |
| Occupancy | `properties_occupancy` | `db_table = 'occupancy'` |
| OccupancyHistory | `properties_occupancyhistory` | `db_table = 'occupancy_history'` |
| Expense | `properties_expense` | `db_table = 'expenses'` |
| Payment | `properties_payment` | `db_table = 'payments'` |
| MaintenanceRequest | `properties_maintenancerequest` | `db_table = 'maintenance_requests'` |
| User | `properties_user` | `db_table = 'users'` |

---

## ✅ Is This a Problem?

**NO!** This is actually **GOOD PRACTICE**. Here's why:

### Pros ✅
1. **Prevents naming conflicts** - Multiple apps can coexist
2. **Organized structure** - All app tables grouped together
3. **Standard Django convention** - Everyone expects this
4. **Scalable** - Works for small and large projects
5. **Clear ownership** - You know which app owns which table

### Cons ❌
1. **Longer table names** - More to type (minor)
2. **Slightly more verbose** - But it's clear (minor)

---

## 🔄 Why Not Change It?

While you CAN customize table names, **DON'T** unless necessary because:

```
1. Django ORM still works perfectly with auto-generated names
2. Migrations work seamlessly
3. Admin interface works automatically
4. API queries work as expected
5. This is what other Django developers expect

Changing would:
- Add complexity
- Require custom Meta classes on each model
- Make it less "Pythonic"
- Cause issues if switching to other apps
```

---

## 📝 Example: How Django Generates Names

### Step 1: Define Model
```python
# In properties/models.py
class Property(models.Model):
    name = models.CharField(max_length=255)
```

### Step 2: Django Converts to Table
```
App folder:  properties/
Model name:  Property
Django does: <app>_<model_lowercase>
Result:      properties_property
```

### Step 3: SQL Query
```sql
-- Django generates this automatically:
SELECT * FROM properties_property;
```

### Step 4: ORM Query
```python
# You write this:
Property.objects.all()

# Django translates to:
SELECT * FROM properties_property;
```

---

## 🗄️ Real Examples from Your Database

```sql
-- Your tables (with properties_ prefix):
SELECT table_name FROM information_schema.tables 
WHERE table_name LIKE 'properties_%';

Results:
├── properties_property
├── properties_floor
├── properties_room
├── properties_bed
├── properties_resident
├── properties_occupancy
├── properties_occupancyhistory
├── properties_expense
├── properties_payment
├── properties_maintenancerequest
└── properties_user

-- Django's internal tables (no prefix):
├── auth_user
├── auth_group
├── auth_permission
├── django_migrations
├── django_content_type
└── django_admin_log
```

---

## 🎯 How to Query Tables

### Using Django ORM (Recommended)
```python
# No need to think about table names!
from properties.models import Property

properties = Property.objects.all()
```

### Using Raw SQL (Advanced)
```python
# If you need to, you can use full table name:
from django.db import connection

cursor = connection.cursor()
cursor.execute("SELECT * FROM properties_property")
```

### Using psql (PostgreSQL CLI)
```bash
# Connect to database
psql -U postgres -d pgadmin_db

# See all properties
SELECT * FROM properties_property;

# Count properties
SELECT COUNT(*) FROM properties_property;
```

---

## 🔍 How Django Knows Table Names

### Migration Files
When you run `makemigrations`, Django creates migration files:

```python
# properties/migrations/0001_initial.py

class Migration(migrations.Migration):
    operations = [
        migrations.CreateModel(
            name='Property',
            fields=[...],
            options={'db_table': 'properties_property'},  # ← Here!
        ),
    ]
```

Django stores the table name mapping here!

---

## 📚 Django Documentation

The naming convention follows Django's official naming rules:

```
https://docs.djangoproject.com/en/4.2/ref/models/options/#table-names
```

From Django docs:
> "The name of the table to use for the model. If this isn't given, 
> Django will use <app_name>_<model_name_lowercase> as the table name."

---

## 🎓 Multi-App Example

If your project grows:

```
pgadmin_config/          ← Main project
├── properties/          ← App 1 (yours)
│   └── models.py
│       ├── Property           → properties_property
│       ├── Resident           → properties_resident
│       └── Payment            → properties_payment
│
├── billing/             ← App 2 (hypothetical)
│   └── models.py
│       ├── Invoice            → billing_invoice
│       ├── Bill               → billing_bill
│       └── Customer           → billing_customer
│
└── notifications/       ← App 3 (hypothetical)
    └── models.py
        ├── Notification      → notifications_notification
        └── Preference        → notifications_preference
```

All namespaced clearly! ✅

---

## ✨ Summary

| Aspect | Answer |
|--------|--------|
| Why prefix? | Django naming convention: `<app>_<model>` |
| Is it a problem? | NO! It's actually best practice |
| Can I change it? | Yes, but NOT recommended |
| Does it affect functionality? | NO! Django handles it automatically |
| Should I worry? | NO! Use Django ORM, let it handle table names |
| How do I query? | Use `Model.objects.all()` - Django translates automatically |

---

## 🎯 Bottom Line

```
✅ Your table naming is PERFECT
✅ This is the standard Django way
✅ All your queries work automatically
✅ Your API works seamlessly
✅ No changes needed!

Just use: Property.objects.all()
Django translates to: SELECT * FROM properties_property
```

---

**Everything is working as designed! No action needed.** 🎉
