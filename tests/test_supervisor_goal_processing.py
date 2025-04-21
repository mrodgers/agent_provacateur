"""Tests for the goal processing functionality in the ResearchSupervisorAgent."""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agent_provocateur.research_supervisor_agent import ResearchSupervisorAgent
from agent_provocateur.goal_refiner import GoalRefiner
from agent_provocateur.a2a_models import TaskRequest, TaskStatus, TaskResult
from agent_provocateur.a2a_messaging import InMemoryMessageBroker


class TestSupervisorGoalProcessing:
    """Tests for the goal processing functionality in ResearchSupervisorAgent."""
    
    @pytest.fixture
    def mock_broker(self):
        """Mock message broker for testing."""
        broker = InMemoryMessageBroker()
        return broker
    
    @pytest.fixture
    def supervisor_agent(self, mock_broker):
        """ResearchSupervisorAgent instance for testing."""
        agent = ResearchSupervisorAgent("research_supervisor_agent", mock_broker)
        return agent
    
    @pytest.mark.asyncio
    async def test_initialize_agent_capabilities(self, supervisor_agent):
        """Test that agent capabilities are initialized correctly."""
        # Call the method
        await supervisor_agent._initialize_agent_capabilities()
        
        # Verify that the capabilities were initialized
        assert "xml_agent" in supervisor_agent.agent_capabilities
        assert "web_search_agent" in supervisor_agent.agent_capabilities
        assert "research_supervisor_agent" in supervisor_agent.agent_capabilities
        
        # Verify that each agent has the expected capabilities
        assert "extract_entities" in supervisor_agent.agent_capabilities["xml_agent"]["capabilities"]
        assert "search" in supervisor_agent.agent_capabilities["web_search_agent"]["capabilities"]
        assert "coordinate_workflow" in supervisor_agent.agent_capabilities["research_supervisor_agent"]["capabilities"]
        
    @pytest.mark.asyncio
    async def test_map_task_to_intent(self, supervisor_agent):
        """Test mapping tasks to intents for various agent types."""
        # Initialize agent capabilities first
        await supervisor_agent._initialize_agent_capabilities()
        
        # Test with different task and agent combinations
        
        # XML agent tasks
        xml_task = {
            "description": "Extract entities from document",
            "capabilities": ["extract_entities"]
        }
        assert supervisor_agent._map_task_to_intent(xml_task, "xml_agent") == "extract_entities"
        
        # Web search agent tasks
        search_task = {
            "description": "Search for information",
            "capabilities": ["search"]
        }
        assert supervisor_agent._map_task_to_intent(search_task, "web_search_agent") == "search"
        
        # Research supervisor agent tasks
        research_task = {
            "description": "Coordinate research workflow",
            "capabilities": ["coordinate_workflow"]
        }
        assert supervisor_agent._map_task_to_intent(research_task, "research_supervisor_agent") == "research_document"
        
        # Test fallback to description-based mapping
        desc_task = {
            "description": "Search for machine learning",
            "capabilities": ["unknown_capability"]
        }
        assert supervisor_agent._map_task_to_intent(desc_task, "web_search_agent") == "search"
        
        # Test when no mapping is found
        unknown_task = {
            "description": "Unknown task",
            "capabilities": ["unknown_capability"]
        }
        assert supervisor_agent._map_task_to_intent(unknown_task, "xml_agent") is None
        
    @pytest.mark.asyncio
    async def test_create_task_payload(self, supervisor_agent):
        """Test creating task payloads based on task descriptions and capabilities."""
        # Initialize agent capabilities first
        await supervisor_agent._initialize_agent_capabilities()
        
        # Options to include in all payloads
        options = {"max_results": 10, "doc_id": "doc123"}
        
        # Test search task
        search_task = {
            "description": "Search for machine learning",
            "capabilities": ["search"]
        }
        search_payload = supervisor_agent._create_task_payload(search_task, options)
        assert search_payload["query"] == "Search for machine learning"
        assert search_payload["max_results"] == 10
        
        # Test entity research task
        research_task = {
            "description": "Research entity artificial intelligence",
            "capabilities": ["research_entity"]
        }
        research_payload = supervisor_agent._create_task_payload(research_task, options)
        assert research_payload["entity"] == "intelligence"  # Last word in description
        
        # Test entity extraction task
        extract_task = {
            "description": "Extract entities from document",
            "capabilities": ["extract_entities"]
        }
        extract_payload = supervisor_agent._create_task_payload(extract_task, options)
        assert extract_payload["doc_id"] == "doc123"
        
        # Test with task-specific options
        task_with_options = {
            "description": "Search with options",
            "capabilities": ["search"],
            "options": {"max_results": 5, "provider": "brave"}
        }
        options_payload = supervisor_agent._create_task_payload(task_with_options, options)
        assert options_payload["options"]["provider"] == "brave"
        assert options_payload["options"]["max_results"] == 5  # Task option overrides global option
        
    @pytest.mark.asyncio
    async def test_handle_process_goal(self, supervisor_agent):
        """Test the handle_process_goal method."""
        # Initialize the agent
        await supervisor_agent.on_startup()
        
        # Mock the goal refiner's refine_goal method
        mock_tasks = [
            {
                "task_id": "task1",
                "description": "Search for machine learning",
                "capabilities": ["search"],
                "assigned_agent": "web_search_agent"
            },
            {
                "task_id": "task2",
                "description": "Extract entities from document",
                "capabilities": ["extract_entities"],
                "assigned_agent": "xml_agent"
            }
        ]
        supervisor_agent.goal_refiner.refine_goal = AsyncMock(return_value=mock_tasks)
        
        # Mock the send_request_and_wait method
        mock_result = TaskResult(
            task_id="task1",
            status=TaskStatus.COMPLETED,
            source_agent="web_search_agent",
            target_agent="research_supervisor_agent",
            output={"query": "machine learning", "results": [{"title": "ML Article"}]}
        )
        supervisor_agent.send_request_and_wait = AsyncMock(return_value=mock_result)
        
        # Create a task request
        task_request = TaskRequest(
            task_id="test_goal",
            source_agent="test",
            target_agent="research_supervisor_agent",
            intent="process_goal",
            payload={"goal": "Research machine learning and extract entities"}
        )
        
        # Call the method
        result = await supervisor_agent.handle_process_goal(task_request)
        
        # Verify the goal refiner was called
        supervisor_agent.goal_refiner.refine_goal.assert_called_once_with(
            "Research machine learning and extract entities"
        )
        
        # Verify the send_request_and_wait method was called for each task
        assert supervisor_agent.send_request_and_wait.call_count == 2
        
        # Verify the workflow status was created and updated
        workflow_id = list(supervisor_agent.workflows.keys())[0]
        assert supervisor_agent.workflows[workflow_id]["status"] == "completed"
        assert "tasks" in supervisor_agent.workflows[workflow_id]
        assert len(supervisor_agent.workflows[workflow_id]["tasks"]) == 2
        assert "results" in supervisor_agent.workflows[workflow_id]
        
        # Verify the result structure
        assert result["workflow_id"] == workflow_id
        assert result["goal"] == "Research machine learning and extract entities"
        assert result["task_count"] == 2
        assert result["status"] == "completed"
        assert len(result["results"]) == 2