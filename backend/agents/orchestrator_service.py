#!/usr/bin/env python3
"""
Project Pravaah - Orchestrator Service Entry Point
==================================================
FastAPI service wrapper for ADK Orchestrator Agent
"""

import asyncio
import logging
import os
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import the ADK Orchestrator Agent
from adk_orchestrator_agent import ADKOrchestratorAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Project Pravaah - Orchestrator Service",
    description="ADK-enhanced Orchestrator Agent microservice",
    version="1.0.0"
)

# Global agent instance
orchestrator_agent = None

# Pydantic models
class A2ATaskRequest(BaseModel):
    task_id: str
    task_name: str
    params: Dict[str, Any]
    correlation_id: str
    timestamp: str
    source_service: str = "api-gateway"
    target_service: str = "orchestrator"
    priority: str = "normal"

class A2ATaskResponse(BaseModel):
    success: bool
    task_id: str
    correlation_id: str
    data: Dict[str, Any]
    timestamp: str
    processing_time_ms: float

@app.on_event("startup")
async def startup_event():
    """Initialize the orchestrator agent"""
    global orchestrator_agent
    try:
        logger.info("Initializing ADK Orchestrator Agent...")
        orchestrator_agent = ADKOrchestratorAgent()
        await orchestrator_agent.on_start()
        logger.info("Orchestrator Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Orchestrator Agent: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup the orchestrator agent"""
    global orchestrator_agent
    if orchestrator_agent:
        try:
            await orchestrator_agent.on_stop()
            logger.info("Orchestrator Agent stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping Orchestrator Agent: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "orchestrator-service",
        "agent_status": "active" if orchestrator_agent else "inactive"
    }

@app.post("/a2a/tasks", response_model=A2ATaskResponse)
async def handle_a2a_task(task: A2ATaskRequest):
    """Handle A2A task requests"""
    if not orchestrator_agent:
        raise HTTPException(status_code=503, detail="Orchestrator agent not initialized")
    
    try:
        logger.info(f"Processing A2A task: {task.task_id}")
        
        # Create proper A2A message for the agent
        from adk_base import A2AMessage, MessageType
        
        a2a_message = A2AMessage(
            message_id=task.task_id,
            sender=task.source_service,
            receiver="orchestrator",
            message_type=MessageType.REQUEST,
            action=task.task_name,
            payload=task.params,
            correlation_id=task.correlation_id,
            timestamp=task.timestamp
        )
        
        # Process the task using the orchestrator agent
        result = await orchestrator_agent.on_message(a2a_message)
        
        return A2ATaskResponse(
            success=True,
            task_id=task.task_id,
            correlation_id=task.correlation_id,
            data=result,
            timestamp=task.timestamp,
            processing_time_ms=0.0  # TODO: Calculate actual processing time
        )
        
    except Exception as e:
        logger.error(f"Error processing A2A task {task.task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Task processing failed: {str(e)}")

if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "orchestrator_service:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        reload=False,
        log_level="info"
    )
