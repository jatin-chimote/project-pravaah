#!/usr/bin/env python3
"""
Project Pravaah - Communications Service Entry Point
===================================================
FastAPI service wrapper for ADK Communications Agent
"""

import asyncio
import logging
import os
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import the ADK Communications Agent
from adk_communications_agent import ADKCommunicationsAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Project Pravaah - Communications Service",
    description="ADK-enhanced Communications Agent microservice",
    version="1.0.0"
)

# Global agent instance
communications_agent = None

# Pydantic models
class A2ATaskRequest(BaseModel):
    task_id: str
    task_name: str
    params: Dict[str, Any]
    correlation_id: str
    timestamp: str
    source_service: str = "orchestrator"
    target_service: str = "communications"
    priority: str = "normal"

@app.on_event("startup")
async def startup_event():
    """Initialize the communications agent"""
    global communications_agent
    try:
        logger.info("Initializing ADK Communications Agent...")
        communications_agent = ADKCommunicationsAgent()
        await communications_agent.on_start()
        logger.info("Communications Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Communications Agent: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup the communications agent"""
    global communications_agent
    if communications_agent:
        try:
            await communications_agent.on_stop()
            logger.info("Communications Agent stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping Communications Agent: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "communications-service",
        "agent_status": "active" if communications_agent else "inactive"
    }

@app.post("/a2a/tasks")
async def handle_a2a_task(task: A2ATaskRequest):
    """Handle A2A task requests"""
    if not communications_agent:
        raise HTTPException(status_code=503, detail="Communications agent not initialized")
    
    try:
        logger.info(f"Processing A2A task: {task.task_id}")
        
        # Create proper A2A message for the agent
        from adk_base import A2AMessage, MessageType
        
        a2a_message = A2AMessage(
            message_id=task.task_id,
            sender=task.source_service,
            receiver="communications",
            message_type=MessageType.REQUEST,
            action=task.task_name,
            payload=task.params,
            correlation_id=task.correlation_id,
            timestamp=task.timestamp
        )
        
        # Process the task using the communications agent
        result = await communications_agent.on_message(a2a_message)
        
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
        "communications_service:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        reload=False,
        log_level="info"
    )
