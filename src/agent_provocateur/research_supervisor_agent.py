"""Research Supervisor Agent for orchestrating document research workflows."""

from typing import Any, Dict, List, Optional
import logging
import asyncio
import time
import uuid
import datetime

from agent_provocateur.a2a_models import TaskRequest, TaskStatus
from agent_provocateur.agent_base import BaseAgent
from agent_provocateur.models import Document, Source, SourceType
from agent_provocateur.goal_refiner import GoalRefiner

logger = logging.getLogger(__name__)

class ResearchSupervisorAgent(BaseAgent):
    """
    Top-level supervisor for research workflows that coordinates:
    1. XML document analysis and entity extraction
    2. Delegation to specialized agents (Search, JIRA, Doc, PDF)
    3. Research synthesis
    4. XML output generation
    """
    
    def __init__(self, agent_id: str, broker=None, mcp_url: str = "http://localhost:8000") -> None:
        """Initialize the research supervisor agent.
        
        Args:
            agent_id: The ID of this agent
            broker: Optional message broker to use
            mcp_url: URL of the MCP server
        """
        super().__init__(agent_id, broker, mcp_url)
        self.workflows = {}
        self.agent_capabilities = {}
    
    async def on_startup(self) -> None:
        """Initialize the research supervisor agent."""
        self.logger.info("Starting research supervisor agent...")
        
        # Initialize agent capabilities registry
        await self._initialize_agent_capabilities()
        
        # Initialize the goal refiner
        self.goal_refiner = GoalRefiner(self.agent_capabilities, self.async_mcp_client)
        self.logger.info("Goal refiner initialized")
    
    async def _initialize_agent_capabilities(self) -> None:
        """
        Initialize the registry of agent capabilities.
        In a production system, this might be loaded from a configuration file
        or a database, or discovered dynamically from the MCP server.
        """
        # Define capabilities for each agent type
        self.agent_capabilities = {
            "xml_agent": {
                "description": "Processes XML documents and extracts entities",
                "capabilities": [
                    "extract_entities", 
                    "validate_xml", 
                    "parse_xml",
                    "analyze_structure"
                ]
            },
            "web_search_agent": {
                "description": "Performs web searches and retrieves content",
                "capabilities": [
                    "search", 
                    "fetch_content", 
                    "research_entity",
                    "find_external_sources"
                ]
            },
            "research_supervisor_agent": {
                "description": "Coordinates research workflows and synthesizes results",
                "capabilities": [
                    "coordinate_workflow",
                    "synthesize_research",
                    "process_research",
                    "generate_output"
                ]
            }
        }
        
        self.logger.info(f"Initialized capabilities for {len(self.agent_capabilities)} agent types")
    
    async def handle_research_document(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Start a research workflow for a document.
        
        Args:
            task_request: Task request with document ID and research options
            
        Returns:
            Dict with research results
        """
        doc_id = task_request.payload.get("doc_id")
        options = task_request.payload.get("options", {})
        
        if not doc_id:
            raise ValueError("Missing required parameter: doc_id")
            
        workflow_id = f"research_{doc_id}_{int(time.time())}"
        self.workflows[workflow_id] = {
            "status": "in_progress",
            "start_time": time.time(),
            "doc_id": doc_id,
            "options": options,
            "steps_completed": []
        }
        
        try:
            # Step 1: Detect document type
            self.logger.info(f"[{workflow_id}] Detecting document type for {doc_id}")
            document_type_result = await self.detect_document_type(doc_id)
            self.workflows[workflow_id]["steps_completed"].append("detect_document_type")
            
            # Step 2: Process based on document type
            if document_type_result.get("is_xml", False):
                # XML document workflow
                self.logger.info(f"[{workflow_id}] Processing XML document: {doc_id}")
                result = await self._handle_xml_research(doc_id, options, workflow_id)
            else:
                # Standard document research
                self.logger.info(f"[{workflow_id}] Processing standard document: {doc_id}")
                result = await self._handle_standard_research(doc_id, options, workflow_id)
            
            # Update workflow status
            self.workflows[workflow_id]["status"] = "completed"
            self.workflows[workflow_id]["end_time"] = time.time()
            self.workflows[workflow_id]["duration"] = self.workflows[workflow_id]["end_time"] - self.workflows[workflow_id]["start_time"]
            
            return result
        except Exception as e:
            # Update workflow status on error
            self.logger.error(f"[{workflow_id}] Error in research workflow: {e}")
            self.workflows[workflow_id]["status"] = "failed"
            self.workflows[workflow_id]["error"] = str(e)
            raise
    
    async def handle_research_entities(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Research specific entities across available sources.
        
        Args:
            task_request: Task request with entity list
            
        Returns:
            Dict with research results for each entity
        """
        entities = task_request.payload.get("entities", [])
        max_entities = task_request.payload.get("max_entities", 10)
        use_web_search = task_request.payload.get("use_web_search", True)
        search_provider = task_request.payload.get("search_provider", "brave")
        
        if not entities:
            raise ValueError("Missing required parameter: entities")
        
        # Limit to top N entities if there are too many
        if len(entities) > max_entities:
            self.logger.info(f"Limiting to top {max_entities} entities out of {len(entities)}")
            # Sort by confidence and take top N
            entities = sorted(entities, key=lambda x: x.get("confidence", 0), reverse=True)[:max_entities]
        
        research_results = []
        
        # Research each entity
        for entity in entities:
            entity_name = entity.get("name")
            if not entity_name:
                continue
                
            self.logger.info(f"Researching entity: {entity_name}")
            
            try:
                if use_web_search:
                    # Use the web search agent to research this entity
                    self.logger.info(f"Using web search to research: {entity_name}")
                    search_result = await self.send_request_and_wait(
                        target_agent="web_search_agent",
                        intent="research_entity",
                        payload={
                            "entity": entity_name,
                            "provider": search_provider,
                            "max_results": 3,  # Limit to 3 results per entity
                            "include_structured_data": True
                        }
                    )
                    
                    if search_result and search_result.status == TaskStatus.COMPLETED:
                        # Extract the research result from the search response
                        entity_result = search_result.output
                        
                        # Create a research result with the web search data
                        research_result = {
                            "entity": entity_name,
                            "definition": entity_result.get("definition", f"No definition found for {entity_name}"),
                            "confidence": entity_result.get("sources", [{}])[0].get("confidence", 0.7) if entity_result.get("sources") else 0.7,
                            "sources": entity_result.get("sources", []),
                            "original_xpath": entity.get("xpath"),
                            "original_context": entity.get("context"),
                            "structured_data": entity_result.get("structured_data")
                        }
                        
                        research_results.append(research_result)
                    else:
                        # Fall back to mock research if web search fails
                        self.logger.warning(f"Web search failed for {entity_name}, using mock data")
                        mock_result = self._generate_mock_research_result(entity)
                        research_results.append(mock_result)
                else:
                    # Use mock research data
                    mock_result = self._generate_mock_research_result(entity)
                    research_results.append(mock_result)
            except Exception as e:
                self.logger.error(f"Error researching entity {entity_name}: {e}")
                # Add with error
                research_results.append({
                    "entity": entity_name,
                    "error": str(e),
                    "definition": f"Unable to research {entity_name}",
                    "confidence": 0.0,
                    "sources": [],
                    "original_xpath": entity.get("xpath"),
                    "original_context": entity.get("context")
                })
        
        return {
            "entity_count": len(entities),
            "researched_count": len(research_results),
            "research_results": research_results,
            "used_web_search": use_web_search
        }
    
    async def handle_generate_research_xml(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Generate XML output from research results.
        
        Args:
            task_request: Task request with research results
            
        Returns:
            Dict with generated XML and validation status
        """
        original_doc_id = task_request.payload.get("original_doc_id")
        research_results = task_request.payload.get("research_results", [])
        
        if not original_doc_id or not research_results:
            raise ValueError("Missing required parameters: original_doc_id and research_results")
        
        try:
            # Get original XML content
            self.logger.info(f"Fetching original XML for {original_doc_id}")
            xml_content = await self.async_mcp_client.get_xml_content(original_doc_id)
            
            # In Phase 2, we'll generate a simple enriched XML
            # In Phase 3, we'll delegate to the Synthesis Agent
            enriched_xml = self._generate_enriched_xml(xml_content, research_results)
            
            # Basic validation (we'll improve this in Phase 3)
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": ["Basic validation only - schema validation will be added in Phase 3"]
            }
            
            return {
                "original_doc_id": original_doc_id,
                "enriched_xml": enriched_xml,
                "entity_count": len(research_results),
                "validation": validation_result
            }
        except Exception as e:
            self.logger.error(f"Error generating research XML: {e}")
            return {
                "original_doc_id": original_doc_id,
                "error": str(e),
                "validation": {
                    "valid": False,
                    "errors": [str(e)]
                }
            }
    
    async def handle_get_workflow_status(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Get the status of a research workflow.
        
        Args:
            task_request: Task request with workflow ID
            
        Returns:
            Dict with workflow status
        """
        workflow_id = task_request.payload.get("workflow_id")
        
        if not workflow_id:
            # Return all workflow statuses
            return {
                "workflows": self.workflows
            }
        
        # Return specific workflow status
        if workflow_id in self.workflows:
            return self.workflows[workflow_id]
        else:
            raise ValueError(f"Workflow not found: {workflow_id}")
            
    async def handle_process_goal(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Process a high-level user goal, break it down into tasks, and execute them.
        
        Args:
            task_request: Task request with user goal
            
        Returns:
            Dict with goal processing results
        """
        user_goal = task_request.payload.get("goal")
        options = task_request.payload.get("options", {})
        
        if not user_goal:
            raise ValueError("Missing required parameter: goal")
            
        # Create a new workflow for this goal
        workflow_id = f"goal_{int(time.time())}"
        self.workflows[workflow_id] = {
            "status": "in_progress",
            "start_time": time.time(),
            "goal": user_goal,
            "options": options,
            "steps_completed": [],
            "tasks": []
        }
        
        try:
            # Step 1: Refine the goal into structured tasks
            self.logger.info(f"[{workflow_id}] Refining goal: {user_goal}")
            refined_tasks = await self.goal_refiner.refine_goal(user_goal)
            self.workflows[workflow_id]["tasks"] = refined_tasks
            self.workflows[workflow_id]["steps_completed"].append("refine_goal")
            
            # Step 2: Execute each task in order
            results = []
            for task in refined_tasks:
                task_id = task.get("task_id", str(uuid.uuid4()))
                description = task.get("description", "")
                agent_id = task.get("assigned_agent")
                
                if not agent_id:
                    self.logger.warning(f"[{workflow_id}] No agent assigned for task: {description}")
                    # Try to clarify with user or skip
                    # For now, we'll use the supervisor as fallback
                    agent_id = "research_supervisor_agent"
                
                self.logger.info(f"[{workflow_id}] Executing task '{description}' with agent {agent_id}")
                
                # Map the task to an appropriate intent for the target agent
                intent = self._map_task_to_intent(task, agent_id)
                
                # Create task payload based on task description
                task_payload = self._create_task_payload(task, options)
                
                # Only execute the task if it maps to a known intent
                if intent:
                    # If the target is self, handle locally
                    if agent_id == self.agent_id:
                        # Create a local task request
                        local_request = TaskRequest(
                            task_id=f"{workflow_id}_{task_id}",
                            source_agent="self",
                            target_agent=self.agent_id,
                            intent=intent,
                            payload=task_payload
                        )
                        
                        # Get the appropriate handler method
                        handler_name = f"handle_{intent}"
                        handler = getattr(self, handler_name, None)
                        
                        if handler:
                            task_result = await handler(local_request)
                        else:
                            task_result = {
                                "error": f"No handler found for intent: {intent}",
                                "status": "failed"
                            }
                    else:
                        # Send to another agent
                        task_result_obj = await self.send_request_and_wait(
                            target_agent=agent_id,
                            intent=intent,
                            payload=task_payload
                        )
                        
                        if task_result_obj:
                            task_result = task_result_obj.output
                        else:
                            task_result = {
                                "error": "No response from agent",
                                "status": "failed"
                            }
                    
                    # Add result
                    results.append({
                        "task_id": task_id,
                        "description": description,
                        "agent": agent_id,
                        "intent": intent,
                        "result": task_result
                    })
                else:
                    # No intent mapping found
                    results.append({
                        "task_id": task_id,
                        "description": description,
                        "agent": agent_id,
                        "error": "No intent mapping available for this task",
                        "status": "skipped"
                    })
            
            # Update workflow status
            self.workflows[workflow_id]["status"] = "completed"
            self.workflows[workflow_id]["end_time"] = time.time()
            self.workflows[workflow_id]["duration"] = self.workflows[workflow_id]["end_time"] - self.workflows[workflow_id]["start_time"]
            self.workflows[workflow_id]["results"] = results
            
            # Return the combined results
            return {
                "workflow_id": workflow_id,
                "goal": user_goal,
                "task_count": len(refined_tasks),
                "completed_count": len([r for r in results if r.get("status") != "failed" and r.get("status") != "skipped"]),
                "results": results,
                "summary": f"Processed goal: {user_goal}",
                "status": "completed"
            }
        except Exception as e:
            # Update workflow status on error
            self.logger.error(f"[{workflow_id}] Error in goal processing: {e}")
            self.workflows[workflow_id]["status"] = "failed"
            self.workflows[workflow_id]["error"] = str(e)
            raise
    
    def _map_task_to_intent(self, task: Dict[str, Any], agent_id: str) -> Optional[str]:
        """
        Map a task to an appropriate intent for the target agent.
        
        Args:
            task: The task to map
            agent_id: The target agent ID
            
        Returns:
            The mapped intent name or None if no mapping is found
        """
        # Get required capabilities for the task
        capabilities = task.get("capabilities", [])
        
        # Map common capabilities to intents for each agent type
        capability_to_intent = {
            "xml_agent": {
                "extract_entities": "extract_entities",
                "validate_xml": "validate",
                "parse_xml": "parse_document",
                "analyze_structure": "analyze_structure"
            },
            "web_search_agent": {
                "search": "search",
                "fetch_content": "fetch_content",
                "research_entity": "research_entity",
                "find_external_sources": "search"
            },
            "research_supervisor_agent": {
                "coordinate_workflow": "research_document",
                "synthesize_research": "generate_research_xml",
                "process_research": "research_entities"
            }
        }
        
        # Get intent mappings for the target agent
        agent_intent_map = capability_to_intent.get(agent_id, {})
        
        # Find the first capability that maps to an intent for this agent
        for capability in capabilities:
            if capability in agent_intent_map:
                return agent_intent_map[capability]
        
        # If no mapping found but this is a standard task type, use default mappings
        description = task.get("description", "").lower()
        
        if "search" in description and agent_id == "web_search_agent":
            return "search"
        elif "research" in description and agent_id == "web_search_agent":
            return "research_entity"
        elif "extract" in description and agent_id == "xml_agent":
            return "extract_entities"
        
        # No mapping found
        return None
    
    def _create_task_payload(self, task: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a payload for a task based on its description and type.
        
        Args:
            task: The task to create a payload for
            options: Additional options to include
            
        Returns:
            The task payload
        """
        description = task.get("description", "")
        capabilities = task.get("capabilities", [])
        
        # Start with a basic payload including the original task data
        payload = {
            "original_task": task,
            "options": options
        }
        
        # Add payload details based on the task description and capabilities
        if "search" in capabilities:
            # For search tasks, extract the query from the description
            payload["query"] = description
            payload["max_results"] = options.get("max_results", 5)
        
        elif "research_entity" in capabilities:
            # For entity research, extract the entity from the description
            # This is a simplified approach - in a real system, you'd use NLP to extract entities
            words = description.split()
            if len(words) > 2:
                # Assume the entity is the last word or phrase
                payload["entity"] = words[-1]
            else:
                payload["entity"] = description
        
        elif "extract_entities" in capabilities or "parse_xml" in capabilities or "analyze_structure" in capabilities:
            # For XML-related tasks, we need a document ID
            if "doc_id" in options:
                payload["doc_id"] = options["doc_id"]
                
                # If this is a command extraction task, set the appropriate options
                if "extract" in description.lower() and any(term in description.lower() for term in 
                                                          ["command", "step", "config", "cisco", "router"]):
                    payload["extract_type"] = "commands"
                    payload["format"] = options.get("format", "text")
                    
                # If this is a validation task, set validation options
                elif any(term in description.lower() for term in ["validate", "verify", "check"]):
                    payload["validation_level"] = options.get("validation_level", "standard")
        
        elif "validate_xml" in capabilities:
            # For XML validation, we need a document ID
            if "doc_id" in options:
                payload["doc_id"] = options["doc_id"]
                payload["validation_level"] = options.get("validation_level", "standard")
        
        # Add any additional options from the task itself
        task_options = task.get("options", {})
        if task_options:
            payload["options"].update(task_options)
        
        return payload
    
    async def detect_document_type(self, doc_id: str) -> Dict[str, Any]:
        """
        Detect the document type and specialized handling needs.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Dict with document type information
        """
        try:
            # Attempt to get the document
            doc = await self.async_mcp_client.get_document(doc_id)
            
            # Detect XML
            is_xml = False
            needs_verification = False
            
            if hasattr(doc, 'doc_type') and doc.doc_type == "xml":
                is_xml = True
                needs_verification = True
            elif hasattr(doc, 'content') and isinstance(doc.content, str):
                # Check for XML signatures in content
                if doc.content.strip().startswith('<?xml'):
                    is_xml = True
                    needs_verification = True
            
            # Check for entity tags or structure that suggests research need
            needs_research = is_xml
            
            return {
                "doc_id": doc_id,
                "detected_type": getattr(doc, 'doc_type', 'unknown'),
                "is_xml": is_xml,
                "needs_verification": needs_verification,
                "needs_research": needs_research,
                "title": getattr(doc, 'title', ''),
                "content_excerpt": getattr(doc, 'content', '')[:100] if hasattr(doc, 'content') else ""
            }
        except Exception as e:
            self.logger.error(f"Error detecting document type: {e}")
            return {
                "doc_id": doc_id,
                "error": str(e),
                "is_xml": False,
                "needs_verification": False,
                "needs_research": False
            }
    
    async def _handle_xml_research(self, doc_id: str, options: Dict, workflow_id: str) -> Dict[str, Any]:
        """
        Handle research workflow for XML documents.
        
        Args:
            doc_id: Document ID
            options: Research options
            workflow_id: Workflow tracking ID
            
        Returns:
            Dict with research results
        """
        # Extract entities from XML
        self.logger.info(f"[{workflow_id}] Extracting entities from {doc_id}")
        entity_result = await self.send_request_and_wait(
            target_agent="xml_agent",
            intent="extract_entities",
            payload={
                "doc_id": doc_id,
                "options": options
            }
        )
        if entity_result:
            entity_result = entity_result.output
        else:
            entity_result = {"entity_count": 0, "entities": []}
        self.workflows[workflow_id]["steps_completed"].append("extract_entities")
        
        # Research entities
        self.logger.info(f"[{workflow_id}] Researching {len(entity_result.get('entities', []))} entities")
        research_result = await self.handle_research_entities(TaskRequest(
            task_id=f"{workflow_id}_research",
            source_agent="self",
            target_agent=self.agent_id,
            intent="research_entities",
            payload={
                "entities": entity_result.get("entities", []),
                "max_entities": options.get("max_entities", 10),
                "use_web_search": options.get("use_web_search", True),
                "search_provider": options.get("search_provider", "brave")
            }
        ))
        self.workflows[workflow_id]["steps_completed"].append("research_entities")
        
        # Generate enriched XML
        self.logger.info(f"[{workflow_id}] Generating enriched XML")
        xml_result = await self.handle_generate_research_xml(TaskRequest(
            task_id=f"{workflow_id}_xml",
            source_agent="self",
            target_agent=self.agent_id,
            intent="generate_research_xml",
            payload={
                "original_doc_id": doc_id,
                "research_results": research_result.get("research_results", []),
                "format": options.get("format", "xml")
            }
        ))
        self.workflows[workflow_id]["steps_completed"].append("generate_research_xml")
        
        return {
            "doc_id": doc_id,
            "entity_count": entity_result.get("entity_count", 0),
            "research_count": len(research_result.get("research_results", [])),
            "enriched_xml": xml_result.get("enriched_xml"),
            "validation": xml_result.get("validation"),
            "summary": f"Research completed for {entity_result.get('entity_count', 0)} entities from XML document {doc_id}",
            "workflow_id": workflow_id
        }
    
    async def _handle_standard_research(self, doc_id: str, options: Dict, workflow_id: str) -> Dict[str, Any]:
        """
        Handle research workflow for standard (non-XML) documents.
        
        Args:
            doc_id: Document ID
            options: Research options
            workflow_id: Workflow tracking ID
            
        Returns:
            Dict with research results
        """
        # For Phase 2, we'll just handle XML documents
        # This is a placeholder for future implementation
        return {
            "doc_id": doc_id,
            "error": "Standard document research not yet implemented",
            "workflow_id": workflow_id
        }
    
    def _generate_mock_research_result(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate mock research result for an entity.
        
        Args:
            entity: Entity information
            
        Returns:
            Dict with research result
        """
        entity_name = entity.get("name", "")
        context = entity.get("context", "")
        
        # Generate a mock definition based on entity name
        definition = f"{entity_name} is a term used in the context of artificial intelligence and natural language processing."
        
        if "language" in entity_name.lower():
            definition = f"{entity_name} refers to computational techniques for processing and analyzing human language."
        elif "model" in entity_name.lower():
            definition = f"{entity_name} is a mathematical representation of data patterns used in machine learning."
        elif "gpt" in entity_name.lower():
            definition = f"{entity_name} is a generative pre-trained transformer model developed by OpenAI for natural language tasks."
        
        # Add context-specific information if available
        if context:
            definition += f" In the provided context, it relates to: {context[:100]}..."
        
        # Generate mock sources using the Source model
        sources = [
            Source(
                source_id=str(uuid.uuid4()),
                source_type=SourceType.WEB,
                title=f"{entity_name} - Wikipedia",
                url=f"https://en.wikipedia.org/wiki/{entity_name.replace(' ', '_')}",
                retrieved_at=datetime.datetime.now(),
                confidence=0.85,
                citation=f"Wikipedia. \"{entity_name}\" Retrieved on {datetime.datetime.now().strftime('%Y-%m-%d')}."
            ),
            Source(
                source_id=str(uuid.uuid4()),
                source_type=SourceType.DOCUMENT,
                title="AI Research Papers",
                doc_id="doc1",
                retrieved_at=datetime.datetime.now(),
                confidence=0.65,
                citation="Internal Research Document: \"AI Research Papers\" (2023)"
            )
        ]
        
        return {
            "entity": entity_name,
            "definition": definition,
            "confidence": 0.75,
            "sources": sources,
            "original_xpath": entity.get("xpath"),
            "original_context": context
        }
    
    def _generate_enriched_xml(self, xml_content: str, research_results: List[Dict[str, Any]]) -> str:
        """
        Generate enriched XML with research results.
        
        Args:
            xml_content: Original XML content
            research_results: Research results for entities
            
        Returns:
            Enriched XML content
        """
        # For Phase 2, we'll implement a simple XML transformation
        # In Phase 3, we'll implement a more sophisticated approach with proper XML parsing
        
        # Create a basic XML header
        enriched_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        enriched_xml += '<research-document>\n'
        
        # Include original XML
        enriched_xml += '  <original-content>\n'
        # Indent each line of the original XML
        for line in xml_content.splitlines():
            enriched_xml += f"    {line}\n"
        enriched_xml += '  </original-content>\n'
        
        # Add research results
        enriched_xml += '  <research-results>\n'
        for result in research_results:
            entity = result.get("entity", "")
            definition = result.get("definition", "")
            confidence = result.get("confidence", 0.0)
            
            enriched_xml += f'    <entity-research entity="{entity}" confidence="{confidence:.2f}">\n'
            enriched_xml += f'      <definition>{definition}</definition>\n'
            
            # Add sources with enhanced attribution
            enriched_xml += '      <sources>\n'
            for source in result.get("sources", []):
                # Check if we're dealing with a Source object or a dict
                if isinstance(source, Source):
                    # Use properties of Source model
                    source_type = source.source_type.value
                    source_title = source.title
                    source_id = source.source_id
                    source_url = source.url or ""
                    source_confidence = source.confidence
                    source_citation = source.citation or ""
                    retrieved_at = ""
                    if source.retrieved_at:
                        retrieved_at = source.retrieved_at.isoformat()
                    
                    # Generate enhanced XML with more attribution data
                    enriched_xml += f'        <source id="{source_id}" type="{source_type}"'
                    if source_url:
                        enriched_xml += f' url="{source_url}"'
                    enriched_xml += f' confidence="{source_confidence:.2f}"'
                    if retrieved_at:
                        enriched_xml += f' retrieved_at="{retrieved_at}"'
                    enriched_xml += f'>\n'
                    enriched_xml += f'          <title>{source_title}</title>\n'
                    if source_citation:
                        enriched_xml += f'          <citation>{source_citation}</citation>\n'
                    enriched_xml += f'        </source>\n'
                else:
                    # Fallback for backward compatibility with dict format
                    source_type = source.get("type", "unknown")
                    source_title = source.get("title", "")
                    source_url = source.get("url", "")
                    
                    enriched_xml += f'        <source type="{source_type}"'
                    if source_url:
                        enriched_xml += f' url="{source_url}"'
                    enriched_xml += f'>{source_title}</source>\n'
            
            enriched_xml += '      </sources>\n'
            enriched_xml += '    </entity-research>\n'
        
        enriched_xml += '  </research-results>\n'
        enriched_xml += '</research-document>'
        
        return enriched_xml