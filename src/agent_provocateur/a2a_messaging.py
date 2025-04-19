import time
import uuid
import asyncio
from typing import Any, Dict, List, Optional, Set, Union, Callable, TypeVar

from agent_provocateur.a2a_models import (
    Heartbeat,
    Message,
    MessageType,
    TaskRequest,
    TaskResult,
    TaskStatus,
)

# Type variable for the message callback
T = TypeVar("T", bound=Callable[[Message], Any])


class InMemoryMessageBroker:
    """In-memory implementation of a message broker for development and testing."""
    
    def __init__(self) -> None:
        """Initialize the in-memory broker."""
        self.topics: Dict[str, List[Message]] = {}
        self.subscribers: Dict[str, List[Callable[[Message], Any]]] = {}
        self.processed_messages: Set[str] = set()
    
    def publish(self, topic: str, message: Message) -> None:
        """Publish a message to a topic.
        
        Args:
            topic: The topic to publish to
            message: The message to publish
        """
        if topic not in self.topics:
            self.topics[topic] = []
        
        self.topics[topic].append(message)
        
        # Notify subscribers
        if topic in self.subscribers:
            for callback in self.subscribers[topic]:
                callback(message)
    
    def subscribe(self, topic: str, callback: Callable[[Message], Any]) -> None:
        """Subscribe to a topic.
        
        Args:
            topic: The topic to subscribe to
            callback: The callback to call when a message is received
        """
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        
        self.subscribers[topic].append(callback)
    
    def unsubscribe(self, topic: str, callback: Callable[[Message], Any]) -> None:
        """Unsubscribe from a topic.
        
        Args:
            topic: The topic to unsubscribe from
            callback: The callback to remove
        """
        if topic in self.subscribers and callback in self.subscribers[topic]:
            self.subscribers[topic].remove(callback)
    
    def get_messages(self, topic: str) -> List[Message]:
        """Get all messages for a topic.
        
        Args:
            topic: The topic to get messages for
            
        Returns:
            List[Message]: The messages for the topic
        """
        return self.topics.get(topic, [])
    
    def has_processed(self, message_id: str) -> bool:
        """Check if a message has been processed.
        
        Args:
            message_id: The ID of the message to check
            
        Returns:
            bool: True if the message has been processed
        """
        return message_id in self.processed_messages
    
    def mark_processed(self, message_id: str) -> None:
        """Mark a message as processed.
        
        Args:
            message_id: The ID of the message to mark
        """
        self.processed_messages.add(message_id)
    
    def clear_topic(self, topic: str) -> None:
        """Clear all messages for a topic.
        
        Args:
            topic: The topic to clear
        """
        if topic in self.topics:
            self.topics[topic] = []


