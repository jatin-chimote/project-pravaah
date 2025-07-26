#!/bin/bash

# =============================================================================
# Project Pravaah - Pre-Deployment Verification Script
# =============================================================================
# Verifies all required files and configurations are ready for deployment
# Run this script before executing deploy.sh
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
CHECKS_PASSED=0
CHECKS_FAILED=0
TOTAL_CHECKS=0

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✅ PASS]${NC} $1"
    ((CHECKS_PASSED++))
}

log_error() {
    echo -e "${RED}[❌ FAIL]${NC} $1"
    ((CHECKS_FAILED++))
}

log_warning() {
    echo -e "${YELLOW}[⚠️  WARN]${NC} $1"
}

check_file() {
    local file_path=$1
    local description=$2
    ((TOTAL_CHECKS++))
    
    if [[ -f "$file_path" ]]; then
        log_success "$description: $file_path"
    else
        log_error "$description: $file_path (MISSING)"
    fi
}

check_directory() {
    local dir_path=$1
    local description=$2
    ((TOTAL_CHECKS++))
    
    if [[ -d "$dir_path" ]]; then
        log_success "$description: $dir_path"
    else
        log_error "$description: $dir_path (MISSING)"
    fi
}

check_gcp_setup() {
    log_info "Checking Google Cloud setup..."
    ((TOTAL_CHECKS++))
    
    if command -v gcloud &> /dev/null; then
        log_success "gcloud CLI is installed"
        
        # Check if authenticated
        if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
            log_success "gcloud is authenticated"
            
            # Check project
            local current_project=$(gcloud config get-value project 2>/dev/null || echo "")
            if [[ "$current_project" == "stable-sign-454210-i0" ]]; then
                log_success "Correct GCP project set: $current_project"
            else
                log_error "Wrong GCP project. Current: $current_project, Expected: stable-sign-454210-i0"
            fi
        else
            log_error "gcloud is not authenticated. Run 'gcloud auth login'"
        fi
    else
        log_error "gcloud CLI is not installed"
    fi
}

main() {
    echo "============================================================================="
    echo "🔍 Project Pravaah - Pre-Deployment Verification"
    echo "============================================================================="
    
    # Check core deployment files
    log_info "Checking deployment scripts..."
    check_file "deploy.sh" "Main deployment script"
    check_file "DEPLOYMENT_CHECKLIST.md" "Deployment checklist"
    
    # Check API Gateway service
    log_info "Checking API Gateway service files..."
    check_directory "api_gateway_service" "API Gateway service directory"
    check_file "api_gateway_service/main.py" "API Gateway main application"
    check_file "api_gateway_service/Dockerfile" "API Gateway Dockerfile"
    check_file "api_gateway_service/requirements.txt" "API Gateway requirements"
    
    # Check agents directory
    log_info "Checking agents directory..."
    check_directory "agents" "Agents directory"
    
    # Check for ADK agent files (these would be needed for individual service deployment)
    log_info "Checking ADK agent files..."
    check_file "agents/adk_observer_agent.py" "ADK Observer Agent"
    check_file "agents/adk_simulation_agent.py" "ADK Simulation Agent"
    check_file "agents/adk_orchestrator_agent.py" "ADK Orchestrator Agent"
    check_file "agents/adk_communications_agent.py" "ADK Communications Agent"
    
    # Check for original agent files (fallback)
    log_info "Checking original agent files (fallback)..."
    check_file "agents/observer_agent.py" "Original Observer Agent"
    check_file "agents/simulation_agent.py" "Original Simulation Agent"
    check_file "agents/orchestrator_agent.py" "Original Orchestrator Agent"
    check_file "agents/communications_agent.py" "Original Communications Agent"
    
    # Check demo files
    log_info "Checking demo files..."
    check_file "main_demo.py" "Demo main application"
    check_file "demo_agents.py" "Demo agents"
    
    # Check Google Cloud setup (only if gcloud is available)
    if command -v gcloud &> /dev/null; then
        check_gcp_setup
    else
        log_warning "gcloud CLI not available (expected in Cloud Shell)"
    fi
    
    # Summary
    echo ""
    echo "============================================================================="
    echo "📊 Verification Summary"
    echo "============================================================================="
    echo "Total Checks: $TOTAL_CHECKS"
    echo "Passed: $CHECKS_PASSED"
    echo "Failed: $CHECKS_FAILED"
    
    if [[ $CHECKS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}🎉 All checks passed! Ready for deployment.${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Upload this backend folder to Google Cloud Shell"
        echo "2. Run: chmod +x deploy.sh"
        echo "3. Run: ./deploy.sh"
        exit 0
    else
        echo -e "${RED}❌ Some checks failed. Please fix the issues before deployment.${NC}"
        echo ""
        echo "Common fixes:"
        echo "- Ensure all files are present in the backend directory"
        echo "- Check that ADK agent files exist for microservices deployment"
        echo "- Verify Google Cloud project access and authentication"
        exit 1
    fi
}

main "$@"
