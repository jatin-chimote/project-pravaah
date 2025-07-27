#!/bin/bash

# =============================================================================
# Project Pravaah - Comprehensive GCP Deployment Script
# =============================================================================
# Deploys complete microservices architecture to Google Cloud Platform
# 
# Services Deployed:
# - api-gateway-service (Public)
# - orchestrator-service (Private)
# - simulation-service (Private) 
# - observer-service (Private)
# - communications-service (Private)
#
# Author: Project Pravaah Team
# GCP Project: stable-sign-454210-i0
# Region: asia-south1
# =============================================================================

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# =============================================================================
# Configuration Variables
# =============================================================================

# GCP Configuration
PROJECT_ID="stable-sign-454210-i0"
REGION="asia-south1"  # Cloud Run deployment region
BUILD_REGION="us-central1"  # Cloud Build region (to avoid quota issues)
REPOSITORY_NAME="pravaah-services"
SERVICE_ACCOUNT="pravaah-agent-runner@${PROJECT_ID}.iam.gserviceaccount.com"

# Docker Registry Configuration
REGISTRY_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY_NAME}"

# Service Configuration
declare -a SERVICES=(
    "api-gateway-service"
    "orchestrator-service" 
    "simulation-service"
    "observer-service"
    "communications-service"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# Utility Functions
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed. Please install Google Cloud SDK."
        exit 1
    fi
    
    # Check if authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "Not authenticated with gcloud. Run 'gcloud auth login'"
        exit 1
    fi
    
    # Set project
    gcloud config set project $PROJECT_ID
    log_success "Prerequisites checked"
}

enable_apis() {
    log_info "Enabling required Google Cloud APIs..."
    
    local apis=(
        "cloudbuild.googleapis.com"
        "run.googleapis.com"
        "artifactregistry.googleapis.com"
        "iam.googleapis.com"
        "cloudresourcemanager.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        log_info "Enabling $api..."
        gcloud services enable $api --project=$PROJECT_ID
    done
    
    log_success "All APIs enabled"
}

setup_artifact_registry() {
    log_info "Setting up Artifact Registry..."
    
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

build_and_deploy_service() {
    local service_name=$1
    local service_dir=""
    
    log_info "Processing service: $service_name"
    
    # Determine service directory and entry point based on naming convention
    case $service_name in
        "api-gateway-service")
            service_dir="api_gateway_service"
            ;;
        "orchestrator-service")
            service_dir="agents"
            ;;
        "simulation-service")
            service_dir="agents"
            ;;
        "observer-service")
            service_dir="agents"
            ;;
        "communications-service")
            service_dir="agents"
            ;;
        *)
            log_error "Unknown service: $service_name"
            return 1
            ;;
    esac
    
    # Check if service directory exists
    if [[ ! -d "$service_dir" ]]; then
        log_warning "Service directory $service_dir not found, skipping $service_name"
        return 0
    fi
    
    local image_tag="${REGISTRY_URL}/${service_name}:latest"
    
    # Build container image using Cloud Build
    log_info "Building container image for $service_name..."
    
    if gcloud builds submit "$service_dir" \
        --tag="$image_tag" \
        --project=$PROJECT_ID \
        --region=$BUILD_REGION; then
        log_success "Container built: $image_tag"
    else
        log_error "Failed to build container for $service_name"
        return 1
    fi
    
    # Deploy to Cloud Run
    log_info "Deploying $service_name to Cloud Run..."
    
    # Set service-specific environment variables and commands
    local service_env_vars="GCP_PROJECT_ID=$PROJECT_ID,ENVIRONMENT=production"
    local service_cmd=""
    
    case $service_name in
        "orchestrator-service")
            service_cmd="--command=python,--args=-m,uvicorn,orchestrator_service:app,--host,0.0.0.0,--port,8080"
            ;;
        "simulation-service")
            service_cmd="--command=python,--args=-m,uvicorn,simulation_service:app,--host,0.0.0.0,--port,8080"
            ;;
        "observer-service")
            service_cmd="--command=python,--args=-m,uvicorn,observer_service:app,--host,0.0.0.0,--port,8080"
            ;;
        "communications-service")
            service_cmd="--command=python,--args=-m,uvicorn,communications_service:app,--host,0.0.0.0,--port,8080"
            ;;
    esac
    
    local deploy_args=(
        "--image=$image_tag"
        "--platform=managed"
        "--region=$REGION"
        "--project=$PROJECT_ID"
        "--service-account=$SERVICE_ACCOUNT"
        "--set-env-vars=$service_env_vars"
        "--memory=1Gi"
        "--cpu=1"
        "--concurrency=100"
        "--max-instances=10"
        "--timeout=300"
    )
    
    # Add service-specific command if defined
    if [[ -n "$service_cmd" ]]; then
        deploy_args+=($service_cmd)
    fi
    
    # Configure authentication based on service type
    if [[ "$service_name" == "api-gateway-service" ]]; then
        deploy_args+=("--allow-unauthenticated")
        log_info "Deploying $service_name as PUBLIC service"
    else
        deploy_args+=("--no-allow-unauthenticated")
        log_info "Deploying $service_name as PRIVATE service"
    fi
    
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

