#!/usr/bin/env python3
"""
Standalone XML Command Agent that can respond to tasks from the Goal Refiner.
This agent specifically handles extracting commands from Cisco XML documentation.
"""

import asyncio
import sys
import re
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add the parent directory to the path so we can import the agent_provocateur package
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_provocateur.agent_base import BaseAgent
from agent_provocateur.a2a_models import TaskRequest
from agent_provocateur.a2a_messaging import InMemoryMessageBroker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class XmlCommandAgent(BaseAgent):
    """
    Specialized agent for extracting and processing commands from XML documentation.
    """
    
    async def on_startup(self) -> None:
        """Initialize the XML command agent."""
        self.logger.info("Starting XML Command Agent...")
        self.supported_intents = [
            "extract_entities", 
            "validate", 
            "parse_document", 
            "analyze_structure"
        ]
    
    async def handle_extract_entities(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Extract entities (commands, steps, etc.) from XML document.
        
        Args:
            task_request: The task request containing the document ID
            
        Returns:
            Dict with extracted entities
        """
        doc_id = task_request.payload.get("doc_id")
        extract_type = task_request.payload.get("extract_type", "commands")
        
        if not doc_id:
            return {
                "error": "Missing required parameter: doc_id",
                "status": "failed"
            }
        
        self.logger.info(f"Extracting {extract_type} from document: {doc_id}")
        
        try:
            # Get the XML content
            xml_content = await self.async_mcp_client.get_xml_content(doc_id)
            
            # Extract based on type
            if extract_type == "commands":
                result = await self._extract_commands(doc_id, xml_content)
                return {
                    "doc_id": doc_id,
                    "extract_type": extract_type,
                    "command_count": len(result["command_blocks"]),
                    "command_blocks": result["command_blocks"],
                    "sections": result["sections"],
                    "formatted_output": result["formatted_commands"],
                    "status": "completed"
                }
            else:
                # Generic entity extraction
                entities = self._extract_generic_entities(xml_content)
                return {
                    "doc_id": doc_id,
                    "entity_count": len(entities),
                    "entities": entities,
                    "status": "completed"
                }
                
        except Exception as e:
            self.logger.error(f"Error extracting from {doc_id}: {e}")
            return {
                "error": f"Extraction failed: {str(e)}",
                "doc_id": doc_id,
                "status": "failed"
            }
    
    async def handle_validate(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Validate XML document structure.
        
        Args:
            task_request: The task request containing the document ID
            
        Returns:
            Dict with validation results
        """
        doc_id = task_request.payload.get("doc_id")
        validation_level = task_request.payload.get("validation_level", "standard")
        
        if not doc_id:
            return {
                "error": "Missing required parameter: doc_id",
                "status": "failed"
            }
        
        self.logger.info(f"Validating document: {doc_id} (level: {validation_level})")
        
        try:
            # Get the XML content
            xml_content = await self.async_mcp_client.get_xml_content(doc_id)
            
            # Validate the XML
            is_valid, issues = self._validate_xml(xml_content, validation_level)
            
            return {
                "doc_id": doc_id,
                "is_valid": is_valid,
                "validation_level": validation_level,
                "issues": issues,
                "status": "completed"
            }
                
        except Exception as e:
            self.logger.error(f"Error validating {doc_id}: {e}")
            return {
                "error": f"Validation failed: {str(e)}",
                "doc_id": doc_id,
                "status": "failed"
            }
    
    async def _extract_commands(self, doc_id: str, xml_content: str) -> Dict[str, Any]:
        """Extract configuration commands from XML content."""
        # Extract code blocks
        command_blocks = []
        
        # Find all code blocks
        matches = re.finditer(r'<code-block>(.*?)</code-block>', xml_content, re.DOTALL)
        for i, match in enumerate(matches, 1):
            # Clean up the block (remove leading/trailing whitespace and indentation)
            block_text = match.group(1).strip()
            clean_block = "\n".join(line.strip() for line in block_text.split("\n"))
            
            # Find the section containing this code block
            section_match = re.search(r'<section id="([^"]+)">(.*?)<code-block>' + re.escape(block_text), 
                                     xml_content, re.DOTALL)
            section_id = section_match.group(1) if section_match else "unknown"
            
            # Find the title of the section
            title_match = re.search(r'<section id="' + re.escape(section_id) + 
                                   r'">\s*<title>([^<]+)</title>', xml_content)
            title = title_match.group(1) if title_match else "Unknown Section"
            
            command_blocks.append({
                "id": f"block_{i}",
                "content": clean_block,
                "section_id": section_id,
                "section_title": title
            })
            
        # Extract sections
        sections = []
        section_matches = re.finditer(r'<section id="([^"]+)">\s*<title>([^<]+)</title>', xml_content)
        for match in section_matches:
            section_id = match.group(1)
            title = match.group(2)
            
            # Find the chapter containing this section
            chapter_match = re.search(r'<chapter id="([^"]+)">(.*?)<section id="' + re.escape(section_id), 
                                     xml_content, re.DOTALL)
            chapter_id = chapter_match.group(1) if chapter_match else "unknown"
            
            # Find the chapter title
            chapter_title_match = re.search(r'<chapter id="' + re.escape(chapter_id) + 
                                          r'">\s*<title>([^<]+)</title>', xml_content)
            chapter_title = chapter_title_match.group(1) if chapter_title_match else "Unknown Chapter"
            
            sections.append({
                "id": section_id,
                "title": title,
                "chapter_id": chapter_id,
                "chapter_title": chapter_title
            })
        
        # Format the commands
        formatted_commands = self._format_commands(command_blocks, sections)
        
        return {
            "command_blocks": command_blocks,
            "sections": sections,
            "formatted_commands": formatted_commands
        }
    
    def _extract_generic_entities(self, xml_content: str) -> List[Dict[str, Any]]:
        """Extract generic entities from XML content."""
        entities = []
        
        # Extract elements with useful content
        element_matches = re.finditer(r'<([a-zA-Z0-9_-]+)(?:\s+[^>]*)?>([^<]+)</\1>', xml_content)
        
        for i, match in enumerate(entities, 1):
            element_name = match.group(1)
            content = match.group(2).strip()
            
            # Only include elements with meaningful content
            if content and len(content) > 3:
                entities.append({
                    "id": f"entity_{i}",
                    "element": element_name,
                    "content": content,
                    "confidence": 0.7
                })
        
        return entities
    
    def _validate_xml(self, xml_content: str, validation_level: str) -> tuple:
        """Validate XML content."""
        # Simple validation check - in a real system, this would use proper XML validation
        is_valid = True
        issues = []
        
        # Check for well-formedness
        if not xml_content.startswith('<?xml'):
            is_valid = False
            issues.append({"severity": "error", "message": "Missing XML declaration"})
        
        # Check for balanced tags (very simplified)
        opening_tags = re.findall(r'<([a-zA-Z0-9_-]+)[^/>]*>', xml_content)
        closing_tags = re.findall(r'</([a-zA-Z0-9_-]+)>', xml_content)
        
        if len(opening_tags) != len(closing_tags):
            is_valid = False
            issues.append({
                "severity": "error", 
                "message": f"Unbalanced tags: {len(opening_tags)} opening vs {len(closing_tags)} closing"
            })
        
        # Add additional checks for higher validation levels
        if validation_level in ["strict", "full"]:
            # Check for namespace declarations
            if 'xmlns' not in xml_content:
                issues.append({
                    "severity": "warning", 
                    "message": "No namespace declarations found"
                })
            
            # Check for XML schema references
            if 'schemaLocation' not in xml_content:
                issues.append({
                    "severity": "warning", 
                    "message": "No XML Schema references found"
                })
        
        return is_valid, issues
    
    def _format_commands(self, command_blocks: List[Dict[str, str]], 
                       sections: List[Dict[str, str]]) -> str:
        """Format extracted commands in a readable form."""
        output = "# CISCO ROUTER CONFIGURATION COMMANDS\n\n"
        
        # Group commands by chapter
        commands_by_chapter = {}
        for block in command_blocks:
            # Find the chapter for this block
            section_id = block["section_id"]
            chapter_id = next((s["chapter_id"] for s in sections if s["id"] == section_id), "unknown")
            chapter_title = next((s["chapter_title"] for s in sections if s["id"] == section_id), "Unknown")
            
            if chapter_id not in commands_by_chapter:
                commands_by_chapter[chapter_id] = {
                    "title": chapter_title,
                    "sections": {}
                }
                
            if section_id not in commands_by_chapter[chapter_id]["sections"]:
                commands_by_chapter[chapter_id]["sections"][section_id] = {
                    "title": block["section_title"],
                    "commands": []
                }
                
            commands_by_chapter[chapter_id]["sections"][section_id]["commands"].append(block["content"])
        
        # Format the output
        for chapter_id, chapter_data in commands_by_chapter.items():
            output += f"## {chapter_data['title']}\n\n"
            
            for section_id, section_data in chapter_data["sections"].items():
                output += f"### {section_data['title']}\n\n"
                
                for i, commands in enumerate(section_data["commands"], 1):
                    output += f"```\n{commands}\n```\n\n"
                    
        return output

async def main():
    """Run the XML Command Agent."""
    # Create message broker
    broker = InMemoryMessageBroker()
    
    # Create and start the agent
    agent = XmlCommandAgent("xml_agent", broker)
    await agent.start()
    
    try:
        print(f"XML Command Agent running with ID: {agent.agent_id}")
        print("Waiting for tasks... (Press Ctrl+C to exit)")
        
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())