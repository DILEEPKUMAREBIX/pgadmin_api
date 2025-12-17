# API Usage Examples

## Base URL
```
http://localhost:8000/api/v1/
```

## Authentication
Currently configured for Token-based or Session authentication. Add to requests:
```
Authorization: Token YOUR_AUTH_TOKEN
```

## Examples Using cURL

### Properties

#### List all properties
```bash
curl http://localhost:8000/api/v1/properties/
```

#### Get property with ID 1
```bash
curl http://localhost:8000/api/v1/properties/1/
```

#### Get property summary
```bash
curl http://localhost:8000/api/v1/properties/1/summary/
```

#### Create a new property
```bash
curl -X POST http://localhost:8000/api/v1/properties/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Residency",
    "address": "789 New Street",
    "city": "Mumbai",
    "state": "MH",
    "zip_code": "400001",
    "floors_count": 3,
    "rooms_per_floor": 4,
    "beds_per_room": 2,
    "description": "Premium residential complex"
  }'
```

### Residents

#### List all residents
```bash
curl http://localhost:8000/api/v1/residents/
```

#### Search residents by name
```bash
curl http://localhost:8000/api/v1/residents/?search=John
```

#### Filter residents by property
```bash
curl http://localhost:8000/api/v1/residents/?property=1
```

#### Get residents with payment due soon
```bash
curl http://localhost:8000/api/v1/residents/due_soon/
```

#### Get residents with overdue payments
```bash
curl http://localhost:8000/api/v1/residents/overdue/
```

#### Create new resident
```bash
curl -X POST http://localhost:8000/api/v1/residents/ \
  -H "Content-Type: application/json" \
  -d '{
    "property": 1,
    "name": "John Doe",
    "gender": "M",
    "email": "john@example.com",
    "mobile": "9876543210",
    "rent": 5000.00,
    "rent_type": "monthly",
    "joining_date": "2024-01-15",
    "next_pay_date": "2024-02-15"
  }'
```

#### Update resident
```bash
curl -X PATCH http://localhost:8000/api/v1/residents/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "next_pay_date": "2024-02-15",
    "notes": "Updated contact details"
  }'
```

### Occupancy

#### List all occupancy records
```bash
curl http://localhost:8000/api/v1/occupancy/
```

#### Get occupied beds
```bash
curl http://localhost:8000/api/v1/occupancy/occupied/
```

#### Get available beds
```bash
curl http://localhost:8000/api/v1/occupancy/available/
```

#### Filter by property
```bash
curl http://localhost:8000/api/v1/occupancy/?property=1
```

#### Create occupancy record
```bash
curl -X POST http://localhost:8000/api/v1/occupancy/ \
  -H "Content-Type: application/json" \
  -d '{
    "property": 1,
    "floor": 1,
    "room": 1,
    "bed": 1,
    "resident": 1,
    "is_occupied": true,
    "occupied_since": "2024-01-15"
  }'
```

### Expenses

#### List all expenses
```bash
curl http://localhost:8000/api/v1/expenses/
```

#### Filter expenses by category
```bash
curl http://localhost:8000/api/v1/expenses/?category=Electricity
```

#### Filter by payment method
```bash
curl http://localhost:8000/api/v1/expenses/?payment_method=bank_transfer
```

#### Get expense summary
```bash
curl http://localhost:8000/api/v1/expenses/summary/
```

#### Get expenses grouped by category
```bash
curl http://localhost:8000/api/v1/expenses/by_category/
```

#### Create new expense
```bash
curl -X POST http://localhost:8000/api/v1/expenses/ \
  -H "Content-Type: application/json" \
  -d '{
    "property": 1,
    "amount": 1200.00,
    "category": "Electricity",
    "description": "Monthly electricity bill",
    "expense_date": "2024-01-15T00:00:00Z",
    "paid_by": "Manager",
    "payment_method": "bank_transfer"
  }'
```

### Payments

#### List all payments
```bash
curl http://localhost:8000/api/v1/payments/
```

#### Filter payments by resident
```bash
curl http://localhost:8000/api/v1/payments/?resident=1
```

#### Get payment summary
```bash
curl http://localhost:8000/api/v1/payments/summary/
```

#### Get payments for specific resident
```bash
curl http://localhost:8000/api/v1/payments/by_resident/?resident_id=1
```

#### Record new payment
```bash
curl -X POST http://localhost:8000/api/v1/payments/ \
  -H "Content-Type: application/json" \
  -d '{
    "property": 1,
    "resident": 1,
    "resident_name": "John Doe",
    "amount": 5000.00,
    "payment_method": "bank_transfer",
    "reference_number": "TXN123456"
  }'
```

### Maintenance Requests

#### List all maintenance requests
```bash
curl http://localhost:8000/api/v1/maintenance-requests/
```

#### Filter by status
```bash
curl http://localhost:8000/api/v1/maintenance-requests/?status=open
```

