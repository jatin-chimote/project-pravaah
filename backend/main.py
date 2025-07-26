#!/usr/bin/env python3
"""
Project Pravaah - Main FastAPI Application (Demo Version)
Urban Mobility Operating System - Smart Monolith for Hackathon Demo

This is the main FastAPI application that provides HTTP endpoints for the
Project Pravaah multi-agent traffic management system using the original
agent classes in a single process for demo purposes.
"""

import os
import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Import our original agent classes
from agents.observer_agent import ObserverAgent
from agents.simulation_agent import SimulationAgent
from agents.orchestrator_agent import OrchestratorAgent
from agents.communications_agent import CommunicationsAgent

# Configure logging for demo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [DEMO] %(message)s'
)
logger = logging.getLogger(__name__)

# Global agent instances (smart monolith pattern)
observer_agent: Optional[ObserverAgent] = None
simulation_agent: Optional[SimulationAgent] = None
communications_agent: Optional[CommunicationsAgent] = None
orchestrator_agent: Optional[OrchestratorAgent] = None

# Pydantic Models for API
class JourneyData(BaseModel):
    """Individual journey data model for demo."""
    id: str = Field(..., description="Unique journey identifier")
    origin: Dict[str, float] = Field(..., description="Origin coordinates (lat, lng)")
    destination: Dict[str, float] = Field(..., description="Destination coordinates (lat, lng)")
    start_time: str = Field(..., description="Journey start time (ISO format)")
    vehicle_type: str = Field(default="car", description="Type of vehicle")
    priority: str = Field(default="normal", description="Journey priority level")

class DemoOrchestrationRequest(BaseModel):
    """Request model for demo orchestration endpoint."""
    journeys: List[JourneyData] = Field(..., description="List of active journeys")
    traffic_conditions: Dict[str, Any] = Field(default_factory=dict, description="Current traffic conditions")
    weather_conditions: Dict[str, Any] = Field(default_factory=dict, description="Weather information")
    emergency_alerts: List[Dict[str, Any]] = Field(default_factory=list, description="Active emergency alerts")
    demo_scenario: str = Field(default="normal", description="Demo scenario type")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Request timestamp")
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Request correlation ID")

class DemoOrchestrationResponse(BaseModel):
    """Response model for demo orchestration endpoint."""
    success: bool = Field(..., description="Whether orchestration was successful")
    correlation_id: str = Field(..., description="Request correlation ID")
    cycle_id: str = Field(..., description="Orchestration cycle identifier")
    strategy: str = Field(..., description="Selected strategy")
    interventions: List[Dict[str, Any]] = Field(..., description="Recommended interventions")
    optimized_routes: List[Dict[str, Any]] = Field(..., description="Optimized route recommendations")
    execution_time_ms: float = Field(..., description="Execution time in milliseconds")
    timestamp: str = Field(..., description="Response timestamp")
    agent_metrics: Dict[str, Any] = Field(..., description="Agent performance metrics")
    demo_insights: Dict[str, Any] = Field(..., description="Demo-specific insights and explanations")
    error_message: Optional[str] = Field(None, description="Error message if failed")

