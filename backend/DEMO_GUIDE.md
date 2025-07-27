# 🚗 Project Pravaah - Command Line Demo Guide

## 🎯 Overview
Project Pravaah is an **Urban Mobility Operating System** that prevents traffic congestion in Bengaluru using AI-powered multi-agent coordination.

## 🚀 Quick Start Demo

### 1. **Basic Setup (Google Cloud Shell)**
```bash
# Clone or navigate to project
cd project-pravaah/backend

# Make demo script executable
chmod +x demo_pravaah.sh

# Update service URLs in the script (replace with your actual Cloud Run URLs)
# Edit demo_pravaah.sh and update these variables:
# API_GATEWAY_URL="https://your-api-gateway-url"
# ORCHESTRATOR_URL="https://your-orchestrator-url"
# etc.
```

### 2. **Run Demo Scenarios**

#### 🔹 **Basic Demo** (Recommended for first-time)
```bash
./demo_pravaah.sh basic
```
**Shows:** Individual agent capabilities, health checks, A2A messaging

#### 🔹 **Traffic Jam Response**
```bash
./demo_pravaah.sh traffic_jam
```
**Shows:** End-to-end orchestration, real-time response to congestion

#### 🔹 **Emergency Response**
```bash
./demo_pravaah.sh emergency
```
**Shows:** Priority corridor creation, emergency vehicle routing

#### 🔹 **Full System Demo**
```bash
./demo_pravaah.sh full_demo
```
**Shows:** All capabilities in sequence (15-20 minutes)

#### 🔹 **Performance Testing**
```bash
./demo_pravaah.sh performance
```
**Shows:** System performance under concurrent load

## 🎬 Demo Flow Explanation

### **Multi-Agent Architecture**
```
🔍 Observer Agent    → Real-time traffic monitoring
🧠 Simulation Agent  → AI-powered congestion prediction  
🎯 Orchestrator Agent → Gemini-driven strategic decisions
📢 Communications Agent → Journey rerouting & notifications
```

### **Demo Scenarios Showcase**

#### **Scenario 1: Rush Hour Congestion**
1. **Observer** detects high traffic density on Hosur Road
2. **Simulation** predicts 40-minute delays at Electronic City
3. **Orchestrator** uses Gemini AI to select optimal intervention
4. **Communications** reroutes 50+ vehicles via Bannerghatta Road

#### **Scenario 2: Emergency Vehicle Priority**
1. **Observer** receives emergency vehicle alert
2. **Simulation** calculates fastest corridor to hospital
3. **Orchestrator** prioritizes emergency response protocol
4. **Communications** creates priority lane, notifies affected drivers

#### **Scenario 3: Proactive Congestion Prevention**
1. **Observer** monitors traffic patterns and "intent" signals
2. **Simulation** predicts congestion 30 minutes before it occurs
3. **Orchestrator** implements preventive rerouting strategy
4. **Communications** guides vehicles away from future choke points

## 🛠️ Manual Testing Commands

### **Health Checks**
```bash
# Test all services
curl https://api-gateway-url/health
curl https://orchestrator-url/health
curl https://observer-url/health
curl https://simulation-url/health
curl https://communications-url/health
```

### **Individual Agent Testing**
```bash
# Observer Agent - Traffic Monitoring
curl -X POST https://observer-url/process_task \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "TRAFFIC_MONITORING",
    "payload": {"location": "Electronic City", "radius_km": 5},
    "correlation_id": "test_001"
  }'

# Simulation Agent - Congestion Prediction
curl -X POST https://simulation-url/process_task \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "CONGESTION_ANALYSIS", 
    "payload": {"choke_points": ["Silk Board"], "time_horizon_minutes": 60},
    "correlation_id": "test_002"
  }'

# Orchestrator Agent - Strategic Planning
curl -X POST https://orchestrator-url/process_task \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "STRATEGIC_PLANNING",
    "payload": {"scenario": "peak_hour_congestion", "severity": "high"},
    "correlation_id": "test_003"
  }'

# Communications Agent - Journey Rerouting
curl -X POST https://communications-url/process_task \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "NOTIFICATION_DELIVERY",
    "payload": {"journey_id": "j001", "new_route": {"from": "EC", "to": "KR"}},
    "correlation_id": "test_004"
  }'
```

