## Residents API - Enhanced with Payment Details ✅

The Residents API now includes complete payment and due information inline, eliminating the need for separate payments API calls.

---

## New Fields Added to Resident Serializer

| Field | Type | Description |
|-------|------|-------------|
| `due` | string (decimal) | Total due amount (existing, already included) |
| `arrears` | string (decimal) | Previous unpaid amounts (existing, already included) |
| **`is_overdue`** | boolean | **NEW:** Whether resident payment is overdue |
| **`overdue_amount`** | string (decimal) | **NEW:** Only the overdue portion of `due` |
| **`next_payment_date`** | date (ISO) | **NEW:** Next billing/payment date (e.g., "2026-06-02") |
| **`days_overdue`** | integer | **NEW:** Number of days past due (0 if not overdue) |
| **`payment_status`** | string | **NEW:** Status: ON_TIME \| DUE_SOON \| OVERDUE \| SEVERELY_OVERDUE |

---

## API Response Examples

### GET /api/residents/65/ - MANIKANTA (Monthly with Arrears)

```json
{
  "id": 65,
  "first_name": "MANIKANTA",
  "last_name": "TANGUDU",
  "name": "MANIKANTA TANGUDU",
  "mobile": "7702783047",
  "email": "manikantajoy.tangudu@gmail.com",
  "rent": "10000.00",
  "rent_type": "monthly",
  "joining_date": "2026-05-16",
  "preferred_billing_day": 2,
  "address": "Koppara, Srikakulam, 535557",
  
  // Current occupancy
  "current_floor": 3,
  "current_floor_number": 3,
  "current_room": 11,
  "current_room_number": "303",
  "current_bed": 17,
  "current_bed_number": "2",
  
  // PAYMENT & DUE INFORMATION (COMPLETE - No separate API call needed!)
  "arrears": "5000.00",                    // Had previous unpaid amount
  "due": "5000.00",                        // Total due = arrears
  
  // NEW FIELDS FOR PAYMENT STATUS
  "is_overdue": false,                     // Not yet overdue (only 1 day)
  "overdue_amount": "0.00",                // No overdue yet, just arrears
  "next_payment_date": "2026-06-02",       // Next billing on June 2
  "days_overdue": 0,                       // Not overdue
  "payment_status": "DUE_SOON",            // Has arrears to pay + upcoming billing
  
  // Payment history (no separate call needed)
  "payments": [],                          // No payments made yet
  
  "is_active": true,
  "created_at": "2026-05-16T03:46:28Z",
  "updated_at": "2026-05-16T10:05:37Z"
}
```

---

### GET /api/residents/63/ - Test Delete (Daily - 23 Days Overdue)

```json
{
  "id": 63,
  "first_name": "Test",
  "last_name": "Delete",
  "name": "Test Delete",
  "mobile": "9807564615",
  "rent": "1500.00",
  "rent_type": "daily",
  "joining_date": "2026-04-24",
  "address": "Hyderabad",
  
  "current_floor": 3,
  "current_floor_number": 3,
  "current_room": 11,
  "current_room_number": "303",
  "current_bed": 17,
  "current_bed_number": "2",
  
  // PAYMENT STATUS
  "arrears": "0.00",
  "due": "34500.00",                       // 23 days × $1,500/day
  
  "is_overdue": true,                      // YES - 23 days overdue
  "overdue_amount": "34500.00",            // All of it is overdue
  "next_payment_date": "2026-05-17",       // Next payment was already due
  "days_overdue": 23,                      // 23 days late!
  "payment_status": "SEVERELY_OVERDUE",    // Very late payment
  
  "payments": [],                          // No payments
  
  "is_active": true,
  "created_at": "2026-05-09T07:08:03Z",
  "updated_at": "2026-05-09T07:08:03Z"
}
```

---

### GET /api/residents/62/ - San Latest (Monthly - 2+ Months Overdue)

```json
{
  "id": 62,
  "first_name": "San",
  "last_name": "Latest",
  "name": "San Latest",
  "mobile": "1234567890",
  "email": "sandeepreddy8523@gmail.com",
  "rent": "9000.00",
  "rent_type": "monthly",
  "joining_date": "2026-03-01",
  "preferred_billing_day": 4,
  "address": "Test Hayathnagar",
  
  "current_floor": null,
  "current_room": null,
  "current_bed": null,
  
  // PAYMENT STATUS
  "arrears": "0.00",
  "due": "18000.00",                       // 2 complete months × $9,000
                                          // (March = complete, April = complete, May not counted yet)
  
  "is_overdue": true,                      // YES - months 1-2 unpaid
  "overdue_amount": "18000.00",            // All due is overdue
  "next_payment_date": "2026-06-04",       // June 4 (next billing)
  "days_overdue": 44,                      // ~44 days overdue
  "payment_status": "SEVERELY_OVERDUE",    // Multiple months late
  
  "payments": []
}
```

