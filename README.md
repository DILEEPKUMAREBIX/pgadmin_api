# PG Admin REST API

A comprehensive Django REST Framework API for managing residential properties, residents, occupancy, expenses, payments, and maintenance requests.

## Project Overview

This is a complete REST API backend for the PG Admin mobile application. It provides a complete data management system for:
- **Properties**: Manage multiple residential properties
- **Residents**: Track resident information, payments, and history
- **Occupancy**: Manage bed/room occupancy status
- **Expenses**: Track property expenses
- **Payments**: Record resident rent payments
- **Maintenance**: Manage maintenance requests
- **Users**: User authentication and role management

## Technology Stack

- **Framework**: Django 4.2.7
- **API**: Django REST Framework 3.14.0
- **Database**: PostgreSQL
- **Database Adapter**: psycopg2-binary 2.9.9
- **Documentation**: drf-spectacular 0.26.5 (Swagger/OpenAPI)
- **CORS**: django-cors-headers 4.3.0
- **Filtering**: django-filter 23.4
- **Server**: gunicorn 21.2.0 (production)

## Database Schema

### 11 Core Models

1. **Property** - Residential property information
2. **Floor** - Floor levels within properties
3. **Room** - Individual rooms on floors
4. **Bed** - Individual beds within rooms
5. **Resident** - Resident/tenant information
6. **Occupancy** - Current occupancy status of beds
7. **OccupancyHistory** - Historical occupancy changes
8. **Expense** - Property-related expenses
9. **Payment** - Resident rent payments
10. **MaintenanceRequest** - Maintenance issue tracking
11. **User** - System users and authentication

## Installation & Setup

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Virtual Environment (venv)

### Step 1: Clone or Create Project

```bash
cd C:\Users\kotta\OneDrive\Desktop\PGAdmin\PGAdmin-Backend
```

### Step 2: Activate Virtual Environment

**Windows:**
```bash
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Database

Create PostgreSQL database:
```sql
CREATE DATABASE pgadmin_db;
```

Update database credentials in `pgadmin_config/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Step 5: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

### Step 7: Load Sample Data (Optional)

If you have the SQL file with sample data:
```bash
python manage.py shell

# Or use psql to load from SQL file
psql -U postgres -d pgadmin_db -f pgadmin_database_setup.sql
```

### Step 8: Run Development Server

```bash
python manage.py runserver
```

Server will be available at: http://localhost:8000

## API Documentation

### API Base URL
```
http://localhost:8000/api/v1/
```

### Swagger/OpenAPI Documentation
- **Interactive Docs**: http://localhost:8000/api/docs/
- **Schema**: http://localhost:8000/api/schema/

### Available Endpoints

#### Properties
- `GET/POST /api/v1/properties/` - List/create properties
- `GET /api/v1/properties/{id}/` - Get property details
- `PUT/PATCH /api/v1/properties/{id}/` - Update property
- `DELETE /api/v1/properties/{id}/` - Delete property
- `GET /api/v1/properties/{id}/summary/` - Get property summary with stats

#### Residents
- `GET/POST /api/v1/residents/` - List/create residents
- `GET /api/v1/residents/{id}/` - Get resident details
- `PUT/PATCH /api/v1/residents/{id}/` - Update resident
- `DELETE /api/v1/residents/{id}/` - Delete resident
- `GET /api/v1/residents/due_soon/` - Residents with payment due soon
- `GET /api/v1/residents/overdue/` - Residents with overdue payments

#### Occupancy
- `GET/POST /api/v1/occupancy/` - List/create occupancy records
- `GET /api/v1/occupancy/{id}/` - Get occupancy details
- `PUT/PATCH /api/v1/occupancy/{id}/` - Update occupancy
- `DELETE /api/v1/occupancy/{id}/` - Delete occupancy
- `GET /api/v1/occupancy/occupied/` - Get all occupied beds
- `GET /api/v1/occupancy/available/` - Get all available beds

#### Expenses
- `GET/POST /api/v1/expenses/` - List/create expenses
- `GET /api/v1/expenses/{id}/` - Get expense details
- `PUT/PATCH /api/v1/expenses/{id}/` - Update expense
- `DELETE /api/v1/expenses/{id}/` - Delete expense
- `GET /api/v1/expenses/summary/` - Get expense summary
- `GET /api/v1/expenses/by_category/` - Expenses grouped by category

#### Payments
- `GET/POST /api/v1/payments/` - List/create payments
- `GET /api/v1/payments/{id}/` - Get payment details
- `PUT /api/v1/payments/{id}/` - Update payment
- `GET /api/v1/payments/summary/` - Get payment summary
- `GET /api/v1/payments/by_resident/` - Payments by resident

#### Maintenance Requests
- `GET/POST /api/v1/maintenance-requests/` - List/create requests
- `GET /api/v1/maintenance-requests/{id}/` - Get request details
- `PUT/PATCH /api/v1/maintenance-requests/{id}/` - Update request
- `POST /api/v1/maintenance-requests/{id}/resolve/` - Mark as resolved
- `GET /api/v1/maintenance-requests/open_requests/` - Get open requests
- `GET /api/v1/maintenance-requests/by_priority/` - Requests grouped by priority

