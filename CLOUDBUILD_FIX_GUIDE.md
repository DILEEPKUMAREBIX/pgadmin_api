# 🔧 Cloud Build Error Fix - Service Account Logging Issue

## ❌ The Error You Got

```
Your build failed to run: if 'build.service_account' is specified, the build must either 
(a) specify 'build.logs_bucket', 
(b) use the REGIONAL_USER_OWNED_BUCKET build.options.default_logs_bucket_behavior option, or 
(c) use either CLOUD_LOGGING_ONLY / NONE logging options: invalid argument
```

## ✅ What Was Fixed

The `cloudbuild.yaml` file was missing the critical `options` section that Cloud Build requires when using a service account.

### Before (Broken)
```yaml
steps:
  - name: 'gcr.io/cloud-builders/gke-deploy'
    # ... steps ...

# ❌ MISSING: options section
```

### After (Fixed)
```yaml
steps:
  - name: 'gcr.io/cloud-builders/gcloud'
    # ... steps ...

# ✅ ADDED: options section
options:
  defaultLogsBucketBehavior: REGIONAL_USER_OWNED_BUCKET
  logging: CLOUD_LOGGING_ONLY
  machineType: 'N1_HIGHCPU_8'
```

## 🎯 What This Does

### 1. `defaultLogsBucketBehavior: REGIONAL_USER_OWNED_BUCKET`
- Tells Cloud Build to use a regional, user-owned bucket for logs
- Fixes the service account logging requirement
- Logs stored in: `gs://[project]_cloudbuild/[region]`

### 2. `logging: CLOUD_LOGGING_ONLY`
- Use Google Cloud Logging instead of Cloud Storage bucket
- Simpler and requires less configuration
- Logs visible in Cloud Console > Logging

### 3. `machineType: 'N1_HIGHCPU_8'`
- Uses higher performance machine for faster builds
- N1_HIGHCPU_8 = 8 vCPUs, good for Python builds

## 🚀 Next Steps to Deploy

### Step 1: Ensure Cloud Build is Enabled
```bash
gcloud services enable cloudbuild.googleapis.com
```

### Step 2: Grant Cloud Build Service Account Permissions
```bash
# Get project number
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

# Grant Cloud Run admin role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com \
  --role=roles/run.admin

# Grant Cloud SQL client role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com \
  --role=roles/cloudsql.client

# Grant Secret Manager secret accessor role
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

### Step 3: Ensure Secrets Exist in Secret Manager
```bash
# These must exist before Cloud Build runs
gcloud secrets list

# Should see:
# - db-password
# - django-secret-key
# - database-host

# If missing, create them:
echo -n "your_db_password" | gcloud secrets create db-password --data-file=-
echo -n "your_django_secret_key" | gcloud secrets create django-secret-key --data-file=-
echo -n "your_database_host_ip" | gcloud secrets create database-host --data-file=-
```

### Step 4: Commit and Push to GitHub
```bash
git add cloudbuild.yaml
git commit -m "Fix: Cloud Build logging configuration for service account"
git push origin main
```

### Step 5: Cloud Build Will Automatically Trigger
- GitHub detects push
- Cloud Build reads `cloudbuild.yaml`
- Build starts with new logging configuration
- Should succeed this time! ✅

## 📋 Verify Build Is Working

### Check Cloud Build History
```bash
gcloud builds list --limit=5
```

### Check Latest Build Logs
```bash
# Get most recent build ID
BUILD_ID=$(gcloud builds list --limit=1 --format='value(id)')

# View logs
gcloud builds log $BUILD_ID --stream
```

### Check Cloud Run Deployment
```bash
# Verify service is deployed
gcloud run services list --region=us-central1

# Test API
curl https://pgadmin-api-[random].run.app/api/
```

## 🆘 If Build Still Fails

### Check Cloud Build Logs Detail
```bash
BUILD_ID=$(gcloud builds list --limit=1 --format='value(id)')
gcloud builds log $BUILD_ID --stream --limit=100
```

### Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Permission denied | Run Step 2 (grant IAM roles) |
| Secret not found | Run Step 3 (create secrets) |
| Image build failed | Check Python requirements.txt |
| Migrations failed | May be normal - check DB connection |
| Cloud Run deploy failed | Check environment variables |

### Reset Cloud Build Trigger
```bash
# List triggers
gcloud builds triggers list

# Delete broken trigger
gcloud builds triggers delete pgadmin-api-trigger

# Recreate via GCP Console or use gcloud
```

## 📚 What Changed in cloudbuild.yaml

### Key Improvements:

1. **Fixed Logging** ✅
   - Before: No options section (caused error)
   - After: CLOUD_LOGGING_ONLY (works with service account)

2. **Better Step Names** ✅
   - Before: gke-deploy (wrong image)
   - After: gcr.io/cloud-builders/gcloud (correct)

3. **Correct Args Format** ✅
   - Before: Mixed entrypoint and args (confusing)
   - After: Consistent gcloud command syntax

4. **Migration Handling** ✅
   - Added onFailure: ALLOW (continues even if migrations fail)
   - Allows debugging failed migrations after deployment

5. **Image Registry** ✅
   - Added images section
   - Pushes to gcr.io for reuse in Cloud Run jobs

## 📊 Architecture After Fix

```
Push to GitHub
       ↓
GitHub Webhook triggers Cloud Build
       ↓
Cloud Build reads cloudbuild.yaml (with FIXED options section)
       ↓
Build Step 1: Build & Deploy to Cloud Run
       ↓
Build Step 2: Create Cloud Run Job for migrations
       ↓
Logs stored via CLOUD_LOGGING_ONLY (no service account issue!)
       ↓
API Live at: https://pgadmin-api-[random].run.app
```

## ✨ You're All Set!

The `cloudbuild.yaml` now has:
- ✅ Proper logging configuration for service account
- ✅ Correct Cloud Build syntax
- ✅ Automatic database migrations
- ✅ Error-tolerant migration step

**Next build should succeed!** 🚀

---

**File Updated**: `cloudbuild.yaml`
**Date**: 2025-12-18
**Status**: Ready for deployment
