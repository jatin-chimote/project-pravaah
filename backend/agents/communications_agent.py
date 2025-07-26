"""
Communications Agent - The "Voice" of Project Pravaah

This agent executes the Orchestrator's commands by writing to Firestore
and sending alerts via Firebase Cloud Messaging.
"""

import os
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials, messaging


class CommunicationsAgent:
    """
    Communications Agent responsible for executing commands and sending notifications.
    
    This agent implements the decisions made by the Orchestrator by updating
    database records and sending real-time alerts to vehicles and users.
    """
    
    def __init__(self, project_id: str = "stable-sign-454210-i0"):
        """
        Initialize the Communications Agent with Firebase Admin SDK.
        
        Args:
            project_id: Google Cloud Project ID
        """
        self.project_id = project_id
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Initialize Firebase Admin SDK (same pattern as ObserverAgent)
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
                self.logger.error(f"Service account key not found at: {service_account_path}")
                raise FileNotFoundError(f"Service account key not found: {service_account_path}")
        
        # Initialize Firestore client
        self.db = firestore.Client(project=project_id)
        
        # Communications metrics
        self.metrics = {
            'total_executions': 0,
            'successful_updates': 0,
            'failed_updates': 0,
            'notifications_sent': 0,
            'notification_failures': 0,
            'avg_execution_time': 0.0
        }
        
        self.logger.info(f"CommunicationsAgent initialized for project: {project_id}")
        
    def execute_reroute_and_notify(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute reroute command and notify affected parties.
        
        Args:
            payload: Dictionary containing:
                - journeyId: Unique identifier for the journey
                - new_route_data: New route information
                - reason_for_change: Reason for the reroute
            
        Returns:
            Dict containing execution results
        """
        execution_start = datetime.now()
        execution_id = f"exec_{execution_start.strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        correlation_id = payload.get('correlation_id', str(uuid.uuid4()))
        
        self.logger.info(f"[{correlation_id}] Starting reroute execution: {execution_id}")
        self.metrics['total_executions'] += 1
        
        # Extract payload data
        journey_id = payload.get('journeyId')
        new_route_data = payload.get('new_route_data')
        reason_for_change = payload.get('reason_for_change')
        
        # Validate required fields
        if not all([journey_id, new_route_data, reason_for_change]):
            error_msg = "Missing required fields: journeyId, new_route_data, or reason_for_change"
            self.logger.error(f"[{correlation_id}] {error_msg}")
            return self._create_error_result(execution_id, correlation_id, error_msg)
        
        try:
            # STEP 1: Update Database
            self.logger.info(f"[{correlation_id}] Updating journey {journey_id} in Firestore")
            
            # Find and update the journey document
            journey_ref = self.db.collection('journeys').document(journey_id)
            journey_doc = journey_ref.get()
            
            if not journey_doc.exists:
                error_msg = f"Journey {journey_id} not found in database"
                self.logger.error(f"[{correlation_id}] {error_msg}")
                self.metrics['failed_updates'] += 1
                return self._create_error_result(execution_id, correlation_id, error_msg)
            
            # Update journey with new route and status
            update_data = {
                'route_data': new_route_data,
                'status': 'REROUTED',
                'reroute_reason': reason_for_change,
                'rerouted_at': datetime.now(),
                'reroute_execution_id': execution_id,
                'updated_at': datetime.now()
            }
            
            journey_ref.update(update_data)
            self.logger.info(f"[{correlation_id}] Successfully updated journey {journey_id} to REROUTED status")
            self.metrics['successful_updates'] += 1
            
            # STEP 2: Send Notifications
            self.logger.info(f"[{correlation_id}] Sending notifications for journey {journey_id}")
            
            # Get journey data for notification context
            updated_journey = journey_ref.get().to_dict()
            notification_payload = {
                'journey_id': journey_id,
                'reason': reason_for_change,
                'new_route': new_route_data,
                'journey_data': updated_journey,
                'correlation_id': correlation_id
            }
            
            # Call FCM notification helper
            fcm_result = self._send_fcm_alert(notification_payload)
            
            # Calculate execution metrics
            execution_duration = (datetime.now() - execution_start).total_seconds()
            
            # Create success result
            execution_result = {
                "timestamp": execution_start.isoformat(),
                "execution_id": execution_id,
                "correlation_id": correlation_id,
                "status": "success",
                "journey_id": journey_id,
                "results": {
                    "database_update": {
                        "status": "success",
                        "journey_id": journey_id,
                        "new_status": "REROUTED",
                        "reason": reason_for_change
                    },
                    "notification": fcm_result
                },
                "performance": {
                    "execution_time_seconds": round(execution_duration, 3),
                    "database_operation_success": True,
                    "notification_sent": fcm_result.get('status') == 'success'
                }
            }
            
            self.logger.info(f"[{correlation_id}] Reroute execution completed successfully in {execution_duration:.3f}s")
            return execution_result
            
        except Exception as e:
            self.logger.error(f"[{correlation_id}] Failed to execute reroute: {str(e)}")
            self.metrics['failed_updates'] += 1
            return self._create_error_result(execution_id, correlation_id, str(e))
    
    def _send_fcm_alert(self, notification_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send Firebase Cloud Messaging alert for journey reroute.
        
        Args:
            notification_payload: Dictionary containing:
                - journey_id: Journey identifier
                - reason: Reason for reroute
                - new_route: New route data
                - journey_data: Complete journey information
                - correlation_id: Correlation ID for tracing
            
        Returns:
            Dict containing FCM delivery results
        """
        journey_id = notification_payload.get('journey_id')
        reason = notification_payload.get('reason')
        correlation_id = notification_payload.get('correlation_id')
        
        try:
            # For hackathon: Log FCM alert to console as requested
            self.logger.info(f"FCM Alert Sent: Rerouting Journey [{journey_id}] due to [{reason}]")
            
            # In production, this would send actual FCM notifications
            # Example production code (commented for hackathon):
            # message = messaging.Message(
            #     notification=messaging.Notification(
            #         title="Route Update - Project Pravaah",
            #         body=f"Your journey has been rerouted due to {reason}"
            #     ),
            #     data={
            #         'journey_id': journey_id,
            #         'reason': reason,
            #         'action': 'route_update'
            #     },
            #     topic='journey_updates'  # or specific FCM tokens
            # )
            # response = messaging.send(message)
            
            # Simulate successful notification for hackathon
            self.metrics['notifications_sent'] += 1
            
            fcm_result = {
                "timestamp": datetime.now().isoformat(),
                "message_id": f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}",
                "status": "success",
                "journey_id": journey_id,
                "correlation_id": correlation_id,
                "notification_type": "reroute_alert",
                "delivery_status": {
                    "method": "console_log_simulation",  # For hackathon
                    "successful": True,
                    "message": f"FCM Alert Sent: Rerouting Journey [{journey_id}] due to [{reason}]"
                },
                "message_metadata": {
                    "priority": "high",  # Reroute notifications are high priority
                    "notification_title": "Route Update - Project Pravaah",
                    "notification_body": f"Your journey has been rerouted due to {reason}",
                    "delivery_attempts": 1
                }
            }
            
            self.logger.info(f"[{correlation_id}] FCM notification simulated successfully for journey {journey_id}")
            return fcm_result
            
        except Exception as e:
            self.logger.error(f"[{correlation_id}] Failed to send FCM alert: {str(e)}")
            self.metrics['notification_failures'] += 1
            
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "journey_id": journey_id,
                "correlation_id": correlation_id,
                "error": str(e),
                "delivery_status": {
                    "successful": False,
                    "error_message": str(e)
                }
            }
    
    def _create_error_result(self, execution_id: str, correlation_id: str, error_message: str) -> Dict[str, Any]:
        """
        Create standardized error result for failed operations.
        
        Args:
            execution_id: Unique execution identifier
            correlation_id: Correlation ID for tracing
            error_message: Error description
            
        Returns:
            Standardized error result dictionary
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "execution_id": execution_id,
            "correlation_id": correlation_id,
            "status": "error",
            "error": {
                "message": error_message,
                "type": "execution_failure"
            },
            "results": {
                "database_update": {
                    "status": "failed",
                    "error": error_message
                },
                "notification": {
                    "status": "skipped",
                    "reason": "database_update_failed"
                }
            },
            "performance": {
                "execution_time_seconds": 0,
                "database_operation_success": False,
                "notification_sent": False
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status and metrics of the CommunicationsAgent.
        
        Returns:
            Dictionary containing agent status and performance metrics
        """
        total_ops = self.metrics['total_executions']
        success_rate = (self.metrics['successful_updates'] / max(1, total_ops)) * 100
        notification_rate = (self.metrics['notifications_sent'] / max(1, total_ops)) * 100
        
        return {
            "agent": "CommunicationsAgent",
            "status": "operational",
            "project_id": self.project_id,
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "total_executions": total_ops,
                "successful_updates": self.metrics['successful_updates'],
                "failed_updates": self.metrics['failed_updates'],
                "notifications_sent": self.metrics['notifications_sent'],
                "notification_failures": self.metrics['notification_failures'],
                "success_rate_percent": round(success_rate, 2),
                "notification_delivery_rate_percent": round(notification_rate, 2),
                "average_execution_time_seconds": self.metrics['avg_execution_time']
            },
            "capabilities": {
                "firestore_updates": True,
                "fcm_notifications": True,
                "journey_rerouting": True,
                "correlation_tracking": True
            }
        }
