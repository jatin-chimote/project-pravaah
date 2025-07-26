"""Observer Agent - The "Eyes and Ears" of Project Pravaah

This agent perceives the real world by reading from Firestore database 
and listening to real-time vehicle telemetry via Pub/Sub to gather 
current traffic conditions and vehicle positions.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import uuid

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.types import PubsubMessage
from google.api_core import retry
from google.api_core.exceptions import GoogleAPICallError


class ObserverAgent:
    """
    Observer Agent responsible for real-world perception and data collection.
    
    This agent monitors traffic conditions, vehicle positions, and network state
    by listening to real-time telemetry data and maintaining Firestore records.
    """
    
    def __init__(self, 
                 project_id: str = "stable-sign-454210-i0",
                 subscription_name: str = "vehicle-telemetry-sub",
                 max_messages: int = 100,
                 ack_deadline_seconds: int = 60):
        """
        Initialize the Observer Agent.
        
        Args:
            project_id: Google Cloud Project ID
            subscription_name: Pub/Sub subscription name for vehicle telemetry
            max_messages: Maximum messages to pull at once
            ack_deadline_seconds: Message acknowledgment deadline
        """
        self.project_id = project_id
        self.subscription_name = subscription_name
        self.max_messages = max_messages
        self.ack_deadline_seconds = ack_deadline_seconds
        
        # Setup logging with correlation IDs
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Initialize Firebase Admin SDK
        self._initialize_firebase()
        
        # Initialize Firestore client
        self.db = firestore.client()
        
        # Initialize Pub/Sub subscriber client
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(
            project_id, subscription_name
        )
        
        # Thread pool for handling concurrent message processing
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Track agent state
        self.is_listening = False
        self.processed_messages = 0
        self.failed_messages = 0
        
        self.logger.info(f"ObserverAgent initialized for project: {project_id}")
    
    def _initialize_firebase(self) -> None:
        """Initialize Firebase Admin SDK if not already initialized."""
        try:
            # Check if Firebase app is already initialized
            firebase_admin.get_app()
            self.logger.info("Firebase Admin SDK already initialized")
        except ValueError:
            # Initialize Firebase Admin SDK
            service_account_path = os.getenv(
                'GOOGLE_APPLICATION_CREDENTIALS', 
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'serviceAccountKey.json')
            )
            
            if os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                self.logger.info("Firebase Admin SDK initialized with service account")
            else:
                # Use default credentials in Cloud Run environment
                firebase_admin.initialize_app()
                self.logger.info("Firebase Admin SDK initialized with default credentials")
    
    def start_listening(self, timeout: Optional[float] = None) -> None:
        """
        Start listening for real-time vehicle telemetry messages.
        
        Args:
            timeout: Optional timeout for listening (useful for Cloud Run)
        """
        if self.is_listening:
            self.logger.warning("Observer Agent is already listening")
            return
        
        self.is_listening = True
        self.logger.info(f"Starting to listen on subscription: {self.subscription_path}")
        
        try:
            # Configure flow control settings
            flow_control = pubsub_v1.types.FlowControl(max_messages=self.max_messages)
            
            # Start pulling messages with timeout
            streaming_pull_future = self.subscriber.subscribe(
                self.subscription_path,
                callback=self.telemetry_callback,
                flow_control=flow_control,
                await_ready_timeout=30.0
            )
            
            self.logger.info(f"Listening for messages on {self.subscription_path}...")
            
            try:
                # Keep the main thread running
                streaming_pull_future.result(timeout=timeout)
            except KeyboardInterrupt:
                self.logger.info("Received interrupt signal, stopping listener...")
            except Exception as e:
                self.logger.error(f"Error in streaming pull: {e}")
            finally:
                streaming_pull_future.cancel()
                streaming_pull_future.result()  # Block until the shutdown is complete
                
        except Exception as e:
            self.logger.error(f"Failed to start listening: {e}")
            raise
        finally:
            self.is_listening = False
            self.logger.info("Observer Agent stopped listening")
    
    def telemetry_callback(self, message: PubsubMessage) -> None:
        """
        Callback function to process incoming vehicle telemetry messages.
        
        Args:
            message: Pub/Sub message containing vehicle telemetry data
        """
        correlation_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Parse message data
            message_data = json.loads(message.data.decode('utf-8'))
            
            self.logger.info(
                f"Processing telemetry message [ID: {correlation_id}] "
                f"for vehicle: {message_data.get('vehicle_id', 'unknown')}"
            )
            
            # Validate required fields
            if not self._validate_telemetry_data(message_data):
                self.logger.error(f"Invalid telemetry data [ID: {correlation_id}]: {message_data}")
                message.nack()
                self.failed_messages += 1
                return
            
            # Update vehicle document in Firestore
            self._update_vehicle_location(message_data, correlation_id)
            
            # Acknowledge message after successful processing
            message.ack()
            self.processed_messages += 1
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(
                f"Successfully processed telemetry [ID: {correlation_id}] "
                f"in {processing_time:.3f}s"
            )
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode message JSON [ID: {correlation_id}]: {e}")
            message.nack()
            self.failed_messages += 1
            
        except GoogleAPICallError as e:
            self.logger.error(f"Google Cloud API error [ID: {correlation_id}]: {e}")
            message.nack()
            self.failed_messages += 1
            
        except Exception as e:
            self.logger.error(f"Error processing telemetry [ID: {correlation_id}]: {e}")
            message.nack()
            self.failed_messages += 1
    
    def _validate_telemetry_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate incoming telemetry data structure and values.
        
        Args:
            data: Telemetry data dictionary
            
        Returns:
            True if data is valid, False otherwise
        """
        required_fields = ['vehicle_id', 'latitude', 'longitude', 'timestamp']
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                return False
        
        # Validate data types and ranges
        try:
            lat = float(data['latitude'])
            lng = float(data['longitude'])
            
            # Basic coordinate validation (Bengaluru area)
            if not (12.0 <= lat <= 13.5 and 77.0 <= lng <= 78.0):
                self.logger.warning(f"Coordinates outside Bengaluru area: {lat}, {lng}")
                return False
                
            # Validate timestamp
            timestamp = data['timestamp']
            if isinstance(timestamp, str):
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            return True
            
        except (ValueError, TypeError) as e:
            self.logger.error(f"Data validation error: {e}")
            return False
    
    @retry.Retry(predicate=retry.if_exception_type(GoogleAPICallError))
    def _update_vehicle_location(self, telemetry_data: Dict[str, Any], correlation_id: str) -> None:
        """
        Update vehicle location in Firestore database.
        
        Args:
            telemetry_data: Vehicle telemetry data
            correlation_id: Correlation ID for tracking
        """
        vehicle_id = telemetry_data['vehicle_id']
        
        try:
            # Prepare update data
            update_data = {
                'location': {
                    'latitude': float(telemetry_data['latitude']),
                    'longitude': float(telemetry_data['longitude']),
                    'timestamp': telemetry_data['timestamp'],
                    'last_updated': firestore.SERVER_TIMESTAMP
                },
                'status': telemetry_data.get('status', 'active'),
                'speed': telemetry_data.get('speed', 0),
                'heading': telemetry_data.get('heading', 0),
                'correlation_id': correlation_id
            }
            
            # Update vehicle document
            vehicle_ref = self.db.collection('vehicles').document(vehicle_id)
            vehicle_ref.set(update_data, merge=True)
            
            # Also update location history (optional)
            history_ref = self.db.collection('vehicle_history').document()
            history_data = {
                'vehicle_id': vehicle_id,
                **update_data,
                'recorded_at': firestore.SERVER_TIMESTAMP
            }
            history_ref.set(history_data)
            
            self.logger.debug(f"Updated vehicle {vehicle_id} location [ID: {correlation_id}]")
            
        except Exception as e:
            self.logger.error(f"Failed to update vehicle {vehicle_id} [ID: {correlation_id}]: {e}")
            raise
    
    def get_network_state(self) -> Dict[str, Any]:
        """
        Get the current state of the transportation network from Firestore.
        
        Returns:
            Dict containing current network state including:
            - Active vehicles and their positions
            - Traffic conditions
            - Route congestion levels
            - System metrics
        """
        self.logger.info("Collecting network state data...")
        
        try:
            # Get active vehicles
            vehicles_ref = self.db.collection('vehicles')
            vehicles = vehicles_ref.where('status', '==', 'active').stream()
            
            active_vehicles = {}
            for vehicle in vehicles:
                vehicle_data = vehicle.to_dict()
                active_vehicles[vehicle.id] = {
                    'location': vehicle_data.get('location', {}),
                    'status': vehicle_data.get('status'),
                    'speed': vehicle_data.get('speed', 0),
                    'last_updated': vehicle_data.get('location', {}).get('timestamp')
                }
            
            # Get traffic conditions (if available)
            traffic_ref = self.db.collection('traffic_conditions').limit(100)
            traffic_docs = traffic_ref.stream()
            
            traffic_conditions = {}
            for doc in traffic_docs:
                traffic_conditions[doc.id] = doc.to_dict()
            
            network_state = {
                "timestamp": datetime.now().isoformat(),
                "active_vehicles_count": len(active_vehicles),
                "active_vehicles": active_vehicles,
                "traffic_conditions": traffic_conditions,
                "agent_metrics": {
                    "processed_messages": self.processed_messages,
                    "failed_messages": self.failed_messages,
                    "is_listening": self.is_listening
                }
            }
            
            self.logger.info(f"Network state collected: {len(active_vehicles)} active vehicles")
            return network_state
            
        except Exception as e:
            self.logger.error(f"Failed to get network state: {e}")
            raise
    
    def stop_listening(self) -> None:
        """Stop the telemetry listener gracefully."""
        self.is_listening = False
        self.logger.info("Observer Agent stopping...")
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of the Observer Agent.
        
        Returns:
            Dict containing health metrics
        """
        return {
            "status": "healthy" if self.is_listening else "stopped",
            "processed_messages": self.processed_messages,
            "failed_messages": self.failed_messages,
            "success_rate": (
                self.processed_messages / (self.processed_messages + self.failed_messages)
                if (self.processed_messages + self.failed_messages) > 0 else 1.0
            ),
            "subscription_path": self.subscription_path,
            "timestamp": datetime.now().isoformat()
        }
