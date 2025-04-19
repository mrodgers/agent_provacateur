from typing import Any, Dict, Optional, Union
from enum import Enum
from pydantic import BaseModel


class MessageType(str, Enum):
    """Types of agent-to-agent messages."""
    
    TASK_REQUEST = "task_request"
    TASK_RESULT = "task_result"
    HEARTBEAT = "heartbeat"


class TaskStatus(str, Enum):
    """Status of a task."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskRequest(BaseModel):
    """Model for a task request from one agent to another."""
    
    task_id: str
    intent: str
    payload: Dict[str, Any]
    source_agent: str
    target_agent: str
    priority: int = 1  # Higher numbers mean higher priority
    timeout_sec: Optional[int] = 300  # Default 5-minute timeout


class TaskResult(BaseModel):
    """Model for a task result from one agent to another."""
    
    task_id: str
    status: TaskStatus
    source_agent: str
    target_agent: str
    output: Dict[str, Any]
    error: Optional[str] = None


class Heartbeat(BaseModel):
    """Model for a heartbeat message from an agent."""
    
    agent_id: str
    timestamp: float
    status: str = "active"
    metrics: Optional[Dict[str, Union[int, float]]] = None


class Message(BaseModel):
    """Container model for all types of agent-to-agent messages."""
    
    message_id: str
    message_type: MessageType
    timestamp: float
    payload: Union[TaskRequest, TaskResult, Heartbeat]
    retries: int = 0
    deduplication_key: Optional[str] = None