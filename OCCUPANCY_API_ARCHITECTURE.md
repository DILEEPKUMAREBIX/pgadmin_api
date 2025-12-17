# Occupancy Detail API - Data Flow & Architecture

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         MOBILE APP                              │
│              (Occupancy Tab - React Native/Flutter)             │
└────────────────────────────┬──────────────────────────────────┘
                             │
                             │ Single API Call
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DJANGO REST API                            │
│     GET /api/v1/properties/{id}/occupancy_detail/              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PropertyViewSet                                                │
│  ├─ @action(detail=True)                                        │
│  └─ def occupancy_detail(self):                                │
│     ├─ Get Property object                                      │
│     ├─ Use PropertyOccupancyDetailSerializer                    │
│     └─ Return Response(serializer.data)                         │
│                                                                 │
└────────────────────────────┬──────────────────────────────────┘
                             │
                             │ Serialization Process
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        SERIALIZERS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PropertyOccupancyDetailSerializer                              │
│  │                                                              │
│  ├─ Property Fields (id, name, address, etc.)                 │
│  │                                                              │
│  ├─ get_total_floors() → Count floors                          │
│  ├─ get_total_rooms() → Count rooms                            │
│  ├─ get_total_beds() → Property.total_beds                     │
│  ├─ get_occupied_beds() → Query Occupancy                      │
│  ├─ get_available_beds() → Query Occupancy                     │
│  ├─ get_occupancy_percentage() → Calculate %                   │
│  │                                                              │
│  └─ get_floors()                                                │
│     │                                                           │
│     └─ FloorOccupancySerializer (for each floor)               │
│        │                                                        │
│        ├─ Floor Fields (id, floor_level, floor_name)           │
│        ├─ Floor Stats (total_beds, occupied, available)        │
│        │                                                        │
│        └─ get_rooms()                                           │
│           │                                                     │
│           └─ RoomOccupancySerializer (for each room)           │
│              │                                                  │
│              ├─ Room Fields (id, room_number, room_type, etc)  │
│              ├─ Room Stats (occupied_count, available_count)   │
│              │                                                  │
│              └─ get_beds()                                      │
│                 │                                               │
│                 └─ BedOccupancySerializer (for each bed)       │
│                    │                                            │
│                    ├─ Bed Fields (id, bed_number, bed_name)    │
│                    ├─ get_is_occupied() → Query Occupancy      │
│                    ├─ get_resident_name() → Query Resident     │
│                    └─ get_resident_id() → Query Resident       │
│                                                                 │
└────────────────────────────┬──────────────────────────────────┘
                             │
                             │ Database Queries
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      POSTGRESQL DATABASE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Tables Queried:                                                │
│  ├─ properties_property (main data)                            │
│  ├─ properties_floor (GET floors for property)                 │
│  ├─ properties_room (GET rooms for each floor)                 │
│  ├─ properties_bed (GET beds for each room)                    │
│  ├─ properties_occupancy (GET occupancy status)                │
│  └─ properties_resident (GET resident info)                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Example

### Step 1: Request
```
GET /api/v1/properties/1/occupancy_detail/
```

### Step 2: View Processing
```python
# PropertyViewSet.occupancy_detail()
1. property_obj = Property.objects.get(id=1)
2. serializer = PropertyOccupancyDetailSerializer(property_obj)
3. return Response(serializer.data)
```

### Step 3: Serializer Processing

#### A. Property Level
```python
# PropertyOccupancyDetailSerializer.to_representation()
{
  "property_id": property_obj.id,
  "property_name": property_obj.name,
  "address": property_obj.address,
  "city": property_obj.city,
  "state": property_obj.state,
  "zip_code": property_obj.zip_code,
  
  # Stats
  "total_floors": property_obj.floors.count(),  # Query 1
  "total_rooms": property_obj.rooms.count(),    # Query 2
  "total_beds": property_obj.total_beds,        # Property @property
  "occupied_beds": Occupancy.objects.filter(property=property_obj, is_occupied=True).count(),  # Query 3
  "available_beds": Occupancy.objects.filter(property=property_obj, is_occupied=False).count(), # Query 4
  "occupancy_percentage": (occupied / total) * 100,
  
  # Floors (recursively process)
  "floors": [FloorOccupancySerializer(floor).data for floor in property_obj.floors.all()]
}
```

#### B. Floor Level (for each floor)
```python
# FloorOccupancySerializer.to_representation()
{
  "floor_id": floor.id,
  "floor_level": floor.floor_level,
  "floor_name": floor.floor_name,
  
  # Stats
  "total_beds": floor.rooms.aggregate(Sum('total_beds'))['total'],
  "occupied_beds": Occupancy.objects.filter(floor=floor, is_occupied=True).count(),
  "available_beds": Occupancy.objects.filter(floor=floor, is_occupied=False).count(),
  
  # Rooms (recursively process)
  "rooms": [RoomOccupancySerializer(room).data for room in floor.rooms.all()]
}
```

#### C. Room Level (for each room)
```python
# RoomOccupancySerializer.to_representation()
{
  "room_id": room.id,
  "room_number": room.room_number,
  "room_type": room.room_type,
  "total_beds": room.total_beds,
  
  # Stats
  "occupied_count": Occupancy.objects.filter(room=room, is_occupied=True).count(),
  "available_count": Occupancy.objects.filter(room=room, is_occupied=False).count(),
  
  # Beds (recursively process)
  "beds": [BedOccupancySerializer(bed).data for bed in room.beds.all()]
}
```

