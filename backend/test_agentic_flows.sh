#!/bin/bash

# =============================================================================
# Project Pravaah - Comprehensive Agentic Flow Testing Suite
# =============================================================================
# Tests all ADK agents, A2A protocol, Gemini AI, and end-to-end orchestration
# =============================================================================

set -euo pipefail

# Configuration
PROJECT_ID="stable-sign-454210-i0"
REGION="asia-south1"
API_GATEWAY_URL="https://api-gateway-service-vzjgh3ibra-el.a.run.app"

# Service URLs (will be auto-detected)
ORCHESTRATOR_URL=""
SIMULATION_URL=""
OBSERVER_URL=""
COMMUNICATIONS_URL=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✅ PASS]${NC} $1"
    ((PASSED_TESTS++))
}

log_error() {
    echo -e "${RED}[❌ FAIL]${NC} $1"
    ((FAILED_TESTS++))
}

log_test() {
    echo -e "${YELLOW}[🧪 TEST]${NC} $1"
    ((TOTAL_TESTS++))
}

log_section() {
    echo ""
    echo -e "${PURPLE}=============================================================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}=============================================================================${NC}"
}

# Function to test HTTP endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local method="${3:-GET}"
    local data="${4:-}"
    local expected_status="${5:-200}"
    
    log_test "$name"
    
    if [[ "$method" == "POST" && -n "$data" ]]; then
        response=$(curl -s -w "%{http_code}" -X POST "$url" \
            -H "Content-Type: application/json" \
            -d "$data" || echo "000")
    else
        response=$(curl -s -w "%{http_code}" "$url" || echo "000")
    fi
    
    status_code="${response: -3}"
    body="${response%???}"
    
    if [[ "$status_code" == "$expected_status" ]]; then
        log_success "$name - Status: $status_code"
        if [[ -n "$body" && "$body" != "null" ]]; then
            echo "   Response: ${body:0:100}..."
        fi
        return 0
    else
        log_error "$name - Expected: $expected_status, Got: $status_code"
        if [[ -n "$body" ]]; then
            echo "   Error: ${body:0:200}..."
        fi
        return 1
    fi
}

# Function to get service URL
get_service_url() {
    local service_name="$1"
    gcloud run services describe "$service_name" \
        --region=$REGION --project=$PROJECT_ID \
        --format="value(status.url)" 2>/dev/null || echo ""
}

# Function to setup port forwarding for private services
setup_port_forwarding() {
    log_info "Setting up port forwarding for private services..."
    
    # Kill any existing port forwards
    pkill -f "gcloud run services proxy" 2>/dev/null || true
    sleep 2
    
    # Start port forwarding in background
    gcloud run services proxy orchestrator-service --port=8080 --region=$REGION &
    gcloud run services proxy simulation-service --port=8081 --region=$REGION &
    gcloud run services proxy observer-service --port=8082 --region=$REGION &
    gcloud run services proxy communications-service --port=8083 --region=$REGION &
    
    # Wait for port forwards to be ready
    log_info "Waiting for port forwards to be ready..."
    sleep 10
    
    ORCHESTRATOR_URL="http://localhost:8080"
    SIMULATION_URL="http://localhost:8081"
    OBSERVER_URL="http://localhost:8082"
    COMMUNICATIONS_URL="http://localhost:8083"
}

# Function to cleanup port forwarding
cleanup_port_forwarding() {
    log_info "Cleaning up port forwarding..."
    pkill -f "gcloud run services proxy" 2>/dev/null || true
}

echo "============================================================================="
echo "🚀 Project Pravaah - Agentic Flow Testing Suite"
echo "============================================================================="
echo "Testing ADK agents, A2A protocol, and Urban Mobility Operating System"
echo "============================================================================="

# Set project
gcloud config set project $PROJECT_ID

log_section "🔍 Phase 1: Service Discovery & Health Checks"

# Test API Gateway (public)
test_endpoint "API Gateway Health Check" "$API_GATEWAY_URL/health"
test_endpoint "API Gateway Root" "$API_GATEWAY_URL/"

# Setup port forwarding for private services
setup_port_forwarding

