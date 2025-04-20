"""Simple test script for document functionality."""

import asyncio
import json
import logging
import sys
from typing import Dict, List, Any

from agent_provocateur.mcp_client import McpClient


async def test_document_functionality():
    """Test document functionality."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    
    # Create MCP client
    client = McpClient("http://localhost:8000")
    
    print("\n=== Testing Document Listing ===")
    try:
        # List all documents
        all_documents = await client.list_documents()
        print(f"Found {len(all_documents)} documents:")
        for doc in all_documents:
            print(f"  - {doc.doc_id} ({doc.doc_type}): {doc.title}")
        
        # List documents by type
        print("\n=== Listing Documents by Type ===")
        doc_types = ["text", "pdf", "image", "code", "structured_data"]
        for doc_type in doc_types:
            docs = await client.list_documents(doc_type=doc_type)
            print(f"\n{doc_type.capitalize()} Documents ({len(docs)} found):")
            for doc in docs:
                print(f"  - {doc.doc_id}: {doc.title}")
        
        # Get and display specific documents
        print("\n=== Getting Specific Documents ===")
        document_ids = ["doc1", "pdf1", "img1", "code1", "data1"]
        
        for doc_id in document_ids:
            try:
                doc = await client.get_document(doc_id)
                print(f"\nDocument {doc_id} ({doc.doc_type}):")
                print(f"  Title: {doc.title}")
                print(f"  Created: {doc.created_at}")
                
                # Display content based on document type
                if doc.doc_type == "text":
                    print(f"  Content (excerpt): {doc.markdown[:100]}...")
                elif doc.doc_type == "pdf":
                    page_count = len(doc.pages) if hasattr(doc, 'pages') and doc.pages else 0
                    print(f"  Pages: {page_count}")
                    if page_count > 0:
                        print(f"  First page (excerpt): {doc.pages[0].text[:100]}...")
                elif doc.doc_type == "image":
                    print(f"  Format: {doc.format}")
                    dimensions = f"{doc.width}x{doc.height}" if hasattr(doc, 'width') and doc.width and hasattr(doc, 'height') and doc.height else "unknown"
                    print(f"  Dimensions: {dimensions}")
                    print(f"  Caption: {doc.caption if hasattr(doc, 'caption') and doc.caption else 'None'}")
                elif doc.doc_type == "code":
                    print(f"  Language: {doc.language if hasattr(doc, 'language') else 'unknown'}")
                    print(f"  Line count: {doc.line_count if hasattr(doc, 'line_count') else 0}")
                    content_excerpt = doc.content[:100] + "..." if hasattr(doc, 'content') and len(doc.content) > 100 else doc.content
                    print(f"  Content (excerpt): {content_excerpt}")
                elif doc.doc_type == "structured_data":
                    print(f"  Format: {doc.format if hasattr(doc, 'format') else 'unknown'}")
                    data_keys = list(doc.data.keys()) if hasattr(doc, 'data') and doc.data else []
                    print(f"  Top-level keys: {data_keys}")
            except Exception as e:
                print(f"Error fetching document {doc_id}: {e}")
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_document_functionality())