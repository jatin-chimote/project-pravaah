#!/bin/bash

# =============================================================================
# Project Pravaah - Quick Agentic Flow Test
# =============================================================================
# Simplified version for rapid testing during development
# =============================================================================

# Configuration
API_GATEWAY_URL="https://api-gateway-service-vzjgh3ibra-el.a.run.app"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Quick Agentic Flow Test${NC}"
echo "============================================================================="

# Test 1: API Gateway Health
echo -e "${BLUE}Testing API Gateway...${NC}"
curl -s "$API_GATEWAY_URL/health" | jq '.' || echo "API Gateway not responding"

echo ""

# Test 2: Simple Orchestration
echo -e "${BLUE}Testing End-to-End Orchestration...${NC}"
curl -s -X POST "$API_GATEWAY_URL/run_orchestration" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "quick_test",
    "location": "Electronic City",
    "correlation_id": "quick-test-001"
  }' | jq '.' || echo "Orchestration failed"

echo ""
echo -e "${GREEN}✅ Quick test complete!${NC}"
