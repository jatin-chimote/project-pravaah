"""
Project Pravaah - Agentic API Gateway Service
==============================================

Public-facing HTTP-to-A2A Protocol Translation Gateway
Securely bridges Angular frontend with internal agentic microservices

Author: Project Pravaah Team
GCP Project: stable-sign-454210-i0
"""

import asyncio
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
import structlog
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# =============================================================================
# Configuration
# =============================================================================

class GatewayConfig:
    """API Gateway configuration settings"""
    
    # Service configuration
    SERVICE_NAME = "pravaah-api-gateway"
    VERSION = "1.0.0"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # Internal service URLs (Cloud Run services)
    ORCHESTRATOR_SERVICE_URL = os.getenv(
        "ORCHESTRATOR_SERVICE_URL", 
        "http://localhost:8081"  # Local development fallback
    )
    
    # Timeouts and limits
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "300"))  # 5 minutes
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    
    # Security
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:4200").split(",")
    
    # GCP Project
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "stable-sign-454210-i0")

config = GatewayConfig()

# =============================================================================
# Pydantic Models
# =============================================================================

class JourneyRequest(BaseModel):
    """Individual journey request model"""
    id: str = Field(..., description="Unique journey identifier")
    origin: Dict[str, float] = Field(..., description="Origin coordinates {lat, lng}")
    destination: Dict[str, float] = Field(..., description="Destination coordinates {lat, lng}")
    start_time: str = Field(..., description="Journey start time (ISO format)")
    vehicle_type: str = Field(default="car", description="Vehicle type")
    priority: str = Field(default="normal", description="Journey priority")

class TrafficConditions(BaseModel):
    """Traffic conditions model"""
    peak_hour: bool = Field(default=False, description="Is it peak hour?")
    weather: str = Field(default="clear", description="Weather conditions")
    incidents: List[Dict[str, Any]] = Field(default=[], description="Traffic incidents")

class OrchestrationRequest(BaseModel):
    """Main orchestration request from Angular frontend"""
    journeys: List[JourneyRequest] = Field(..., description="List of journeys to orchestrate")
    traffic_conditions: Optional[TrafficConditions] = Field(default=None, description="Current traffic conditions")
    priority: str = Field(default="normal", description="Overall request priority")
    client_id: Optional[str] = Field(default=None, description="Client identifier")

class A2ATask(BaseModel):
    """A2A Protocol Task Message"""
    task_id: str = Field(..., description="Unique task identifier")
    task_name: str = Field(..., description="Task name for agent processing")
    params: Dict[str, Any] = Field(..., description="Task parameters")
    correlation_id: str = Field(..., description="Request correlation ID")
    timestamp: str = Field(..., description="Task creation timestamp")
    source_service: str = Field(default="api-gateway", description="Source service")
    target_service: str = Field(default="orchestrator", description="Target service")
    priority: str = Field(default="normal", description="Task priority")

class GatewayResponse(BaseModel):
    """Standardized gateway response"""
    success: bool = Field(..., description="Request success status")
    task_id: str = Field(..., description="Generated task ID")
    correlation_id: str = Field(..., description="Request correlation ID")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message if any")
    timestamp: str = Field(..., description="Response timestamp")
    processing_time_ms: Optional[float] = Field(default=None, description="Processing time in milliseconds")

# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="Project Pravaah - Agentic API Gateway",
    description="HTTP-to-A2A Protocol Translation Gateway for Urban Mobility Operating System",
    version=config.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for Angular frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# =============================================================================
# HTTP Client for A2A Communication
# =============================================================================

