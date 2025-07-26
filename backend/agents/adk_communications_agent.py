#!/usr/bin/env python3
"""
ADK-Enhanced CommunicationsAgent for Project Pravaah
Urban Mobility Operating System - Communication and Execution Agent

This agent uses Google ADK with A2A protocol and is optimized for GCP deployment.
"""

import os
import json
import uuid
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from google.cloud import firestore
from google.api_core.exceptions import GoogleAPICallError
import firebase_admin
from firebase_admin import credentials, messaging

# Import ADK base classes
from adk_base import (
    PravaahAgent, 
    AgentCapability, 
    A2AMessage, 
    MessageType
)

# Configure logging for GCP
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ADKCommunicationsAgent(PravaahAgent):
    """
    ADK-Enhanced Communications Agent for Project Pravaah
    
    Capabilities:
    - Journey rerouting and Firestore updates
    - FCM notification delivery
    - User communication management
    - GCP-optimized for Cloud Run deployment
    """
    
    def __init__(self, 
                 project_id: str = "stable-sign-454210-i0",
                 region: str = "asia-south1"):
        
        # Initialize ADK Agent
        super().__init__(
            agent_id="communications-agent",
            name="Traffic Communications Agent",
            capabilities=[
                AgentCapability.COMMUNICATION,
                AgentCapability.NOTIFICATION_DELIVERY
            ]
        )
        
        self.project_id = project_id
        self.region = region
        
        # Initialize Google Cloud services
        self.firestore_client = firestore.Client(project=project_id)
        
        # Collections
        self.journeys_collection = "journeys"
        self.notifications_collection = "notifications"
        
        # Agent-specific metrics
        self.agent_metrics = {
            "executions_completed": 0,
            "firestore_updates": 0,
            "notifications_sent": 0,
            "reroutes_executed": 0,
            "failed_operations": 0,
            "last_execution": None
        }
        
        logger.info(f"ADK CommunicationsAgent initialized for project: {project_id}")
    
    async def on_start(self):
        """ADK lifecycle hook - called when agent starts."""
        try:
            # Verify Firestore connectivity
            await self._test_firestore_connectivity()
            
            # Initialize FCM (if available)
            await self._initialize_fcm()
            
            # Start background processing loop
            asyncio.create_task(self._communication_loop())
            
            logger.info("ADK CommunicationsAgent started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start ADK CommunicationsAgent: {e}")
            raise
    
    async def on_stop(self):
        """ADK lifecycle hook - called when agent stops."""
        try:
            logger.info("ADK CommunicationsAgent stopping...")
            # Cleanup resources if needed
            
        except Exception as e:
            logger.error(f"Error stopping ADK CommunicationsAgent: {e}")
    
    async def on_message(self, message: A2AMessage) -> Optional[Dict[str, Any]]:
        """Handle incoming A2A messages."""
        try:
            action = message.action
            payload = message.payload
            
            logger.info(f"CommunicationsAgent processing A2A message: {action}")
            
            if action == "execute_reroute_and_notify":
                return await self._handle_execute_reroute_and_notify(payload)
            
            elif action == "execute_intervention":
                return await self._handle_execute_intervention(payload)
            
            elif action == "send_notification":
                return await self._handle_send_notification(payload)
            
            elif action == "update_journey_status":
                return await self._handle_update_journey_status(payload)
            
            elif action == "broadcast_alert":
                return await self._handle_broadcast_alert(payload)
            
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
    
    async def _handle_execute_reroute_and_notify(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle reroute and notify request via A2A."""
        try:
            journey_id = payload.get("journey_id")
            new_route_data = payload.get("new_route_data", {})
            reason_for_change = payload.get("reason_for_change", "Traffic optimization")
            correlation_id = payload.get("correlation_id", str(uuid.uuid4()))
            
            # Execute reroute and notify
            execution_result = await self.execute_reroute_and_notify({
                "journey_id": journey_id,
                "new_route_data": new_route_data,
                "reason_for_change": reason_for_change
            })
            
            self.agent_metrics["executions_completed"] += 1
            self.agent_metrics["last_execution"] = datetime.now(timezone.utc).isoformat()
            
            return {
                "success": True,
                "correlation_id": correlation_id,
                "execution_result": execution_result,
                "journey_id": journey_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent_id": self.agent_id
            }
            
        except Exception as e:
            logger.error(f"Error executing reroute and notify: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def _handle_execute_intervention(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle intervention execution request via A2A."""
        try:
            intervention_type = payload.get("intervention_type", "REROUTE")
            decision_result = payload.get("decision_result", {})
            correlation_id = payload.get("correlation_id", str(uuid.uuid4()))
            
            # Execute intervention based on type
            intervention_result = await self._execute_intervention_by_type(intervention_type, decision_result)
            
            return {
                "success": True,
                "correlation_id": correlation_id,
                "intervention_result": intervention_result,
                "intervention_type": intervention_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent_id": self.agent_id
            }
            
        except Exception as e:
            logger.error(f"Error executing intervention: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def _handle_send_notification(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle notification sending request via A2A."""
        try:
            notification_data = payload.get("notification_data", {})
            correlation_id = payload.get("correlation_id", str(uuid.uuid4()))
            
            # Send notification
            notification_result = await self._send_fcm_alert(notification_data)
            
            return {
                "success": True,
                "correlation_id": correlation_id,
                "notification_result": notification_result,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent_id": self.agent_id
            }
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def _handle_update_journey_status(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle journey status update request via A2A."""
        try:
            journey_id = payload.get("journey_id")
            new_status = payload.get("new_status", "UPDATED")
            correlation_id = payload.get("correlation_id", str(uuid.uuid4()))
            
            # Update journey status
            update_result = await self._update_journey_in_firestore(journey_id, {"status": new_status})
            
            return {
                "success": True,
                "correlation_id": correlation_id,
                "update_result": update_result,
                "journey_id": journey_id,
                "new_status": new_status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent_id": self.agent_id
            }
            
        except Exception as e:
            logger.error(f"Error updating journey status: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def _handle_broadcast_alert(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle broadcast alert request via A2A."""
        try:
            alert_message = payload.get("alert_message", "Traffic alert")
            alert_type = payload.get("alert_type", "INFO")
            correlation_id = payload.get("correlation_id", str(uuid.uuid4()))
            
            # Broadcast alert
            broadcast_result = await self._broadcast_traffic_alert(alert_message, alert_type)
            
            return {
                "success": True,
                "correlation_id": correlation_id,
                "broadcast_result": broadcast_result,
                "alert_type": alert_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent_id": self.agent_id
            }
            
        except Exception as e:
            logger.error(f"Error broadcasting alert: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def _handle_health_check(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle health check request via A2A."""
        firestore_status = "connected" if self.firestore_client else "disconnected"
        
        return {
            "success": True,
            "status": "healthy",
            "metrics": self.agent_metrics,
            "firestore_status": firestore_status,
            "collections": {
                "journeys": self.journeys_collection,
                "notifications": self.notifications_collection
            },
            "capabilities": [cap.value for cap in self.capabilities],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": self.agent_id
        }
    
    async def execute_reroute_and_notify(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute reroute and notification with GCP optimization.
        Core method for journey rerouting and user notification.
        """
        try:
            execution_id = str(uuid.uuid4())
            journey_id = payload.get("journey_id")
            new_route_data = payload.get("new_route_data", {})
            reason_for_change = payload.get("reason_for_change", "Traffic optimization")
            
            logger.info(f"Executing reroute for journey {journey_id} [execution_id: {execution_id}]")
            
            if not journey_id:
                raise ValueError("journey_id is required for reroute execution")
            
            # Step 1: Update journey in Firestore
            journey_update_result = await self._update_journey_in_firestore(
                journey_id, 
                {
                    "status": "REROUTED",
                    "new_route": new_route_data,
                    "reroute_reason": reason_for_change,
                    "rerouted_at": datetime.now(timezone.utc).isoformat(),
                    "rerouted_by": self.agent_id
                }
            )
            
            # Step 2: Send FCM notification
            notification_payload = {
                "journey_id": journey_id,
                "title": "Route Updated",
                "message": f"Your journey has been rerouted due to {reason_for_change}",
                "type": "REROUTE",
                "new_route": new_route_data,
                "execution_id": execution_id
            }
            
            notification_result = await self._send_fcm_alert(notification_payload)
            
            # Update metrics
            self.agent_metrics["reroutes_executed"] += 1
            if journey_update_result.get("success", False):
                self.agent_metrics["firestore_updates"] += 1
            if notification_result.get("success", False):
                self.agent_metrics["notifications_sent"] += 1
            
            execution_result = {
                "execution_id": execution_id,
                "journey_id": journey_id,
                "journey_update": journey_update_result,
                "notification": notification_result,
                "status": "completed",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Reroute execution completed for journey {journey_id}")
            
            return execution_result
            
        except Exception as e:
            logger.error(f"Error in reroute execution: {e}")
            self.agent_metrics["failed_operations"] += 1
            raise
    
    async def _update_journey_in_firestore(self, journey_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update journey document in Firestore with GCP optimization."""
        try:
            # Check if journey exists
            journey_ref = self.firestore_client.collection(self.journeys_collection).document(journey_id)
            journey_doc = journey_ref.get()
            
            if not journey_doc.exists:
                # Create new journey document if it doesn't exist
                initial_journey_data = {
                    "id": journey_id,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "created_by": self.agent_id
                }
                initial_journey_data.update(update_data)
                journey_ref.set(initial_journey_data)
                
                logger.info(f"Created new journey document: {journey_id}")
                
                return {
                    "success": True,
                    "action": "created",
                    "journey_id": journey_id,
                    "data": initial_journey_data
                }
            else:
                # Update existing journey
                journey_ref.update(update_data)
                
                logger.info(f"Updated journey document: {journey_id}")
                
                return {
                    "success": True,
                    "action": "updated",
                    "journey_id": journey_id,
                    "updates": update_data
                }
                
        except Exception as e:
            logger.error(f"Error updating journey {journey_id} in Firestore: {e}")
            return {
                "success": False,
                "error": str(e),
                "journey_id": journey_id
            }
    
    async def _send_fcm_alert(self, notification_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send FCM notification with GCP optimization.
        Hackathon-friendly implementation with production-ready code.
        """
        try:
            message_id = str(uuid.uuid4())
            journey_id = notification_payload.get("journey_id", "unknown")
            title = notification_payload.get("title", "Traffic Alert")
            message = notification_payload.get("message", "Traffic update available")
            notification_type = notification_payload.get("type", "INFO")
            
            # Hackathon-friendly: Console logging for demo
            logger.info(f"FCM Alert Sent: {title} - {message} (Journey: {journey_id})")
            print(f"🔔 FCM NOTIFICATION: {title}")
            print(f"   Message: {message}")
            print(f"   Journey ID: {journey_id}")
            print(f"   Type: {notification_type}")
            print(f"   Message ID: {message_id}")
            
            # Store notification in Firestore for tracking
            notification_doc = {
                "message_id": message_id,
                "journey_id": journey_id,
                "title": title,
                "message": message,
                "type": notification_type,
                "status": "sent",
                "sent_at": datetime.now(timezone.utc).isoformat(),
                "sent_by": self.agent_id,
                "payload": notification_payload
            }
            
            # Save to Firestore
            notification_ref = self.firestore_client.collection(self.notifications_collection).document(message_id)
            notification_ref.set(notification_doc)
            
            # Production-ready FCM code (commented for hackathon speed)
            """
            # Uncomment for production FCM integration
            try:
                fcm_message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=message
                    ),
                    data={
                        "journey_id": journey_id,
                        "type": notification_type,
                        "message_id": message_id
                    },
                    topic="traffic_alerts"  # Or use specific user tokens
                )
                
                response = messaging.send(fcm_message)
                logger.info(f"FCM message sent successfully: {response}")
                
            except Exception as fcm_error:
                logger.error(f"FCM sending failed: {fcm_error}")
            """
            
            return {
                "success": True,
                "message_id": message_id,
                "journey_id": journey_id,
                "title": title,
                "message": message,
                "type": notification_type,
                "method": "console_log_demo",  # Change to "fcm" in production
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sending FCM alert: {e}")
            return {
                "success": False,
                "error": str(e),
                "journey_id": notification_payload.get("journey_id", "unknown")
            }
    
    async def _execute_intervention_by_type(self, intervention_type: str, decision_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute intervention based on type with GCP optimization."""
        try:
            intervention_id = str(uuid.uuid4())
            
            if intervention_type == "REROUTE":
                # Execute reroute intervention
                result = await self._execute_reroute_intervention(decision_result, intervention_id)
                
            elif intervention_type == "EMERGENCY":
                # Execute emergency intervention
                result = await self._execute_emergency_intervention(decision_result, intervention_id)
                
            elif intervention_type == "COORDINATE":
                # Execute coordination intervention
                result = await self._execute_coordination_intervention(decision_result, intervention_id)
                
            else:
                # Monitor intervention (no action needed)
                result = {
                    "intervention_id": intervention_id,
                    "type": intervention_type,
                    "action": "monitoring_continued",
                    "status": "completed"
                }
            
            result["timestamp"] = datetime.now(timezone.utc).isoformat()
            return result
            
        except Exception as e:
            logger.error(f"Error executing intervention {intervention_type}: {e}")
            return {
                "success": False,
                "error": str(e),
                "intervention_type": intervention_type
            }
    
    async def _execute_reroute_intervention(self, decision_result: Dict[str, Any], intervention_id: str) -> Dict[str, Any]:
        """Execute reroute intervention."""
        try:
            # Get affected journeys (simulated for demo)
            affected_journeys = ["journey_001", "journey_002", "journey_003"]
            
            reroute_results = []
            for journey_id in affected_journeys:
                reroute_result = await self.execute_reroute_and_notify({
                    "journey_id": journey_id,
                    "new_route_data": {
                        "alternate_route": "Outer Ring Road",
                        "estimated_time_savings": "15 minutes"
                    },
                    "reason_for_change": "Traffic congestion detected"
                })
                reroute_results.append(reroute_result)
            
            return {
                "intervention_id": intervention_id,
                "type": "REROUTE",
                "affected_journeys": len(affected_journeys),
                "reroute_results": reroute_results,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error in reroute intervention: {e}")
            return {"error": str(e)}
    
    async def _execute_emergency_intervention(self, decision_result: Dict[str, Any], intervention_id: str) -> Dict[str, Any]:
        """Execute emergency intervention."""
        try:
            # Broadcast emergency alert
            alert_result = await self._broadcast_traffic_alert(
                "EMERGENCY: Severe traffic congestion detected. Avoid affected areas.",
                "EMERGENCY"
            )
            
            # Notify authorities (simulated)
            authority_notifications = await self._notify_authorities(decision_result)
            
            return {
                "intervention_id": intervention_id,
                "type": "EMERGENCY",
                "alert_result": alert_result,
                "authority_notifications": authority_notifications,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error in emergency intervention: {e}")
            return {"error": str(e)}
    
    async def _execute_coordination_intervention(self, decision_result: Dict[str, Any], intervention_id: str) -> Dict[str, Any]:
        """Execute coordination intervention."""
        try:
            # Coordinate with traffic authorities
            coordination_result = await self._coordinate_with_authorities(decision_result)
            
            # Send coordination alerts
            alert_result = await self._broadcast_traffic_alert(
                "Traffic coordination in progress. Please follow alternate routes.",
                "COORDINATION"
            )
            
            return {
                "intervention_id": intervention_id,
                "type": "COORDINATE",
                "coordination_result": coordination_result,
                "alert_result": alert_result,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error in coordination intervention: {e}")
            return {"error": str(e)}
    
    async def _broadcast_traffic_alert(self, alert_message: str, alert_type: str) -> Dict[str, Any]:
        """Broadcast traffic alert to all users."""
        try:
            broadcast_id = str(uuid.uuid4())
            
            # Broadcast via FCM (simulated for demo)
            broadcast_payload = {
                "broadcast_id": broadcast_id,
                "title": f"Traffic Alert - {alert_type}",
                "message": alert_message,
                "type": alert_type
            }
            
            notification_result = await self._send_fcm_alert(broadcast_payload)
            
            logger.info(f"Traffic alert broadcasted: {alert_type}")
            
            return {
                "success": True,
                "broadcast_id": broadcast_id,
                "alert_type": alert_type,
                "message": alert_message,
                "notification_result": notification_result
            }
            
        except Exception as e:
            logger.error(f"Error broadcasting alert: {e}")
            return {"success": False, "error": str(e)}
    
    async def _notify_authorities(self, decision_result: Dict[str, Any]) -> Dict[str, Any]:
        """Notify traffic authorities (simulated for demo)."""
        try:
            authorities = ["Traffic Police", "BMTC", "BBMP Traffic"]
            notifications_sent = []
            
            for authority in authorities:
                notification = {
                    "authority": authority,
                    "message": f"Traffic intervention required: {decision_result.get('strategy', 'Unknown')}",
                    "status": "notified",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                notifications_sent.append(notification)
                
                logger.info(f"Authority notified: {authority}")
            
            return {
                "success": True,
                "authorities_notified": len(authorities),
                "notifications": notifications_sent
            }
            
        except Exception as e:
            logger.error(f"Error notifying authorities: {e}")
            return {"success": False, "error": str(e)}
    
    async def _coordinate_with_authorities(self, decision_result: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate with traffic authorities (simulated for demo)."""
        try:
            coordination_actions = [
                "Signal timing optimization requested",
                "Traffic police deployment coordinated",
                "Public transport rerouting initiated"
            ]
            
            coordination_result = {
                "success": True,
                "actions_taken": coordination_actions,
                "coordination_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info("Traffic authority coordination completed")
            
            return coordination_result
            
        except Exception as e:
            logger.error(f"Error coordinating with authorities: {e}")
            return {"success": False, "error": str(e)}
    
    async def _test_firestore_connectivity(self):
        """Test Firestore connectivity for GCP deployment."""
        try:
            # Test Firestore connection
            test_doc = self.firestore_client.collection("health_check").document("test")
            test_doc.set({"test": True, "timestamp": datetime.now(timezone.utc).isoformat()})
            
            # Clean up test document
            test_doc.delete()
            
            logger.info("Firestore connectivity test successful")
            
        except Exception as e:
            logger.warning(f"Firestore connectivity test failed: {e}")
    
    async def _initialize_fcm(self):
        """Initialize FCM for GCP deployment."""
        try:
            # FCM is initialized with Firebase Admin SDK
            # For production, ensure FCM is properly configured
            logger.info("FCM initialization ready (using console logging for demo)")
            
        except Exception as e:
            logger.warning(f"FCM initialization warning: {e}")
    
    async def _communication_loop(self):
        """Background communication processing loop for GCP deployment."""
        try:
            logger.info("Starting communication loop")
            
            while self.status == "active":
                try:
                    # Process pending communications
                    await asyncio.sleep(60)  # Check every minute
                    
                    # Process any queued notifications or updates
                    await self._process_pending_communications()
                    
                except Exception as e:
                    logger.error(f"Error in communication loop: {e}")
                    await asyncio.sleep(120)  # Wait longer on error
            
        except Exception as e:
            logger.error(f"Communication loop failed: {e}")
    
    async def _process_pending_communications(self):
        """Process pending communications and notifications."""
        try:
            # This would process any queued communications in production
            # For now, just update metrics
            pass
            
        except Exception as e:
            logger.error(f"Error processing pending communications: {e}")

# Factory function for creating ADK CommunicationsAgent
async def create_adk_communications_agent(project_id: str = "stable-sign-454210-i0") -> ADKCommunicationsAgent:
    """Create and start ADK CommunicationsAgent for GCP deployment."""
    agent = ADKCommunicationsAgent(project_id=project_id)
    await agent.start()
    return agent

# Main function for GCP Cloud Run deployment
async def main():
    """Main function for GCP Cloud Run deployment."""
    try:
        logger.info("Starting ADK CommunicationsAgent for GCP deployment")
        
        # Create and start agent
        agent = await create_adk_communications_agent()
        
        # Keep agent running for Cloud Run
        logger.info("ADK CommunicationsAgent is running on GCP")
        while True:
            await asyncio.sleep(60)
            status = agent.get_status()
            logger.info(f"Agent status: {status['status']}, Executions: {status['metrics']['executions_completed']}")
            
    except Exception as e:
        logger.error(f"Error in ADK CommunicationsAgent: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
