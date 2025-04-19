import asyncio
import os
import sys
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent_provocateur.a2a_messaging import InMemoryMessageBroker
from src.agent_provocateur.a2a_models import TaskRequest, TaskStatus
from src.agent_provocateur.agent_base import BaseAgent


# Define a test agent that implements task handlers
class MockAgent(BaseAgent):
    """Test agent implementation for testing."""
    
    async def handle_test_task(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Handle a test task."""
        return {"success": True, "data": task_request.payload}
    
    async def handle_error_task(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Handle a task that raises an error."""
        raise ValueError("Test error")


# Define test fixtures
@pytest.fixture
def broker():
    """Create a new in-memory message broker for testing."""
    return InMemoryMessageBroker()


@pytest.fixture
async def agent1(broker):
    """Create agent 1 for testing."""
    agent = MockAgent("agent1", broker)
    await agent.start()
    yield agent
    await agent.stop()


@pytest.fixture
async def agent2(broker):
    """Create agent 2 for testing."""
    agent = MockAgent("agent2", broker)
    await agent.start()
    yield agent
    await agent.stop()


# Test cases
@pytest.mark.asyncio
async def test_agent_initialization(broker):
    """Test agent initialization."""
    agent = MockAgent("test_agent", broker)
    
    assert agent.agent_id == "test_agent"
    assert agent.messaging is not None
    assert agent.mcp_client is not None
    assert agent.async_mcp_client is not None
    assert agent.logger is not None


@pytest.mark.asyncio
async def test_agent_heartbeat(broker):
    """Test agent heartbeat."""
    agent = MockAgent("test_agent", broker)
    
    # Mock the messaging module
    agent.messaging.send_heartbeat = MagicMock()
    
    # Set shorter heartbeat interval for testing
    agent.heartbeat_interval_sec = 0.1
    
    # Start agent
    await agent.start()
    
    # Wait for at least one heartbeat
    await asyncio.sleep(0.2)
    
    # Stop agent
    await agent.stop()
    
    # Check that heartbeat was sent
    agent.messaging.send_heartbeat.assert_called()


@pytest.mark.asyncio
async def test_agent_task_handling(agent1, agent2):
    """Test agent task handling."""
    result = await agent1.send_request_and_wait(
        target_agent="agent2",
        intent="test_task",
        payload={"test_key": "test_value"},
        timeout_sec=1,
    )
    
    assert result is not None
    assert result.status == TaskStatus.COMPLETED
    assert result.output == {"success": True, "data": {"test_key": "test_value"}}


@pytest.mark.asyncio
async def test_agent_error_handling(agent1, agent2):
    """Test agent error handling."""
    result = await agent1.send_request_and_wait(
        target_agent="agent2",
        intent="error_task",
        payload={"test_key": "test_value"},
        timeout_sec=1,
    )
    
    assert result is not None
    assert result.status == TaskStatus.FAILED
    assert "Test error" in result.error


@pytest.mark.asyncio
async def test_agent_unknown_intent(agent1, agent2):
    """Test handling of unknown intents."""
    result = await agent1.send_request_and_wait(
        target_agent="agent2",
        intent="unknown_intent",
        payload={"test_key": "test_value"},
        timeout_sec=1,
    )
    
    assert result is not None
    assert result.status == TaskStatus.FAILED
    assert "No handler found for intent" in result.error


if __name__ == "__main__":
    # Run the tests directly
    pytest.main(["-xvs", __file__])