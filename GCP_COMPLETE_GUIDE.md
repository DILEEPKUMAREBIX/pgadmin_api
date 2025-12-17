# 🚀 GCP Cloud Run + Cloud SQL Complete Deployment Guide

## Overview

This guide walks you through deploying your Django PGAdmin API to Google Cloud Platform using Cloud Run and PostgreSQL Cloud SQL.

**Estimated Time:** 2-3 hours  
**Cost:** Free to $5/month (stays within free tier)  
**Difficulty:** Intermediate

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture](#architecture)
3. [Step-by-Step Deployment](#step-by-step-deployment)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### What You Need

- [ ] **GCP Account** - [Create free account](https://cloud.google.com/free) ($300 free credits)
- [ ] **Google Cloud SDK** - [Install gcloud CLI](https://cloud.google.com/sdk/docs/install)
- [ ] **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop)
- [ ] **Git** - [Download](https://git-scm.com/)
- [ ] **Your Django Project** - Already have it ✅

### System Requirements

- Windows, Mac, or Linux
- Minimum 4GB RAM
- Internet connection
- Terminal/Command prompt access

### Prerequisites Checklist

```bash
# Verify installations
gcloud --version          # Should show: Google Cloud SDK version
docker --version          # Should show: Docker version
git --version             # Should show: git version
python --version          # Should show: Python 3.8+
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Mobile App (Frontend)                 │
│              https://yourapp.com/occupancy             │
└────────────────────────┬────────────────────────────────┘
                         │
                    HTTPS Request
                         │
                         ↓
┌─────────────────────────────────────────────────────────┐
│              Google Cloud Platform (GCP)                │
│                                                         │
│  Region: us-central1 (or your choice)                  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │   Cloud Run (Serverless Container)              │  │
│  │   • Django REST API                             │  │
│  │   • Auto-scales 0→1000 instances               │  │
│  │   • Pay only for requests                       │  │
│  │   • Free tier: 2M requests/month                │  │
│  │   URL: https://pgadmin-api-xxxxx.run.app/      │  │
│  └────────────────────┬─────────────────────────────┘  │
│                       │                                 │
│                  Private Network                        │
│                       │                                 │
│  ┌────────────────────↓─────────────────────────────┐  │
│  │    Cloud SQL (Managed PostgreSQL)               │  │
│  │    • 10 GB storage (free tier)                  │  │
│  │    • 1 shared core CPU (free tier)              │  │
│  │    • Automatic backups                          │  │
│  │    • 99.95% SLA                                 │  │
│  │    Instance: pgadmin-db                         │  │
│  │    Database: pgadmin_production                 │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │     Cloud Build (CI/CD Automation)              │  │
│  │     • Monitors git repository                   │  │
│  │     • Auto-builds on push                       │  │
│  │     • Auto-deploys to Cloud Run                 │  │
│  │     • Free: 120 build minutes/day               │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Cloud Logging & Monitoring                     │  │
│  │  • View application logs                        │  │
│  │  • Set up alerts                                │  │
│  │  • Monitor performance                          │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Secret Manager                                 │  │
│  │  • Store environment variables securely         │  │
│  │  • Manage API keys and credentials              │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Deployment

### Phase 1: GCP Setup (20 minutes)

#### Step 1.1: Install and Configure gcloud CLI

```bash
# After installing Google Cloud SDK, initialize it
gcloud init

# You'll be prompted to:
# 1. Log in with your Google account
# 2. Create a new project or select existing
# 3. Set default region (choose: us-central1)
# 4. Set default zone (choose: us-central1-a)

# Verify setup
gcloud config list
```

**Expected Output:**
```
[core]
account = your-email@gmail.com
project = pgadmin-production
region = us-central1
zone = us-central1-a
```

#### Step 1.2: Create GCP Project

```bash
# Create new project
gcloud projects create pgadmin-production \
  --name="PGAdmin Production"

# Set as default project
gcloud config set project pgadmin-production

# Verify project created
gcloud projects list
```

#### Step 1.3: Enable Required Services

```bash
# Enable Cloud Run
gcloud services enable run.googleapis.com

# Enable Cloud SQL
gcloud services enable sqladmin.googleapis.com

# Enable Cloud Build (for CI/CD)
gcloud services enable cloudbuild.googleapis.com

# Enable Artifact Registry (for container images)
gcloud services enable artifactregistry.googleapis.com

# Enable Cloud Logging
gcloud services enable logging.googleapis.com

# Enable Secret Manager
gcloud services enable secretmanager.googleapis.com

# Verify services are enabled
gcloud services list --enabled
```

---

### Phase 2: Cloud SQL Setup (30 minutes)

#### Step 2.1: Create Cloud SQL Instance

```bash
# Create PostgreSQL instance
gcloud sql instances create pgadmin-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --availability-type=ZONAL \
  --storage-type=PD_SSD \
  --storage-size=10GB \
  --no-assign-ip

# This creates a private Cloud SQL instance (more secure)
# Wait 3-5 minutes for creation to complete
```

**Explanation of flags:**
- `--database-version=POSTGRES_14` - PostgreSQL version
- `--tier=db-f1-micro` - Free tier machine type
- `--region=us-central1` - Region (must match Cloud Run)
- `--availability-type=ZONAL` - Single zone (free tier)
- `--storage-type=PD_SSD` - SSD storage (faster)
- `--storage-size=10GB` - 10GB free tier limit
- `--no-assign-ip` - No public IP (private, more secure)

#### Step 2.2: Set Root Password

```bash
# Set password for postgres user
gcloud sql users set-password postgres \
  --instance=pgadmin-db \
  --password=your_secure_password_here

# Note: Replace 'your_secure_password_here' with a strong password
# Store this securely - you'll need it for connection strings
```

#### Step 2.3: Create Application Database

```bash
# Connect to Cloud SQL and create database
gcloud sql connect pgadmin-db \
  --user=postgres

# In the PostgreSQL prompt, run:
# (You'll be prompted for password)
```

Once connected to PostgreSQL:
```sql
CREATE DATABASE pgadmin_production;
CREATE USER pgadmin_user WITH PASSWORD 'your_app_password';
ALTER ROLE pgadmin_user SET client_encoding TO 'utf8';
ALTER ROLE pgadmin_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pgadmin_user SET default_transaction_deferrable TO on;
GRANT ALL PRIVILEGES ON DATABASE pgadmin_production TO pgadmin_user;
\q
```

#### Step 2.4: Verify Cloud SQL Connection

```bash
# Get Cloud SQL instance connection details
gcloud sql instances describe pgadmin-db

# Look for:
# - privateIpAddress: (for Cloud Run connection)
# - ipAddresses (if public IP needed)
```

---

### Phase 3: Environment Configuration (15 minutes)

#### Step 3.1: Create .env File for Production

Create `pgadmin_config/.env.production`:

```env
# ============================================================================
# ENVIRONMENT
# ============================================================================
ENVIRONMENT=production
DEBUG=False
ALLOWED_HOSTS=pgadmin-api-xxxxx.run.app,localhost

# ============================================================================
# SECRET KEY (Generate a new one for production)
# ============================================================================
SECRET_KEY=your-secret-key-generate-new-one

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=pgadmin_production
DATABASE_USER=pgadmin_user
DATABASE_PASSWORD=your_app_password
DATABASE_HOST=10.x.x.x  # Private IP of Cloud SQL
DATABASE_PORT=5432

# ============================================================================
# CLOUD SQL PROXY (when using public IP)
# ============================================================================
# DATABASE_URL=postgresql://pgadmin_user:password@127.0.0.1:5432/pgadmin_production

# ============================================================================
# CORS CONFIGURATION
# ============================================================================
CORS_ALLOWED_ORIGINS=https://yourapp.com,https://www.yourapp.com,http://localhost:8081

# ============================================================================
# STATIC FILES & MEDIA
# ============================================================================
STATIC_URL=/static/
STATIC_ROOT=staticfiles/
MEDIA_URL=/media/
MEDIA_ROOT=media/

# ============================================================================
# SECURITY
# ============================================================================
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL=INFO
```

#### Step 3.2: Update Django Settings for Production

Modify `pgadmin_config/settings.py`:

```python
import os
from decouple import config, Csv

# ============================================================================
# ENVIRONMENT
# ============================================================================
ENVIRONMENT = config('ENVIRONMENT', default='development')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=Csv())
SECRET_KEY = config('SECRET_KEY')

# ============================================================================
# DATABASE
# ============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST'),
        'PORT': config('DATABASE_PORT', default='5432'),
    }
}

# ============================================================================
# STATIC FILES FOR PRODUCTION
# ============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============================================================================
# SECURITY SETTINGS (Production)
# ============================================================================
if ENVIRONMENT == 'production':
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
    SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True, cast=bool)
    SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=True, cast=bool)