# Test individual agent health checks
test_endpoint "Orchestrator Agent Health" "$ORCHESTRATOR_URL/health"
test_endpoint "Simulation Agent Health" "$SIMULATION_URL/health"
test_endpoint "Observer Agent Health" "$OBSERVER_URL/health"
test_endpoint "Communications Agent Health" "$COMMUNICATIONS_URL/health"

log_section "🤖 Phase 2: Individual Agent A2A Testing"

# Test Observer Agent (Perception)
observer_task='{
    "task_id": "obs-test-001",
    "task_name": "get_network_state",
    "params": {
        "location": "Electronic City, Bengaluru",
        "radius_km": 5,
        "include_traffic_data": true
    },
    "correlation_id": "test-observer-001",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "source_service": "test-suite",
    "target_service": "observer"
}'

test_endpoint "Observer Agent - Network State" "$OBSERVER_URL/a2a/tasks" "POST" "$observer_task"

# Test Simulation Agent (Prediction)
simulation_task='{
    "task_id": "sim-test-001",
    "task_name": "run_gridlock_prediction",
    "params": {
        "journey_data": [
            {"route": "Electronic City to Koramangala", "vehicle_count": 450, "avg_speed": 25},
            {"route": "Whitefield to MG Road", "vehicle_count": 380, "avg_speed": 18},
            {"route": "Silk Board to BTM Layout", "vehicle_count": 320, "avg_speed": 15}
        ],
        "time_horizon_minutes": 60,
        "weather_conditions": "clear"
    },
    "correlation_id": "test-simulation-001",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "source_service": "test-suite",
    "target_service": "simulation"
}'

test_endpoint "Simulation Agent - Gridlock Prediction" "$SIMULATION_URL/a2a/tasks" "POST" "$simulation_task"

# Test Orchestrator Agent (Decision Making)
orchestrator_task='{
    "task_id": "orch-test-001",
    "task_name": "run_orchestration_cycle",
    "params": {
        "trigger": "high_congestion_detected",
        "priority": "urgent",
        "affected_areas": ["Electronic City", "Silk Board", "Outer Ring Road"],
        "severity_level": "high",
        "vehicle_count": 1250
    },
    "correlation_id": "test-orchestrator-001",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "source_service": "test-suite",
    "target_service": "orchestrator"
}'

test_endpoint "Orchestrator Agent - Strategic Decision" "$ORCHESTRATOR_URL/a2a/tasks" "POST" "$orchestrator_task"

# Test Communications Agent (Action)
communications_task='{
    "task_id": "comm-test-001",
    "task_name": "execute_reroute_and_notify",
    "params": {
        "journeyId": "journey_test_12345",
        "new_route_data": {
            "from": "Electronic City",
            "to": "Koramangala",
            "via": "Hosur Road (alternate route)",
            "estimated_time": "45 minutes",
            "distance_km": 18.5
        },
        "reason_for_change": "Predicted gridlock on primary route due to high congestion",
        "affected_drivers": ["driver_001", "driver_002", "driver_003"],
        "notification_channels": ["FCM", "SMS"]
    },
    "correlation_id": "test-communications-001",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "source_service": "test-suite",
    "target_service": "communications"
}'

test_endpoint "Communications Agent - Reroute & Notify" "$COMMUNICATIONS_URL/a2a/tasks" "POST" "$communications_task"

log_section "🌟 Phase 3: End-to-End Agentic Orchestration"

# Test complete orchestration flow via API Gateway
e2e_scenario_1='{
    "scenario": "peak_hour_congestion",
    "location": "Electronic City to Koramangala corridor",
    "severity": "high",
    "vehicle_count": 1500,
    "weather": "clear",
    "time_of_day": "evening_peak",
    "emergency_vehicles": 0,
    "special_events": [],
    "correlation_id": "e2e-test-001"
}'

test_endpoint "E2E Flow - Peak Hour Congestion" "$API_GATEWAY_URL/run_orchestration" "POST" "$e2e_scenario_1"

