#!/usr/bin/env python3
"""
Cisco XML Agent - Specialized agent for extracting and processing commands from Cisco XML documentation.

This agent provides functionality to:
1. Extract configuration commands from Cisco XML guides
2. Categorize and explain Cisco IOS commands
3. Generate command summaries and usage examples
4. Create structured output for command documentation

Usage:
  ./cisco_xml_agent.py extract DOC_ID      # Extract configuration commands
  ./cisco_xml_agent.py categorize DOC_ID    # Categorize commands by function
  ./cisco_xml_agent.py summarize DOC_ID     # Generate human-readable summaries
  ./cisco_xml_agent.py format DOC_ID        # Format commands for documentation
"""

import asyncio
import sys
import re
import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add the parent directory to the path so we can import the agent_provocateur package
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_provocateur.agent_base import BaseAgent
from agent_provocateur.a2a_models import TaskRequest
from agent_provocateur.a2a_messaging import InMemoryMessageBroker
from agent_provocateur.mcp_client import McpClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class CiscoXmlAgent(BaseAgent):
    """
    Specialized agent for extracting and processing commands from Cisco XML documentation.
    """
    
    async def on_startup(self) -> None:
        """Initialize the Cisco XML agent."""
        self.logger.info("Starting Cisco XML Agent...")
        self.supported_intents = [
            "extract_commands",
            "categorize_commands",
            "summarize_commands",
            "format_commands"
        ]
        
        # Initialize MCP client for document access
        self.client = McpClient(base_url="http://localhost:8000")
    
    async def handle_extract_commands(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Extract configuration commands from Cisco XML document.
        
        Args:
            task_request: The task request containing the document ID
            
        Returns:
            Dict with extracted commands
        """
        doc_id = task_request.payload.get("doc_id")
        if not doc_id:
            raise ValueError("Missing required parameter: doc_id")
        
        # Get XML content
        try:
            xml_content = await self.client.get_xml_content(doc_id)
        except Exception as e:
            self.logger.error(f"Error fetching XML content: {e}")
            return {"error": f"Error fetching XML content: {str(e)}"}
        
        # Extract code blocks containing commands
        code_blocks = self._extract_code_blocks(xml_content)
        
        # Process and clean up command blocks
        processed_commands = []
        for i, block in enumerate(code_blocks, 1):
            # Clean up the block (remove leading/trailing whitespace and indentation)
            clean_block = "\n".join(line.strip() for line in block.strip().split("\n"))
            
            # Add to processed commands
            processed_commands.append({
                "block_id": i,
                "commands": clean_block,
                "line_count": len(clean_block.split("\n"))
            })
        
        return {
            "doc_id": doc_id,
            "command_count": len(processed_commands),
            "commands": processed_commands
        }
    
    async def handle_categorize_commands(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Categorize Cisco commands by functionality.
        
        Args:
            task_request: The task request containing the document ID
            
        Returns:
            Dict with categorized commands
        """
        # First extract the commands
        extract_result = await self.handle_extract_commands(task_request)
        
        if "error" in extract_result:
            return extract_result
        
        # Combine all command blocks for analysis
        all_commands = "\n\n".join([cmd["commands"] for cmd in extract_result["commands"]])
        
        # Use LLM to categorize the commands
        try:
            prompt = f"""
            Analyze the following Cisco IOS configuration commands and categorize them by functionality.
            For each category, list the commands that belong to it and provide a brief explanation.
            
            Commands:
            {all_commands}
            
            Output as JSON with the following structure:
            {{
                "categories": [
                    {{
                        "name": "category_name",
                        "description": "brief description",
                        "commands": [
                            {{
                                "command": "command text",
                                "purpose": "what this command does"
                            }}
                        ]
                    }}
                ]
            }}
            """
            
            response = await self.client.generate_text(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.2
            )
            
            # Extract JSON from response
            try:
                result = json.loads(response.content)
                return {
                    "doc_id": extract_result["doc_id"],
                    "categorized_commands": result
                }
            except json.JSONDecodeError:
                # If not valid JSON, return the raw response
                return {
                    "doc_id": extract_result["doc_id"],
                    "categorization": response.content
                }
                
        except Exception as e:
            self.logger.error(f"Error categorizing commands: {e}")
            return {"error": f"Error categorizing commands: {str(e)}"}
    
    async def handle_summarize_commands(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Generate human-readable summaries of Cisco commands.
        
        Args:
            task_request: The task request containing the document ID
            
        Returns:
            Dict with command summaries
        """
        # First extract the commands
        extract_result = await self.handle_extract_commands(task_request)
        
        if "error" in extract_result:
            return extract_result
        
        # Combine all command blocks for analysis
        all_commands = "\n\n".join([cmd["commands"] for cmd in extract_result["commands"]])
        
        # Use LLM to generate a summary
        try:
            prompt = f"""
            Summarize the following Cisco router configuration commands in a structured format.
            Explain what these commands achieve collectively, their purpose, and any potential implications.
            If possible, identify the network scenario these commands are designed for.
            
            Commands:
            {all_commands}
            """
            
            response = await self.client.generate_text(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3
            )
            
            return {
                "doc_id": extract_result["doc_id"],
                "summary": response.content
            }
                
        except Exception as e:
            self.logger.error(f"Error summarizing commands: {e}")
            return {"error": f"Error summarizing commands: {str(e)}"}
    
    async def handle_format_commands(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Format Cisco commands for documentation.
        
        Args:
            task_request: The task request containing the document ID
            
        Returns:
            Dict with formatted commands for documentation
        """
        format_type = task_request.payload.get("format", "markdown")
        
        # First extract the commands
        extract_result = await self.handle_extract_commands(task_request)
        
        if "error" in extract_result:
            return extract_result
        
        # Format the commands based on the requested format
        if format_type == "markdown":
            formatted_content = self._format_markdown(extract_result)
        elif format_type == "html":
            formatted_content = self._format_html(extract_result)
        elif format_type == "json":
            formatted_content = json.dumps(extract_result, indent=2)
        else:
            formatted_content = self._format_text(extract_result)
        
        return {
            "doc_id": extract_result["doc_id"],
            "format": format_type,
            "formatted_content": formatted_content
        }
    
    def _extract_code_blocks(self, xml_content: str) -> List[str]:
        """
        Extract code blocks from XML content.
        
        Args:
            xml_content: The XML content to extract code blocks from
            
        Returns:
            List of code blocks
        """
        # Extract code blocks using regex
        code_blocks = re.findall(r'<code-block>(.*?)</code-block>', xml_content, re.DOTALL)
        
        # If no code blocks found, try alternative tags
        if not code_blocks:
            # Try command blocks
            code_blocks = re.findall(r'<command>(.*?)</command>', xml_content, re.DOTALL)
        
        if not code_blocks:
            # Try pre-formatted blocks
            code_blocks = re.findall(r'<pre>(.*?)</pre>', xml_content, re.DOTALL)
            
        if not code_blocks:
            # Last resort: try to find command-like patterns in the content
            # Look for lines that start with router prompts
            lines = xml_content.split('\n')
            current_block = []
            all_blocks = []
            
            in_block = False
            for line in lines:
                if re.match(r'^\s*(Router|Switch|R\d+|S\d+)[#>]', line):
                    in_block = True
                    current_block.append(line)
                elif in_block and line.strip() and not line.strip().startswith('<'):
                    current_block.append(line)
                elif in_block and (not line.strip() or line.strip().startswith('<')):
                    if current_block:
                        all_blocks.append('\n'.join(current_block))
                        current_block = []
                    in_block = False
            
            if current_block:
                all_blocks.append('\n'.join(current_block))
            
            if all_blocks:
                code_blocks = all_blocks
        
        return code_blocks
    
    def _format_markdown(self, extract_result: Dict[str, Any]) -> str:
        """Format commands as Markdown."""
        md = f"# Cisco Configuration Commands\n\n"
        md += f"Document ID: {extract_result['doc_id']}\n\n"
        md += f"Total command blocks: {extract_result['command_count']}\n\n"
        
        for cmd in extract_result["commands"]:
            md += f"## Command Block {cmd['block_id']}\n\n"
            md += "```\n"
            md += cmd["commands"]
            md += "\n```\n\n"
        
        return md
    
    def _format_html(self, extract_result: Dict[str, Any]) -> str:
        """Format commands as HTML."""
        html = f"<h1>Cisco Configuration Commands</h1>\n"
        html += f"<p>Document ID: {extract_result['doc_id']}</p>\n"
        html += f"<p>Total command blocks: {extract_result['command_count']}</p>\n\n"
        
        for cmd in extract_result["commands"]:
            html += f"<h2>Command Block {cmd['block_id']}</h2>\n"
            html += "<pre><code>\n"
            html += cmd["commands"].replace("<", "&lt;").replace(">", "&gt;")
            html += "\n</code></pre>\n"
        
        return html
    
    def _format_text(self, extract_result: Dict[str, Any]) -> str:
        """Format commands as plain text."""
        text = f"CISCO CONFIGURATION COMMANDS\n"
        text += f"Document ID: {extract_result['doc_id']}\n"
        text += f"Total command blocks: {extract_result['command_count']}\n\n"
        
        for cmd in extract_result["commands"]:
            text += f"Command Block {cmd['block_id']}:\n"
            text += "-" * 40 + "\n"
            text += cmd["commands"] + "\n"
            text += "-" * 40 + "\n\n"
        
        return text


async def extract_configuration_commands(doc_id):
    """Extract configuration commands from the Cisco guide XML."""
    # Create agent
    agent = CiscoXmlAgent()
    await agent.on_startup()
    
    # Create task request
    request = TaskRequest(
        task_id=f"task_{doc_id}",
        intent="extract_commands",
        payload={"doc_id": doc_id}
    )
    
    # Process extraction
    result = await agent.handle_extract_commands(request)
    
    # Print results
    print(f"Found {result.get('command_count', 0)} command blocks")
    print("\n=== Configuration Commands ===\n")
    
    for cmd in result.get("commands", []):
        print(f"Command Block {cmd['block_id']}:")
        print("-------------------")
        print(cmd["commands"])
        print("-------------------\n")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Cisco XML Agent for extracting and processing configuration commands",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Extract commands
    extract_parser = subparsers.add_parser("extract", help="Extract configuration commands")
    extract_parser.add_argument("doc_id", help="Document ID")
    extract_parser.add_argument("--json", action="store_true", help="Output in JSON format")
    
    # Categorize commands
    categorize_parser = subparsers.add_parser("categorize", help="Categorize commands by function")
    categorize_parser.add_argument("doc_id", help="Document ID")
    
    # Summarize commands
    summarize_parser = subparsers.add_parser("summarize", help="Generate human-readable summaries")
    summarize_parser.add_argument("doc_id", help="Document ID")
    
    # Format commands
    format_parser = subparsers.add_parser("format", help="Format commands for documentation")
    format_parser.add_argument("doc_id", help="Document ID")
    format_parser.add_argument("--format", choices=["markdown", "html", "json", "text"], 
                             default="markdown", help="Output format")
    
    args = parser.parse_args()
    
    # Create agent
    agent = CiscoXmlAgent()
    await agent.on_startup()
    
    if args.command == "extract":
        # Create task request
        request = TaskRequest(
            task_id=f"task_{args.doc_id}",
            intent="extract_commands",
            payload={"doc_id": args.doc_id}
        )
        
        # Process extraction
        result = await agent.handle_extract_commands(request)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Found {result.get('command_count', 0)} command blocks")
            print("\n=== Configuration Commands ===\n")
            
            for cmd in result.get("commands", []):
                print(f"Command Block {cmd['block_id']}:")
                print("-------------------")
                print(cmd["commands"])
                print("-------------------\n")
    
    elif args.command == "categorize":
        # Create task request
        request = TaskRequest(
            task_id=f"task_{args.doc_id}",
            intent="categorize_commands",
            payload={"doc_id": args.doc_id}
        )
        
        # Process categorization
        result = await agent.handle_categorize_commands(request)
        
        if "error" in result:
            print(f"Error: {result['error']}")
        elif "categorized_commands" in result:
            print(json.dumps(result["categorized_commands"], indent=2))
        else:
            print(result.get("categorization", "No categorization available"))
    
    elif args.command == "summarize":
        # Create task request
        request = TaskRequest(
            task_id=f"task_{args.doc_id}",
            intent="summarize_commands",
            payload={"doc_id": args.doc_id}
        )
        
        # Process summarization
        result = await agent.handle_summarize_commands(request)
        
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print("\n=== Command Summary ===\n")
            print(result.get("summary", "No summary available"))
    
    elif args.command == "format":
        # Create task request
        request = TaskRequest(
            task_id=f"task_{args.doc_id}",
            intent="format_commands",
            payload={"doc_id": args.doc_id, "format": args.format}
        )
        
        # Process formatting
        result = await agent.handle_format_commands(request)
        
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(result.get("formatted_content", "No formatted content available"))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    import argparse
    asyncio.run(main())