#### Floors, Rooms, Beds
- `GET/POST /api/v1/floors/` - List/create floors
- `GET/POST /api/v1/rooms/` - List/create rooms
- `GET/POST /api/v1/beds/` - List/create beds
- Full CRUD operations available for each

#### Occupancy History
- `GET /api/v1/occupancy-history/` - List all changes
- `GET /api/v1/occupancy-history/?resident_id=1` - Changes for specific resident

#### Users
- `GET/POST /api/v1/users/` - List/create users
- `GET /api/v1/users/{id}/` - Get user details
- `PUT/PATCH /api/v1/users/{id}/` - Update user
- `DELETE /api/v1/users/{id}/` - Delete user

## Query Parameters

### Filtering
Most endpoints support filtering:
```
GET /api/v1/residents/?property=1&is_active=true
GET /api/v1/expenses/?category=Electricity
GET /api/v1/occupancy/?is_occupied=false
```

### Search
Search supported on endpoints with search_fields:
```
GET /api/v1/residents/?search=John
GET /api/v1/rooms/?search=A101
GET /api/v1/users/?search=admin@example.com
```

### Ordering
```
GET /api/v1/residents/?ordering=-next_pay_date
GET /api/v1/payments/?ordering=-payment_date
```

### Pagination
Default page size: 20 items
```
GET /api/v1/residents/?page=2&page_size=50
```

## Request/Response Examples

### Create a Resident
```bash
POST /api/v1/residents/
Content-Type: application/json

{
  "property": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "mobile": "9876543210",
  "rent": "5000.00",
  "rent_type": "monthly",
  "joining_date": "2024-01-15",
  "next_pay_date": "2024-02-15"
}
```

### Get Overdue Residents
```bash
GET /api/v1/residents/overdue/
```

### Record a Payment
```bash
POST /api/v1/payments/
Content-Type: application/json

{
  "property": 1,
  "resident": 1,
  "resident_name": "John Doe",
  "amount": "5000.00",
  "payment_method": "bank_transfer",
  "reference_number": "TXN123456"
}
```

### Get Property Summary
```bash
GET /api/v1/properties/1/summary/
```

## Admin Interface

Access the Django Admin interface at:
```
http://localhost:8000/admin/
```

Login with the superuser credentials created earlier.

## Production Deployment

### Using Gunicorn
```bash
gunicorn pgadmin_config.wsgi:application --bind 0.0.0.0:8000
```

### Environment Variables
Create a `.env` file for sensitive configuration:
```
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_NAME=pgadmin_db
DB_USER=postgres
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432
```

### CORS Configuration
Update CORS settings in `pgadmin_config/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    'https://yourdomain.com',
    'https://www.yourdomain.com',
]
```

## Development Workflow

### Creating a New Endpoint

1. Add model to `properties/models.py`
2. Create serializer in `properties/serializers.py`
3. Create viewset in `properties/views.py`
4. Register in `properties/urls.py`
5. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### Running Tests
```bash
python manage.py test properties
```

### Linting and Formatting
```bash
# Install linters
pip install flake8 black isort

# Format code
black properties/

# Check linting
flake8 properties/
```

## File Structure

```
PGAdmin-Backend/
├── pgadmin_config/           # Main project configuration
│   ├── settings.py           # Django settings
│   ├── urls.py               # Main URL configuration
│   ├── wsgi.py               # WSGI application
│   └── asgi.py               # ASGI application
├── properties/               # Main app
│   ├── migrations/           # Database migrations
│   ├── models.py             # 11 database models
│   ├── serializers.py        # DRF serializers
│   ├── views.py              # ViewSets and API logic
│   ├── urls.py               # App URL routing
│   ├── admin.py              # Django admin configuration
│   └── apps.py               # App configuration
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## API Features

✅ Full CRUD operations for all models
✅ Advanced filtering and searching
✅ Pagination with configurable page size
✅ Ordering by multiple fields
✅ Nested relationships serialization
✅ Token-based authentication ready
✅ Comprehensive API documentation (Swagger/OpenAPI)
✅ CORS enabled for cross-origin requests
✅ Optimized database queries with select_related/prefetch_related
✅ Database indexes on frequently queried fields
✅ Custom actions for business logic (due_soon, overdue, summary, etc.)

## Troubleshooting

### Database Connection Error
```
Error: could not translate host name "localhost" to address
```
Solution: Ensure PostgreSQL is running and database credentials are correct.

### Migration Conflicts
```bash
python manage.py migrate --fake-initial
```

### Port Already in Use
```bash
python manage.py runserver 8001
```

## Support & Documentation

- Django Documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- PostgreSQL: https://www.postgresql.org/docs/

## License

Proprietary - PG Admin Management System

## Contact

For issues or questions, contact the development team.
