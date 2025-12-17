# 📸 Cloud SQL Database & User Setup - Visual Guide

## Step-by-Step with Visual Layout

### PART 1: CREATE DATABASE

#### Step 1: Go to Cloud SQL

```
GCP Console (console.cloud.google.com)
         ↓
   Left Menu → SQL
         ↓
   Click "Instances"
         ↓
   Click "pgadmin-db"
```

**You should see:**
```
┌─────────────────────────────────────────────────────────┐
│  pgadmin-db                                     ✓ Running │
├─────────────────────────────────────────────────────────┤
│                                                           │
│ [CONNECT] [RESTART] [EDIT] [DELETE] [⋮]                │
│                                                           │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ OVERVIEW  DATABASES  USERS  BACKUPS  NETWORKING     │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

#### Step 2: Click DATABASES Tab

**Current state:**
```
┌─────────────────────────────────────────────────────────┐
│ DATABASES                                                 │
├─────────────────────────────────────────────────────────┤
│  [+ CREATE DATABASE]                                     │
├─────────────────────────────────────────────────────────┤
│ Database ID          Character Set       Collation       │
├─────────────────────────────────────────────────────────┤
│ postgres             UTF8                en_US.utf8     │
│ template0            UTF8                en_US.utf8     │
│ template1            UTF8                en_US.utf8     │
└─────────────────────────────────────────────────────────┘
```

#### Step 3: Click "CREATE DATABASE" Button

**Dialog appears:**
```
┌─────────────────────────────────────────────────────┐
│ Create a database                                    │
├─────────────────────────────────────────────────────┤
│                                                      │
│ Database ID *                                       │
│ ┌──────────────────────────────────────────────┐   │
│ │ [Enter: pgadmin_production]                  │   │
│ └──────────────────────────────────────────────┘   │
│                                                      │
│ Collation                                           │
│ ┌──────────────────────────────────────────────┐   │
│ │ [use_default] ✓                              │   │
│ └──────────────────────────────────────────────┘   │
│                                                      │
│ Character set                                       │
│ ┌──────────────────────────────────────────────┐   │
│ │ [utf8] ✓                                     │   │
│ └──────────────────────────────────────────────┘   │
│                                                      │
│ [CANCEL]          [CREATE DATABASE]                │
└─────────────────────────────────────────────────────┘
```

#### Step 4: Enter Database Name

Type in the Database ID field:
```
pgadmin_production
```

**Important:** 
- Use lowercase
- Use underscore, not hyphen
- No special characters

#### Step 5: Leave Other Fields Default

```
✓ Collation: use_default (this is fine)
✓ Character set: utf8 (this is correct)
```

#### Step 6: Click CREATE DATABASE

```
[CREATE DATABASE] ← Click this button
```

**Wait:** ~30 seconds for creation

**Success screen:**
```
✓ pgadmin_production database created successfully
```

**Verify in list:**
```
Database ID              Character Set        Collation
────────────────────────────────────────────────────────
pgadmin_production       UTF8                 en_US.utf8  ✓
postgres                 UTF8                 en_US.utf8
template0                UTF8                 en_US.utf8
template1                UTF8                 en_US.utf8
```

---

### PART 2: CREATE USER

#### Step 7: Click USERS Tab

**Current state:**
```
┌─────────────────────────────────────────────────────────┐
│ USERS                                                     │
├─────────────────────────────────────────────────────────┤
│  [+ CREATE USER ACCOUNT]                                │
├─────────────────────────────────────────────────────────┤
│ User Name          Type          Authentication Type     │
├─────────────────────────────────────────────────────────┤
│ postgres           BUILT_IN      Password               │
└─────────────────────────────────────────────────────────┘
```

#### Step 8: Click "CREATE USER ACCOUNT" Button

**Dialog appears:**
```
┌─────────────────────────────────────────────────────┐
│ Create a user                                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│ User name *                                         │
│ ┌──────────────────────────────────────────────┐   │
│ │ [Enter username here]                        │   │
│ └──────────────────────────────────────────────┘   │
│                                                      │
│ Password *                                          │
│ ┌──────────────────────────────────────────────┐   │
│ │ [Enter password here]                        │   │
│ └──────────────────────────────────────────────┘   │
│  ☐ Show password                                   │
│                                                      │
│ [CANCEL]          [CREATE USER]                    │
└─────────────────────────────────────────────────────┘
```

#### Step 9: Enter Username

Type in the User name field:
```
pgadmin_user
```

**Important:**
- Lowercase only
- No special characters
- No spaces

#### Step 10: Enter Strong Password

Type in the Password field:
```
SecureP@ss123!
```

**Password must have:**
- ✓ At least 8 characters
- ✓ Uppercase letters (A-Z)
- ✓ Lowercase letters (a-z)
- ✓ Numbers (0-9)
- ✓ Special characters (!@#$%^&*)

**Examples of strong passwords:**
```
MyPgAdmin123!
Secure@Pass456
ComplexP@ssw0rd!
```

#### Step 11: (Optional) Show Password

Check "Show password" to verify you typed it correctly:
```
☑ Show password    ← Check this to see password
```

#### Step 12: Click CREATE USER

```
[CREATE USER] ← Click this button
```

**Wait:** ~10 seconds for creation

**Success screen:**
```
✓ User pgadmin_user created successfully
```

**Verify in list:**
```
User Name           Type              Authentication Type
─────────────────────────────────────────────────────────
pgadmin_user        BUILT_IN          Password            ✓
postgres            BUILT_IN          Password
```

---

### PART 3: GRANT PERMISSIONS

#### Step 13: Open Cloud Shell

**Option 1: From Cloud SQL Instance Page**
```
1. Click [CONNECT] button → "Open Cloud Shell"
   ↓
