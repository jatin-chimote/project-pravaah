"""Simulation Agent - The "Data Scientist" of Project Pravaah

This agent runs predictive simulations to forecast future gridlock
and traffic congestion patterns in the urban mobility network.
"""

import math
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
from google.cloud import firestore


class SimulationAgent:
    """
    Simulation Agent responsible for predictive traffic modeling and gridlock forecasting.
    
    This agent analyzes journey data to predict future traffic conditions
    and identify potential congestion hotspots at critical Bengaluru choke points.
    """
    
    # Critical Bengaluru choke points for congestion monitoring
    CHOKE_POINTS = {
        "marathahalli_bridge": {
            "name": "Marathahalli Bridge",
            "lat": 12.9592,
            "lng": 77.6974,
            "radius_meters": 400
        },
        "iblur_junction": {
            "name": "Iblur Junction",
            "lat": 12.9284,
            "lng": 77.6754,
            "radius_meters": 500
        },
        "silk_board_junction": {
            "name": "Silk Board Junction",
            "lat": 12.9176,
            "lng": 77.6237,
            "radius_meters": 600
        }
    }
    
    def __init__(self, project_id: str = "stable-sign-454210-i0"):
        """
        Initialize the Simulation Agent.
        
        Args:
            project_id: Google Cloud Project ID
        """
        self.project_id = project_id
        self.db = firestore.Client(project=project_id)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        self.logger.info(f"SimulationAgent initialized for project: {project_id}")
        self.logger.info(f"Monitoring {len(self.CHOKE_POINTS)} critical choke points in Bengaluru")
    
    def run_gridlock_prediction(self, 
                               active_journeys: List[Dict[str, Any]],
                               active_events: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run predictive simulation to forecast potential gridlock scenarios.
        
        Args:
            active_journeys: List of active vehicle journeys with route data
            active_events: Dictionary of active traffic events (optional)
            
        Returns:
            Dict containing gridlock prediction results:
            - choke_point_name: Name of the highest risk choke point
            - congestion_score: Numerical score indicating congestion level
            - affected_vehicle_ids: List of vehicle IDs predicted to be affected
        """
        start_time = datetime.now()
        self.logger.info("Starting gridlock prediction analysis...")
        
        if not active_journeys:
            self.logger.warning("No active journeys provided for prediction")
            return self._empty_prediction_result()
        
        try:
            # Validate input data
            validated_journeys = self._validate_journey_data(active_journeys)
            if not validated_journeys:
                self.logger.error("No valid journeys found after validation")
                return self._empty_prediction_result()
            
            # Initialize congestion scores for each choke point
            congestion_scores = {key: 0 for key in self.CHOKE_POINTS.keys()}
            affected_vehicles = {key: [] for key in self.CHOKE_POINTS.keys()}
            
            # Analyze each journey for potential choke point impact
            for journey in validated_journeys:
                self._analyze_journey_impact(
                    journey, 
                    congestion_scores, 
                    affected_vehicles
                )
            
            # Find the choke point with highest congestion risk
            hotspot_key = max(congestion_scores, key=congestion_scores.get)
            hotspot_score = congestion_scores[hotspot_key]
            hotspot_name = self.CHOKE_POINTS[hotspot_key]["name"]
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            prediction_result = {
                "timestamp": datetime.now().isoformat(),
                "choke_point_name": hotspot_name,
                "congestion_score": hotspot_score,
                "affected_vehicle_ids": affected_vehicles[hotspot_key],
                "all_choke_points": {
                    self.CHOKE_POINTS[key]["name"]: {
                        "score": congestion_scores[key],
                        "affected_vehicles": len(affected_vehicles[key])
                    }
                    for key in self.CHOKE_POINTS.keys()
                },
                "simulation_metadata": {
                    "total_journeys_analyzed": len(validated_journeys),
                    "prediction_horizon_minutes": 60,
                    "processing_time_ms": round(processing_time, 2),
                    "model_version": "1.0",
                    "choke_points_monitored": len(self.CHOKE_POINTS)
                }
            }
            
            self.logger.info(
                f"Prediction complete: {hotspot_name} has highest risk "
                f"(score: {hotspot_score}, {len(affected_vehicles[hotspot_key])} vehicles affected)"
            )
            
            return prediction_result
            
        except Exception as e:
            self.logger.error(f"Error in gridlock prediction: {e}")
            return self._empty_prediction_result(error=str(e))
    
    def _validate_journey_data(self, journeys: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and filter journey data for analysis.
        
        Args:
            journeys: Raw journey data
            
        Returns:
            List of validated journey objects
        """
        validated = []
        required_fields = ['vehicle_id', 'current_location', 'destination', 'route_points']
        
        for journey in journeys:
            try:
                # Check required fields
                if not all(field in journey for field in required_fields):
                    continue
                
                # Validate current location
                current_loc = journey['current_location']
                if not self._is_valid_coordinate(current_loc.get('lat'), current_loc.get('lng')):
                    continue
                
                # Validate destination
                destination = journey['destination']
                if not self._is_valid_coordinate(destination.get('lat'), destination.get('lng')):
                    continue
                
                # Validate route points
                route_points = journey.get('route_points', [])
                if not isinstance(route_points, list) or len(route_points) == 0:
                    continue
                
                validated.append(journey)
                
            except Exception as e:
                self.logger.warning(f"Invalid journey data for vehicle {journey.get('vehicle_id', 'unknown')}: {e}")
                continue
        
        self.logger.info(f"Validated {len(validated)} out of {len(journeys)} journeys")
        return validated
    
    def _analyze_journey_impact(self, 
                               journey: Dict[str, Any], 
                               congestion_scores: Dict[str, int],
                               affected_vehicles: Dict[str, List[str]]) -> None:
        """
        Analyze a single journey's impact on choke points over the next 60 minutes.
        
        Args:
            journey: Journey data with route information
            congestion_scores: Dictionary to update with congestion scores
            affected_vehicles: Dictionary to update with affected vehicle IDs
        """
        vehicle_id = journey['vehicle_id']
        route_points = journey['route_points']
        
        # Project vehicle movement over next 60 minutes
        # Sample every 5 minutes for performance (12 time points)
        time_intervals = 12
        points_per_interval = max(1, len(route_points) // time_intervals)
        
        vehicle_affected_choke_points = set()
        
        for i in range(0, len(route_points), points_per_interval):
            if i >= len(route_points):
                break
                
            point = route_points[i]
            
            # Check if this point affects any choke point
            for choke_key, choke_data in self.CHOKE_POINTS.items():
                distance = self._calculate_distance(
                    point.get('lat', 0), 
                    point.get('lng', 0),
                    choke_data['lat'], 
                    choke_data['lng']
                )
                
                if distance <= choke_data['radius_meters']:
                    # Apply time-based weighting (earlier impact = higher score)
                    time_weight = max(1, time_intervals - (i // points_per_interval))
                    congestion_scores[choke_key] += time_weight
                    vehicle_affected_choke_points.add(choke_key)
        
        # Add vehicle to affected lists for choke points it impacts
        for choke_key in vehicle_affected_choke_points:
            if vehicle_id not in affected_vehicles[choke_key]:
                affected_vehicles[choke_key].append(vehicle_id)
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate the Haversine distance between two geographic points in meters.
        
        Args:
            lat1, lng1: First point coordinates
            lat2, lng2: Second point coordinates
            
        Returns:
            Distance in meters
        """
        # Convert latitude and longitude from degrees to radians
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of Earth in meters
        earth_radius_m = 6371000
        distance = earth_radius_m * c
        
        return distance
    
    def _is_valid_coordinate(self, lat: float, lng: float) -> bool:
        """
        Validate if coordinates are within reasonable Bengaluru bounds.
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            True if coordinates are valid
        """
        if lat is None or lng is None:
            return False
            
        try:
            lat, lng = float(lat), float(lng)
            # Bengaluru approximate bounds
            return (12.0 <= lat <= 13.5) and (77.0 <= lng <= 78.0)
        except (ValueError, TypeError):
            return False
    
    def _empty_prediction_result(self, error: str = None) -> Dict[str, Any]:
        """
        Return an empty prediction result for error cases.
        
        Args:
            error: Optional error message
            
        Returns:
            Empty prediction result dictionary
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "choke_point_name": None,
            "congestion_score": 0,
            "affected_vehicle_ids": [],
            "all_choke_points": {
                self.CHOKE_POINTS[key]["name"]: {
                    "score": 0,
                    "affected_vehicles": 0
                }
                for key in self.CHOKE_POINTS.keys()
            },
            "simulation_metadata": {
                "total_journeys_analyzed": 0,
                "prediction_horizon_minutes": 60,
                "processing_time_ms": 0,
                "model_version": "1.0",
                "choke_points_monitored": len(self.CHOKE_POINTS),
                "error": error
            }
        }
