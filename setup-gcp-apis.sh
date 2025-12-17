#!/bin/bash
# ============================================================================
# GCP Setup Script - Enable Required APIs for Cloud Build & Cloud Run
# ============================================================================
# Run this ONCE before triggering Cloud Build
# This script enables all required GCP services
# ============================================================================

PROJECT_ID=$(gcloud config get-value project)

echo ""
echo "🔧 Enabling Required GCP Services for pgAdmin API..."
echo "Project ID: $PROJECT_ID"
echo ""

# Array of required services
SERVICES=(
  "cloudbuild.googleapis.com"           # Cloud Build
  "run.googleapis.com"                   # Cloud Run
  "artifactregistry.googleapis.com"     # Artifact Registry (for Docker images)
  "cloudsql.googleapis.com"              # Cloud SQL
  "secretmanager.googleapis.com"         # Secret Manager
  "compute.googleapis.com"               # Compute (for networking)
  "servicenetworking.googleapis.com"     # Service Networking
)

echo "Enabling services..."
for service in "${SERVICES[@]}"; do
  echo "  ✓ Enabling $service..."
  gcloud services enable "$service" --quiet
done

echo ""
echo "✅ All services enabled!"
echo ""

# Get project number
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
CLOUD_BUILD_SA="$PROJECT_NUMBER@cloudbuild.gserviceaccount.com"

echo "🔐 Granting Cloud Build Service Account Permissions..."
echo "Service Account: $CLOUD_BUILD_SA"
echo ""

# Grant required IAM roles
ROLES=(
  "roles/run.admin"                    # Cloud Run Admin
  "roles/cloudsql.client"              # Cloud SQL Client
  "roles/secretmanager.secretAccessor" # Secret Manager Access
  "roles/artifactregistry.admin"       # Artifact Registry Admin
  "roles/editor"                       # Editor (for broader permissions during testing)
)

for role in "${ROLES[@]}"; do
  echo "  ✓ Granting $role..."
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member=serviceAccount:$CLOUD_BUILD_SA \
    --role=$role \
    --quiet
done

echo ""
echo "✅ Service Account permissions granted!"
echo ""

# Create Artifact Registry repository if it doesn't exist
echo "🐳 Setting up Artifact Registry Repository..."
REPO_NAME="cloud-run-source-deploy"
REGION="us-central1"

# Check if repository exists
if gcloud artifacts repositories describe $REPO_NAME --location=$REGION &>/dev/null; then
  echo "  ✓ Repository $REPO_NAME already exists in $REGION"
else
  echo "  ✓ Creating repository $REPO_NAME in $REGION..."
  gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --quiet
fi

echo ""
echo "✅ Artifact Registry Repository ready!"
echo ""

# Verify Secret Manager secrets exist
echo "🔑 Verifying Secret Manager Secrets..."
SECRETS=("db-password" "django-secret-key" "database-host")

for secret in "${SECRETS[@]}"; do
  if gcloud secrets describe $secret &>/dev/null; then
    echo "  ✓ Secret '$secret' exists"
  else
    echo "  ⚠️  Secret '$secret' NOT FOUND"
    echo "     Run: echo -n 'value' | gcloud secrets create $secret --data-file=-"
  fi
done

echo ""
echo "========================================="
echo "✅ GCP Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Verify all secrets exist (create missing ones if needed)"
echo "2. Commit cloudbuild.yaml changes to GitHub"
echo "3. Push to main branch to trigger Cloud Build"
echo "4. Monitor build: gcloud builds list --limit=5"
echo "5. Check logs: gcloud builds log BUILD_ID"
echo ""
