#!/usr/bin/env python3
"""
Project Pravaah - Simulation Service Entry Point
===============================================
FastAPI service wrapper for ADK Simulation Agent
"""

import asyncio
import logging
import os
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import the ADK Simulation Agent
from adk_simulation_agent import ADKSimulationAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Project Pravaah - Simulation Service",
    description="ADK-enhanced Simulation Agent microservice",
    version="1.0.0"
)

# Global agent instance
simulation_agent = None

# Pydantic models
class A2ATaskRequest(BaseModel):
    task_id: str
    task_name: str
    params: Dict[str, Any]
    correlation_id: str
    timestamp: str
    source_service: str = "orchestrator"
    target_service: str = "simulation"
    priority: str = "normal"

@app.on_event("startup")
async def startup_event():
    """Initialize the simulation agent"""
    global simulation_agent
    try:
        logger.info("Initializing ADK Simulation Agent...")
        simulation_agent = ADKSimulationAgent()
        await simulation_agent.on_start()
        logger.info("Simulation Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Simulation Agent: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup the simulation agent"""
    global simulation_agent
    if simulation_agent:
        try:
            await simulation_agent.on_stop()
            logger.info("Simulation Agent stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping Simulation Agent: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "simulation-service",
        "agent_status": "active" if simulation_agent else "inactive"
    }

@app.post("/a2a/tasks")
async def handle_a2a_task(task: A2ATaskRequest):
    """Handle A2A task requests"""
    if not simulation_agent:
        raise HTTPException(status_code=503, detail="Simulation agent not initialized")
    
    try:
        logger.info(f"Processing A2A task: {task.task_id}")
        
        # Create proper A2A message for the agent
        from adk_base import A2AMessage, MessageType
        
        a2a_message = A2AMessage(
            message_id=task.task_id,
            sender=task.source_service,
            receiver="simulation",
            message_type=MessageType.REQUEST,
            action=task.task_name,
            payload=task.params,
            correlation_id=task.correlation_id,
            timestamp=task.timestamp
        )
        
        # Process the task using the simulation agent
        result = await simulation_agent.on_message(a2a_message)
        
        return {
            "success": True,
            "task_id": task.task_id,
            "correlation_id": task.correlation_id,
            "data": result,
            "timestamp": task.timestamp
        }
        
    except Exception as e:
        logger.error(f"Error processing A2A task {task.task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Task processing failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "simulation_service:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        reload=False,
        log_level="info"
    )