class A2AClient:
    """Async HTTP client for A2A protocol communication"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(config.REQUEST_TIMEOUT),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
    
    async def send_a2a_task(self, task: A2ATask, target_url: str) -> Dict[str, Any]:
        """Send A2A task to target service"""
        try:
            logger.info(
                "Sending A2A task",
                task_id=task.task_id,
                target_url=target_url,
                task_name=task.task_name
            )
            
            response = await self.client.post(
                f"{target_url}/a2a/tasks",
                json=task.dict(),
                headers={
                    "Content-Type": "application/json",
                    "X-Correlation-ID": task.correlation_id,
                    "X-Source-Service": task.source_service
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(
                "A2A task completed successfully",
                task_id=task.task_id,
                status_code=response.status_code,
                response_size=len(response.content)
            )
            
            return result
            
        except httpx.TimeoutException:
            logger.error("A2A task timeout", task_id=task.task_id, target_url=target_url)
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"Timeout communicating with orchestrator service"
            )
        except httpx.HTTPStatusError as e:
            logger.error(
                "A2A task HTTP error",
                task_id=task.task_id,
                status_code=e.response.status_code,
                error_detail=e.response.text
            )
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Orchestrator service error: {e.response.text}"
            )
        except Exception as e:
            logger.error("A2A task unexpected error", task_id=task.task_id, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal gateway error: {str(e)}"
            )
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

# Global A2A client instance
a2a_client = A2AClient()

# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": config.SERVICE_NAME,
        "version": config.VERSION,
        "environment": config.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/gateway/info")
async def gateway_info():
    """Gateway service information"""
    return {
        "service_name": config.SERVICE_NAME,
        "version": config.VERSION,
        "environment": config.ENVIRONMENT,
        "orchestrator_url": config.ORCHESTRATOR_SERVICE_URL,
        "gcp_project": config.GCP_PROJECT_ID,
        "cors_origins": config.CORS_ORIGINS,
        "request_timeout": config.REQUEST_TIMEOUT,
        "max_retries": config.MAX_RETRIES
    }

@app.post("/run_orchestration", response_model=GatewayResponse)
async def run_orchestration(request: OrchestrationRequest, http_request: Request):
    """
    Main orchestration endpoint - HTTP to A2A Protocol Translation
    
    This endpoint:
    1. Accepts standard HTTP JSON from Angular frontend
    2. Generates unique task_id and correlation_id
    3. Creates formal A2A task object
    4. Makes async HTTP call to orchestrator service
    5. Returns orchestrator response to client
    """
    start_time = datetime.now(timezone.utc)
    
    # Generate unique identifiers
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    correlation_id = f"corr_{uuid.uuid4().hex[:12]}"
    
    logger.info(
        "Processing orchestration request",
        task_id=task_id,
        correlation_id=correlation_id,
        journey_count=len(request.journeys),
        client_ip=http_request.client.host if http_request.client else "unknown"
    )
    
    try:
        # Create A2A task object
        a2a_task = A2ATask(
            task_id=task_id,
            task_name="solve_traffic_conflict",
            params={
                "journeys": [journey.dict() for journey in request.journeys],
                "traffic_conditions": request.traffic_conditions.dict() if request.traffic_conditions else {},
                "priority": request.priority,
                "client_id": request.client_id,
                "gateway_metadata": {
                    "client_ip": http_request.client.host if http_request.client else "unknown",
                    "user_agent": http_request.headers.get("user-agent", "unknown"),
                    "request_timestamp": start_time.isoformat()
                }
            },
            correlation_id=correlation_id,
            timestamp=start_time.isoformat(),
            priority=request.priority
        )
        
        # Send A2A task to orchestrator service
        orchestrator_response = await a2a_client.send_a2a_task(
            task=a2a_task,
            target_url=config.ORCHESTRATOR_SERVICE_URL
        )
        
        # Calculate processing time
        end_time = datetime.now(timezone.utc)
        processing_time_ms = (end_time - start_time).total_seconds() * 1000
        
        logger.info(
            "Orchestration completed successfully",
            task_id=task_id,
            correlation_id=correlation_id,
            processing_time_ms=processing_time_ms
        )
        
        # Return standardized response
        return GatewayResponse(
            success=True,
            task_id=task_id,
            correlation_id=correlation_id,
            data=orchestrator_response,
            timestamp=end_time.isoformat(),
            processing_time_ms=processing_time_ms
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (already logged)
        raise
    except Exception as e:
        logger.error(
            "Orchestration request failed",
            task_id=task_id,
            correlation_id=correlation_id,
            error=str(e)
        )
        
        end_time = datetime.now(timezone.utc)
        processing_time_ms = (end_time - start_time).total_seconds() * 1000
        
        return GatewayResponse(
            success=False,
            task_id=task_id,
            correlation_id=correlation_id,
            error=f"Gateway processing error: {str(e)}",
            timestamp=end_time.isoformat(),
            processing_time_ms=processing_time_ms
        )

# =============================================================================
# Application Lifecycle
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info(
        "API Gateway starting up",
        service=config.SERVICE_NAME,
        version=config.VERSION,
        environment=config.ENVIRONMENT,
        orchestrator_url=config.ORCHESTRATOR_SERVICE_URL
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("API Gateway shutting down")
    await a2a_client.close()

# =============================================================================
# Development Server
# =============================================================================

if __name__ == "__main__":
    # Development server configuration
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info",
        access_log=True
    )
