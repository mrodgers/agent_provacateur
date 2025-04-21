#!/usr/bin/env python3
"""
Script for extracting Cisco router configuration commands.
This script shows how we can implement a task handler for the specific goal
of extracting configuration commands from Cisco documentation.
"""

import asyncio
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Any

# Add the parent directory to the path so we can import the agent_provocateur package
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_provocateur.mcp_client import McpClient

class CiscoCommandExtractor:
    """
    Extracts and formats Cisco router configuration commands from XML documentation.
    """
    
    def __init__(self, mcp_client):
        """Initialize with an MCP client."""
        self.mcp_client = mcp_client
    
    async def extract_commands(self, doc_id: str) -> Dict[str, Any]:
        """
        Extract configuration commands from Cisco router guide XML.
        
        Args:
            doc_id: The document ID
            
        Returns:
            Dict with extracted commands and metadata
        """
        print(f"Extracting configuration commands from document: {doc_id}")
        
        try:
            # Get the XML content
            xml_content = await self.mcp_client.get_xml_content(doc_id)
            
            # Extract command blocks
            command_blocks = self._extract_code_blocks(xml_content)
            
            # Group commands by section
            sections = self._extract_sections(xml_content)
            
            # Format results
            result = {
                "doc_id": doc_id,
                "command_count": len(command_blocks),
                "command_blocks": command_blocks,
                "sections": sections,
                "formatted_commands": self._format_commands(command_blocks, sections)
            }
            
            return result
            
        except Exception as e:
            print(f"Error extracting commands: {e}")
            return {
                "error": str(e),
                "doc_id": doc_id
            }
    
    def _extract_code_blocks(self, xml_content: str) -> List[Dict[str, str]]:
        """Extract code blocks from XML content."""
        code_blocks = []
        
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
            
            code_blocks.append({
                "id": f"block_{i}",
                "content": clean_block,
                "section_id": section_id,
                "section_title": title
            })
            
        return code_blocks
    
    def _extract_sections(self, xml_content: str) -> List[Dict[str, str]]:
        """Extract sections from XML content."""
        sections = []
        
        # Find all sections
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
            
        return sections
    
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
    """Run the command extractor on our Cisco router guide."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <doc_id>")
        print(f"Example: {sys.argv[0]} xml3")
        sys.exit(1)
        
    doc_id = sys.argv[1]
    
    # Create MCP client
    client = McpClient("http://localhost:8000")
    
    # Create extractor
    extractor = CiscoCommandExtractor(client)
    
    # Extract commands
    result = await extractor.extract_commands(doc_id)
    
    # Print formatted commands
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Found {result['command_count']} command blocks\n")
        print(result["formatted_commands"])
    
if __name__ == "__main__":
    asyncio.run(main())