---

### GET /api/residents/58/ - Vasavi K (Monthly - Recently Due)

```json
{
  "id": 58,
  "first_name": "Vasavi",
  "last_name": "K",
  "name": "Vasavi K",
  "mobile": "8309970138",
  "rent": "10000.00",
  "rent_type": "monthly",
  "joining_date": "2026-04-01",
  "preferred_billing_day": 1,
  "address": "Hyderabad",
  
  // PAYMENT STATUS
  "arrears": "0.00",
  "due": "10000.00",                       // 1 complete month (April)
  
  "is_overdue": true,                      // YES - April passed without payment
  "overdue_amount": "10000.00",            // All is overdue (April rent)
  "next_payment_date": "2026-05-01",       // Today (May 1)! Was already due
  "days_overdue": 16,                      // ~16 days over
  "payment_status": "OVERDUE",             // Recently overdue
  
  "payments": []
}
```

---

## Mobile App Usage - No More Separate Calls!

### Old Way (Multiple API Calls):
```javascript
// 1. Get resident
const resident = await fetch('/api/residents/65/')

// 2. Get their payments (EXTRA CALL)
const payments = await fetch('/api/residents/65/payments/')

// 3. Manually calculate due, overdue, next payment date (CLIENT-SIDE LOGIC)
// ... complicated calculations ...

// 4. Show UI with calculated values
```

### New Way (Single API Call):
```javascript
// 1. Get resident - COMPLETE WITH EVERYTHING
const resident = await fetch('/api/residents/65/')

// Response already has:
// - due: "5000.00"
// - is_overdue: false
// - overdue_amount: "0.00"
// - next_payment_date: "2026-06-02"
// - days_overdue: 0
// - payment_status: "DUE_SOON"
// - payments: [...]

// 2. Directly use the values in UI
console.log(`Due: ${resident.due}`)
console.log(`Status: ${resident.payment_status}`)
console.log(`Next Payment: ${resident.next_payment_date}`)
```

---

## Payment Status Meanings

| Status | Condition | Example |
|--------|-----------|---------|
| **ON_TIME** | No due amount | Resident joined today, no billing yet |
| **DUE_SOON** | Has due but not overdue | Has arrears or billing approaching |
| **OVERDUE** | Payment past due | 1-2 days for daily, 1+ month for monthly |
| **SEVERELY_OVERDUE** | Very late payment | 3+ days for daily, 30+ days for monthly |

---

## List Residents with Payment Details

### GET /api/residents/?property=1

```json
[
  {
    "id": 65,
    "first_name": "MANIKANTA",
    "rent_type": "monthly",
    "due": "5000.00",
    "is_overdue": false,
    "overdue_amount": "0.00",
    "next_payment_date": "2026-06-02",
    "payment_status": "DUE_SOON",
    ...
  },
  {
    "id": 63,
    "first_name": "Test",
    "rent_type": "daily",
    "due": "34500.00",
    "is_overdue": true,
    "overdue_amount": "34500.00",
    "next_payment_date": "2026-05-17",
    "days_overdue": 23,
    "payment_status": "SEVERELY_OVERDUE",
    ...
  },
  ...
]
```

---

## Filtering by Payment Status (Optional Frontend Logic)

```javascript
// Get all residents
const residents = await fetch('/api/residents/?property=1')

// Filter by status
const overdue = residents.filter(r => r.is_overdue)
const dueRecently = residents.filter(r => r.next_payment_date === today)
const severely = residents.filter(r => r.payment_status === 'SEVERELY_OVERDUE')
```

---

## Backend Calculation Details

All calculations use the centralized `payment_utils` module:

### Fields Calculated From:
- **`due`** → `calculate_due_amount()` - considers rent type, payments, arrears
- **`is_overdue`** → `is_overdue()` - checks if payment period passed
- **`overdue_amount`** → `get_overdue_amount()` - only overdue portion
- **`next_payment_date`** → `next_billing_date()` - when next payment due
- **`days_overdue`** → `get_days_overdue()` - how many days late
- **`payment_status`** → Custom logic combining above fields

### Rent Type Thresholds:
| Rent Type | Overdue After | Example |
|-----------|---------------|---------|
| Daily | 3+ days | Joined May 14, today May 17 = overdue |
| Weekly | 7+ days | Joined May 10, today May 17 = overdue |
| Bi-weekly | 14+ days | Joined May 3, today May 17 = overdue |
| Monthly | 1+ complete months | Joined April 1, today May 17 = 1 month overdue |

---

## Summary: All-In-One Resident Details

Every resident endpoint now returns complete payment information:

✅ **Current due amount**
✅ **Overdue status & amount**
✅ **Next payment date** (no more double-checking)
✅ **Days overdue**
✅ **Human-readable payment status**
✅ **Payment history**
✅ **Arrears**

**No additional API calls needed!** 🎉
