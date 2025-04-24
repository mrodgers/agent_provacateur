#!/usr/bin/env python3
"""
Script to extract configuration commands from Cisco Router Configuration Guide.
"""

import asyncio
import sys
import re
from pathlib import Path

# Add the parent directory to the path so we can import the agent_provocateur package
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_provocateur.mcp_client import McpClient

async def extract_configuration_commands(doc_id):
    """Extract configuration commands from the Cisco guide XML."""
    # Create MCP client
    client = McpClient("http://localhost:8000")
    
    print(f"Fetching XML content for document {doc_id}...")
    
    try:
        # Get the XML content
        xml_content = await client.get_xml_content(doc_id)
        
        # Parse the XML to extract code blocks
        code_blocks = re.findall(r'<code-block>(.*?)</code-block>', xml_content, re.DOTALL)
        
        print(f"Found {len(code_blocks)} code blocks")
        print("\n=== Configuration Commands ===\n")
        
        # Process and display each code block
        for i, block in enumerate(code_blocks, 1):
            # Clean up the block (remove leading/trailing whitespace and indentation)
            clean_block = "\n".join(line.strip() for line in block.strip().split("\n"))
            
            print(f"Command Block {i}:")
            print("-------------------")
            print(clean_block)
            print("-------------------\n")
            
        # Generate a result document using LLM
        print("\nGenerating structured command summary...")
        response = await client.generate_text(
            prompt=f"Summarize the following Cisco router configuration commands in a structured format, grouping similar commands and explaining their purpose:\n\n{code_blocks}",
            max_tokens=1000,
            temperature=0.3
        )
        
        print("\n=== Command Summary ===\n")
        print(response.text)
        
    except Exception as e:
        print(f"Error processing document: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <doc_id>")
        print(f"Example: {sys.argv[0]} xml3")
        sys.exit(1)
        
    doc_id = sys.argv[1]
    asyncio.run(extract_configuration_commands(doc_id))