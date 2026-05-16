# Due Amount Calculation Backend Migration

## Overview

The due amount calculation logic has been successfully moved from the mobile app/client to the backend API. This change reduces complexity on the UI side and ensures consistent calculations across all clients.

## Key Changes

### 1. New Utility Module: `payment_utils.py`

A centralized module for all payment and due calculation logic:

**Main Functions:**

- **`calculate_due_amount(resident, as_of_date=None)`** - Calculate total due for a resident
  - Returns: Decimal amount
  - Supports: daily, weekly, bi-weekly, monthly rent types
  - For DAILY: `days_since_joining × daily_rent - payments_made + arrears`

- **`is_overdue(resident, as_of_date=None)`** - Check if a resident has overdue payments
  - Returns: Boolean
  - Considers rent_type specific thresholds

- **`get_overdue_amount(resident, as_of_date=None)`** - Get only the overdue portion
  - Returns: Decimal amount

- **`get_days_overdue(resident, as_of_date=None)`** - Days past due date

- **`next_billing_date(resident, as_of_date=None)`** - Calculate next billing date for a resident

### 2. Updated ResidentSerializer

The `get_due()` method now uses the centralized `calculate_due_amount()` function:

```python
def get_due(self, obj):
    """Calculate total due amount for resident using centralized payment utils."""
    from .payment_utils import calculate_due_amount
    due_amount = calculate_due_amount(obj)
    return str(due_amount.quantize(Decimal('0.01')))
```

When retrieving a resident, the `due` field in the response now includes:
- Arrears from previous periods
- Expected rent for all billing periods that have elapsed
- Minus all payments received
- Calculation varies by rent_type (see below)

### 3. Enhanced Home Summary API

**Endpoint:** `GET /api/properties/{property_id}/home_summary/`

**New Response Structure:**

```json
{
  "property": {
    "id": 1,
    "name": "Property Name"
  },
  "occupied_beds": 15,
  "available_beds": 20,
  "overdue": {
    "count": 5,
    "total_amount": "2500.00",
    "details": [
      {
        "id": 10,
        "first_name": "John",
        "last_name": "Doe",
        "rent_type": "monthly",
        "due_amount": "5000.00",
        ... (full resident serializer data)
      }
    ]
  },
  "due": {
    "count": 3,
    "total_amount": "1450.00",
    "details": [
      {
        "id": 11,
        "first_name": "Jane",
        "last_name": "Smith",
        "rent_type": "daily",
        "due_amount": "500.00",
        ... (full resident serializer data)
      }
    ]
  }
}
```

**Key Improvements:**

1. **Includes All Rent Types** - Now handles daily, weekly, bi-weekly, and monthly residents
2. **Separate Due vs Overdue** - Distinguishes between amounts that are currently overdue vs. upcoming due
3. **Full Resident Data** - Returns complete resident information in details array
4. **Consistent Calculations** - All amounts calculated using centralized utility functions

## How Due is Calculated by Rent Type

### DAILY Rent Type

- **Expected Amount**: `days_since_joining × daily_rent`
- **Due Status**: Shows as "DUE" if 1+ days have passed since joining
- **Overdue Status**: Marked as overdue if 1+ day has elapsed without payment
- **Example**: 
  - Resident joins on May 10, daily rent = $50
  - On May 12 (2 days later): Due amount = 2 × $50 = $100 (OVERDUE)
  - On May 11 (1 day later): Due amount = 1 × $50 = $50 (DUE)

### WEEKLY Rent Type

- **Expected Amount**: `(days_since_joining / 7) × weekly_rent`
- **Due Status**: Shows as "DUE" if in last 2 days of the week (days 5-6)
- **Overdue Status**: Marked as overdue if 7+ days have elapsed
- **Example**:
  - Resident joins on May 10, weekly rent = $350
  - On May 17 (7 days later): Due amount = $350 (OVERDUE)

### BI-WEEKLY Rent Type

- **Expected Amount**: `(days_since_joining / 14) × bi_weekly_rent`
- **Due Status**: Shows as "DUE" if in last 3 days of the bi-weekly period
- **Overdue Status**: Marked as overdue if 14+ days have elapsed
- **Example**:
  - Resident joins on May 10, bi-weekly rent = $700
  - On May 24 (14 days later): Due amount = $700 (OVERDUE)

### MONTHLY Rent Type

