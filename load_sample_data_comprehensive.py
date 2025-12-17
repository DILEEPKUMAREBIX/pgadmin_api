import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pgadmin_config.settings')
django.setup()

from datetime import datetime, timedelta
from properties.models import (
    Property, Floor, Room, Bed, Resident, Occupancy, 
    OccupancyHistory, Expense, Payment, MaintenanceRequest, User
)

# Clear existing data (optional - comment out to keep existing data)
print("Clearing existing data...")
Property.objects.all().delete()
Resident.objects.all().delete()
User.objects.all().delete()

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
print(f"     - {property1.name}: 3 floors")
print(f"     - {property2.name}: 2 floors")

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
resident1 = Resident.objects.create(
    name="Michael Brown",
    email="michael.brown@email.com",
    phone="555-1001",
    emergency_contact="555-1011",
    id_number="ID-20241",
    check_in_date=datetime.now().date() - timedelta(days=90)
)
print(f"   ✓ Created: {resident1.name}")

resident2 = Resident.objects.create(
    name="Emily Davis",
    email="emily.davis@email.com",
    phone="555-1002",
    emergency_contact="555-1012",
    id_number="ID-20242",
    check_in_date=datetime.now().date() - timedelta(days=60)
)
print(f"   ✓ Created: {resident2.name}")

resident3 = Resident.objects.create(
    name="James Wilson",
    email="james.wilson@email.com",
    phone="555-1003",
    emergency_contact="555-1013",
    id_number="ID-20243",
    check_in_date=datetime.now().date() - timedelta(days=30)
)
print(f"   ✓ Created: {resident3.name}")

resident4 = Resident.objects.create(
    name="Lisa Anderson",
    email="lisa.anderson@email.com",
    phone="555-1004",
    emergency_contact="555-1014",
    id_number="ID-20244",
    check_in_date=datetime.now().date() - timedelta(days=15)
)
print(f"   ✓ Created: {resident4.name}")

# ============================================================================
# 6. CREATE OCCUPANCY
# ============================================================================
print("\n6️⃣  Creating Occupancy Records...")
occupancy1 = Occupancy.objects.create(
    property=property1,
    resident=resident1,
    bed=beds[0],
    room=rooms[0],
    floor=floor1_p1,
    check_in_date=resident1.check_in_date,
    status="Occupied",
    lease_end_date=datetime.now().date() + timedelta(days=90)
)
print(f"   ✓ {resident1.name} → Room {rooms[0].room_number}")

occupancy2 = Occupancy.objects.create(
    property=property1,
    resident=resident2,
    bed=beds[4],
    room=rooms[2],
    floor=floor1_p1,
    check_in_date=resident2.check_in_date,
    status="Occupied",
    lease_end_date=datetime.now().date() + timedelta(days=120)
)
print(f"   ✓ {resident2.name} → Room {rooms[2].room_number}")

occupancy3 = Occupancy.objects.create(
    property=property2,
    resident=resident3,
    bed=beds[12],
    room=rooms[12],
    floor=floor1_p2,
    check_in_date=resident3.check_in_date,
    status="Occupied",
    lease_end_date=datetime.now().date() + timedelta(days=60)
)
print(f"   ✓ {resident3.name} → Room {rooms[12].room_number}")

occupancy4 = Occupancy.objects.create(
    property=property2,
    resident=resident4,
    bed=beds[15],
    room=rooms[15],
    floor=floor2_p2,
    check_in_date=resident4.check_in_date,
    status="Occupied",
    lease_end_date=datetime.now().date() + timedelta(days=180)
)
print(f"   ✓ {resident4.name} → Room {rooms[15].room_number}")

# ============================================================================
# 7. CREATE OCCUPANCY HISTORY
# ============================================================================
print("\n7️⃣  Creating Occupancy History...")
for i, occupancy in enumerate([occupancy1, occupancy2, occupancy3, occupancy4]):
    history = OccupancyHistory.objects.create(
        occupancy=occupancy,
        resident=occupancy.resident,
        room=occupancy.room,
        check_in_date=occupancy.check_in_date,
        status="Checked In"
    )

