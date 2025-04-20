# Phase 2 XML Implementation: XML Analysis Agent

This document outlines the implementation of Phase 2 of the XML processing capabilities for Agent Provocateur, specifically the XML Analysis Agent for advanced node identification and verification planning.

## Overview

Phase 2 builds on the foundation of Phase 1 by adding:

1. Advanced researchable node identification with content analysis
2. Confidence scoring for verification needs
3. Rule-based analysis for identifying claims and statements
4. Verification planning with task prioritization
5. A dedicated `XmlAgent` class extending `BaseAgent`
6. Interactive CLI tools for testing the advanced functionality

## Implementation Details

### Enhanced XML Parser (`xml_parser.py`)

The XML Parser module has been extended with:

- **Advanced Node Identification**: The new `identify_researchable_nodes_advanced()` function uses multiple rule types to identify content that needs verification:
  - Element name patterns (e.g., "claim", "finding")
  - Content keyword matching (e.g., "all", "never", "always")
  - Attribute value analysis (e.g., "confidence=low")
  - Content pattern matching with regex (e.g., percentages, years, absolute terms)

- **Confidence Scoring**: Each identified node receives a confidence score (0.0-1.0) indicating how likely it needs verification, with supporting evidence.

- **Verification Needs Analysis**: The `analyze_xml_verification_needs()` function assesses document-level verification requirements, prioritization, and recommended approaches.

- **Improved XPath Generation**: Enhanced XPath generation for more precise node targeting.

### XML Agent (`xml_agent.py`)

A new `XmlAgent` class extending `BaseAgent` provides:

- **Document Analysis**: `handle_analyze_xml()` examines XML documents and determines verification needs.
  
- **Advanced Node Identification**: `handle_identify_nodes()` finds elements requiring verification based on configurable rules and confidence thresholds.
  
- **Verification Planning**: `handle_create_verification_plan()` generates a structured verification plan with prioritized tasks.
  
- **Node Status Updates**: `handle_update_node_status()` implements status updates for verification results.
  
- **Batch Verification**: `handle_batch_verify_nodes()` supports batch processing of multiple nodes.

### Testing and Integration

- **Unit Tests**: Comprehensive tests in `tests/test_xml_agent.py` verify the functionality of the XML Agent.

- **Interactive CLI Tools**:
  - `xml_agent_cli.py`: Command-line interface for interacting with the XML Agent
  - Support for custom rules via JSON configuration files
  - Verification plan generation and testing 
  - Confidence threshold adjustment

- **Sample Rules**: `sample_rules.json` provides example rules for advanced node identification.

- **Documentation Updates**: README.md updated with XML Agent usage examples and capabilities.

## Usage Examples

### Identifying Researchable Nodes

```bash
# With file input
python xml_agent_cli.py identify --file sample.xml --confidence 0.4 --evidence

# With document ID and custom rules
python xml_agent_cli.py identify --doc_id xml1 --rules-file sample_rules.json
```

### Creating Verification Plans

```bash
python xml_agent_cli.py plan xml1
```

### Testing Batch Verification

```bash
python xml_agent_cli.py verify xml1 --search-depth high
```

### Using the API

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
        intent="create_verification_plan",
        payload={"doc_id": "xml1"}
    )
    
    # Run the task
    plan = await agent.handle_create_verification_plan(task_request)
    print(f"Created verification plan with {len(plan['tasks'])} tasks")

asyncio.run(main())
```

## Configuration

The XML Agent supports various configuration options:

### Node Identification Rules

```json
{
  "keyword_rules": {
    "claim": ["all", "every", "never", "always", "best", "worst", "only", "unique"]
  },
  "attribute_rules": {
    "confidence": ["low", "medium", "uncertain", "preliminary"]
  },
  "content_patterns": [
    "\\d+%",
    "\\$\\d+",
    "(increased|decreased) by \\d+"
  ]
}
```

### Verification Configuration

```python
agent.verification_config = {
    "min_confidence": 0.5,
    "prioritize_recent": True,
    "max_nodes_per_task": 5
}
```

## Next Steps (Phase 3)

With Phase 2 complete, the following can be addressed in Phase 3:

1. Integration with search capabilities for fact-checking
2. Implement actual verification logic using LLMs
3. Verification result storage and update
4. Multi-source verification with confidence scoring
5. Verification workflow orchestration

## Dependencies

The XML implementation requires the following Python packages:

- `lxml`: For fast XML processing
- `defusedxml`: For secure XML parsing (protection against XXE attacks)
- `xmlschema`: For schema validation