# XML Verification Component

The XML Verification component in Agent Provocateur is a specialized system for analyzing XML documents, identifying content that requires verification, and creating structured verification plans.

## Overview

The XML Verification component consists of:

1. **XML Parser**: Utilities for parsing, analyzing, and extracting verification-worthy content from XML documents
2. **XML Agent**: A specialized agent that handles XML document analysis and verification planning
3. **CLI Tools**: Command-line interfaces for interactive testing and document processing
4. **Integration APIs**: Integration points with the broader Agent Provocateur ecosystem

## Key Features

- **Advanced Node Identification**: Automatically identifies content requiring verification using rule-based analysis
- **Confidence Scoring**: Assigns confidence scores to indicate verification priority
- **Verification Planning**: Creates structured plans with prioritized tasks
- **XPath Navigation**: Uses XPath expressions to precisely locate nodes in XML documents
- **Rule Customization**: Supports custom rules for different document types and domains
- **Batch Processing**: Enables processing of multiple verification tasks in parallel

## Architecture

```
┌─────────────────┐      ┌─────────────────┐     ┌─────────────────┐
│   XML Parser    │─────▶│    XML Agent    │────▶│  MCP Integration │
└─────────────────┘      └─────────────────┘     └─────────────────┘
       ▲                        │                        │
       │                        │                        │
       │                        ▼                        ▼
┌─────────────────┐      ┌─────────────────┐     ┌─────────────────┐
│  XML Documents  │      │ Verification    │     │  A2A Messaging  │
│                 │      │ Planning        │     │                 │
└─────────────────┘      └─────────────────┘     └─────────────────┘
```

## XML Parser (`xml_parser.py`)

The XML parser provides functions for:

- Parsing XML content into structured dictionaries
- Identifying researchable nodes using XPath expressions
- Advanced node identification with confidence scoring
- Verification needs analysis
- Loading XML from files

Key functions include:

```python
parse_xml(xml_content: str) -> Tuple[Dict[str, Any], Dict[str, str]]
create_xml_document(xml_content: str, doc_id: str, title: str) -> XmlDocument
identify_researchable_nodes(xml_content: str, xpath_rules: List[str] = None) -> List[XmlNode]
identify_researchable_nodes_advanced(xml_content: str, keyword_rules: Dict, ...) -> List[XmlNode]
analyze_xml_verification_needs(xml_doc: XmlDocument) -> Dict[str, Any]
```

## XML Agent (`xml_agent.py`)

The XML Agent extends the BaseAgent class and provides:

- On-demand XML document analysis
- Advanced node identification with customizable rules
- Verification plan creation with task prioritization
- Node status updates for verification results
- Batch verification of multiple nodes

Key handlers include:

```python
handle_analyze_xml(task_request: TaskRequest) -> Dict[str, Any]
handle_identify_nodes(task_request: TaskRequest) -> Dict[str, Any]
handle_create_verification_plan(task_request: TaskRequest) -> Dict[str, Any]
handle_update_node_status(task_request: TaskRequest) -> Dict[str, Any]
handle_batch_verify_nodes(task_request: TaskRequest) -> Dict[str, Any]
```

## Data Models

The component defines and uses two main data models:

### XmlDocument

```python
class XmlDocument(Document):
    content: str
    schema_url: Optional[str]
    root_element: str
    namespaces: Dict[str, str]
    researchable_nodes: List[XmlNode]
    doc_type: str = "xml"
```

### XmlNode

```python
class XmlNode(BaseModel):
    xpath: str
    element_name: str
    content: Optional[str]
    attributes: Dict[str, str]
    verification_status: str
    verification_data: Dict[str, Any]
```

## Command-Line Tools

### Basic XML CLI (`xml_cli.py`)

The `xml_cli.py` script provides basic document operations:

```bash
# List all XML documents
python xml_cli.py list

# View document details
python xml_cli.py get xml1 --nodes

# Upload a new XML document
python xml_cli.py upload sample.xml --title "My Document"
```

### XML Agent CLI (`xml_agent_cli.py`)

The `xml_agent_cli.py` script provides advanced functionality:

```bash
# Identify researchable nodes with confidence scoring
python xml_agent_cli.py identify --file sample.xml --confidence 0.4 --evidence

# Create verification plan
python xml_agent_cli.py plan xml1

# Test batch verification
python xml_agent_cli.py verify xml1 --search-depth high
```

## Customization

### Verification Rules

You can customize verification rules using a JSON configuration file:

```json
{
  "keyword_rules": {
    "claim": ["all", "every", "never", "always", "best", "worst"],
    "statement": ["proves", "confirmed", "established"]
  },
  "attribute_rules": {
    "confidence": ["low", "medium", "uncertain"],
    "status": ["unverified", "preliminary", "pending"]
  },
  "content_patterns": [
    "\\d+%",
    "\\$\\d+",
    "(increased|decreased) by \\d+"
  ]
}
```

### Agent Configuration

The XML Agent can be configured with:

```python
agent.verification_config = {
    "min_confidence": 0.5,
    "custom_rules": {},
    "prioritize_recent": True,
    "max_nodes_per_task": 5
}
```

## Integration

The XML Verification component integrates with:

1. **MCP Server**: For document storage and retrieval
2. **A2A Messaging**: For task-based communication with other agents
3. **Workflows**: For integration into larger verification workflows

## Usage Examples

### Programmatic Usage

```python
import asyncio
from agent_provocateur.xml_agent import XmlAgent
from agent_provocateur.a2a_models import TaskRequest

async def main():
    # Initialize agent
    agent = XmlAgent(agent_id="xml_agent")
    
    # Create verification plan
    task_request = TaskRequest(
        task_id="test_task",
        source_agent="test_agent",
        target_agent="xml_agent",
        intent="create_verification_plan",
        payload={"doc_id": "xml1"}
    )
    
    # Run the task
    plan = await agent.handle_create_verification_plan(task_request)
    print(f"Created verification plan with {len(plan['tasks'])} tasks")

asyncio.run(main())
```

### Workflow Integration

```python
# In a workflow definition:
tasks = [
    {
        "name": "analyze_xml",
        "agent": "xml_agent",
        "intent": "analyze_xml",
        "payload": {"doc_id": "${doc_id}"}
    },
    {
        "name": "create_verification_plan",
        "agent": "xml_agent",
        "intent": "create_verification_plan",
        "payload": {"doc_id": "${doc_id}"}
    },
    {
        "name": "batch_verify",
        "agent": "xml_agent",
        "intent": "batch_verify_nodes",
        "payload": {
            "doc_id": "${doc_id}",
            "options": {"search_depth": "high"}
        }
    }
]
```

## Future Enhancements

Planned enhancements for the XML Verification component:

1. Integration with search capabilities for fact-checking
2. LLM-assisted verification with context retrieval
3. Improved confidence scoring with machine learning
4. Collaborative verification workflows with human-in-the-loop
5. Schema validation and structural verification

## Dependencies

- `defusedxml`: For secure XML parsing
- `lxml`: For advanced XML processing (optional)