class AgentMessaging:
    """Agent messaging library for sending and receiving A2A messages."""
    
    def __init__(
        self, 
        agent_id: str, 
        broker: Optional[InMemoryMessageBroker] = None,
        max_retries: int = 3,
        retry_delay_ms: int = 500,
    ) -> None:
        """Initialize the agent messaging.
        
        Args:
            agent_id: The ID of this agent
            broker: The message broker to use
            max_retries: Maximum number of retry attempts for failed messages
            retry_delay_ms: Base delay in milliseconds between retries (will use exponential backoff)
        """
        self.agent_id = agent_id
        self.broker = broker or InMemoryMessageBroker()
        self.max_retries = max_retries
        self.retry_delay_ms = retry_delay_ms
        self.message_callbacks: Dict[str, List[Callable[[Message], Any]]] = {}
        self.task_callbacks: Dict[str, Callable[[TaskRequest], Any]] = {}
        self.pending_tasks: Dict[str, TaskRequest] = {}
        self.task_results: Dict[str, TaskResult] = {}
        
        # Subscribe to agent-specific topic
        self.broker.subscribe(f"agent.{agent_id}", self._handle_message)
    
    def _generate_message_id(self) -> str:
        """Generate a unique message ID.
        
        Returns:
            str: The unique message ID
        """
        return str(uuid.uuid4())
    
    def _handle_message(self, message: Message) -> None:
        """Handle a received message.
        
        Args:
            message: The message to handle
        """
        # Print for debugging
        print(f"DEBUG: Handling message: {message.message_type}, id={message.message_id}")
        
        # Check if we've already processed this message (deduplication)
        if message.deduplication_key and self.broker.has_processed(message.deduplication_key):
            print(f"DEBUG: Skipping already processed message: {message.deduplication_key}")
            return
        
        # Mark as processed to avoid duplicate processing
        if message.deduplication_key:
            self.broker.mark_processed(message.deduplication_key)
        
        # Handle by message type
        if message.message_type == MessageType.TASK_REQUEST:
            task_request = message.payload
            if isinstance(task_request, TaskRequest):
                print(f"DEBUG: Processing task request: {task_request.task_id}, intent={task_request.intent}")
                self._handle_task_request(task_request)
            else:
                print(f"DEBUG: Invalid task request type: {type(task_request)}")
        elif message.message_type == MessageType.TASK_RESULT:
            task_result = message.payload
            if isinstance(task_result, TaskResult):
                print(f"DEBUG: Storing task result: {task_result.task_id}, status={task_result.status}")
                self.task_results[task_result.task_id] = task_result
            else:
                print(f"DEBUG: Invalid task result type: {type(task_result)}")
        
        # Notify registered callbacks
        if message.message_type.value in self.message_callbacks:
            for callback in self.message_callbacks[message.message_type.value]:
                callback(message)
    
    def _handle_task_request(self, task_request: TaskRequest) -> None:
        """Handle a task request.
        
        Args:
            task_request: The task request to handle
        """
        # Store pending task
        self.pending_tasks[task_request.task_id] = task_request
        
        # If there's a registered handler for this intent, call it
        if task_request.intent in self.task_callbacks:
            self.task_callbacks[task_request.intent](task_request)
    
    def create_message(
        self, 
        message_type: MessageType, 
        payload: Union[TaskRequest, TaskResult, Heartbeat],
        deduplication_key: Optional[str] = None,
    ) -> Message:
        """Create a new message.
        
        Args:
            message_type: The type of message
            payload: The message payload
            deduplication_key: Optional key for deduplication
            
        Returns:
            Message: The created message
        """
        return Message(
            message_id=self._generate_message_id(),
            message_type=message_type,
            timestamp=time.time(),
            payload=payload,
            deduplication_key=deduplication_key or None,
        )
    
    def send_task_request(
        self, 
        target_agent: str, 
        intent: str, 
        payload: Dict[str, Any],
        priority: int = 1,
        timeout_sec: Optional[int] = 300,
    ) -> str:
        """Send a task request to another agent.
        
        Args:
            target_agent: The target agent ID
            intent: The intent of the task
            payload: The task payload
            priority: The priority of the task
            timeout_sec: The timeout in seconds
            
        Returns:
            str: The task ID
        """
        task_id = str(uuid.uuid4())
        
        task_request = TaskRequest(
            task_id=task_id,
            intent=intent,
            payload=payload,
            source_agent=self.agent_id,
            target_agent=target_agent,
            priority=priority,
            timeout_sec=timeout_sec,
        )
        
        message = self.create_message(
            message_type=MessageType.TASK_REQUEST,
            payload=task_request,
            deduplication_key=f"task:{task_id}",
        )
        
        self.broker.publish(f"agent.{target_agent}", message)
        return task_id
    
    def send_task_result(
        self, 
        task_id: str, 
        target_agent: str, 
        status: TaskStatus,
        output: Dict[str, Any],
        error: Optional[str] = None,
    ) -> None:
        """Send a task result to another agent.
        
        Args:
            task_id: The task ID
            target_agent: The target agent ID
            status: The task status
            output: The task output
            error: Optional error message
        """
        task_result = TaskResult(
            task_id=task_id,
            status=status,
            source_agent=self.agent_id,
            target_agent=target_agent,
            output=output,
            error=error,
        )
        
        # Use a different deduplication key for each status to avoid skipping important updates
        message = self.create_message(
            message_type=MessageType.TASK_RESULT,
            payload=task_result,
            deduplication_key=f"result:{task_id}:{status.value}",
        )
        
        self.broker.publish(f"agent.{target_agent}", message)
    
    def send_heartbeat(self, metrics: Optional[Dict[str, Union[int, float]]] = None) -> None:
        """Send a heartbeat message.
        
        Args:
            metrics: Optional metrics to include
        """
        heartbeat = Heartbeat(
            agent_id=self.agent_id,
            timestamp=time.time(),
            metrics=metrics,
        )
        
        message = self.create_message(
            message_type=MessageType.HEARTBEAT,
            payload=heartbeat,
        )
        
        self.broker.publish("heartbeats", message)
    
    async def send_with_retry(
        self, 
        topic: str, 
        message: Message, 
        max_retries: Optional[int] = None,
    ) -> bool:
        """Send a message with retry logic.
        
        Args:
            topic: The topic to publish to
            message: The message to send
            max_retries: Maximum number of retries (defaults to self.max_retries)
            
        Returns:
            bool: True if the message was successfully sent
        """
        retries = 0
        max_retry_count = max_retries if max_retries is not None else self.max_retries
        
        while retries <= max_retry_count:
            try:
                self.broker.publish(topic, message)
                return True
            except Exception:
                retries += 1
                if retries > max_retry_count:
                    return False
                
                # Exponential backoff
                delay_ms = self.retry_delay_ms * (2 ** (retries - 1))
                await asyncio.sleep(delay_ms / 1000.0)
                
                # Update retry count in message
                message.retries = retries
        
        return False
    
    def register_task_handler(self, intent: str, callback: Callable[[TaskRequest], Any]) -> None:
        """Register a handler for a specific task intent.
        
        Args:
            intent: The intent to handle
            callback: The callback to call when a task request with this intent is received
        """
        self.task_callbacks[intent] = callback
    
    def register_message_handler(
        self, 
        message_type: Union[MessageType, str], 
        callback: Callable[[Message], Any],
    ) -> None:
        """Register a handler for a specific message type.
        
        Args:
            message_type: The message type to handle
            callback: The callback to call when a message of this type is received
        """
        type_str = message_type.value if isinstance(message_type, MessageType) else message_type
        
        if type_str not in self.message_callbacks:
            self.message_callbacks[type_str] = []
        
        self.message_callbacks[type_str].append(callback)
    
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get the result for a task.
        
        Args:
            task_id: The task ID
            
        Returns:
            Optional[TaskResult]: The task result if available
        """
        return self.task_results.get(task_id)
    
    async def wait_for_task_result(
        self, 
        task_id: str, 
        timeout_sec: int = 60,
    ) -> Optional[TaskResult]:
        """Wait for a task result.
        
        Args:
            task_id: The task ID
            timeout_sec: The timeout in seconds
            
        Returns:
            Optional[TaskResult]: The task result if available with a final status
        """
        start_time = time.time()
        
        # Make sure task_id is a string
        if not isinstance(task_id, str):
            print(f"WARNING: task_id is not a string: {task_id}")
            return None
            
        # First, create a placeholder for IN_PROGRESS
        in_progress_result = None
            
        # Wait loop
        while time.time() - start_time < timeout_sec:
            # Check if we have a result
            result = self.get_task_result(task_id)
            
            # Save the IN_PROGRESS result if we have one
            if result and result.status == TaskStatus.IN_PROGRESS:
                in_progress_result = result
                
            # Only return result if it's a final status (COMPLETED or FAILED)
            if result and result.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                return result
            
            # Small sleep to avoid busy-waiting
            await asyncio.sleep(0.1)
        
        # If we timed out, return the last known status, even if it's not final
        result = self.get_task_result(task_id)
        if result:
            return result
            
        # If we don't have any result but have an IN_PROGRESS one, return that
        if in_progress_result:
            return in_progress_result
            
        # Otherwise, no result at all
        return None