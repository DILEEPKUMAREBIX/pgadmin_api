# ✅ GCP Cloud Build + Cloud Run Deployment Checklist

## Pre-Deployment Setup

### Local Machine Setup
- [ ] Git CLI installed (`git --version`)
- [ ] GitHub account created
- [ ] Project pushed to GitHub repo
- [ ] `.gitignore` configured
- [ ] `requirements.txt` updated (`pip freeze > requirements.txt`)
- [ ] `manage.py` exists
- [ ] Django settings updated for production

### GCP Account Setup
- [ ] GCP account created [gcloud.google.com/free](https://cloud.google.com/free)
- [ ] New GCP project created: `pgadmin-production`
- [ ] Billing account linked to project

### Services Enabled
- [ ] Cloud Run API enabled
- [ ] Cloud SQL Admin API enabled
- [ ] Cloud Build API enabled
- [ ] Cloud Logging API enabled
- [ ] Secret Manager API enabled

---

## Cloud SQL Setup

### Database Instance
- [ ] Cloud SQL PostgreSQL instance created: `pgadmin-db`
- [ ] Region set to: `us-central1`
- [ ] Machine type: `db-f1-micro` (free tier)
- [ ] Storage: `10GB` SSD
- [ ] Root password set and saved securely

### Database & User
- [ ] Database created: `pgadmin_production`
- [ ] Database user created: `pgadmin_user`
- [ ] User password set and saved securely
- [ ] User has privileges on database

### Connectivity
- [ ] Public IP assigned to Cloud SQL instance
- [ ] Network authorization configured (0.0.0.0/0 for Cloud Run)
- [ ] Or Private IP setup with VPC

---

## Secrets Configuration

### Secret Manager Secrets Created
- [ ] Secret: `db-password` → Your Cloud SQL password
- [ ] Secret: `django-secret-key` → Generated Django key
- [ ] Secret: `database-host` → Cloud SQL private/public IP
- [ ] All secrets verified accessible

### Secret Values Saved
- [ ] Cloud SQL password saved securely
- [ ] Django secret key saved securely
- [ ] Database host IP saved
- [ ] Database user: `pgadmin_user` saved

---

## GitHub Setup

### Repository
- [ ] Repository created on GitHub: `pgadmin-api`
- [ ] Code pushed to `main` branch
- [ ] All files committed:
  - [ ] `requirements.txt`
  - [ ] `manage.py`
  - [ ] `pgadmin_config/settings.py` (updated)
  - [ ] `pgadmin_config/wsgi.py`
  - [ ] `cloudbuild.yaml` (create if missing)
  - [ ] `.gitignore`
  - [ ] All app files

### GitHub-GCP Integration
- [ ] GCP authenticated with GitHub
- [ ] Repository connected in Cloud Build
- [ ] GitHub app installed on account

---

## Cloud Build Configuration

### Build Trigger
- [ ] Trigger created: `pgadmin-auto-deploy`
- [ ] Trigger type: `Push to branch`
- [ ] Branch: `^main$`
- [ ] Build configuration: `cloudbuild.yaml`
- [ ] Location: `Repository`
- [ ] Trigger shows as "Active"

### cloudbuild.yaml File
- [ ] File exists in repository root
- [ ] References all secrets correctly
- [ ] Uses correct Cloud Run service name: `pgadmin-api`
- [ ] Region set to: `us-central1`
- [ ] Entry point set to: `gunicorn`

---

## Django Configuration

### Settings Updates
- [ ] `ENVIRONMENT = 'production'` configured
- [ ] `DEBUG = False` in production
- [ ] `SECRET_KEY` uses environment variable
- [ ] `ALLOWED_HOSTS` includes Cloud Run domain
- [ ] `DATABASES` configured with environment variables
- [ ] `STATIC_ROOT` configured
- [ ] `STATIC_URL` configured
- [ ] `CORS_ALLOWED_ORIGINS` configured for frontend

### Middleware
- [ ] `whitenoise.middleware.WhiteNoiseMiddleware` added
- [ ] Order is correct (SecurityMiddleware → WhiteNoise → rest)

### Logging
- [ ] Logging configured for production
- [ ] Error logging enabled

---

## Pre-Deployment Testing (Local)

- [ ] Run migrations locally: `python manage.py migrate`
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Test locally: `python manage.py runserver`
- [ ] API responds at: `http://localhost:8000/api/v1/`
- [ ] No Python import errors
- [ ] No configuration errors

---

## First Deployment

### Trigger Build
- [ ] Make small test commit and push to GitHub:
  ```bash
  git add .
  git commit -m "Deployment ready"
  git push origin main
  ```
- [ ] Go to Cloud Build console
- [ ] Verify build started
- [ ] Watch build logs

### Build Success Indicators
- [ ] Build completes without errors (green checkmark)
- [ ] Logs show: "Successfully deployed service"
- [ ] No error messages in build logs
- [ ] Build time: typically 5-10 minutes first time

### Cloud Run Deployment
- [ ] Service appears in Cloud Run console
- [ ] Service shows "OK" status
- [ ] Service URL generated: `https://pgadmin-api-xxxxx.us-central1.run.app`
- [ ] Revision shows as "Latest"

---

## Post-Deployment Verification

### API Accessibility
- [ ] API responds to request:
  ```bash
  curl https://pgadmin-api-xxxxx.us-central1.run.app/api/v1/properties/
  ```
- [ ] Returns JSON (not error)
- [ ] HTTP status: 200 OK

### API Endpoints
- [ ] Properties endpoint works
- [ ] Swagger docs accessible: `/api/docs/`
- [ ] Redoc docs accessible: `/api/redoc/`

### Database Connection
- [ ] API queries database
- [ ] Returns actual data
- [ ] No "connection refused" errors
- [ ] No "database does not exist" errors

### Logs
- [ ] Cloud Run logs show successful requests
- [ ] No Python exceptions in logs
- [ ] No database errors in logs
- [ ] No 500 errors

---

## Post-Deployment Configuration

### Frontend Integration
- [ ] Update frontend API base URL to Cloud Run URL
- [ ] Update CORS in settings if needed
- [ ] Test frontend ↔ API communication

### Monitoring Setup (Optional)
- [ ] Set up error alerts
- [ ] Set up performance monitoring
- [ ] Configure log filters

### Backup Setup (Optional)
- [ ] Enable Cloud SQL automated backups
- [ ] Test backup restoration

---

## Continuous Deployment Testing

### Test Auto-Deploy
- [ ] Make code change locally
- [ ] Push to GitHub: `git push origin main`
- [ ] Verify Cloud Build triggers automatically
- [ ] Verify deployment completes
- [ ] Verify API updates with new code
- [ ] **Confirm: Auto-deployment works!** ✅

---

## Troubleshooting Checklist

### If Build Fails
- [ ] Check Cloud Build console for error messages
- [ ] View full build logs
- [ ] Common issues:
  - [ ] Missing `requirements.txt`
  - [ ] Missing `manage.py`
  - [ ] Python syntax errors
  - [ ] Missing dependencies

### If Deployment Fails
- [ ] Check Cloud Run logs: `gcloud run logs read pgadmin-api`
- [ ] Common issues:
  - [ ] Database connection string incorrect
  - [ ] Environment variables not set
  - [ ] Secret not accessible
  - [ ] SECRET_KEY missing

### If API Doesn't Respond
- [ ] Check Cloud Run service status
- [ ] Verify service has revisions deployed
- [ ] Check Cloud Run logs for errors
- [ ] Verify database is accessible

---

## Security Checklist

- [ ] `.env` file in `.gitignore` ✅
- [ ] Secrets stored in Secret Manager (not in git)
- [ ] Database password not in source code
- [ ] SECRET_KEY stored in secrets (not hardcoded)
- [ ] HTTPS/SSL enabled (automatic with Cloud Run)
- [ ] CORS configured (not wildcard)
- [ ] DEBUG = False in production
- [ ] Database user has minimum required permissions

---

## Success Criteria

✅ **All items checked = Ready to deploy!**

When all checkboxes are complete:
1. Your code is on GitHub
2. Cloud Build is connected
3. Cloud SQL is ready
4. Secrets are configured
5. Django is configured for production
6. First deployment will be automatic!

---

## First Push = First Deployment

When ready:

```bash
# Push code to GitHub
git push origin main

# That's it! 
# Cloud Build automatically:
# - Detects the push
# - Builds your application
# - Deploys to Cloud Run
# - Your API is live!
```

**Monitor:**
- Cloud Build: [console.cloud.google.com/cloud-build](https://console.cloud.google.com/cloud-build)
- Cloud Run: [console.cloud.google.com/run](https://console.cloud.google.com/run)
- Logs: [console.cloud.google.com/logs](https://console.cloud.google.com/logs)

---

**When all items are checked, you're ready for production deployment!** 🚀
