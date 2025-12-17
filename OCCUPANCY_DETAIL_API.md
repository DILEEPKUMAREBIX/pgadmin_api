# Occupancy Detail API Endpoint

## Overview
The **Occupancy Detail API** provides a consolidated view of property occupancy information, perfect for displaying occupancy data in the mobile app's occupancy tab.

## Endpoint

```
GET /api/v1/properties/{id}/occupancy_detail/
```

## Purpose
This endpoint returns complete property details including:
- ✅ Property basic information (name, address, etc.)
- ✅ All floors in the property
- ✅ All rooms per floor with room details
- ✅ All beds per room with occupancy status
- ✅ Resident information for occupied beds
- ✅ Occupancy statistics at property, floor, and room levels

Perfect for mobile app occupancy tab display.

## Request Example

```bash
curl -X GET http://localhost:8000/api/v1/properties/1/occupancy_detail/
```

## Response Structure

### Top Level (Property)
```json
{
  "property_id": 1,
  "property_name": "Sunrise Apartments",
  "address": "123 Main Street, Downtown",
  "city": "New York",
  "state": "NY",
  "zip_code": "10001",
  "description": "Modern apartment complex in downtown area",
  
  // Property Level Statistics
  "total_floors": 3,
  "total_rooms": 12,
  "total_beds": 12,
  "occupied_beds": 2,
  "available_beds": 10,
  "occupancy_percentage": 16.67,
  
  // Floors with detailed information
  "floors": [...]
}
```

### Floor Level
```json
{
  "floor_id": 1,
  "floor_level": 1,
  "floor_name": "Ground Floor",
  
  // Floor Level Statistics
  "total_beds": 6,
  "occupied_beds": 2,
  "available_beds": 4,
  
  // Rooms in floor
  "rooms": [...]
}
```

### Room Level
```json
{
  "room_id": 1,
  "room_number": "1011",
  "room_name": null,
  "room_type": "double",
  "total_beds": 2,
  
  // Room Level Statistics
  "occupied_count": 1,
  "available_count": 1,
  
  // Beds in room
  "beds": [...]
}
```

### Bed Level
```json
{
  "bed_id": 1,
  "bed_number": "1",
  "bed_name": "Room 1011 - Bed 1",
  "is_occupied": true,
  "resident_name": "Michael Brown",
  "resident_id": 1
}
```

## Complete Response Example

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
          "room_name": null,
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

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Integer | Property ID |
| `property_name` | String | Name of the property |
| `address` | String | Property address |
| `city` | String | City name |
| `state` | String | State/Province |
| `zip_code` | String | Postal code |
| `description` | String | Property description |
| `total_floors` | Integer | Total number of floors |
| `total_rooms` | Integer | Total number of rooms |
| `total_beds` | Integer | Total number of beds |
| `occupied_beds` | Integer | Number of occupied beds |
| `available_beds` | Integer | Number of available beds |
| `occupancy_percentage` | Float | Percentage of occupied beds (0-100) |
| `floors` | Array | Array of floor objects |
| `floors[].floor_id` | Integer | Floor ID |
| `floors[].floor_level` | Integer | Floor level number |
| `floors[].floor_name` | String | Floor name/label |
| `floors[].total_beds` | Integer | Total beds on floor |
| `floors[].occupied_beds` | Integer | Occupied beds on floor |
| `floors[].available_beds` | Integer | Available beds on floor |
| `floors[].rooms` | Array | Array of room objects |
| `floors[].rooms[].room_id` | Integer | Room ID |
| `floors[].rooms[].room_number` | String | Room number/code |
| `floors[].rooms[].room_type` | String | Room type (single/double/triple/dormitory) |
| `floors[].rooms[].total_beds` | Integer | Total beds in room |
| `floors[].rooms[].occupied_count` | Integer | Occupied beds in room |
| `floors[].rooms[].available_count` | Integer | Available beds in room |
| `floors[].rooms[].beds` | Array | Array of bed objects |
| `floors[].rooms[].beds[].bed_id` | Integer | Bed ID |
| `floors[].rooms[].beds[].bed_number` | String | Bed number within room |
| `floors[].rooms[].beds[].bed_name` | String | Bed label/name |
| `floors[].rooms[].beds[].is_occupied` | Boolean | Whether bed is occupied |
| `floors[].rooms[].beds[].resident_name` | String | Name of resident (if occupied) |
| `floors[].rooms[].beds[].resident_id` | Integer | ID of resident (if occupied) |