### **End-to-End Orchestration**
```bash
# Complete multi-agent pipeline via API Gateway
curl -X POST https://api-gateway-url/run_orchestration \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "traffic_congestion_detected",
    "location": "Electronic City Junction",
    "severity": "high",
    "affected_routes": ["Hosur Road", "Bannerghatta Road"]
  }'
```

## 📊 Expected Demo Outputs

### **Successful Health Check**
```
✅ API Gateway... Healthy
✅ Orchestrator... Healthy  
✅ Observer... Healthy
✅ Simulation... Healthy
✅ Communications... Healthy
```

### **Agent Response Example**
```json
{
  "status": "success",
  "task_id": "demo_observer_001",
  "result": {
    "traffic_density": "high",
    "congestion_score": 85,
    "affected_areas": ["Electronic City", "Silk Board"],
    "recommendations": ["reroute_via_bannerghatta"]
  },
  "processing_time_ms": 245,
  "correlation_id": "demo_001"
}
```

### **End-to-End Orchestration Response**
```json
{
  "orchestration_id": "orch_001",
  "status": "completed",
  "agents_involved": ["observer", "simulation", "orchestrator", "communications"],
  "decisions_made": {
    "strategy": "REROUTE_VEHICLES",
    "confidence": 0.92,
    "reasoning": "Gemini AI recommends immediate rerouting..."
  },
  "actions_taken": {
    "vehicles_rerouted": 47,
    "notifications_sent": 47,
    "estimated_time_saved": "15_minutes"
  }
}
```

## 🎯 Key Demo Highlights

### **🤖 AI-Powered Decision Making**
- **Gemini Integration**: Orchestrator uses Vertex AI for strategic planning
- **Context-Aware**: Considers Bengaluru-specific traffic patterns
- **Adaptive**: Learns from real-time conditions

### **🔄 Agent-to-Agent (A2A) Protocol**
- **Standardized Messaging**: All agents use consistent A2A format
- **Correlation Tracking**: End-to-end request tracing
- **Async Processing**: Non-blocking multi-agent coordination

### **📈 Scalable Architecture**
- **Cloud-Native**: Google Cloud Run auto-scaling
- **Microservices**: Independent agent deployment
- **Resilient**: Graceful failure handling

### **🎪 Hackathon-Friendly Features**
- **Visual Feedback**: Colorized console output
- **Interactive**: Step-by-step progression
- **Comprehensive**: Shows all system capabilities
- **Fast**: Quick demos for time-constrained presentations

## 🚨 Troubleshooting

### **Service URLs Not Set**
```bash
# Edit demo script and update URLs
nano demo_pravaah.sh
# Update API_GATEWAY_URL, ORCHESTRATOR_URL, etc.
```

### **Authentication Issues**
```bash
# Ensure you're authenticated to GCP
gcloud auth list
gcloud config set project stable-sign-454210-i0
```

### **Services Not Responding**
```bash
# Check Cloud Run services
gcloud run services list --region=asia-south1
```

### **Port Forwarding for Private Services**
```bash
# If services are private, use port forwarding
gcloud run services proxy orchestrator-service --port=8080 --region=asia-south1
```

## 🎉 Demo Success Criteria

✅ **All health checks pass**  
✅ **Individual agents respond correctly**  
✅ **End-to-end orchestration completes**  
✅ **Gemini AI provides strategic recommendations**  
✅ **A2A messaging works between all agents**  
✅ **Performance test handles concurrent requests**  

---

**🏆 Ready to showcase Project Pravaah's Urban Mobility Operating System!**