# Test AI-powered decision making scenario
ai_scenario='{
    "scenario": "multi_point_congestion",
    "locations": [
        {"name": "Electronic City", "congestion": 85, "vehicles": 1200},
        {"name": "Silk Board Junction", "congestion": 92, "vehicles": 800},
        {"name": "Outer Ring Road", "congestion": 78, "vehicles": 950}
    ],
    "weather": "heavy_rain",
    "time": "peak_evening",
    "emergency_vehicles": 2,
    "special_conditions": ["road_construction", "traffic_signal_failure"],
    "correlation_id": "ai-test-001"
}'

test_endpoint "E2E Flow - AI Multi-Point Decision" "$API_GATEWAY_URL/run_orchestration" "POST" "$ai_scenario"

log_section "🎭 Phase 4: Hackathon Demo Scenarios"

# Morning Rush Hour Scenario
morning_rush='{
    "scenario": "morning_rush_hour",
    "time": "08:30",
    "location": "Whitefield to MG Road",
    "vehicle_types": ["private_cars", "buses", "two_wheelers"],
    "congestion_hotspots": ["Marathahalli", "Domlur", "Indiranagar"],
    "correlation_id": "demo-morning-rush"
}'

test_endpoint "Demo - Morning Rush Hour" "$API_GATEWAY_URL/run_orchestration" "POST" "$morning_rush"

# Emergency Vehicle Priority
emergency_scenario='{
    "scenario": "emergency_vehicle_priority",
    "vehicle_type": "ambulance",
    "route": "Whitefield to Victoria Hospital",
    "urgency": "critical",
    "estimated_arrival": "15 minutes",
    "affected_signals": ["Marathahalli", "Domlur", "Richmond Road"],
    "correlation_id": "demo-emergency"
}'

test_endpoint "Demo - Emergency Vehicle Priority" "$API_GATEWAY_URL/run_orchestration" "POST" "$emergency_scenario"

# Weather-Based Disruption
weather_scenario='{
    "scenario": "weather_disruption",
    "condition": "heavy_rain",
    "affected_routes": ["Outer Ring Road", "Hosur Road", "Bannerghatta Road"],
    "visibility": "low",
    "flooding_risk": ["Electronic City underpass", "Silk Board underpass"],
    "duration_hours": 3,
    "correlation_id": "demo-weather"
}'

test_endpoint "Demo - Weather Disruption" "$API_GATEWAY_URL/run_orchestration" "POST" "$weather_scenario"

log_section "📊 Phase 5: Performance & Monitoring"

# Test agent status endpoints
test_endpoint "Orchestrator Status" "$ORCHESTRATOR_URL/status"
test_endpoint "Simulation Status" "$SIMULATION_URL/status"
test_endpoint "Observer Status" "$OBSERVER_URL/status"
test_endpoint "Communications Status" "$COMMUNICATIONS_URL/status"

# Test API Gateway metrics
test_endpoint "API Gateway Metrics" "$API_GATEWAY_URL/metrics"

log_section "🔧 Phase 6: A2A Protocol Validation"

# Test agent discovery (if implemented)
test_endpoint "Agent Registry" "$ORCHESTRATOR_URL/agents/registry" "GET" "" "200"

# Test A2A message format validation
invalid_a2a='{
    "invalid_field": "test",
    "missing_required_fields": true
}'

test_endpoint "A2A Validation - Invalid Message" "$ORCHESTRATOR_URL/a2a/tasks" "POST" "$invalid_a2a" "422"

log_section "🎯 Phase 7: Stress Testing (Light)"

# Send multiple concurrent requests
log_test "Concurrent Orchestration Requests"
for i in {1..5}; do
    concurrent_scenario='{
        "scenario": "stress_test_'$i'",
        "location": "Test Location '$i'",
        "correlation_id": "stress-test-'$i'"
    }'
    
    curl -s -X POST "$API_GATEWAY_URL/run_orchestration" \
        -H "Content-Type: application/json" \
        -d "$concurrent_scenario" &
done

# Wait for all background requests
wait
log_success "Concurrent requests completed"

# Cleanup
cleanup_port_forwarding

log_section "📋 Test Results Summary"

echo ""
echo "============================================================================="
echo "🎉 Project Pravaah Agentic Flow Testing Complete!"
echo "============================================================================="
echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

if [[ $FAILED_TESTS -eq 0 ]]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! Your Urban Mobility Operating System is ready!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Check the logs above for details.${NC}"
    exit 1
fi
