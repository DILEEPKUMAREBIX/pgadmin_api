# 🔧 GCP Deployment Troubleshooting Guide

## Common Issues & Solutions

---

## 🔴 Critical Issues

### Issue 1: 502 Bad Gateway / Service Unavailable

**Symptoms:**
- API returns 502 error
- Service is deployed but not responding
- Error appears immediately after deployment

**Solutions:**

1. **Check Logs First**
   ```bash
   gcloud run logs read pgadmin-api --region us-central1 --limit 100
   ```

2. **Common Log Errors & Fixes:**

   **Error:** `ModuleNotFoundError: No module named 'xxx'`
   - **Fix:** Update `requirements.txt` and redeploy
   ```bash
   pip freeze > requirements.txt
   git add requirements.txt
   gcloud run deploy pgadmin-api --source . --region us-central1
   ```

   **Error:** `Secret key not found` or `SECRET_KEY not set`
   - **Fix:** Add SECRET_KEY environment variable
   ```bash
   gcloud run services update pgadmin-api \
     --region us-central1 \
     --update-env-vars=SECRET_KEY=your-secret-key
   ```

   **Error:** `django.core.exceptions.ImproperlyConfigured`
   - **Fix:** Check `settings.py` for missing configuration
   ```python
   # Make sure these exist in settings.py:
   ALLOWED_HOSTS = config('ALLOWED_HOSTS')
   DATABASES = {...}
   SECRET_KEY = config('SECRET_KEY')
   ```

3. **Check Container is Running**
   ```bash
   # View service details
   gcloud run services describe pgadmin-api --region us-central1
   
   # Look for: status.conditions[].status == True
   ```

4. **Rebuild and Redeploy**
   ```bash
   gcloud run deploy pgadmin-api \
     --source . \
     --region us-central1 \
     --platform managed \
     --no-cache
   ```

---

### Issue 2: Database Connection Failed

**Symptoms:**
- API works but database queries fail
- `ProgrammingError: could not translate host name "10.x.x.x" to address`
- Connection timeout errors in logs

**Solutions:**

1. **Verify Cloud SQL Instance is Running**
   ```bash
   gcloud sql instances describe pgadmin-db
   
   # Check status field - should be "RUNNABLE"
   ```

2. **Verify Connection String**
   ```bash
   # Get Cloud SQL private IP
   gcloud sql instances describe pgadmin-db \
     --format='value(ipAddresses[0].ipAddress)'
   
   # Make sure DATABASE_HOST env var is set correctly
   gcloud run services describe pgadmin-api \
     --region us-central1 \
     --format='value(spec.template.spec.containers[0].env)'
   ```

3. **Check Database Exists**
   ```bash
   # Connect to Cloud SQL
   gcloud sql connect pgadmin-db --user=postgres
   
   # List databases
   \l
   
   # Should see: pgadmin_production
   # If not, create it:
   CREATE DATABASE pgadmin_production;
   ```

4. **Verify User Permissions**
   ```bash
   # Connect as postgres
   gcloud sql connect pgadmin-db --user=postgres
   
   # Check user exists
   \du
   
   # Grant permissions
   GRANT ALL PRIVILEGES ON DATABASE pgadmin_production TO pgadmin_user;
   ```

5. **Test Connection from Cloud Run**
   ```bash
   # Create test script
   cat > test_db.py << 'EOF'
   import os
   import psycopg2
   
   try:
       conn = psycopg2.connect(
           host=os.getenv('DATABASE_HOST'),
           user=os.getenv('DATABASE_USER'),
           password=os.getenv('DATABASE_PASSWORD'),
           database=os.getenv('DATABASE_NAME')
       )
       print("✅ Database connection successful!")
       conn.close()
   except Exception as e:
       print(f"❌ Connection failed: {e}")
   EOF
   
   # Deploy as one-off job
   gcloud run jobs create test-db \
     --image pgadmin-api:latest \
     --command python test_db.py
   ```

---

### Issue 3: Environment Variables Not Set

**Symptoms:**
- `KeyError: 'DATABASE_PASSWORD'`
- Missing configuration errors
- Variables work locally but not in production

**Solutions:**

1. **Set All Required Variables**
   ```bash
   gcloud run services update pgadmin-api \
     --region us-central1 \
     --update-env-vars=\
   ENVIRONMENT=production,\
   DEBUG=False,\
   SECRET_KEY=your-key,\
   DATABASE_NAME=pgadmin_production,\
   DATABASE_USER=pgadmin_user,\
   DATABASE_PASSWORD=your-password,\
   DATABASE_HOST=10.x.x.x,\
   DATABASE_PORT=5432,\
   CORS_ALLOWED_ORIGINS=https://yourapp.com
   ```

