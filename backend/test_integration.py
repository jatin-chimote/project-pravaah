#!/usr/bin/env python3
"""
Project Pravaah - Multi-Agent System Integration Test

This test demonstrates the complete pipeline:
Observer → Simulation → Orchestrator (with Gemini) → Communications

Perfect for hackathon demonstration!
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Set up authentication BEFORE importing agents
service_account_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
if os.path.exists(service_account_path):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(service_account_path)
    print(f"[AUTH] Authentication configured: {os.path.abspath(service_account_path)}")
else:
    print(f"[WARNING] Service account key not found at: {service_account_path}")

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all agents
from agents.observer_agent import ObserverAgent
from agents.simulation_agent import SimulationAgent
from agents.orchestrator_agent import OrchestratorAgent
from agents.communications_agent import CommunicationsAgent

# Configure logging for the test
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PravaahIntegrationTest:
    """
    Integration test suite for Project Pravaah multi-agent system.
    """
    
    def __init__(self):
        """Initialize the integration test with all agents."""
        logger.info("🚀 Initializing Project Pravaah Integration Test")
        
        # Initialize all agents
        try:
            self.observer = ObserverAgent()
            self.simulation = SimulationAgent()
            self.communications = CommunicationsAgent()
            
            # Initialize orchestrator with all dependencies
            self.orchestrator = OrchestratorAgent(
                observer_agent=self.observer,
                simulation_agent=self.simulation,
                communications_agent=self.communications
            )
            
            logger.info("✅ All agents initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize agents: {e}")
            raise
    
    def create_test_network_state(self) -> Dict[str, Any]:
        """
        Create realistic test data representing current network state.
        
        Returns:
            Mock network state with active vehicles in Bengaluru
        """
        logger.info("📊 Creating test network state with Bengaluru traffic data")
        
        # Simulate active vehicles near critical choke points
        test_vehicles = {
            "vehicle_001": {
                "vehicle_id": "vehicle_001",
                "current_location": {"lat": 12.9698, "lng": 77.7500},  # Near Marathahalli
                "destination": {"lat": 12.9716, "lng": 77.5946},       # Koramangala
                "journey_id": "journey_001",
                "estimated_arrival": (datetime.now() + timedelta(minutes=45)).isoformat(),
                "vehicle_type": "commercial",
                "last_updated": datetime.now().isoformat()
            },
            "vehicle_002": {
                "vehicle_id": "vehicle_002", 
                "current_location": {"lat": 12.9279, "lng": 77.6271},  # Near Silk Board
                "destination": {"lat": 12.9352, "lng": 77.6245},       # BTM Layout
                "journey_id": "journey_002",
                "estimated_arrival": (datetime.now() + timedelta(minutes=30)).isoformat(),
                "vehicle_type": "commercial",
                "last_updated": datetime.now().isoformat()
            },
            "vehicle_003": {
                "vehicle_id": "vehicle_003",
                "current_location": {"lat": 12.9698, "lng": 77.7500},  # Near Marathahalli
                "destination": {"lat": 12.9716, "lng": 77.5946},       # Electronic City
                "journey_id": "journey_003", 
                "estimated_arrival": (datetime.now() + timedelta(minutes=60)).isoformat(),
                "vehicle_type": "commercial",
                "last_updated": datetime.now().isoformat()
            }
        }
        
        network_state = {
            "timestamp": datetime.now().isoformat(),
            "active_vehicles": test_vehicles,
            "total_vehicle_count": len(test_vehicles),
            "network_status": "active",
            "data_source": "integration_test"
        }
        
        logger.info(f"✅ Created test network state with {len(test_vehicles)} active vehicles")
        return network_state
    
    def create_test_journeys(self) -> List[Dict[str, Any]]:
        """
        Convert network state to journey format for SimulationAgent.
        
        Returns:
            List of journey objects for congestion prediction
        """
        logger.info("🛣️ Creating test journey data for simulation")
        
        test_journeys = [
            {
                "journey_id": "journey_001",
                "vehicle_id": "vehicle_001",
                "origin": {"lat": 12.9698, "lng": 77.7500},
                "destination": {"lat": 12.9716, "lng": 77.5946},
                "planned_route": [
                    {"lat": 12.9698, "lng": 77.7500, "timestamp": datetime.now().isoformat()},
                    {"lat": 12.9352, "lng": 77.6245, "timestamp": (datetime.now() + timedelta(minutes=20)).isoformat()},
                    {"lat": 12.9716, "lng": 77.5946, "timestamp": (datetime.now() + timedelta(minutes=45)).isoformat()}
                ],
                "estimated_duration_minutes": 45,
                "vehicle_type": "commercial"
            },
            {
                "journey_id": "journey_002", 
                "vehicle_id": "vehicle_002",
                "origin": {"lat": 12.9279, "lng": 77.6271},
                "destination": {"lat": 12.9352, "lng": 77.6245},
                "planned_route": [
                    {"lat": 12.9279, "lng": 77.6271, "timestamp": datetime.now().isoformat()},
                    {"lat": 12.9352, "lng": 77.6245, "timestamp": (datetime.now() + timedelta(minutes=30)).isoformat()}
                ],
                "estimated_duration_minutes": 30,
                "vehicle_type": "commercial"
            },
            {
                "journey_id": "journey_003",
                "vehicle_id": "vehicle_003", 
                "origin": {"lat": 12.9698, "lng": 77.7500},
                "destination": {"lat": 12.8560, "lng": 77.6645},
                "planned_route": [
                    {"lat": 12.9698, "lng": 77.7500, "timestamp": datetime.now().isoformat()},
                    {"lat": 12.9279, "lng": 77.6271, "timestamp": (datetime.now() + timedelta(minutes=25)).isoformat()},
                    {"lat": 12.8560, "lng": 77.6645, "timestamp": (datetime.now() + timedelta(minutes=60)).isoformat()}
                ],
                "estimated_duration_minutes": 60,
                "vehicle_type": "commercial"
            }
        ]
        
        logger.info(f"✅ Created {len(test_journeys)} test journeys")
        return test_journeys
    
    def test_simulation_agent(self) -> Dict[str, Any]:
        """
        Test the SimulationAgent congestion prediction.
        
        Returns:
            Simulation results with congestion predictions
        """
        logger.info("🧠 Testing SimulationAgent congestion prediction")
        
        test_journeys = self.create_test_journeys()
        
        try:
            predictions = self.simulation.run_gridlock_prediction(test_journeys)
            
            logger.info("✅ SimulationAgent test completed")
            logger.info(f"   Congestion Score: {predictions.get('congestion_score', 0)}")
            logger.info(f"   Critical Choke Point: {predictions.get('choke_point_name', 'None')}")
            logger.info(f"   Affected Vehicles: {len(predictions.get('affected_vehicle_ids', []))}")
            
            return predictions
            
        except Exception as e:
            logger.error(f"❌ SimulationAgent test failed: {e}")
            raise
    
    def test_orchestrator_with_gemini(self, test_predictions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test the OrchestratorAgent with Gemini-powered decision making.
        
        Args:
            test_predictions: Predictions from SimulationAgent
            
        Returns:
            Orchestration decisions from Gemini
        """
        logger.info("🎯 Testing OrchestratorAgent with Gemini AI")
        
        try:
            # Mock the network state for orchestrator
            network_state = self.create_test_network_state()
            
            # Temporarily override the orchestrator's perception method for testing
            original_perceive = self.orchestrator._perceive_network_state
            self.orchestrator._perceive_network_state = lambda: network_state
            
            # Temporarily override the prediction method for testing
            original_predict = self.orchestrator._predict_congestion
            self.orchestrator._predict_congestion = lambda ns: test_predictions
            
            # Run the orchestration cycle
            orchestration_result = self.orchestrator.run_orchestration_cycle()
            
            # Restore original methods
            self.orchestrator._perceive_network_state = original_perceive
            self.orchestrator._predict_congestion = original_predict
            
            logger.info("✅ OrchestratorAgent test completed")
            logger.info(f"   Gemini Strategy: {orchestration_result.get('decisions', {}).get('gemini_strategy', {}).get('recommended_strategy', 'Unknown')}")
            logger.info(f"   Intervention Needed: {orchestration_result.get('decisions', {}).get('intervention_needed', False)}")
            logger.info(f"   Risk Level: {orchestration_result.get('decisions', {}).get('reasoning', {}).get('risk_level', 'Unknown')}")
            
            return orchestration_result
            
        except Exception as e:
            logger.error(f"❌ OrchestratorAgent test failed: {e}")
            raise
    
    def test_communications_agent(self, orchestration_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test the CommunicationsAgent execution and notification.
        
        Args:
            orchestration_result: Results from OrchestratorAgent
            
        Returns:
            Communications execution results
        """
        logger.info("📱 Testing CommunicationsAgent execution and notifications")
        
        try:
            # Extract decision data for communications
            decisions = orchestration_result.get('decisions', {})
            intervention_needed = decisions.get('intervention_needed', False)
            
            if intervention_needed:
                # Create payload for communications agent
                vehicles_to_reroute = decisions.get('vehicles_to_reroute', [])
                journey_id = vehicles_to_reroute[0] if vehicles_to_reroute else "journey_001"
                
                payload = {
                    "journeyId": journey_id,
                    "new_route_data": {
                        "waypoints": [
                            {"lat": 12.9698, "lng": 77.7500},
                            {"lat": 12.9716, "lng": 77.5946}
                        ],
                        "estimated_time_minutes": 40,
                        "alternative_route": True
                    },
                    "reason_for_change": f"Gemini recommended intervention due to {decisions.get('reasoning', {}).get('risk_level', 'high')} risk",
                    "correlation_id": orchestration_result.get('cycle_id', 'test_cycle')
                }
                
                # Execute reroute and notify
                comm_result = self.communications.execute_reroute_and_notify(payload)
                
                logger.info("✅ CommunicationsAgent test completed")
                logger.info(f"   Execution Status: {comm_result.get('status', 'Unknown')}")
                logger.info(f"   Journey Updated: {comm_result.get('journey_id', 'None')}")
                logger.info(f"   FCM Notification: {comm_result.get('results', {}).get('notification', {}).get('status', 'Unknown')}")
                
                return comm_result
            else:
                logger.info("✅ CommunicationsAgent test completed (no intervention needed)")
                return {"status": "no_intervention_needed", "reason": "Gemini recommended monitoring"}
                
        except Exception as e:
            logger.error(f"❌ CommunicationsAgent test failed: {e}")
            raise
    
    def run_full_integration_test(self) -> Dict[str, Any]:
        """
        Run the complete multi-agent integration test.
        
        Returns:
            Complete test results from all agents
        """
        logger.info("🎬 Starting FULL Multi-Agent Integration Test")
        logger.info("=" * 60)
        
        test_start_time = datetime.now()
        
        try:
            # Step 1: Test SimulationAgent
            logger.info("STEP 1: Testing Congestion Prediction")
            simulation_results = self.test_simulation_agent()
            
            # Step 2: Test OrchestratorAgent with Gemini
            logger.info("\nSTEP 2: Testing Gemini-Powered Orchestration")
            orchestration_results = self.test_orchestrator_with_gemini(simulation_results)
            
            # Step 3: Test CommunicationsAgent
            logger.info("\nSTEP 3: Testing Communications and Notifications")
            communications_results = self.test_communications_agent(orchestration_results)
            
            # Calculate test duration
            test_duration = (datetime.now() - test_start_time).total_seconds()
            
            # Compile final results
            final_results = {
                "test_metadata": {
                    "timestamp": test_start_time.isoformat(),
                    "duration_seconds": round(test_duration, 3),
                    "status": "SUCCESS",
                    "agents_tested": ["SimulationAgent", "OrchestratorAgent", "CommunicationsAgent"]
                },
                "simulation_results": simulation_results,
                "orchestration_results": orchestration_results,
                "communications_results": communications_results,
                "pipeline_summary": {
                    "congestion_detected": simulation_results.get('congestion_score', 0) > 50,
                    "gemini_strategy": orchestration_results.get('decisions', {}).get('gemini_strategy', {}).get('recommended_strategy', 'Unknown'),
                    "intervention_executed": communications_results.get('status') == 'success',
                    "vehicles_affected": len(simulation_results.get('affected_vehicle_ids', []))
                }
            }
            
            logger.info("=" * 60)
            logger.info("🎉 INTEGRATION TEST COMPLETED SUCCESSFULLY!")
            logger.info(f"   Total Duration: {test_duration:.3f} seconds")
            logger.info(f"   Congestion Score: {simulation_results.get('congestion_score', 0)}")
            logger.info(f"   Gemini Strategy: {orchestration_results.get('decisions', {}).get('gemini_strategy', {}).get('recommended_strategy', 'Unknown')}")
            logger.info(f"   Pipeline Status: OPERATIONAL ✅")
            logger.info("=" * 60)
            
            return final_results
            
        except Exception as e:
            test_duration = (datetime.now() - test_start_time).total_seconds()
            logger.error("=" * 60)
            logger.error(f"❌ INTEGRATION TEST FAILED after {test_duration:.3f} seconds")
            logger.error(f"   Error: {str(e)}")
            logger.error("=" * 60)
            raise

def main():
    """Main function to run the integration test."""
    try:
        # Create and run the integration test
        test_suite = PravaahIntegrationTest()
        results = test_suite.run_full_integration_test()
        
        # Save results to file for analysis
        results_file = f"integration_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"📄 Test results saved to: {results_file}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Integration test failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
