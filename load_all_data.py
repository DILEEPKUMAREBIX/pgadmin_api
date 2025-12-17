import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pgadmin_config.settings')
django.setup()

from properties.models import (
    Property, Floor, Room, Bed, Resident, Occupancy, 
    OccupancyHistory, Expense, Payment, MaintenanceRequest, User
)

# Clear existing data
print("🗑️  Clearing existing data...")
Property.objects.all().delete()

print("\n" + "="*80)
print("LOADING SAMPLE DATA TO ALL PROPERTIES_* TABLES")
print("="*80 + "\n")

# ============================================================================
# 1. CREATE SAMPLE PROPERTIES
# ============================================================================
print("1️⃣  Creating Properties...")
property1 = Property.objects.create(
    name="Sunrise Apartments",
    address="123 Main Street, Downtown",
    city="New York",
    state="NY",
    zip_code="10001",
    floors_count=3,
    rooms_per_floor=4,
    beds_per_room=1,
    description="Modern apartment complex in downtown area"
)
print(f"   ✓ Created: {property1.name} ({property1.total_beds} total beds)")

property2 = Property.objects.create(
    name="Greenfield Housing",
    address="456 Oak Avenue, Suburbs",
    city="Los Angeles",
    state="CA",
    zip_code="90001",
    floors_count=2,
    rooms_per_floor=4,
    beds_per_room=1,
    description="Suburban housing community with green spaces"
)
print(f"   ✓ Created: {property2.name} ({property2.total_beds} total beds)")

# ============================================================================
# 2. CREATE FLOORS
# ============================================================================
print("\n2️⃣  Creating Floors...")
floor1_p1 = Floor.objects.create(property=property1, floor_level=1, floor_name="Ground Floor")
floor2_p1 = Floor.objects.create(property=property1, floor_level=2, floor_name="First Floor")
floor3_p1 = Floor.objects.create(property=property1, floor_level=3, floor_name="Second Floor")

floor1_p2 = Floor.objects.create(property=property2, floor_level=1, floor_name="Ground Floor")
floor2_p2 = Floor.objects.create(property=property2, floor_level=2, floor_name="First Floor")

print(f"   ✓ Created 5 floors across 2 properties")

# ============================================================================
# 3. CREATE ROOMS
# ============================================================================
print("\n3️⃣  Creating Rooms...")
rooms = []

# Property 1 - Floor 1
for i in range(1, 5):
    room = Room.objects.create(
        floor=floor1_p1,
        property=property1,
        room_number=f"101{i}",
        room_type="single" if i % 2 == 0 else "double",
        total_beds=1 if i % 2 == 0 else 2,
        capacity=1 if i % 2 == 0 else 2
    )
    rooms.append(room)

# Property 1 - Floor 2
for i in range(1, 5):
    room = Room.objects.create(
        floor=floor2_p1,
        property=property1,
        room_number=f"202{i}",
        room_type="single" if i % 2 == 0 else "double",
        total_beds=1 if i % 2 == 0 else 2,
        capacity=1 if i % 2 == 0 else 2
    )
    rooms.append(room)

# Property 1 - Floor 3
for i in range(1, 5):
    room = Room.objects.create(
        floor=floor3_p1,
        property=property1,
        room_number=f"303{i}",
        room_type="single" if i % 2 == 0 else "double",
        total_beds=1 if i % 2 == 0 else 2,
        capacity=1 if i % 2 == 0 else 2
    )
    rooms.append(room)

# Property 2 - Floor 1
for i in range(1, 5):
    room = Room.objects.create(
        floor=floor1_p2,
        property=property2,
        room_number=f"101{i}",
        room_type="single" if i % 2 == 0 else "double",
        total_beds=1 if i % 2 == 0 else 2,
        capacity=1 if i % 2 == 0 else 2
    )
    rooms.append(room)

