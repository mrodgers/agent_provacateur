# XML Verification in Agent Provocateur

This document describes how to use the XML verification capabilities in Agent Provocateur, including the XML Agent for document analysis and verification planning.

## Overview

Agent Provocateur provides comprehensive support for analyzing and verifying XML documents through:

1. **XML Document Handling**: Store and retrieve XML documents with namespaces and structural information
2. **Researchable Node Identification**: Automatically identify content that requires verification
3. **Verification Planning**: Generate structured verification plans with prioritization
4. **Batch Verification**: Execute verification tasks in parallel or sequential order
5. **Confidence Scoring**: Assess verification needs with confidence scores and evidence

## XML Document Structure

XML documents are represented by the `XmlDocument` model which includes:

- `content`: Raw XML content
- `schema_url`: Optional URL to XML schema definition
- `root_element`: Name of the root element
- `namespaces`: Dictionary of XML namespaces
- `researchable_nodes`: List of nodes requiring verification

Nodes needing verification are represented by the `XmlNode` model:

- `xpath`: XPath to locate the node
- `element_name`: Name of the element
- `content`: Text content of the node
- `attributes`: Dictionary of node attributes
- `verification_status`: Status (pending, verified, etc.)
- `verification_data`: Verification results and confidence scores

## Command-Line Tools

### Basic XML CLI

The `xml_cli.py` script provides basic XML document operations:

```bash
# List all XML documents
python xml_cli.py list

# View document details
python xml_cli.py get xml1

# View document content
python xml_cli.py get xml1 --content

# View researchable nodes
python xml_cli.py get xml1 --nodes

# Upload a new XML document
python xml_cli.py upload sample.xml --title "My Document"
```

### XML Agent CLI

The `xml_agent_cli.py` script provides advanced XML Agent functionality:

```bash
# Identify researchable nodes with confidence scoring
python xml_agent_cli.py identify --file sample.xml --confidence 0.4 --evidence

# Use custom rules for identification
python xml_agent_cli.py identify --doc_id xml1 --rules-file sample_rules.json

# Create verification plan
python xml_agent_cli.py plan xml1

# Test batch verification
python xml_agent_cli.py verify xml1 --search-depth high
```

## Customizing Verification Rules

You can customize verification rules by providing a JSON configuration file:

```json
{
  "keyword_rules": {
    "claim": ["all", "every", "never", "always", "best", "worst"],
    "statement": ["proves", "confirmed", "established", "demonstrates"],
    "finding": ["significant", "breakthrough", "revolutionary"]
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

Use this file with the `--rules-file` parameter in the CLI:

```bash
python xml_agent_cli.py identify --doc_id xml1 --rules-file my_rules.json
```

## Programmatic Usage

### Working with XML Documents

```python
import asyncio
from agent_provocateur.mcp_client import McpClient
from agent_provocateur.xml_parser import load_xml_file

async def main():
    # Initialize client
    client = McpClient("http://localhost:8000")
    
    # List XML documents
    docs = await client.list_documents(doc_type="xml")
    for doc in docs:
        print(f"{doc.doc_id}: {doc.title}")
    
    # Get XML document
    xml_doc = await client.get_xml_document("xml1")
    print(f"Root element: {xml_doc.root_element}")
    print(f"Researchable nodes: {len(xml_doc.researchable_nodes)}")
    
    # Upload XML document
    with open("sample.xml", "r") as f:
        xml_content = f.read()
    new_doc = await client.upload_xml(xml_content, "New Document")
    print(f"Uploaded document ID: {new_doc.doc_id}")

asyncio.run(main())
```

### Using the XML Agent

```python
import asyncio
from agent_provocateur.xml_agent import XmlAgent
from agent_provocateur.a2a_models import TaskRequest
from agent_provocateur.a2a_messaging import InMemoryMessageBroker

async def main():
    # Initialize agent
    broker = InMemoryMessageBroker()
    agent = XmlAgent(agent_id="xml_agent", broker=broker)
    
    # Configure verification preferences
    agent.verification_config = {
        "min_confidence": 0.5,
        "custom_rules": {},
        "prioritize_recent": True,
        "max_nodes_per_task": 5
    }
    
    # Create verification plan
    plan_request = TaskRequest(
        task_id="plan_task",
        source_agent="user_agent",
        target_agent="xml_agent",
        intent="create_verification_plan",
        payload={"doc_id": "xml1"}
    )
    
    plan = await agent.handle_create_verification_plan(plan_request)
    print(f"Created plan with {len(plan['tasks'])} tasks")
    
    # Perform batch verification
    verify_request = TaskRequest(
        task_id="verify_task",
        source_agent="user_agent",
        target_agent="xml_agent",
        intent="batch_verify_nodes",
        payload={
            "doc_id": "xml1",
            "options": {
                "search_depth": "high",
                "verify_all": True
            }
        }
    )
    
    results = await agent.handle_batch_verify_nodes(verify_request)
    print(f"Verified {results['completed_nodes']} of {results['total_nodes']} nodes")

asyncio.run(main())
```

## Integration with Workflows

The XML verification capabilities can be integrated into larger workflows:

1. **Document Ingestion**: Upload XML documents through the MCP server
2. **Automatic Analysis**: Use the XML Agent to identify content needing verification
3. **Verification Planning**: Create structured verification plans
4. **Task Assignment**: Assign verification tasks to human or AI verifiers
5. **Reporting**: Compile verification results and generate reports

## XML Research

Agent Provocateur now includes integrated research capabilities for XML documents through the CLI's `research` command:

```bash
# Research entities in an XML document
ap-client research xml1

# Customize research parameters
ap-client research xml1 --min-confidence 0.7 --max-entities 5 

# Generate enriched XML output
ap-client research xml1 --format xml --output enriched.xml

# Include search for external validation
ap-client research xml1 --with-search --with-jira
```

The research workflow:

1. **Entity Extraction**: XML documents are analyzed to extract entities requiring research
2. **Research Orchestration**: The ResearchSupervisorAgent coordinates research on each entity
3. **Definition Generation**: Definitions are generated with confidence scores
4. **Enriched XML Output**: Original XML is enhanced with research results
5. **Validation**: Output XML is validated for correctness

The enriched XML includes:
- The original XML content
- Research results for each entity
- Definitions with confidence scores
- Source information
- Validation status

For implementation details, see [Phase 3 Implementation](../implementation/phase3_implementation.md).

## Next Steps

Future enhancements planned for XML verification and research:

1. Advanced entity extraction with natural language understanding
2. Integration with additional search capabilities for automatic fact-checking
3. Improved confidence scoring with machine learning
4. Collaborative verification workflows with human-in-the-loop
5. Full DocBook and DITA schema validation and compliance checking
6. Custom research templates for different domains

## Troubleshooting

Common issues:

- **Invalid XML Error**: Ensure your XML is well-formed and validate against schemas when available
- **Missing Nodes**: Check that your element names match the default XPath rules or provide custom rules
- **Low Confidence Scores**: Adjust the `min_confidence` threshold or update rule patterns
- **Timeout Errors**: For large XML documents, consider processing subsets of nodes