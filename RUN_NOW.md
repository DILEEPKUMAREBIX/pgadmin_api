# 🚀 QUICK START - Run Your Django API in 5 Minutes

## Step 1: Open PowerShell

Press `Windows + R` and type:
```
powershell
```

Then press Enter.

---

## Step 2: Navigate to Project Folder

Copy and paste this command:

```bash
cd C:\Users\kotta\OneDrive\Desktop\PGAdmin\PGAdmin-Backend
```

Press Enter. You should see:
```
C:\Users\kotta\OneDrive\Desktop\PGAdmin\PGAdmin-Backend>
```

---

## Step 3: Activate Virtual Environment

Copy and paste:

```bash
.\.venv\Scripts\Activate.ps1
```

Press Enter.

**If you get an error**, run this first:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then press `Y` and try the activation command again.

**Success looks like:**
```
(.venv) C:\Users\kotta\OneDrive\Desktop\PGAdmin\PGAdmin-Backend>
```

Notice the `(.venv)` at the beginning - that means it's activated! ✅

---

## Step 4: Run Migrations (First Time Only)

This creates the database tables:

```bash
python manage.py migrate
```

You'll see lots of `OK` messages. Wait for it to finish.

---

## Step 5: Start the Server

This is the main command to run your API:

```bash
python manage.py runserver
```

**Wait for this message:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

---

## Step 6: Open Your Browser

Open any web browser (Chrome, Edge, Firefox) and go to:

```
http://localhost:8000/api/docs/
```

You should see a beautiful interactive API interface! 🎉

---

## 📋 What You Can Do Now

### Browse All Endpoints
You can see all available API endpoints like:
- `/residents/` - Manage residents
- `/properties/` - Manage properties
- `/expenses/` - Track expenses
- `/payments/` - Record payments
- And many more!

### Test the API
Click on any endpoint (like `/residents/`) and click "Try it out" to test it!

### View Admin Panel
Go to: http://localhost:8000/admin/
(You'll need to create a user first - see below)

---

## 🛑 To Stop the Server

In PowerShell, press:
```
CTRL + C
```

The server will stop. You'll see:
```
KeyboardInterrupt: Quit the server with CONTROL-C
```

---

## ➕ Optional: Load Sample Data

If you want test data to play with:

```bash
python manage.py load_sample_data
```

This adds:
- 2 sample properties
- 2 sample residents
- Sample expenses and payments
- Sample maintenance requests

Then refresh your browser or visit `/api/docs/` again to see the data!

---

## 🔐 Optional: Create Admin User

To access the admin panel at `/admin/`:

```bash
python manage.py createsuperuser
```

Follow the prompts:
- Username: `admin`
- Email: `admin@example.com`
- Password: `(type something secure)`

Then you can login at http://localhost:8000/admin/

---

## 🎯 Common URLs

| URL | Purpose |
|-----|---------|
| http://localhost:8000/api/docs/ | Interactive API documentation |
| http://localhost:8000/admin/ | Admin panel (after creating superuser) |
| http://localhost:8000/api/v1/residents/ | See all residents |
| http://localhost:8000/api/v1/properties/ | See all properties |
| http://localhost:8000/api/v1/expenses/ | See all expenses |
| http://localhost:8000/api/schema/ | API schema (for tools) |

---

## 📖 Next Steps

1. ✅ **Run the server** (you just did this!)
2. 📚 **Explore the API** - Click around in `/api/docs/`
3. 🧪 **Test endpoints** - Click "Try it out" on any endpoint
4. 📱 **Connect your mobile app** - Use `http://your-server:8000/api/v1/` as base URL
5. 📚 **Read full docs** - Check `README.md` for complete reference

---

## ✨ Example: Test Get Residents

1. Go to: http://localhost:8000/api/docs/
2. Scroll down to find `residents` endpoint
3. Look for `GET /api/v1/residents/`
4. Click on it to expand
5. Click blue "Try it out" button
6. Click "Execute"
7. See the response!

---

## 🆘 If Something Goes Wrong

### Error: "Connection refused"
- PostgreSQL might not be running
- Restart PostgreSQL and try again

### Error: "Port 8000 in use"
- Something else is using port 8000
- Use: `python manage.py runserver 8001`

### Error: "ModuleNotFoundError: No module named 'django'"
- Virtual environment not activated
- Check if `(.venv)` shows in your prompt
- If not, run activation command again

### Error: "Module not found: psycopg2"
```bash
pip install --upgrade psycopg2-binary
```

### Error: Database doesn't exist
```bash
python manage.py migrate
```

---

## 🎉 Congratulations!

Your Django REST API is now **running and ready to use**!

- ✅ Server is running at `http://localhost:8000/`
- ✅ API is available at `http://localhost:8000/api/v1/`
- ✅ Documentation at `http://localhost:8000/api/docs/`
- ✅ Your mobile app can now connect!

### Keep the server running while you develop!

To stop: Press `CTRL + C`
To start again: Run `python manage.py runserver`

---

**Enjoy building with Django! 🚀**
