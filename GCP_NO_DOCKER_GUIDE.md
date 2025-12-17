# 🚀 GCP Cloud Run Deployment - GitHub & Cloud Build (NO DOCKER!)

## ⭐ Recommended Method: Cloud Build with GitHub

**Why This Method?**
- ✅ NO Docker Desktop needed
- ✅ Fully automated deployments
- ✅ Every git push auto-deploys
- ✅ Simplest setup (5 minutes)
- ✅ Best for teams

**Estimated Time:** 30-45 minutes total  
**Cost:** Free (stays within free tier)  
**Difficulty:** Easy

---

## Table of Contents

1. [Quick Overview](#quick-overview)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Setup](#step-by-step-setup)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

---

## Quick Overview

```
Your Local Machine          GitHub              Google Cloud Platform
         │                   │                           │
    git push ───────────→ Repository  ───→  Cloud Build  │
                                                  │       │
                                                  ↓       ↓
                                            Build & Deploy
                                                        │
                                                        ↓
                                            Cloud Run (Running!)
                                                        │
                                                        ↓
                                            Serving API Requests
```

**After Setup:**
- You push code to GitHub
- Cloud Build automatically detects the push
- GCP builds your application (no Docker needed!)
- Cloud Run deploys the application
- Your API is live in seconds!
- **You don't do anything manually** ✨

---

## Prerequisites

### What You Need

- [ ] **GCP Account** - [Create free account](https://cloud.google.com/free) ($300 free credits)
- [ ] **GitHub Account** - [Create if needed](https://github.com)
- [ ] **Git CLI** - [Download](https://git-scm.com/)
- [ ] **Your Django Project** - Already have it ✅
- [ ] **gcloud CLI** (Optional, for advanced) - [Install](https://cloud.google.com/sdk/docs/install)

### What You DON'T Need

- ❌ **Docker Desktop** - Not needed!
- ❌ **Python installed locally** - GCP handles it
- ❌ **Any build tools** - Cloud Build handles it

### Quick Verification

```bash
# Verify you have
git --version        # Should show: git version 2.x

# That's it! No need to verify Docker or Python
```

---

## Step-by-Step Setup

### Phase 1: Push Code to GitHub (5 minutes)

#### Step 1.1: Create GitHub Repository

1. Go to [github.com](https://github.com)
2. Click **"New repository"**
3. Name: `pgadmin-api`
4. Description: `PG Admin REST API`
5. Visibility: **Public** (recommended for free tier)
6. Click **"Create repository"**

#### Step 1.2: Push Your Code

```bash
# Navigate to your project
cd /path/to/PGAdmin-Backend

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial Django API setup with Cloud SQL support"

# Add GitHub remote
git remote add origin https://github.com/YOUR-USERNAME/pgadmin-api.git

# Change branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

**Verify:** Check GitHub - you should see all your files there ✅

---

### Phase 2: GCP Project Setup (10 minutes)

#### Step 2.1: Create GCP Project

1. Go to [GCP Console](https://console.cloud.google.com)
2. Click **"Select a Project"** (top left)
3. Click **"NEW PROJECT"**
4. Name: `pgadmin-production`
5. Click **"CREATE"**
6. Wait for project to be created (~1 minute)

#### Step 2.2: Enable Required Services

1. Go to [APIs & Services](https://console.cloud.google.com/apis/dashboard)
2. Click **"+ ENABLE APIS AND SERVICES"**
3. Search and enable each:

   **Search and enable:**
   - `Cloud Run API`
   - `Cloud SQL Admin API`
   - `Cloud Build API`
   - `Cloud Logging API`
   - `Secret Manager API`

   Or use commands:
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable sqladmin.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable logging.googleapis.com
   gcloud services enable secretmanager.googleapis.com
   ```

**Verify:** All services should show "Enabled" ✅

---

### Phase 3: Cloud SQL Setup (15 minutes)

#### Step 3.1: Create Cloud SQL Instance

1. Go to [Cloud SQL Instances](https://console.cloud.google.com/sql/instances)
2. Click **"CREATE INSTANCE"**
3. Choose **"PostgreSQL"**
4. Configure:
   - **Instance ID:** `pgadmin-db`
   - **Password:** Set strong password (save it!)
   - **Database version:** PostgreSQL 14
   - **Region:** `us-central1`
   - **Zonal availability:** Single zone (free tier)
   - **Machine type:** Shared core (db-f1-micro) ✅ Free tier
   - **Storage:** SSD, 10GB ✅ Free tier

5. Click **"CREATE INSTANCE"**
6. Wait 3-5 minutes for creation

**Note:** Take note of the **Connection name** (format: `project:region:instance`)

#### Step 3.2: Create Database & User

Once created:

1. Click the instance name `pgadmin-db`
2. Click **"DATABASES"** tab
3. Click **"CREATE DATABASE"**
4. Name: `pgadmin_production`
5. Click **"CREATE"**

Then create user:

1. Click **"USERS"** tab
2. Click **"CREATE ACCOUNT"**
3. **Username:** `pgadmin_user`
4. **Password:** Create strong password (save it!)
5. Click **"CREATE"**

**Save these for later:**
```
Database Host: Will be set later (private IP)
Database Name: pgadmin_production
Database User: pgadmin_user
Database Password: [your strong password]
```

#### Step 3.3: Allow Cloud Run to Connect

1. Click **"CONNECTIVITY"** tab
2. Under **"Public IP"** → Click **"Add Network"**
   - Name: `Cloud Run`
   - Network: `0.0.0.0/0` (Cloud Run access)
3. Click **"SAVE"**

Or use private IP (more secure):
1. Click **"CONNECTIVITY"** tab
2. Enable **"Private IP"**
3. Use default VPC
4. Click **"SAVE"**

---

### Phase 4: Connect GitHub to GCP (10 minutes)

#### Step 4.1: Create Cloud Build Trigger

1. Go to [Cloud Build Console](https://console.cloud.google.com/cloud-build)
2. Click **"Triggers"**
3. Click **"CREATE TRIGGER"**
4. Configure:
   - **Name:** `pgadmin-auto-deploy`
   - **Event:** `Push to a branch`
   - **Repository:** Click "CONNECT REPOSITORY"

#### Step 4.2: Connect GitHub Repo

1. Click **"CONNECT REPOSITORY"**
2. Choose **GitHub (Cloud Build GitHub App)**
3. Click **"AUTHENTICATE WITH GITHUB"**
4. Authorize GCP access to GitHub
5. Select your repository: `YOUR-USERNAME/pgadmin-api`
6. Click **"CONNECT"**

#### Step 4.3: Configure Build Trigger

Back in trigger creation:
- **Branch:** `^main$` (deploy on main branch push)
- **Build Configuration:** `Cloud Build configuration file (yaml)`
- **Location:** `Repository` → `cloudbuild.yaml`

Click **"CREATE"**

**Verify:** You should see your trigger in the Triggers list ✅

---

### Phase 5: Configure Environment Variables (10 minutes)

#### Step 5.1: Store Secrets in Secret Manager

Go to [Secret Manager](https://console.cloud.google.com/security/secret-manager)

Create these secrets:

**1. Database Password**
- Click **"CREATE SECRET"**
- Name: `db-password`
- Value: Your Cloud SQL password
- Click **"CREATE SECRET"**

**2. Django Secret Key**
- Click **"CREATE SECRET"**
- Name: `django-secret-key`
- Value: Generate one:
  ```bash
  python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
  ```
  (Copy the output)
- Click **"CREATE SECRET"**

**3. Database Host**
- Click **"CREATE SECRET"**
- Name: `database-host`
- Value: Your Cloud SQL private IP (from Cloud SQL instance page)
- Click **"CREATE SECRET"**

#### Step 5.2: Update cloudbuild.yaml

Your `cloudbuild.yaml` should reference these secrets. Here's the complete file:

```yaml
# cloudbuild.yaml
steps:
  # Step 1: Build image using buildpacks (NO DOCKERFILE NEEDED!)
  - name: 'gcr.io/cloud-builders/gke-deploy'
    id: 'build-image'
    entrypoint: 'gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'pgadmin-api'
      - '--source'
      - '.'
      - '--platform'
      - 'managed'
      - '--region'
      - 'us-central1'
      - '--runtime'
      - 'python311'
      - '--entry-point'
      - 'gunicorn'
      - '--allow-unauthenticated'
      - '--set-env-vars=ENVIRONMENT=production,DEBUG=False'
      - '--set-env-vars=DATABASE_NAME=pgadmin_production'
      - '--set-env-vars=DATABASE_USER=pgadmin_user'
      - '--update-secrets=DATABASE_PASSWORD=db-password:latest,SECRET_KEY=django-secret-key:latest,DATABASE_HOST=database-host:latest'

  # Step 2: Run migrations
  - name: 'gcr.io/cloud-builders/gke-deploy'
    id: 'run-migrations'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        gcloud run jobs create run-migrations-$BUILD_ID \
          --image gcr.io/$PROJECT_ID/pgadmin-api \
          --region us-central1 \
          --execute-now \
          --tasks 1 \
          --command python manage.py migrate || true
```

Or simpler version (if migrations already run):

```yaml
steps:
  - name: 'gcr.io/cloud-builders/gke-deploy'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'pgadmin-api'
      - '--source'
      - '.'
      - '--platform'
      - 'managed'
      - '--region'
      - 'us-central1'
      - '--runtime'
      - 'python311'
      - '--allow-unauthenticated'
      - '--set-env-vars=ENVIRONMENT=production,DEBUG=False'
      - '--update-secrets=DATABASE_PASSWORD=db-password:latest,SECRET_KEY=django-secret-key:latest,DATABASE_HOST=database-host:latest'
```

#### Step 5.3: Push cloudbuild.yaml to GitHub

```bash
git add cloudbuild.yaml
git commit -m "Update cloudbuild.yaml with secrets"
git push origin main
```

---

### Phase 6: Update Django Settings (5 minutes)

Update `pgadmin_config/settings.py`:

```python
import os
from decouple import config, Csv

# ============================================================================
# ENVIRONMENT
# ============================================================================
ENVIRONMENT = config('ENVIRONMENT', default='development')
DEBUG = config('DEBUG', default=False, cast=bool)

# For production on Cloud Run
if ENVIRONMENT == 'production':
    ALLOWED_HOSTS = ['pgadmin-api-*.run.app', 'localhost']
else:
    ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=Csv())

SECRET_KEY = config('SECRET_KEY', default='dev-key-not-secure')

# ============================================================================
# DATABASE
# ============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DATABASE_NAME', default='pgadmin_db'),
        'USER': config('DATABASE_USER', default='postgres'),
        'PASSWORD': config('DATABASE_PASSWORD', default=''),
        'HOST': config('DATABASE_HOST', default='localhost'),
        'PORT': config('DATABASE_PORT', default='5432'),
    }
}

# ============================================================================
# STATIC FILES
# ============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============================================================================
# CORS
# ============================================================================
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:8081',
    cast=Csv()
)

# ============================================================================
# SECURITY (Production)
# ============================================================================
if ENVIRONMENT == 'production':
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# ============================================================================
# LOGGING
# ============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': config('LOG_LEVEL', default='INFO'),
        },
    },
}

# Middleware (add whitenoise)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    # ... rest of middleware
]
```

Push to GitHub:

```bash
git add pgadmin_config/settings.py
git commit -m "Update settings for production Cloud Run deployment"
git push origin main
```

---

### Phase 7: First Deployment (Automatic!)

**The magic happens now:**

1. You pushed code to GitHub (main branch)
2. GitHub notifies Cloud Build
3. Cloud Build:
   - Detects Python project
   - Builds container (no Docker needed!)
   - Deploys to Cloud Run
   - Runs migrations
   - Your API is live!

Check status:

```bash
# View build status
gcloud builds log --limit=100

# Or go to Cloud Build console:
# https://console.cloud.google.com/cloud-build/builds
```

Your API URL will be:
```
https://pgadmin-api-xxxxx.us-central1.run.app
```

---

## Verification

### Check Deployment Status

1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click `pgadmin-api` service
3. Should show:
   - ✅ Status: `OK`
   - ✅ Revisions: At least 1
   - ✅ Service URL: `https://pgadmin-api-xxxxx.run.app`

### Test API

```bash
# Get service URL
curl https://pgadmin-api-xxxxx.us-central1.run.app/api/v1/properties/

# Or open in browser:
https://pgadmin-api-xxxxx.us-central1.run.app/api/docs/
```

### Check Logs

```bash
# View real-time logs
gcloud run logs read pgadmin-api --region us-central1 --follow

# Or in console:
# https://console.cloud.google.com/run
# → Click service → "Logs"
```

---

## Continuous Deployment (From Now On)

**The beauty of this setup:**

```bash
# 1. Make changes locally
# 2. Test on your machine
# 3. Push to GitHub
git add .
git commit -m "Add new feature"
git push origin main

# That's it! ✨
# Cloud Build automatically:
# - Builds your app
# - Deploys to Cloud Run
# - Your API is updated
# - No manual commands needed
```

---

## Troubleshooting

### Build Failed / Deployment Failed

1. Go to [Cloud Build Console](https://console.cloud.google.com/cloud-build/builds)
2. Click the failed build
3. View logs to see error
4. Fix error locally
5. Push to GitHub (auto-tries again!)

### Common Errors

**Error:** `ModuleNotFoundError: No module named 'xxx'`
- Fix: Add to `requirements.txt` and push
```bash
pip freeze > requirements.txt
git add requirements.txt
git push origin main
```

**Error:** `Database connection failed`
- Fix: Check DATABASE_HOST secret is correct
- Verify Cloud SQL is running
- Check firewall rules

**Error:** `SECRET_KEY not set`
- Fix: Verify secrets in Secret Manager
- Check cloudbuild.yaml references them correctly

### View Logs for Debugging

```bash
# Real-time logs
gcloud run logs read pgadmin-api --region us-central1 --follow

# Last 100 lines
gcloud run logs read pgadmin-api --region us-central1 --limit 100

# Specific time period
gcloud run logs read pgadmin-api --region us-central1 --limit 500
```

---

## Cost Summary

| Service | Free Tier Limit | Monthly Cost |
|---------|-----------------|--------------|
| Cloud Run | 2M requests | $0 ✅ |
| Cloud SQL | 10GB storage + 1 shared CPU | $0 ✅ |
| Cloud Build | 120 build-minutes/day | $0 ✅ |
| **Total** | - | **$0-5** ✅ |

---

## File Checklist

Make sure these files exist in your repository:

- ✅ `requirements.txt` - Python dependencies
- ✅ `manage.py` - Django management script
- ✅ `pgadmin_config/settings.py` - Updated for production
- ✅ `pgadmin_config/wsgi.py` - WSGI entry point
- ✅ `cloudbuild.yaml` - Build configuration
- ✅ `.gitignore` - Exclude secrets
- ✅ `Procfile` (optional) - Or just rely on buildpacks

---

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Create GCP project
3. ✅ Setup Cloud SQL
4. ✅ Configure Cloud Build trigger
5. ✅ Create secrets
6. ✅ Push cloudbuild.yaml
7. ✅ Watch automatic deployment
8. ✅ Test API
9. ✅ Celebrate! 🎉

**Automatic deployments from now on!** Every push = automatic update ✨

---

## Useful Links

- [Cloud Run Docs](https://cloud.google.com/run/docs)
- [Cloud Build Docs](https://cloud.google.com/build/docs)
- [Cloud SQL Docs](https://cloud.google.com/sql/docs/postgres)
- [GCP Console](https://console.cloud.google.com)
- [Buildpacks Documentation](https://buildpacks.io)

---

**You're done! Your API is now live and auto-deploys with every git push!** 🚀✨