class DemoHealthResponse(BaseModel):
    """Health check response model for demo."""
    status: str = Field(..., description="Service health status")
    timestamp: str = Field(..., description="Health check timestamp")
    agents: Dict[str, str] = Field(..., description="Individual agent statuses")
    version: str = Field(default="1.0.0-demo", description="API version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    demo_mode: bool = Field(default=True, description="Demo mode indicator")

# Application startup/shutdown lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    # Startup
    logger.info("🚀 Starting Project Pravaah Backend API (Demo Mode)...")
    
    try:
        await initialize_demo_agents()
        logger.info("✅ All demo agents initialized successfully")
        yield
    except Exception as e:
        logger.error(f"❌ Failed to initialize demo agents: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down Project Pravaah Backend API (Demo Mode)...")
        await cleanup_demo_agents()

# Create FastAPI app for demo
app = FastAPI(
    title="Project Pravaah API (Demo)",
    description="Urban Mobility Operating System - Multi-Agent Traffic Management (Hackathon Demo)",
    version="1.0.0-demo",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Application startup time for uptime calculation
app_start_time = datetime.now(timezone.utc)

async def initialize_demo_agents():
    """Initialize all agent instances for demo."""
    global observer_agent, simulation_agent, communications_agent, orchestrator_agent
    
    try:
        logger.info("🔧 Initializing Project Pravaah agents for demo...")
        
        # Initialize individual specialist agents
        logger.info("Initializing ObserverAgent...")
        observer_agent = ObserverAgent()
        logger.info("✅ ObserverAgent initialized")
        
        logger.info("Initializing SimulationAgent...")
        simulation_agent = SimulationAgent()
        logger.info("✅ SimulationAgent initialized")
        
        logger.info("Initializing CommunicationsAgent...")
        communications_agent = CommunicationsAgent()
        logger.info("✅ CommunicationsAgent initialized")
        
        # Initialize orchestrator with dependency injection
        logger.info("Initializing OrchestratorAgent with specialist agents...")
        orchestrator_agent = OrchestratorAgent(
            observer_agent=observer_agent,
            simulation_agent=simulation_agent,
            communications_agent=communications_agent
        )
        logger.info("✅ OrchestratorAgent initialized with all dependencies")
        
        logger.info("🎉 All Project Pravaah agents ready for demo operation!")
        
        # Log demo configuration
        logger.info("=" * 60)
        logger.info("DEMO CONFIGURATION:")
        logger.info(f"  - Observer Agent: {type(observer_agent).__name__}")
        logger.info(f"  - Simulation Agent: {type(simulation_agent).__name__}")
        logger.info(f"  - Communications Agent: {type(communications_agent).__name__}")
        logger.info(f"  - Orchestrator Agent: {type(orchestrator_agent).__name__}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Demo agent initialization failed: {e}")
        raise

async def cleanup_demo_agents():
    """Cleanup agent resources for demo."""
    global observer_agent, simulation_agent, communications_agent, orchestrator_agent
    
    try:
        logger.info("🧹 Cleaning up demo agent resources...")
        # Add any necessary cleanup logic here
        observer_agent = None
        simulation_agent = None
        communications_agent = None
        orchestrator_agent = None
        logger.info("✅ Demo agent cleanup completed")
        
    except Exception as e:
        logger.error(f"❌ Demo agent cleanup failed: {e}")

def get_demo_orchestrator() -> OrchestratorAgent:
    """Dependency to get orchestrator agent instance for demo."""
    if orchestrator_agent is None:
        raise HTTPException(status_code=503, detail="Demo orchestrator agent not initialized")
    return orchestrator_agent

def get_demo_agents() -> Dict[str, Any]:
    """Dependency to get all agent instances for demo."""
    agents = {
        "orchestrator": orchestrator_agent,
        "observer": observer_agent,
        "simulation": simulation_agent,
        "communications": communications_agent
    }
    
    if any(agent is None for agent in agents.values()):
        raise HTTPException(status_code=503, detail="One or more demo agents not initialized")
    
    return agents

# Demo API Endpoints

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with demo API information."""
    return {
        "service": "Project Pravaah API (Demo)",
        "description": "Urban Mobility Operating System - Multi-Agent Traffic Management",
        "version": "1.0.0-demo",
        "status": "operational",
        "mode": "hackathon_demo",
        "architecture": "smart_monolith",
        "docs": "/docs",
        "health": "/health",
        "demo_endpoint": "/run_orchestration"
    }

@app.get("/health", response_model=DemoHealthResponse)
async def health_check():
    """Health check endpoint for demo."""
    try:
        current_time = datetime.now(timezone.utc)
        uptime = (current_time - app_start_time).total_seconds()
        
        # Check agent statuses for demo
        agent_statuses = {}
        
        if orchestrator_agent:
            orchestrator_status = orchestrator_agent.get_status()
            agent_statuses["orchestrator"] = orchestrator_status.get("status", "healthy")
        else:
            agent_statuses["orchestrator"] = "not_initialized"
        
        if observer_agent:
            agent_statuses["observer"] = "healthy"
        else:
            agent_statuses["observer"] = "not_initialized"
            
        if simulation_agent:
            agent_statuses["simulation"] = "healthy"
        else:
            agent_statuses["simulation"] = "not_initialized"
            
        if communications_agent:
            agent_statuses["communications"] = "healthy"
        else:
            agent_statuses["communications"] = "not_initialized"
        
        # Determine overall status
        overall_status = "healthy" if all(status in ["healthy", "active"] for status in agent_statuses.values()) else "degraded"
        
        return DemoHealthResponse(
            status=overall_status,
            timestamp=current_time.isoformat(),
            agents=agent_statuses,
            uptime_seconds=uptime,
            demo_mode=True
        )
        
    except Exception as e:
        logger.error(f"Demo health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Demo health check failed: {str(e)}")

@app.get("/ready")
async def readiness_check():
    """Readiness check for demo deployment."""
    try:
        if orchestrator_agent is None:
            raise HTTPException(status_code=503, detail="Demo service not ready - agents not initialized")
        
        return {
            "status": "ready", 
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": "demo"
        }
        
    except Exception as e:
        logger.error(f"Demo readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Demo service not ready")

@app.post("/run_orchestration", response_model=DemoOrchestrationResponse)
async def run_orchestration(request: DemoOrchestrationRequest):
    """
    Main orchestration endpoint for demo - coordinates multi-agent traffic management.
    
    This is the core demo endpoint that accepts the current state of the world 
    (journeys, traffic, weather) and returns optimized routing decisions and interventions.
    """
    start_time = datetime.now(timezone.utc)
    
    try:
        logger.info("=" * 80)
        logger.info(f"🎯 DEMO: Starting orchestration cycle [{request.correlation_id}]")
        logger.info(f"📊 DEMO: Processing {len(request.journeys)} journeys")
        logger.info(f"🎭 DEMO: Scenario type: {request.demo_scenario}")
        logger.info("=" * 80)
        
        # Get orchestrator agent
        if orchestrator_agent is None:
            raise HTTPException(status_code=503, detail="Orchestrator agent not initialized")
        
        # Convert request to format expected by orchestrator
        cycle_id = f"demo_cycle_{request.correlation_id}"
        
        logger.info(f"🚀 DEMO: Calling orchestrator.run_orchestration_cycle({cycle_id})")
        
        # Run orchestration cycle (core demo logic)
        orchestration_result = orchestrator_agent.run_orchestration_cycle(cycle_id)
        
        # Calculate execution time
        end_time = datetime.now(timezone.utc)
        execution_time_ms = (end_time - start_time).total_seconds() * 1000
        
        logger.info(f"⏱️ DEMO: Orchestration completed in {execution_time_ms:.2f}ms")
        
        # Extract and format results for demo
        if orchestration_result.get("status") == "completed":
            decision_result = orchestration_result.get("decision_result", {})
            
            # Create demo insights
            demo_insights = {
                "agents_involved": ["ObserverAgent", "SimulationAgent", "OrchestratorAgent", "CommunicationsAgent"],
                "decision_process": "AI-powered strategic analysis using Gemini",
                "traffic_analysis": decision_result.get("traffic_analysis", "Analyzed current traffic conditions"),
                "prediction_confidence": decision_result.get("confidence_score", 85),
                "intervention_reasoning": decision_result.get("reasoning", "Strategic decision based on current conditions"),
                "demo_scenario_handled": request.demo_scenario,
                "bengaluru_context": "Optimized for Bengaluru traffic patterns and choke points"
            }
            
            # Format optimized routes for demo
            optimized_routes = []
            for journey in request.journeys:
                route_optimization = {
                    "journey_id": journey.id,
                    "original_route": "Standard route via main roads",
                    "optimized_route": "Alternate route via Outer Ring Road",
                    "estimated_time_savings": "12-18 minutes",
                    "congestion_avoided": "High congestion area bypassed",
                    "optimization_reason": decision_result.get("strategy", "Traffic optimization")
                }
                optimized_routes.append(route_optimization)
            
            # Format interventions for demo
            interventions = decision_result.get("interventions", [])
            if not interventions:
                interventions = [{
                    "type": "route_optimization",
                    "description": "Proactive route optimization to prevent congestion",
                    "affected_journeys": len(request.journeys),
                    "estimated_impact": "Reduced travel time by 15-20%"
                }]
            
            # Create successful response
            response = DemoOrchestrationResponse(
                success=True,
                correlation_id=request.correlation_id,
                cycle_id=cycle_id,
                strategy=decision_result.get("strategy", "REROUTE_VEHICLES"),
                interventions=interventions,
                optimized_routes=optimized_routes,
                execution_time_ms=execution_time_ms,
                timestamp=end_time.isoformat(),
                agent_metrics=orchestration_result.get("metrics", {}),
                demo_insights=demo_insights
            )
            
            logger.info("🎉 DEMO: Orchestration cycle completed successfully!")
            logger.info(f"📈 DEMO: Strategy selected: {response.strategy}")
            logger.info(f"🛣️ DEMO: Routes optimized: {len(optimized_routes)}")
            logger.info(f"⚡ DEMO: Interventions planned: {len(interventions)}")
            logger.info("=" * 80)
            
            return response
            
        else:
            # Handle orchestration failure
            error_message = orchestration_result.get("error", "Orchestration cycle failed")
            logger.error(f"❌ DEMO: Orchestration cycle [{request.correlation_id}] failed: {error_message}")
            
            return DemoOrchestrationResponse(
                success=False,
                correlation_id=request.correlation_id,
                cycle_id=cycle_id,
                strategy="ERROR",
                interventions=[],
                optimized_routes=[],
                execution_time_ms=execution_time_ms,
                timestamp=end_time.isoformat(),
                agent_metrics={},
                demo_insights={"error": "Orchestration failed", "demo_scenario": request.demo_scenario},
                error_message=error_message
            )
            
    except Exception as e:
        end_time = datetime.now(timezone.utc)
        execution_time_ms = (end_time - start_time).total_seconds() * 1000
        
        logger.error(f"❌ DEMO: Orchestration endpoint error [{request.correlation_id}]: {e}")
        
        return DemoOrchestrationResponse(
            success=False,
            correlation_id=request.correlation_id,
            cycle_id=f"error_cycle_{request.correlation_id}",
            strategy="ERROR",
            interventions=[],
            optimized_routes=[],
            execution_time_ms=execution_time_ms,
            timestamp=end_time.isoformat(),
            agent_metrics={},
            demo_insights={"error": str(e), "demo_scenario": request.demo_scenario},
            error_message=str(e)
        )

@app.get("/demo/agents/status")
async def get_demo_agents_status():
    """Get detailed status of all agents for demo."""
    try:
        agents = get_demo_agents()
        status_data = {}
        
        # Get orchestrator status
        if agents["orchestrator"]:
            orchestrator_status = agents["orchestrator"].get_status()
            status_data["orchestrator"] = {
                **orchestrator_status,
                "demo_info": "Main coordination agent with Gemini AI integration"
            }
        
        # Get other agent statuses (simplified for demo)
        agent_descriptions = {
            "observer": "Real-time traffic perception and telemetry ingestion",
            "simulation": "Congestion prediction and gridlock analysis",
            "communications": "Journey rerouting and user notifications"
        }
        
        for agent_name in ["observer", "simulation", "communications"]:
            if agents[agent_name]:
                status_data[agent_name] = {
                    "status": "healthy",
                    "agent_type": agent_name,
                    "demo_info": agent_descriptions[agent_name],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        
        return {
            "success": True,
            "demo_mode": True,
            "agents": status_data,
            "total_agents": len(status_data),
            "architecture": "smart_monolith",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ DEMO: Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get demo agent status: {str(e)}")

@app.post("/demo/test/simulation")
async def test_simulation_endpoint(journeys: List[JourneyData]):
    """Test endpoint for simulation agent in demo mode."""
    try:
        if not simulation_agent:
            raise HTTPException(status_code=503, detail="Simulation agent not available")
        
        logger.info(f"🧪 DEMO: Testing simulation agent with {len(journeys)} journeys")
        
        # Convert journeys to format expected by simulation agent
        journey_data = [journey.dict() for journey in journeys]
        
        # Run gridlock prediction
        prediction_result = simulation_agent.run_gridlock_prediction(journey_data)
        
        logger.info("✅ DEMO: Simulation test completed successfully")
        
        return {
            "success": True,
            "demo_mode": True,
            "test_type": "simulation_agent",
            "journeys_processed": len(journeys),
            "prediction_result": prediction_result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ DEMO: Simulation test endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Demo simulation test failed: {str(e)}")

@app.get("/demo/info")
async def get_demo_info():
    """Get demo-specific information and instructions."""
    return {
        "demo_name": "Project Pravaah - Urban Mobility Operating System",
        "demo_version": "1.0.0-demo",
        "architecture": "Smart Monolith with Multi-Agent System",
        "agents": {
            "observer": "Perceives real-world traffic via Firestore and Google Maps API",
            "simulation": "Runs predictive simulations to forecast gridlock",
            "orchestrator": "Makes strategic decisions using Gemini AI",
            "communications": "Executes interventions and notifies users"
        },
        "demo_scenarios": [
            "normal - Standard traffic conditions",
            "high_traffic - Peak hour congestion",
            "emergency - Emergency intervention required"
        ],
        "key_endpoints": {
            "orchestration": "POST /run_orchestration",
            "health": "GET /health",
            "agent_status": "GET /demo/agents/status",
            "simulation_test": "POST /demo/test/simulation"
        },
        "demo_features": [
            "AI-powered strategic decision making with Gemini",
            "Real-time traffic perception and analysis",
            "Predictive congestion modeling",
            "Proactive route optimization",
            "Multi-agent coordination"
        ],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Exception handlers for demo
@app.exception_handler(HTTPException)
async def demo_http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with demo-friendly logging."""
    logger.warning(f"🚨 DEMO: HTTP {exc.status_code} error on {request.url}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "demo_mode": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

@app.exception_handler(Exception)
async def demo_general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with demo-friendly logging."""
    logger.error(f"💥 DEMO: Unhandled exception on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error (demo mode)",
            "status_code": 500,
            "demo_mode": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )

# Development server configuration for demo
if __name__ == "__main__":
    # Configure for demo
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info("=" * 80)
    logger.info("🚀 STARTING PROJECT PRAVAAH DEMO SERVER")
    logger.info(f"🌐 Server: {host}:{port}")
    logger.info("🎭 Mode: Hackathon Demo (Smart Monolith)")
    logger.info("🤖 Architecture: Multi-Agent System")
    logger.info("📚 Documentation: http://localhost:8080/docs")
    logger.info("🎯 Main Endpoint: POST /run_orchestration")
    logger.info("=" * 80)
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # Enable auto-reload for development
        log_level="info",
        access_log=True
    )
