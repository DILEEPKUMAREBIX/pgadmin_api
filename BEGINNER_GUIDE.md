# 🎓 Beginner's Guide to Running Django Application

## What is Django?
Django is a Python framework that helps you build web applications and APIs (like this one). Think of it as a toolkit that handles the complex parts so you can focus on your app's features.

## What is an API?
An API (Application Programming Interface) lets your mobile app communicate with a server. Our API manages residents, expenses, payments, and more for your PG Admin app.

---

## 📋 Prerequisites Check

Before starting, you need:
1. **Python** - Programming language (you already have: 3.14.0)
2. **PostgreSQL** - Database (need to install/verify)
3. **Virtual Environment** - Isolated Python workspace (already created: `.venv`)

### Verify Python Installation
```bash
python --version
```

Should show: `Python 3.14.0` or similar

### Verify PostgreSQL Installation
```bash
psql --version
```

Should show: `psql (PostgreSQL) 12.0` or higher

If you don't have PostgreSQL installed:
- **Windows**: Download from https://www.postgresql.org/download/windows/
- **macOS**: Install via Homebrew: `brew install postgresql`
- **Linux**: `sudo apt-get install postgresql`

---

## 🚀 Step 1: Navigate to Your Project

Open PowerShell and go to your project folder:

```bash
cd C:\Users\kotta\OneDrive\Desktop\PGAdmin\PGAdmin-Backend
```

You should see your project files and a folder named `.venv` (the virtual environment).

---

## 🔧 Step 2: Activate Virtual Environment

A virtual environment is like a separate Python workspace for this project. It keeps dependencies isolated.

**On Windows PowerShell:**
```bash
.\.venv\Scripts\Activate.ps1
```

**If you get an error** about execution policy, run this first:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again.

**If activation works**, you should see `(.venv)` at the start of your command prompt:
```
(.venv) C:\Users\kotta\OneDrive\Desktop\PGAdmin\PGAdmin-Backend>
```

---

## 📦 Step 3: Install Dependencies

The project needs several Python packages to run. These are listed in `requirements.txt`.

