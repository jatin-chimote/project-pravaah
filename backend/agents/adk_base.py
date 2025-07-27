#!/usr/bin/env python3
"""
Google ADK Base Classes for Project Pravaah
Urban Mobility Operating System - Agent Development Kit Integration
"""

import os
import json
import uuid
import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

import yaml
from google.cloud import firestore
from google.cloud import pubsub_v1
import firebase_admin
from firebase_admin import credentials

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentCapability(Enum):
    """Standard agent capabilities for Project Pravaah."""
    PERCEPTION = "perception"
    PREDICTION = "prediction"
    DECISION_MAKING = "decision_making"
    COMMUNICATION = "communication"
    TRAFFIC_MONITORING = "traffic_monitoring"
    TELEMETRY_INGESTION = "telemetry_ingestion"
    CONGESTION_PREDICTION = "congestion_prediction"
    STRATEGIC_PLANNING = "strategic_planning"
    NOTIFICATION_DELIVERY = "notification_delivery"

class MessageType(Enum):
    """A2A message types."""
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    HEARTBEAT = "heartbeat"

@dataclass
class A2AMessage:
    """Agent-to-Agent message structure."""
    message_id: str
    sender: str
    receiver: str
    message_type: MessageType
    action: str
    payload: Dict[str, Any]
    correlation_id: str
    timestamp: str
    ttl: int = 300  # 5 minutes default TTL
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AMessage':
        """Create message from dictionary."""
        return cls(**data)

@dataclass
class AgentCapabilityInfo:
    """Agent capability information."""
    capability: AgentCapability
    version: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]

@dataclass
class AgentRegistration:
    """Agent registration information."""
    agent_id: str
    name: str
    capabilities: List[AgentCapabilityInfo]
    endpoint: str
    status: str
    last_heartbeat: str
    metadata: Dict[str, Any]

class ADKConfig:
    """ADK configuration manager."""
    
    def __init__(self, config_path: str = "adk_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load ADK configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load ADK config: {e}")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration fallback."""
        return {
            "project_id": "stable-sign-454210-i0",
            "region": "asia-south1",
            "agent_registry": {"type": "firestore", "collection": "agent_registry"},
            "messaging": {"type": "pubsub", "topic": "pravaah-agent-messages"}
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, {})
        return value if value != {} else default

class AgentRegistry:
    """ADK Agent Registry using Firestore."""
    
    def __init__(self, config: ADKConfig):
        self.config = config
        self.firestore_client = firestore.Client(
            project=config.get('project_id')
        )
        self.collection_name = config.get('agent_registry.collection', 'agent_registry')
        
    async def register_agent(self, registration: AgentRegistration) -> bool:
        """Register an agent in the registry."""
        try:
            doc_ref = self.firestore_client.collection(self.collection_name).document(registration.agent_id)
            doc_ref.set(asdict(registration))
            logger.info(f"Agent {registration.agent_id} registered successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to register agent {registration.agent_id}: {e}")
            return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the registry."""
        try:
            doc_ref = self.firestore_client.collection(self.collection_name).document(agent_id)
            doc_ref.delete()
            logger.info(f"Agent {agent_id} unregistered successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to unregister agent {agent_id}: {e}")
            return False
    
    async def discover_agents_by_capability(self, capability: AgentCapability) -> List[AgentRegistration]:
        """Discover agents by capability."""
        try:
            docs = self.firestore_client.collection(self.collection_name)\
                .where('capabilities', 'array_contains', capability.value)\
                .where('status', '==', 'active')\
                .stream()
            
            agents = []
            for doc in docs:
                data = doc.to_dict()
                agents.append(AgentRegistration(**data))
            
            return agents
        except Exception as e:
            logger.error(f"Failed to discover agents by capability {capability}: {e}")
            return []
    
    async def get_agent(self, agent_id: str) -> Optional[AgentRegistration]:
        """Get agent registration by ID."""
        try:
            doc_ref = self.firestore_client.collection(self.collection_name).document(agent_id)
            doc = doc_ref.get()
            if doc.exists:
                return AgentRegistration(**doc.to_dict())
            return None
        except Exception as e:
            logger.error(f"Failed to get agent {agent_id}: {e}")
            return None