# ============================================================================
# CORS
# ============================================================================
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:8081', cast=Csv())

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
```

#### Step 3.3: Store Secrets in Google Secret Manager

```bash
# Store database password
echo -n "your_app_password" | gcloud secrets create db-password --data-file=-

# Store Django secret key (generate one first!)
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
# Copy the output and run:
echo -n "your-generated-secret-key" | gcloud secrets create django-secret-key --data-file=-

# Store Django allowed hosts
echo -n "pgadmin-api-xxxxx.run.app" | gcloud secrets create django-allowed-hosts --data-file=-

# List all secrets
gcloud secrets list
```

---

### Phase 4: Docker Configuration (10 minutes)

#### Step 4.1: Verify Dockerfile

Your `Dockerfile` should exist and look like this:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Run migrations
RUN python manage.py migrate || true

# Expose port
EXPOSE 8080

# Start application
CMD ["gunicorn", "pgadmin_config.wsgi:application", "--bind", "0.0.0.0:8080"]
```

#### Step 4.2: Verify .dockerignore

Your `.dockerignore` should exclude:
```
.venv/
.git/
.env
db.sqlite3
__pycache__/
*.pyc
.pytest_cache/
```

---

### Phase 5: Deploy to Cloud Run (20 minutes)

#### Step 5.1: Build and Deploy

