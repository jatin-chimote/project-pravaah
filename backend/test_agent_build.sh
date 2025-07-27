#!/bin/bash

# Quick test script to verify agent service Docker build works
# Run this before full deployment to catch issues early

set -euo pipefail

PROJECT_ID="stable-sign-454210-i0"
BUILD_REGION="us-central1"
REGISTRY_URL="asia-south1-docker.pkg.dev/${PROJECT_ID}/pravaah-services"

echo "Testing orchestrator service Docker build..."

# Test build for orchestrator service
gcloud builds submit agents \
    --tag="${REGISTRY_URL}/orchestrator-service:test" \
    --project=$PROJECT_ID \
    --region=$BUILD_REGION \
    --file=Dockerfile

echo "✅ Orchestrator service build test successful!"
echo "Ready to run full deployment with ./deploy.sh"