# Property 2 - Floor 2
for i in range(1, 5):
    room = Room.objects.create(
        floor=floor2_p2,
        property=property2,
        room_number=f"202{i}",
        room_type="single" if i % 2 == 0 else "double",
        total_beds=1 if i % 2 == 0 else 2,
        capacity=1 if i % 2 == 0 else 2
    )
    rooms.append(room)

print(f"   ✓ Created {len(rooms)} rooms across all floors")

# ============================================================================
# 4. CREATE BEDS
# ============================================================================
print("\n4️⃣  Creating Beds...")
beds = []
bed_count = 0
for room in rooms:
    for i in range(1, room.total_beds + 1):
        bed = Bed.objects.create(
            room=room,
            floor=room.floor,
            property=room.property,
            bed_number=str(i),
            bed_name=f"Room {room.room_number} - Bed {i}"
        )
        beds.append(bed)
        bed_count += 1

print(f"   ✓ Created {bed_count} beds across all rooms")

# ============================================================================
# 5. CREATE RESIDENTS
# ============================================================================
print("\n5️⃣  Creating Residents...")
today = datetime.now().date()

resident1 = Resident.objects.create(
    property=property1,
    name="Michael Brown",
    gender="Male",
    email="michael.brown@email.com",
    mobile="555-1001",
    dob=today - timedelta(days=365*30),
    rent=800.00,
    rent_type="monthly",
    joining_date=today - timedelta(days=90),
    next_pay_date=today + timedelta(days=5)
)
print(f"   ✓ Created: {resident1.name}")

resident2 = Resident.objects.create(
    property=property1,
    name="Emily Davis",
    gender="Female",
    email="emily.davis@email.com",
    mobile="555-1002",
    rent=1200.00,
    rent_type="monthly",
    joining_date=today - timedelta(days=60),
    next_pay_date=today + timedelta(days=10)
)
print(f"   ✓ Created: {resident2.name}")

resident3 = Resident.objects.create(
    property=property2,
    name="James Wilson",
    gender="Male",
    email="james.wilson@email.com",
    mobile="555-1003",
    rent=750.00,
    rent_type="monthly",
    joining_date=today - timedelta(days=30),
    next_pay_date=today + timedelta(days=15)
)
print(f"   ✓ Created: {resident3.name}")

resident4 = Resident.objects.create(
    property=property2,
    name="Lisa Anderson",
    gender="Female",
    email="lisa.anderson@email.com",
    mobile="555-1004",
    rent=1100.00,
    rent_type="monthly",
    joining_date=today - timedelta(days=15),
    next_pay_date=today + timedelta(days=20)
)
print(f"   ✓ Created: {resident4.name}")

# ============================================================================
# 6. CREATE OCCUPANCY
# ============================================================================
print("\n6️⃣  Creating Occupancy Records...")
occupancy1 = Occupancy.objects.create(
    property=property1,
    resident=resident1,
    floor=floor1_p1,
    room=rooms[0],
    bed=beds[0],
    is_occupied=True,
    occupied_since=resident1.joining_date
)
print(f"   ✓ {resident1.name} → Room {rooms[0].room_number}, Bed {beds[0].bed_number}")

occupancy2 = Occupancy.objects.create(
    property=property1,
    resident=resident2,
    floor=floor1_p1,
    room=rooms[2],
    bed=beds[4],
    is_occupied=True,
    occupied_since=resident2.joining_date
)
print(f"   ✓ {resident2.name} → Room {rooms[2].room_number}, Bed {beds[4].bed_number}")

occupancy3 = Occupancy.objects.create(
    property=property2,
    resident=resident3,
    floor=floor1_p2,
    room=rooms[12],
    bed=beds[12],
    is_occupied=True,
    occupied_since=resident3.joining_date
)
print(f"   ✓ {resident3.name} → Room {rooms[12].room_number}, Bed {beds[12].bed_number}")

occupancy4 = Occupancy.objects.create(
    property=property2,
    resident=resident4,
    floor=floor2_p2,
    room=rooms[15],
    bed=beds[15],
    is_occupied=True,
    occupied_since=resident4.joining_date
)
print(f"   ✓ {resident4.name} → Room {rooms[15].room_number}, Bed {beds[15].bed_number}")

