"""
API QUICK REFERENCE - Due Amount Calculations
================================================

This document provides quick API reference examples for the new due calculation system.
"""

# ENDPOINT 1: Get all due and overdue residents for a property
# ============================================================
GET /api/properties/1/home_summary/

RESPONSE:
{
  "property": {
    "id": 1,
    "name": "PG Downtown"
  },
  "occupied_beds": 18,
  "available_beds": 32,
  "overdue": {
    "count": 3,
    "total_amount": "15000.00",
    "details": [
      {
        "id": 10,
        "first_name": "Rajesh",
        "last_name": "Kumar",
        "gender": "Male",
        "email": "rajesh@example.com",
        "mobile": "9876543210",
        "dob": "1995-03-15",
        "rent": "5000.00",
        "rent_type": "monthly",
        "joining_date": "2026-02-01",
        "move_out_date": null,
        "preferred_billing_day": 1,
        "arrears": "0.00",
        "due": "5000.00",
        "due_amount": "5000.00",
        "current_floor": "Floor 2",
        "current_room": "Room 201",
        "current_bed": "Bed A"
      },
      {
        "id": 11,
        "first_name": "Priya",
        "last_name": "Singh",
        "gender": "Female",
        "email": "priya@example.com",
        "mobile": "9876543211",
        "dob": "1996-07-20",
        "rent": "5000.00",
        "rent_type": "monthly",
        "joining_date": "2026-01-15",
        "move_out_date": null,
        "preferred_billing_day": 15,
        "arrears": "0.00",
        "due": "10000.00",
        "due_amount": "10000.00",
        "current_floor": "Floor 3",
        "current_room": "Room 302",
        "current_bed": "Bed B"
      },
      {
        "id": 12,
        "first_name": "Amit",
        "last_name": "Patel",
        "gender": "Male",
        "email": "amit@example.com",
        "mobile": "9876543212",
        "dob": "1994-11-08",
        "rent": "500.00",
        "rent_type": "daily",
        "joining_date": "2026-05-14",
        "move_out_date": null,
        "arrears": "0.00",
        "due": "1000.00",
        "due_amount": "1000.00",
        "current_floor": "Floor 1",
        "current_room": "Room 105",
        "current_bed": "Bed A"
      }
    ]
  },
  "due": {
    "count": 2,
    "total_amount": "2500.00",
    "details": [
      {
        "id": 13,
        "first_name": "Sarah",
        "last_name": "Johnson",
        "gender": "Female",
        "email": "sarah@example.com",
        "mobile": "9876543213",
        "dob": "1997-02-14",
        "rent": "500.00",
        "rent_type": "daily",
        "joining_date": "2026-05-16",
        "move_out_date": null,
        "arrears": "0.00",
        "due": "500.00",
        "due_amount": "500.00",
        "current_floor": "Floor 2",
        "current_room": "Room 204",
        "current_bed": "Bed C"
      },
      {
        "id": 14,
        "first_name": "David",
        "last_name": "Lee",
        "gender": "Male",
        "email": "david@example.com",
        "mobile": "9876543214",
        "dob": "1993-08-25",
        "rent": "4000.00",
        "rent_type": "monthly",
        "joining_date": "2026-04-10",
        "move_out_date": null,
        "preferred_billing_day": 10,
        "arrears": "0.00",
        "due": "2000.00",
        "due_amount": "2000.00",
        "current_floor": "Floor 3",
        "current_room": "Room 301",
        "current_bed": "Bed D"
      }
    ]
  }
}

---

# ENDPOINT 2: Get single resident with due amount
# ================================================
GET /api/residents/10/

RESPONSE:
{
  "id": 10,
  "property": 1,
  "property_name": "PG Downtown",
  "first_name": "Rajesh",
  "last_name": "Kumar",
  "name": "Rajesh Kumar",
  "gender": "Male",
  "email": "rajesh@example.com",
  "mobile": "9876543210",
  "dob": "1995-03-15",
  "address": "123 Main St, City",
  "rent": "5000.00",
  "rent_type": "monthly",
  "joining_date": "2026-02-01",
  "move_out_date": null,
  "preferred_billing_day": 1,
  "photo_url": "https://example.com/photos/rajesh.jpg",
  "aadhar_url": "https://example.com/aadhar/rajesh.jpg",
  "vehicle_2wheeler": "DL01AB1234",
  "vehicle_4wheeler": null,
  "current_floor": "Floor 2",
  "current_floor_number": 2,
  "current_room": "Room 201",
  "current_room_number": "201",
  "current_bed": "Bed A",
  "current_bed_number": "A",
  "arrears": "0.00",
  "due": "5000.00",
  "payments": [
    {
      "id": 25,
      "amount": "5000.00",
      "payment_date": "2026-02-15",
      "payment_method": "bank_transfer",
      "reference_number": "TRF123456",
      "notes": "Monthly rent - February"
    },
    {
      "id": 26,
      "amount": "5000.00",
      "payment_date": "2026-03-01",
      "payment_method": "bank_transfer",
      "reference_number": "TRF123457",
      "notes": "Monthly rent - March"
    }
  ],
  "is_active": true,
  "created_at": "2026-02-01T10:30:00Z",
  "updated_at": "2026-05-16T14:22:00Z"
}

---

# ENDPOINT 3: List residents (filtered by property)
# ==================================================
GET /api/residents/?property=1

