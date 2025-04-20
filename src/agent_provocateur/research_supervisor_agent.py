"""Research Supervisor Agent for orchestrating document research workflows."""

from typing import Any, Dict, List, Optional
import logging
import asyncio
import time

from agent_provocateur.a2a_models import TaskRequest, TaskStatus
from agent_provocateur.agent_base import BaseAgent
from agent_provocateur.models import Document

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
    
    async def on_startup(self) -> None:
        """Initialize the research supervisor agent."""
        self.logger.info("Starting research supervisor agent...")
    
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
            
            # Mock research for now - in a real implementation we would call other agents
            # This is a simplified version for Phase 2
            try:
                # Simulate research by generating a mock result
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
            "research_results": research_results
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
                "max_entities": options.get("max_entities", 10)
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
        
        # Generate mock sources
        sources = [
            {
                "type": "web",
                "title": f"{entity_name} - Wikipedia",
                "url": f"https://en.wikipedia.org/wiki/{entity_name.replace(' ', '_')}"
            },
            {
                "type": "document",
                "title": "AI Research Papers",
                "doc_id": "doc1"
            }
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
            
            # Add sources
            enriched_xml += '      <sources>\n'
            for source in result.get("sources", []):
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