## Use Cases

### 1. Display Occupancy Tab in Mobile App
```javascript
const response = await fetch('http://localhost:8000/api/v1/properties/1/occupancy_detail/');
const data = await response.json();

// Display property summary
console.log(`${data.property_name}: ${data.occupancy_percentage}% occupied`);

// Display floors
data.floors.forEach(floor => {
  console.log(`Floor ${floor.floor_level}: ${floor.occupied_beds}/${floor.total_beds} beds occupied`);
  
  // Display rooms
  floor.rooms.forEach(room => {
    console.log(`  Room ${room.room_number}: ${room.occupied_count} occupied`);
  });
});
```

### 2. Get Specific Property Occupancy Status
```javascript
// Get occupancy for property ID 1
const response = await fetch('http://localhost:8000/api/v1/properties/1/occupancy_detail/');
const property = await response.json();

// Check occupancy percentage
if (property.occupancy_percentage > 90) {
  alert('Property is nearly full!');
}
```

### 3. Display Bed Status
```javascript
// Find all occupied beds in a property
const response = await fetch('http://localhost:8000/api/v1/properties/1/occupancy_detail/');
const property = await response.json();

const occupiedBeds = [];
property.floors.forEach(floor => {
  floor.rooms.forEach(room => {
    room.beds.forEach(bed => {
      if (bed.is_occupied) {
        occupiedBeds.push({
          bed: bed.bed_name,
          resident: bed.resident_name
        });
      }
    });
  });
});

console.log(occupiedBeds);
```

## Performance Notes

- ✅ Single API call returns all occupancy data
- ✅ No need for multiple API calls to different endpoints
- ✅ Efficient hierarchical data structure (Property → Floor → Room → Bed)
- ✅ Includes occupancy statistics at each level
- ✅ Optimized for mobile app display

## Related Endpoints

- `GET /api/v1/properties/` - List all properties
- `GET /api/v1/properties/{id}/` - Get property details
- `GET /api/v1/properties/{id}/summary/` - Get property summary
- `GET /api/v1/occupancy/` - List all occupancy records
- `GET /api/v1/residents/` - List all residents

## Mobile App Integration Example

```javascript
// React Native / Flutter equivalent

async function fetchPropertyOccupancy(propertyId) {
  try {
    const response = await fetch(
      `http://your-server:8000/api/v1/properties/${propertyId}/occupancy_detail/`
    );
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching occupancy data:', error);
    return null;
  }
}

// Usage in occupancy tab
function OccupancyTab({ propertyId }) {
  const [occupancyData, setOccupancyData] = useState(null);

  useEffect(() => {
    fetchPropertyOccupancy(propertyId).then(data => {
      setOccupancyData(data);
    });
  }, [propertyId]);

  return (
    <View>
      <Text>{occupancyData?.property_name}</Text>
      <ProgressBar value={occupancyData?.occupancy_percentage} />
      
      {occupancyData?.floors.map(floor => (
        <FloorCard key={floor.floor_id} floor={floor} />
      ))}
    </View>
  );
}
```

## Status Codes

- `200 OK` - Successfully retrieved occupancy details
- `404 Not Found` - Property not found
- `500 Internal Server Error` - Server error

## Available in Swagger UI

Access the interactive API documentation at: `http://localhost:8000/api/docs/`

Search for "Properties > occupancy_detail" endpoint.
