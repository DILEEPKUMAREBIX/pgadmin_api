# 📋 Quick Reference: Table Naming Convention

## The Formula

```
Django Table Name = <app_name> + "_" + <model_name_lowercase>
```

## Your Project

```
App Name: properties
          ↓
          
Model Classes:
  ├─ Property              → properties_property
  ├─ Floor                 → properties_floor
  ├─ Room                  → properties_room
  ├─ Bed                   → properties_bed
  ├─ Resident              → properties_resident
  ├─ Occupancy             → properties_occupancy
  ├─ OccupancyHistory      → properties_occupancyhistory
  ├─ Expense               → properties_expense
  ├─ Payment               → properties_payment
  ├─ MaintenanceRequest    → properties_maintenancerequest
  └─ User                  → properties_user
```

## In Your PostgreSQL Database

```sql
\dt properties_*

                    List of relations
 Schema |              Name              | Type  | Owner
--------+--------------------------------+-------+----------
 public | properties_bed                 | table | postgres
 public | properties_expense             | table | postgres
 public | properties_floor               | table | postgres
 public | properties_maintenancerequest  | table | postgres
 public | properties_occupancy           | table | postgres
 public | properties_occupancyhistory    | table | postgres
 public | properties_payment             | table | postgres
 public | properties_property            | table | postgres
 public | properties_resident            | table | postgres
 public | properties_room                | table | postgres
 public | properties_user                | table | postgres
```

## Why?

```
✅ Namespace separation      - Prevents table name conflicts
✅ App organization         - All app tables grouped together
✅ Standard Django pattern  - Every Django project does this
✅ Multi-app support       - Scale easily with more apps
✅ Clear ownership         - Know which app owns which table
```

## How Django Handles It

```
Your Python Code (Django ORM):
    Property.objects.all()
              ↓
    Django internally translates to:
              ↓
    SELECT * FROM properties_property
              ↓
    PostgreSQL executes query
              ↓
    Results returned to your app
```

**You never think about table names!** Django handles it automatically. ✅

## Can You Customize?

Yes, but not recommended:

```python
# Current (Auto):
class Property(models.Model):
    name = models.CharField(max_length=255)
    # Table: properties_property ✅

# Custom (Not recommended):
class Property(models.Model):
    name = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'custom_name'  # Table: custom_name
        # But this breaks conventions!
```

## Best Practice

✅ **Leave it as is!** Use Django's auto-naming convention.

This is what the entire Django community does.

---

**No changes needed. Everything is working perfectly!** 🎉