class A2AMessaging:
    """A2A messaging system using Pub/Sub."""
    
    def __init__(self, config: ADKConfig, agent_id: str):
        self.config = config
        self.agent_id = agent_id
        self.project_id = config.get('project_id')
        self.topic_name = config.get('messaging.topic', 'pravaah-agent-messages')
        
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        
        self.topic_path = self.publisher.topic_path(self.project_id, self.topic_name)
        self.subscription_name = f"{config.get('messaging.subscription_prefix', 'pravaah-agent-')}{agent_id}"
        self.subscription_path = self.subscriber.subscription_path(self.project_id, self.subscription_name)
        
        self._ensure_topic_and_subscription()
    
    def _ensure_topic_and_subscription(self):
        """Ensure topic and subscription exist."""
        try:
            # Create topic if it doesn't exist
            try:
                self.publisher.create_topic(request={"name": self.topic_path})
                logger.info(f"Created topic: {self.topic_path}")
            except Exception:
                pass  # Topic might already exist
            
            # Create subscription if it doesn't exist
            try:
                self.subscriber.create_subscription(
                    request={
                        "name": self.subscription_path,
                        "topic": self.topic_path,
                        "ack_deadline_seconds": self.config.get('messaging.ack_deadline', 600)
                    }
                )
                logger.info(f"Created subscription: {self.subscription_path}")
            except Exception:
                pass  # Subscription might already exist
                
        except Exception as e:
            logger.error(f"Failed to ensure topic/subscription: {e}")
    
    async def send_message(self, message: A2AMessage) -> bool:
        """Send A2A message."""
        try:
            message_data = json.dumps(message.to_dict()).encode('utf-8')
            future = self.publisher.publish(self.topic_path, message_data)
            message_id = future.result()
            logger.info(f"Message sent: {message_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    async def receive_messages(self, callback, timeout: int = 60):
        """Receive A2A messages."""
        def message_callback(message):
            try:
                data = json.loads(message.data.decode('utf-8'))
                a2a_message = A2AMessage.from_dict(data)
                
                # Filter messages for this agent
                if a2a_message.receiver == self.agent_id or a2a_message.receiver == "all":
                    asyncio.create_task(callback(a2a_message))
                
                message.ack()
            except Exception as e:
                logger.error(f"Failed to process message: {e}")
                message.nack()
        
        try:
            flow_control = pubsub_v1.types.FlowControl(max_messages=100)
            streaming_pull_future = self.subscriber.subscribe(
                self.subscription_path,
                callback=message_callback,
                flow_control=flow_control
            )
            
            logger.info(f"Listening for messages on {self.subscription_path}")
            
            try:
                streaming_pull_future.result(timeout=timeout)
            except Exception:
                streaming_pull_future.cancel()
                
        except Exception as e:
            logger.error(f"Failed to receive messages: {e}")

class PravaahAgent(ABC):
    """Base ADK Agent class for Project Pravaah."""
    
    def __init__(self, 
                 agent_id: str,
                 name: str,
                 capabilities: List[AgentCapability],
                 config_path: str = "adk_config.yaml"):
        
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.config = ADKConfig(config_path)
        
        # Initialize ADK components
        self.registry = AgentRegistry(self.config)
        self.messaging = A2AMessaging(self.config, agent_id)
        
        # Agent state
        self.status = "initializing"
        self.metadata = {}
        self.metrics = {
            "messages_sent": 0,
            "messages_received": 0,
            "errors": 0,
            "uptime_start": datetime.now(timezone.utc).isoformat()
        }
        
        # Initialize Firebase Admin SDK
        self._initialize_firebase()
        
        logger.info(f"ADK Agent {self.agent_id} initialized")
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK."""
        try:
            if not firebase_admin._apps:
                key_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
                if os.path.exists(key_path):
                    cred = credentials.Certificate(key_path)
                    firebase_admin.initialize_app(cred)
                    logger.info("Firebase Admin SDK initialized with service account")
                else:
                    firebase_admin.initialize_app()
                    logger.info("Firebase Admin SDK initialized with default credentials")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
    
    async def start(self):
        """Start the agent."""
        try:
            await self.on_start()
            
            # Register agent
            registration = AgentRegistration(
                agent_id=self.agent_id,
                name=self.name,
                capabilities=[
                    AgentCapabilityInfo(
                        capability=cap,
                        version="1.0.0",
                        description=f"{cap.value} capability",
                        input_schema={},
                        output_schema={}
                    ) for cap in self.capabilities
                ],
                endpoint=f"pubsub://{self.messaging.subscription_path}",
                status="active",
                last_heartbeat=datetime.now(timezone.utc).isoformat(),
                metadata=self.metadata
            )
            
            await self.registry.register_agent(registration)
            self.status = "active"
            
            # Start message listening
            asyncio.create_task(self._message_loop())
            
            logger.info(f"Agent {self.agent_id} started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start agent {self.agent_id}: {e}")
            self.status = "error"
    
    async def stop(self):
        """Stop the agent."""
        try:
            await self.on_stop()
            await self.registry.unregister_agent(self.agent_id)
            self.status = "stopped"
            logger.info(f"Agent {self.agent_id} stopped successfully")
        except Exception as e:
            logger.error(f"Failed to stop agent {self.agent_id}: {e}")
    
    async def _message_loop(self):
        """Main message processing loop."""
        await self.messaging.receive_messages(self._handle_message)
    
    async def _handle_message(self, message: A2AMessage):
        """Handle incoming A2A message."""
        try:
            self.metrics["messages_received"] += 1
            logger.info(f"Agent {self.agent_id} received message: {message.action} from {message.sender}")
            
            response = await self.on_message(message)
            
            if response and message.message_type == MessageType.REQUEST:
                response_message = A2AMessage(
                    message_id=str(uuid.uuid4()),
                    sender=self.agent_id,
                    receiver=message.sender,
                    message_type=MessageType.RESPONSE,
                    action=f"{message.action}_response",
                    payload=response,
                    correlation_id=message.correlation_id,
                    timestamp=datetime.now(timezone.utc).isoformat()
                )
                await self.send_message(response_message)
                
        except Exception as e:
            logger.error(f"Error handling message in agent {self.agent_id}: {e}")
            self.metrics["errors"] += 1
    
    async def send_message(self, message: A2AMessage) -> bool:
        """Send A2A message."""
        try:
            success = await self.messaging.send_message(message)
            if success:
                self.metrics["messages_sent"] += 1
            return success
        except Exception as e:
            logger.error(f"Failed to send message from agent {self.agent_id}: {e}")
            self.metrics["errors"] += 1
            return False
    
    async def discover_agents(self, capability: AgentCapability) -> List[AgentRegistration]:
        """Discover agents by capability."""
        return await self.registry.discover_agents_by_capability(capability)
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status and metrics."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status,
            "capabilities": [cap.value for cap in self.capabilities],
            "metrics": self.metrics,
            "metadata": self.metadata
        }
    
    @abstractmethod
    async def on_start(self):
        """Called when agent starts."""
        pass
    
    @abstractmethod
    async def on_stop(self):
        """Called when agent stops."""
        pass
    
    @abstractmethod
    async def on_message(self, message: A2AMessage) -> Optional[Dict[str, Any]]:
        """Handle incoming A2A message."""
        pass
