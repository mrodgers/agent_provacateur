from typing import Any, Dict, List, Union

from agent_provocateur.a2a_models import TaskRequest, TaskStatus
from agent_provocateur.agent_base import BaseAgent
from agent_provocateur.models import (
    DocumentContent,
    PdfDocument,
    ImageDocument,
    CodeDocument,
    StructuredDataDocument,
)


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
    
    async def handle_get_document(self, task_request: Union[TaskRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Handle fetching a document using the unified document API.
        
        Args:
            task_request: The task request or direct dict
            
        Returns:
            Dict[str, Any]: The document data
        """
        # Handle both TaskRequest and direct dict inputs
        if hasattr(task_request, 'payload'):
            payload = task_request.payload
        else:
            payload = task_request
            
        doc_id = payload.get("doc_id")
        if not doc_id:
            raise ValueError("Missing required parameter: doc_id")
        
        # Use async MCP client to fetch document
        doc = await self.async_mcp_client.get_document(doc_id)
        
        return doc.dict()
    
    async def handle_list_documents(self, task_request: Union[TaskRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Handle listing available documents.
        
        Args:
            task_request: The task request or direct dict
            
        Returns:
            Dict[str, Any]: The list of documents
        """
        # Handle both TaskRequest and direct dict inputs
        if hasattr(task_request, 'payload'):
            payload = task_request.payload
        else:
            payload = task_request
            
        doc_type = payload.get("doc_type")
        
        # Use async MCP client to list documents
        documents = await self.async_mcp_client.list_documents(doc_type)
        
        return {
            "documents": [doc.dict(exclude={"markdown", "html", "content", "data", "pages"}) for doc in documents]
        }


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


class DocumentProcessingAgent(BaseAgent):
    """Agent for processing different document types."""
    
    async def handle_summarize_document(self, task_request: Union[TaskRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize a document based on its type.
        
        Args:
            task_request: The task request or direct dict
            
        Returns:
            Dict[str, Any]: The summary data
        """
        # Handle both TaskRequest and direct dict inputs
        if hasattr(task_request, 'payload'):
            payload = task_request.payload
        else:
            payload = task_request
            
        doc_id = payload.get("doc_id")
        if not doc_id:
            raise ValueError("Missing required parameter: doc_id")
        
        # Fetch the document
        doc = await self.async_mcp_client.get_document(doc_id)
        
        # Process based on document type
        if isinstance(doc, DocumentContent):
            return await self._summarize_text_document(doc)
        elif isinstance(doc, PdfDocument):
            return await self._summarize_pdf_document(doc)
        elif isinstance(doc, ImageDocument):
            return await self._summarize_image_document(doc)
        elif isinstance(doc, CodeDocument):
            return await self._summarize_code_document(doc)
        elif isinstance(doc, StructuredDataDocument):
            return await self._summarize_structured_data_document(doc)
        else:
            return {
                "summary": f"Unknown document type: {doc.doc_type}",
                "doc_id": doc.doc_id,
                "title": doc.title,
            }
    
    async def _summarize_text_document(self, doc: DocumentContent) -> Dict[str, Any]:
        """Summarize a text document.
        
        Args:
            doc: The document to summarize
            
        Returns:
            Dict[str, Any]: The summary data
        """
        # In a real implementation, this might use an LLM to generate a summary
        word_count = len(doc.markdown.split())
        
        return {
            "summary": f"Text document with {word_count} words",
            "doc_id": doc.doc_id,
            "title": doc.title,
            "doc_type": doc.doc_type,
            "word_count": word_count,
        }
    
    async def _summarize_pdf_document(self, doc: PdfDocument) -> Dict[str, Any]:
        """Summarize a PDF document.
        
        Args:
            doc: The document to summarize
            
        Returns:
            Dict[str, Any]: The summary data
        """
        page_count = len(doc.pages)
        total_words = sum(len(page.text.split()) for page in doc.pages)
        
        return {
            "summary": f"PDF document with {page_count} pages and approximately {total_words} words",
            "doc_id": doc.doc_id,
            "title": doc.title,
            "doc_type": doc.doc_type,
            "page_count": page_count,
            "word_count": total_words,
        }
    
    async def _summarize_image_document(self, doc: ImageDocument) -> Dict[str, Any]:
        """Summarize an image document.
        
        Args:
            doc: The document to summarize
            
        Returns:
            Dict[str, Any]: The summary data
        """
        dimensions = f"{doc.width}x{doc.height}" if doc.width and doc.height else "unknown dimensions"
        
        return {
            "summary": f"Image document in {doc.format} format with {dimensions}",
            "doc_id": doc.doc_id,
            "title": doc.title,
            "doc_type": doc.doc_type,
            "format": doc.format,
            "dimensions": dimensions,
            "alt_text": doc.alt_text,
        }
    
    async def _summarize_code_document(self, doc: CodeDocument) -> Dict[str, Any]:
        """Summarize a code document.
        
        Args:
            doc: The document to summarize
            
        Returns:
            Dict[str, Any]: The summary data
        """
        return {
            "summary": f"Code document in {doc.language} with {doc.line_count} lines",
            "doc_id": doc.doc_id,
            "title": doc.title,
            "doc_type": doc.doc_type,
            "language": doc.language,
            "line_count": doc.line_count,
        }
    
    async def _summarize_structured_data_document(self, doc: StructuredDataDocument) -> Dict[str, Any]:
        """Summarize a structured data document.
        
        Args:
            doc: The document to summarize
            
        Returns:
            Dict[str, Any]: The summary data
        """
        # For JSON data, count keys at the top level
        if doc.format.lower() == "json":
            keys = list(doc.data.keys())
            key_count = len(keys)
            return {
                "summary": f"Structured data in {doc.format} format with {key_count} top-level keys",
                "doc_id": doc.doc_id,
                "title": doc.title,
                "doc_type": doc.doc_type,
                "format": doc.format,
                "top_level_keys": keys,
            }
        else:
            return {
                "summary": f"Structured data in {doc.format} format",
                "doc_id": doc.doc_id,
                "title": doc.title,
                "doc_type": doc.doc_type,
                "format": doc.format,
            }


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
            "results": results
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
            # Check if it's a list or a single document
            if isinstance(document_data, list):
                for doc in document_data:
                    document_title = doc.get('title', f"Document {doc.get('doc_id', 'unknown')}")
                    document_type = doc.get('doc_type', 'unknown')
                    sections.append({
                        "title": f"{document_title} ({document_type.capitalize()})",
                        "content": self._generate_document_summary(doc)
                    })
            else:
                document_title = document_data.get('title', f"Document {document_data.get('doc_id', 'unknown')}")
                document_type = document_data.get('doc_type', 'unknown')
                sections.append({
                    "title": f"{document_title} ({document_type.capitalize()})",
                    "content": self._generate_document_summary(document_data)
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
    
    def _generate_document_summary(self, doc: Dict[str, Any]) -> str:
        """Generate a summary for a document based on its type.
        
        Args:
            doc: The document data
            
        Returns:
            str: A summary of the document
        """
        doc_type = doc.get('doc_type', 'unknown')
        
        if doc_type == 'text':
            markdown = doc.get('markdown', '')
            return f"Text document contains {len(markdown)} characters."
        
        elif doc_type == 'pdf':
            pages = doc.get('pages', [])
            return f"PDF document with {len(pages)} pages."
        
        elif doc_type == 'image':
            dimensions = f"{doc.get('width', '?')}x{doc.get('height', '?')}"
            return f"Image in {doc.get('format', 'unknown')} format ({dimensions}). Caption: {doc.get('caption', 'None')}"
        
        elif doc_type == 'code':
            return f"Code in {doc.get('language', 'unknown')} with {doc.get('line_count', '?')} lines."
        
        elif doc_type == 'structured_data':
            format = doc.get('format', 'unknown')
            if isinstance(doc.get('data', {}), dict):
                key_count = len(doc.get('data', {}).keys())
                return f"Structured data in {format} format with {key_count} top-level elements."
            else:
                return f"Structured data in {format} format."
        
        else:
            return f"Unknown document type: {doc_type}"
    


class DecisionAgent(BaseAgent):
    """Agent for making decisions using LLM assistance."""
    
    async def handle_make_decision(self, task_request: Union[TaskRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Handle making a decision using LLM.
        
        Args:
            task_request: The task request or direct dict
            
        Returns:
            Dict[str, Any]: The decision result
        """
        # Handle both TaskRequest and direct dict inputs
        if hasattr(task_request, 'payload'):
            payload = task_request.payload
        else:
            payload = task_request
        
        # Extract decision parameters
        decision_type = payload.get("decision_type", "generic")
        options = payload.get("options", [])
        criteria = payload.get("criteria", [])
        context_data = payload.get("context", {})
        
        # Build prompt based on decision type
        if decision_type == "prioritize":
            prompt = self._build_prioritization_prompt(options, criteria)
        elif decision_type == "select":
            prompt = self._build_selection_prompt(options, criteria)
        elif decision_type == "analyze":
            prompt = self._build_analysis_prompt(context_data)
        elif decision_type == "document_analysis":
            prompt = self._build_document_analysis_prompt(context_data)
        else:
            prompt = self._build_generic_decision_prompt(task_request.payload)
        
        # Check if there's a provider preference in context_data
        provider = context_data.get("llm_provider", "mock")
        model = context_data.get("llm_model", None)
        
        # Use LLM to make the decision
        try:
            # First try with Ollama provider if requested
            if provider == "ollama":
                # Create a messages format for better context handling with chat models
                messages = []
                
                # Add system prompt if available
                if context_data.get("system_prompt"):
                    messages.append({
                        "role": "system", 
                        "content": context_data.get("system_prompt")
                    })
                
                # Add the decision context
                if context_data:
                    context_message = "Context information:\n"
                    for key, value in context_data.items():
                        if key not in ["llm_provider", "llm_model", "system_prompt"]:
                            context_message += f"{key}: {value}\n"
                    
                    if context_message != "Context information:\n":
                        messages.append({
                            "role": "user",
                            "content": context_message
                        })
                
                # Add the main prompt
                messages.append({
                    "role": "user",
                    "content": prompt
                })
                
                llm_response = await self.async_mcp_client.generate_text(
                    messages=messages,
                    temperature=0.3,  # Lower temperature for more deterministic outputs
                    provider=provider,
                    model=model,
                )
            else:
                # Use regular prompt-based approach for other providers
                llm_response = await self.async_mcp_client.generate_text(
                    prompt=prompt,
                    temperature=0.3,  # Lower temperature for more deterministic outputs
                    context=context_data,
                    provider=provider,
                    model=model,
                )
                
            # Process and return the decision
            return {
                "decision": llm_response.text,
                "confidence": 0.85,  # Confidence score
                "model": llm_response.model,
                "provider": llm_response.provider,
                "reasoning": "Decision based on provided criteria and context",
                "token_usage": {
                    "prompt_tokens": llm_response.usage.prompt_tokens,
                    "completion_tokens": llm_response.usage.completion_tokens,
                    "total_tokens": llm_response.usage.total_tokens,
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error using {provider} LLM: {e}")
            
            # Fallback to mock provider if original provider fails
            if provider != "mock":
                self.logger.info("Falling back to mock LLM provider")
                llm_response = await self.async_mcp_client.generate_text(
                    prompt=prompt,
                    temperature=0.3,
                    context=context_data,
                    provider="mock",
                )
                
                return {
                    "decision": llm_response.text,
                    "confidence": 0.75,  # Lower confidence for fallback
                    "model": llm_response.model,
                    "provider": "mock (fallback)",
                    "reasoning": "Decision based on provided criteria and context (using fallback provider)",
                    "token_usage": {
                        "prompt_tokens": llm_response.usage.prompt_tokens,
                        "completion_tokens": llm_response.usage.completion_tokens,
                        "total_tokens": llm_response.usage.total_tokens,
                    }
                }
            
            # If mock also fails or was the original provider
            return {
                "decision": f"Error generating decision: {str(e)}",
                "confidence": 0.0,
                "model": "error",
                "provider": "error",
                "reasoning": "Failed to generate decision due to an error",
                "token_usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                }
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
    
    def _build_document_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Build a prompt for document analysis decisions."""
        prompt = "Please analyze the following document information and provide insights:\n\n"
        
        document = context.get('document', {})
        doc_type = document.get('doc_type', 'unknown')
        
        prompt += f"Document Title: {document.get('title', 'Untitled')}\n"
        prompt += f"Document Type: {doc_type}\n"
        
        # Add type-specific information
        if doc_type == 'text':
            prompt += f"Content Length: {len(document.get('markdown', ''))}\n"
            prompt += f"Content Sample: {document.get('markdown', '')[:200]}...\n"
        
        elif doc_type == 'pdf':
            pages = document.get('pages', [])
            prompt += f"Pages: {len(pages)}\n"
            if pages:
                prompt += f"First Page Sample: {pages[0].get('text', '')[:200]}...\n"
        
        elif doc_type == 'image':
            prompt += f"Format: {document.get('format', 'unknown')}\n"
            prompt += f"Dimensions: {document.get('width', '?')}x{document.get('height', '?')}\n"
            prompt += f"Alt Text: {document.get('alt_text', 'None')}\n"
            prompt += f"Caption: {document.get('caption', 'None')}\n"
        
        elif doc_type == 'code':
            prompt += f"Language: {document.get('language', 'unknown')}\n"
            prompt += f"Lines: {document.get('line_count', '?')}\n"
            prompt += f"Code Sample: {document.get('content', '')[:200]}...\n"
        
        elif doc_type == 'structured_data':
            prompt += f"Format: {document.get('format', 'unknown')}\n"
            if isinstance(document.get('data', {}), dict):
                keys = list(document.get('data', {}).keys())
                prompt += f"Top-level keys: {', '.join(keys)}\n"
        
        # Add query for analysis
        prompt += "\nBased on this document information, please provide:\n"
        prompt += "1. A summary of the document's purpose and content\n"
        prompt += "2. Key insights that can be extracted\n"
        prompt += "3. Recommendations for further analysis\n"
        prompt += "4. Potential connections to other documents or topics\n"
        
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
    
    async def handle_research_query(self, task_request: Union[TaskRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Handle a research query.
        
        Args:
            task_request: The task request or dict with query parameters
            
        Returns:
            Dict[str, Any]: The research report
        """
        # Handle both TaskRequest and direct dict inputs
        if hasattr(task_request, 'payload'):
            payload = task_request.payload
        else:
            payload = task_request
            
        query = payload.get("query")
        ticket_id = payload.get("ticket_id")
        doc_id = payload.get("doc_id")
        doc_type = payload.get("doc_type")
        
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
                # Use appropriate agent based on document type
                if doc_type == "pdf":
                    doc_result = await self.send_request_and_wait(
                        target_agent="pdf_agent",
                        intent="get_pdf",
                        payload={"pdf_id": doc_id},
                        timeout_sec=5,
                    )
                else:
                    # Use unified document interface
                    doc_result = await self.send_request_and_wait(
                        target_agent="doc_agent",
                        intent="get_document",
                        payload={"doc_id": doc_id},
                        timeout_sec=5,
                    )
                
                if doc_result and doc_result.status == TaskStatus.COMPLETED:
                    self.logger.info(f"Successfully fetched document: {doc_id}")
                    results["document_data"] = doc_result.output
                    
                    # Step 2.1: Process document if needed
                    if doc_type:
                        self.logger.info(f"Processing document: {doc_id}")
                        processing_result = await self.send_request_and_wait(
                            target_agent="document_processing_agent",
                            intent="summarize_document",
                            payload={"doc_id": doc_id},
                            timeout_sec=5,
                        )
                        
                        if processing_result and processing_result.status == TaskStatus.COMPLETED:
                            self.logger.info(f"Successfully processed document: {doc_id}")
                            results["document_summary"] = processing_result.output
                        else:
                            self.logger.warning(f"Failed to process document: {doc_id}")
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
                        "document_summary": results.get("document_summary"),
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