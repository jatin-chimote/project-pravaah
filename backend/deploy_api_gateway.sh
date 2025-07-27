#!/bin/bash

# =============================================================================
# Project Pravaah - API Gateway Service Deployment
# =============================================================================
# Deploy only the API Gateway service for testing
# =============================================================================

set -euo pipefail

# Configuration
PROJECT_ID="stable-sign-454210-i0"
REGION="asia-south1"
BUILD_REGION="us-central1"
REPOSITORY_NAME="pravaah-services"
SERVICE_ACCOUNT="pravaah-agent-runner@${PROJECT_ID}.iam.gserviceaccount.com"
REGISTRY_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}"

SERVICE_NAME="api-gateway-service"
SERVICE_DIR="api_gateway_service"

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
echo "🚀 Project Pravaah - API Gateway Service Deployment"
echo "============================================================================="

# Set project
gcloud config set project $PROJECT_ID

# Check if service directory exists
if [[ ! -d "$SERVICE_DIR" ]]; then
    log_error "Service directory $SERVICE_DIR not found"
    exit 1
fi

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
    --allow-unauthenticated; then
    
    log_success "Service deployed: $SERVICE_NAME"
    
    # Get service URL
    service_url=$(gcloud run services describe "$SERVICE_NAME" \
        --region=$REGION --project=$PROJECT_ID \
        --format="value(status.url)")
    echo "  Service URL: $service_url"
    
    echo ""
    echo "🧪 Testing public API Gateway..."
    if curl -f -s "$service_url/health" > /dev/null; then
        log_success "API Gateway health check passed"
        echo "✅ API Gateway is publicly accessible"
    else
        log_error "API Gateway health check failed"
    fi
    
    echo ""
    echo "📖 API Documentation available at:"
    echo "   $service_url/docs"
    
else
    log_error "Failed to deploy $SERVICE_NAME"
    exit 1
fi

echo ""
echo "============================================================================="
echo "🎉 API Gateway Service Deployment Complete!"
echo "============================================================================="
echo "Service: $SERVICE_NAME"
echo "URL: $service_url"
echo "Status: Deployed successfully (PUBLIC)"
echo "Documentation: $service_url/docs"
echo ""
echo "🔗 Ready to connect Angular frontend to this API Gateway URL"
echo "============================================================================="
