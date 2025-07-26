#!/usr/bin/env python3
"""
Project Pravaah - Demo Agent Classes
Simplified agent classes for local demo without Google Cloud dependencies
"""

import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class DemoObserverAgent:
    """Demo version of ObserverAgent without Google Cloud dependencies."""
    
    def __init__(self):
        self.agent_id = "demo-observer-agent"
        self.metrics = {
            "telemetry_ingested": 0,
            "network_states_captured": 0,
            "last_update": None
        }
        logger.info("✅ DemoObserverAgent initialized (no GCP dependencies)")
    
    def get_network_state(self, correlation_id: str = None) -> Dict[str, Any]:
        """Get current network state (demo simulation)."""
        try:
            # Simulate network state data
            network_state = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "correlation_id": correlation_id or str(uuid.uuid4()),
                "traffic_density": {
                    "outer_ring_road": 75,
                    "inner_ring_road": 85,
                    "mg_road": 60,
                    "brigade_road": 70,
                    "whitefield": 80
                },
                "active_journeys": 1247,
                "average_speed_kmh": 25.4,
                "congestion_hotspots": [
                    {"location": "Silk Board Junction", "severity": "high", "delay_minutes": 15},
                    {"location": "Electronic City Toll", "severity": "medium", "delay_minutes": 8},
                    {"location": "Hebbal Flyover", "severity": "medium", "delay_minutes": 12}
                ],
                "weather_impact": "clear",
                "data_source": "demo_simulation"
            }
            
            self.metrics["network_states_captured"] += 1
            self.metrics["last_update"] = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"📡 DEMO: Network state captured - {network_state['active_journeys']} active journeys")
            return network_state
            
        except Exception as e:
            logger.error(f"Error getting network state: {e}")
            return {"error": str(e), "correlation_id": correlation_id}

class DemoSimulationAgent:
    """Demo version of SimulationAgent without Google Cloud dependencies."""
    
    def __init__(self):
        self.agent_id = "demo-simulation-agent"
        self.metrics = {
            "predictions_run": 0,
            "gridlock_analyses": 0,
            "last_prediction": None
        }
        logger.info("✅ DemoSimulationAgent initialized (no GCP dependencies)")
    
    def run_gridlock_prediction(self, journeys: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run gridlock prediction analysis (demo simulation)."""
        try:
            prediction_id = str(uuid.uuid4())
            
            # Simulate gridlock prediction
            prediction_result = {
                "prediction_id": prediction_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "journeys_analyzed": len(journeys),
                "congestion_forecast": {
                    "next_30_minutes": {
                        "risk_level": "medium",
                        "congestion_score": 72,
                        "affected_routes": ["Outer Ring Road", "Sarjapur Road"]
                    },
                    "next_60_minutes": {
                        "risk_level": "high", 
                        "congestion_score": 85,
                        "affected_routes": ["Electronic City", "Whitefield", "Koramangala"]
                    }
                },
                "choke_points": [
                    {
                        "location": "Silk Board Junction",
                        "predicted_delay": "18-25 minutes",
                        "confidence": 0.87,
                        "alternative_routes": ["Hosur Road via Bommanahalli"]
                    },
                    {
                        "location": "Electronic City Toll",
                        "predicted_delay": "12-15 minutes", 
                        "confidence": 0.82,
                        "alternative_routes": ["Bannerghatta Road"]
                    }
                ],
                "recommendations": [
                    "Reroute 15% of traffic via Outer Ring Road",
                    "Implement dynamic signal timing at major junctions",
                    "Alert users about predicted congestion"
                ],
                "confidence_score": 0.84,
                "data_source": "demo_simulation"
            }
            
            self.metrics["predictions_run"] += 1
            self.metrics["gridlock_analyses"] += 1
            self.metrics["last_prediction"] = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"🧮 DEMO: Gridlock prediction completed - Risk: {prediction_result['congestion_forecast']['next_60_minutes']['risk_level']}")
            return prediction_result
            
        except Exception as e:
            logger.error(f"Error running gridlock prediction: {e}")
            return {"error": str(e), "prediction_id": prediction_id if 'prediction_id' in locals() else "unknown"}

class DemoCommunicationsAgent:
    """Demo version of CommunicationsAgent without Google Cloud dependencies."""
    
    def __init__(self):
        self.agent_id = "demo-communications-agent"
        self.metrics = {
            "executions_completed": 0,
            "notifications_sent": 0,
            "reroutes_executed": 0,
            "last_execution": None
        }
        logger.info("✅ DemoCommunicationsAgent initialized (no GCP dependencies)")
    
    def execute_reroute_and_notify(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute reroute and notification (demo simulation)."""
        try:
            execution_id = str(uuid.uuid4())
            journey_id = payload.get("journey_id", "demo_journey")
            
            # Simulate reroute execution
            execution_result = {
                "execution_id": execution_id,
                "journey_id": journey_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "reroute_applied": {
                    "original_route": "Standard route via main roads",
                    "new_route": payload.get("new_route_data", {}).get("alternate_route", "Outer Ring Road"),
                    "estimated_savings": "12-18 minutes",
                    "reason": payload.get("reason_for_change", "Traffic optimization")
                },
                "notification_sent": {
                    "method": "demo_console_log",
                    "message": f"Your journey {journey_id} has been rerouted for optimal travel time",
                    "status": "delivered"
                },
                "status": "completed",
                "data_source": "demo_simulation"
            }
            
            self.metrics["executions_completed"] += 1
            self.metrics["notifications_sent"] += 1
            self.metrics["reroutes_executed"] += 1
            self.metrics["last_execution"] = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"📱 DEMO: Reroute executed for journey {journey_id} - Savings: {execution_result['reroute_applied']['estimated_savings']}")
            return execution_result
            
        except Exception as e:
            logger.error(f"Error executing reroute: {e}")
            return {"error": str(e), "execution_id": execution_id if 'execution_id' in locals() else "unknown"}

