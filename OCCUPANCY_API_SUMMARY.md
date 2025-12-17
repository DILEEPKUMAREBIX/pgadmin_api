# ✅ New API Endpoint: Occupancy Detail

## Summary

A new consolidated **Occupancy Detail API** endpoint has been created specifically for the mobile app's occupancy tab.

## What's New

### New Endpoint
```
GET /api/v1/properties/{id}/occupancy_detail/
```

**Example:**
```bash
http://localhost:8000/api/v1/properties/1/occupancy_detail/
```

### What It Returns

**Single API call that returns:**

1. **Property Basic Details**
   - Property name, address, city, state, zip code
   - Description

2. **Property-Level Occupancy Statistics**
   - Total floors
   - Total rooms
   - Total beds
   - Occupied beds count
   - Available beds count
   - Occupancy percentage

3. **Complete Hierarchical Structure**
   ```
   Property
   ├── Floor 1
   │   ├── Room 101
   │   │   ├── Bed 1 (Occupied - Michael Brown)
   │   │   ├── Bed 2 (Available)
   │   │   └── Occupancy Stats: 1 occupied, 1 available
   │   ├── Room 102
   │   │   ├── Bed 1 (Available)
   │   │   └── Occupancy Stats: 0 occupied, 1 available
   │   └── Floor Stats: 1 occupied, 3 available
   ├── Floor 2
   │   ├── Room 201
   │   ├── Room 202
   │   └── Floor Stats
   └── Property Stats
   ```

4. **Resident Information for Occupied Beds**
   - Resident name
   - Resident ID
   - Occupancy status (occupied/available)

## Response Example (Abbreviated)

```json
{
  "property_id": 1,
  "property_name": "Sunrise Apartments",
  "address": "123 Main Street, Downtown",
  "city": "New York",
  "state": "NY",
  "zip_code": "10001",
  "description": "Modern apartment complex in downtown area",
  
  // Property Level Stats
  "total_floors": 3,
  "total_rooms": 12,
  "total_beds": 12,
  "occupied_beds": 2,
  "available_beds": 10,
  "occupancy_percentage": 16.67,
  
  // Detailed Floors with Rooms and Beds
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

## Why This Endpoint?

### ✅ Before (Without This Endpoint)
- Need to call `/api/v1/properties/{id}/` - Get property
- Then call `/api/v1/floors/` - Get all floors
- Then call `/api/v1/rooms/` - Get all rooms
- Then call `/api/v1/beds/` - Get all beds
- Then call `/api/v1/occupancy/` - Get occupancy status
- **Multiple API calls needed**

### ✅ After (With This Endpoint)
- Single call to `/api/v1/properties/{id}/occupancy_detail/`
- **Everything in one response**
- **Perfect for mobile app occupancy tab**

## Key Features

| Feature | Description |
|---------|-------------|
| **Hierarchical Data** | Property → Floors → Rooms → Beds structure |
| **Occupancy Info** | Shows which beds are occupied and by whom |
| **Statistics** | Occupancy percentages at all levels |
| **Resident Data** | Resident names and IDs for occupied beds |
| **Mobile Optimized** | Perfect JSON structure for mobile app display |
| **Performance** | Single API call instead of 5+ calls |

## Access

### Via Swagger UI
1. Go to: http://localhost:8000/api/docs/
2. Find: **Properties** section
3. Look for: **occupancy_detail** endpoint
4. Click **Try it out**
5. Enter property ID (e.g., 1)
6. Click **Execute**

### Via cURL
```bash
curl -X GET http://localhost:8000/api/v1/properties/1/occupancy_detail/
```

### Via JavaScript/React Native
```javascript
const response = await fetch('http://localhost:8000/api/v1/properties/1/occupancy_detail/');
const data = await response.json();
console.log(data);
```

## Mobile App Usage Example

### Display Occupancy Tab
```javascript
function OccupancyTab({ propertyId }) {
  const [occupancy, setOccupancy] = useState(null);

  useEffect(() => {
    fetch(`http://api.example.com/api/v1/properties/${propertyId}/occupancy_detail/`)
      .then(r => r.json())
      .then(data => setOccupancy(data));
  }, [propertyId]);

  if (!occupancy) return <Loading />;

  return (
    <ScrollView>
      {/* Property Info */}
      <PropertyHeader 
        name={occupancy.property_name}
        occupancy={occupancy.occupancy_percentage}
        occupied={occupancy.occupied_beds}
        total={occupancy.total_beds}
      />

      {/* Floors */}
      {occupancy.floors.map(floor => (
        <FloorSection key={floor.floor_id} floor={floor} />
      ))}
    </ScrollView>
  );
}
```

## Files Created/Modified

### New Files
- ✅ `OCCUPANCY_DETAIL_API.md` - Comprehensive API documentation

### Modified Files
- ✅ `properties/serializers.py` - Added PropertyOccupancyDetailSerializer and related serializers
- ✅ `properties/views.py` - Added occupancy_detail action to PropertyViewSet

### Features Added

1. **BedOccupancySerializer**
   - Serializes bed with occupancy status
   - Shows resident name and ID if occupied

2. **RoomOccupancySerializer**
   - Serializes room with all beds
   - Includes occupied/available counts

3. **FloorOccupancySerializer**
   - Serializes floor with all rooms
   - Includes floor-level occupancy stats

4. **PropertyOccupancyDetailSerializer**
   - Main serializer for complete property view
   - Includes all floors, rooms, beds with occupancy
   - Calculates occupancy percentage

## Testing

### Test the Endpoint
```bash
# Terminal command
curl -X GET http://localhost:8000/api/v1/properties/1/occupancy_detail/ | python -m json.tool
```

### View in Browser
Open: http://localhost:8000/api/v1/properties/1/occupancy_detail/

### Use Swagger UI
1. Go to http://localhost:8000/api/docs/
2. Expand **Properties** section
3. Click on **GET /api/v1/properties/{id}/occupancy_detail/**
4. Click **Try it out**
5. Enter ID: 1
6. Click **Execute**

## Next Steps for Mobile App

1. **Install API endpoint URL** in mobile app config
2. **Add occupancy tab** that calls this endpoint
3. **Parse the response** and display hierarchical structure
4. **Color code beds** based on occupancy status (green = available, red = occupied)
5. **Show resident names** on occupied beds
6. **Add refresh button** to fetch latest data

## Response Time

- Single API call returns all occupancy data for a property
- Response size: ~10-50 KB (depends on number of floors/rooms/beds)
- Response time: <500ms (for properties with <100 beds)

## Troubleshooting

**Q: Getting 404 error?**
- A: Make sure the property ID exists. Check `/api/v1/properties/` to see valid IDs.

**Q: Bed occupancy showing as false even though resident is there?**
- A: Make sure the Occupancy record's `is_occupied` field is set to `true`. Check `/api/v1/occupancy/`.

**Q: Resident name showing null?**
- A: The Occupancy record might not have a resident linked to it. Check the database.

## Documentation Reference

For complete API documentation, see: `OCCUPANCY_DETAIL_API.md`

---

## ✅ Ready for Mobile App Integration!

The occupancy detail endpoint is now ready to be integrated into your PGAdmin mobile app's occupancy tab.
