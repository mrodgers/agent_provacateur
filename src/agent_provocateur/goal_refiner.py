"""Goal Refiner for decomposing high-level goals into structured tasks."""

from typing import Any, Dict, List, Optional, Union
import logging
import uuid
import datetime

from agent_provocateur.models import Source, SourceType
from agent_provocateur.a2a_models import TaskRequest, TaskStatus

logger = logging.getLogger(__name__)

class GoalRefiner:
    """
    Handles the decomposition and refinement of high-level goals into
    structured tasks mapped to specific agent capabilities.
    """
    
    def __init__(self, agent_capabilities: Dict[str, Dict[str, Any]], mcp_client=None) -> None:
        """
        Initialize the goal refiner with agent capabilities.
        
        Args:
            agent_capabilities: Dictionary mapping agent IDs to their capabilities
            mcp_client: Optional MCP client for LLM interactions
        """
        self.agent_capabilities = agent_capabilities
        self.mcp_client = mcp_client
        self.logger = logging.getLogger(__name__)
        
    async def refine_goal(self, high_level_goal: str) -> List[Dict[str, Any]]:
        """
        Refine a high-level goal into structured tasks.
        
        Args:
            high_level_goal: The user's high-level goal or request
            
        Returns:
            List of task definitions with agent assignments
        """
        self.logger.info(f"Refining goal: {high_level_goal}")
        
        # Use LLM to parse the high-level goal
        task_tree = await self._generate_task_tree(high_level_goal)
        
        # Map tasks to agents based on capabilities
        mapped_tasks = self._map_tasks_to_agents(task_tree)
        
        return mapped_tasks
    
    async def _generate_task_tree(self, high_level_goal: str) -> List[Dict[str, Any]]:
        """
        Generate a tree of tasks from a high-level goal using an LLM.
        
        Args:
            high_level_goal: The user's high-level goal
            
        Returns:
            List of task definitions
        """
        # Use MCP client to call LLM for goal decomposition
        if self.mcp_client:
            # Define the system prompt for task decomposition
            system_prompt = """
            Analyze the user's goal and break it down into a structured set of tasks.
            For each task, provide:
            1. A clear description
            2. Required capabilities (e.g., "search", "summarize", "compare", "extract_entities")
            3. Dependencies on other tasks, if any
            4. Priority (1-5, where 1 is highest)
            
            Format your response as JSON with an array of tasks.
            """
            
            # Call LLM with goal as prompt
            response = await self.mcp_client.generate_text(
                prompt=high_level_goal,
                system_prompt=system_prompt,
                temperature=0.1,  # Low temperature for more deterministic output
                max_tokens=1000,
                provider="native",  # Use the default LLM provider
                model=None  # Use default model
            )
            
            try:
                # Parse JSON response
                import json
                tasks = json.loads(response.text)
                self.logger.info(f"Generated {len(tasks)} tasks from goal")
                return tasks
            except Exception as e:
                self.logger.error(f"Error parsing LLM task output: {e}")
                # Fall back to simplified task structure
                return self._generate_fallback_tasks(high_level_goal)
        else:
            # If no MCP client, use fallback method
            return self._generate_fallback_tasks(high_level_goal)
    
    def _generate_fallback_tasks(self, high_level_goal: str) -> List[Dict[str, Any]]:
        """
        Generate basic tasks without using an LLM.
        
        Args:
            high_level_goal: The user's high-level goal
            
        Returns:
            List of task definitions
        """
        # Simple fallback that creates a generic task
        self.logger.info("Using fallback task generation")
        
        # Create a single task with the goal as description
        return [{
            "task_id": str(uuid.uuid4()),
            "description": high_level_goal,
            "capabilities": ["process_text", "search", "analyze"],
            "dependencies": [],
            "priority": 1
        }]
    
    def _map_tasks_to_agents(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Map tasks to specific agents based on required capabilities.
        
        Args:
            tasks: List of task definitions
            
        Returns:
            List of tasks with agent assignments
        """
        mapped_tasks = []
        
        for task in tasks:
            task_capabilities = task.get("capabilities", [])
            
            # Find the most suitable agent
            assigned_agent = self._find_matching_agent(task_capabilities)
            
            # Add agent assignment to task
            task_with_agent = task.copy()
            task_with_agent["assigned_agent"] = assigned_agent
            
            mapped_tasks.append(task_with_agent)
            
            self.logger.info(f"Mapped task '{task.get('description', '')}' to agent '{assigned_agent}'")
        
        return mapped_tasks
    
    def _find_matching_agent(self, required_capabilities: List[str]) -> str:
        """
        Find the best agent to handle the given capabilities.
        
        Args:
            required_capabilities: List of capabilities required for the task
            
        Returns:
            Agent ID of the best matching agent
        """
        if not required_capabilities:
            return "research_supervisor_agent"  # Default agent
        
        # Score each agent based on capability match
        best_score = 0  # Start at 0 to ensure we only match if there's at least one capability match
        best_agent = "research_supervisor_agent"  # Default agent
        
        for agent_id, agent_info in self.agent_capabilities.items():
            agent_caps = agent_info.get("capabilities", [])
            
            # Count how many required capabilities this agent supports
            score = sum(1 for cap in required_capabilities if cap in agent_caps)
            
            # Choose the agent with the highest score
            if score > best_score:
                best_score = score
                best_agent = agent_id
        
        # If no capabilities match any agent, use the supervisor as fallback
        if best_score == 0:
            return "research_supervisor_agent"
            
        return best_agent
    
    async def prompt_for_clarification(self, task_description: str) -> str:
        """
        Use the LLM to generate a clarification question for an ambiguous task.
        
        Args:
            task_description: The ambiguous task description
            
        Returns:
            A clarification question
        """
        if self.mcp_client:
            system_prompt = """
            The user has provided a task description that needs clarification.
            Generate a clear, specific question that will help disambiguate the task.
            Focus on getting information about:
            - What exactly needs to be done
            - What entities or data are involved
            - What the output should look like
            """
            
            response = await self.mcp_client.generate_text(
                prompt=f"Generate a clarification question for this task: {task_description}",
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=100
            )
            
            return response.text.strip()
        else:
            # Fallback without LLM
            return f"Could you please clarify what you mean by '{task_description}'?"