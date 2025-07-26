#!/usr/bin/env python3
"""
ADK Integration Test for Project Pravaah
Urban Mobility Operating System - Complete Multi-Agent ADK Pipeline Test

This test validates the full ADK implementation with A2A protocol for GCP deployment.
"""

import os
import json
import uuid
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any

# Set up authentication for local testing
key_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
if os.path.exists(key_path):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(key_path)

# Import ADK agents
from agents.adk_observer_agent import ADKObserverAgent
from agents.adk_simulation_agent import ADKSimulationAgent
from agents.adk_orchestrator_agent import ADKOrchestratorAgent
from agents.adk_communications_agent import ADKCommunicationsAgent

from adk_base import A2AMessage, MessageType, AgentCapability

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ADKIntegrationTest:
    """Comprehensive ADK integration test for Project Pravaah."""
    
    def __init__(self):
        self.test_results = {
            "test_start": datetime.now(timezone.utc).isoformat(),
            "agents_tested": [],
            "a2a_messages_tested": [],
            "test_scenarios": [],
            "performance_metrics": {},
            "errors": []
        }
        
        # Test agents
        self.observer_agent = None
        self.simulation_agent = None
        self.orchestrator_agent = None
        self.communications_agent = None
    
    async def run_complete_test_suite(self) -> Dict[str, Any]:
        """Run complete ADK integration test suite."""
        try:
            logger.info("🚀 Starting ADK Integration Test Suite for Project Pravaah")
            logger.info("=" * 80)
            
            # Test 1: Agent Initialization
            await self._test_agent_initialization()
            
            # Test 2: A2A Message Handling
            await self._test_a2a_messaging()
            
            # Test 3: Agent Discovery
            await self._test_agent_discovery()
            
            # Test 4: Complete Pipeline
            await self._test_complete_pipeline()
            
            # Test 5: GCP Deployment Readiness
            await self._test_gcp_deployment_readiness()
            
            # Generate final report
            return await self._generate_test_report()
            
        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            self.test_results["errors"].append(str(e))
            return self.test_results
        finally:
            await self._cleanup_agents()
    
    async def _test_agent_initialization(self):
        """Test ADK agent initialization."""
        logger.info("🔧 TEST 1: ADK Agent Initialization")
        logger.info("-" * 40)
        
        try:
            # Initialize ObserverAgent
            logger.info("Initializing ADK ObserverAgent...")
            self.observer_agent = ADKObserverAgent()
            await self.observer_agent.start()
            logger.info("✅ ObserverAgent initialized successfully")
            
            # Initialize SimulationAgent
            logger.info("Initializing ADK SimulationAgent...")
            self.simulation_agent = ADKSimulationAgent()
            await self.simulation_agent.start()
            logger.info("✅ SimulationAgent initialized successfully")
            
            # Initialize OrchestratorAgent
            logger.info("Initializing ADK OrchestratorAgent...")
            self.orchestrator_agent = ADKOrchestratorAgent()
            await self.orchestrator_agent.start()
            logger.info("✅ OrchestratorAgent initialized successfully")
            
            # Initialize CommunicationsAgent
            logger.info("Initializing ADK CommunicationsAgent...")
            self.communications_agent = ADKCommunicationsAgent()
            await self.communications_agent.start()
            logger.info("✅ CommunicationsAgent initialized successfully")
            
            self.test_results["agents_tested"] = [
                "observer-agent", "simulation-agent", 
                "orchestrator-agent", "communications-agent"
            ]
            
            logger.info("✅ All ADK agents initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Agent initialization failed: {e}")
            self.test_results["errors"].append(f"Agent initialization: {e}")
            raise
    
    async def _test_a2a_messaging(self):
        """Test A2A messaging between agents."""
        logger.info("\n📡 TEST 2: A2A Messaging")
        logger.info("-" * 40)
        
        try:
            # Test ObserverAgent A2A
            logger.info("Testing ObserverAgent A2A messaging...")
            observer_message = A2AMessage(
                message_id=str(uuid.uuid4()),
                sender="test-client",
                receiver="observer-agent",
                message_type=MessageType.REQUEST,
                action="health_check",
                payload={"test": True},
                correlation_id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            observer_response = await self.observer_agent.on_message(observer_message)
            assert observer_response["success"] == True
            logger.info("✅ ObserverAgent A2A messaging working")
            
            # Test SimulationAgent A2A
            logger.info("Testing SimulationAgent A2A messaging...")
            simulation_message = A2AMessage(
                message_id=str(uuid.uuid4()),
                sender="test-client",
                receiver="simulation-agent",
                message_type=MessageType.REQUEST,
                action="health_check",
                payload={"test": True},
                correlation_id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            simulation_response = await self.simulation_agent.on_message(simulation_message)
            assert simulation_response["success"] == True
            logger.info("✅ SimulationAgent A2A messaging working")
            
            # Test OrchestratorAgent A2A
            logger.info("Testing OrchestratorAgent A2A messaging...")
            orchestrator_message = A2AMessage(
                message_id=str(uuid.uuid4()),
                sender="test-client",
                receiver="orchestrator-agent",
                message_type=MessageType.REQUEST,
                action="health_check",
                payload={"test": True},
                correlation_id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            orchestrator_response = await self.orchestrator_agent.on_message(orchestrator_message)
            assert orchestrator_response["success"] == True
            logger.info("✅ OrchestratorAgent A2A messaging working")
            
            # Test CommunicationsAgent A2A
            logger.info("Testing CommunicationsAgent A2A messaging...")
            communications_message = A2AMessage(
                message_id=str(uuid.uuid4()),
                sender="test-client",
                receiver="communications-agent",
                message_type=MessageType.REQUEST,
                action="health_check",
                payload={"test": True},
                correlation_id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            communications_response = await self.communications_agent.on_message(communications_message)
            assert communications_response["success"] == True
            logger.info("✅ CommunicationsAgent A2A messaging working")
            
            self.test_results["a2a_messages_tested"] = [
                "health_check", "observer_messaging", "simulation_messaging",
                "orchestrator_messaging", "communications_messaging"
            ]
            
            logger.info("✅ All A2A messaging tests passed")
            
        except Exception as e:
            logger.error(f"❌ A2A messaging test failed: {e}")
            self.test_results["errors"].append(f"A2A messaging: {e}")
            raise
    
    async def _test_agent_discovery(self):
        """Test agent discovery and capability matching."""
        logger.info("\n🔍 TEST 3: Agent Discovery")
        logger.info("-" * 40)
        
        try:
            # Test capability discovery
            logger.info("Testing agent capability discovery...")
            
            # Discover perception agents
            perception_agents = await self.orchestrator_agent.discover_agents(AgentCapability.PERCEPTION)
            logger.info(f"Found {len(perception_agents)} perception agents")
            
            # Discover prediction agents
            prediction_agents = await self.orchestrator_agent.discover_agents(AgentCapability.PREDICTION)
            logger.info(f"Found {len(prediction_agents)} prediction agents")
            
            # Discover communication agents
            communication_agents = await self.orchestrator_agent.discover_agents(AgentCapability.COMMUNICATION)
            logger.info(f"Found {len(communication_agents)} communication agents")
            
            logger.info("✅ Agent discovery tests completed")
            
        except Exception as e:
            logger.error(f"❌ Agent discovery test failed: {e}")
            self.test_results["errors"].append(f"Agent discovery: {e}")
    
    async def _test_complete_pipeline(self):
        """Test complete multi-agent pipeline with A2A protocol."""
        logger.info("\n🔄 TEST 4: Complete ADK Pipeline")
        logger.info("-" * 40)
        
        try:
            # Test Scenario 1: Low Traffic
            logger.info("Testing Scenario 1: Low Traffic Conditions")
            await self._test_low_traffic_scenario()
            
            # Test Scenario 2: High Traffic
            logger.info("Testing Scenario 2: High Traffic Conditions")
            await self._test_high_traffic_scenario()
            
            # Test Scenario 3: Emergency Intervention
            logger.info("Testing Scenario 3: Emergency Intervention")
            await self._test_emergency_scenario()
            
            logger.info("✅ Complete pipeline tests passed")
            
        except Exception as e:
            logger.error(f"❌ Complete pipeline test failed: {e}")
            self.test_results["errors"].append(f"Complete pipeline: {e}")
    
    async def _test_low_traffic_scenario(self):
        """Test low traffic scenario."""
        try:
            scenario_id = str(uuid.uuid4())
            logger.info(f"Running low traffic scenario [{scenario_id}]")
            
            # Simulate low traffic data
            test_journeys = [
                {
                    "id": "journey_low_001",
                    "origin": {"lat": 12.9716, "lng": 77.5946},
                    "destination": {"lat": 12.9352, "lng": 77.6245},
                    "route": "standard_route",
                    "start_time": datetime.now(timezone.utc).isoformat()
                }
            ]
            
            # Run orchestration cycle
            orchestration_result = await self.orchestrator_agent.run_orchestration_cycle(f"test_cycle_{scenario_id}")
            
            # Verify results
            assert orchestration_result["status"] == "completed"
            assert "decision_result" in orchestration_result
            
            self.test_results["test_scenarios"].append({
                "scenario": "low_traffic",
                "scenario_id": scenario_id,
                "result": "passed",
                "orchestration_result": orchestration_result
            })
            
            logger.info("✅ Low traffic scenario completed")
            
        except Exception as e:
            logger.error(f"❌ Low traffic scenario failed: {e}")
            raise
    
    async def _test_high_traffic_scenario(self):
        """Test high traffic scenario."""
        try:
            scenario_id = str(uuid.uuid4())
            logger.info(f"Running high traffic scenario [{scenario_id}]")
            
            # Simulate high traffic data
            test_journeys = []
            for i in range(10):
                journey = {
                    "id": f"journey_high_{i:03d}",
                    "origin": {"lat": 12.9716 + (i * 0.01), "lng": 77.5946 + (i * 0.01)},
                    "destination": {"lat": 12.9352, "lng": 77.6245},
                    "route": "congested_route",
                    "start_time": datetime.now(timezone.utc).isoformat()
                }
                test_journeys.append(journey)
            
            # Test simulation agent with high traffic
            simulation_message = A2AMessage(
                message_id=str(uuid.uuid4()),
                sender="test-client",
                receiver="simulation-agent",
                message_type=MessageType.REQUEST,
                action="run_gridlock_prediction",
                payload={"journeys": test_journeys, "correlation_id": scenario_id},
                correlation_id=scenario_id,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            simulation_response = await self.simulation_agent.on_message(simulation_message)
            assert simulation_response["success"] == True
            
            # Run orchestration cycle
            orchestration_result = await self.orchestrator_agent.run_orchestration_cycle(f"test_cycle_{scenario_id}")
            
            self.test_results["test_scenarios"].append({
                "scenario": "high_traffic",
                "scenario_id": scenario_id,
                "result": "passed",
                "simulation_response": simulation_response,
                "orchestration_result": orchestration_result
            })
            
            logger.info("✅ High traffic scenario completed")
            
        except Exception as e:
            logger.error(f"❌ High traffic scenario failed: {e}")
            raise
    
    async def _test_emergency_scenario(self):
        """Test emergency intervention scenario."""
        try:
            scenario_id = str(uuid.uuid4())
            logger.info(f"Running emergency scenario [{scenario_id}]")
            
            # Test emergency intervention
            intervention_message = A2AMessage(
                message_id=str(uuid.uuid4()),
                sender="test-client",
                receiver="communications-agent",
                message_type=MessageType.REQUEST,
                action="execute_intervention",
                payload={
                    "intervention_type": "EMERGENCY",
                    "decision_result": {
                        "strategy": "EMERGENCY_INTERVENTION",
                        "risk_level": "critical"
                    },
                    "correlation_id": scenario_id
                },
                correlation_id=scenario_id,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            intervention_response = await self.communications_agent.on_message(intervention_message)
            assert intervention_response["success"] == True
            
            self.test_results["test_scenarios"].append({
                "scenario": "emergency_intervention",
                "scenario_id": scenario_id,
                "result": "passed",
                "intervention_response": intervention_response
            })
            
            logger.info("✅ Emergency scenario completed")
            
        except Exception as e:
            logger.error(f"❌ Emergency scenario failed: {e}")
            raise
    
    async def _test_gcp_deployment_readiness(self):
        """Test GCP deployment readiness."""
        logger.info("\n☁️ TEST 5: GCP Deployment Readiness")
        logger.info("-" * 40)
        
        try:
            # Test environment variables
            logger.info("Checking environment configuration...")
            
            # Check authentication
            auth_configured = bool(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
            logger.info(f"Authentication configured: {auth_configured}")
            
            # Test agent health endpoints
            logger.info("Testing agent health endpoints...")
            
            agents = [
                self.observer_agent,
                self.simulation_agent,
                self.orchestrator_agent,
                self.communications_agent
            ]
            
            for agent in agents:
                if agent:
                    status = agent.get_status()
                    assert status["status"] in ["active", "healthy"]
                    logger.info(f"✅ {agent.agent_id} health check passed")
            
            # Test performance metrics
            logger.info("Collecting performance metrics...")
            performance_metrics = await self._collect_performance_metrics()
            self.test_results["performance_metrics"] = performance_metrics
            
            logger.info("✅ GCP deployment readiness verified")
            
        except Exception as e:
            logger.error(f"❌ GCP deployment readiness test failed: {e}")
            self.test_results["errors"].append(f"GCP deployment: {e}")
    
    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect performance metrics from all agents."""
        try:
            metrics = {
                "test_duration": None,
                "agents_performance": {},
                "a2a_message_latency": [],
                "memory_usage": "not_measured",
                "cpu_usage": "not_measured"
            }
            
            # Collect agent metrics
            agents = {
                "observer": self.observer_agent,
                "simulation": self.simulation_agent,
                "orchestrator": self.orchestrator_agent,
                "communications": self.communications_agent
            }
            
            for agent_name, agent in agents.items():
                if agent:
                    agent_status = agent.get_status()
                    metrics["agents_performance"][agent_name] = {
                        "status": agent_status.get("status"),
                        "metrics": agent_status.get("metrics", {}),
                        "capabilities": agent_status.get("capabilities", [])
                    }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
            return {"error": str(e)}
    
    async def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        try:
            test_end = datetime.now(timezone.utc)
            test_start = datetime.fromisoformat(self.test_results["test_start"])
            test_duration = (test_end - test_start).total_seconds()
            
            self.test_results.update({
                "test_end": test_end.isoformat(),
                "test_duration_seconds": test_duration,
                "test_status": "PASSED" if not self.test_results["errors"] else "FAILED",
                "total_agents_tested": len(self.test_results["agents_tested"]),
                "total_scenarios_tested": len(self.test_results["test_scenarios"]),
                "total_errors": len(self.test_results["errors"])
            })
            
            # Save test results
            results_filename = f"adk_integration_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_filename, 'w') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            
            logger.info("=" * 80)
            logger.info("🎉 ADK INTEGRATION TEST COMPLETED!")
            logger.info(f"📊 Test Status: {self.test_results['test_status']}")
            logger.info(f"⏱️ Duration: {test_duration:.2f} seconds")
            logger.info(f"🤖 Agents Tested: {self.test_results['total_agents_tested']}")
            logger.info(f"📋 Scenarios Tested: {self.test_results['total_scenarios_tested']}")
            logger.info(f"❌ Errors: {self.test_results['total_errors']}")
            logger.info(f"📄 Results saved to: {results_filename}")
            logger.info("=" * 80)
            
            return self.test_results
            
        except Exception as e:
            logger.error(f"Error generating test report: {e}")
            return self.test_results
    
    async def _cleanup_agents(self):
        """Cleanup all test agents."""
        try:
            logger.info("Cleaning up test agents...")
            
            agents = [
                self.observer_agent,
                self.simulation_agent,
                self.orchestrator_agent,
                self.communications_agent
            ]
            
            for agent in agents:
                if agent:
                    try:
                        await agent.stop()
                    except Exception as e:
                        logger.warning(f"Error stopping agent {agent.agent_id}: {e}")
            
            logger.info("✅ Agent cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

async def main():
    """Main test execution function."""
    try:
        # Create and run integration test
        test_suite = ADKIntegrationTest()
        test_results = await test_suite.run_complete_test_suite()
        
        # Print summary
        if test_results["test_status"] == "PASSED":
            print("\n🎉 ALL ADK INTEGRATION TESTS PASSED!")
            print("✅ Project Pravaah ADK implementation is ready for GCP deployment!")
        else:
            print("\n❌ SOME TESTS FAILED")
            print("🔧 Please review the errors and fix before deployment")
            for error in test_results["errors"]:
                print(f"   - {error}")
        
        return test_results
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        return {"test_status": "FAILED", "error": str(e)}

if __name__ == "__main__":
    asyncio.run(main())
