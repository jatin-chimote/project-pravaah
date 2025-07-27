#!/bin/bash

# =============================================================================
# Project Pravaah - Orchestrator Service Deployment
# =============================================================================
# Deploy only the orchestrator service for testing
# =============================================================================

set -euo pipefail

# Configuration
PROJECT_ID="stable-sign-454210-i0"
REGION="asia-south1"
BUILD_REGION="us-central1"
REPOSITORY_NAME="pravaah-services"
SERVICE_ACCOUNT="pravaah-agent-runner@${PROJECT_ID}.iam.gserviceaccount.com"
REGISTRY_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}"

SERVICE_NAME="orchestrator-service"
SERVICE_DIR="agents"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "============================================================================="
echo "🚀 Project Pravaah - Orchestrator Service Deployment"
echo "============================================================================="

# Set project
gcloud config set project $PROJECT_ID

image_tag="${REGISTRY_URL}/${SERVICE_NAME}:latest"

# Build container image
log_info "Building container image for $SERVICE_NAME..."
if gcloud builds submit "$SERVICE_DIR" \
    --tag="$image_tag" \
    --project=$PROJECT_ID \
    --region=$BUILD_REGION; then
    log_success "Container built: $image_tag"
else
    log_error "Failed to build container for $SERVICE_NAME"
    exit 1
fi

# Deploy to Cloud Run
log_info "Deploying $SERVICE_NAME to Cloud Run..."

if gcloud run deploy "$SERVICE_NAME" \
    --image="$image_tag" \
    --platform=managed \
    --region=$REGION \
    --project=$PROJECT_ID \
    --service-account=$SERVICE_ACCOUNT \
    --set-env-vars=GCP_PROJECT_ID=$PROJECT_ID,ENVIRONMENT=production \
    --memory=1Gi \
    --cpu=1 \
    --concurrency=100 \
    --max-instances=10 \
    --timeout=300 \
    --no-allow-unauthenticated \
    --command=python \
    --args=-m,uvicorn,orchestrator_service:app,--host,0.0.0.0,--port,8080; then
    
    log_success "Service deployed: $SERVICE_NAME"
    
    # Get service URL
    service_url=$(gcloud run services describe "$SERVICE_NAME" \
        --region=$REGION --project=$PROJECT_ID \
        --format="value(status.url)")
    echo "  Service URL: $service_url"
    
    echo ""
    echo "🧪 Testing service (requires authentication)..."
    echo "To test manually:"
    echo "  gcloud run services proxy $SERVICE_NAME --port=8080 --region=$REGION"
    echo "  Then: curl http://localhost:8080/health"
    
else
    log_error "Failed to deploy $SERVICE_NAME"
    exit 1
fi

echo ""
echo "============================================================================="
echo "🎉 Orchestrator Service Deployment Complete!"
echo "============================================================================="
echo "Service: $SERVICE_NAME"
echo "URL: $service_url"
echo "Status: Deployed successfully"
echo "============================================================================="
