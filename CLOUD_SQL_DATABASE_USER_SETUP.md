# 🗄️ Cloud SQL: Create Database & User - Complete Guide

## Overview

This guide walks you through creating a PostgreSQL database and user in Google Cloud SQL with detailed screenshots and explanations.

**Estimated Time:** 10-15 minutes  
**Difficulty:** Easy

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Method 1: Using GCP Console (GUI)](#method-1-using-gcp-console-gui)
3. [Method 2: Using gcloud CLI](#method-2-using-gcloud-cli)
4. [Method 3: Using psql (SQL Commands)](#method-3-using-psql-sql-commands)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, you should have:
- ✅ GCP Account created
- ✅ Cloud SQL PostgreSQL instance created (`pgadmin-db`)
- ✅ Instance is in "RUNNABLE" status
- ✅ Root password set for postgres user

**Verify:**
1. Go to [Cloud SQL Console](https://console.cloud.google.com/sql/instances)
2. You should see `pgadmin-db` with status "✓ Running"

---

## Method 1: Using GCP Console (GUI) - EASIEST

### Step 1: Go to Cloud SQL Instance

1. Open [GCP Console](https://console.cloud.google.com)
2. Go to **SQL → Instances**
3. Click on your instance: **`pgadmin-db`**

### Step 2: Create Database

#### Step 2.1: Navigate to Databases Tab

In your Cloud SQL instance page:
- Click the **"DATABASES"** tab (top menu)
- Currently should show only `postgres` database

#### Step 2.2: Create New Database

1. Click **"CREATE DATABASE"** button
2. Dialog appears with fields:

```
┌─────────────────────────────────────┐
│ Create a database                   │
├─────────────────────────────────────┤
│                                     │
│ Database ID: [_________________]   │
│                                     │
│ Collation: (use_default) ✓         │
│                                     │
│ Character set: (utf8)              │
│                                     │
│ [CANCEL]  [CREATE DATABASE]        │
└─────────────────────────────────────┘
```

3. Enter: **`pgadmin_production`**
4. Leave other fields as default
5. Click **"CREATE DATABASE"**

**Wait:** Database creation takes ~30 seconds

**Success:** You should see `pgadmin_production` listed under DATABASES

---

### Step 3: Create Database User

#### Step 3.1: Navigate to Users Tab

In your Cloud SQL instance page:
- Click the **"USERS"** tab (top menu)
- Currently shows the `postgres` user

#### Step 3.2: Create New User

1. Click **"CREATE USER ACCOUNT"** button
2. Dialog appears:

```
┌─────────────────────────────────────┐
│ Create a user                       │
├─────────────────────────────────────┤
│                                     │
│ User name: [_________________]     │
│                                     │
│ Password:  [_________________]     │
│            [Show password]          │
│                                     │
│ [CANCEL]  [CREATE USER]            │
└─────────────────────────────────────┘
```

3. Enter **Username:** `pgadmin_user`
4. Enter **Password:** Create a strong password
   - Must be at least 8 characters
   - Include: uppercase, lowercase, numbers, symbols
   - Example: `SecureP@ss123!`
5. **SAVE THIS PASSWORD SECURELY!**
6. Click **"CREATE USER"**

**Wait:** User creation takes ~10 seconds

**Success:** You should see `pgadmin_user` listed under USERS

---

### Step 4: Grant Permissions to User

#### Step 4.1: Connect to Database

To grant permissions, we need to connect using the `postgres` admin user.

1. In your Cloud SQL instance page
2. Click the **"CONNECT"** button
3. Choose **"Open Cloud Shell"**

A Cloud Shell terminal will open at the bottom

#### Step 4.2: Connect as Postgres

In Cloud Shell, type:

```bash
gcloud sql connect pgadmin-db --user=postgres
```

You'll be prompted:
```
Connecting to database with SQL user [postgres].
Connecting to instance [pgadmin-db].
```

Enter your postgres password (set during instance creation)

You should see the PostgreSQL prompt:
```
postgres=>
```

#### Step 4.3: Grant Permissions

Copy and paste this command:

```sql
GRANT ALL PRIVILEGES ON DATABASE pgadmin_production TO pgadmin_user;
```

Press Enter. You should see:
```
GRANT
```

Then run these commands (copy-paste each):

```sql
-- Set default settings for the user
ALTER ROLE pgadmin_user SET client_encoding TO 'utf8';
ALTER ROLE pgadmin_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pgadmin_user SET default_transaction_deferrable TO on;
```

Each should return:
```
ALTER ROLE
```

#### Step 4.4: Verify Permissions

Run this to verify:

```sql
SELECT * FROM information_schema.role_table_grants WHERE grantee='pgadmin_user';
```

You should see results showing the permissions.

#### Step 4.5: Exit PostgreSQL

Type:
```sql
\q
```

Or press `Ctrl + D`

---

## Method 2: Using gcloud CLI

If you prefer command-line, use these commands:

### Step 1: Create Database

```bash
# Create the database
gcloud sql databases create pgadmin_production \
  --instance=pgadmin-db

# Output should show:
# Creating Cloud SQL database [pgadmin_production]...done.
```

### Step 2: Create User

```bash
# Create the user with password
gcloud sql users create pgadmin_user \
  --instance=pgadmin-db \
  --password=YOUR_STRONG_PASSWORD

# Replace YOUR_STRONG_PASSWORD with an actual strong password
# Output should show:
# Creating user [pgadmin_user]...done.
```

### Step 3: Grant Permissions

```bash
# Connect to database
gcloud sql connect pgadmin-db --user=postgres

# Then run (from the sql prompt):
GRANT ALL PRIVILEGES ON DATABASE pgadmin_production TO pgadmin_user;
ALTER ROLE pgadmin_user SET client_encoding TO 'utf8';
ALTER ROLE pgadmin_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pgadmin_user SET default_transaction_deferrable TO on;

# Exit
\q
```

---

## Method 3: Using psql (SQL Commands)

If you have psql installed locally:

### Step 1: Get Connection Info

Go to your Cloud SQL instance → **CONNECTIVITY** tab

Copy the **Public IP** (e.g., `35.192.xxx.xxx`)

### Step 2: Connect Locally

```bash
# Install psql if needed (PostgreSQL client)
# For Windows: https://www.postgresql.org/download/windows/
# For Mac: brew install postgresql
# For Linux: sudo apt-get install postgresql-client

# Connect to the database
psql -h YOUR_PUBLIC_IP -U postgres -d postgres

# You'll be prompted for password
# Enter the postgres root password you set
```

### Step 3: Create Database and User

Once connected (you see `postgres=>`):

```sql
-- Create database
CREATE DATABASE pgadmin_production;

-- Create user
CREATE USER pgadmin_user WITH PASSWORD 'YOUR_STRONG_PASSWORD';

-- Grant permissions
ALTER ROLE pgadmin_user SET client_encoding TO 'utf8';
ALTER ROLE pgadmin_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pgadmin_user SET default_transaction_deferrable TO on;
GRANT ALL PRIVILEGES ON DATABASE pgadmin_production TO pgadmin_user;

-- Exit
\q
```

---

## Verification

### Check Database Exists

**Using gcloud:**
```bash
gcloud sql databases list --instance=pgadmin-db
```

Should show:
```
NAME                  CHARSET  COLLATION
pgadmin_production    UTF8     en_US.utf8
postgres              UTF8     en_US.utf8
template0             UTF8     en_US.utf8
template1             UTF8     en_US.utf8
```

**Or in GCP Console:**
1. Cloud SQL → Instances → `pgadmin-db`
2. Click **DATABASES** tab
3. Should list `pgadmin_production` ✅

### Check User Exists

**Using gcloud:**
```bash
gcloud sql users list --instance=pgadmin-db
```

Should show:
```
NAME          TYPE
pgadmin_user  BUILT_IN
postgres      BUILT_IN
```

**Or in GCP Console:**
1. Cloud SQL → Instances → `pgadmin-db`
2. Click **USERS** tab
3. Should list `pgadmin_user` ✅

### Test Connection

Connect as the new user:

```bash
gcloud sql connect pgadmin-db --user=pgadmin_user
```

Enter the password you set.

You should see:
```
pgadmin_user=>
```

If you can connect, everything is set up correctly! ✅

---

## Troubleshooting

### Issue 1: Database Creation Failed

**Error:** "Database already exists" or "Invalid database name"

**Solution:**
- Name must start with letter
- No special characters except underscore
- Keep it lowercase
- Try: `pgadmin_production` (with underscore)

**Fix:**
```bash
gcloud sql databases create pgadmin_production \
  --instance=pgadmin-db
```

---

### Issue 2: User Creation Failed

**Error:** "Username already exists"

**Solution:**
- Use a different username (or delete existing first)
- Try: `pgadmin_user` or `pgadmin_app_user`

**If username taken, delete it first:**
```bash
gcloud sql users delete pgadmin_user --instance=pgadmin-db
```

Then create again:
```bash
gcloud sql users create pgadmin_user \
  --instance=pgadmin-db \
  --password=YourStrongPassword123!
```

---

### Issue 3: Permission Denied When Connecting

**Error:** "FATAL: role does not exist" or "password authentication failed"

**Solution:**
- Verify username: `pgadmin_user` (lowercase)
- Verify password is correct
- Check permissions were granted
- Try connecting as postgres first to verify database exists:

```bash
gcloud sql connect pgadmin-db --user=postgres
# Then list databases:
\l
```

---

### Issue 4: Can't Verify Permissions

**If you can't run GRANT command:**

Reconnect as postgres:
```bash
gcloud sql connect pgadmin-db --user=postgres
```

Run permissions again:
```sql
GRANT ALL PRIVILEGES ON DATABASE pgadmin_production TO pgadmin_user;
ALTER ROLE pgadmin_user SET client_encoding TO 'utf8';
ALTER ROLE pgadmin_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pgadmin_user SET default_transaction_deferrable TO on;
```

Verify:
```sql
SELECT * FROM information_schema.role_table_grants WHERE grantee='pgadmin_user';
```

---

## Summary of What Was Created

### Database
- **Name:** `pgadmin_production`
- **Type:** PostgreSQL
- **Encoding:** UTF-8
- **Owner:** postgres (admin)
- **Access:** pgadmin_user can read/write

### User
- **Username:** `pgadmin_user`
- **Type:** PostgreSQL user
- **Permissions:** Full access to `pgadmin_production` database
- **Connection:** Can connect from Cloud Run

---

## Connection String for Django

Once created, use this in your Django settings:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pgadmin_production',        # ← Database name
        'USER': 'pgadmin_user',              # ← Username
        'PASSWORD': 'YOUR_PASSWORD',         # ← Password you set
        'HOST': 'YOUR_CLOUD_SQL_IP',        # ← Cloud SQL IP
        'PORT': '5432',                      # ← PostgreSQL default port
    }
}
```

---

## Next Steps

After creating database and user:

1. ✅ Get the Cloud SQL private or public IP
2. ✅ Store password in GCP Secret Manager
3. ✅ Update Django settings.py
4. ✅ Update Cloud Build secrets
5. ✅ Deploy to Cloud Run

---

## Quick Reference

| Item | Value |
|------|-------|
| **Instance Name** | `pgadmin-db` |
| **Database Name** | `pgadmin_production` |
| **Database User** | `pgadmin_user` |
| **Admin User** | `postgres` |
| **Default Port** | `5432` |
| **Encoding** | UTF-8 |

---

## Common Commands Cheatsheet

```bash
# List databases
gcloud sql databases list --instance=pgadmin-db

# List users
gcloud sql users list --instance=pgadmin-db

# Connect as postgres
gcloud sql connect pgadmin-db --user=postgres

# Connect as pgadmin_user
gcloud sql connect pgadmin-db --user=pgadmin_user

# Create database (if needed again)
gcloud sql databases create pgadmin_production --instance=pgadmin-db

# Create user (if needed again)
gcloud sql users create pgadmin_user --instance=pgadmin-db --password=PASSWORD

# Delete user (if needed)
gcloud sql users delete pgadmin_user --instance=pgadmin-db

# Get instance details
gcloud sql instances describe pgadmin-db
```

---

## Success Criteria

✅ You successfully set up Cloud SQL when:

- [ ] Database `pgadmin_production` exists
- [ ] User `pgadmin_user` exists
- [ ] User can connect to database
- [ ] User has permissions to read/write
- [ ] Connection string tested locally

---

**When all items are verified, you're ready to connect from Django!** 🚀
