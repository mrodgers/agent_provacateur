"""XML Agent for processing and verification of XML documents."""

from typing import Any, Dict, List, Optional
import logging
import asyncio
import time

from agent_provocateur.a2a_models import TaskRequest, TaskStatus
from agent_provocateur.agent_base import BaseAgent
from agent_provocateur.models import XmlDocument, XmlNode
from agent_provocateur.xml_parser import (
    identify_researchable_nodes_advanced,
    analyze_xml_verification_needs
)

logger = logging.getLogger(__name__)

class XmlAgent(BaseAgent):
    """Agent for XML document analysis and verification planning."""
    
    async def on_startup(self) -> None:
        """Initialize the XML agent."""
        self.logger.info("Starting XML agent...")
        self.verification_config = {
            "min_confidence": 0.5,
            "custom_rules": {},
            "prioritize_recent": True,
            "max_nodes_per_task": 5
        }
    
    async def handle_analyze_xml(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Analyze an XML document to identify verification needs.
        
        Args:
            task_request: Task request with XML document ID
            
        Returns:
            Dict with analysis results
        """
        doc_id = task_request.payload.get("doc_id")
        if not doc_id:
            raise ValueError("Missing required parameter: doc_id")
        
        # Retrieve the XML document
        xml_doc = await self.async_mcp_client.get_xml_document(doc_id)
        
        # Analyze verification needs
        analysis = analyze_xml_verification_needs(xml_doc)
        
        return {
            "doc_id": doc_id,
            "title": xml_doc.title,
            "analysis": analysis,
            "node_count": len(xml_doc.researchable_nodes),
            "root_element": xml_doc.root_element
        }
    
    async def handle_identify_nodes(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Identify researchable nodes in an XML document with advanced rules.
        
        Args:
            task_request: Task request with XML document ID and optional rules
            
        Returns:
            Dict with identified nodes
        """
        doc_id = task_request.payload.get("doc_id")
        if not doc_id:
            raise ValueError("Missing required parameter: doc_id")
        
        # Get optional parameters
        keyword_rules = task_request.payload.get("keyword_rules")
        attribute_rules = task_request.payload.get("attribute_rules")
        content_patterns = task_request.payload.get("content_patterns")
        min_confidence = task_request.payload.get("min_confidence", 0.5)
        
        # Get XML content
        xml_content = await self.async_mcp_client.get_xml_content(doc_id)
        
        # Identify researchable nodes
        nodes = identify_researchable_nodes_advanced(
            xml_content,
            keyword_rules=keyword_rules,
            attribute_rules=attribute_rules,
            content_patterns=content_patterns,
            min_confidence=min_confidence
        )
        
        # Sort nodes by confidence
        sorted_nodes = sorted(
            nodes,
            key=lambda x: x.verification_data.get("confidence", 0.0),
            reverse=True
        )
        
        return {
            "doc_id": doc_id,
            "node_count": len(sorted_nodes),
            "nodes": [node.dict() for node in sorted_nodes],
            "confidence_threshold": min_confidence
        }
    
    async def handle_create_verification_plan(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Create a verification plan for an XML document.
        
        Args:
            task_request: Task request with XML document ID
            
        Returns:
            Dict with verification plan
        """
        doc_id = task_request.payload.get("doc_id")
        if not doc_id:
            raise ValueError("Missing required parameter: doc_id")
        
        # Get XML document
        xml_doc = await self.async_mcp_client.get_xml_document(doc_id)
        
        # Analyze verification needs
        analysis = analyze_xml_verification_needs(xml_doc)
        
        # If verification not needed, return early
        if not analysis.get("verification_needed", False):
            return {
                "doc_id": doc_id,
                "verification_needed": False,
                "reason": analysis.get("reason", "No verification needed")
            }
        
        # Create verification tasks
        tasks = self._create_verification_tasks(xml_doc.researchable_nodes, analysis)
        
        return {
            "doc_id": doc_id,
            "title": xml_doc.title,
            "verification_needed": True,
            "priority": analysis.get("priority", "medium"),
            "estimated_time_minutes": analysis.get("estimated_time_minutes", 0),
            "node_count": len(xml_doc.researchable_nodes),
            "tasks": tasks,
            "recommended_approach": analysis.get("recommended_approach", "sequential")
        }
    
    async def handle_update_node_status(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Update the verification status of an XML node.
        
        Args:
            task_request: Task request with document ID, node information, and verification results
            
        Returns:
            Dict with update result
        """
        doc_id = task_request.payload.get("doc_id")
        xpath = task_request.payload.get("xpath")
        new_status = task_request.payload.get("status")
        verification_data = task_request.payload.get("verification_data", {})
        
        if not doc_id or not xpath or not new_status:
            raise ValueError("Missing required parameters: doc_id, xpath, and status are required")
        
        # This is a mock implementation - in a real system we would update the node in a database
        # For this mock version, we just return the update information
        
        return {
            "doc_id": doc_id,
            "xpath": xpath,
            "old_status": "pending",
            "new_status": new_status,
            "verification_data": verification_data,
            "updated_at": time.time()
        }
    
    async def handle_batch_verify_nodes(self, task_request: TaskRequest) -> Dict[str, Any]:
        """
        Start batch verification of multiple nodes.
        
        Args:
            task_request: Task request with document ID and verification options
            
        Returns:
            Dict with batch verification results
        """
        doc_id = task_request.payload.get("doc_id")
        nodes = task_request.payload.get("nodes", [])
        options = task_request.payload.get("options", {})
        
        if not doc_id:
            raise ValueError("Missing required parameter: doc_id")
        
        if not nodes:
            # If no specific nodes provided, get all pending nodes
            xml_doc = await self.async_mcp_client.get_xml_document(doc_id)
            nodes = [
                node.dict() for node in xml_doc.researchable_nodes 
                if node.verification_status == "pending"
            ]
        
        # This would delegate to verification tasks in a real implementation
        # For this mock, we'll simulate the process
        
        completed = 0
        verification_results = []
        
        # Process each node
        for node in nodes:
            # In a real implementation, we'd do actual verification
            # For now, we'll just simulate different verification outcomes
            
            element_name = node.get("element_name", "unknown")
            content = node.get("content", "")
            
            # Mock verification process based on node attributes
            if "high" in node.get("attributes", {}).get("confidence", ""):
                status = "verified"
                confidence = 0.9
                sources = ["Trusted source 1", "Database match"]
            elif "medium" in node.get("attributes", {}).get("confidence", ""):
                status = "partially_verified"
                confidence = 0.6
                sources = ["Single source"]
            else:
                status = "unverified"
                confidence = 0.3
                sources = []
            
            # Record result
            verification_results.append({
                "xpath": node.get("xpath"),
                "element_name": element_name,
                "status": status,
                "confidence": confidence,
                "sources": sources,
                "notes": f"Mock verification for {element_name}"
            })
            
            completed += 1
        
        return {
            "doc_id": doc_id,
            "total_nodes": len(nodes),
            "completed_nodes": completed,
            "verification_results": verification_results,
            "options": options
        }
    
    def _create_verification_tasks(
        self, 
        nodes: List[XmlNode], 
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create individual verification tasks from a list of nodes.
        
        Args:
            nodes: List of XML nodes to verify
            analysis: Analysis information
            
        Returns:
            List of verification task definitions
        """
        tasks = []
        max_nodes_per_task = self.verification_config.get("max_nodes_per_task", 5)
        
        # Group nodes by element type
        grouped_nodes = {}
        for node in nodes:
            element_name = node.element_name
            if element_name not in grouped_nodes:
                grouped_nodes[element_name] = []
            grouped_nodes[element_name].append(node)
        
        # Create tasks for each group
        task_id = 1
        for element_name, element_nodes in grouped_nodes.items():
            # Split into batches
            for i in range(0, len(element_nodes), max_nodes_per_task):
                batch = element_nodes[i:i + max_nodes_per_task]
                
                # Create task
                task = {
                    "task_id": f"verify_{task_id}",
                    "element_type": element_name,
                    "node_count": len(batch),
                    "priority": "high" if element_name in ["claim", "finding", "fact"] else "medium",
                    "estimated_minutes": len(batch) * 5,
                    "nodes": [node.dict() for node in batch]
                }
                
                tasks.append(task)
                task_id += 1
        
        # Sort tasks by priority
        tasks.sort(key=lambda x: 0 if x["priority"] == "high" else 1)
        
        return tasks