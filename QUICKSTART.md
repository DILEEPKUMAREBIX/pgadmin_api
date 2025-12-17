# Quick Start Guide - PG Admin REST API

## 🚀 Prerequisites

- Python 3.8+
- PostgreSQL 12+ running and accessible
- Git (optional)

## 📋 Step-by-Step Setup

### 1️⃣ Create PostgreSQL Database

Open PostgreSQL client (psql) or pgAdmin and run:

```sql
CREATE DATABASE pgadmin_db;
```

### 2️⃣ Navigate to Project Directory

```bash
cd C:\Users\kotta\OneDrive\Desktop\PGAdmin\PGAdmin-Backend
```

### 3️⃣ Activate Virtual Environment

```bash
.venv\Scripts\activate
```

### 4️⃣ Create .env File (Optional but Recommended)

Copy `.env.example` to `.env` and update with your database credentials:

```bash
copy .env.example .env
```

Edit `.env` with your PostgreSQL credentials.

### 5️⃣ Install Dependencies (if needed)

```bash
pip install -r requirements.txt
```

### 6️⃣ Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7️⃣ Load Sample Data (Optional)

```bash
python manage.py load_sample_data
```

### 8️⃣ Create Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 9️⃣ Start Development Server

```bash
python manage.py runserver
```

You should see:

```
Starting development server at http://127.0.0.1:8000/
```

## 🌐 Access the API

### Interactive Documentation
Open your browser and go to:

```
http://localhost:8000/api/docs/
```

This opens the **Swagger UI** where you can:
- Browse all available endpoints
- View request/response examples
- Test endpoints directly
- See automatic documentation

### Admin Panel
```
http://localhost:8000/admin/
```

Login with your superuser credentials to manage data directly.

### API Base URL
```
http://localhost:8000/api/v1/
```

## 🔍 Test API Endpoints

### Using Curl

**Get all residents:**
```bash
curl http://localhost:8000/api/v1/residents/
```

**Get residents due for payment:**
```bash
curl http://localhost:8000/api/v1/residents/due_soon/
```

**Create a new expense:**
```bash
curl -X POST http://localhost:8000/api/v1/expenses/ \
  -H "Content-Type: application/json" \
  -d "{\"property\": 1, \"amount\": 1200, \"category\": \"Electricity\", \"description\": \"Monthly bill\", \"expense_date\": \"2024-01-15T00:00:00Z\"}"
```

### Using Postman

1. Import the Swagger schema:
   - URL: `http://localhost:8000/api/schema/`
   
2. Create requests using the API Base URL:
   - `http://localhost:8000/api/v1/`

## 📱 Mobile App Integration

Your mobile app can now consume the API:

```javascript
// Example: React Native / Flutter
const API_URL = 'http://your-server:8000/api/v1';

// Get all residents
fetch(`${API_URL}/residents/`)
  .then(res => res.json())
  .then(data => console.log(data));

// Filter residents due for payment
fetch(`${API_URL}/residents/due_soon/`)
  .then(res => res.json())
  .then(data => console.log(data));
```

## 🛑 Troubleshooting

### Error: "could not translate host name"
**Solution**: PostgreSQL is not running or database doesn't exist.
```bash
# Create the database again
# In PostgreSQL client:
CREATE DATABASE pgadmin_db;
```

### Error: "psycopg2 module not found"
**Solution**: Reinstall psycopg2
```bash
pip install --upgrade psycopg2-binary
```

### Error: "No such table"
**Solution**: Run migrations
```bash
python manage.py migrate
```

### Port 8000 already in use
**Solution**: Use a different port
```bash
python manage.py runserver 8001
```

## 📚 Available Endpoints Quick Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/properties/` | List all properties |
| POST | `/properties/` | Create new property |
| GET | `/residents/` | List all residents |
| GET | `/residents/due_soon/` | Residents with payment due soon |
| GET | `/residents/overdue/` | Residents with overdue payments |
| GET | `/occupancy/occupied/` | Get occupied beds |
| GET | `/occupancy/available/` | Get available beds |
| POST | `/expenses/` | Record new expense |
| GET | `/expenses/summary/` | Get expense summary |
| POST | `/payments/` | Record new payment |
| GET | `/payments/summary/` | Get payment summary |
| POST | `/maintenance-requests/` | Create maintenance request |
| POST | `/maintenance-requests/{id}/resolve/` | Mark as resolved |

See full API documentation at: `http://localhost:8000/api/docs/`

## ⚙️ Configuration Files

- **`pgadmin_config/settings.py`** - Main Django settings
- **`pgadmin_config/urls.py`** - URL routing
- **`properties/models.py`** - Database models
- **`properties/serializers.py`** - API serializers
- **`properties/views.py`** - API viewsets
- **`.env`** - Environment variables (create from .env.example)

## 🔐 Security Notes

For production:
1. Change `SECRET_KEY` in settings.py
2. Set `DEBUG = False`
3. Update `ALLOWED_HOSTS`
4. Use environment variables for sensitive data
5. Enable HTTPS
6. Set strong database password
7. Configure CORS for your frontend domain

## 📝 Useful Django Commands

```bash
# Check configuration
python manage.py check

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Access Django shell
python manage.py shell

# Create superuser
python manage.py createsuperuser

# Collect static files (production)
python manage.py collectstatic

# Run tests
python manage.py test

# Load sample data
python manage.py load_sample_data
```

## 📖 Additional Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **Django REST Framework**: https://www.django-rest-framework.org/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Swagger UI**: The interactive documentation at `/api/docs/`

## 💡 Next Steps

1. ✅ API is running
2. Test endpoints using Swagger UI at `/api/docs/`
3. Create your mobile app to consume the API
4. Implement authentication in your frontend
5. Configure CORS for your frontend domain
6. Deploy to production when ready

## 🆘 Need Help?

Check the detailed documentation:
- `README.md` - Complete API reference
- `API_SETUP_SUMMARY.md` - Setup summary
- `.env.example` - Configuration template

---

**Happy coding! 🎉**

The API is ready to power your PG Admin mobile application.