```bash
# Deploy directly from local machine
gcloud run deploy pgadmin-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=production,DEBUG=False \
  --memory 512Mi \
  --cpu 1 \
  --timeout 3600 \
  --max-instances 10

# This will:
# 1. Build Docker image from your Dockerfile
# 2. Push to Artifact Registry
# 3. Deploy to Cloud Run
# 4. Show you the service URL
```

**Flag Explanations:**
- `--source .` - Build from current directory
- `--platform managed` - Use fully managed Cloud Run
- `--region us-central1` - Deploy to this region
- `--allow-unauthenticated` - Public access (remove for private)
- `--memory 512Mi` - Allocate 512MB RAM (free tier)
- `--cpu 1` - 1 CPU (free tier)
- `--max-instances 10` - Auto-scale up to 10 instances

**Expected Output:**
```
Service [pgadmin-api] revision [pgadmin-api-00001-xxx] has been deployed and is serving traffic at https://pgadmin-api-xxxxx.us-central1.run.app
```

#### Step 5.2: Set Environment Variables

```bash
# Set all environment variables for Cloud Run service
gcloud run services update pgadmin-api \
  --region us-central1 \
  --update-env-vars=\
ENVIRONMENT=production,\
DEBUG=False,\
DATABASE_ENGINE=django.db.backends.postgresql,\
DATABASE_NAME=pgadmin_production,\
DATABASE_USER=pgadmin_user,\
DATABASE_HOST=10.x.x.x,\
DATABASE_PORT=5432,\
CORS_ALLOWED_ORIGINS=https://yourapp.com
```

---

### Phase 6: Configure Cloud SQL Connection (10 minutes)

#### Step 6.1: Connect Cloud Run to Cloud SQL

There are two methods:

**Method A: Using Private IP (Recommended)**

```bash
# Get the private IP of Cloud SQL
gcloud sql instances describe pgadmin-db --format='value(ipAddresses[0].ipAddress)'

# Add this IP to your DATABASE_HOST environment variable
gcloud run services update pgadmin-api \
  --region us-central1 \
  --update-env-vars=DATABASE_HOST=10.x.x.x
```

**Method B: Using Cloud SQL Proxy (Easier)**

```bash
# Deploy Cloud SQL proxy as sidecar
# This requires a more complex setup - see troubleshooting

# Simpler: Use Cloud SQL Public IP
gcloud sql instances patch pgadmin-db \
  --assign-ip
```

---

## Verification

### Test Your API

```bash
# Get your service URL
gcloud run services describe pgadmin-api --region us-central1 --format='value(status.url)'

# Test basic endpoint
curl https://pgadmin-api-xxxxx.us-central1.run.app/api/v1/properties/

# Test with jq for pretty output
curl https://pgadmin-api-xxxxx.us-central1.run.app/api/v1/properties/ | jq .

# Test API documentation
curl https://pgadmin-api-xxxxx.us-central1.run.app/api/docs/
```

### Check Logs

```bash
# View recent logs
gcloud run logs read pgadmin-api --region us-central1 --limit 50

# Follow logs in real-time
gcloud run logs read pgadmin-api --region us-central1 --follow

# View specific revision logs
gcloud run logs read pgadmin-api --region us-central1 --limit 100
```

---

## Troubleshooting

### Issue: 502 Bad Gateway

```bash
# Check logs for errors
gcloud run logs read pgadmin-api --region us-central1 --limit 100

# Common causes:
# - Database connection string incorrect
# - Environment variables not set
# - Secret key not configured
```

### Issue: Database Connection Failed

```bash
# Verify Cloud SQL instance is running
gcloud sql instances describe pgadmin-db

# Test connection locally first
psql -h 10.x.x.x -U pgadmin_user -d pgadmin_production

# Verify Cloud Run can reach Cloud SQL
# Check VPC configuration
gcloud compute networks list
```

### Issue: Migrations Failed

```bash
# Run migrations manually
gcloud sql connect pgadmin-db --user=postgres

# Or use Cloud Run to run one-off command
gcloud run jobs create run-migrations \
  --image pgadmin-api:latest \
  --command python manage.py migrate
```

---

## Cost Summary

| Service | Free Tier | Limit | Monthly Cost |
|---------|-----------|-------|--------------|
| Cloud Run | 2M invocations | Per month | $0 |
| Cloud SQL | 10GB + 1 shared | Per month | $0 |
| Cloud Build | 120 minutes | Per day | $0 |
| Artifact Registry | 500MB | Per month | $0 |
| **Total** | | | **$0-5** ✅ |

---

## Next Steps

1. ✅ Follow steps in order
2. ✅ Keep `.env` file secure
3. ✅ Test API after each phase
4. ✅ Monitor logs regularly
5. ✅ Set up billing alerts

Your Django API is now live on Google Cloud! 🚀
