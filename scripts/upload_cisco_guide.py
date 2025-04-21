#!/usr/bin/env python3
"""
Script to upload the Cisco Router Guide XML file.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the agent_provocateur package
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_provocateur.mcp_client import McpClient

async def upload_cisco_guide():
    # Path to the XML file
    xml_file = Path(__file__).parent.parent / "examples" / "cisco_router_guide.xml"
    
    # Read the XML content
    xml_content = xml_file.read_text()
    
    # Create MCP client
    client = McpClient("http://localhost:8000")
    
    print(f"Uploading {xml_file.name}...")
    
    try:
        # Upload the XML document
        result = await client.upload_xml(xml_content, "Cisco Router Configuration Guide")
        print(f"Successfully uploaded document with ID: {result.doc_id}")
        print(f"Root element: {result.root_element}")
        return result.doc_id
    except Exception as e:
        print(f"Error uploading document: {e}")
        return None

if __name__ == "__main__":
    doc_id = asyncio.run(upload_cisco_guide())
    if doc_id:
        print(f"\nTo use this document with goal refiner, run:")
        print(f"./scripts/goal_refiner_cli.py \"Extract configuration steps from Cisco guide\" --doc-id {doc_id}")