#!/usr/bin/env python3
"""
ADK-Enhanced SimulationAgent for Project Pravaah
Urban Mobility Operating System - Traffic Prediction Agent

This agent uses Google ADK with A2A protocol for standardized multi-agent coordination.
"""

import os
import json
import uuid
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional

from google.cloud import firestore
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

class ADKSimulationAgent(PravaahAgent):
    """
    ADK-Enhanced Simulation Agent for Project Pravaah
    
    Capabilities:
    - Congestion prediction at Bengaluru choke points
    - Traffic gridlock analysis and modeling
    - Journey impact assessment
    - A2A communication with other agents
    """
    
    def __init__(self, 
                 project_id: str = "stable-sign-454210-i0",
                 region: str = "asia-south1"):
        
        # Initialize ADK Agent
        super().__init__(
            agent_id="simulation-agent",
            name="Traffic Simulation Agent",
            capabilities=[
                AgentCapability.PREDICTION,
                AgentCapability.CONGESTION_PREDICTION
            ]
        )
        
        self.project_id = project_id
        self.region = region
        
        # Initialize Google Cloud services
        self.firestore_client = firestore.Client(project=project_id)
        
        # Bengaluru critical choke points
        self.choke_points = {
            "silk_board": {
                "name": "Silk Board Junction",
                "coordinates": {"lat": 12.9176, "lng": 77.6228},
                "capacity": 2000,
                "critical_threshold": 1600
            },
            "electronic_city": {
                "name": "Electronic City Toll Plaza",
                "coordinates": {"lat": 12.8456, "lng": 77.6603},
                "capacity": 1500,
                "critical_threshold": 1200
            },
            "whitefield": {
                "name": "Whitefield Main Road",
                "coordinates": {"lat": 12.9698, "lng": 77.7500},
                "capacity": 1200,
                "critical_threshold": 960
            }
        }
        
        # Agent-specific metrics
        self.agent_metrics = {
            "predictions_made": 0,
            "gridlock_alerts": 0,
            "journeys_analyzed": 0,
            "accuracy_score": 0.0,
            "last_prediction": None
        }
        
        logger.info(f"ADK SimulationAgent initialized for project: {project_id}")
        logger.info(f"Monitoring {len(self.choke_points)} critical choke points in Bengaluru")
    
    async def on_start(self):
        """ADK lifecycle hook - called when agent starts."""
        try:
            # Initialize prediction models
            await self._initialize_prediction_models()
            
            # Start background prediction loop
            asyncio.create_task(self._prediction_loop())
            
            logger.info("ADK SimulationAgent started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start ADK SimulationAgent: {e}")
            raise
    
    async def on_stop(self):
        """ADK lifecycle hook - called when agent stops."""
        try:
            logger.info("ADK SimulationAgent stopping...")
            # Cleanup resources if needed
            
        except Exception as e:
            logger.error(f"Error stopping ADK SimulationAgent: {e}")
    
    async def on_message(self, message: A2AMessage) -> Optional[Dict[str, Any]]:
        """Handle incoming A2A messages."""
        try:
            action = message.action
            payload = message.payload
            
            logger.info(f"SimulationAgent processing A2A message: {action}")
            
            if action == "predict_congestion":
                return await self._handle_predict_congestion(payload)
            
            elif action == "run_gridlock_prediction":
                return await self._handle_run_gridlock_prediction(payload)
            
            elif action == "analyze_journey_impact":
                return await self._handle_analyze_journey_impact(payload)
            
            elif action == "get_choke_point_status":
                return await self._handle_get_choke_point_status(payload)
            
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
    
    async def _handle_run_gridlock_prediction(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle gridlock prediction request via A2A."""
        try:
            journeys = payload.get("journeys", [])
            correlation_id = payload.get("correlation_id", str(uuid.uuid4()))
            
            # Run gridlock prediction analysis
            gridlock_result = await self.run_gridlock_prediction(journeys)
            
            self.agent_metrics["journeys_analyzed"] += len(journeys)
            
            if gridlock_result.get("congestion_score", 0) > 80:
                self.agent_metrics["gridlock_alerts"] += 1
            
            return {
                "success": True,
                "correlation_id": correlation_id,
                "gridlock_result": gridlock_result,
                "journeys_count": len(journeys),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent_id": self.agent_id
            }
            
        except Exception as e:
            logger.error(f"Error in gridlock prediction: {e}")
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
            "choke_points_monitored": len(self.choke_points),
            "capabilities": [cap.value for cap in self.capabilities],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": self.agent_id
        }
    
    async def run_gridlock_prediction(self, journeys: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Core gridlock prediction logic for Bengaluru choke points.
        Enhanced with ADK integration and A2A communication.
        """
        try:
            logger.info("Starting gridlock prediction analysis...")
            
            # Validate and filter journeys
            valid_journeys = await self._validate_journeys(journeys)
            logger.info(f"Validated {len(valid_journeys)} out of {len(journeys)} journeys")
            
            if not valid_journeys:
                logger.error("No valid journeys found after validation")
                return {
                    "congestion_score": 0,
                    "critical_choke_point": None,
                    "affected_vehicles": 0,
                    "prediction_confidence": 0.0,
                    "recommendations": ["No valid journey data available"],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Analyze traffic load at each choke point
            choke_point_analysis = {}
            total_congestion_score = 0
            
            for cp_id, cp_info in self.choke_points.items():
                analysis = await self._analyze_choke_point_load(cp_id, valid_journeys)
                choke_point_analysis[cp_id] = analysis
                total_congestion_score += analysis["congestion_score"]
            
            # Calculate overall congestion score
            avg_congestion_score = total_congestion_score / len(self.choke_points)
            
            # Find most critical choke point
            critical_choke_point = max(
                choke_point_analysis.items(),
                key=lambda x: x[1]["congestion_score"]
            )
            
            # Count affected vehicles
            affected_vehicles = sum(
                analysis["vehicle_count"] 
                for analysis in choke_point_analysis.values()
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                choke_point_analysis, 
                avg_congestion_score
            )
            
            # Calculate prediction confidence
            confidence = await self._calculate_prediction_confidence(
                valid_journeys, 
                choke_point_analysis
            )
            
            prediction_result = {
                "congestion_score": round(avg_congestion_score, 2),
                "critical_choke_point": critical_choke_point[0] if critical_choke_point[1]["congestion_score"] > 50 else None,
                "critical_choke_point_details": {
                    "name": self.choke_points[critical_choke_point[0]]["name"],
                    "score": critical_choke_point[1]["congestion_score"],
                    "vehicle_count": critical_choke_point[1]["vehicle_count"]
                } if critical_choke_point[1]["congestion_score"] > 50 else None,
                "affected_vehicles": affected_vehicles,
                "prediction_confidence": round(confidence, 2),
                "choke_point_analysis": choke_point_analysis,
                "recommendations": recommendations,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent_id": self.agent_id
            }
            
            logger.info(f"Gridlock prediction completed: Score={avg_congestion_score:.2f}")
            
            return prediction_result
            
        except Exception as e:
            logger.error(f"Error in gridlock prediction: {e}")
            self.agent_metrics["errors"] += 1
            raise
    
    async def _validate_journeys(self, journeys: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate journey data for prediction analysis."""
        valid_journeys = []
        
        for journey in journeys:
            try:
                # Check required fields
                if not all(key in journey for key in ["origin", "destination", "route"]):
                    continue
                
                # Validate coordinates
                origin = journey["origin"]
                destination = journey["destination"]
                
                if not self._validate_coordinates(origin) or not self._validate_coordinates(destination):
                    continue
                
                # Check if journey passes through Bengaluru area
                if not self._is_bengaluru_journey(origin, destination):
                    continue
                
                valid_journeys.append(journey)
                
            except Exception as e:
                logger.warning(f"Invalid journey data: {e}")
                continue
        
        return valid_journeys
    
    def _validate_coordinates(self, coords: Dict[str, Any]) -> bool:
        """Validate coordinate data."""
        try:
            lat = float(coords.get("lat", 0))
            lng = float(coords.get("lng", 0))
            
            # Basic coordinate validation for Bengaluru area
            return (12.5 <= lat <= 13.5) and (77.0 <= lng <= 78.0)
            
        except (ValueError, TypeError):
            return False
    
    def _is_bengaluru_journey(self, origin: Dict[str, Any], destination: Dict[str, Any]) -> bool:
        """Check if journey is within Bengaluru metropolitan area."""
        try:
            # Bengaluru bounding box
            bengaluru_bounds = {
                "north": 13.5,
                "south": 12.5,
                "east": 78.0,
                "west": 77.0
            }
            
            origin_in_bounds = (
                bengaluru_bounds["south"] <= origin["lat"] <= bengaluru_bounds["north"] and
                bengaluru_bounds["west"] <= origin["lng"] <= bengaluru_bounds["east"]
            )
            
            dest_in_bounds = (
                bengaluru_bounds["south"] <= destination["lat"] <= bengaluru_bounds["north"] and
                bengaluru_bounds["west"] <= destination["lng"] <= bengaluru_bounds["east"]
            )
            
            return origin_in_bounds or dest_in_bounds
            
        except Exception:
            return False
    
    async def _analyze_choke_point_load(self, choke_point_id: str, journeys: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze traffic load at a specific choke point."""
        try:
            choke_point = self.choke_points[choke_point_id]
            vehicles_through_point = 0
            
            # Count vehicles that would pass through this choke point
            for journey in journeys:
                if await self._journey_passes_through_choke_point(journey, choke_point):
                    vehicles_through_point += 1
            
            # Calculate congestion score
            capacity = choke_point["capacity"]
            threshold = choke_point["critical_threshold"]
            
            if vehicles_through_point >= threshold:
                congestion_score = min(100, (vehicles_through_point / capacity) * 100)
            else:
                congestion_score = (vehicles_through_point / threshold) * 50
            
            return {
                "choke_point_id": choke_point_id,
                "name": choke_point["name"],
                "vehicle_count": vehicles_through_point,
                "capacity": capacity,
                "threshold": threshold,
                "congestion_score": round(congestion_score, 2),
                "status": self._get_congestion_status(congestion_score)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing choke point {choke_point_id}: {e}")
            return {
                "choke_point_id": choke_point_id,
                "vehicle_count": 0,
                "congestion_score": 0,
                "status": "error",
                "error": str(e)
            }
    
    async def _journey_passes_through_choke_point(self, journey: Dict[str, Any], choke_point: Dict[str, Any]) -> bool:
        """Determine if a journey passes through a specific choke point."""
        try:
            origin = journey["origin"]
            destination = journey["destination"]
            cp_coords = choke_point["coordinates"]
            
            # Check if journey crosses the choke point area (simplified)
            origin_distance = self._calculate_distance(origin, cp_coords)
            dest_distance = self._calculate_distance(destination, cp_coords)
            
            # If either origin or destination is near the choke point, or
            # if the journey crosses the general area, consider it passes through
            return (origin_distance < 5.0 or dest_distance < 5.0 or 
                    self._route_crosses_area(origin, destination, cp_coords))
            
        except Exception as e:
            logger.error(f"Error checking journey route: {e}")
            return False
    
    def _calculate_distance(self, point1: Dict[str, Any], point2: Dict[str, Any]) -> float:
        """Calculate distance between two points (simplified)."""
        try:
            import math
            
            lat1, lng1 = point1["lat"], point1["lng"]
            lat2, lng2 = point2["lat"], point2["lng"]
            
            # Simplified distance calculation
            return math.sqrt((lat2 - lat1)**2 + (lng2 - lng1)**2) * 111  # Rough km conversion
            
        except Exception:
            return float('inf')
    
    def _route_crosses_area(self, origin: Dict[str, Any], destination: Dict[str, Any], choke_point: Dict[str, Any]) -> bool:
        """Check if route between origin and destination crosses choke point area."""
        try:
            # Simplified check: if choke point is roughly between origin and destination
            cp_lat, cp_lng = choke_point["lat"], choke_point["lng"]
            
            min_lat = min(origin["lat"], destination["lat"])
            max_lat = max(origin["lat"], destination["lat"])
            min_lng = min(origin["lng"], destination["lng"])
            max_lng = max(origin["lng"], destination["lng"])
            
            return (min_lat <= cp_lat <= max_lat) and (min_lng <= cp_lng <= max_lng)
            
        except Exception:
            return False
    
    def _get_congestion_status(self, congestion_score: float) -> str:
        """Get congestion status based on score."""
        if congestion_score >= 80:
            return "critical"
        elif congestion_score >= 60:
            return "high"
        elif congestion_score >= 40:
            return "medium"
        elif congestion_score >= 20:
            return "low"
        else:
            return "minimal"
    
    async def _generate_recommendations(self, choke_point_analysis: Dict[str, Any], avg_score: float) -> List[str]:
        """Generate traffic management recommendations."""
        recommendations = []
        
        try:
            if avg_score >= 80:
                recommendations.append("CRITICAL: Implement emergency traffic intervention")
                recommendations.append("Activate all available alternate routes")
                recommendations.append("Deploy traffic police at critical junctions")
            
            elif avg_score >= 60:
                recommendations.append("HIGH: Reroute vehicles to alternate paths")
                recommendations.append("Increase signal timing optimization")
            
            elif avg_score >= 40:
                recommendations.append("MEDIUM: Monitor closely and prepare interventions")
                recommendations.append("Suggest alternate routes to new journeys")
            
            else:
                recommendations.append("LOW: Continue normal monitoring")
            
            # Add specific choke point recommendations
            for cp_id, analysis in choke_point_analysis.items():
                if analysis["congestion_score"] >= 70:
                    cp_name = self.choke_points[cp_id]["name"]
                    recommendations.append(f"Priority intervention needed at {cp_name}")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append("Unable to generate specific recommendations")
        
        return recommendations
    
    async def _calculate_prediction_confidence(self, journeys: List[Dict[str, Any]], analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for the prediction."""
        try:
            # Base confidence on data quality and quantity
            data_quality_score = min(100, len(journeys) * 10)  # More journeys = higher confidence
            
            # Adjust based on analysis consistency
            scores = [cp["congestion_score"] for cp in analysis.values() if "congestion_score" in cp]
            if scores:
                score_variance = max(scores) - min(scores)
                consistency_score = max(0, 100 - score_variance)
            else:
                consistency_score = 50
            
            # Combined confidence
            confidence = (data_quality_score * 0.6 + consistency_score * 0.4) / 100
            
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5  # Default medium confidence
    
    async def _initialize_prediction_models(self):
        """Initialize prediction models and data."""
        try:
            logger.info("Initializing prediction models...")
            # In production, this would load ML models, historical data, etc.
            
        except Exception as e:
            logger.error(f"Error initializing prediction models: {e}")
    
    async def _prediction_loop(self):
        """Background loop for continuous prediction updates."""
        try:
            logger.info("Starting prediction loop")
            
            while self.status == "active":
                try:
                    # Run periodic predictions
                    await asyncio.sleep(120)  # Run every 2 minutes
                    
                except Exception as e:
                    logger.error(f"Error in prediction loop: {e}")
                    await asyncio.sleep(300)  # Wait longer on error
            
        except Exception as e:
            logger.error(f"Prediction loop failed: {e}")

# Factory function for creating ADK SimulationAgent
async def create_adk_simulation_agent(project_id: str = "stable-sign-454210-i0") -> ADKSimulationAgent:
    """Create and start ADK SimulationAgent."""
    agent = ADKSimulationAgent(project_id=project_id)
    await agent.start()
    return agent
