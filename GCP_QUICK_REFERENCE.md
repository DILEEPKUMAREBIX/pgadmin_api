# ⚡ GCP Quick Reference & Commands

## Quick Command Cheatsheet

### Initialize GCP
```bash
gcloud init
gcloud config set project pgadmin-production
gcloud config set region us-central1
```

### Enable Services
```bash
gcloud services enable run.googleapis.com sqladmin.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com logging.googleapis.com secretmanager.googleapis.com
```

### Cloud SQL Commands
```bash
# Create instance
gcloud sql instances create pgadmin-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1

# Set password
gcloud sql users set-password postgres \
  --instance=pgadmin-db \
  --password=YOUR_PASSWORD

# Connect
gcloud sql connect pgadmin-db --user=postgres

# Get connection info
gcloud sql instances describe pgadmin-db
```

### Cloud Run Commands
```bash
# Deploy
gcloud run deploy pgadmin-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Update environment variables
gcloud run services update pgadmin-api \
  --region us-central1 \
  --update-env-vars=KEY=value,KEY2=value2

# View service
gcloud run services describe pgadmin-api --region us-central1

# Get service URL
gcloud run services describe pgadmin-api \
  --region us-central1 \
  --format='value(status.url)'

# View logs
gcloud run logs read pgadmin-api --region us-central1 --limit 50

# Delete service
gcloud run services delete pgadmin-api --region us-central1
```

### Secret Manager
```bash
# Create secret
echo -n "secret-value" | gcloud secrets create secret-name --data-file=-

# List secrets
gcloud secrets list

# Get secret value
gcloud secrets versions access latest --secret=secret-name

# Delete secret
gcloud secrets delete secret-name
```

---

## Deployment Checklist

Before deploying:

- [ ] GCP account created and project set up
- [ ] gcloud CLI installed and configured
- [ ] Docker Desktop installed
- [ ] `.env.production` file created
- [ ] Dockerfile verified
- [ ] Cloud SQL instance created
- [ ] Database and user created in PostgreSQL
- [ ] requirements.txt updated (includes gunicorn, whitenoise, psycopg2)
- [ ] settings.py updated for production
- [ ] `.gitignore` configured
- [ ] Local testing passed

During deployment:

- [ ] Run `gcloud run deploy` command
- [ ] Wait for build to complete (5-10 minutes)
- [ ] Verify Cloud Run service URL created
- [ ] Set environment variables for Cloud Run
- [ ] Test API endpoints with curl

After deployment:

- [ ] Check logs for errors
- [ ] Test all API endpoints
- [ ] Verify database connection
- [ ] Check Cloud Run metrics
- [ ] Set up monitoring alerts

---

## File Locations & URLs

```
Local Development:
  API: http://localhost:8000/
  Docs: http://localhost:8000/api/docs/

Production (after deployment):
  API: https://pgadmin-api-xxxxx.us-central1.run.app/
  Docs: https://pgadmin-api-xxxxx.us-central1.run.app/api/docs/

GCP Console URLs:
  Cloud Run: https://console.cloud.google.com/run
  Cloud SQL: https://console.cloud.google.com/sql/instances
  Cloud Build: https://console.cloud.google.com/cloud-build
  Logs: https://console.cloud.google.com/logs/query
```

---

## Environment Variables Reference

### Required
```
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-generated-key
DATABASE_NAME=pgadmin_production
DATABASE_USER=pgadmin_user
DATABASE_PASSWORD=your-password
DATABASE_HOST=10.x.x.x or public-ip
DATABASE_PORT=5432
```

### Recommended
```
ALLOWED_HOSTS=pgadmin-api-xxxxx.run.app
CORS_ALLOWED_ORIGINS=https://yourapp.com
STATIC_URL=/static/
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

## Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| 502 Bad Gateway | Check logs: `gcloud run logs read pgadmin-api` |
| Database connection failed | Verify DATABASE_HOST in env vars |
| Migrations not running | Check if Cloud Run has enough permissions |
| Static files not serving | Run `python manage.py collectstatic` |
| Timeout errors | Increase `--timeout` flag in deploy command |
| High CPU usage | Check for inefficient queries in logs |
| Deployment takes too long | Build is slow on first deploy - normal |

---

## Monitoring

### View Real-time Logs
```bash
gcloud run logs read pgadmin-api --region us-central1 --follow
```

### Check Service Status
```bash
gcloud run services describe pgadmin-api --region us-central1
```

### View Metrics
```bash
# Requests per second
gcloud monitoring time-series list \
  --filter='metric.type=run.googleapis.com/request_count'

# CPU usage
gcloud monitoring time-series list \
  --filter='metric.type=run.googleapis.com/cpu_allocations'

# Memory usage
gcloud monitoring time-series list \
  --filter='metric.type=run.googleapis.com/memory_allocations'
```

---

## Scaling & Performance

### Auto-scaling Settings
```bash
# Set max instances
gcloud run services update pgadmin-api \
  --max-instances 100 \
  --region us-central1

# Set min instances
gcloud run services update pgadmin-api \
  --min-instances 1 \
  --region us-central1

# Adjust CPU allocation
gcloud run services update pgadmin-api \
  --cpu 2 \
  --region us-central1

# Adjust memory
gcloud run services update pgadmin-api \
  --memory 2Gi \
  --region us-central1
```

---

## Backup & Recovery

### Cloud SQL Backups
```bash
# Create manual backup
gcloud sql backups create \
  --instance=pgadmin-db \
  --description="Pre-deployment backup"

# List backups
gcloud sql backups list --instance=pgadmin-db

# Restore from backup
gcloud sql backups restore BACKUP_ID \
  --backup-instance=pgadmin-db \
  --restore-instance=pgadmin-db
```

### Database Export
```bash
# Export to Cloud Storage
gcloud sql export sql pgadmin-db \
  gs://your-bucket/backup-$(date +%Y%m%d).sql \
  --database=pgadmin_production
```

---

## Cost Tracking

### Set Budget Alert
```bash
# Via console: https://console.cloud.google.com/billing
# Set budget limit: $5
# Create alert at 50%, 90%, 100%
```

### View Billing
```bash
gcloud billing accounts list
gcloud billing accounts describe ACCOUNT_ID
```

---

## Useful Links

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [gcloud CLI Reference](https://cloud.google.com/sdk/gcloud/reference)
- [Pricing Calculator](https://cloud.google.com/products/calculator)
- [GCP Console](https://console.cloud.google.com/)

---

## Getting Help

```bash
# Get help for any gcloud command
gcloud COMMAND --help
gcloud run deploy --help
gcloud sql instances create --help

# Check gcloud version
gcloud --version

# Update gcloud CLI
gcloud components update
```

---

## One-Line Deployment (After Initial Setup)

```bash
# Make changes locally, then deploy in one command:
git push && gcloud run deploy pgadmin-api --source . --region us-central1 --platform managed
```

---

**Save this page for quick reference during deployment!** 🚀
