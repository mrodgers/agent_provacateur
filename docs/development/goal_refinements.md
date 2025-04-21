✅ Summary: What We’re Building

A Goal Refinement & Context Modeling Tool that allows the Supervisor Agent to:
	•	Interpret a high-level goal or prompt.
	•	Break it into structured tasks (tree format).
	•	Dynamically interact with the user for refinement.
	•	Map sub-tasks to available tools or agents.

⸻

🧱 Architectural Fit

📍 Existing Modules to Leverage
	•	supervisor.py (or equivalent): Primary coordinator.
	•	a2a/messaging.py: For delegation and tool dispatch.
	•	mcp_client/: Tool registry & metadata—can be extended for capability matching.
	•	goals.json or other config storage: Can track user intent trees.

⸻

🛠️ Implementation Plan

1. Add GoalRefiner Agent or Submodule

Create a dedicated GoalRefiner component or behavior within the Supervisor Agent.

# agent_provocateur/agents/goal_refiner.py

class GoalRefiner:
    def __init__(self, agent_capabilities: dict):
        self.agent_capabilities = agent_capabilities

    def refine(self, high_level_goal: str) -> List[Dict]:
        # Use langchain or LLMClient to break down the goal into sub-tasks
        plan = langgraph_generate_task_tree(high_level_goal)
        return self.map_to_agents(plan)

    def map_to_agents(self, plan: List[Dict]) -> List[Dict]:
        for step in plan:
            step['agent'] = self.find_matching_agent(step['action'])
        return plan

Use langgraph or similar for multi-step prompting or tree-based decision making.

⸻

2. Update Supervisor Agent Logic

Incorporate GoalRefiner as a sub-agent or method inside Supervisor’s plan-execute loop.

# agent_provocateur/agents/supervisor.py

from agent_provocateur.agents.goal_refiner import GoalRefiner

class Supervisor:
    def __init__(self):
        self.goal_refiner = GoalRefiner(self.agent_registry())

    def process_user_goal(self, user_input: str):
        structured_tasks = self.goal_refiner.refine(user_input)
        for task in structured_tasks:
            self.delegate(task)



⸻

3. Create Interactive Clarification Mode

Allow Supervisor to call back to the user for disambiguation if:
	•	Tasks are vague or missing entities
	•	A match is not found in the agent registry

Use A2A or CLI prompt fallback:

if not task['agent']:
    clarification = prompt_user(f"Can you clarify: {task['description']}?")
    task['description'] = clarification



⸻

4. Tree-Based Task Tracking (Optional v2)

Use a simple TaskTree structure to manage hierarchy and dependency between subtasks.

class TaskNode:
    def __init__(self, description, agent=None, children=[]):
        ...

Render this as JSON or Graphviz for visualization in the frontend later.

⸻

5. Agent/Tool Capability Registry (Metadata Matching)

Extend the MCP tool mock registry to describe:
	•	What inputs each tool accepts
	•	What it can solve (e.g., “summarize”, “compare”, “extract features”)

You can do this in JSON, YAML, or inline Python:

{
  "doc_parser": { "capabilities": ["extract entities", "compare versions"] },
  "search_tool": { "capabilities": ["find external sources"] }
}

Then match:

def find_matching_agent(action_text):
    for agent, meta in registry.items():
        if action_text in meta['capabilities']:
            return agent



⸻

📊 Optional Enhancements
	•	LangGraph Planner Node: Turn GoalRefiner into a LangGraph node for better explainability and retries.
	•	Frontend Tree Editor: Let the user drag-and-drop or approve goal decomposition in a future GUI.
	•	Memory: Cache goal decomposition and user clarifications to prevent re-asking.

⸻

✅ Why This Is a Clean Fit
	•	MCP & A2A already exist – just need better goal modeling.
	•	Supervisor is modular – easy to insert the refiner before tool execution.
	•	Tool mocking is well structured – metadata matching is straightforward.
