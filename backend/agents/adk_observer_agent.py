#!/usr/bin/env python3
"""
ADK-Enhanced ObserverAgent for Project Pravaah
Urban Mobility Operating System - Traffic Perception Agent

This agent uses Google ADK with A2A protocol for standardized multi-agent coordination.
"""

import os
import json
import uuid
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from google.cloud import firestore
from google.cloud import pubsub_v1
from google.api_core.exceptions import GoogleAPICallError
import firebase_admin
from firebase_admin import credentials

# Import ADK base classes
from adk_base import (
    PravaahAgent, 
    AgentCapability, 
    A2AMessage, 
    MessageType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ADKObserverAgent(PravaahAgent):
    """
    ADK-Enhanced Observer Agent for Project Pravaah
    
    Capabilities:
    - Real-time traffic telemetry ingestion
    - Network state perception and monitoring
    - Firestore data updates
    - A2A communication with other agents
    """
    
    def __init__(self, 
                 project_id: str = "stable-sign-454210-i0",
                 region: str = "asia-south1"):
        
        # Initialize ADK Agent
        super().__init__(
            agent_id="observer-agent",
            name="Traffic Observer Agent",
            capabilities=[
                AgentCapability.PERCEPTION,
                AgentCapability.TRAFFIC_MONITORING,
                AgentCapability.TELEMETRY_INGESTION
            ]
        )
        
        self.project_id = project_id
        self.region = region
        
        # Initialize Google Cloud services
        self.firestore_client = firestore.Client(project=project_id)
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        
        # Agent-specific configuration
        self.telemetry_topic = "vehicle-telemetry"
        self.network_state_collection = "network_state"
        self.journeys_collection = "journeys"
        
        # Performance metrics
        self.agent_metrics = {
            "telemetry_processed": 0,
            "network_updates": 0,
            "perception_cycles": 0,
            "errors": 0,
            "last_perception": None
        }
        
        logger.info(f"ADK ObserverAgent initialized for project: {project_id}")
    
    async def on_start(self):
        """ADK lifecycle hook - called when agent starts."""
        try:
            # Set up Pub/Sub topic and subscription
            await self._setup_pubsub()
            
            # Initialize Firestore collections
            await self._initialize_firestore_collections()
            
            # Start background telemetry ingestion
            asyncio.create_task(self._telemetry_ingestion_loop())
            
            logger.info("ADK ObserverAgent started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start ADK ObserverAgent: {e}")
            raise
    
    async def on_stop(self):
        """ADK lifecycle hook - called when agent stops."""
        try:
            logger.info("ADK ObserverAgent stopping...")
            # Cleanup resources if needed
            
        except Exception as e:
            logger.error(f"Error stopping ADK ObserverAgent: {e}")
    
    async def on_message(self, message: A2AMessage) -> Optional[Dict[str, Any]]:
        """Handle incoming A2A messages."""
        try:
            action = message.action
            payload = message.payload
            
            logger.info(f"ObserverAgent processing A2A message: {action}")
            
            if action == "get_network_state":
                return await self._handle_get_network_state(payload)
            
            elif action == "get_telemetry_data":
                return await self._handle_get_telemetry_data(payload)
            
            elif action == "start_perception_cycle":
                return await self._handle_start_perception_cycle(payload)
            
            elif action == "health_check":
                return await self._handle_health_check(payload)
            
            else:
                logger.warning(f"Unknown action: {action}")
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "agent_id": self.agent_id
                }
                
        except Exception as e:
            logger.error(f"Error handling A2A message: {e}")
            self.agent_metrics["errors"] += 1
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def _handle_get_network_state(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle network state request via A2A."""
        try:
            correlation_id = payload.get("correlation_id", str(uuid.uuid4()))
            
            # Get current network state
            network_state = await self.get_network_state()
            
            return {
                "success": True,
                "correlation_id": correlation_id,
                "network_state": network_state,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent_id": self.agent_id
            }
            
        except Exception as e:
            logger.error(f"Error getting network state: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def _handle_get_telemetry_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle telemetry data request via A2A."""
        try:
            time_window = payload.get("time_window_minutes", 10)
            correlation_id = payload.get("correlation_id", str(uuid.uuid4()))
            
            # Get recent telemetry data
            telemetry_data = await self._get_recent_telemetry(time_window)
            
            return {
                "success": True,
                "correlation_id": correlation_id,
                "telemetry_data": telemetry_data,
                "time_window_minutes": time_window,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent_id": self.agent_id
            }
            
        except Exception as e:
            logger.error(f"Error getting telemetry data: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def _handle_start_perception_cycle(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle perception cycle start request via A2A."""
        try:
            cycle_id = payload.get("cycle_id", str(uuid.uuid4()))
            
            # Start perception cycle
            perception_result = await self._run_perception_cycle(cycle_id)
            
            self.agent_metrics["perception_cycles"] += 1
            self.agent_metrics["last_perception"] = datetime.now(timezone.utc).isoformat()
            
            return {
                "success": True,
                "cycle_id": cycle_id,
                "perception_result": perception_result,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent_id": self.agent_id
            }
            
        except Exception as e:
            logger.error(f"Error in perception cycle: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def _handle_health_check(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle health check request via A2A."""
        return {
            "success": True,
            "status": "healthy",
            "metrics": self.agent_metrics,
            "capabilities": [cap.value for cap in self.capabilities],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": self.agent_id
        }
    
    async def get_network_state(self) -> Dict[str, Any]:
        """Get current network state from Firestore."""
        try:
            # Get latest network state document
            network_docs = self.firestore_client.collection(self.network_state_collection)\
                .order_by("timestamp", direction=firestore.Query.DESCENDING)\
                .limit(1)\
                .stream()
            
            for doc in network_docs:
                network_data = doc.to_dict()
                logger.info("Retrieved current network state from Firestore")
                return network_data
            
            # If no network state found, return default
            default_state = {
                "active_vehicles": 0,
                "average_speed": 0.0,
                "congestion_level": "unknown",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "observer_agent_default"
            }
            
            logger.warning("No network state found, returning default state")
            return default_state
            
        except Exception as e:
            logger.error(f"Error retrieving network state: {e}")
            self.agent_metrics["errors"] += 1
            raise
    
    async def _get_recent_telemetry(self, time_window_minutes: int = 10) -> List[Dict[str, Any]]:
        """Get recent telemetry data from Firestore."""
        try:
            # Calculate time threshold
            from datetime import timedelta
            threshold_time = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)
            
            # Query recent telemetry
            telemetry_docs = self.firestore_client.collection("vehicle_telemetry")\
                .where("timestamp", ">=", threshold_time.isoformat())\
                .order_by("timestamp", direction=firestore.Query.DESCENDING)\
                .limit(100)\
                .stream()
            
            telemetry_data = []
            for doc in telemetry_docs:
                telemetry_data.append(doc.to_dict())
            
            logger.info(f"Retrieved {len(telemetry_data)} telemetry records from last {time_window_minutes} minutes")
            return telemetry_data
            
        except Exception as e:
            logger.error(f"Error retrieving telemetry data: {e}")
            return []
    
    async def _run_perception_cycle(self, cycle_id: str) -> Dict[str, Any]:
        """Run a complete perception cycle."""
        try:
            start_time = datetime.now(timezone.utc)
            
            # 1. Get current network state
            network_state = await self.get_network_state()
            
            # 2. Get recent telemetry
            telemetry_data = await self._get_recent_telemetry(5)  # Last 5 minutes
            
            # 3. Analyze traffic patterns
            traffic_analysis = await self._analyze_traffic_patterns(telemetry_data)
            
            # 4. Update network state if needed
            if traffic_analysis.get("state_changed", False):
                await self._update_network_state(traffic_analysis["new_state"])
                self.agent_metrics["network_updates"] += 1
            
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            perception_result = {
                "cycle_id": cycle_id,
                "network_state": network_state,
                "telemetry_count": len(telemetry_data),
                "traffic_analysis": traffic_analysis,
                "duration_seconds": duration,
                "timestamp": end_time.isoformat()
            }
            
            logger.info(f"Perception cycle {cycle_id} completed in {duration:.2f}s")
            return perception_result
            
        except Exception as e:
            logger.error(f"Error in perception cycle {cycle_id}: {e}")
            raise
    
    async def _analyze_traffic_patterns(self, telemetry_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze traffic patterns from telemetry data."""
        try:
            if not telemetry_data:
                return {
                    "state_changed": False,
                    "analysis": "No telemetry data available"
                }
            
            # Simple traffic analysis
            total_vehicles = len(telemetry_data)
            avg_speed = sum(t.get("speed", 0) for t in telemetry_data) / max(total_vehicles, 1)
            
            # Determine congestion level
            if avg_speed < 20:
                congestion_level = "high"
            elif avg_speed < 40:
                congestion_level = "medium"
            else:
                congestion_level = "low"
            
            # Check if state changed significantly
            current_state = await self.get_network_state()
            state_changed = (
                abs(current_state.get("active_vehicles", 0) - total_vehicles) > 5 or
                current_state.get("congestion_level") != congestion_level
            )
            
            analysis = {
                "state_changed": state_changed,
                "analysis": {
                    "total_vehicles": total_vehicles,
                    "average_speed": avg_speed,
                    "congestion_level": congestion_level,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
            
            if state_changed:
                analysis["new_state"] = {
                    "active_vehicles": total_vehicles,
                    "average_speed": avg_speed,
                    "congestion_level": congestion_level,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "observer_agent_analysis"
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing traffic patterns: {e}")
            return {"state_changed": False, "error": str(e)}
    
    async def _update_network_state(self, new_state: Dict[str, Any]):
        """Update network state in Firestore."""
        try:
            doc_ref = self.firestore_client.collection(self.network_state_collection).document()
            doc_ref.set(new_state)
            logger.info("Network state updated in Firestore")
            
        except Exception as e:
            logger.error(f"Error updating network state: {e}")
            raise
    
    async def _setup_pubsub(self):
        """Set up Pub/Sub topic and subscription for telemetry."""
        try:
            topic_path = self.publisher.topic_path(self.project_id, self.telemetry_topic)
            
            # Create topic if it doesn't exist
            try:
                self.publisher.create_topic(request={"name": topic_path})
                logger.info(f"Created Pub/Sub topic: {topic_path}")
            except Exception:
                logger.info(f"Pub/Sub topic already exists: {topic_path}")
            
        except Exception as e:
            logger.error(f"Error setting up Pub/Sub: {e}")
    
    async def _initialize_firestore_collections(self):
        """Initialize Firestore collections with default documents if needed."""
        try:
            # Check if network_state collection has any documents
            network_docs = list(self.firestore_client.collection(self.network_state_collection).limit(1).stream())
            
            if not network_docs:
                # Create initial network state
                initial_state = {
                    "active_vehicles": 0,
                    "average_speed": 0.0,
                    "congestion_level": "unknown",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "source": "observer_agent_initialization"
                }
                
                doc_ref = self.firestore_client.collection(self.network_state_collection).document()
                doc_ref.set(initial_state)
                logger.info("Initialized network_state collection")
            
        except Exception as e:
            logger.error(f"Error initializing Firestore collections: {e}")
    
    async def _telemetry_ingestion_loop(self):
        """Background loop for telemetry ingestion."""
        try:
            logger.info("Starting telemetry ingestion loop")
            
            while self.status == "active":
                try:
                    # Simulate telemetry ingestion
                    # In production, this would pull from actual Pub/Sub subscription
                    await asyncio.sleep(30)  # Check every 30 seconds
                    
                    # Process any pending telemetry
                    await self._process_pending_telemetry()
                    
                except Exception as e:
                    logger.error(f"Error in telemetry ingestion loop: {e}")
                    await asyncio.sleep(60)  # Wait longer on error
            
        except Exception as e:
            logger.error(f"Telemetry ingestion loop failed: {e}")
    
    async def _process_pending_telemetry(self):
        """Process pending telemetry data."""
        try:
            # This is a placeholder for actual telemetry processing
            # In production, this would process real vehicle telemetry data
            self.agent_metrics["telemetry_processed"] += 1
            
        except Exception as e:
            logger.error(f"Error processing telemetry: {e}")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status."""
        base_status = self.get_status()
        base_status.update({
            "agent_metrics": self.agent_metrics,
            "project_id": self.project_id,
            "region": self.region,
            "collections": {
                "network_state": self.network_state_collection,
                "journeys": self.journeys_collection
            }
        })
        return base_status

# Factory function for creating ADK ObserverAgent
async def create_adk_observer_agent(project_id: str = "stable-sign-454210-i0") -> ADKObserverAgent:
    """Create and start ADK ObserverAgent."""
    agent = ADKObserverAgent(project_id=project_id)
    await agent.start()
    return agent

# Main function for testing
async def main():
    """Main function for testing ADK ObserverAgent."""
    try:
        logger.info("Starting ADK ObserverAgent test")
        
        # Create and start agent
        agent = await create_adk_observer_agent()
        
        # Test A2A messaging
        test_message = A2AMessage(
            message_id=str(uuid.uuid4()),
            sender="test-client",
            receiver="observer-agent",
            message_type=MessageType.REQUEST,
            action="health_check",
            payload={"test": True},
            correlation_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
        response = await agent.on_message(test_message)
        logger.info(f"Test response: {response}")
        
        # Keep agent running
        logger.info("ADK ObserverAgent is running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(10)
            status = agent.get_agent_status()
            logger.info(f"Agent status: {status['status']}, Messages: {status['metrics']['messages_received']}")
            
    except KeyboardInterrupt:
        logger.info("Stopping ADK ObserverAgent...")
        await agent.stop()
    except Exception as e:
        logger.error(f"Error in ADK ObserverAgent test: {e}")

if __name__ == "__main__":
    asyncio.run(main())
