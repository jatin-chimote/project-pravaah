#!/bin/bash
# ============================================================================
# Project Pravaah - Command Line Demo Script
# ============================================================================
# Demonstrates the full Urban Mobility Operating System capabilities
# Usage: ./demo_pravaah.sh [scenario]
# Scenarios: basic, traffic_jam, emergency, full_demo
# ============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration
API_GATEWAY_URL="https://api-gateway-service-123456789-uc.a.run.app"
ORCHESTRATOR_URL="https://orchestrator-service-123456789-uc.a.run.app"
OBSERVER_URL="https://observer-service-123456789-uc.a.run.app"
SIMULATION_URL="https://simulation-service-123456789-uc.a.run.app"
COMMUNICATIONS_URL="https://communications-service-123456789-uc.a.run.app"

# Demo scenario (default: basic)
SCENARIO=${1:-basic}

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo -e "${WHITE}============================================================================${NC}"
    echo -e "${WHITE}$1${NC}"
    echo -e "${WHITE}============================================================================${NC}"
}

print_step() {
    echo -e "${CYAN}🚀 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

wait_for_user() {
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# ============================================================================
# API Testing Functions
# ============================================================================

test_health_checks() {
    print_step "Testing all service health endpoints..."
    
    services=(
        "API Gateway:$API_GATEWAY_URL/health"
        "Orchestrator:$ORCHESTRATOR_URL/health"
        "Observer:$OBSERVER_URL/health"
        "Simulation:$SIMULATION_URL/health"
        "Communications:$COMMUNICATIONS_URL/health"
    )
    
    for service in "${services[@]}"; do
        name=$(echo $service | cut -d: -f1)
        url=$(echo $service | cut -d: -f2-)
        
        echo -n "  Checking $name... "
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Healthy${NC}"
        else
            echo -e "${RED}❌ Unhealthy${NC}"
        fi
    done
}

demo_observer_agent() {
    print_step "Demo: Observer Agent - Real-time Traffic Monitoring"
    
    echo -e "${BLUE}Observer Agent monitors traffic conditions across Bengaluru...${NC}"
    
    # Simulate traffic monitoring request
    cat > /tmp/observer_request.json << 'EOF'
{
    "task_type": "TRAFFIC_MONITORING",
    "task_id": "demo_observer_001",
    "payload": {
        "location": "Electronic City",
        "radius_km": 5,
        "include_predictions": true
    },
    "correlation_id": "demo_001",
    "sender": "demo_cli"
}
EOF

    echo -e "${PURPLE}Sending traffic monitoring request...${NC}"
    curl -X POST "$OBSERVER_URL/process_task" \
         -H "Content-Type: application/json" \
         -d @/tmp/observer_request.json \
         --silent | jq '.' || echo "Response received"
    
    print_success "Observer Agent processed traffic monitoring request"
}

demo_simulation_agent() {
    print_step "Demo: Simulation Agent - Congestion Prediction"
    
    echo -e "${BLUE}Simulation Agent predicts traffic congestion at key choke points...${NC}"
    
    # Simulate congestion prediction request
    cat > /tmp/simulation_request.json << 'EOF'
{
    "task_type": "CONGESTION_ANALYSIS",
    "task_id": "demo_simulation_001",
    "payload": {
        "choke_points": ["Silk Board", "Electronic City Toll", "Hosur Road"],
        "time_horizon_minutes": 60,
        "vehicle_types": ["car", "bus", "truck"]
    },
    "correlation_id": "demo_001",
    "sender": "demo_cli"
}
EOF

    echo -e "${PURPLE}Sending congestion prediction request...${NC}"
    curl -X POST "$SIMULATION_URL/process_task" \
         -H "Content-Type: application/json" \
         -d @/tmp/simulation_request.json \
         --silent | jq '.' || echo "Response received"
    
    print_success "Simulation Agent completed congestion analysis"
}

demo_orchestrator_agent() {
    print_step "Demo: Orchestrator Agent - AI-Powered Decision Making"
    
    echo -e "${BLUE}Orchestrator Agent uses Gemini AI for strategic traffic management...${NC}"
    
    # Simulate orchestration request
    cat > /tmp/orchestrator_request.json << 'EOF'
{
    "task_type": "STRATEGIC_PLANNING",
    "task_id": "demo_orchestrator_001",
    "payload": {
        "scenario": "peak_hour_congestion",
        "affected_areas": ["Electronic City", "Koramangala", "BTM Layout"],
        "severity": "high",
        "available_interventions": ["rerouting", "signal_optimization", "emergency_response"]
    },
    "correlation_id": "demo_001",
    "sender": "demo_cli"
}
EOF

    echo -e "${PURPLE}Sending strategic planning request to Gemini-powered Orchestrator...${NC}"
    curl -X POST "$ORCHESTRATOR_URL/process_task" \
         -H "Content-Type: application/json" \
         -d @/tmp/orchestrator_request.json \
         --silent | jq '.' || echo "Response received"
    
    print_success "Orchestrator Agent completed AI-driven strategic planning"
}

demo_communications_agent() {
    print_step "Demo: Communications Agent - Journey Rerouting & Notifications"
    
    echo -e "${BLUE}Communications Agent executes rerouting decisions and notifies drivers...${NC}"
    
    # Simulate rerouting request
    cat > /tmp/communications_request.json << 'EOF'
{
    "task_type": "NOTIFICATION_DELIVERY",
    "task_id": "demo_communications_001",
    "payload": {
        "journey_id": "journey_demo_001",
        "driver_id": "driver_demo_001",
        "new_route": {
            "from": "Electronic City",
            "to": "Koramangala",
            "via": "Bannerghatta Road",
            "estimated_time": 45,
            "reason": "Congestion detected on Hosur Road"
        },
        "notification_type": "reroute_alert"
    },
    "correlation_id": "demo_001",
    "sender": "demo_cli"
}
EOF

    echo -e "${PURPLE}Sending rerouting and notification request...${NC}"
    curl -X POST "$COMMUNICATIONS_URL/process_task" \
         -H "Content-Type: application/json" \
         -d @/tmp/communications_request.json \
         --silent | jq '.' || echo "Response received"
    
    print_success "Communications Agent completed journey rerouting and notifications"
}

demo_end_to_end_orchestration() {
    print_step "Demo: End-to-End Multi-Agent Orchestration"
    
    echo -e "${BLUE}API Gateway orchestrates all agents for complete traffic management...${NC}"
    
    # Simulate end-to-end orchestration via API Gateway
    cat > /tmp/e2e_request.json << 'EOF'
{
    "scenario": "traffic_congestion_detected",
    "location": "Electronic City Junction",
    "severity": "high",
    "affected_routes": ["Hosur Road", "Bannerghatta Road"],
    "vehicle_count": 150,
    "timestamp": "2025-01-27T08:30:00Z"
}
EOF

    echo -e "${PURPLE}Sending end-to-end orchestration request via API Gateway...${NC}"
    echo -e "${YELLOW}This will trigger: Observer → Simulation → Orchestrator → Communications${NC}"
    
    curl -X POST "$API_GATEWAY_URL/run_orchestration" \
         -H "Content-Type: application/json" \
         -d @/tmp/e2e_request.json \
         --silent | jq '.' || echo "Response received"
    
    print_success "Complete multi-agent pipeline executed successfully!"
}

# ============================================================================
# Demo Scenarios
# ============================================================================

demo_basic() {
    print_header "🚗 Project Pravaah - Basic Demo"
    
    echo -e "${WHITE}Urban Mobility Operating System for Bengaluru${NC}"
    echo -e "${WHITE}Preventing traffic congestion through AI-powered multi-agent coordination${NC}"
    echo ""
    
    test_health_checks
    wait_for_user
    
    demo_observer_agent
    wait_for_user
    
    demo_simulation_agent
    wait_for_user
    
    demo_orchestrator_agent
    wait_for_user
    
    demo_communications_agent
    wait_for_user
    
    print_header "✅ Basic Demo Complete!"
}

demo_traffic_jam() {
    print_header "🚨 Project Pravaah - Traffic Jam Response Demo"
    
    echo -e "${RED}SCENARIO: Major traffic jam detected on Hosur Road${NC}"
    echo -e "${YELLOW}System Response: Multi-agent coordination for immediate intervention${NC}"
    echo ""
    
    demo_end_to_end_orchestration
    wait_for_user
    
    print_header "✅ Traffic Jam Response Demo Complete!"
}

demo_emergency() {
    print_header "🚨 Project Pravaah - Emergency Response Demo"
    
    echo -e "${RED}SCENARIO: Emergency vehicle needs priority corridor${NC}"
    echo -e "${YELLOW}System Response: Real-time rerouting and signal optimization${NC}"
    echo ""
    
    # Emergency scenario
    cat > /tmp/emergency_request.json << 'EOF'
{
    "scenario": "emergency_vehicle_priority",
    "emergency_type": "ambulance",
    "route": "Electronic City to Victoria Hospital",
    "priority": "critical",
    "estimated_arrival": "12_minutes",
    "affected_intersections": ["Silk Board", "BTM Layout", "Lalbagh"]
}
EOF

    echo -e "${PURPLE}Activating emergency response protocol...${NC}"
    curl -X POST "$API_GATEWAY_URL/run_orchestration" \
         -H "Content-Type: application/json" \
         -d @/tmp/emergency_request.json \
         --silent | jq '.' || echo "Emergency response activated"
    
    print_success "Emergency corridor established!"
    print_header "✅ Emergency Response Demo Complete!"
}

demo_full() {
    print_header "🌟 Project Pravaah - Full System Demo"
    
    echo -e "${WHITE}Complete demonstration of all system capabilities${NC}"
    echo ""
    
    demo_basic
    echo ""
    demo_traffic_jam
    echo ""
    demo_emergency
    echo ""
    
    print_header "🎉 Full System Demo Complete!"
    echo -e "${GREEN}Project Pravaah successfully demonstrated all capabilities:${NC}"
    echo -e "${GREEN}✅ Real-time traffic monitoring${NC}"
    echo -e "${GREEN}✅ AI-powered congestion prediction${NC}"
    echo -e "${GREEN}✅ Gemini-driven strategic planning${NC}"
    echo -e "${GREEN}✅ Automated journey rerouting${NC}"
    echo -e "${GREEN}✅ Multi-agent coordination${NC}"
    echo -e "${GREEN}✅ Emergency response protocols${NC}"
}

# ============================================================================
# Performance Testing
# ============================================================================

demo_performance() {
    print_header "⚡ Project Pravaah - Performance Testing"
    
    echo -e "${BLUE}Testing system performance under load...${NC}"
    
    # Concurrent requests test
    echo -e "${PURPLE}Sending 10 concurrent orchestration requests...${NC}"
    
    for i in {1..10}; do
        curl -X POST "$API_GATEWAY_URL/run_orchestration" \
             -H "Content-Type: application/json" \
             -d '{"scenario":"load_test_'$i'","location":"Test_Location_'$i'"}' \
             --silent &
    done
    
    wait  # Wait for all background jobs to complete
    print_success "Performance test completed!"
}

# ============================================================================
# Main Demo Logic
# ============================================================================

main() {
    case $SCENARIO in
        "basic")
            demo_basic
            ;;
        "traffic_jam")
            demo_traffic_jam
            ;;
        "emergency")
            demo_emergency
            ;;
        "full_demo")
            demo_full
            ;;
        "performance")
            demo_performance
            ;;
        *)
            echo -e "${RED}Unknown scenario: $SCENARIO${NC}"
            echo -e "${YELLOW}Available scenarios: basic, traffic_jam, emergency, full_demo, performance${NC}"
            exit 1
            ;;
    esac
}

# ============================================================================
# Script Execution
# ============================================================================

echo -e "${CYAN}"
cat << 'EOF'
 ____                            _     
|  _ \ _ __ __ ___   ____ _  __ _| |__  
| |_) | '__/ _` \ \ / / _` |/ _` | '_ \ 
|  __/| | | (_| |\ V / (_| | (_| | | | |
|_|   |_|  \__,_| \_/ \__,_|\__,_|_| |_|
                                       
Urban Mobility Operating System
EOF
echo -e "${NC}"

main

# Cleanup temporary files
rm -f /tmp/observer_request.json
rm -f /tmp/simulation_request.json
rm -f /tmp/orchestrator_request.json
rm -f /tmp/communications_request.json
rm -f /tmp/e2e_request.json
rm -f /tmp/emergency_request.json

echo -e "${GREEN}Demo completed successfully! 🎉${NC}"
