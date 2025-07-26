#!/usr/bin/env python3
"""
Project Pravaah - Demo Main FastAPI Application
Urban Mobility Operating System - Smart Monolith for Testing

This is a simplified version of main.py that uses demo agents without Google Cloud dependencies
for local testing and validation.
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

# Import our demo agent classes (no GCP dependencies)
from demo_agents import (
    DemoObserverAgent,
    DemoSimulationAgent,
    DemoOrchestratorAgent,
    DemoCommunicationsAgent
)

# Configure logging for demo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [DEMO] %(message)s'
)
logger = logging.getLogger(__name__)

# Global agent instances (smart monolith pattern)
observer_agent: Optional[DemoObserverAgent] = None
simulation_agent: Optional[DemoSimulationAgent] = None
communications_agent: Optional[DemoCommunicationsAgent] = None
orchestrator_agent: Optional[DemoOrchestratorAgent] = None

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

# Application startup/shutdown lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    # Startup
    logger.info("🚀 Starting Project Pravaah Demo Backend API...")
    
    try:
        await initialize_demo_agents()
        logger.info("✅ All demo agents initialized successfully")
        yield
    except Exception as e:
        logger.error(f"❌ Failed to initialize demo agents: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down Project Pravaah Demo Backend API...")
        await cleanup_demo_agents()

# Create FastAPI app for demo
app = FastAPI(
    title="Project Pravaah Demo API",
    description="Urban Mobility Operating System - Multi-Agent Traffic Management (Demo Version)",
    version="1.0.0-demo",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Application startup time
app_start_time = datetime.now(timezone.utc)

async def initialize_demo_agents():
    """Initialize all demo agent instances."""
    global observer_agent, simulation_agent, communications_agent, orchestrator_agent
    
    try:
        logger.info("🔧 Initializing Project Pravaah demo agents...")
        
        # Initialize individual specialist agents (no GCP dependencies)
        logger.info("Initializing DemoObserverAgent...")
        observer_agent = DemoObserverAgent()
        
        logger.info("Initializing DemoSimulationAgent...")
        simulation_agent = DemoSimulationAgent()
        
        logger.info("Initializing DemoCommunicationsAgent...")
        communications_agent = DemoCommunicationsAgent()
        
        # Initialize orchestrator with dependency injection
        logger.info("Initializing DemoOrchestratorAgent with specialist agents...")
        orchestrator_agent = DemoOrchestratorAgent(
            observer_agent=observer_agent,
            simulation_agent=simulation_agent,
            communications_agent=communications_agent
        )
        
        logger.info("🎉 All Project Pravaah demo agents ready for operation!")
        
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
    """Cleanup demo agent resources."""
    global observer_agent, simulation_agent, communications_agent, orchestrator_agent
    
    try:
        logger.info("🧹 Cleaning up demo agent resources...")
        observer_agent = None
        simulation_agent = None
        communications_agent = None
        orchestrator_agent = None
        logger.info("✅ Demo agent cleanup completed")
        
    except Exception as e:
        logger.error(f"❌ Demo agent cleanup failed: {e}")

# Demo API Endpoints

@app.get("/")
async def root():
    """Root endpoint with demo API information."""
    return {
        "service": "Project Pravaah Demo API",
        "description": "Urban Mobility Operating System - Multi-Agent Traffic Management",
        "version": "1.0.0-demo",
        "status": "operational",
        "mode": "local_demo",
        "architecture": "smart_monolith",
        "docs": "/docs",
        "health": "/health",
        "demo_endpoint": "/run_orchestration"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for demo."""
    try:
        current_time = datetime.now(timezone.utc)
        uptime = (current_time - app_start_time).total_seconds()
        
        # Check agent statuses
        agent_statuses = {
            "orchestrator": "healthy" if orchestrator_agent else "not_initialized",
            "observer": "healthy" if observer_agent else "not_initialized",
            "simulation": "healthy" if simulation_agent else "not_initialized",
            "communications": "healthy" if communications_agent else "not_initialized"
        }
        
        overall_status = "healthy" if all(status == "healthy" for status in agent_statuses.values()) else "degraded"
        
        return {
            "status": overall_status,
            "timestamp": current_time.isoformat(),
            "agents": agent_statuses,
            "uptime_seconds": uptime,
            "demo_mode": True,
            "version": "1.0.0-demo"
        }
        
    except Exception as e:
        logger.error(f"Demo health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Demo health check failed: {str(e)}")

