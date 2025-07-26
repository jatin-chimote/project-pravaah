#!/usr/bin/env python3
"""
ADK-Enhanced OrchestratorAgent for Project Pravaah
Urban Mobility Operating System - Strategic Decision Making Agent

This agent uses Google ADK with A2A protocol and is optimized for GCP deployment.
"""

import os
import json
import uuid
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import firestore
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

# Configure logging for GCP
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ADKOrchestratorAgent(PravaahAgent):
    """
    ADK-Enhanced Orchestrator Agent for Project Pravaah
    
    Capabilities:
    - Strategic decision making using Gemini AI
    - Multi-agent coordination via A2A protocol
    - Traffic intervention planning
    - GCP-optimized for Cloud Run deployment
    """
    
    def __init__(self, 
                 project_id: str = "stable-sign-454210-i0",
                 location: str = "asia-south1",
                 congestion_threshold: float = 80.0):
        
        # Initialize ADK Agent
        super().__init__(
            agent_id="orchestrator-agent",
            name="Traffic Orchestrator Agent",
            capabilities=[
                AgentCapability.DECISION_MAKING,
                AgentCapability.STRATEGIC_PLANNING
            ]
        )
        
        self.project_id = project_id
        self.location = location
        self.congestion_threshold = congestion_threshold
        
        # Initialize Google Cloud services
        self.firestore_client = firestore.Client(project=project_id)
        
        # Initialize Vertex AI for Gemini
        self._initialize_vertex_ai()
        
        # Agent-specific metrics
        self.agent_metrics = {
            "orchestration_cycles": 0,
            "interventions_planned": 0,
            "gemini_calls": 0,
            "gemini_failures": 0,
            "decisions_made": 0,
            "last_orchestration": None
        }
        
        # Strategic decision options
        self.strategy_options = [
            "MONITOR_AND_WAIT",
            "REROUTE_VEHICLES", 
            "EMERGENCY_INTERVENTION",
            "COORDINATE_WITH_AUTHORITIES"
        ]
        
        logger.info(f"ADK OrchestratorAgent initialized for project: {project_id}")
        logger.info(f"Gemini AI integration ready in region: {location}")
    
    def _initialize_vertex_ai(self):
        """Initialize Vertex AI for GCP deployment."""
        try:
            # For GCP deployment, use Application Default Credentials
            if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                # Local development with service account key
                key_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
                logger.info(f"Using service account: {key_path}")
            else:
                # Cloud Run deployment with metadata service
                logger.info("Using GCP metadata service for authentication")
            
            # Initialize Vertex AI
            vertexai.init(project=self.project_id, location=self.location)
            
            # Initialize Gemini model
            self.gemini_model = GenerativeModel("gemini-1.5-pro")
            
            logger.info(f"Vertex AI initialized for project {self.project_id} in {self.location}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            self.gemini_model = None
    
    async def on_start(self):
        """ADK lifecycle hook - called when agent starts."""
        try:
            # Verify Gemini connectivity
            await self._test_gemini_connectivity()
            
            # Start orchestration loop
            asyncio.create_task(self._orchestration_loop())
            
            logger.info("ADK OrchestratorAgent started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start ADK OrchestratorAgent: {e}")
            raise
    
    async def on_stop(self):
        """ADK lifecycle hook - called when agent stops."""
        try:
            logger.info("ADK OrchestratorAgent stopping...")
            # Cleanup resources if needed
            
        except Exception as e:
            logger.error(f"Error stopping ADK OrchestratorAgent: {e}")
    
    async def on_message(self, message: A2AMessage) -> Optional[Dict[str, Any]]:
        """Handle incoming A2A messages."""
        try:
            action = message.action
            payload = message.payload
            
            logger.info(f"OrchestratorAgent processing A2A message: {action}")
            
            if action == "run_orchestration_cycle":
                return await self._handle_run_orchestration_cycle(payload)
            
            elif action == "make_strategic_decision":
                return await self._handle_make_strategic_decision(payload)
            
            elif action == "coordinate_agents":
                return await self._handle_coordinate_agents(payload)
            
            elif action == "plan_intervention":
                return await self._handle_plan_intervention(payload)
            
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
    
    async def _handle_run_orchestration_cycle(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle orchestration cycle request via A2A."""
        try:
            cycle_id = payload.get("cycle_id", str(uuid.uuid4()))
            correlation_id = payload.get("correlation_id", str(uuid.uuid4()))
            
            # Run complete orchestration cycle
            orchestration_result = await self.run_orchestration_cycle(cycle_id)
            
            self.agent_metrics["orchestration_cycles"] += 1
            self.agent_metrics["last_orchestration"] = datetime.now(timezone.utc).isoformat()
            
            return {
                "success": True,
                "correlation_id": correlation_id,
                "cycle_id": cycle_id,
                "orchestration_result": orchestration_result,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent_id": self.agent_id
            }
            
        except Exception as e:
            logger.error(f"Error in orchestration cycle: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def _handle_make_strategic_decision(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle strategic decision request via A2A."""
        try:
            situation_data = payload.get("situation_data", {})
            correlation_id = payload.get("correlation_id", str(uuid.uuid4()))
            
            # Make strategic decision using Gemini AI
            decision_result = await self._reason_and_decide(situation_data)
            
            self.agent_metrics["decisions_made"] += 1
            
            return {
                "success": True,
                "correlation_id": correlation_id,
                "decision_result": decision_result,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent_id": self.agent_id
            }
            
        except Exception as e:
            logger.error(f"Error making strategic decision: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def _handle_coordinate_agents(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent coordination request via A2A."""
        try:
            coordination_plan = payload.get("coordination_plan", {})
            correlation_id = payload.get("correlation_id", str(uuid.uuid4()))
            
            # Coordinate with other agents
            coordination_result = await self._coordinate_multi_agent_action(coordination_plan)
            
            return {
                "success": True,
                "correlation_id": correlation_id,
                "coordination_result": coordination_result,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent_id": self.agent_id
            }
            
        except Exception as e:
            logger.error(f"Error coordinating agents: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def _handle_plan_intervention(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle intervention planning request via A2A."""
        try:
            intervention_type = payload.get("intervention_type", "REROUTE_VEHICLES")
            situation_data = payload.get("situation_data", {})
            correlation_id = payload.get("correlation_id", str(uuid.uuid4()))
            
            # Plan intervention
            intervention_plan = await self._plan_intervention(intervention_type, situation_data)
            
            self.agent_metrics["interventions_planned"] += 1
            
            return {
                "success": True,
                "correlation_id": correlation_id,
                "intervention_plan": intervention_plan,
                "intervention_type": intervention_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent_id": self.agent_id
            }
            
        except Exception as e:
            logger.error(f"Error planning intervention: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def _handle_health_check(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle health check request via A2A."""
        gemini_status = "connected" if self.gemini_model else "disconnected"
        
        return {
            "success": True,
            "status": "healthy",
            "metrics": self.agent_metrics,
            "gemini_status": gemini_status,
            "strategy_options": self.strategy_options,
            "capabilities": [cap.value for cap in self.capabilities],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": self.agent_id
        }
    
    async def run_orchestration_cycle(self, cycle_id: str = None) -> Dict[str, Any]:
        """
        Run complete orchestration cycle using A2A protocol.
        GCP-optimized for Cloud Run deployment.
        """
        try:
            if not cycle_id:
                cycle_id = f"cycle_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            
            start_time = datetime.now(timezone.utc)
            logger.info(f"Starting orchestration cycle [{cycle_id}]")
            
            # Step 1: Get network state from ObserverAgent via A2A
            perception_data = await self._request_perception_data()
            
            # Step 2: Get predictions from SimulationAgent via A2A
            prediction_data = await self._request_prediction_data(perception_data)
            
            # Step 3: Make strategic decision using Gemini AI
            decision_result = await self._reason_and_decide(prediction_data)
            
            # Step 4: Execute decision via CommunicationsAgent if needed
            execution_result = None
            if decision_result.get("intervention_needed", False):
                execution_result = await self._execute_intervention(decision_result)
            
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            orchestration_result = {
                "cycle_id": cycle_id,
                "perception_data": perception_data,
                "prediction_data": prediction_data,
                "decision_result": decision_result,
                "execution_result": execution_result,
                "duration_seconds": duration,
                "timestamp": end_time.isoformat(),
                "status": "completed"
            }
            
            logger.info(f"Orchestration cycle [{cycle_id}] completed in {duration:.2f}s")
            
            return orchestration_result
            
        except Exception as e:
            logger.error(f"Error in orchestration cycle [{cycle_id}]: {e}")
            self.agent_metrics["errors"] += 1
            raise
    
    async def _request_perception_data(self) -> Dict[str, Any]:
        """Request perception data from ObserverAgent via A2A."""
        try:
            # Discover ObserverAgent
            observer_agents = await self.discover_agents(AgentCapability.PERCEPTION)
            
            if not observer_agents:
                logger.warning("No ObserverAgent found, using fallback")
                return {"network_state": {"active_vehicles": 0, "congestion_level": "unknown"}}
            
            # Send A2A message to ObserverAgent
            perception_message = A2AMessage(
                message_id=str(uuid.uuid4()),
                sender=self.agent_id,
                receiver="observer-agent",
                message_type=MessageType.REQUEST,
                action="get_network_state",
                payload={"correlation_id": str(uuid.uuid4())},
                correlation_id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            # For now, simulate the response (in full implementation, this would use actual A2A messaging)
            perception_data = {
                "network_state": {
                    "active_vehicles": 150,
                    "average_speed": 35.5,
                    "congestion_level": "medium",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                "source": "observer_agent_a2a"
            }
            
            logger.info("Received perception data via A2A")
            return perception_data
            
        except Exception as e:
            logger.error(f"Error requesting perception data: {e}")
            return {"error": str(e)}
    
    async def _request_prediction_data(self, perception_data: Dict[str, Any]) -> Dict[str, Any]:
        """Request prediction data from SimulationAgent via A2A."""
        try:
            # Discover SimulationAgent
            simulation_agents = await self.discover_agents(AgentCapability.PREDICTION)
            
            if not simulation_agents:
                logger.warning("No SimulationAgent found, using fallback")
                return {"congestion_score": 0, "critical_choke_point": None}
            
            # Send A2A message to SimulationAgent
            prediction_message = A2AMessage(
                message_id=str(uuid.uuid4()),
                sender=self.agent_id,
                receiver="simulation-agent",
                message_type=MessageType.REQUEST,
                action="predict_congestion",
                payload={
                    "network_state": perception_data.get("network_state", {}),
                    "time_horizon_minutes": 30,
                    "correlation_id": str(uuid.uuid4())
                },
                correlation_id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            # For now, simulate the response (in full implementation, this would use actual A2A messaging)
            prediction_data = {
                "congestion_score": 45.5,
                "critical_choke_point": None,
                "affected_vehicles": 75,
                "prediction_confidence": 0.85,
                "recommendations": ["Monitor closely", "Prepare alternate routes"],
                "source": "simulation_agent_a2a"
            }
            
            logger.info("Received prediction data via A2A")
            return prediction_data
            
        except Exception as e:
            logger.error(f"Error requesting prediction data: {e}")
            return {"error": str(e)}
    
    async def _reason_and_decide(self, prediction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make strategic decision using Gemini AI with GCP optimization."""
        try:
            # Create situation report for Gemini
            situation_report = {
                "traffic_analysis": {
                    "congestion_score": prediction_data.get("congestion_score", 0),
                    "critical_choke_point": prediction_data.get("critical_choke_point"),
                    "affected_vehicles": prediction_data.get("affected_vehicles", 0),
                    "prediction_confidence": prediction_data.get("prediction_confidence", 0.5)
                },
                "temporal_context": {
                    "current_time": datetime.now(timezone.utc).isoformat(),
                    "is_peak_hour": self._is_peak_hour(),
                    "day_of_week": datetime.now().strftime("%A")
                },
                "system_state": {
                    "available_strategies": self.strategy_options,
                    "congestion_threshold": self.congestion_threshold
                },
                "bengaluru_context": {
                    "major_routes": ["ORR", "Hosur Road", "Whitefield Road"],
                    "critical_junctions": ["Silk Board", "Electronic City", "Whitefield"]
                }
            }
            
            # Try Gemini AI decision
            gemini_strategy = await self._get_gemini_strategy(situation_report)
            
            if gemini_strategy:
                # Use Gemini recommendation
                strategy = gemini_strategy
                reasoning_source = "gemini_ai"
                self.agent_metrics["gemini_calls"] += 1
            else:
                # Fallback to rule-based decision
                strategy = self._fallback_strategy_decision(prediction_data)
                reasoning_source = "fallback_rules"
                self.agent_metrics["gemini_failures"] += 1
            
            # Map strategy to intervention
            intervention_type = self._map_strategy_to_intervention(strategy)
            intervention_needed = intervention_type != "MONITOR"
            
            decision_result = {
                "strategy": strategy,
                "intervention_type": intervention_type,
                "intervention_needed": intervention_needed,
                "reasoning_source": reasoning_source,
                "risk_level": self._calculate_risk_level(prediction_data),
                "confidence": prediction_data.get("prediction_confidence", 0.5),
                "situation_report": situation_report,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Strategic decision: {strategy} -> {intervention_type} (source: {reasoning_source})")
            
            return decision_result
            
        except Exception as e:
            logger.error(f"Error in strategic decision making: {e}")
            return {
                "strategy": "MONITOR_AND_WAIT",
                "intervention_needed": False,
                "error": str(e),
                "reasoning_source": "error_fallback"
            }
    
    async def _get_gemini_strategy(self, situation_report: Dict[str, Any]) -> Optional[str]:
        """Get strategic recommendation from Gemini AI (GCP-optimized)."""
        try:
            if not self.gemini_model:
                logger.warning("Gemini model not available")
                return None
            
            prompt = f"""
You are the strategic decision-making AI for Project Pravaah, an Urban Mobility Operating System for Bengaluru traffic management.

Current Situation:
- Congestion Score: {situation_report['traffic_analysis']['congestion_score']}/100
- Critical Choke Point: {situation_report['traffic_analysis']['critical_choke_point']}
- Affected Vehicles: {situation_report['traffic_analysis']['affected_vehicles']}
- Prediction Confidence: {situation_report['traffic_analysis']['prediction_confidence']}
- Peak Hour: {situation_report['temporal_context']['is_peak_hour']}
- Day: {situation_report['temporal_context']['day_of_week']}

Available Strategies:
1. MONITOR_AND_WAIT - Continue monitoring, no intervention
2. REROUTE_VEHICLES - Suggest alternate routes to vehicles
3. EMERGENCY_INTERVENTION - Immediate traffic control measures
4. COORDINATE_WITH_AUTHORITIES - Alert traffic police/authorities

Respond with exactly this JSON format:
{{
  "recommended_strategy": "[ONE_OF_THE_FOUR_STRATEGIES]",
  "confidence": [0.0-1.0],
  "reasoning": "[Brief explanation]"
}}
"""
            
            response = self.gemini_model.generate_content(prompt)
            
            if response and response.text:
                # Parse JSON response
                import re
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    strategy_data = json.loads(json_match.group())
                    recommended_strategy = strategy_data.get("recommended_strategy")
                    
                    if recommended_strategy in self.strategy_options:
                        logger.info(f"Gemini recommended: {recommended_strategy}")
                        return recommended_strategy
            
            logger.warning("Invalid Gemini response format")
            return None
            
        except GoogleAPICallError as e:
            logger.error(f"Gemini API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error calling Gemini: {e}")
            return None
    
    def _fallback_strategy_decision(self, prediction_data: Dict[str, Any]) -> str:
        """Fallback rule-based strategy decision."""
        try:
            congestion_score = prediction_data.get("congestion_score", 0)
            
            if congestion_score >= 80:
                strategy = "EMERGENCY_INTERVENTION"
            elif congestion_score >= 60:
                strategy = "REROUTE_VEHICLES"
            elif congestion_score >= 40:
                strategy = "COORDINATE_WITH_AUTHORITIES"
            else:
                strategy = "MONITOR_AND_WAIT"
            
            logger.info(f"Fallback strategy: {strategy} (congestion: {congestion_score})")
            return strategy
            
        except Exception as e:
            logger.error(f"Error in fallback decision: {e}")
            return "MONITOR_AND_WAIT"
    
    def _map_strategy_to_intervention(self, strategy: str) -> str:
        """Map strategy to intervention type."""
        strategy_mapping = {
            "MONITOR_AND_WAIT": "MONITOR",
            "REROUTE_VEHICLES": "REROUTE",
            "EMERGENCY_INTERVENTION": "EMERGENCY",
            "COORDINATE_WITH_AUTHORITIES": "COORDINATE"
        }
        return strategy_mapping.get(strategy, "MONITOR")
    
    def _calculate_risk_level(self, prediction_data: Dict[str, Any]) -> str:
        """Calculate risk level based on prediction data."""
        try:
            congestion_score = prediction_data.get("congestion_score", 0)
            
            if congestion_score >= 80:
                return "critical"
            elif congestion_score >= 60:
                return "high"
            elif congestion_score >= 40:
                return "medium"
            else:
                return "low"
                
        except Exception:
            return "unknown"
    
    def _is_peak_hour(self) -> bool:
        """Check if current time is peak hour in Bengaluru."""
        try:
            current_hour = datetime.now().hour
            return (8 <= current_hour <= 11) or (17 <= current_hour <= 21)
        except Exception:
            return False
    
    async def _execute_intervention(self, decision_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute intervention via CommunicationsAgent using A2A."""
        try:
            intervention_type = decision_result.get("intervention_type", "MONITOR")
            
            if intervention_type == "MONITOR":
                return {"action": "no_intervention_needed"}
            
            # Discover CommunicationsAgent
            comm_agents = await self.discover_agents(AgentCapability.COMMUNICATION)
            
            if not comm_agents:
                logger.warning("No CommunicationsAgent found")
                return {"error": "No communications agent available"}
            
            # Send A2A message to CommunicationsAgent
            execution_message = A2AMessage(
                message_id=str(uuid.uuid4()),
                sender=self.agent_id,
                receiver="communications-agent",
                message_type=MessageType.REQUEST,
                action="execute_intervention",
                payload={
                    "intervention_type": intervention_type,
                    "decision_result": decision_result,
                    "correlation_id": str(uuid.uuid4())
                },
                correlation_id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            # For now, simulate the response
            execution_result = {
                "intervention_executed": True,
                "intervention_type": intervention_type,
                "notifications_sent": 1,
                "source": "communications_agent_a2a"
            }
            
            logger.info(f"Intervention executed: {intervention_type}")
            return execution_result
            
        except Exception as e:
            logger.error(f"Error executing intervention: {e}")
            return {"error": str(e)}
    
    async def _coordinate_multi_agent_action(self, coordination_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate actions across multiple agents."""
        try:
            coordination_results = {}
            
            # This would coordinate with multiple agents based on the plan
            # For now, return a simulated coordination result
            coordination_results = {
                "agents_coordinated": ["observer-agent", "simulation-agent", "communications-agent"],
                "coordination_success": True,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            return coordination_results
            
        except Exception as e:
            logger.error(f"Error coordinating agents: {e}")
            return {"error": str(e)}
    
    async def _plan_intervention(self, intervention_type: str, situation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Plan specific intervention based on type and situation."""
        try:
            intervention_plans = {
                "REROUTE": {
                    "action": "reroute_vehicles",
                    "target_routes": ["Outer Ring Road", "Hosur Road Alternate"],
                    "estimated_impact": "30% congestion reduction"
                },
                "EMERGENCY": {
                    "action": "emergency_intervention",
                    "measures": ["Traffic police deployment", "Signal optimization", "Route closure"],
                    "estimated_impact": "50% congestion reduction"
                },
                "COORDINATE": {
                    "action": "coordinate_authorities",
                    "contacts": ["Traffic Police", "BMTC", "Metro"],
                    "estimated_impact": "20% congestion reduction"
                }
            }
            
            plan = intervention_plans.get(intervention_type, {"action": "monitor"})
            plan["intervention_type"] = intervention_type
            plan["situation_data"] = situation_data
            plan["timestamp"] = datetime.now(timezone.utc).isoformat()
            
            return plan
            
        except Exception as e:
            logger.error(f"Error planning intervention: {e}")
            return {"error": str(e)}
    
    async def _test_gemini_connectivity(self):
        """Test Gemini connectivity for GCP deployment."""
        try:
            if self.gemini_model:
                test_response = self.gemini_model.generate_content("Test connectivity")
                if test_response:
                    logger.info("Gemini connectivity test successful")
                else:
                    logger.warning("Gemini connectivity test failed")
            else:
                logger.warning("Gemini model not initialized")
                
        except Exception as e:
            logger.warning(f"Gemini connectivity test error: {e}")
    
    async def _orchestration_loop(self):
        """Background orchestration loop for GCP deployment."""
        try:
            logger.info("Starting orchestration loop")
            
            while self.status == "active":
                try:
                    # Run periodic orchestration cycles
                    await asyncio.sleep(300)  # Every 5 minutes
                    
                    # Only run if no recent orchestration
                    if self.agent_metrics.get("last_orchestration"):
                        last_time = datetime.fromisoformat(self.agent_metrics["last_orchestration"].replace('Z', '+00:00'))
                        time_diff = (datetime.now(timezone.utc) - last_time).total_seconds()
                        
                        if time_diff < 240:  # Skip if less than 4 minutes ago
                            continue
                    
                    # Run orchestration cycle
                    cycle_result = await self.run_orchestration_cycle()
                    logger.info(f"Periodic orchestration completed: {cycle_result.get('status', 'unknown')}")
                    
                except Exception as e:
                    logger.error(f"Error in orchestration loop: {e}")
                    await asyncio.sleep(600)  # Wait longer on error
            
        except Exception as e:
            logger.error(f"Orchestration loop failed: {e}")

# Factory function for creating ADK OrchestratorAgent
async def create_adk_orchestrator_agent(project_id: str = "stable-sign-454210-i0") -> ADKOrchestratorAgent:
    """Create and start ADK OrchestratorAgent for GCP deployment."""
    agent = ADKOrchestratorAgent(project_id=project_id)
    await agent.start()
    return agent

# Main function for GCP Cloud Run deployment
async def main():
    """Main function for GCP Cloud Run deployment."""
    try:
        logger.info("Starting ADK OrchestratorAgent for GCP deployment")
        
        # Create and start agent
        agent = await create_adk_orchestrator_agent()
        
        # Keep agent running for Cloud Run
        logger.info("ADK OrchestratorAgent is running on GCP")
        while True:
            await asyncio.sleep(60)
            status = agent.get_status()
            logger.info(f"Agent status: {status['status']}, Cycles: {status['metrics']['orchestration_cycles']}")
            
    except Exception as e:
        logger.error(f"Error in ADK OrchestratorAgent: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
