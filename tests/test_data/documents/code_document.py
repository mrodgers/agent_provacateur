"""Sample code document for testing.

This file demonstrates a Python code document that can be loaded
and processed by the agent_provocateur framework.
"""

from typing import Dict, List, Optional


class ExampleAgent:
    """An example agent implementation."""
    
    def __init__(self, agent_id: str) -> None:
        """Initialize the agent.
        
        Args:
            agent_id: The unique identifier for this agent
        """
        self.agent_id = agent_id
        self.messages = []
    
    async def handle_message(self, message: Dict) -> Optional[Dict]:
        """Process an incoming message.
        
        Args:
            message: The message to process
            
        Returns:
            Optional response message
        """
        self.messages.append(message)
        
        # Process message logic would go here
        response = {"status": "received", "agent_id": self.agent_id}
        
        return response


def main() -> None:
    """Example usage of the ExampleAgent class."""
    agent = ExampleAgent("example_agent_1")
    print(f"Created agent with ID: {agent.agent_id}")


if __name__ == "__main__":
    main()