setup_service_permissions() {
    log_info "Setting up service-to-service permissions..."
    
    # Get service account emails for each service
    local gateway_sa=$(gcloud run services describe api-gateway-service \
        --region=$REGION --project=$PROJECT_ID \
        --format="value(spec.template.spec.serviceAccountName)" 2>/dev/null || echo "$SERVICE_ACCOUNT")
    
    local orchestrator_sa=$(gcloud run services describe orchestrator-service \
        --region=$REGION --project=$PROJECT_ID \
        --format="value(spec.template.spec.serviceAccountName)" 2>/dev/null || echo "$SERVICE_ACCOUNT")
    
    # Grant API Gateway permission to invoke Orchestrator
    if gcloud run services describe orchestrator-service --region=$REGION --project=$PROJECT_ID &>/dev/null; then
        log_info "Granting API Gateway permission to invoke Orchestrator service..."
        gcloud run services add-iam-policy-binding orchestrator-service \
            --region=$REGION \
            --project=$PROJECT_ID \
            --member="serviceAccount:$gateway_sa" \
            --role="roles/run.invoker"
        log_success "API Gateway → Orchestrator permissions set"
    fi
    
    # Grant Orchestrator permission to invoke other agent services
    for service in "simulation-service" "observer-service" "communications-service"; do
        if gcloud run services describe "$service" --region=$REGION --project=$PROJECT_ID &>/dev/null; then
            log_info "Granting Orchestrator permission to invoke $service..."
            gcloud run services add-iam-policy-binding "$service" \
                --region=$REGION \
                --project=$PROJECT_ID \
                --member="serviceAccount:$orchestrator_sa" \
                --role="roles/run.invoker"
            log_success "Orchestrator → $service permissions set"
        fi
    done
    
    log_success "Service-to-service permissions configured"
}

perform_health_checks() {
    log_info "Performing health checks on deployed services..."
    
    # Check API Gateway (public endpoint)
    if [[ -n "${api_gateway_service_URL:-}" ]]; then
        log_info "Health checking API Gateway..."
        if curl -f -s "${api_gateway_service_URL}/health" > /dev/null; then
            log_success "API Gateway health check passed"
        else
            log_warning "API Gateway health check failed"
        fi
    fi
    
    # Note: Other services are private and require authentication for health checks
    log_info "Private services require authentication for health checks"
}

cleanup_old_images() {
    log_info "Cleaning up old container images..."
    
    # Keep last 5 versions of each image
    for service in "${SERVICES[@]}"; do
        log_info "Cleaning up old images for $service..."
        gcloud artifacts docker images list "${REGISTRY_URL}/${service}" \
            --include-tags --format="value(IMAGE)" \
            --sort-by="~UPDATE_TIME" \
            --limit=999 | tail -n +6 | \
        while read image; do
            if [[ -n "$image" ]]; then
                gcloud artifacts docker images delete "$image" --quiet || true
            fi
        done
    done
    
    log_success "Image cleanup completed"
}

# =============================================================================
# Main Deployment Flow
# =============================================================================

main() {
    echo "============================================================================="
    echo "🚀 Project Pravaah - GCP Microservices Deployment"
    echo "============================================================================="
    echo "Project ID: $PROJECT_ID"
    echo "Region: $REGION"
    echo "Repository: $REPOSITORY_NAME"
    echo "Services: ${SERVICES[*]}"
    echo "============================================================================="
    
    # Pre-deployment checks
    check_prerequisites
    enable_apis
    setup_artifact_registry
    
    echo ""
    echo "🔨 Building and Deploying Services..."
    echo "============================================================================="
    
    # Build and deploy each service
    local deployed_services=()
    local failed_services=()
    
    for service in "${SERVICES[@]}"; do
        echo ""
        if build_and_deploy_service "$service"; then
            deployed_services+=("$service")
        else
            failed_services+=("$service")
        fi
    done
    
    echo ""
    echo "🔐 Configuring Service Permissions..."
    echo "============================================================================="
    setup_service_permissions
    
    echo ""
    echo "🏥 Performing Health Checks..."
    echo "============================================================================="
    perform_health_checks
    
    echo ""
    echo "🧹 Cleaning Up Old Images..."
    echo "============================================================================="
    cleanup_old_images
    
    # Final deployment summary
    echo ""
    echo "============================================================================="
    echo "🎉 Deployment Complete!"
    echo "============================================================================="
    
    if [[ ${#deployed_services[@]} -gt 0 ]]; then
        echo "✅ Successfully Deployed Services:"
        for service in "${deployed_services[@]}"; do
            local url_var="${service//-/_}_URL"
            local url="${!url_var:-N/A}"
            echo "   - $service: $url"
        done
    fi
    
    if [[ ${#failed_services[@]} -gt 0 ]]; then
        echo ""
        echo "❌ Failed Services:"
        for service in "${failed_services[@]}"; do
            echo "   - $service"
        done
    fi
    
    # Show public API Gateway URL
    if [[ -n "${api_gateway_service_URL:-}" ]]; then
        echo ""
        echo "🌐 Public API Gateway URL:"
        echo "   ${api_gateway_service_URL}"
        echo ""
        echo "📖 API Documentation:"
        echo "   ${api_gateway_service_URL}/docs"
    fi
    
    echo ""
    echo "🔧 Next Steps:"
    echo "   1. Test API Gateway: curl ${api_gateway_service_URL:-https://api-gateway-service-PROJECT.a.run.app}/health"
    echo "   2. Configure Angular frontend to use API Gateway URL"
    echo "   3. Set up monitoring and alerting"
    echo "   4. Configure custom domain (optional)"
    echo ""
    echo "Deployment completed at: $(date)"
    echo "============================================================================="
}

# =============================================================================
# Script Execution
# =============================================================================

# Handle script interruption
trap 'log_error "Deployment interrupted"; exit 1' INT TERM

# Run main deployment
main "$@"
