#!/usr/bin/env python
"""
Example script demonstrating how to use the Text GraphRAG agent with markdown and text files.

This example shows how to:
1. Index a markdown document into GraphRAG
2. Extract entities and relationships
3. Visualize entity connections

Usage:
    python text_document_graphrag.py [path_to_markdown_file]
"""

import os
import sys
import asyncio
import argparse
import json
from typing import Dict, Any

from agent_provocateur.text_graphrag_agent import TextGraphRAGAgent
from agent_provocateur.a2a_models import TaskRequest


async def index_markdown_document(agent: TextGraphRAGAgent, content: str, title: str) -> Dict[str, Any]:
    """
    Index a markdown document in GraphRAG.
    
    Args:
        agent: Text GraphRAG agent
        content: Document content
        title: Document title
        
    Returns:
        Indexing result
    """
    task_request = TaskRequest(
        task_id="index_markdown",
        source_agent="example_script",
        target_agent="text_graphrag_agent",
        intent="index_text_document",
        payload={
            "content": content,
            "title": title,
            "doc_type": "markdown",
            "metadata": {
                "source": "example_script",
                "format": "markdown"
            }
        }
    )
    
    return await agent.handle_index_text_document(task_request)


async def extract_and_analyze_entities(agent: TextGraphRAGAgent, content: str) -> Dict[str, Any]:
    """
    Extract entities from document and analyze relationships.
    
    Args:
        agent: Text GraphRAG agent
        content: Document content
        
    Returns:
        Entity analysis results
    """
    # Extract enhanced entities (with relationships)
    extract_task = TaskRequest(
        task_id="extract_entities",
        source_agent="example_script",
        target_agent="text_graphrag_agent",
        intent="extract_enhanced_entities",
        payload={
            "content": content,
            "min_confidence": 0.6
        }
    )
    
    extraction_result = await agent.handle_extract_enhanced_entities(extract_task)
    
    # Analyze relationships
    if extraction_result["status"] == "success" and extraction_result["entity_count"] > 0:
        analyze_task = TaskRequest(
            task_id="analyze_relationships",
            source_agent="example_script",
            target_agent="text_graphrag_agent",
            intent="analyze_entity_relationships",
            payload={}  # Use all extracted entities
        )
        
        return await agent.handle_analyze_entity_relationships(analyze_task)
    
    return extraction_result


async def main():
    """Main function for the example script."""
    parser = argparse.ArgumentParser(description="Process markdown documents with GraphRAG")
    parser.add_argument("file_path", help="Path to markdown file", nargs="?")
    args = parser.parse_args()
    
    # Use default example if no file provided
    if args.file_path:
        if not os.path.exists(args.file_path):
            print(f"Error: File '{args.file_path}' not found.")
            return
        
        with open(args.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            title = os.path.basename(args.file_path)
    else:
        # Use embedded example
        content = """# Introduction to GraphRAG

Graph-based Retrieval Augmented Generation (GraphRAG) combines knowledge graphs with traditional RAG to enhance context awareness and reasoning capabilities.

## Key Concepts

- **Knowledge Graphs**: Structured representations of entities and relationships
- **Semantic Search**: Finding relevant information based on meaning, not just keywords
- **Entity Linking**: Connecting mentions in text to canonical entities

## Benefits

Graph-based RAG offers several advantages:

1. Better handling of complex, interconnected information
2. Improved source attribution and fact validation
3. More accurate entity disambiguation
4. Enhanced reasoning capabilities through relationship awareness

## Implementation

This project implements GraphRAG using vector embeddings for semantic search and a graph database for entity relationships.
"""
        title = "Introduction to GraphRAG"
    
    # Initialize agent
    agent = TextGraphRAGAgent("text_graphrag_agent")
    await agent.on_startup()
    
    # Step 1: Index the document
    print(f"Indexing document: {title}...")
    index_result = await index_markdown_document(agent, content, title)
    print(f"Indexing result: {json.dumps(index_result, indent=2)}")
    
    # Step 2: Extract and analyze entities
    print("\nExtracting and analyzing entities...")
    analysis_result = await extract_and_analyze_entities(agent, content)
    
    # Step 3: Display results
    print("\nEntity Analysis Result:")
    print(f"Found {analysis_result.get('entity_count', 0)} entities and {analysis_result.get('relationship_count', 0)} relationships")
    
    if analysis_result.get("status") == "success":
        # Print entity types
        print("\nEntity Types:")
        for entity_type, count in analysis_result.get("entity_types", {}).items():
            print(f"  - {entity_type}: {count}")
        
        # Print relationship types
        print("\nRelationship Types:")
        for rel_type, count in analysis_result.get("relationship_types", {}).items():
            print(f"  - {rel_type}: {count}")
        
        # Print clusters
        print("\nEntity Clusters:")
        for i, cluster in enumerate(analysis_result.get("clusters", [])):
            print(f"  Cluster {i+1} (Size: {cluster['size']}, Type: {cluster['primary_type']})")
    else:
        print(f"Analysis failed: {analysis_result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    asyncio.run(main())