Install them using pip (Python's package manager):

```bash
pip install -r requirements.txt
```

**What this does:**
- Installs Django (the web framework)
- Installs DRF (Django REST Framework)
- Installs psycopg2 (PostgreSQL connector)
- Installs other necessary packages

**This takes 2-3 minutes.** You'll see `Successfully installed...` messages.

---

## 🗄️ Step 4: Create PostgreSQL Database

Open PostgreSQL client (pgAdmin or psql) and create a database:

**Using psql (command line):**
```bash
psql -U postgres
```

When prompted for password, enter your PostgreSQL password.

Then run:
```sql
CREATE DATABASE pgadmin_db;
\q
```

The `\q` command exits psql.

**Using pgAdmin (GUI):**
1. Open pgAdmin
2. Right-click "Databases"
3. Create → Database
4. Name it: `pgadmin_db`
5. Click Save

---

## 🔄 Step 5: Run Database Migrations

Migrations are like "database update scripts" that create tables and structure.

Run this command:

```bash
python manage.py migrate
```

You'll see messages like:
```
Running migrations:
  Applying admin.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying properties.0001_initial... OK
```

This creates all the database tables for your API.

---

## 📥 Step 6: Load Sample Data (Optional)

Want to test with real-looking data? Load samples:

```bash
python manage.py load_sample_data
```

This creates:
- 2 sample properties
- 2 sample residents
- Sample expenses and payments
- Sample maintenance requests

---

## 👤 Step 7: Create Admin User (Optional but Recommended)

Create an admin account to access the Django admin interface:

```bash
python manage.py createsuperuser
```

Answer the prompts:
```
Username: admin
Email: admin@example.com
Password: (type password - won't show)
Password (again): (confirm)
```

---

## ✅ Step 8: Verify Everything Works

Run Django's system check:

```bash
python manage.py check
```

Should output:
```
System check identified no issues (0 silenced).
```

---

## 🎯 Step 9: Start the Development Server

**This is the main command to run your API:**

```bash
python manage.py runserver
```

You should see:
```
Watching for file changes with StatReloader
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

**Congratulations! Your API is now running! 🎉**

---

## 🌐 Step 10: Access Your API

Open your web browser and visit:

### 📚 **Interactive API Documentation** (Best for beginners!)
```
http://localhost:8000/api/docs/
```

This is where you can:
- See all available endpoints
- Read what each endpoint does
- Test requests right from your browser
- See example responses

### 🔧 **Admin Panel**
```
http://localhost:8000/admin/
```

Login with admin username/password you created.
View and edit all data directly.

### 🔌 **API Base URL**
```
http://localhost:8000/api/v1/
```

This is where your mobile app will send requests.

---

## 📱 Example: Test the API

### In Browser

1. Go to: http://localhost:8000/api/v1/properties/
2. You should see JSON data (if you loaded sample data)

### Using Python

Create a file `test_api.py`:

```python
import requests

API_URL = "http://localhost:8000/api/v1"

# Get all residents
response = requests.get(f"{API_URL}/residents/")
print("All Residents:")
print(response.json())

# Get residents due for payment
response = requests.get(f"{API_URL}/residents/due_soon/")
print("\nResidents Due Soon:")
print(response.json())
```

Run it:
```bash
pip install requests
python test_api.py
```

### Using cURL (Command Line)

```bash
curl http://localhost:8000/api/v1/residents/
```

---

## 🛑 Step 11: Stop the Server

Press `CTRL + C` in your terminal to stop the server.

---

## 📝 Complete Command Summary

Here's the complete flow in one place:

```bash
# 1. Navigate to project
cd C:\Users\kotta\OneDrive\Desktop\PGAdmin\PGAdmin-Backend

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations (setup database)
python manage.py migrate

# 5. Load sample data
python manage.py load_sample_data

# 6. Create admin user
python manage.py createsuperuser

# 7. Start server
python manage.py runserver
```

Then visit: http://localhost:8000/api/docs/

---

## 🔧 Useful Django Commands

Once the virtual environment is activated, you can use these:

```bash
# Check for any configuration issues
python manage.py check

# View all available commands
python manage.py help

# Create migrations (if you modify models)
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate

# Access Python shell with Django loaded
python manage.py shell

# Run tests
python manage.py test

# Load sample data
python manage.py load_sample_data

# Start development server
python manage.py runserver

# Change port (if 8000 is busy)
python manage.py runserver 8001
```

---

## ❓ Troubleshooting for Beginners

### Problem: "psycopg2 module not found"
```bash
pip install --upgrade psycopg2-binary
```

### Problem: "Could not connect to database"
- Check if PostgreSQL is running
- Verify database `pgadmin_db` exists
- Check username/password in settings.py

### Problem: "Port 8000 already in use"
```bash
# Use a different port
python manage.py runserver 8001
```

### Problem: "ModuleNotFoundError"
- Make sure virtual environment is activated
- `.venv` should be visible in your prompt

### Problem: ".venv\Scripts\Activate.ps1 cannot be loaded"
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again.

### Problem: "No module named django"
- Virtual environment might not be activated
- Check if `(.venv)` shows in prompt
- Run `pip install -r requirements.txt` again

---

## 🎓 Understanding the Flow

1. **Project Setup** → Organize files
2. **Virtual Environment** → Create isolated Python space
3. **Dependencies** → Install needed packages
4. **Database Setup** → Create database and tables
5. **Sample Data** → Load test data
6. **Admin User** → Create account for management
7. **Server Start** → Run the application
8. **Access API** → Use the web interface

---

## 📚 What's Running?

When you run `python manage.py runserver`, these things happen:

1. **Django Web Server** starts at `http://localhost:8000/`
2. **API Routes** are registered at `/api/v1/`
3. **Interactive Docs** load at `/api/docs/` (Swagger UI)
4. **Admin Interface** available at `/admin/`
5. **Database Connection** established with PostgreSQL

Your mobile app will send requests to `http://your-server:8000/api/v1/...`

---

## ✨ Next Steps After Running

1. **Explore the API** at http://localhost:8000/api/docs/
2. **Test some endpoints** - try getting residents, creating expenses
3. **Login to admin** at http://localhost:8000/admin/
4. **View the database** - create, edit, delete data
5. **Read the docs** - Check README.md for full API reference

---

## 🎯 Summary

To run your Django API:

```bash
# Activate environment
.\.venv\Scripts\Activate.ps1

# Run migrations (one time)
python manage.py migrate

# Start server
python manage.py runserver

# Visit http://localhost:8000/api/docs/
```

That's it! Your API is running and ready to use. 🚀

---

**Questions?** Check:
- `README.md` - Complete documentation
- `QUICKSTART.md` - Another quick start guide
- `API_EXAMPLES.md` - How to use the API
- `/api/docs/` - Interactive documentation

Good luck with your Django journey! 🎉
