#!/bin/bash

# =============================================================================
# Project Pravaah - Alternative Deployment Script (Local Docker Build)
# =============================================================================
# Alternative deployment approach that builds containers locally and pushes
# to Artifact Registry, bypassing Cloud Build quota restrictions
# 
# Prerequisites:
# - Docker installed in Cloud Shell
# - gcloud configured and authenticated
# =============================================================================

set -euo pipefail

# GCP Configuration
PROJECT_ID="stable-sign-454210-i0"
REGION="asia-south1"
REPOSITORY_NAME="pravaah-services"
SERVICE_ACCOUNT="pravaah-agent-runner@${PROJECT_ID}.iam.gserviceaccount.com"

# Docker Registry Configuration
REGISTRY_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}"

# Service Configuration
declare -a SERVICES=(
    "api-gateway-service"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

check_docker() {
    log_info "Checking Docker availability..."
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Installing Docker in Cloud Shell..."
        # Install Docker in Cloud Shell
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        log_success "Docker installed. Please restart Cloud Shell and run this script again."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Starting Docker..."
        sudo systemctl start docker || sudo service docker start
    fi
    
    log_success "Docker is ready"
}

setup_artifact_registry() {
    log_info "Setting up Artifact Registry..."
    
    # Enable APIs
    gcloud services enable artifactregistry.googleapis.com --project=$PROJECT_ID
    gcloud services enable run.googleapis.com --project=$PROJECT_ID
    
    # Check if repository exists
    if gcloud artifacts repositories describe $REPOSITORY_NAME \
        --location=$REGION --project=$PROJECT_ID &>/dev/null; then
        log_warning "Repository $REPOSITORY_NAME already exists"
    else
        log_info "Creating Artifact Registry repository: $REPOSITORY_NAME"
        gcloud artifacts repositories create $REPOSITORY_NAME \
            --repository-format=docker \
            --location=$REGION \
            --description="Project Pravaah microservices container registry" \
            --project=$PROJECT_ID
        log_success "Artifact Registry repository created"
    fi
    
    # Configure Docker authentication
    gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet
    log_success "Docker authentication configured"
}

build_and_push_local() {
    local service_name=$1
    local service_dir=""
    
    log_info "Processing service: $service_name"
    
    # Determine service directory
    case $service_name in
        "api-gateway-service")
            service_dir="api_gateway_service"
            ;;
        *)
            log_error "Unknown service: $service_name"
            return 1
            ;;
    esac
    
    # Check if service directory exists
    if [[ ! -d "$service_dir" ]]; then
        log_error "Service directory $service_dir not found"
        return 1
    fi
    
    local image_tag="${REGISTRY_URL}/${service_name}:latest"
    
    # Build container image locally
    log_info "Building container image locally for $service_name..."
    if docker build -t "$image_tag" "$service_dir"; then
        log_success "Container built locally: $image_tag"
    else
        log_error "Failed to build container for $service_name"
        return 1
    fi
    
    # Push to Artifact Registry
    log_info "Pushing image to Artifact Registry..."
    if docker push "$image_tag"; then
        log_success "Image pushed: $image_tag"
    else
        log_error "Failed to push image for $service_name"
        return 1
    fi
    
    # Deploy to Cloud Run
    log_info "Deploying $service_name to Cloud Run..."
    
    local deploy_args=(
        "--image=$image_tag"
        "--platform=managed"
        "--region=$REGION"
        "--project=$PROJECT_ID"
        "--service-account=$SERVICE_ACCOUNT"
        "--set-env-vars=GCP_PROJECT_ID=$PROJECT_ID,ENVIRONMENT=production"
        "--memory=1Gi"
        "--cpu=1"
        "--concurrency=100"
        "--max-instances=10"
        "--timeout=300"
        "--allow-unauthenticated"
    )
    
    if gcloud run deploy "$service_name" "${deploy_args[@]}"; then
        log_success "Service deployed: $service_name"
        
        # Get service URL
        local service_url=$(gcloud run services describe "$service_name" \
            --region=$REGION --project=$PROJECT_ID \
            --format="value(status.url)")
        echo "  Service URL: $service_url"
        
        # Store URL for later use
        declare -g "${service_name//-/_}_URL=$service_url"
        
    else
        log_error "Failed to deploy $service_name"
        return 1
    fi
}

main() {
    echo "============================================================================="
    echo "🚀 Project Pravaah - Local Build Deployment (Cloud Build Alternative)"
    echo "============================================================================="
    echo "Project ID: $PROJECT_ID"
    echo "Region: $REGION"
    echo "Repository: $REPOSITORY_NAME"
    echo "============================================================================="
    
    # Check prerequisites
    gcloud config set project $PROJECT_ID
    check_docker
    setup_artifact_registry
    
    echo ""
    echo "🔨 Building and Deploying Services (Local Build)..."
    echo "============================================================================="
    
    # Build and deploy each service
    for service in "${SERVICES[@]}"; do
        echo ""
        if build_and_push_local "$service"; then
            log_success "Successfully deployed $service"
        else
            log_error "Failed to deploy $service"
        fi
    done
    
    echo ""
    echo "============================================================================="
    echo "🎉 Local Build Deployment Complete!"
    echo "============================================================================="
    
    if [[ -n "${api_gateway_service_URL:-}" ]]; then
        echo ""
        echo "🌐 Public API Gateway URL:"
        echo "   ${api_gateway_service_URL}"
        echo ""
        echo "📖 API Documentation:"
        echo "   ${api_gateway_service_URL}/docs"
        echo ""
        echo "🧪 Test the deployment:"
        echo "   curl ${api_gateway_service_URL}/health"
    fi
    
    echo ""
    echo "Deployment completed at: $(date)"
    echo "============================================================================="
}

# Run main deployment
main "$@"
