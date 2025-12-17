# ⚡ Cloud SQL Setup - Quick Reference Card

## 🚀 Fastest Way (GUI Method - 10 Minutes)

### 1. Create Database
```
1. Go to console.cloud.google.com → SQL → Instances
2. Click pgadmin-db
3. Click "DATABASES" tab
4. Click "CREATE DATABASE"
5. Name: pgadmin_production
6. Click "CREATE DATABASE"
   ↓ Wait 30 seconds ↓
   Done! ✅
```

### 2. Create User
```
1. Click "USERS" tab (same page)
2. Click "CREATE USER ACCOUNT"
3. Username: pgadmin_user
4. Password: YourStrongPassword123!
5. Click "CREATE USER"
   ↓ Wait 10 seconds ↓
   Done! ✅
```

### 3. Grant Permissions
```
1. Click "CONNECT" → "Open Cloud Shell"
2. Paste command:
   gcloud sql connect pgadmin-db --user=postgres
3. Enter postgres password
4. Copy-paste these commands one by one:
   
   GRANT ALL PRIVILEGES ON DATABASE pgadmin_production TO pgadmin_user;
   ALTER ROLE pgadmin_user SET client_encoding TO 'utf8';
   ALTER ROLE pgadmin_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE pgadmin_user SET default_transaction_deferrable TO on;

5. Exit with: \q
   Done! ✅
```

---

## 🎯 Commands Quick Copy-Paste

### List Databases
```bash
gcloud sql databases list --instance=pgadmin-db
```

### List Users
```bash
gcloud sql users list --instance=pgadmin-db
```

### Connect as Admin
```bash
gcloud sql connect pgadmin-db --user=postgres
```

### Connect as App User
```bash
gcloud sql connect pgadmin-db --user=pgadmin_user
```

### Create Database
```bash
gcloud sql databases create pgadmin_production --instance=pgadmin-db
```

### Create User
```bash
gcloud sql users create pgadmin_user \
  --instance=pgadmin-db \
  --password=YourPassword123!
```

### Grant Permissions (via SQL)
```sql
GRANT ALL PRIVILEGES ON DATABASE pgadmin_production TO pgadmin_user;
ALTER ROLE pgadmin_user SET client_encoding TO 'utf8';
ALTER ROLE pgadmin_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pgadmin_user SET default_transaction_deferrable TO on;
```

---

## 📋 Information to Save

After setup, save this information:

```
Instance Name: pgadmin-db
Database Name: pgadmin_production
Database User: pgadmin_user
Database Password: [Your password - keep secret!]
Database Port: 5432
Database Host: [Get from Cloud SQL instance page]
```

---

## ✅ Verification Commands

```bash
# Check if database exists
gcloud sql databases list --instance=pgadmin-db | grep pgadmin_production

# Check if user exists
gcloud sql users list --instance=pgadmin-db | grep pgadmin_user

# Test connection as user
gcloud sql connect pgadmin-db --user=pgadmin_user
# Enter password, then type: SELECT 1;
# Should see: ?column?
#            1
# Type: \q to exit
```

---

## 🆘 Common Issues & Quick Fixes

| Issue | Fix |
|-------|-----|
| Database already exists | It's fine! Just verify in UI |
| User already exists | Delete first: `gcloud sql users delete pgadmin_user --instance=pgadmin-db` |
| Can't connect | Wrong password? Try: `gcloud sql users set-password pgadmin_user --instance=pgadmin-db` |
| Permission denied | Connect as postgres, not pgadmin_user |
| Can't find instance | Make sure `pgadmin-db` was created and is "Running" |

---

## 📝 Exact Names to Use

**DO NOT change these names - use exactly as shown:**
- Database: `pgadmin_production` (lowercase, with underscore)
- User: `pgadmin_user` (lowercase, with underscore)
- Admin: `postgres` (lowercase, default)
- Port: `5432` (default PostgreSQL)

---

## 🔐 Strong Password Requirements

Your password MUST have:
- ✓ 8+ characters
- ✓ Uppercase (A-Z)
- ✓ Lowercase (a-z)
- ✓ Numbers (0-9)
- ✓ Special chars (!@#$%^&*)

**Examples:**
```
MySecure@Pw123
Prod123!App
P@ssw0rd!Cloud
Secure!Pg2024
```

---

## 🔄 Flow Diagram

```
Start
  ↓
Create Cloud SQL Instance (pgadmin-db)
  ↓
Create Database (pgadmin_production)  ← You are here
  ↓
Create User (pgadmin_user)
  ↓
Grant Permissions
  ↓
Test Connection
  ↓
Get Connection Details
  ↓
Setup Django
  ↓
Deploy to Cloud Run
```

---

## 📌 What's Next After Database Setup?

1. ✅ Get Cloud SQL Host IP (from instance page)
2. ✅ Store password in Secret Manager
3. ✅ Update Django settings.py with connection details
4. ✅ Test connection from Django locally
5. ✅ Push to GitHub
6. ✅ Deploy to Cloud Run

---

## 🎓 Understanding What You Created

**Database (pgadmin_production):**
- Container for all your app data
- Will store: properties, floors, rooms, beds, residents, etc.
- Separate from postgres default database (for safety)

**User (pgadmin_user):**
- Account to access the database
- Can read/write to pgadmin_production
- Can't access other databases (safe!)
- Password-protected

**Permissions:**
- pgadmin_user can do anything in pgadmin_production
- Can't modify database structure
- Can't access system tables
- Perfect for application access

---

## 🔍 Checklist When Done

- [ ] Database pgadmin_production created
- [ ] User pgadmin_user created
- [ ] Can connect as pgadmin_user
- [ ] Permissions granted
- [ ] Password saved securely
- [ ] Host IP noted
- [ ] Ready for Django connection

---

## 💡 Pro Tips

**Tip 1:** Always use strong, unique passwords
```
Good: MyApp@123Prod!
Bad: password123
Bad: pgadmin
```

**Tip 2:** Save credentials securely
- Use GCP Secret Manager (don't commit to git!)
- Use password manager (1Password, LastPass, etc.)

**Tip 3:** Test connection after setup
- Verify user can access database
- Try running a simple query: `SELECT 1;`

**Tip 4:** Keep admin password different from app password
- postgres password (admin) - very secure
- pgadmin_user password (app) - different strong password

---

## 📞 Still Stuck?

**If database creation fails:**
- Check instance is "Running" (green checkmark)
- Wait 2-3 minutes after instance creation
- Try clicking "Refresh" in console

**If user creation fails:**
- Username might already exist - delete and recreate
- Use lowercase, no special characters

**If permission grant fails:**
- Make sure you're connected as `postgres` (not the app user)
- Run GRANT commands one by one
- Wait ~5 seconds after each command

---

## 📚 Related Guides

- **GCP_NO_DOCKER_GUIDE.md** - Main deployment guide
- **CLOUD_SQL_DATABASE_USER_SETUP.md** - Detailed setup
- **CLOUD_SQL_VISUAL_GUIDE.md** - Visual screenshots
- **GCP_DEPLOYMENT_CHECKLIST.md** - Full checklist

---

**You're doing great! Next step: Connect Django to this database!** 🚀
