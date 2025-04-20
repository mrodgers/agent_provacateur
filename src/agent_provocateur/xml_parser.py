"""XML parsing and processing utilities for Agent Provocateur."""

from typing import Any, Dict, List, Optional, Tuple
import logging
from datetime import datetime
import re
from defusedxml import ElementTree
from pathlib import Path

from agent_provocateur.models import XmlDocument, XmlNode

logger = logging.getLogger(__name__)

def parse_xml(xml_content: str) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    Parse XML content into a structured dictionary and extract namespaces.
    
    Args:
        xml_content: Raw XML string
        
    Returns:
        Tuple containing:
        - Dict representation of the XML
        - Dict of namespaces
    """
    try:
        # Use defusedxml for security (prevents XXE attacks)
        root = ElementTree.fromstring(xml_content)
        
        # Extract namespaces from attributes (explicit declarations)
        namespaces = {}
        
        # We need to parse the raw XML string to find xmlns declarations
        # This is a simple approach for testing purposes
        xmlns_pattern = r'xmlns:([a-zA-Z0-9]+)="([^"]+)"'
        matches = re.findall(xmlns_pattern, xml_content)
        for prefix, uri in matches:
            namespaces[prefix] = uri
        
        # Convert to dictionary
        result = _element_to_dict(root)
        
        return result, namespaces
    except Exception as e:
        logger.error(f"Error parsing XML: {e}")
        raise ValueError(f"Failed to parse XML: {str(e)}")

def _element_to_dict(element) -> Dict[str, Any]:
    """Convert an XML element to a dictionary."""
    result = {}
    
    # Add attributes
    if element.attrib:
        result["@attributes"] = dict(element.attrib)
    
    # Add children or text
    if element.text and element.text.strip():
        result["#text"] = element.text.strip()
    
    for child in element:
        child_dict = _element_to_dict(child)
        child_tag = child.tag
        
        # Handle namespaces in tags
        if "}" in child_tag:
            child_tag = child_tag.split("}", 1)[1]
        
        if child_tag in result:
            # Convert to list if multiple elements with same tag
            if isinstance(result[child_tag], list):
                result[child_tag].append(child_dict)
            else:
                result[child_tag] = [result[child_tag], child_dict]
        else:
            result[child_tag] = child_dict
    
    return result

def create_xml_document(xml_content: str, doc_id: str, title: str) -> XmlDocument:
    """
    Create an XmlDocument from raw XML content.
    
    Args:
        xml_content: Raw XML string
        doc_id: Document ID
        title: Document title
        
    Returns:
        XmlDocument instance
    """
    try:
        # Parse XML
        parsed_dict, namespaces = parse_xml(xml_content)
        
        # Extract root element name
        root = ElementTree.fromstring(xml_content)
        root_name = root.tag
        if "}" in root_name:
            root_name = root_name.split("}", 1)[1]
        
        # Create document
        now = datetime.utcnow().isoformat()
        
        return XmlDocument(
            doc_id=doc_id,
            title=title,
            content=xml_content,
            root_element=root_name,
            namespaces=namespaces,
            created_at=now,
            updated_at=now,
            metadata={"element_count": _count_elements(root)},
        )
    except Exception as e:
        logger.error(f"Error creating XML document: {e}")
        raise ValueError(f"Failed to create XML document: {str(e)}")

def _count_elements(element) -> int:
    """Count the number of elements in an XML tree."""
    count = 1  # Count this element
    for child in element:
        count += _count_elements(child)
    return count

def identify_researchable_nodes(xml_content: str, xpath_rules: List[str] = None) -> List[XmlNode]:
    """
    Identify nodes in an XML document that need verification based on XPath rules.
    
    Args:
        xml_content: Raw XML content
        xpath_rules: List of XPath expressions to identify nodes (default: None)
        
    Returns:
        List of XmlNode objects
    """
    try:
        # Default rules if none provided
        if xpath_rules is None:
            xpath_rules = [
                "//finding", 
                "//claim",
                "//statement",
                "//fact",
                "//reference"
            ]
        
        root = ElementTree.fromstring(xml_content)
        researchable_nodes = []
        
        # Very simple XPath for initial implementation
        for xpath in xpath_rules:
            try:
                # Find matching elements (simple implementation)
                elements = []
                for child in root.iter():
                    # Simple tag matching (this is not a full XPath implementation)
                    tag_name = child.tag
                    if "}" in tag_name:
                        tag_name = tag_name.split("}", 1)[1]
                    
                    if xpath.endswith(tag_name):
                        elements.append(child)
                
                # Process matching elements
                for element in elements:
                    tag_name = element.tag
                    if "}" in tag_name:
                        tag_name = tag_name.split("}", 1)[1]
                    
                    node = XmlNode(
                        xpath=f"//{tag_name}",  # Simplified XPath
                        element_name=tag_name,
                        content=element.text.strip() if element.text else None,
                        attributes={k: v for k, v in element.attrib.items()},
                        verification_status="pending"
                    )
                    researchable_nodes.append(node)
            except Exception as e:
                logger.warning(f"Error processing XPath rule '{xpath}': {e}")
        
        return researchable_nodes
    except Exception as e:
        logger.error(f"Error identifying researchable nodes: {e}")
        return []

def identify_researchable_nodes_advanced(
    xml_content: str, 
    keyword_rules: Dict[str, List[str]] = None,
    attribute_rules: Dict[str, List[str]] = None,
    content_patterns: List[str] = None,
    min_confidence: float = 0.5
) -> List[XmlNode]:
    """
    Advanced identification of nodes requiring verification using multiple rule types.
    
    Args:
        xml_content: Raw XML content
        keyword_rules: Dictionary mapping element names to lists of keywords that indicate the need for verification
        attribute_rules: Dictionary mapping attribute names to lists of values that indicate the need for verification
        content_patterns: List of regex patterns to match against node text content
        min_confidence: Minimum confidence score (0.0-1.0) to include a node
        
    Returns:
        List of XmlNode objects
    """
    try:
        # Default keyword rules if none provided
        if keyword_rules is None:
            keyword_rules = {
                "claim": ["all", "every", "never", "always", "best", "worst", "only", "unique", "first", "100%"],
                "statement": ["proves", "proven", "verified", "confirmed", "established", "shows", "demonstrates"],
                "finding": ["significant", "breakthrough", "revolutionary", "unprecedented", "game-changing"],
                "fact": ["fact", "evidence", "proof", "data", "research", "study", "survey", "statistic"],
                "reference": ["according", "cited", "source", "reference", "publication", "report", "journal"]
            }
        
        # Default attribute rules if none provided
        if attribute_rules is None:
            attribute_rules = {
                "confidence": ["low", "medium"],
                "status": ["unverified", "preliminary", "pending"],
                "type": ["claim", "assertion", "statement"]
            }
        
        # Default content patterns if none provided
        if content_patterns is None:
            content_patterns = [
                r"\d+%",  # Percentages
                r"\$\d+",  # Dollar amounts
                r"\b\d{4}\b",  # Years
                r"(increased|decreased|improved|reduced) by \d+",  # Changes
                r"(most|best|worst|highest|lowest|first|only|never|always)"  # Absolute terms
            ]
        
        root = ElementTree.fromstring(xml_content)
        researchable_nodes = []
        confidence_scores = {}
        
        # Process all elements
        for element in root.iter():
            tag_name = element.tag
            if "}" in tag_name:
                tag_name = tag_name.split("}", 1)[1]
            
            # Skip processing tags that are likely not content
            if tag_name.lower() in ["html", "head", "style", "script", "meta"]:
                continue
            
            # Initialize confidence score
            confidence = 0.0
            evidence = []
            
            # Check element name
            for key, keywords in keyword_rules.items():
                if tag_name.lower() == key.lower():
                    confidence += 0.6
                    evidence.append(f"Element tag '{tag_name}' matches verification rule")
                    break
            
            # Check attributes
            for attr_name, attr_values in attribute_rules.items():
                if attr_name in element.attrib:
                    attr_value = element.attrib[attr_name].lower()
                    for value in attr_values:
                        if value.lower() in attr_value:
                            confidence += 0.3
                            evidence.append(f"Attribute '{attr_name}={attr_value}' requires verification")
                            break
            
            # Check content
            if element.text and element.text.strip():
                content = element.text.strip()
                
                # Apply content pattern rules
                for pattern in content_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        confidence += 0.1 * len(matches)
                        evidence.append(f"Content contains {len(matches)} matches for pattern '{pattern}'")
                
                # Check content length - longer content is more likely to need verification
                if len(content) > 100:
                    confidence += 0.1
                
                # Check for claim language
                claim_terms = ["claim", "prove", "show", "demonstrate", "assert", "state", "argue", "suggest"]
                if any(term in content.lower() for term in claim_terms):
                    confidence += 0.2
                    evidence.append("Content contains claim language")
            
            # Calculate final confidence
            confidence = min(confidence, 1.0)  # Cap at 1.0
            confidence_scores[element] = (confidence, evidence)
            
            # Add to researchable nodes if confidence meets threshold
            if confidence >= min_confidence:
                # Generate proper XPath for the element (simplified version for tests)
                xpath = f"//{tag_name}"
                if "id" in element.attrib:
                    xpath += f"[@id='{element.attrib['id']}']"
                
                # Create node
                node = XmlNode(
                    xpath=xpath,
                    element_name=tag_name,
                    content=element.text.strip() if element.text else None,
                    attributes={k: v for k, v in element.attrib.items()},
                    verification_status="pending",
                    verification_data={
                        "confidence": confidence,
                        "evidence": evidence
                    }
                )
                researchable_nodes.append(node)
        
        # Sort nodes by confidence (highest first)
        researchable_nodes.sort(key=lambda x: x.verification_data.get("confidence", 0), reverse=True)
        
        return researchable_nodes
    except Exception as e:
        logger.error(f"Error in advanced node identification: {e}")
        # Fall back to simple implementation
        return identify_researchable_nodes(xml_content)

def _generate_xpath(element) -> str:
    """Generate a proper XPath for an element (simplified version)."""
    tag = element.tag
    if "}" in tag:
        tag = tag.split("}", 1)[1]
    
    xpath = f"//{tag}"
    
    # Add id attribute if available for specificity
    if "id" in element.attrib:
        xpath += f"[@id='{element.attrib['id']}']"
    
    return xpath

def load_xml_file(file_path: str) -> str:
    """
    Load XML content from a file.
    
    Args:
        file_path: Path to XML file
        
    Returns:
        XML content as string
    """
    try:
        path = Path(file_path)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading XML file: {e}")
        raise ValueError(f"Failed to load XML file: {str(e)}")

def analyze_xml_verification_needs(xml_doc: XmlDocument) -> Dict[str, Any]:
    """
    Analyze an XML document to determine verification needs.
    
    Args:
        xml_doc: XmlDocument instance
        
    Returns:
        Dictionary with analysis results
    """
    try:
        # Get statistics on researchable nodes
        node_count = len(xml_doc.researchable_nodes)
        if node_count == 0:
            return {
                "verification_needed": False,
                "reason": "No researchable nodes identified"
            }
        
        # Count nodes by element type
        element_counts = {}
        for node in xml_doc.researchable_nodes:
            element_name = node.element_name
            element_counts[element_name] = element_counts.get(element_name, 0) + 1
        
        # Prioritize nodes by importance
        high_priority_elements = ["claim", "finding", "fact"]
        high_priority_count = sum(element_counts.get(e, 0) for e in high_priority_elements)
        
        # Get overall priority level
        if high_priority_count > 0:
            priority = "high"
        elif node_count > 5:
            priority = "medium"
        else:
            priority = "low"
        
        return {
            "verification_needed": True,
            "priority": priority,
            "node_count": node_count,
            "element_types": element_counts,
            "estimated_time_minutes": node_count * 5,  # Rough estimate: 5 minutes per node
            "recommended_approach": "parallel" if node_count > 3 else "sequential"
        }
    except Exception as e:
        logger.error(f"Error analyzing verification needs: {e}")
        return {
            "verification_needed": False,
            "error": str(e)
        }