@app.post("/run_orchestration", response_model=DemoOrchestrationResponse)
async def run_orchestration(request: DemoOrchestrationRequest):
    """
    Main orchestration endpoint for demo - coordinates multi-agent traffic management.
    
    This is the core demo endpoint that accepts the current state of the world 
    and returns optimized routing decisions and interventions.
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
                "agents_involved": ["DemoObserverAgent", "DemoSimulationAgent", "DemoOrchestratorAgent", "DemoCommunicationsAgent"],
                "decision_process": "Simulated AI-powered strategic analysis",
                "traffic_analysis": decision_result.get("traffic_analysis", {}),
                "prediction_confidence": decision_result.get("confidence_score", 0.87),
                "intervention_reasoning": decision_result.get("reasoning", "Strategic decision based on simulated conditions"),
                "demo_scenario_handled": request.demo_scenario,
                "bengaluru_context": "Optimized for Bengaluru traffic patterns and choke points",
                "demo_mode": True
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
    """Get detailed status of all demo agents."""
    try:
        status_data = {}
        
        # Get orchestrator status
        if orchestrator_agent:
            orchestrator_status = orchestrator_agent.get_status()
            status_data["orchestrator"] = {
                **orchestrator_status,
                "demo_info": "Main coordination agent with simulated AI integration"
            }
        
        # Get other agent statuses
        agent_descriptions = {
            "observer": "Simulated real-time traffic perception and telemetry ingestion",
            "simulation": "Simulated congestion prediction and gridlock analysis",
            "communications": "Simulated journey rerouting and user notifications"
        }
        
        for agent_name, agent_instance in [
            ("observer", observer_agent),
            ("simulation", simulation_agent), 
            ("communications", communications_agent)
        ]:
            if agent_instance:
                status_data[agent_name] = {
                    "agent_id": agent_instance.agent_id,
                    "status": "healthy",
                    "agent_type": agent_name,
                    "demo_info": agent_descriptions[agent_name],
                    "metrics": getattr(agent_instance, 'metrics', {}),
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

@app.get("/demo/info")
async def get_demo_info():
    """Get demo-specific information and instructions."""
    return {
        "demo_name": "Project Pravaah - Urban Mobility Operating System",
        "demo_version": "1.0.0-demo",
        "architecture": "Smart Monolith with Multi-Agent System (Demo Version)",
        "agents": {
            "observer": "Simulates real-world traffic perception via demo data",
            "simulation": "Simulates predictive analysis to forecast gridlock",
            "orchestrator": "Simulates strategic decisions using demo AI logic",
            "communications": "Simulates intervention execution and user notifications"
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
            "demo_info": "GET /demo/info"
        },
        "demo_features": [
            "Simulated AI-powered strategic decision making",
            "Simulated real-time traffic perception and analysis",
            "Simulated predictive congestion modeling",
            "Simulated proactive route optimization",
            "Multi-agent coordination (demo version)"
        ],
        "note": "This is a demo version without Google Cloud dependencies for local testing",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Development server configuration for demo
if __name__ == "__main__":
    # Configure for demo
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info("=" * 80)
    logger.info("🚀 STARTING PROJECT PRAVAAH DEMO SERVER")
    logger.info(f"🌐 Server: {host}:{port}")
    logger.info("🎭 Mode: Local Demo (No GCP Dependencies)")
    logger.info("🤖 Architecture: Multi-Agent System (Demo Version)")
    logger.info("📚 Documentation: http://localhost:8080/docs")
    logger.info("🎯 Main Endpoint: POST /run_orchestration")
    logger.info("=" * 80)
    
    uvicorn.run(
        "main_demo:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
        access_log=True
    )
