from typing import Any, Dict

from agent_provocateur.a2a_models import TaskRequest, TaskStatus
from agent_provocateur.agent_base import BaseAgent


class JiraAgent(BaseAgent):
    """Agent for fetching JIRA tickets."""
    
    async def handle_fetch_ticket(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Handle fetching a JIRA ticket.
        
        Args:
            task_request: The task request
            
        Returns:
            Dict[str, Any]: The ticket data
        """
        ticket_id = task_request.payload.get("ticket_id")
        if not ticket_id:
            raise ValueError("Missing required parameter: ticket_id")
        
        # Use MCP client to fetch ticket
        ticket = self.mcp_client.fetch_ticket(ticket_id)
        
        return ticket.dict()


class DocAgent(BaseAgent):
    """Agent for fetching documents."""
    
    async def handle_get_doc(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Handle fetching a document.
        
        Args:
            task_request: The task request
            
        Returns:
            Dict[str, Any]: The document data
        """
        doc_id = task_request.payload.get("doc_id")
        if not doc_id:
            raise ValueError("Missing required parameter: doc_id")
        
        # Use MCP client to fetch document
        doc = self.mcp_client.get_doc(doc_id)
        
        return doc.dict()


class PdfAgent(BaseAgent):
    """Agent for fetching PDF documents."""
    
    async def handle_get_pdf(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Handle fetching a PDF document.
        
        Args:
            task_request: The task request
            
        Returns:
            Dict[str, Any]: The PDF data
        """
        pdf_id = task_request.payload.get("pdf_id")
        if not pdf_id:
            raise ValueError("Missing required parameter: pdf_id")
        
        # Use MCP client to fetch PDF
        pdf = self.mcp_client.get_pdf(pdf_id)
        
        return pdf.dict()


class SearchAgent(BaseAgent):
    """Agent for performing web searches."""
    
    async def handle_search_web(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Handle a web search request.
        
        Args:
            task_request: The task request
            
        Returns:
            Dict[str, Any]: The search results
        """
        query = task_request.payload.get("query")
        if not query:
            raise ValueError("Missing required parameter: query")
        
        # Use MCP client to search
        results = self.mcp_client.search_web(query)
        
        return {
            "results": [result.dict() for result in results]
        }


class SynthesisAgent(BaseAgent):
    """Agent for synthesizing results from multiple sources."""
    
    async def handle_synthesize(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Handle synthesizing results.
        
        Args:
            task_request: The task request
            
        Returns:
            Dict[str, Any]: The synthesized report
        """
        ticket_data = task_request.payload.get("ticket_data")
        document_data = task_request.payload.get("document_data", [])
        search_results = task_request.payload.get("search_results", [])
        
        # Simple synthesis algorithm - in a real system, this would be more sophisticated
        sections = []
        
        if ticket_data:
            sections.append({
                "title": "JIRA Ticket Information",
                "content": f"Ticket {ticket_data['id']}: {ticket_data['summary']} (Status: {ticket_data['status']})"
            })
        
        if document_data:
            sections.append({
                "title": "Document Summary",
                "content": f"Document {document_data['doc_id']} contains {len(document_data['markdown'])} characters."
            })
        
        if search_results:
            content = "Found the following related resources:\n"
            for i, result in enumerate(search_results, 1):
                content += f"\n{i}. {result['title']} - {result['url']}"
            
            sections.append({
                "title": "Search Results",
                "content": content
            })
        
        # Create summary
        summary = f"Report compiled with {len(sections)} sections."
        
        return {
            "sections": sections,
            "summary": summary
        }


class ManagerAgent(BaseAgent):
    """Agent for orchestrating research workflows."""
    
    async def handle_research_query(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Handle a research query.
        
        Args:
            task_request: The task request
            
        Returns:
            Dict[str, Any]: The research report
        """
        query = task_request.payload.get("query")
        ticket_id = task_request.payload.get("ticket_id")
        doc_id = task_request.payload.get("doc_id")
        
        if not query:
            raise ValueError("Missing required parameter: query")
        
        results = {}
        
        # Step 1: Fetch JIRA ticket if provided
        if ticket_id:
            ticket_result = await self.send_request_and_wait(
                target_agent="jira_agent",
                intent="fetch_ticket",
                payload={"ticket_id": ticket_id},
            )
            
            if ticket_result and ticket_result.status == TaskStatus.COMPLETED:
                results["ticket_data"] = ticket_result.output
        
        # Step 2: Fetch document if provided
        if doc_id:
            doc_result = await self.send_request_and_wait(
                target_agent="doc_agent",
                intent="get_doc",
                payload={"doc_id": doc_id},
            )
            
            if doc_result and doc_result.status == TaskStatus.COMPLETED:
                results["document_data"] = doc_result.output
        
        # Step 3: Perform web search
        search_result = await self.send_request_and_wait(
            target_agent="search_agent",
            intent="search_web",
            payload={"query": query},
        )
        
        if search_result and search_result.status == TaskStatus.COMPLETED:
            results["search_results"] = search_result.output.get("results", [])
        
        # Step 4: Synthesize results
        synthesis_result = await self.send_request_and_wait(
            target_agent="synthesis_agent",
            intent="synthesize",
            payload=results,
        )
        
        if synthesis_result and synthesis_result.status == TaskStatus.COMPLETED:
            return synthesis_result.output
        else:
            return {"error": "Failed to synthesize results"}