from typing import Any, Dict, List, Optional

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
        
        # Use async MCP client to fetch ticket
        ticket = await self.async_mcp_client.fetch_ticket(ticket_id)
        
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
        
        # Use async MCP client to fetch document
        doc = await self.async_mcp_client.get_doc(doc_id)
        
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
        
        # Use async MCP client to fetch PDF
        pdf = await self.async_mcp_client.get_pdf(pdf_id)
        
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
        
        # Use async MCP client to search
        results = await self.async_mcp_client.search_web(query)
        
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
        research_approach = task_request.payload.get("research_approach")
        
        # Simple synthesis algorithm - in a real system, this would be more sophisticated
        sections = []
        
        # Include research approach if available
        if research_approach:
            sections.append({
                "title": "Research Approach (LLM-Guided)",
                "content": research_approach
            })
        
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


class DecisionAgent(BaseAgent):
    """Agent for making decisions using LLM assistance."""
    
    async def handle_make_decision(self, task_request: TaskRequest) -> Dict[str, Any]:
        """Handle making a decision using LLM.
        
        Args:
            task_request: The task request
            
        Returns:
            Dict[str, Any]: The decision result
        """
        # Extract decision parameters
        decision_type = task_request.payload.get("decision_type", "generic")
        options = task_request.payload.get("options", [])
        criteria = task_request.payload.get("criteria", [])
        context_data = task_request.payload.get("context", {})
        
        # Build prompt based on decision type
        if decision_type == "prioritize":
            prompt = self._build_prioritization_prompt(options, criteria)
        elif decision_type == "select":
            prompt = self._build_selection_prompt(options, criteria)
        elif decision_type == "analyze":
            prompt = self._build_analysis_prompt(context_data)
        else:
            prompt = self._build_generic_decision_prompt(task_request.payload)
        
        # Use LLM to make the decision
        llm_response = await self.async_mcp_client.generate_text(
            prompt=prompt,
            temperature=0.3,  # Lower temperature for more deterministic outputs
            context=context_data
        )
        
        # Process and return the decision
        return {
            "decision": llm_response.text,
            "confidence": 0.85,  # Mock confidence score
            "model": llm_response.model,
            "reasoning": "Decision based on provided criteria and context",
            "token_usage": llm_response.usage
        }
    
    def _build_prioritization_prompt(self, options: List[Dict[str, Any]], criteria: List[str]) -> str:
        """Build a prompt for prioritization decisions."""
        prompt = "Please prioritize the following tasks based on the given criteria:\n\n"
        
        # Add options
        prompt += "Tasks to prioritize:\n"
        for i, option in enumerate(options, 1):
            prompt += f"{i}. {option.get('name', f'Task {i}')}: {option.get('description', 'No description')}\n"
        
        # Add criteria
        prompt += "\nCriteria for prioritization:\n"
        for i, criterion in enumerate(criteria, 1):
            prompt += f"{i}. {criterion}\n"
        
        prompt += "\nPlease provide a prioritized list with clear reasoning for your decision."
        return prompt
    
    def _build_selection_prompt(self, options: List[Dict[str, Any]], criteria: List[str]) -> str:
        """Build a prompt for selection decisions."""
        prompt = "Please select the best option from the following based on the given criteria:\n\n"
        
        # Add options
        prompt += "Available options:\n"
        for i, option in enumerate(options, 1):
            prompt += f"{i}. {option.get('name', f'Option {i}')}: {option.get('description', 'No description')}\n"
        
        # Add criteria
        prompt += "\nSelection criteria:\n"
        for i, criterion in enumerate(criteria, 1):
            prompt += f"{i}. {criterion}\n"
        
        prompt += "\nPlease recommend the best option with clear reasoning for your decision."
        return prompt
    
    def _build_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Build a prompt for analysis decisions."""
        prompt = "Please analyze the following data and provide insights:\n\n"
        
        # Add context details
        for key, value in context.items():
            if isinstance(value, dict):
                prompt += f"{key}:\n"
                for sub_key, sub_value in value.items():
                    prompt += f"  - {sub_key}: {sub_value}\n"
            else:
                prompt += f"{key}: {value}\n"
        
        prompt += "\nPlease provide a detailed analysis with key findings and recommendations."
        return prompt
    
    def _build_generic_decision_prompt(self, payload: Dict[str, Any]) -> str:
        """Build a generic decision prompt."""
        prompt = "Please evaluate the following information and provide a decision:\n\n"
        
        # Add all payload details
        for key, value in payload.items():
            if key not in ["decision_type", "context"]:
                prompt += f"{key}: {value}\n"
        
        prompt += "\nBased on this information, what decision would you recommend? Please explain your reasoning."
        return prompt


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
        
        try:
            # Step 1: Fetch JIRA ticket if provided
            if ticket_id:
                self.logger.info(f"Fetching JIRA ticket: {ticket_id}")
                ticket_result = await self.send_request_and_wait(
                    target_agent="jira_agent",
                    intent="fetch_ticket",
                    payload={"ticket_id": ticket_id},
                    timeout_sec=5,  # Shorter timeout to avoid hanging
                )
                
                if ticket_result and ticket_result.status == TaskStatus.COMPLETED:
                    self.logger.info(f"Successfully fetched ticket: {ticket_id}")
                    results["ticket_data"] = ticket_result.output
                else:
                    self.logger.warning(f"Failed to fetch ticket: {ticket_id}")
            
            # Step 2: Fetch document if provided
            if doc_id:
                self.logger.info(f"Fetching document: {doc_id}")
                doc_result = await self.send_request_and_wait(
                    target_agent="doc_agent",
                    intent="get_doc",
                    payload={"doc_id": doc_id},
                    timeout_sec=5,  # Shorter timeout to avoid hanging
                )
                
                if doc_result and doc_result.status == TaskStatus.COMPLETED:
                    self.logger.info(f"Successfully fetched document: {doc_id}")
                    results["document_data"] = doc_result.output
                else:
                    self.logger.warning(f"Failed to fetch document: {doc_id}")
            
            # Step 3: Perform web search
            self.logger.info(f"Performing web search for: {query}")
            search_result = await self.send_request_and_wait(
                target_agent="search_agent",
                intent="search_web",
                payload={"query": query},
                timeout_sec=5,  # Shorter timeout to avoid hanging
            )
            
            if search_result and search_result.status == TaskStatus.COMPLETED:
                self.logger.info("Successfully performed web search")
                results["search_results"] = search_result.output.get("results", [])
            else:
                self.logger.warning("Failed to perform web search")
            
            # Step 4: Use decision agent to decide on research approach
            self.logger.info("Making research approach decision")
            decision_result = await self.send_request_and_wait(
                target_agent="decision_agent",
                intent="make_decision",
                payload={
                    "decision_type": "analyze",
                    "context": {
                        "query": query,
                        "ticket": results.get("ticket_data"),
                        "document": results.get("document_data"),
                        "search_results_count": len(results.get("search_results", [])),
                    }
                },
                timeout_sec=5,  # Shorter timeout to avoid hanging
            )
            
            if decision_result and decision_result.status == TaskStatus.COMPLETED:
                self.logger.info("Successfully made research approach decision")
                results["research_approach"] = decision_result.output.get("decision")
            else:
                self.logger.warning("Failed to make research approach decision")
            
            # Step 5: Synthesize results
            self.logger.info("Synthesizing results")
            synthesis_result = await self.send_request_and_wait(
                target_agent="synthesis_agent",
                intent="synthesize",
                payload=results,
                timeout_sec=5,  # Shorter timeout to avoid hanging
            )
            
            if synthesis_result and synthesis_result.status == TaskStatus.COMPLETED:
                self.logger.info("Successfully synthesized results")
                return synthesis_result.output
            else:
                self.logger.warning("Failed to synthesize results")
                return {"error": "Failed to synthesize results"}
                
        except Exception as e:
            self.logger.error(f"Error in research query: {e}")
            return {
                "error": f"An error occurred during research: {str(e)}",
                "sections": [{"title": "Error", "content": f"Research failed: {str(e)}"}],
                "summary": "Research failed due to an error"
            }