2. **Verify Variables are Set**
   ```bash
   # View all env vars
   gcloud run services describe pgadmin-api \
     --region us-central1 \
     --format='value(spec.template.spec.containers[0].env[].{name: name, value: value})'
   ```

3. **Use Secret Manager for Sensitive Values**
   ```bash
   # Store password securely
   echo -n "your-password" | gcloud secrets create db-password --data-file=-
   
   # Reference in Cloud Run
   gcloud run services update pgadmin-api \
     --region us-central1 \
     --set-env-vars=DATABASE_PASSWORD=ref:db-password
   ```

---

## ⚠️ Medium Issues

### Issue 4: Migrations Failed

**Symptoms:**
- `RuntimeError: Database table does not exist`
- `ProgrammingError: relation "pg_property" does not exist`
- Database queries fail after deployment

**Solutions:**

1. **Run Migrations Manually**
   ```bash
   # Option A: Via gcloud SQL shell
   gcloud sql connect pgadmin-db --user=postgres
   
   # Then in psql:
   python manage.py migrate
   
   # Option B: Create one-off job
   gcloud run jobs create run-migrations \
     --image pgadmin-api:latest \
     --command "python manage.py migrate"
   ```

2. **Check Migration Status**
   ```bash
   # Connect to database
   gcloud sql connect pgadmin-db --user=postgres
   
   # List migrations
   SELECT * FROM django_migrations;
   ```

3. **Reset Migrations (Last Resort)**
   ```sql
   -- WARNING: This deletes all data!
   DROP DATABASE pgadmin_production;
   CREATE DATABASE pgadmin_production;
   GRANT ALL PRIVILEGES ON DATABASE pgadmin_production TO pgadmin_user;
   ```

---

### Issue 5: Static Files Not Serving

**Symptoms:**
- CSS/JS not loading
- 404 errors on static files
- Admin page looks broken

**Solutions:**

1. **Collect Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

2. **Update Dockerfile to Run collectstatic**
   ```dockerfile
   # Add to Dockerfile before EXPOSE
   RUN python manage.py collectstatic --noinput || true
   ```

3. **Configure Static Files in settings.py**
   ```python
   STATIC_URL = '/static/'
   STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
   
   # For production, use whitenoise
   STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
   ```

4. **Add whitenoise to middleware**
   ```python
   MIDDLEWARE = [
       'django.middleware.security.SecurityMiddleware',
       'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
       # ... rest of middleware ...
   ]
   ```

---

### Issue 6: CORS Errors

**Symptoms:**
- Frontend gets CORS errors
- `Access-Control-Allow-Origin` header missing
- Cross-origin requests blocked

**Solutions:**

1. **Add Frontend URL to CORS**
   ```bash
   gcloud run services update pgadmin-api \
     --region us-central1 \
     --update-env-vars=\
   CORS_ALLOWED_ORIGINS=https://yourapp.com,https://www.yourapp.com,http://localhost:8081
   ```

2. **Update settings.py**
   ```python
   from decouple import config, Csv
   
   CORS_ALLOWED_ORIGINS = config(
       'CORS_ALLOWED_ORIGINS',
       default='http://localhost:8081',
       cast=Csv()
   )
   ```

3. **Check if django-cors-headers is installed**
   ```bash
   pip list | grep django-cors
   
   # If not installed:
   pip install django-cors-headers
   pip freeze > requirements.txt
   ```

4. **Verify it's in INSTALLED_APPS**
   ```python
   INSTALLED_APPS = [
       # ...
       'corsheaders',
       # ...
   ]
   ```

---

### Issue 7: Deployment Takes Too Long

**Symptoms:**
- Deployment stuck at "Building image"
- Takes >30 minutes to deploy
- Timeouts during build

**Solutions:**

1. **Reduce Build Time**
   ```bash
   # Deploy with skip-cache (faster after first time)
   gcloud run deploy pgadmin-api \
     --source . \
     --region us-central1 \
     --no-cache
   ```

2. **Optimize Docker Image**
   ```dockerfile
   # Use slim base image
   FROM python:3.11-slim
   
   # Combine RUN commands
   RUN apt-get update && apt-get install -y package1 package2 && rm -rf /var/lib/apt/lists/*
   
   # Exclude unnecessary files
   .dockerignore should include:
   - .git/
   - .venv/
   - __pycache__/
   - *.pyc
   ```

3. **Use Buildpack (Even Simpler)**
   ```bash
   # Use Cloud Run's built-in buildpacks
   gcloud run deploy pgadmin-api \
     --source . \
     --runtime python311 \
     --region us-central1
   ```

---

## 🟢 Minor Issues

### Issue 8: High Memory Usage