# Update residents with current location info
resident1.current_floor = floor1_p1
resident1.current_room = rooms[0]
resident1.current_bed = beds[0]
resident1.save()

resident2.current_floor = floor1_p1
resident2.current_room = rooms[2]
resident2.current_bed = beds[4]
resident2.save()

resident3.current_floor = floor1_p2
resident3.current_room = rooms[12]
resident3.current_bed = beds[12]
resident3.save()

resident4.current_floor = floor2_p2
resident4.current_room = rooms[15]
resident4.current_bed = beds[15]
resident4.save()

# ============================================================================
# 7. CREATE OCCUPANCY HISTORY
# ============================================================================
print("\n7️⃣  Creating Occupancy History...")
occupancy_histories = [
    OccupancyHistory.objects.create(
        property=property1,
        floor=floor1_p1,
        room=rooms[0],
        bed=beds[0],
        resident=resident1,
        action="occupied",
        notes="Check-in completed"
    ),
    OccupancyHistory.objects.create(
        property=property1,
        floor=floor1_p1,
        room=rooms[2],
        bed=beds[4],
        resident=resident2,
        action="occupied",
        notes="Check-in completed"
    ),
    OccupancyHistory.objects.create(
        property=property2,
        floor=floor1_p2,
        room=rooms[12],
        bed=beds[12],
        resident=resident3,
        action="occupied",
        notes="Check-in completed"
    ),
    OccupancyHistory.objects.create(
        property=property2,
        floor=floor2_p2,
        room=rooms[15],
        bed=beds[15],
        resident=resident4,
        action="occupied",
        notes="Check-in completed"
    ),
]

print(f"   ✓ Created {len(occupancy_histories)} occupancy history records")

# ============================================================================
# 8. CREATE EXPENSES
# ============================================================================
print("\n8️⃣  Creating Expenses...")
expenses = [
    Expense.objects.create(
        property=property1,
        category="Maintenance",
        description="Plumbing repair - 3rd floor bathroom",
        amount=350.00,
        expense_date=datetime.now() - timedelta(days=10),
        payment_method="bank_transfer"
    ),
    Expense.objects.create(
        property=property1,
        category="Utilities",
        description="Electric bill for November",
        amount=420.50,
        expense_date=datetime.now() - timedelta(days=5),
        payment_method="bank_transfer"
    ),
    Expense.objects.create(
        property=property1,
        category="Cleaning",
        description="Common area cleaning service",
        amount=200.00,
        expense_date=datetime.now() - timedelta(days=3),
        payment_method="cash"
    ),
    Expense.objects.create(
        property=property2,
        category="Maintenance",
        description="HVAC system inspection",
        amount=500.00,
        expense_date=datetime.now() - timedelta(days=8),
        payment_method="card"
    ),
    Expense.objects.create(
        property=property2,
        category="Insurance",
        description="Monthly building insurance",
        amount=800.00,
        expense_date=datetime.now() - timedelta(days=1),
        payment_method="bank_transfer"
    ),
]

for expense in expenses:
    print(f"   ✓ {expense.category}: ${expense.amount} - {expense.description}")

# ============================================================================
# 9. CREATE PAYMENTS
# ============================================================================
print("\n9️⃣  Creating Payments...")
payments = [
    Payment.objects.create(
        property=property1,
        resident=resident1,
        resident_name=resident1.name,
        amount=800.00,
        payment_method="bank_transfer"
    ),
    Payment.objects.create(
        property=property1,
        resident=resident2,
        resident_name=resident2.name,
        amount=1200.00,
        payment_method="card"
    ),
    Payment.objects.create(
        property=property2,
        resident=resident3,
        resident_name=resident3.name,
        amount=750.00,
        payment_method="bank_transfer"
    ),
    Payment.objects.create(
        property=property2,
        resident=resident4,
        resident_name=resident4.name,
        amount=1100.00,
        payment_method="upi"
    ),
]