#### Filter by priority
```bash
curl http://localhost:8000/api/v1/maintenance-requests/?priority=high
```

#### Get open maintenance requests
```bash
curl http://localhost:8000/api/v1/maintenance-requests/open_requests/
```

#### Get requests by priority
```bash
curl http://localhost:8000/api/v1/maintenance-requests/by_priority/
```

#### Create maintenance request
```bash
curl -X POST http://localhost:8000/api/v1/maintenance-requests/ \
  -H "Content-Type: application/json" \
  -d '{
    "property": 1,
    "resident": 1,
    "category": "Electrical",
    "description": "Broken light in room 101",
    "priority": "high",
    "status": "open",
    "estimated_cost": 200.00
  }'
```

#### Mark request as resolved
```bash
curl -X POST http://localhost:8000/api/v1/maintenance-requests/1/resolve/ \
  -H "Content-Type: application/json"
```

### Floors, Rooms, Beds

#### List floors for property
```bash
curl http://localhost:8000/api/v1/floors/?property=1
```

#### List rooms for floor
```bash
curl http://localhost:8000/api/v1/rooms/?floor=1
```

#### Get available beds
```bash
curl http://localhost:8000/api/v1/beds/available/
```

#### Create floor
```bash
curl -X POST http://localhost:8000/api/v1/floors/ \
  -H "Content-Type: application/json" \
  -d '{
    "property": 1,
    "floor_level": 1,
    "floor_name": "Ground Floor"
  }'
```

#### Create room
```bash
curl -X POST http://localhost:8000/api/v1/rooms/ \
  -H "Content-Type: application/json" \
  -d '{
    "floor": 1,
    "property": 1,
    "room_number": "101",
    "room_name": "Room A",
    "total_beds": 3,
    "room_type": "triple",
    "capacity": 3
  }'
```

#### Create bed
```bash
curl -X POST http://localhost:8000/api/v1/beds/ \
  -H "Content-Type: application/json" \
  -d '{
    "room": 1,
    "floor": 1,
    "property": 1,
    "bed_number": "101A",
    "bed_name": "Bed 1A"
  }'
```

### Occupancy History

#### Get all occupancy changes
```bash
curl http://localhost:8000/api/v1/occupancy-history/
```

#### Get changes for specific resident
```bash
curl http://localhost:8000/api/v1/occupancy-history/?resident_id=1
```

#### Get occupied status changes
```bash
curl http://localhost:8000/api/v1/occupancy-history/?action=occupied
```

### Users

#### List all users
```bash
curl http://localhost:8000/api/v1/users/
```

#### Filter by role
```bash
curl http://localhost:8000/api/v1/users/?role=manager
```

#### Get active users
```bash
curl http://localhost:8000/api/v1/users/?is_active=true
```

#### Create new user
```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password_hash": "hashed_password",
    "role": "staff",
    "property": 1
  }'
```

## Query Parameters

### Filtering
```
?field=value
?property=1&is_active=true
```

### Searching
```
?search=John
?search=room101
```

### Ordering
```
?ordering=created_at
?ordering=-created_at  (descending)
?ordering=name,-created_at  (multiple)
```

### Pagination
```
?page=1&page_size=20
```

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 204 | No Content - Successful deletion |
| 400 | Bad Request - Invalid data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Permission denied |
| 404 | Not Found - Resource not found |
| 500 | Server Error |

## Response Format

### Success Response (200)
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "mobile": "9876543210",
  "property": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### List Response (200)
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/v1/residents/?page=2",
  "previous": null,
  "results": [
    {...},
    {...}
  ]
}
```

### Error Response (400)
```json
{
  "error": "Field is required",
  "field": ["This field is required"]
}
```

## JavaScript Examples

### Fetch Residents
```javascript
fetch('http://localhost:8000/api/v1/residents/')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

### Create Resident (async/await)
```javascript
async function createResident() {
  const response = await fetch('http://localhost:8000/api/v1/residents/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      property: 1,
      name: 'Jane Doe',
      email: 'jane@example.com',
      mobile: '9876543211',
      rent: 5000,
      rent_type: 'monthly',
      joining_date: '2024-01-15',
      next_pay_date: '2024-02-15'
    })
  });
  
  const data = await response.json();
  console.log(data);
}
```

### Get Residents Due Soon
```javascript
async function getResidentsDueSoon() {
  try {
    const response = await fetch('http://localhost:8000/api/v1/residents/due_soon/');
    const residents = await response.json();
    console.log(residents);
  } catch (error) {
    console.error('Error:', error);
  }
}
```

## Swagger Documentation

Access the interactive API documentation at:
```
http://localhost:8000/api/docs/
```

This provides:
- Browse all endpoints
- View request/response schemas
- Test endpoints directly
- Automatic documentation

---

**Happy coding! Start using the API to build amazing features for your PG Admin application.**