2. Cloud Shell terminal opens at bottom
```

**Option 2: From GCP Console**
```
1. Click ☁️ icon (top right)
2. Click "Open Cloud Shell"
```

**Cloud Shell opens:**
```
Welcome to Cloud Shell!
Type "help" to get started.

user@project:~$  ← This is your prompt
```

#### Step 14: Connect to Database as Admin

Type this command:
```bash
gcloud sql connect pgadmin-db --user=postgres
```

**You'll see:**
```
Connecting to database with SQL user [postgres].
Connecting to instance [pgadmin-db].
Allowlisting your IP address for incoming connection for 5 minutes...

Password for user postgres:  ← Enter your root password here
```

**After entering password:**
```
psql (13.8, server 14.5)
Type "help" for help.

postgres=>  ← This is the SQL prompt
```

#### Step 15: Grant Permissions

Copy-paste this command (one at a time):

**Command 1:**
```sql
GRANT ALL PRIVILEGES ON DATABASE pgadmin_production TO pgadmin_user;
```

Press Enter. You should see:
```
GRANT
postgres=>
```

**Command 2:**
```sql
ALTER ROLE pgadmin_user SET client_encoding TO 'utf8';
```

You should see:
```
ALTER ROLE
postgres=>
```

**Command 3:**
```sql
ALTER ROLE pgadmin_user SET default_transaction_isolation TO 'read committed';
```

You should see:
```
ALTER ROLE
postgres=>
```

**Command 4:**
```sql
ALTER ROLE pgadmin_user SET default_transaction_deferrable TO on;
```

You should see:
```
ALTER ROLE
postgres=>
```

#### Step 16: Verify Permissions

Type this command:
```sql
SELECT * FROM information_schema.role_table_grants WHERE grantee='pgadmin_user';
```

You should see results showing permissions (several rows):
```
TABLE_CATALOG | TABLE_SCHEMA | TABLE_NAME | GRANTOR | GRANTEE | PRIVILEGE | IS_GRANTABLE
──────────────┼──────────────┼────────────┼─────────┼────────┼──────────┼──────────────
pgadmin_prod  | public       | ...        | postgres|pgadmin_│ SELECT   | NO
pgadmin_prod  | public       | ...        | postgres|pgadmin_│ INSERT   | NO
...
```

This means permissions are granted! ✅

#### Step 17: Exit SQL

Type:
```sql
\q
```

You should return to:
```
user@project:~$ 
```

---

## Verification Checklist

### ✅ Database Created

```bash
# Command to verify
gcloud sql databases list --instance=pgadmin-db
```

**Should show:**
```
NAME                  CHARSET  COLLATION
pgadmin_production    UTF8     en_US.utf8  ← This should be here
postgres              UTF8     en_US.utf8
```

### ✅ User Created

```bash
# Command to verify
gcloud sql users list --instance=pgadmin-db
```

**Should show:**
```
NAME              TYPE
pgadmin_user      BUILT_IN  ← This should be here
postgres          BUILT_IN
```

### ✅ User Can Connect

```bash
# Try connecting as the new user
gcloud sql connect pgadmin-db --user=pgadmin_user
```

**When prompted for password, enter the password you set**

**Should show:**
```
pgadmin_user=>  ← If you see this, connection works!
```

**Exit:**
```sql
\q
```

---

## If Something Goes Wrong

### Problem: "User already exists"

**Solution:** Delete and recreate
```bash
gcloud sql users delete pgadmin_user --instance=pgadmin-db
gcloud sql users create pgadmin_user --instance=pgadmin-db --password=NewPassword123!
```

### Problem: "Database already exists"

**Solution:** It's already created! Just verify in the DATABASES tab.

### Problem: "Password authentication failed"

**Solution:** 
1. Verify you entered the correct password
2. Try recreating the user with a new password:
```bash
gcloud sql users delete pgadmin_user --instance=pgadmin-db
gcloud sql users create pgadmin_user --instance=pgadmin-db --password=NewPassword123!
```

### Problem: "Permission denied"

**Solution:** Make sure you're connected as `postgres` (admin), not `pgadmin_user`
```bash
# Connect as postgres (admin)
gcloud sql connect pgadmin-db --user=postgres
```

---

## Summary Table

After completing all steps, you should have:

| Item | Value | Status |
|------|-------|--------|
| **Database** | `pgadmin_production` | ✅ Created |
| **Database Owner** | `postgres` | ✅ Set |
| **User** | `pgadmin_user` | ✅ Created |
| **User Password** | Your strong password | ✅ Set |
| **Permissions** | ALL on pgadmin_production | ✅ Granted |
| **Connection** | Can connect via Cloud Shell | ✅ Verified |

---

## Next Steps

1. ✅ Database and user created
2. ✅ Permissions granted
3. → Get the Cloud SQL IP address
4. → Store password in GCP Secret Manager
5. → Update Django settings
6. → Deploy to Cloud Run

---

**Now you're ready to connect Django to your Cloud SQL database!** 🚀