- **Expected Amount**: `complete_months_since_joining × monthly_rent`
  - Only counts COMPLETE calendar months (current month NOT included)
  - Uses `preferred_billing_day` if set, otherwise uses `joining_date.day`
- **Due Status**: Shows between 5 days before and 1 day after billing date
- **Overdue Status**: Marked as overdue after a complete calendar month has passed without payment
- **Example**:
  - Resident joins on May 10, monthly rent = $5000
  - On May 31 (within 1 month): Due amount = $0 (not yet complete month)
  - On June 10 (1+ complete months): Due amount = $5000 (DUE/OVERDUE depending on payment)
  - On July 5 (approaching next month): Due amount shows for next month

## API Response Examples

### Daily Resident - 1 Day Overdue

```json
{
  "id": 42,
  "first_name": "Raj",
  "last_name": "Kumar",
  "rent_type": "daily",
  "rent": "500.00",
  "joining_date": "2026-05-15",
  "due": "500.00",
  "arrears": "0.00",
  "details": {
    "due_amount": "500.00",
    "days_overdue": 1,
    "expected_from": "2026-05-15 to 2026-05-16"
  }
}
```

### Monthly Resident - 2 Months Overdue

```json
{
  "id": 43,
  "first_name": "Priya",
  "last_name": "Singh",
  "rent_type": "monthly",
  "rent": "15000.00",
  "joining_date": "2026-03-01",
  "preferred_billing_day": 1,
  "due": "30000.00",
  "arrears": "0.00",
  "details": {
    "due_amount": "30000.00",
    "months_overdue": 2,
    "expected_for_periods": "March, April 2026"
  }
}
```

## Benefits

1. **Reduced Client Logic** - Mobile app no longer needs to calculate due amounts
2. **Consistency** - All clients receive the same calculations
3. **Accuracy** - Single source of truth for payment calculations
4. **Flexibility** - Easy to adjust calculations without updating all clients
5. **Better UX** - Mobile app can focus on display, not calculation logic
6. **Single Pass** - All data (resident + payments + due amount) in one API response

## Migration Guide

### For Mobile App Developers

Instead of:
1. Getting resident data
2. Getting payment history
3. Manually calculating due amount

Now:
1. Call `home_summary` endpoint to get all due/overdue residents with amounts pre-calculated
2. Or call individual resident endpoint where `due` field contains the calculated amount
3. Focus UI logic on formatting and display

### API Calls

**Get all overdue and due residents:**
```
GET /api/properties/1/home_summary/
```

**Get a specific resident with due amount:**
```
GET /api/residents/42/
```

Response includes:
```json
{
  "id": 42,
  "first_name": "Raj",
  "due": "500.00",  // <-- Pre-calculated
  ...
}
```

## Testing Scenarios

### Test Case 1: Daily Resident - 1 Day Overdue
- Resident: Daily payment, $50/day
- Joining date: Today - 1 day
- Payments: None
- Expected due: $50 (marked as OVERDUE)

### Test Case 2: Daily Resident - Same Day
- Resident: Daily payment, $50/day
- Joining date: Today
- Payments: None
- Expected due: $50 (marked as DUE)

### Test Case 3: Monthly Resident - No Due Yet
- Resident: Monthly payment, $5000/month
- Joining date: Today
- Payments: None
- Expected due: $0 (until end of month)

### Test Case 4: Monthly Resident - 1+ Months Overdue
- Resident: Monthly payment, $5000/month
- Joining date: 60 days ago
- Payments: None
- Expected due: $10000 (2 complete months)

## Database Queries

The calculation uses efficient queries:
- Single SELECT for resident data
- Single aggregation query for total payments
- No N+1 query issues
- Indexed by `resident_id`, `payment_date` for quick lookups

## Dependencies

- Django ORM (already in use)
- Python Decimal (for accurate financial calculations)
- datetime utilities
- calendar module (part of stdlib)

No new external dependencies added.

## Performance Considerations

- Calculations are CPU-bound, not I/O-bound
- Results can be cached at the API level if needed
- For bulk operations, consider QuerySet.bulk_create() optimization
- home_summary endpoint retrieved in O(n) where n = active residents

## Future Enhancements

1. Add `_between_dates()` parameter to calculate due for any date range
2. Implement due payment reminders based on `next_billing_date()`
3. Add payment plan support (e.g., installment payments)
4. Extend to support custom billing cycles
5. Add audit trail for due amount changes