#### D. Bed Level (for each bed)
```python
# BedOccupancySerializer.to_representation()
occupancy = Occupancy.objects.filter(bed=bed, is_occupied=True).first()

{
  "bed_id": bed.id,
  "bed_number": bed.bed_number,
  "bed_name": bed.bed_name,
  
  # Status
  "is_occupied": occupancy is not None,
  "resident_name": occupancy.resident.name if occupancy else None,
  "resident_id": occupancy.resident.id if occupancy else None
}
```

### Step 4: Response JSON

Complete hierarchical structure returned to mobile app:

```json
{
  "property_id": 1,
  "property_name": "Sunrise Apartments",
  "address": "123 Main Street, Downtown",
  "city": "New York",
  "state": "NY",
  "zip_code": "10001",
  "description": "Modern apartment complex in downtown area",
  "total_floors": 3,
  "total_rooms": 12,
  "total_beds": 12,
  "occupied_beds": 2,
  "available_beds": 10,
  "occupancy_percentage": 16.67,
  "floors": [
    {
      "floor_id": 1,
      "floor_level": 1,
      "floor_name": "Ground Floor",
      "total_beds": 6,
      "occupied_beds": 2,
      "available_beds": 4,
      "rooms": [
        {
          "room_id": 1,
          "room_number": "1011",
          "room_type": "double",
          "total_beds": 2,
          "occupied_count": 1,
          "available_count": 1,
          "beds": [
            {
              "bed_id": 1,
              "bed_number": "1",
              "bed_name": "Room 1011 - Bed 1",
              "is_occupied": true,
              "resident_name": "Michael Brown",
              "resident_id": 1
            },
            {
              "bed_id": 2,
              "bed_number": "2",
              "bed_name": "Room 1011 - Bed 2",
              "is_occupied": false,
              "resident_name": null,
              "resident_id": null
            }
          ]
        }
      ]
    }
  ]
}
```

## Database Query Optimization

### Queries Executed

The serializer performs these database queries:

1. **Get Property** - `SELECT * FROM properties_property WHERE id = 1`
2. **Count Floors** - `SELECT COUNT(*) FROM properties_floor WHERE property_id = 1`
3. **Count Rooms** - `SELECT COUNT(*) FROM properties_room WHERE property_id = 1`
4. **Occupied Beds** - `SELECT COUNT(*) FROM properties_occupancy WHERE property_id = 1 AND is_occupied = true`
5. **Available Beds** - `SELECT COUNT(*) FROM properties_occupancy WHERE property_id = 1 AND is_occupied = false`
6. **Get Floors** - `SELECT * FROM properties_floor WHERE property_id = 1 ORDER BY floor_level`
7. **Get Rooms** - `SELECT * FROM properties_room WHERE floor_id IN (...)`
8. **Get Beds** - `SELECT * FROM properties_bed WHERE room_id IN (...)`
9. **Get Occupancy** - `SELECT * FROM properties_occupancy WHERE bed_id IN (...)` (per bed)
10. **Get Residents** - `SELECT * FROM properties_resident WHERE id IN (...)` (for occupied beds)

### Performance Considerations

✅ **Optimized for common queries**
- Floor and room data are relatively small
- Occupancy filtering is efficient with indexes
- Resident lookups only for occupied beds

⚠️ **Large properties might be slow**
- Properties with 1000+ beds will generate larger responses
- Consider implementing pagination if needed

## Mobile App Integration Points

### 1. Display Property Summary
```javascript
const {
  property_name,
  occupancy_percentage,
  occupied_beds,
  total_beds,
  total_floors,
  total_rooms
} = occupancyData;
```

### 2. Display Floors
```javascript
occupancyData.floors.forEach(floor => {
  displayFloor({
    name: floor.floor_name,
    level: floor.floor_level,
    occupancy: (floor.occupied_beds / floor.total_beds) * 100
  });
});
```

### 3. Display Rooms
```javascript
floor.rooms.forEach(room => {
  displayRoom({
    number: room.room_number,
    type: room.room_type,
    occupancy: room.occupied_count
  });
});
```

### 4. Display Beds with Status
```javascript
room.beds.forEach(bed => {
  displayBed({
    number: bed.bed_number,
    status: bed.is_occupied ? 'Occupied' : 'Available',
    resident: bed.resident_name || 'Empty',
    color: bed.is_occupied ? 'red' : 'green'
  });
});
```

## Code Structure

### File Locations

```
properties/
├── models.py (Property, Floor, Room, Bed, Resident, Occupancy models)
├── serializers.py
│   ├── PropertyOccupancyDetailSerializer (NEW)
│   ├── FloorOccupancySerializer (NEW)
│   ├── RoomOccupancySerializer (NEW)
│   └── BedOccupancySerializer (NEW)
├── views.py
│   └── PropertyViewSet
│       └── occupancy_detail(self, request, pk=None) (NEW ACTION)
└── urls.py (auto-generated routes)
```

## Testing Endpoints

### 1. Django Shell Test
```python
python manage.py shell
from properties.models import Property
from properties.serializers import PropertyOccupancyDetailSerializer

property_obj = Property.objects.get(id=1)
serializer = PropertyOccupancyDetailSerializer(property_obj)
print(serializer.data)
```

### 2. cURL Test
```bash
curl -X GET http://localhost:8000/api/v1/properties/1/occupancy_detail/
```

### 3. Swagger UI Test
1. Go to http://localhost:8000/api/docs/
2. Find Properties > occupancy_detail
3. Try it out with property ID 1

## Summary

✅ **Single API endpoint** returns all occupancy data
✅ **Hierarchical structure** matches property organization
✅ **Occupancy stats** at all levels (property, floor, room)
✅ **Resident info** for occupied beds
✅ **Mobile optimized** JSON response
✅ **Efficient queries** with proper indexing

Ready for mobile app integration!
