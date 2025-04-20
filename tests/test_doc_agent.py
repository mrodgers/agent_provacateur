"""Simple test script for DocAgent and DocumentProcessingAgent."""

import asyncio
import logging
import sys

from agent_provocateur.agent_implementations import (
    DocAgent,
    DocumentProcessingAgent,
    DecisionAgent,
)


async def main():
    """Test document agents."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    
    # Create agents
    doc_agent = DocAgent(agent_id="doc_agent")
    doc_processing_agent = DocumentProcessingAgent(agent_id="document_processing_agent")
    decision_agent = DecisionAgent(agent_id="decision_agent")
    
    # Start agents
    for agent in [doc_agent, doc_processing_agent, decision_agent]:
        await agent.start()
    
    try:
        # List all available documents
        print("\n=== Listing All Documents ===")
        doc_list_result = await doc_agent.handle_list_documents({"doc_type": None})
        for doc in doc_list_result["documents"]:
            print(f"{doc['doc_id']} ({doc['doc_type']}): {doc['title']}")
        
        # Process documents by type
        doc_types = ["text", "pdf", "image", "code", "structured_data"]
        for doc_type in doc_types:
            # Get documents of this type
            docs_by_type = await doc_agent.handle_list_documents({"doc_type": doc_type})
            
            if not docs_by_type["documents"]:
                print(f"\nNo {doc_type} documents found.")
                continue
            
            print(f"\n=== Processing {doc_type.capitalize()} Documents ===")
            for doc_info in docs_by_type["documents"]:
                doc_id = doc_info["doc_id"]
                
                # Process document
                summary = await doc_processing_agent.handle_summarize_document({"doc_id": doc_id})
                
                # Print summary
                print(f"\n{doc_info['title']} ({doc_id}):")
                print(f"Summary: {summary.get('summary', 'No summary available')}")
                
                # For text and code documents, let's do document analysis with LLM
                if doc_type in ["text", "code"]:
                    # Get full document
                    full_doc = await doc_agent.handle_get_document({"doc_id": doc_id})
                    
                    # Analyze with DecisionAgent
                    analysis = await decision_agent.handle_make_decision({
                        "decision_type": "document_analysis",
                        "context": {
                            "document": full_doc,
                            "query": "Provide insights on this document",
                        }
                    })
                    
                    # Print analysis
                    print("\nLLM Analysis:")
                    decision_text = analysis.get("decision", "No analysis available")
                    if len(decision_text) > 300:
                        print(f"{decision_text[:300]}...")
                    else:
                        print(decision_text)
    
    except Exception as e:
        logging.error(f"Error in test: {e}")
        raise
    finally:
        # Stop all agents
        for agent in [doc_agent, doc_processing_agent, decision_agent]:
            await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())