for payment in payments:
    print(f"   ✓ {payment.resident_name}: ${payment.amount}")

# ============================================================================
# 10. CREATE MAINTENANCE REQUESTS
# ============================================================================
print("\n🔟 Creating Maintenance Requests...")
maintenance_requests = [
    MaintenanceRequest.objects.create(
        property=property1,
        resident=resident1,
        category="Plumbing",
        description="Leaky faucet in bathroom",
        priority="low",
        status="open"
    ),
    MaintenanceRequest.objects.create(
        property=property1,
        resident=resident2,
        category="HVAC",
        description="Air conditioner not cooling properly",
        priority="high",
        status="in_progress"
    ),
    MaintenanceRequest.objects.create(
        property=property1,
        category="Electrical",
        description="Light fixture broken in hallway",
        priority="medium",
        status="resolved",
        resolved_date=datetime.now() - timedelta(days=3)
    ),
    MaintenanceRequest.objects.create(
        property=property2,
        resident=resident3,
        category="Door Lock",
        description="Room door lock needs replacement",
        priority="high",
        status="open"
    ),
    MaintenanceRequest.objects.create(
        property=property2,
        resident=resident4,
        category="Plumbing",
        description="Low water pressure in bathroom",
        priority="medium",
        status="in_progress"
    ),
]

for mr in maintenance_requests:
    priority_emoji = "🔴" if mr.priority == "high" else "🟡" if mr.priority == "medium" else "🟢"
    print(f"   {priority_emoji} {mr.category}: {mr.description} ({mr.status})")

# ============================================================================
# 11. CREATE USERS
# ============================================================================
print("\n1️⃣1️⃣ Creating Users...")
users = [
    User.objects.create(
        property=property1,
        username="admin1",
        email="admin1@properties.com",
        password_hash="hashed_password_1",
        role="admin"
    ),
    User.objects.create(
        property=property2,
        username="manager1",
        email="manager1@properties.com",
        password_hash="hashed_password_2",
        role="manager"
    ),
    User.objects.create(
        property=property1,
        username="staff1",
        email="staff1@properties.com",
        password_hash="hashed_password_3",
        role="staff"
    ),
]

for user in users:
    print(f"   ✓ {user.username} ({user.role})")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("✅ SAMPLE DATA LOADED SUCCESSFULLY")
print("="*80)
print(f"\n📊 DATA SUMMARY:")
print(f"   Properties:              {Property.objects.count()}")
print(f"   Floors:                  {Floor.objects.count()}")
print(f"   Rooms:                   {Room.objects.count()}")
print(f"   Beds:                    {Bed.objects.count()}")
print(f"   Residents:               {Resident.objects.count()}")
print(f"   Occupancy Records:       {Occupancy.objects.count()}")
print(f"   Occupancy History:       {OccupancyHistory.objects.count()}")
print(f"   Expenses:                {Expense.objects.count()}")
print(f"   Payments:                {Payment.objects.count()}")
print(f"   Maintenance Requests:    {MaintenanceRequest.objects.count()}")
print(f"   Users:                   {User.objects.count()}")
print(f"\n🔗 Test your API:")
print(f"   Swagger UI: http://localhost:8000/api/docs/")
print(f"\n📋 Available endpoints:")
print(f"   • http://localhost:8000/api/v1/properties/")
print(f"   • http://localhost:8000/api/v1/floors/")
print(f"   • http://localhost:8000/api/v1/rooms/")
print(f"   • http://localhost:8000/api/v1/beds/")
print(f"   • http://localhost:8000/api/v1/residents/")
print(f"   • http://localhost:8000/api/v1/occupancy/")
print(f"   • http://localhost:8000/api/v1/expenses/")
print(f"   • http://localhost:8000/api/v1/payments/")
print(f"   • http://localhost:8000/api/v1/maintenance-requests/")
print("="*80 + "\n")
