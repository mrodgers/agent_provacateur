import asyncio
import json
from typing import Any, Callable, Dict, List, Optional

# mypy: ignore-errors
try:
    import redis
except ImportError:
    redis = None

from agent_provocateur.a2a_models import Message


class RedisMessageBroker:
    """Redis implementation of a message broker for production use."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        expiration_sec: int = 86400,  # 24 hours
    ) -> None:
        """Initialize the Redis broker.
        
        Args:
            redis_url: The Redis connection URL
            expiration_sec: Message expiration in seconds
        
        Raises:
            ImportError: If Redis is not installed
        """
        if redis is None:
            raise ImportError(
                "Redis package is required for RedisMessageBroker. "
                "Install it with 'pip install redis'."
            )
        
        self.redis_url = redis_url
        self.expiration_sec = expiration_sec
        self.redis_client = redis.Redis.from_url(redis_url)
        self.pubsub = self.redis_client.pubsub()
        self.subscribers: Dict[str, List[Callable[[Message], Any]]] = {}
        self.running = False
        self.listener_task: Optional[asyncio.Task] = None
    
    def publish(self, topic: str, message: Message) -> None:
        """Publish a message to a topic.
        
        Args:
            topic: The topic to publish to
            message: The message to publish
        """
        message_json = json.dumps(message.dict())
        
        # Store message in Redis with expiration
        if message.message_id:
            self.redis_client.setex(
                f"message:{message.message_id}",
                self.expiration_sec,
                message_json,
            )
        
        # Also store deduplication key if present
        if message.deduplication_key:
            self.redis_client.setex(
                f"dedup:{message.deduplication_key}",
                self.expiration_sec,
                message.message_id,
            )
        
        # Publish to Redis channel
        self.redis_client.publish(topic, message_json)
    
    def subscribe(self, topic: str, callback: Callable[[Message], Any]) -> None:
        """Subscribe to a topic.
        
        Args:
            topic: The topic to subscribe to
            callback: The callback to call when a message is received
        """
        # Register callback
        if topic not in self.subscribers:
            self.subscribers[topic] = []
            # Subscribe to Redis channel
            self.pubsub.subscribe(topic)
        
        self.subscribers[topic].append(callback)
        
        # Start listener if not already running
        if not self.running:
            self.start_listener()
    
    def unsubscribe(self, topic: str, callback: Callable[[Message], Any]) -> None:
        """Unsubscribe from a topic.
        
        Args:
            topic: The topic to unsubscribe from
            callback: The callback to remove
        """
        if topic in self.subscribers and callback in self.subscribers[topic]:
            self.subscribers[topic].remove(callback)
            
            # If no more subscribers for this topic, unsubscribe from Redis
            if not self.subscribers[topic]:
                self.pubsub.unsubscribe(topic)
                del self.subscribers[topic]
    
    def has_processed(self, message_id: str) -> bool:
        """Check if a message has been processed.
        
        Args:
            message_id: The ID of the message to check
            
        Returns:
            bool: True if the message has been processed
        """
        return bool(self.redis_client.exists(f"processed:{message_id}"))
    
    def mark_processed(self, message_id: str) -> None:
        """Mark a message as processed.
        
        Args:
            message_id: The ID of the message to mark
        """
        self.redis_client.setex(
            f"processed:{message_id}",
            self.expiration_sec,
            "1",
        )
    
    def start_listener(self) -> None:
        """Start the Redis listener task."""
        self.running = True
        self.listener_task = asyncio.create_task(self._listener_loop())
    
    def stop_listener(self) -> None:
        """Stop the Redis listener task."""
        self.running = False
        if self.listener_task:
            self.listener_task.cancel()
            self.listener_task = None
    
    async def _listener_loop(self) -> None:
        """Redis listener loop."""
        while self.running:
            try:
                message = self.pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    channel = message["channel"].decode("utf-8")
                    data = message["data"]
                    
                    if isinstance(data, bytes):
                        data = data.decode("utf-8")
                    
                    # Parse message JSON
                    try:
                        message_data = json.loads(data)
                        message_obj = Message(**message_data)
                        
                        # Notify subscribers
                        if channel in self.subscribers:
                            for callback in self.subscribers[channel]:
                                callback(message_obj)
                    except (json.JSONDecodeError, TypeError) as e:
                        print(f"Error parsing message: {e}")
                
                # Avoid busy waiting
                await asyncio.sleep(0.01)
            except Exception as e:
                print(f"Error in Redis listener: {e}")
                await asyncio.sleep(1)  # Back off on error
    
    def close(self) -> None:
        """Close the Redis connection."""
        self.stop_listener()
        self.pubsub.close()
        self.redis_client.close()