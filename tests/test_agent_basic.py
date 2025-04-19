"""Basic agent tests without using the full agent-to-agent system."""

import os
import sys
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent_provocateur.a2a_models import TaskRequest


class TestAgentHandlers:
    """Test agent handlers directly without using the full agent system."""
    
    async def handle_test_task(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Handle a test task."""
        return {"success": True, "data": task_request.payload}
    
    async def handle_error_task(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Handle a task that raises an error."""
        raise ValueError("Test error")


def test_successful_handler():
    """Test a successful task handler."""
    agent = TestAgentHandlers()
    task_request = TaskRequest(
        task_id="test_task_1",
        intent="test_task",
        payload={"test_key": "test_value"},
        source_agent="agent1",
        target_agent="agent2",
    )
    
    # Call handler directly and get future
    future = agent.handle_test_task(task_request)
    
    # Run the future to get the result
    import asyncio
    result = asyncio.run(future)
    
    # Check result
    assert result == {"success": True, "data": {"test_key": "test_value"}}


def test_error_handler():
    """Test an error-raising task handler."""
    agent = TestAgentHandlers()
    task_request = TaskRequest(
        task_id="test_task_2",
        intent="error_task",
        payload={"test_key": "test_value"},
        source_agent="agent1",
        target_agent="agent2",
    )
    
    # Call handler directly and get future
    future = agent.handle_error_task(task_request)
    
    # Run the future and check for error
    import asyncio
    try:
        asyncio.run(future)
        assert False, "Expected ValueError but no exception was raised"
    except ValueError as e:
        assert str(e) == "Test error"