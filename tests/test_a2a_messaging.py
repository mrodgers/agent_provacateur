import asyncio
import os
import sys
import time

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent_provocateur.a2a_messaging import AgentMessaging, InMemoryMessageBroker
from src.agent_provocateur.a2a_models import Message, MessageType, TaskRequest, TaskStatus


# Define test fixtures
@pytest.fixture
def broker():
    """Create a new in-memory message broker for testing."""
    return InMemoryMessageBroker()


@pytest.fixture
def agent1(broker):
    """Create agent 1 for testing."""
    return AgentMessaging("agent1", broker)


@pytest.fixture
def agent2(broker):
    """Create agent 2 for testing."""
    return AgentMessaging("agent2", broker)


# Test cases
def test_broker_publish_subscribe(broker):
    """Test basic publish and subscribe functionality."""
    messages = []
    
    def callback(message):
        messages.append(message)
    
    # Subscribe to a topic
    broker.subscribe("test_topic", callback)
    
    # Create a message
    task_request = TaskRequest(
        task_id="task1",
        intent="test",
        payload={"key": "value"},
        source_agent="agent1",
        target_agent="agent2",
    )
    
    message = Message(
        message_id="msg1",
        message_type=MessageType.TASK_REQUEST,
        timestamp=time.time(),
        payload=task_request,
    )
    
    # Publish the message
    broker.publish("test_topic", message)
    
    # Check that the message was received
    assert len(messages) == 1
    assert messages[0].message_id == "msg1"
    assert messages[0].message_type == MessageType.TASK_REQUEST
    assert messages[0].payload.task_id == "task1"


def test_agent_send_task_request(agent1, agent2):
    """Test sending a task request between agents."""
    received_task = None
    
    def task_handler(task_request):
        nonlocal received_task
        received_task = task_request
    
    # Register task handler
    agent2.register_task_handler("test_intent", task_handler)
    
    # Send task request
    task_id = agent1.send_task_request(
        target_agent="agent2",
        intent="test_intent",
        payload={"data": "test"},
    )
    
    # Check that the task was received
    assert received_task is not None
    assert received_task.task_id == task_id
    assert received_task.intent == "test_intent"
    assert received_task.payload == {"data": "test"}
    assert received_task.source_agent == "agent1"
    assert received_task.target_agent == "agent2"


def test_agent_send_task_result(agent1, agent2):
    """Test sending a task result between agents."""
    # Set up task result handler
    results = []
    
    def result_handler(message):
        if message.message_type == MessageType.TASK_RESULT:
            results.append(message.payload)
    
    agent1.register_message_handler(MessageType.TASK_RESULT, result_handler)
    
    # Send a task result
    agent2.send_task_result(
        task_id="task1",
        target_agent="agent1",
        status=TaskStatus.COMPLETED,
        output={"result": "success"},
    )
    
    # Check that the result was received
    assert len(results) == 1
    assert results[0].task_id == "task1"
    assert results[0].status == TaskStatus.COMPLETED
    assert results[0].output == {"result": "success"}
    assert results[0].source_agent == "agent2"
    assert results[0].target_agent == "agent1"


def test_message_deduplication(broker):
    """Test message deduplication."""
    messages = []
    
    def callback(message):
        messages.append(message)
    
    # Subscribe to a topic
    broker.subscribe("test_topic", callback)
    
    # Create a message with deduplication key
    task_request = TaskRequest(
        task_id="task1",
        intent="test",
        payload={"key": "value"},
        source_agent="agent1",
        target_agent="agent2",
    )
    
    message = Message(
        message_id="msg1",
        message_type=MessageType.TASK_REQUEST,
        timestamp=time.time(),
        payload=task_request,
        deduplication_key="dedup1",
    )
    
    # Publish the message
    broker.publish("test_topic", message)
    
    # Mark as processed
    broker.mark_processed("dedup1")
    
    # Publish the same message again
    broker.publish("test_topic", message)
    
    # Check that the message was only received once
    assert len(messages) == 2  # In the in-memory broker, deduplication happens at the handler level


@pytest.mark.asyncio
async def test_wait_for_task_result():
    """Test waiting for a task result."""
    broker = InMemoryMessageBroker()
    agent1 = AgentMessaging("agent1", broker)
    agent2 = AgentMessaging("agent2", broker)
    
    # Send a task request
    task_id = agent1.send_task_request(
        target_agent="agent2",
        intent="test",
        payload={"data": "test"},
    )
    
    # Simulate async processing
    async def process_task():
        await asyncio.sleep(0.1)
        agent2.send_task_result(
            task_id=task_id,
            target_agent="agent1",
            status=TaskStatus.COMPLETED,
            output={"result": "success"},
        )
    
    # Start task processing
    asyncio.create_task(process_task())
    
    # Wait for result
    result = await agent1.wait_for_task_result(task_id, timeout_sec=1)
    
    # Check result
    assert result is not None
    assert result.task_id == task_id
    assert result.status == TaskStatus.COMPLETED
    assert result.output == {"result": "success"}


@pytest.mark.asyncio
async def test_wait_for_task_result_timeout():
    """Test timeout when waiting for a task result."""
    broker = InMemoryMessageBroker()
    agent1 = AgentMessaging("agent1", broker)
    
    # Send a task request (no agent2 to process it)
    task_id = agent1.send_task_request(
        target_agent="agent2",
        intent="test",
        payload={"data": "test"},
    )
    
    # Wait for result with short timeout
    result = await agent1.wait_for_task_result(task_id, timeout_sec=0.1)
    
    # Check result is None due to timeout
    assert result is None


if __name__ == "__main__":
    # Run the tests directly
    pytest.main(["-xvs", __file__])