# CORS Configuration Guide

## ✅ CORS Error Fixed!

Your frontend at `http://localhost:8081/occupancy` was being blocked by CORS (Cross-Origin Resource Sharing) policy.

## What Changed

Updated `pgadmin_config/settings.py` to allow requests from port 8081:

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',      # React, Vue, etc.
    'http://localhost:8000',      # Django admin, docs
    'http://localhost:8081',      # ✅ YOUR FRONTEND (Added)
    'http://127.0.0.1:3000',
    'http://127.0.0.1:8000',
    'http://127.0.0.1:8081',      # ✅ IPv4 version
]
```

## How to Use Now

### From Frontend (localhost:8081)

**JavaScript/React:**
```javascript
// Now this will work without CORS errors!
const response = await fetch('http://localhost:8000/api/v1/properties/1/occupancy_detail/');
const data = await response.json();
```

**React Hook Example:**
```javascript
import { useState, useEffect } from 'react';

function OccupancyTab() {
  const [occupancy, setOccupancy] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/properties/1/occupancy_detail/')
      .then(res => res.json())
      .then(data => setOccupancy(data))
      .catch(err => setError(err.message));
  }, []);

  if (error) return <div>Error: {error}</div>;
  if (!occupancy) return <div>Loading...</div>;

  return (
    <div>
      <h1>{occupancy.property_name}</h1>
      <p>Occupancy: {occupancy.occupancy_percentage}%</p>
      <p>{occupancy.occupied_beds} / {occupancy.total_beds} beds occupied</p>
    </div>
  );
}

export default OccupancyTab;
```

**Axios Example:**
```javascript
import axios from 'axios';

async function fetchOccupancy(propertyId) {
  try {
    const response = await axios.get(
      `http://localhost:8000/api/v1/properties/${propertyId}/occupancy_detail/`
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching occupancy:', error);
  }
}
```

## Adding More Origins

If you need to add more frontend URLs, edit `pgadmin_config/settings.py` and add to `CORS_ALLOWED_ORIGINS`:

```python
CORS_ALLOWED_ORIGINS = [
    # ... existing origins ...
    'http://localhost:5173',       # Vite
    'http://localhost:5000',       # Flask frontend
    'http://192.168.1.100:8081',   # Network IP
    'https://yourdomain.com',      # Production domain
]
```

Then restart the server:
```bash
python manage.py runserver
```

## For Production

⚠️ **Never use wildcards in production!** Instead, use environment variables:

```python
import os

CORS_ALLOWED_ORIGINS = [
    'https://yourdomain.com',
    'https://www.yourdomain.com',
]

# Or from environment
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
```

## Testing CORS

### Option 1: From Browser Console
```javascript
// Open DevTools (F12) and run:
fetch('http://localhost:8000/api/v1/properties/1/occupancy_detail/')
  .then(r => r.json())
  .then(data => console.log(data))
  .catch(e => console.error('CORS Error:', e));
```

### Option 2: Using cURL
```bash
curl -X GET http://localhost:8000/api/v1/properties/1/occupancy_detail/ \
  -H "Origin: http://localhost:8081"
```

### Option 3: Check Response Headers
```javascript
fetch('http://localhost:8000/api/v1/properties/1/occupancy_detail/')
  .then(r => {
    console.log('Access-Control-Allow-Origin:', 
      r.headers.get('Access-Control-Allow-Origin'));
    return r.json();
  })
  .then(data => console.log('Success:', data));
```

## Common CORS Errors

### Error: "Access to XMLHttpRequest has been blocked by CORS policy"
**Solution**: Add your frontend URL/port to `CORS_ALLOWED_ORIGINS`

### Error: "The request was denied by the server"
**Solution**: 
1. Check if port is in CORS_ALLOWED_ORIGINS
2. Restart Django server after changes
3. Clear browser cache

### Error: "Preflight request failed"
**Solution**: Make sure CORS middleware is before other middleware in settings.py. It should be:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # ← Should be here
    'django.middleware.common.CommonMiddleware',
    # ... rest of middleware
]
```

## ✅ Current CORS Setup

Your API now allows requests from:
- ✅ `http://localhost:8081` (Your frontend)
- ✅ `http://localhost:8000` (Django server)
- ✅ `http://localhost:3000` (React/Vue dev server)
- ✅ IPv4 versions (127.0.0.1)

## API Endpoints Now Accessible

All endpoints are now accessible from `http://localhost:8081`:

```javascript
// Property endpoints
GET /api/v1/properties/
GET /api/v1/properties/{id}/
GET /api/v1/properties/{id}/occupancy_detail/
GET /api/v1/properties/{id}/summary/

// Occupancy endpoints
GET /api/v1/occupancy/
GET /api/v1/occupancy/occupied/
GET /api/v1/occupancy/available/

// Residents
GET /api/v1/residents/
GET /api/v1/residents/due_soon/
GET /api/v1/residents/overdue/

// Other endpoints
GET /api/v1/floors/
GET /api/v1/rooms/
GET /api/v1/beds/
GET /api/v1/expenses/
GET /api/v1/payments/
GET /api/v1/maintenance-requests/
```

## Server Status

✅ Django Server: Running on http://localhost:8000
✅ CORS Enabled: For port 8081
✅ API Ready: For your frontend

Start making requests from `http://localhost:8081/occupancy` now!
