## MANIKANTA Issue - FIXED ✅

### Problem
MANIKANTA (ID 65) resident was not showing in home_summary API even though they had **arrears of 5000**.

**Resident Details:**
- Joining date: May 16, 2026
- Rent type: Monthly
- Rent: 10,000
- **Arrears: 5,000** ← This should make them appear!
- Preferred billing day: 2
- Next billing: June 2 (16 days away)

### Root Cause
The API logic only showed monthly residents if:
1. They were OVERDUE (completed 1+ months), OR
2. Their billing date was within -1 to +5 days

MANIKANTA met neither condition:
- Only 1 day into residency (not a complete month yet)
- Next billing 16 days away (> 5 day window)

**But they had arrears!** This should override the timing logic.

---

## Fix Applied

Updated `home_summary()` API logic:

**For Monthly Residents:**
```python
# Show as DUE if:
# 1. Next billing date is approaching (within 5 days), OR
# 2. Has arrears (even if no rent accrued yet)

has_arrears = Decimal(resident.arrears or 0) > 0
if is_billing_soon or has_arrears:
    should_add_to_due = True
```

Now residents with **any arrears** automatically show in the DUE section, regardless of when they joined or their next billing date.

---

## Expected Behavior After Fix

### MANIKANTA (ID 65) - Now Shows ✅

**API Response:**
```json
{
  "due": {
    "count": 1,
    "total_amount": "5000.00",
    "details": [{
      "id": 65,
      "first_name": "MANIKANTA",
      "last_name": "TANGUDU",
      "rent_type": "monthly",
      "rent": "10000.00",
      "joining_date": "2026-05-16",
      "preferred_billing_day": 2,
      "arrears": "5000.00",
      "due": "5000.00",
      "due_amount": "5000.00"  // ← From arrears
    }]
  }
}
```

**Why:**
1. `calculate_due_amount()` = 5000 (from arrears, no complete month)
2. `is_overdue()` = False (only 1 day passed)
3. `has_arrears` = True (5000 > 0)
4. Result: Shows in "due" section because `is_billing_soon OR has_arrears` = True

---

## All Residents Summary (May 17, 2026)

Based on your pg_resident table data:

| ID | Name | Type | Join | Billing | Arrears | Status | Shows As |
|---|---|---|---|---|---|---|---|
| **65** | MANIKANTA | monthly | May 16 | 2 | **5000** | ✅ DUE | **due** (arrears) |
| **64** | Test Daily | daily | May 4 | - | 0 | Moved out May 9 | ❌ Hidden |
| **63** | Test Delete | daily | Apr 24 | - | 0 | 23 days overdue | **overdue** |
| **62** | San Latest | monthly | Mar 1 | 4 | 0 | 3 months overdue | **overdue** |
| **61** | Dileep | monthly | Apr 1 | - | 0 | Moved out May 9 | ❌ Hidden |
| **59** | San Test | monthly | Mar 1 | 1 | 0 | 3 months overdue | **overdue** |
| **58** | Vasavi K | monthly | Apr 1 | 1 | 0 | 1+ months overdue | **overdue** |

---

## Key Rules Now Implemented

### Daily Residents
✅ Show in **OVERDUE** if 3+ days passed without payment
✅ Show in **DUE** if 1-2 days passed

### Weekly Residents
✅ Show in **OVERDUE** if 7+ days passed
✅ Show in **DUE** if in last 2 days of week

### Bi-Weekly Residents
✅ Show in **OVERDUE** if 14+ days passed
✅ Show in **DUE** if in last 3 days of period

### Monthly Residents
✅ Show in **OVERDUE** if 1+ complete months passed
✅ Show in **DUE** if:
  - Next billing date within 5 days, OR
  - **Has arrears (NEW FIX)**
✅ Skip if moved out

---

## Testing

Run home_summary API:
```
GET /api/properties/1/home_summary/
```

Expected response shows:
- **due:** 1 resident (MANIKANTA with 5000 arrears)
- **overdue:** 4 residents (Test Delete, San Latest, San Test, Vasavi K)

---

## Implementation Notes

1. **Skip Early:** If `due_amount <= 0`, resident is skipped entirely
2. **Check Overdue:** If `is_overdue() = True`, goes to OVERDUE section
3. **Check Conditions:** If not overdue:
   - DAILY: Show if joined today or earlier
   - WEEKLY: Show if in last 2 days of week
   - BI-WEEKLY: Show if in last 3 days
   - **MONTHLY: Show if billing soon OR has arrears ✓**
4. **Add to Section:** If any condition met, add to respective section

This ensures residents with arrears are never hidden, even if timing doesn't align.
