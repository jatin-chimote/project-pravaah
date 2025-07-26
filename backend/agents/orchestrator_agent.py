"""Orchestrator Agent - The "Team Lead" of Project Pravaah

This agent serves as the central brain that makes strategic decisions
based on data from the Observer and predictions from the Simulation Agent.
"""

import logging
import asyncio
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from google.cloud import firestore
import vertexai
from vertexai.generative_models import GenerativeModel

# Import other agents for coordination
from .observer_agent import ObserverAgent
from .simulation_agent import SimulationAgent
from .communications_agent import CommunicationsAgent


class OrchestratorAgent:
    """
    Orchestrator Agent responsible for strategic decision-making and coordination.
    
    This agent implements the agentic loop: Perceive → Predict → Reason → Act
    to orchestrate traffic management decisions across the multi-agent system.
    """
    
    # Configuration constants
    CRITICAL_CONGESTION_THRESHOLD = 80  # Score above which intervention is needed
    MAX_RETRIES = 3  # Maximum retries for agent communications
    ORCHESTRATION_TIMEOUT = 30  # Timeout in seconds for orchestration cycle
    
    def __init__(self, 
                 observer_agent: ObserverAgent,
                 simulation_agent: SimulationAgent,
                 communications_agent: CommunicationsAgent,
                 project_id: str = "stable-sign-454210-i0",
                 location: str = "asia-south1",
                 congestion_threshold: float = 80.0,
                 max_retries: int = 3,
                 orchestration_timeout: int = 300):
        """
        Initialize the Orchestrator Agent with dependencies.
        
        Args:
            observer_agent: Instance of ObserverAgent for network perception
            simulation_agent: Instance of SimulationAgent for predictions
            communications_agent: Instance of CommunicationsAgent for actions
            project_id: Google Cloud Project ID for Vertex AI
            location: Google Cloud region for Vertex AI
            congestion_threshold: Threshold above which intervention is triggered
            max_retries: Maximum retry attempts for failed operations
            orchestration_timeout: Timeout for orchestration cycle in seconds
        """
        self.observer = observer_agent
        self.simulation = simulation_agent
        self.communications = communications_agent
        self.project_id = project_id
        self.location = location
        self.congestion_threshold = congestion_threshold
        self.max_retries = max_retries
        self.orchestration_timeout = orchestration_timeout
        
        # Initialize Vertex AI with proper authentication
        try:
            # Set up service account authentication (same pattern as ObserverAgent)
            service_account_path = os.getenv(
                'GOOGLE_APPLICATION_CREDENTIALS', 
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'serviceAccountKey.json')
            )
            
            # Set environment variable for Vertex AI authentication
            if os.path.exists(service_account_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path
                self.logger = logging.getLogger(__name__)
                self.logger.info(f"Using service account: {service_account_path}")
            else:
                self.logger = logging.getLogger(__name__)
                self.logger.warning(f"Service account key not found at: {service_account_path}")
            
            # Initialize Vertex AI
            vertexai.init(project=self.project_id, location=self.location)
            self.gemini_model = GenerativeModel("gemini-1.5-pro")
            self.logger.info(f"Vertex AI initialized for project {self.project_id} in {self.location}")
            
        except Exception as e:
            self.logger = logging.getLogger(__name__)
            self.logger.error(f"Failed to initialize Vertex AI: {e}")
            self.gemini_model = None
        
        # Initialize logging
        self.logger.setLevel(logging.INFO)
        
        # Orchestration metrics
        self.metrics = {
            'total_cycles': 0,
            'interventions_triggered': 0,
            'avg_cycle_duration': 0.0,
            'last_intervention_time': None,
            'error_count': 0,
            'gemini_calls': 0,
            'gemini_failures': 0
        }
        
        # Current orchestration state
        self.current_state = {
            'status': 'initialized',
            'last_cycle_time': None,
            'active_interventions': [],
            'risk_level': 'low',
            'last_strategy': None
        }
        
        self.logger.info(f"OrchestratorAgent initialized for project: {project_id}")
        self.logger.info("Agent dependencies injected successfully")
    
    def _get_gemini_strategy(self, situation_report: Dict[str, Any]) -> str:
        """
        Get strategic recommendation from Gemini based on current traffic situation.
        
        Args:
            situation_report: JSON object containing current traffic analysis
            
        Returns:
            Recommended strategy string (MONITOR_AND_WAIT, REROUTE_VEHICLES, 
            EMERGENCY_INTERVENTION, or COORDINATE_WITH_AUTHORITIES)
        """
        if not self.gemini_model:
            self.logger.warning("Gemini model not available, falling back to rule-based strategy")
            return "MONITOR_AND_WAIT"
        
        try:
            self.metrics['gemini_calls'] += 1
            
            # Construct the strategic prompt for Gemini
            prompt = f"""
You are the strategic brain of Project Pravaah, an Urban Mobility Operating System for Bengaluru.

Your role: Analyze the current traffic situation and recommend the optimal intervention strategy.

Current Situation Report:
{json.dumps(situation_report, indent=2)}

Available Strategies:
1. MONITOR_AND_WAIT - Continue monitoring, no immediate action needed
2. REROUTE_VEHICLES - Suggest alternative routes to prevent congestion
3. EMERGENCY_INTERVENTION - Immediate action required, coordinate with traffic authorities
4. COORDINATE_WITH_AUTHORITIES - Work with traffic police for traffic signal optimization

Consider:
- Congestion scores at critical choke points (Marathahalli Bridge, Iblur Junction, Silk Board)
- Number of affected vehicles and their destinations
- Time of day and typical traffic patterns
- Weather conditions and special events
- Severity and urgency of the situation

Respond with ONLY a valid JSON object in this exact format:
{{
  "recommended_strategy": "STRATEGY_NAME",
  "confidence_score": 0.95,
  "reasoning": "Brief explanation of why this strategy was chosen",
  "priority_level": "HIGH|MEDIUM|LOW",
  "estimated_impact": "Expected outcome of this strategy"
}}
"""
            
            # Call Gemini for strategic recommendation
            response = self.gemini_model.generate_content(prompt)
            
            if response and response.text:
                try:
                    # Parse the JSON response
                    strategy_data = json.loads(response.text.strip())
                    recommended_strategy = strategy_data.get('recommended_strategy', 'MONITOR_AND_WAIT')
                    
                    # Log the AI decision
                    self.logger.info(f"Gemini recommendation: {recommended_strategy}")
                    self.logger.info(f"Reasoning: {strategy_data.get('reasoning', 'No reasoning provided')}")
                    self.logger.info(f"Confidence: {strategy_data.get('confidence_score', 'Unknown')}")
                    
                    # Store the strategy details for analysis
                    self.current_state['last_strategy'] = strategy_data
                    
                    return recommended_strategy
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse Gemini response as JSON: {e}")
                    self.logger.error(f"Raw response: {response.text}")
                    self.metrics['gemini_failures'] += 1
                    return "MONITOR_AND_WAIT"
            else:
                self.logger.error("Empty response from Gemini")
                self.metrics['gemini_failures'] += 1
                return "MONITOR_AND_WAIT"
                
        except Exception as e:
            self.logger.error(f"Error calling Gemini API: {e}")
            self.metrics['gemini_failures'] += 1
            
            # For hackathon demonstration: provide intelligent fallback based on situation
            congestion_score = situation_report.get('traffic_analysis', {}).get('congestion_score', 0)
            risk_level = situation_report.get('traffic_analysis', {}).get('risk_level', 'low')
            
            if congestion_score > 80 or risk_level == 'critical':
                fallback_strategy = "REROUTE_VEHICLES"
                self.logger.info(f"Gemini fallback: High congestion detected ({congestion_score}), recommending {fallback_strategy}")
            elif congestion_score > 60 or risk_level == 'high':
                fallback_strategy = "COORDINATE_WITH_AUTHORITIES"
                self.logger.info(f"Gemini fallback: Moderate congestion detected ({congestion_score}), recommending {fallback_strategy}")
            else:
                fallback_strategy = "MONITOR_AND_WAIT"
                self.logger.info(f"Gemini fallback: Low congestion detected ({congestion_score}), recommending {fallback_strategy}")
            
            # Store fallback decision for analysis
            self.current_state['last_strategy'] = {
                "recommended_strategy": fallback_strategy,
                "confidence_score": 0.75,
                "reasoning": f"Fallback decision based on congestion score {congestion_score} and risk level {risk_level}",
                "priority_level": "MEDIUM",
                "estimated_impact": "Rule-based intervention decision",
                "method": "fallback_logic"
            }
            
            return fallback_strategy
    
    def _calculate_risk_level(self, congestion_score: float) -> str:
        """
        Calculate risk level based on congestion score.
        
        Args:
            congestion_score: Numerical congestion score
            
        Returns:
            Risk level string (low, medium, high, critical)
        """
        if congestion_score >= 90:
            return "critical"
        elif congestion_score >= 75:
            return "high"
        elif congestion_score >= 50:
            return "medium"
        else:
            return "low"
    
    def _is_peak_hour(self, current_time: datetime) -> bool:
        """
        Determine if current time is during peak traffic hours for Bengaluru.
        
        Args:
            current_time: Current datetime
            
        Returns:
            True if during peak hours, False otherwise
        """
        hour = current_time.hour
        # Bengaluru peak hours: 8-11 AM and 5-9 PM
        morning_peak = 8 <= hour <= 11
        evening_peak = 17 <= hour <= 21
        return morning_peak or evening_peak
    
    def _map_strategy_to_intervention(self, strategy: str) -> str:
        """
        Map Gemini strategy recommendation to intervention type.
        
        Args:
            strategy: Strategy recommended by Gemini
            
        Returns:
            Intervention type string
        """
        strategy_mapping = {
            "MONITOR_AND_WAIT": "monitor",
            "REROUTE_VEHICLES": "reroute_vehicles",
            "EMERGENCY_INTERVENTION": "emergency_response",
            "COORDINATE_WITH_AUTHORITIES": "coordinate_authorities"
        }
        return strategy_mapping.get(strategy, "monitor")
    
    def run_orchestration_cycle(self) -> Dict[str, Any]:
        """
        Execute a complete orchestration cycle using the agentic loop.
        
        The cycle follows: Perceive → Predict → Reason & Decide → Act
        
        Returns:
            Dict containing orchestration results including:
            - Decisions made and actions taken
            - Performance metrics and timing
            - Intervention details and affected vehicles
        """
        cycle_start_time = datetime.now()
        cycle_id = f"cycle_{cycle_start_time.strftime('%Y%m%d_%H%M%S')}"
        
        self.logger.info(f"Starting orchestration cycle [{cycle_id}]")
        
        try:
            # STEP 1: PERCEIVE - Get current network state
            network_state = self._perceive_network_state()
            if not network_state or not network_state.get('active_vehicles'):
                self.logger.warning("No active vehicles detected, skipping cycle")
                return self._empty_orchestration_result(cycle_id, "no_active_vehicles")
            
            # STEP 2: PREDICT - Run congestion predictions
            predictions = self._predict_congestion(network_state)
            if not predictions:
                self.logger.error("Failed to get congestion predictions")
                return self._empty_orchestration_result(cycle_id, "prediction_failed")
            
            # STEP 3: REASON & DECIDE - Analyze predictions and make decisions
            decisions = self._reason_and_decide(predictions)
            
            # STEP 4: ACT - Execute interventions if needed
            actions_taken = self._execute_interventions(decisions)
            
            # Calculate cycle metrics
            cycle_duration = (datetime.now() - cycle_start_time).total_seconds()
            self.metrics['total_cycles'] += 1
            self.current_state['last_cycle_time'] = cycle_start_time
            
            orchestration_result = {
                "timestamp": cycle_start_time.isoformat(),
                "cycle_id": cycle_id,
                "status": "completed",
                "decisions": decisions,
                "actions_taken": actions_taken,
                "network_analysis": {
                    "active_vehicles_count": len(network_state.get('active_vehicles', {})),
                    "highest_risk_choke_point": predictions.get('choke_point_name'),
                    "max_congestion_score": predictions.get('congestion_score', 0),
                    "affected_vehicles_count": len(predictions.get('affected_vehicle_ids', []))
                },
                "performance_metrics": {
                    "cycle_duration_seconds": round(cycle_duration, 3),
                    "total_cycles_completed": self.metrics['total_cycles'],
                    "total_interventions_executed": self.metrics['interventions_triggered'],
                    "intervention_rate": round(self.metrics['interventions_triggered'] / max(1, self.metrics['total_cycles']), 3)
                }
            }
            
            self.logger.info(
                f"Orchestration cycle [{cycle_id}] completed in {cycle_duration:.3f}s. "
                f"Actions taken: {len(actions_taken.get('interventions', []))}"
            )
            
            return orchestration_result
            
        except Exception as e:
            self.logger.error(f"Error in orchestration cycle [{cycle_id}]: {e}")
            return self._empty_orchestration_result(cycle_id, f"error: {str(e)}")
    
    def _perceive_network_state(self) -> Optional[Dict[str, Any]]:
        """
        PERCEIVE: Get current network state from ObserverAgent.
        
        Returns:
            Network state data or None if failed
        """
        try:
            self.logger.debug("Perceiving network state...")
            network_state = self.observer.get_network_state()
            
            active_vehicles_count = len(network_state.get('active_vehicles', {}))
            self.logger.info(f"Perceived {active_vehicles_count} active vehicles")
            
            return network_state
            
        except Exception as e:
            self.logger.error(f"Failed to perceive network state: {e}")
            return None
    
    def _predict_congestion(self, network_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        PREDICT: Run congestion predictions using SimulationAgent.
        
        Args:
            network_state: Current network state from perception
            
        Returns:
            Congestion predictions or None if failed
        """
        try:
            self.logger.debug("Running congestion predictions...")
            
            # Convert network state to journey format expected by SimulationAgent
            active_journeys = self._convert_to_journey_format(network_state)
            
            if not active_journeys:
                self.logger.warning("No valid journeys found for prediction")
                return None
            
            predictions = self.simulator.run_gridlock_prediction(active_journeys)
            
            self.logger.info(
                f"Predictions complete: {predictions.get('choke_point_name', 'None')} "
                f"(score: {predictions.get('congestion_score', 0)})"
            )
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Failed to predict congestion: {e}")
            return None
    
    def _reason_and_decide(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """
        REASON & DECIDE: Analyze predictions and make intervention decisions using Gemini AI.
        
        Args:
            predictions: Congestion predictions from SimulationAgent
            
        Returns:
            Dictionary of decisions and reasoning
        """
        congestion_score = predictions.get('congestion_score', 0)
        affected_vehicles = predictions.get('affected_vehicle_ids', [])
        choke_point_name = predictions.get('choke_point_name')
        
        # Create situation report for Gemini analysis
        current_time = datetime.now()
        situation_report = {
            "timestamp": current_time.isoformat(),
            "traffic_analysis": {
                "primary_choke_point": choke_point_name,
                "congestion_score": congestion_score,
                "affected_vehicle_count": len(affected_vehicles),
                "affected_vehicle_ids": affected_vehicles[:10],
                "risk_level": self._calculate_risk_level(congestion_score)
            },
            "temporal_context": {
                "hour_of_day": current_time.hour,
                "day_of_week": current_time.strftime("%A"),
                "is_peak_hour": self._is_peak_hour(current_time),
                "is_weekend": current_time.weekday() >= 5
            },
            "system_state": {
                "total_cycles_completed": self.metrics['total_cycles'],
                "recent_interventions": self.metrics['interventions_triggered'],
                "system_load": "normal"
            }
        }
        
        # Get strategic recommendation from Gemini
        recommended_strategy = self._get_gemini_strategy(situation_report)
        
        # Map Gemini strategy to intervention decisions
        intervention_needed = recommended_strategy in ["REROUTE_VEHICLES", "EMERGENCY_INTERVENTION", "COORDINATE_WITH_AUTHORITIES"]
        
        # Determine intervention type based on strategy
        intervention_type = self._map_strategy_to_intervention(recommended_strategy)
        
        # Fallback to rule-based decision if needed
        if recommended_strategy == "MONITOR_AND_WAIT" and congestion_score > self.congestion_threshold:
            intervention_needed = True
            intervention_type = "reroute_vehicles"
        
        decisions = {
            "intervention_needed": intervention_needed,
            "congestion_score": congestion_score,
            "threshold_used": self.congestion_threshold,
            "affected_choke_point": choke_point_name,
            "vehicles_to_reroute": affected_vehicles if intervention_needed else [],
            "gemini_strategy": {
                "recommended_strategy": recommended_strategy,
                "intervention_type": intervention_type,
                "ai_reasoning": self.current_state.get('last_strategy', {}),
                "situation_report": situation_report
            },
            "reasoning": {
                "decision_method": "gemini_ai_enhanced",
                "decision_factors": [
                    f"Gemini recommendation: {recommended_strategy}",
                    f"Congestion score: {congestion_score}",
                    f"Risk level: {situation_report['traffic_analysis']['risk_level']}",
                    f"Peak hour: {situation_report['temporal_context']['is_peak_hour']}",
                    f"Affected vehicles: {len(affected_vehicles)}",
                    f"Critical choke point: {choke_point_name}"
                ],
                "risk_level": situation_report['traffic_analysis']['risk_level'],
                "intervention_type": intervention_type,
                "temporal_context": situation_report['temporal_context']
            }
        }
        
        # Update current state with decision
        self.current_state['risk_level'] = situation_report['traffic_analysis']['risk_level']
        if intervention_needed:
            self.current_state['active_interventions'].append({
                "strategy": recommended_strategy,
                "intervention_type": intervention_type,
                "timestamp": current_time.isoformat(),
                "affected_vehicles": len(affected_vehicles)
            })
        
        self.logger.info(
            f"Gemini Decision: {recommended_strategy} -> {'INTERVENE' if intervention_needed else 'MONITOR'} "
            f"(score: {congestion_score}, risk: {situation_report['traffic_analysis']['risk_level']})"
        )
        
        return decisions
    
    def _execute_interventions(self, decisions: Dict[str, Any]) -> Dict[str, Any]:
        """
        ACT: Execute interventions using CommunicationsAgent.
        
        Args:
            decisions: Decisions from reasoning phase
            
        Returns:
            Dictionary of actions taken and results
        """
        actions_taken = {
            "interventions": [],
            "notifications_sent": [],
            "errors": []
        }
        
        if not decisions.get('intervention_needed', False):
            self.logger.info("No intervention needed, monitoring continues")
            return actions_taken
        
        vehicles_to_reroute = decisions.get('vehicles_to_reroute', [])
        
        if not vehicles_to_reroute:
            self.logger.warning("Intervention needed but no vehicles to reroute")
            return actions_taken
        
        try:
            # Prepare orchestration decisions for CommunicationsAgent
            orchestration_decisions = {
                "decisions": {
                    "fleet_routing_commands": [
                        {
                            "vehicle_id": vehicle_id,
                            "action": "reroute",
                            "reason": f"Avoid congestion at {decisions.get('affected_choke_point')}",
                            "priority": "high",
                            "timestamp": datetime.now().isoformat()
                        }
                        for vehicle_id in vehicles_to_reroute
                    ]
                },
                "metadata": {
                    "congestion_score": decisions.get('congestion_score'),
                    "affected_choke_point": decisions.get('affected_choke_point'),
                    "intervention_type": "proactive_congestion_avoidance"
                }
            }
            
            # Execute rerouting and notifications
            self.logger.info(f"Executing interventions for {len(vehicles_to_reroute)} vehicles")
            execution_result = self.communicator.execute_reroute_and_notify(orchestration_decisions)
            
            # Track successful interventions
            if execution_result.get('results', {}).get('routes_updated'):
                self.interventions_executed += len(vehicles_to_reroute)
                actions_taken['interventions'] = vehicles_to_reroute
                actions_taken['notifications_sent'] = execution_result.get('results', {}).get('notifications_sent', [])
            
            self.logger.info(f"Interventions executed successfully for {len(vehicles_to_reroute)} vehicles")
            
        except Exception as e:
            error_msg = f"Failed to execute interventions: {e}"
            self.logger.error(error_msg)
            actions_taken['errors'].append(error_msg)
        
        return actions_taken
    
    def _convert_to_journey_format(self, network_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert network state to journey format expected by SimulationAgent.
        
        Args:
            network_state: Network state from ObserverAgent
            
        Returns:
            List of journey objects
        """
        journeys = []
        active_vehicles = network_state.get('active_vehicles', {})
        
        for vehicle_id, vehicle_data in active_vehicles.items():
            try:
                location = vehicle_data.get('location', {})
                
                # Create a simple journey with current location as both start and destination
                # In a real system, this would come from route planning data
                journey = {
                    'vehicle_id': vehicle_id,
                    'current_location': {
                        'lat': location.get('latitude'),
                        'lng': location.get('longitude')
                    },
                    'destination': {
                        'lat': location.get('latitude', 0) + 0.01,  # Simple offset for demo
                        'lng': location.get('longitude', 0) + 0.01
                    },
                    'route_points': [
                        {
                            'lat': location.get('latitude'),
                            'lng': location.get('longitude')
                        }
                        # In reality, this would contain the full planned route
                    ]
                }
                
                journeys.append(journey)
                
            except Exception as e:
                self.logger.warning(f"Failed to convert vehicle {vehicle_id} to journey format: {e}")
                continue
        
        return journeys
    
    def _calculate_risk_level(self, congestion_score: float) -> str:
        """
        Calculate risk level based on congestion score.
        
        Args:
            congestion_score: Numerical congestion score
            
        Returns:
            Risk level string
        """
        if congestion_score >= 100:
            return "critical"
        elif congestion_score >= self.CRITICAL_CONGESTION_THRESHOLD:
            return "high"
        elif congestion_score >= 50:
            return "medium"
        else:
            return "low"
    
    def _empty_orchestration_result(self, cycle_id: str, reason: str) -> Dict[str, Any]:
        """
        Return an empty orchestration result for error/skip cases.
        
        Args:
            cycle_id: Cycle identifier
            reason: Reason for empty result
            
        Returns:
            Empty orchestration result
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "cycle_id": cycle_id,
            "status": "skipped",
            "reason": reason,
            "decisions": {},
            "actions_taken": {},
            "network_analysis": {},
            "performance_metrics": {
                "cycle_duration_seconds": 0,
                "total_cycles_completed": self.cycles_completed,
                "total_interventions_executed": self.interventions_executed
            }
        }
    
    def get_orchestration_status(self) -> Dict[str, Any]:
        """
        Get current status and metrics of the orchestration system.
        
        Returns:
            Status dictionary with metrics and health information
        """
        return {
            "status": "active",
            "project_id": self.project_id,
            "metrics": {
                "cycles_completed": self.cycles_completed,
                "interventions_executed": self.interventions_executed,
                "intervention_rate": round(self.interventions_executed / max(1, self.cycles_completed), 3),
                "last_cycle_time": self.last_cycle_time.isoformat() if self.last_cycle_time else None
            },
            "configuration": {
                "critical_threshold": self.CRITICAL_CONGESTION_THRESHOLD,
                "max_retries": self.MAX_RETRIES,
                "orchestration_timeout": self.ORCHESTRATION_TIMEOUT
            },
            "timestamp": datetime.now().isoformat()
        }
