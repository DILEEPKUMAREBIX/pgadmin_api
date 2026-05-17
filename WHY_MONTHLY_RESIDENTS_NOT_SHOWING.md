## Why Monthly Due Customers Not Showing in home_summary

There are **specific conditions** for monthly residents to appear in the API response:

---

## Conditions for Monthly Residents to Appear

### 1. In "OVERDUE" Section ✓
Monthly residents appear in overdue section when:
- **Joining date is on/before last month** (April or earlier when today is May 16)  
- **AND** At least one full calendar month has passed
- **AND** They have unpaid rent (due_amount > 0)

**Example (Today = May 16, 2026):**
- ✅ Resident joins April 10 → OVERDUE (1 full month = April)
- ✅ Resident joins March 1 → OVERDUE (2 full months = March + April)
- ❌ Resident joins May 1 → NOT overdue yet (0 complete months)
- ❌ Resident joins May 15 → NOT overdue yet (0 complete months)

**Calculation for April 10 joining date:**
```
Full month completed: April (1 month)
Due amount: 1 × monthly_rent
Status: OVERDUE (assuming no payment)
```

---

### 2. In "DUE" Section ✓
Monthly residents appear in due section when:
- **NOT in overdue** (haven't completed a full month yet)
- **AND** Their next billing date is **-1 to +5 days from today**

This uses the `next_billing_date()` function which:
- Uses `preferred_billing_day` if set, otherwise uses `joining_date.day`
- Calculates when they're next due for payment

**Example (Today = May 16, 2026):**

| Resident | Join | Billing Day | Next Bill | Days Away | Shows in DUE? |
|----------|------|-------------|-----------|-----------|---------------|
| Resident A | May 15 | 15 | May 15 | -1 | ✅ YES |
| Resident B | May 10 | 10 | Jun 10 | +25 | ❌ NO |
| Resident C | May 10 | 16 | May 16 | 0 | ✅ YES |
| Resident D | May 10 | 20 | May 20 | +4 | ✅ YES |
| Resident E | May 10 | 25 | May 25 | +9 | ❌ NO |

---

## Why You Don't See Monthly Residents

### Scenario 1: All Monthly Residents Just Joined This Month
**Problem:** If all residents joined on/after May 1, none have completed a full month yet.

- ❌ Won't show in OVERDUE (< 1 month passed)
- ❌ Won't show in DUE (billing date is too far away)

**Example:**
- Join date: May 10
- Billing day: 10
- Next billing: June 10 (25 days away)
- **Result:** Not shown (25 > 5 days)

### Scenario 2: Monthly Residents' Billing Dates Are Far Away
**Problem:** If billing dates are > 5 days away, they won't show in DUE.

**Example:**
- Join date: May 5
- Billing day: 5
- Today: May 16
- Next billing: June 5 (20 days away)
- **Result:** Not shown (20 > 5 days)

### Scenario 3: Monthly Residents Have Paid
**Problem:** If payment was made, due_amount = 0.

Even if they're overdue by date, they won't show if due_amount is 0.

---

## What You Should Check

### 1. Verify You Have Monthly Residents
```
GET /api/residents/?property=1

Filter for rent_type = 'monthly'
```

### 2. Check Their Joining Dates
For each monthly resident:
- Is joining_date on/before April 30? → Should appear in OVERDUE
- Is joining_date in May? → Won't appear unless billing date approaching

### 3. Check Their Billing Dates
Use this script to check if residents should appear:

```python
from datetime import date

today = date(2026, 5, 16)  # May 16

# For each monthly resident
residents = [
    {"name": "A", "join": date(2026, 4, 10), "billing_day": 10},
    {"name": "B", "join": date(2026, 5, 1), "billing_day": 1},
    {"name": "C", "join": date(2026, 5, 10), "billing_day": 16},
]

for res in residents:
    # Check if overdue (joined before May 1)
    last_month_end = date(2026, 4, 30)
    is_overdue = res["join"] <= last_month_end
    
    # Check billing date
    if res["billing_day"] <= today.day:
        next_bill = date(2026, 6, min(res["billing_day"], 30))
    else:
        next_bill = date(2026, 5, min(res["billing_day"], 31))
    
    delta = (next_bill - today).days
    shows_in_due = -1 <= delta <= 5
    
    in_response = is_overdue or shows_in_due
    print(f"{res['name']}: overdue={is_overdue}, due={shows_in_due}, shows={in_response}")

# Output:
# A: overdue=True, due=?, shows=True  (shows in OVERDUE)
# B: overdue=False, due=False, shows=False  (next bill June 1, 16 days away)
# C: overdue=False, due=True, shows=True  (next bill May 16, billing today!)
```

---

## To Make Monthly Residents Show Up

### Option 1: Create Residents Joining Before Last Month
```python
# They'll automatically show in OVERDUE
Resident.objects.create(
    property=property,
    first_name="John",
    rent=5000,
    rent_type="monthly",
    joining_date=date(2026, 4, 1),  # April = Before May
    preferred_billing_day=1,
)
```

### Option 2: Create Residents with Upcoming Billing Date
```python
# They'll show in DUE if billing is within 5 days
import datetime

today = datetime.date.today()
upcoming_billing_day = (today + datetime.timedelta(days=3)).day  # 3 days away

Resident.objects.create(
    property=property,
    first_name="Jane",
    rent=5000,
    rent_type="monthly",
    joining_date=today,
    preferred_billing_day=upcoming_billing_day,
)
```

### Option 3: Set Billing Day Within Window
```python
today = date(2026, 5, 16)
# Billing day = 16 (today) to 21 (5 days away)

Resident.objects.create(
    property=property,
    first_name="Mike",
    rent=5000,
    rent_type="monthly",
    joining_date=date(2026, 5, 10),  # This month
    preferred_billing_day=16,  # Today - will show in DUE!
)
```

---

## API Behavior Summary

| Rent Type | Overdue Threshold | Due Window | Shows When |
|-----------|------------------|-----------|-----------|
| DAILY | 3+ days | Always | Day 1+ |
| WEEKLY | 7+ days | Week ends (5-6 days) | 5+ days into week |
| BI-WEEKLY | 14+ days | Period ends (11-13 days) | 11+ days in |
| MONTHLY | 1+ month passed | -1 to +5 days before billing | Past month OR billing approaching |

---

## Fix Applied (May 2026)

Updated home_summary logic to:
1. Use centralized `next_billing_date()` function for monthly residents
2. Check if next billing date is within [-1, +5] days window
3. Show in DUE section if approaching (more reliable than checking calendar)

This ensures consistency with other payment type calculations.

---

## Test Your Data

Run this query to see all your residents:

```
GET /api/properties/1/home_summary/
```

Compare the response with this checklist:
- ✅ Daily residents with 3+ days show in OVERDUE
- ✅ Monthly residents from April+ show in OVERDUE  
- ✅ Monthly residents with upcoming billing (within 5 days) show in DUE
- ✅ Monthly residents with billing >5 days away do NOT show

If any of these don't match, check the specific resident's:
- `joining_date`
- `preferred_billing_day` (or defaults to joining_date.day)
- Payment history
