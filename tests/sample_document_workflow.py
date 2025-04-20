"""Sample workflow for demonstrating agent-to-agent communication with real document types."""

import asyncio
import logging
import sys

from agent_provocateur.agent_implementations import (
    DocAgent,
    PdfAgent,
    DocumentProcessingAgent,
    SynthesisAgent,
    DecisionAgent,
    ManagerAgent,
)


async def main():
    """Run a sample workflow."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    
    # Create agents
    doc_agent = DocAgent(agent_id="doc_agent")
    pdf_agent = PdfAgent(agent_id="pdf_agent")
    doc_processing_agent = DocumentProcessingAgent(agent_id="document_processing_agent")
    synthesis_agent = SynthesisAgent(agent_id="synthesis_agent")
    decision_agent = DecisionAgent(agent_id="decision_agent")
    manager_agent = ManagerAgent(agent_id="manager_agent")
    
    # Start all agents
    for agent in [
        doc_agent, 
        pdf_agent, 
        doc_processing_agent,
        synthesis_agent, 
        decision_agent,
        manager_agent,
    ]:
        await agent.start()
    
    try:
        # Start the workflow by sending a research query to the manager agent
        result = await manager_agent.handle_research_query({
            "query": "agent communication protocols",
            "doc_id": "doc1",      # Text document
            "doc_type": "text",
        })
        
        # Print the research report
        print("\n=== Research Report ===")
        print(f"Summary: {result['summary']}")
        print("\nSections:")
        for i, section in enumerate(result["sections"], 1):
            print(f"\n{i}. {section['title']}")
            print("-" * (len(f"{i}. {section['title']}") + 5))
            print(section["content"])
        
        # Try with a different document type
        result = await manager_agent.handle_research_query({
            "query": "PDF document extraction",
            "doc_id": "pdf1",      # PDF document
            "doc_type": "pdf",
        })
        
        # Print the research report
        print("\n=== Research Report (PDF Document) ===")
        print(f"Summary: {result['summary']}")
        print("\nSections:")
        for i, section in enumerate(result["sections"], 1):
            print(f"\n{i}. {section['title']}")
            print("-" * (len(f"{i}. {section['title']}") + 5))
            print(section["content"])
        
        # List all available documents
        doc_list_result = await doc_agent.handle_list_documents({"doc_type": None})
        
        # Print the document list
        print("\n=== Available Documents ===")
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
                print(f"Summary: {summary['summary']}")
                
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
                    print(analysis["decision"][:300] + "..." if len(analysis["decision"]) > 300 else analysis["decision"])
        
    except Exception as e:
        logging.error(f"Error in workflow: {e}")
        raise
    finally:
        # Stop all agents
        for agent in [
            doc_agent, 
            pdf_agent, 
            doc_processing_agent,
            synthesis_agent, 
            decision_agent,
            manager_agent,
        ]:
            await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())