RESPONSE (Array of residents with due field):
[
  {
    "id": 10,
    "first_name": "Rajesh",
    "last_name": "Kumar",
    "rent_type": "monthly",
    "rent": "5000.00",
    "due": "5000.00",
    "arrears": "0.00",
    ...
  },
  {
    "id": 11,
    "first_name": "Priya",
    "last_name": "Singh",
    "rent_type": "monthly",
    "rent": "5000.00",
    "due": "10000.00",
    "arrears": "0.00",
    ...
  },
  {
    "id": 12,
    "first_name": "Amit",
    "last_name": "Patel",
    "rent_type": "daily",
    "rent": "500.00",
    "due": "1000.00",
    "arrears": "0.00",
    ...
  }
]

---

# USAGE EXAMPLES IN MOBILE APP (React Native / Flutter)
# ======================================================

// 1. Get all overdue and due customers
fetch('http://api.example.com/api/properties/1/home_summary/')
  .then(res => res.json())
  .then(data => {
    console.log('Overdue count:', data.overdue.count);
    console.log('Total overdue amount:', data.overdue.total_amount);
    console.log('Due count:', data.due.count);
    
    // Display overdue residents
    data.overdue.details.forEach(resident => {
      console.log(`${resident.first_name} - Due: ${resident.due_amount}`);
    });
    
    // Display due residents
    data.due.details.forEach(resident => {
      console.log(`${resident.first_name} - Due: ${resident.due_amount}`);
    });
  });

// 2. Get specific resident with due amount
fetch('http://api.example.com/api/residents/10/')
  .then(res => res.json())
  .then(resident => {
    // Amount is pre-calculated by backend
    console.log(`${resident.first_name}'s due amount: ${resident.due}`);
    
    // No need for client-side calculation!
    // Just display it:
    showDueAmount(resident.due);
  });

// 3. Filter residents by property
fetch('http://api.example.com/api/residents/?property=1')
  .then(res => res.json())
  .then(residents => {
    residents.forEach(r => {
      if (parseFloat(r.due) > 0) {
        console.log(`${r.first_name} has due: ${r.due}`);
      }
    });
  });

---

# CALCULATION EXAMPLES
# ====================

## DAILY RENT CALCULATION

Example 1: Resident joined May 15 with $500/day rent
- Join date: May 15, 2026
- Today: May 16, 2026 (1 day later)
- No payments made
- Expected rent: 2 days × $500 = $1,000
- Payments: $0
- Due Amount: $1,000
- Status: OVERDUE (1+ days passed)

Example 2: Same resident but joined this morning
- Join date: May 16, 2026
- Today: May 16, 2026 (same day)
- No payments made
- Expected rent: 1 day × $500 = $500
- Payments: $0
- Due Amount: $500
- Status: DUE (today counted)
- NOT YET OVERDUE

Example 3: Resident with partial payment
- Join date: May 10, 2026
- Today: May 16, 2026
- Days elapsed: 7 days
- Expected rent: 7 days × $500 = $3,500
- Payments made: $2,500 (on May 13)
- Due Amount: $3,500 - $2,500 = $1,000
- Status: OVERDUE

## MONTHLY RENT CALCULATION

Example 1: Resident joined Feb 1 with $5,000/month
- Join date: Feb 1, 2026
- Today: May 16, 2026
- Expected months: February (complete) + March (complete) + April (complete) = 3 months
- Expected rent: 3 × $5,000 = $15,000
- Payments made: $10,000 (Feb $5,000, Mar $5,000)
- Due Amount: $15,000 - $10,000 = $5,000
- Status: OVERDUE (April payment pending)

Example 2: Just joined this month
- Join date: May 16, 2026
- Today: May 16, 2026
- Expected months: 0 (current month doesn't count yet)
- Expected rent: 0 × $5,000 = $0
- Due Amount: $0
- Status: NOT DUE YET

## WEEKLY RENT CALCULATION

Example: Resident joined May 10 with $350/week
- Join date: May 10, 2026 (Saturday)
- Today: May 16, 2026 (Friday - 6 days later)
- Daily rate: $350 / 7 = $50/day
- Expected rent: 7 days × $50 = $350
- Payments: $0
- Due Amount: $350
- Status: DUE (approaching payment date)
- NOT YET OVERDUE (exactly 7 days needed)

---

# ERROR HANDLING
# ==============

If resident has no joining_date:
- Due Amount: Shows only arrears

If resident is inactive:
- Due Amount: Shows only arrears (no new accumulation)

If resident has move_out_date in past:
- Due Amount: Calculated up to move_out_date only

If no payments records exist:
- Due Amount: Calculates as if no payments made

---

# SORTING & FILTERING
# ====================

Sort by due amount (highest first):
GET /api/properties/1/home_summary/
results.overdue.details.sort((a, b) => 
  parseFloat(b.due_amount) - parseFloat(a.due_amount)
)

Filter only DAILY rent residents with due:
GET /api/properties/1/home_summary/
daily_residents = results.overdue.details.filter(r => r.rent_type === 'daily')

Filter only residents with arrears:
GET /api/residents/?property=1&arrears__gt=0

---

# TESTING CHECKLIST
# ==================

Test Cases to Verify:
□ Daily rent: 1 day overdue calculation
□ Daily rent: Same day joining calculation
□ Daily rent: Multiple days with partial payment
□ Weekly rent: Within same week
□ Weekly rent: 7+ days calculation
□ Bi-weekly rent: 14+ days calculation
□ Monthly rent: Same month joining
□ Monthly rent: Full month overdue
□ Monthly rent: Multiple months overdue
□ Arrears: Included in total due
□ Inactive resident: Only arrears shown
□ Moved out resident: Calculated till move-out date
□ Partial payments: Reduce due amount
□ Zero payments: Full due shown

All tests should pass before deploying to production.