print(f"   ✓ Created {Occupancy.objects.count()} occupancy history records")

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
        date=datetime.now().date() - timedelta(days=10)
    ),
    Expense.objects.create(
        property=property1,
        category="Utilities",
        description="Electric bill for November",
        amount=420.50,
        date=datetime.now().date() - timedelta(days=5)
    ),
    Expense.objects.create(
        property=property1,
        category="Cleaning",
        description="Common area cleaning service",
        amount=200.00,
        date=datetime.now().date() - timedelta(days=3)
    ),
    Expense.objects.create(
        property=property2,
        category="Maintenance",
        description="HVAC system inspection",
        amount=500.00,
        date=datetime.now().date() - timedelta(days=8)
    ),
    Expense.objects.create(
        property=property2,
        category="Insurance",
        description="Monthly building insurance",
        amount=800.00,
        date=datetime.now().date() - timedelta(days=1)
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
        amount=800.00,
        payment_date=datetime.now().date() - timedelta(days=20),
        payment_method="Bank Transfer",
        due_date=datetime.now().date() - timedelta(days=25),
        status="Paid"
    ),
    Payment.objects.create(
        property=property1,
        resident=resident2,
        amount=1200.00,
        payment_date=datetime.now().date() - timedelta(days=15),
        payment_method="Card",
        due_date=datetime.now().date() - timedelta(days=20),
        status="Paid"
    ),
    Payment.objects.create(
        property=property1,
        resident=resident1,
        amount=800.00,
        payment_date=None,
        payment_method=None,
        due_date=datetime.now().date() - timedelta(days=5),
        status="Overdue"
    ),
    Payment.objects.create(
        property=property2,
        resident=resident3,
        amount=750.00,
        payment_date=datetime.now().date() - timedelta(days=10),
        payment_method="Bank Transfer",
        due_date=datetime.now().date() - timedelta(days=15),
        status="Paid"
    ),
    Payment.objects.create(
        property=property2,
        resident=resident4,
        amount=1100.00,
        payment_date=None,
        payment_method=None,
        due_date=datetime.now().date() + timedelta(days=5),
        status="Due"
    ),
]

for payment in payments:
    status_emoji = "✓" if payment.status == "Paid" else "⏳" if payment.status == "Due" else "⚠️"
    print(f"   {status_emoji} {payment.resident.name}: ${payment.amount} ({payment.status})")

# ============================================================================
# 10. CREATE MAINTENANCE REQUESTS
# ============================================================================
print("\n🔟 Creating Maintenance Requests...")
maintenance_requests = [
    MaintenanceRequest.objects.create(
        property=property1,
        resident=resident1,
        room=rooms[0],
        title="Leaky faucet",
        description="Bathroom sink faucet is dripping",
        priority="Low",
        status="Open",
        requested_date=datetime.now().date() - timedelta(days=7)
    ),
    MaintenanceRequest.objects.create(
        property=property1,
        resident=resident2,
        room=rooms[2],
        title="AC not working",
        description="Air conditioner not cooling properly",
        priority="High",
        status="In Progress",
        requested_date=datetime.now().date() - timedelta(days=2)
    ),
    MaintenanceRequest.objects.create(
        property=property1,
        room=rooms[5],
        title="Light fixture repair",
        description="Hallway light fixture broken",
        priority="Medium",
        status="Resolved",
        requested_date=datetime.now().date() - timedelta(days=10),
        resolved_date=datetime.now().date() - timedelta(days=3)
    ),
    MaintenanceRequest.objects.create(
        property=property2,
        resident=resident3,
        room=rooms[12],
        title="Door lock malfunction",
        description="Room door lock needs replacement",
        priority="High",
        status="Open",
        requested_date=datetime.now().date() - timedelta(days=1)
    ),
    MaintenanceRequest.objects.create(
        property=property2,
        resident=resident4,
        room=rooms[15],
        title="Water pressure issue",
        description="Low water pressure in bathroom",
        priority="Medium",
        status="In Progress",
        requested_date=datetime.now().date() - timedelta(days=4)
    ),
]

for mr in maintenance_requests:
    priority_emoji = "🔴" if mr.priority == "High" else "🟡" if mr.priority == "Medium" else "🟢"
    print(f"   {priority_emoji} {mr.title} ({mr.status})")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("✅ SAMPLE DATA LOADED SUCCESSFULLY")
print("="*80)
print(f"\n📊 SUMMARY:")
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
print(f"\n🔗 Test your API at: http://localhost:8000/api/docs/")
print(f"📋 Available endpoints:")
print(f"   • http://localhost:8000/api/v1/properties/")
print(f"   • http://localhost:8000/api/v1/residents/")
print(f"   • http://localhost:8000/api/v1/occupancy/")
print(f"   • http://localhost:8000/api/v1/expenses/")
print(f"   • http://localhost:8000/api/v1/payments/")
print(f"   • http://localhost:8000/api/v1/maintenance-requests/")
print("="*80 + "\n")