**Symptoms:**
- Memory usage constantly high (>400MB)
- Service getting killed
- Slow response times

**Solutions:**

1. **Increase Memory**
   ```bash
   gcloud run services update pgadmin-api \
     --memory 1Gi \
     --region us-central1
   ```

2. **Check for Memory Leaks**
   ```bash
   # View memory metrics
   gcloud monitoring time-series list \
     --filter='metric.type=run.googleapis.com/memory_allocations AND resource.labels.service_name=pgadmin-api'
   ```

3. **Optimize Queries**
   - Enable database query logging
   - Check for N+1 queries
   - Add database indexes

---

### Issue 9: High CPU Usage

**Symptoms:**
- CPU constantly at 100%
- Slow response times
- High costs

**Solutions:**

1. **Increase CPU**
   ```bash
   gcloud run services update pgadmin-api \
     --cpu 2 \
     --region us-central1
   ```

2. **Identify Slow Requests**
   ```bash
   # Check logs for slow requests
   gcloud run logs read pgadmin-api \
     --region us-central1 \
     --format='value(jsonPayload)' | grep duration
   ```

3. **Optimize Code**
   - Use database indexing
   - Cache responses
   - Optimize queries

---

### Issue 10: Timeouts (504 Gateway Timeout)

**Symptoms:**
- Long-running requests timeout
- `504 Gateway Timeout` errors
- Requests take >15 minutes

**Solutions:**

1. **Increase Timeout**
   ```bash
   gcloud run deploy pgadmin-api \
     --timeout 3600 \
     --region us-central1
   ```

2. **Identify Long-Running Operations**
   ```bash
   gcloud run logs read pgadmin-api \
     --region us-central1 \
     --limit 100 | grep latencies
   ```

3. **Use Background Jobs**
   - Move long operations to Cloud Tasks
   - Use Cloud Pub/Sub for async processing
   - Implement job queues with Celery

---

## 🔍 Debugging Steps

### Step 1: Check Service Status
```bash
gcloud run services describe pgadmin-api --region us-central1
```

### Step 2: Read Latest Logs
```bash
gcloud run logs read pgadmin-api --region us-central1 --limit 100
```

### Step 3: Check Metrics
```bash
gcloud monitoring time-series list \
  --filter='resource.type=cloud_run_revision AND resource.labels.service_name=pgadmin-api'
```

### Step 4: Test Endpoint
```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe pgadmin-api \
  --region us-central1 \
  --format='value(status.url)')

# Test
curl $SERVICE_URL/api/v1/properties/ -v
```

### Step 5: Check Database
```bash
gcloud sql connect pgadmin-db --user=postgres
SELECT * FROM pg_property;
```

---

## Emergency Recovery

### Rollback to Previous Deployment
```bash
# List previous revisions
gcloud run revisions list

# Deploy previous revision
gcloud run deploy pgadmin-api \
  --region us-central1 \
  --image gcr.io/pgadmin-production/pgadmin-api:previous-tag
```

### Delete and Redeploy
```bash
# Delete service
gcloud run services delete pgadmin-api --region us-central1

# Redeploy
gcloud run deploy pgadmin-api \
  --source . \
  --region us-central1 \
  --platform managed
```

### Restore Database from Backup
```bash
# List backups
gcloud sql backups list --instance=pgadmin-db

# Restore
gcloud sql backups restore BACKUP_ID \
  --backup-instance=pgadmin-db \
  --restore-instance=pgadmin-db
```

---

## Getting Help

### Check Official Docs
- [Cloud Run Troubleshooting](https://cloud.google.com/run/docs/troubleshooting)
- [Cloud SQL Troubleshooting](https://cloud.google.com/sql/docs/postgres/troubleshooting)
- [Django on Cloud Run](https://cloud.google.com/python/django/run)

### Useful Commands for Debugging
```bash
# Get full service configuration
gcloud run services describe pgadmin-api --region us-central1

# Get full logs with formatting
gcloud run logs read pgadmin-api --region us-central1 --format json

# List all errors
gcloud run logs read pgadmin-api --region us-central1 \
  --format='value(jsonPayload.message)' | grep -i error

# Performance monitoring
gcloud run describe pgadmin-api --region us-central1 \
  --format='value(status.latestReadyRevision.status.conditions)'
```

---

## Prevention Tips

✅ **Do:**
- Monitor logs regularly
- Set up alerts for errors
- Test locally first
- Keep requirements.txt updated
- Back up database regularly
- Document configuration

❌ **Don't:**
- Commit secrets to git
- Use hardcoded passwords
- Deploy without testing
- Ignore warning logs
- Skip backups

---

**Need more help? Check GCP documentation or contact support!** 🚀