class DemoOrchestratorAgent:
    """Demo version of OrchestratorAgent without Google Cloud dependencies."""
    
    def __init__(self, observer_agent, simulation_agent, communications_agent):
        self.agent_id = "demo-orchestrator-agent"
        self.observer_agent = observer_agent
        self.simulation_agent = simulation_agent
        self.communications_agent = communications_agent
        
        self.metrics = {
            "total_cycles": 0,
            "successful_cycles": 0,
            "failed_cycles": 0,
            "last_cycle": None,
            "gemini_calls": 0,
            "gemini_failures": 0
        }
        
        logger.info("✅ DemoOrchestratorAgent initialized with all specialist agents (no GCP dependencies)")
    
    def run_orchestration_cycle(self, cycle_id: str) -> Dict[str, Any]:
        """Run complete orchestration cycle (demo simulation)."""
        try:
            start_time = datetime.now(timezone.utc)
            logger.info(f"🎯 DEMO: Starting orchestration cycle [{cycle_id}]")
            
            # Step 1: Get network state from observer
            logger.info("📡 DEMO: Getting network state from ObserverAgent...")
            network_state = self.observer_agent.get_network_state(cycle_id)
            
            # Step 2: Run simulation analysis
            logger.info("🧮 DEMO: Running gridlock prediction with SimulationAgent...")
            demo_journeys = [
                {"id": "journey_001", "origin": {"lat": 12.9716, "lng": 77.5946}, "destination": {"lat": 12.9352, "lng": 77.6245}},
                {"id": "journey_002", "origin": {"lat": 12.9352, "lng": 77.6245}, "destination": {"lat": 12.9716, "lng": 77.5946}},
                {"id": "journey_003", "origin": {"lat": 12.9698, "lng": 77.7500}, "destination": {"lat": 12.9352, "lng": 77.6245}}
            ]
            prediction_result = self.simulation_agent.run_gridlock_prediction(demo_journeys)
            
            # Step 3: Make strategic decision (demo AI logic)
            logger.info("🤖 DEMO: Making strategic decision with AI reasoning...")
            decision_result = self._make_demo_decision(network_state, prediction_result)
            
            # Step 4: Execute interventions via communications agent
            if decision_result["strategy"] != "MONITOR_AND_WAIT":
                logger.info("📱 DEMO: Executing interventions via CommunicationsAgent...")
                for intervention in decision_result["interventions"]:
                    if intervention["type"] == "reroute":
                        reroute_result = self.communications_agent.execute_reroute_and_notify({
                            "journey_id": intervention.get("journey_id", "demo_journey"),
                            "new_route_data": {"alternate_route": "Outer Ring Road"},
                            "reason_for_change": "Predicted congestion avoidance"
                        })
                        intervention["execution_result"] = reroute_result
            
            # Complete cycle
            end_time = datetime.now(timezone.utc)
            execution_time = (end_time - start_time).total_seconds()
            
            self.metrics["total_cycles"] += 1
            self.metrics["successful_cycles"] += 1
            self.metrics["last_cycle"] = end_time.isoformat()
            
            orchestration_result = {
                "cycle_id": cycle_id,
                "status": "completed",
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "execution_time_seconds": execution_time,
                "network_state": network_state,
                "prediction_result": prediction_result,
                "decision_result": decision_result,
                "metrics": self.metrics.copy(),
                "data_source": "demo_simulation"
            }
            
            logger.info(f"🎉 DEMO: Orchestration cycle [{cycle_id}] completed successfully in {execution_time:.2f}s")
            return orchestration_result
            
        except Exception as e:
            self.metrics["total_cycles"] += 1
            self.metrics["failed_cycles"] += 1
            logger.error(f"❌ DEMO: Orchestration cycle [{cycle_id}] failed: {e}")
            
            return {
                "cycle_id": cycle_id,
                "status": "failed",
                "error": str(e),
                "metrics": self.metrics.copy(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _make_demo_decision(self, network_state: Dict[str, Any], prediction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Make strategic decision for demo (simulated AI logic)."""
        try:
            # Simulate AI decision-making logic
            congestion_score = prediction_result.get("congestion_forecast", {}).get("next_60_minutes", {}).get("congestion_score", 50)
            
            if congestion_score >= 80:
                strategy = "EMERGENCY_INTERVENTION"
                interventions = [
                    {"type": "emergency_alert", "message": "Severe congestion predicted", "priority": "high"},
                    {"type": "reroute", "journey_id": "journey_001", "alternate_route": "Outer Ring Road"}
                ]
                reasoning = "High congestion score detected, emergency intervention required"
            elif congestion_score >= 60:
                strategy = "REROUTE_VEHICLES"
                interventions = [
                    {"type": "reroute", "journey_id": "journey_001", "alternate_route": "Outer Ring Road"},
                    {"type": "reroute", "journey_id": "journey_002", "alternate_route": "Bannerghatta Road"}
                ]
                reasoning = "Medium congestion predicted, proactive rerouting recommended"
            else:
                strategy = "MONITOR_AND_WAIT"
                interventions = []
                reasoning = "Traffic conditions normal, continue monitoring"
            
            self.metrics["gemini_calls"] += 1  # Simulate AI call
            
            decision_result = {
                "strategy": strategy,
                "confidence_score": 0.87,
                "reasoning": reasoning,
                "interventions": interventions,
                "traffic_analysis": {
                    "current_congestion": congestion_score,
                    "risk_level": "high" if congestion_score >= 80 else "medium" if congestion_score >= 60 else "low",
                    "affected_areas": prediction_result.get("choke_points", [])
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "decision_source": "demo_ai_simulation"
            }
            
            logger.info(f"🤖 DEMO: Strategic decision made - Strategy: {strategy}, Confidence: {decision_result['confidence_score']}")
            return decision_result
            
        except Exception as e:
            self.metrics["gemini_failures"] += 1
            logger.error(f"Error making demo decision: {e}")
            return {
                "strategy": "MONITOR_AND_WAIT",
                "confidence_score": 0.0,
                "reasoning": f"Decision making failed: {str(e)}",
                "interventions": [],
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status for demo."""
        return {
            "agent_id": self.agent_id,
            "status": "active",
            "metrics": self.metrics.copy(),
            "specialist_agents": {
                "observer": self.observer_agent.agent_id,
                "simulation": self.simulation_agent.agent_id,
                "communications": self.communications_agent.agent_id
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "demo_mode": True
        }
